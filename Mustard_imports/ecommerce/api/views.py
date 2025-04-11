from django.db.models import Q
from django.core.paginator import Paginator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from decimal import Decimal
from .permissions import IsOwnerOrAdmin, IsAdminUser
from datetime import datetime
from django.shortcuts import render
from ..models import *
from .serializers import *
from django.http import JsonResponse, Http404 ,FileResponse, HttpResponseBadRequest
from django.db import IntegrityError
from django.db import transaction
from django.db import models
from django.utils import timezone
from django.db import connection, transaction
from django.db.models import Max
import requests , os , logging ,re ,json,base64
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from PIL import Image
from io import BytesIO
from google.oauth2 import id_token
from google.auth.transport import requests

User = get_user_model()
load_dotenv()

# Retrieve secrets from .env
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
CALLBACK_URL = os.getenv('CALLBACK_URL')
MPESA_BASE_URL = os.getenv('MPESA_BASE_URL')

# M-Pesa Helper Functions
def generate_access_token():
    try:
        encoded_credentials = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
        # Fixed typo in URL ('oasuth' -> 'oauth')
        response = requests.get(
            f"{MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
            headers=headers
        ).json()

        if "access_token" in response:
            return response["access_token"]
        else:
            raise Exception(f"Failed to get access token: {response.get('errorMessage', 'Unknown error')}")
    except Exception as e:
        logger.error(f"Failed to generate access token: {str(e)}")
        raise Exception(f"Failed to get access token: {str(e)}")



def send_stk_push(phone_number, amount, order_id):
    try:
        # Convert amount to a positive integer
        try:
            amount = Decimal(str(amount))  # Handle Decimal or string input
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            amount = int(amount)  # Convert to integer, removing decimals
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid amount value: {amount} - {str(e)}")
            raise ValueError("Invalid amount format")

        logger.info(f"Formatted amount for STK push: {amount}")
        token = generate_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        stk_password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()

        request_body = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": stk_password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(amount),  # Send as string
            "PartyA": phone_number,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": CALLBACK_URL,
            "AccountReference": f"Order-{order_id}",
            "TransactionDesc": f"Payment for Order {order_id}"
        }
        response = requests.post(
            f"{MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
            json=request_body,
            headers=headers
        ).json()

        return response
    except Exception as e:
        logger.error(f"Failed to send STK push: {str(e)}")
        raise e

def query_stk_push(checkout_request_id):
    try:
        token = generate_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()).decode()

        request_body = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        response = requests.post(
            f"{MPESA_BASE_URL}/mpesa/stkpushquery/v1/query",
            json=request_body,
            headers=headers
        ).json()
        return response
    except requests.RequestException as e:
        logger.error(f"Failed to query STK status: {str(e)}")
        return {"error": str(e)}

# Existing Views (Integrated from Your Original Code)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_from_cart(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    if cart.items.count() == 0:
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        default_location = DeliveryLocation.objects.filter(user=request.user, is_default=True).first()
        if not default_location:
            return Response({"error": "No default delivery location set"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error fetching delivery location: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    logger.info(f"Cart contains {cart.items.count()} items")
    highest_id = Order.objects.aggregate(Max('id'))['id__max'] or 0
    next_id = highest_id + 1
    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            id=next_id,
            shipping_method='standard',
            delivery_location=default_location,
            payment_status='pending',
            delivery_status='processing',
        )
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                quantity=cart_item.quantity,
                price=cart_item.price_per_piece,
            )
        order.update_total_price()
        cart.items.all().delete()

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_shipping(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    shipping_method = request.data.get('shipping_method')
    delivery_location_id = request.data.get('delivery_location_id')

    if shipping_method:
        order.shipping_method = shipping_method
    if delivery_location_id:
        try:
            delivery_location = DeliveryLocation.objects.get(id=delivery_location_id, user=request.user)
            order.delivery_location = delivery_location
        except DeliveryLocation.DoesNotExist:
            return Response({"error": "Delivery location not found"}, status=status.HTTP_404_NOT_FOUND)

    order.save()
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)

    
def format_phone_number(phone_number):
    logger.info(f"Formatting phone number: {phone_number}")
    phone_number = phone_number.replace("+", "")
    if re.match(r"254\d{9}$", phone_number):
        logger.info(f"Phone number already in 254 format: {phone_number}")
        return phone_number
    elif phone_number.startswith("0") and len(phone_number) == 10:
        formatted_number = "254" + phone_number[1:]
        logger.info(f"Converted phone number to: {formatted_number}")
        return formatted_number
    else:
        logger.error(f"Invalid phone number format: {phone_number}")
        raise ValueError("Invalid phone number format")

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    logger.info(f"Received payment request: {request.data}")
    order_id = request.data.get('order_id')
    phone_number = request.data.get('phone_number')

    if not all([order_id, phone_number]):
        logger.error(f"Missing required fields: order_id={order_id}, phone_number={phone_number}")
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f"Initiating payment for order {order_id} with phone {phone_number}")
    try:
        phone_number = format_phone_number(phone_number)
    except ValueError as e:
        logger.error(f"Invalid phone number: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found for user {request.user}")
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.payment_status != 'pending':
        logger.warning(f"Order {order_id} payment status is {order.payment_status}, cannot process")
        return Response({"error": "Order already paid or cancelled"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        logger.info(f"Order total_price: {order.total_price} (type: {type(order.total_price)})")
        response = send_stk_push(phone_number, order.total_price, order_id)
        logger.info(f"STK push response: {response}")
        if response.get("ResponseCode") == "0":
            checkout_request_id = response["CheckoutRequestID"]
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    'phone_number': phone_number,
                    'payment_method': 'mpesa',
                    'amount': order.total_price,
                    'payment_status': 'pending',
                    'mpesa_checkout_request_id': checkout_request_id
                }
            )
            logger.info(f"Payment initiated for order {order_id}, CheckoutRequestID: {checkout_request_id}")
            return Response({
                "message": "Payment initiated",
                "checkout_request_id": checkout_request_id
            }, status=status.HTTP_200_OK)
        else:
            error_message = response.get("errorMessage", "Failed to process payment request")
            logger.error(f"STK push failed: {error_message}")
            return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Payment initiation failed: {str(e)}")
        return Response({"error": "Failed to initiate payment"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_details(request, order_id):
    """Verifies payment status with fallback to STK Push Query."""
    try:
        payment = Payment.objects.get(order_id=order_id, order__user=request.user)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

    # If payment is still pending, query M-Pesa for status
    if payment.payment_status == 'pending' and payment.mpesa_checkout_request_id:
        try:
            status_response = query_stk_push(payment.mpesa_checkout_request_id)
            if status_response.get("ResultCode") == "0":
                payment.payment_status = 'completed'
                payment.mpesa_receipt_number = status_response.get("MpesaReceiptNumber")
                payment.order.payment_status = 'paid'
                payment.save()
                payment.order.save()
            elif status_response.get("ResultCode"):
                payment.payment_status = 'failed'
                payment.error_message = status_response.get("ResultDesc", "Payment failed")
                payment.save()
        except Exception as e:
            logger.error(f"Failed to query payment status: {str(e)}")

    return Response({
        "payment_status": payment.payment_status,
        "amount": str(payment.amount),
        "phone_number": payment.phone_number,
        "payment_method": payment.payment_method,
        "payment_date": payment.payment_date,
        "mpesa_receipt_number": payment.mpesa_receipt_number,
        "error_message": payment.error_message
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def mpesa_callback(request):
    """Handles M-Pesa STK Push callback to update payment and order status."""
    if request.method != "POST":
        logger.error("Invalid request method: Expected POST")
        return HttpResponseBadRequest("Only POST requests are allowed")

    try:
        callback_data = json.loads(request.body)
        logger.info(f"M-Pesa callback received: {callback_data}")

        stk_callback = callback_data.get("Body", {}).get("stkCallback", {})
        checkout_request_id = stk_callback.get("CheckoutRequestID")
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")

        if not checkout_request_id or result_code is None:
            logger.error("Missing CheckoutRequestID or ResultCode in callback")
            return HttpResponseBadRequest("Invalid callback data: Missing required fields")

        try:
            payment = Payment.objects.get(mpesa_checkout_request_id=checkout_request_id)
        except Payment.DoesNotExist:
            logger.error(f"No payment found for CheckoutRequestID: {checkout_request_id}")
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if result_code == 0:
            callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            amount = next((item["Value"] for item in callback_metadata if item["Name"] == "Amount"), None)
            mpesa_receipt = next((item["Value"] for item in callback_metadata if item["Name"] == "MpesaReceiptNumber"), None)
            phone_number = next((item["Value"] for item in callback_metadata if item["Name"] == "PhoneNumber"), None)

            payment.amount = amount or payment.amount
            payment.mpesa_receipt_number = mpesa_receipt
            payment.phone_number = phone_number or payment.phone_number
            payment.payment_status = "completed"
            payment.save()

            payment.order.payment_status = "paid"
            payment.order.save()

            logger.info(f"Payment completed for Order {payment.order.id} - M-Pesa Receipt: {mpesa_receipt}")
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"}, status=status.HTTP_200_OK)
        else:
            payment.payment_status = "failed"
            payment.error_message = result_desc
            payment.save()

            logger.warning(f"Payment failed for Order {payment.order.id} - ResultCode: {result_code}, Desc: {result_desc}")
            return JsonResponse({"ResultCode": result_code, "ResultDesc": result_desc}, status=status.HTTP_200_OK)

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in callback: {str(e)}")
        return HttpResponseBadRequest(f"Invalid request body: {str(e)}")
    except KeyError as e:
        logger.error(f"Missing key in callback data: {str(e)}")
        return HttpResponseBadRequest(f"Invalid callback data: Missing key {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in callback: {str(e)}", exc_info=True)
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

logger = logging.getLogger(__name__)
@api_view(['POST']) 
@permission_classes([IsAuthenticated]) 
def process_checkout(request, cart_id): 
    try:

        # Log incoming request data
        logger.info(f"Processing checkout for cart {cart_id}. Data: {request.data}")
        reset_order_id_sequence()
        # Extract checkout data with defaults
        shipping_method = request.data.get('shipping_method', 'standard') 
        shipping_address = request.data.get('shipping_address', 'shop pick up')

        # Retrieve the cart
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the user owns the cart
        if cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Check if the cart has items
        if cart.items.count() == 0:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Log cart items before processing
        logger.info(f"Cart contains {cart.items.count()} items")
        highest_id = Order.objects.aggregate(Max('id'))['id__max'] or 0
        next_id = highest_id + 1
        # Use a database transaction to ensure atomicity
        with transaction.atomic():
            # Check if an order was already created for this cart but not completed
            existing_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
            for existing_order in existing_orders:
                # If we find a recent order with no items, it might be a failed checkout
                if not existing_order.items.exists() and (timezone.now() - existing_order.created_at).seconds < 300:  # 5 min
                    logger.info(f"Found incomplete order #{existing_order.id}, deleting it")
                    existing_order.delete()
            
            # Create order with all necessary details
            order = Order.objects.create(
                id=next_id, 
                user=cart.user,
                shipping_method=shipping_method,
                shipping_address=shipping_address,
            )
            for cart_item in cart.items.all():
                price_per_unit = cart_item.line_total / cart_item.quantity if cart_item.quantity > 0 else Decimal('0.00')
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=price_per_unit
                )
            order.save()  # Let the model calculate total_price

            # Clear the cart after checkout
            cart.items.all().delete()

            # Serialize and return the order
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        logger.error(f"IntegrityError during checkout: {str(e)}")
        return Response(
            {"error": "Failed to create order due to a database conflict. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Unexpected error during checkout: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@csrf_protect
def test_image(request):
    image_path = os.path.join(settings.MEDIA_ROOT, 'category_images', 'agriculture.jpeg')
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
    else:
        return JsonResponse({"error": "File not found"}, status=404)

def reset_order_id_sequence():
    with connection.cursor() as cursor:
        # Get the current maximum ID
        cursor.execute("SELECT MAX(id) FROM ecommerce_order")
        max_id = cursor.fetchone()[0] or 0
        # Reset the sequence to be higher than the current maximum
        cursor.execute(f"SELECT setval('ecommerce_order_id_seq', {max_id + 1}, false)")




# Authentication Views

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        id_token_str = request.data.get('access_token')
        try:
            # Verify the Google ID token
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            # Extract user info
            email = idinfo['email']
            name = idinfo.get('name', '')
            # Check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create new user if not exists
                user = User.objects.create_user(
                    username=email,  # Using email as username (ensure uniqueness in your model)
                    email=email,
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                    user_type='customer',
                )
            # Generate or get token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Google login successful',
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return super().get_serializer_class()

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Create or get a token for this user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username,
                'token': token.key  # Return the token to the client
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Token validation should be handled by permission classes in each view
        # This endpoint is kept for compatibility
        if request.user.is_authenticated:
            return Response({
                'message': 'Logged in',
                'user_id': request.user.id,
                'username': request.user.username
            }, status=status.HTTP_200_OK)
        return Response({'message': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    try:
        # Check if the user is authenticated via token
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Delete the user's token
        Token.objects.filter(user=request.user).delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Logout error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred during logout'
        }, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer =RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create a token for the new user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username,
                'token': token.key  # Return the token to the client
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):

    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
    })


@api_view(['POST'])
def create_cart(request, user_id=None):
    # If user_id is provided, use that. Otherwise, use current user
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user
    
    # Check if user is authenticated
    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Use get_or_create to avoid duplicate carts for the user
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_cart(request, user_id):
    # Ensure the requesting user is either the cart owner or an admin
    if request.user.id != user_id and not request.user.is_staff:
        return Response(
            {"detail": "You do not have permission to access this cart."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Try to get an existing cart or create a new one
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item_to_cart(request, cart_id):
    try:
        # cart_id is now coming from the URL parameter
        product_id = request.data.get('productId')
        variant_id = request.data.get('variantId')
        quantity = request.data.get('quantity', 1)

        cart = Cart.objects.get(id=cart_id)
        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.get(id=variant_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product, 
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Product variant not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_item_quantity(request, item_id):  # Add item_id as URL param
    try:
        # Get cart_id from request data (optional, depending on your needs)
        cart_id = request.data.get('cart_id')
        new_quantity = request.data.get('quantity')

        # Validate new_quantity
        if not isinstance(new_quantity, int) or new_quantity < 1:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch cart item using item_id and optionally cart_id
        if cart_id:
            cart_item = CartItem.objects.get(id=item_id, cart_id=cart_id)
        else:
            cart_item = CartItem.objects.get(id=item_id)

        # Check authorization
        if cart_item.cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        cart_item.quantity = new_quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, cart_id):  # Add cart_id as URL param
    try:
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({"error": "Item ID required"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the cart item
        cart_item = CartItem.objects.get(id=item_id, cart_id=cart_id)
        
        # Authorization check
        if cart_item.cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Delete the cart item
        cart_item.delete()

        # Return updated cart
        cart = Cart.objects.get(id=cart_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request, order_id=None):
    """Retrieves all orders or a specific order for the authenticated user."""
    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            logger.info(f"Order {order_id} not found for user {request.user.id}")
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        try:
            orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error fetching orders for user {request.user.id}: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    ordering = request.GET.get('ordering', '-created_at')
    
    if query:
        # First apply all filters
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by(ordering)
        
        # Then handle pagination
        paginator = Paginator(products, per_page)
        page_obj = paginator.get_page(page)
        
        serializer = ProductSerializer(page_obj, many=True)
        
        return Response({
            'results': serializer.data,  # Changed from 'products' to 'results' to match frontend expectation
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page
        })
    else:
        return Response({
            "results": [],  # Changed from 'products' to 'results'
            "total": 0, 
            "pages": 0, 
            "current_page": 1
        })

class CategoryProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_slug, *args, **kwargs):
        cache_key = f'category_products_{category_slug}_page_{request.query_params.get("page", 1)}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            # Fetch the category, ensuring it's active
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            products = Product.objects.filter(category=category).order_by('-created_at')

            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 5))
            total = products.count()
            start = (page - 1) * per_page
            end = start + per_page
            products = products[start:end]

            # Serialize category with request context
            category_serializer = CategorySerializer(category, context={'request': request})
            product_serializer = ProductSerializer(products, many=True, context={'request': request})

            response_data = {
                'category': category_serializer.data,
                'products': product_serializer.data,
                'total': total,
            }

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data)
        except Http404:
            return Response({'error': 'Category not found or inactive'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CategoriesWithProductsViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryListView(APIView):
    def get(self, request):
        try:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllCategoriesWithProductsView(APIView):
    permission_classes = [permissions.AllowAny]


    def get(self, request, *args, **kwargs):
        cache_key = 'all_categories_with_products'
        result = cache.get(cache_key)
        if not result: 
            categories = Category.objects.prefetch_related('products')
            serializer = CategoriesProductsSerializer(categories, many=True, context={'request': request})
            result = serializer.data
            cache.set(cache_key, result, 60*15)

        return Response(result)


# ViewSets
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().only('id', 'name', 'slug')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None  # Disable pagination

    def list(self, request, *args, **kwargs):
        cache_key = 'categories_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data

        cache.set(cache_key, response_data, timeout=60 * 15)
        return Response(response_data)


class ProductDetail(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.filter(category__slug=category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'delivery_status', 'is_cancelled']
    ordering_fields = ['created_at', 'price']

    def get_queryset(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id and self.request.user.is_authenticated:
            return Order.objects.filter(user_id=user_id)
        if self.request.user.is_staff:
            return Order.objects.prefetch_related("items").all()
        return Order.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.delivery_status not in ['processing', 'shipped']:
            return Response({"error": "Order cannot be cancelled in its current state"}, status=status.HTTP_400_BAD_REQUEST)
        order.is_cancelled = True
        order.delivery_status = 'cancelled'
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class CompletedOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompletedOrderSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id and self.request.user.is_authenticated:
            return CompletedOrder.objects.filter(user_id=user_id)
        if self.request.user.is_staff:
            return CompletedOrder.objects.all()
        return CompletedOrder.objects.filter(user=self.request.user)

class CustomerReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating']
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        return CustomerReview.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class MOQRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MOQRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return MOQRequest.objects.all()
        return MOQRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        moq_request = self.get_object()
        status = request.data.get('status')
        if status not in [choice[0] for choice in MOQRequest.STATUS_CHOICES]:
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
        moq_request.status = status
        moq_request.save()
        serializer = MOQRequestSerializer(moq_request)
        return Response(serializer.data)
    

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'name': user.first_name,
            'phone': user.phone_number,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'date_joined': user.date_joined,
            'avatar': getattr(user, 'avatar', ''),
        }
        return Response(data)

    def put(self, request):
        user = request.user
        data = request.data
        user.first_name = data.get('name', user.first_name)
        user.email = data.get('email', user.email)
        if 'phone' in data:
            user.phone = data['phone']
        if 'gender' in data:
            user.gender = data['gender']
        if 'dob' in data:
            user.dob = data['dob']
        if 'avatar' in data:
            user.avatar = data['avatar']
        user.save()
        return Response({
            'username': user.username,
            'email': user.email,
            'name': user.first_name,
            'phone': user.phone,
            'gender': user.gender,
            'dob': user.dob,
            'avatar': user.avatar,
        })

class DeliveryLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, location_id=None):
        """Retrieve all delivery locations for the authenticated user."""
        locations = DeliveryLocation.objects.filter(user=request.user)
        serializer = DeliveryLocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, location_id=None):
        """Add a new delivery location for the authenticated user."""
        data = request.data
        serializer = DeliveryLocationSerializer(data={
            'name': data.get('name'),
            'address': data.get('address'),
            'latitude': data.get('latitude'),  # Include latitude
            'longitude': data.get('longitude'),  # Include longitude
            'is_default': data.get('is_default', False),  # Changed key to match API
            'user': request.user.id
        })
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, location_id=None):
        """Set a location as the default for the authenticated user."""
        if not location_id:
            return Response({'message': 'Location ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = DeliveryLocation.objects.get(id=location_id, user=request.user)
        except DeliveryLocation.DoesNotExist:
            return Response({'message': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        location.is_default = True
        location.save()  # This will trigger the save method to unset other defaults
        return Response({'message': 'Set as default'}, status=status.HTTP_200_OK)

    def delete(self, request, location_id=None):
        """Delete a delivery location for the authenticated user."""
        if not location_id:
            return Response({'message': 'Location ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = DeliveryLocation.objects.get(id=location_id, user=request.user)
        except DeliveryLocation.DoesNotExist:
            return Response({'message': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        location.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
  
def autocomplete(request):
    query = request.GET.get('input', '')
    if not query:
        return JsonResponse({'status': 'error', 'message': 'No input provided'}, status=400)

    api_key = 'AIzaSyAmhYzyxBYyvs0sFbVVbXCnEdTbEgO1Tz8'  # Same as Vue frontend
    # Alternatively, use settings.GOOGLE_MAPS_API_KEY if defined in settings.py
    url = (
        f"https://maps.googleapis.com/maps/api/place/autocomplete/json?"
        f"input={query}&key={api_key}&types=geocode"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return JsonResponse(data)
    except requests.RequestException as e:
        print(f"Error fetching autocomplete data: {str(e)}")  # Log error for debugging
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def place_details(request):
    place_id = request.GET.get('place_id', '')
    if not place_id:
        return JsonResponse({'status': 'error', 'message': 'No place_id provided'}, status=400)

    api_key = 'AIzaSyAmhYzyxBYyvs0sFbVVbXCnEdTbEgO1Tz8'  # Same key as frontend
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json?"
        f"place_id={place_id}&key={api_key}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data)
    except requests.RequestException as e:
        print(f"Error fetching place details: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)