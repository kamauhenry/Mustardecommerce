from django.db.models import Q, Sum, Count, F
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
from ..models import (
    Order, OrderItem, Payment, Cart, CartItem, Product, Inventory,
    DeliveryLocation, ShippingMethod, CustomerReview, MOQRequest,
    CompletedOrder
)
from .serializers import (
    OrderSerializer, PaymentSerializer, CustomerReviewSerializer,
    MOQRequestSerializer, CompletedOrderSerializer, DeliveryLocationSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminUser
from .utils import invalidate_order_caches, format_phone_number, MAX_RECENT_ITEMS, MAX_DASHBOARD_ITEMS
from .locations import COUNTIES_AND_WARDS
from datetime import datetime
from django.http import JsonResponse, FileResponse, HttpResponseBadRequest
from django.db import IntegrityError, transaction, connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.template.loader import render_to_string
import requests
import os
import logging
import json
import base64
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# M-Pesa Configuration
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
CALLBACK_URL = os.getenv('CALLBACK_URL')
MPESA_BASE_URL = os.getenv('MPESA_BASE_URL')


# M-Pesa Payment Integration Functions

def generate_access_token():
    try:
        encoded_credentials = base64.b64encode(f"{CONSUMER_KEY}:{CONSUMER_SECRET}".encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
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
        try:
            amount = float(amount)  # Ensure amount is numeric
            if amount <= 0:
                raise ValueError("Amount must be greater than 0")
            amount = int(amount)
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
            "Amount": str(amount),
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


# Order Creation & Management

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_from_cart(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    if cart.items.count() == 0:
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    # Validate shipping method and Pick and Pay requirements
    all_pick_and_pay = all(item.product.is_pick_and_pay for item in cart.items.all())
    if all_pick_and_pay:
        if cart.shipping_method:
            return Response({"error": "Shipping method must be null for carts with only Pick and Pay products"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        if not cart.shipping_method:
            return Response({"error": "No shipping method selected for non-Pick and Pay products"}, status=status.HTTP_400_BAD_REQUEST)

    shipping_method = cart.shipping_method  # Already a ShippingMethod instance

    def create_order():
        with transaction.atomic():
            # Clean up incomplete orders
            existing_orders = Order.objects.filter(user=request.user).select_for_update().order_by('-created_at')[:MAX_RECENT_ITEMS]
            for existing_order in existing_orders:
                if not existing_order.items.exists() and (timezone.now() - existing_order.created_at).seconds < 300:
                    logger.info(f"Found incomplete order #MI{existing_order.id}, deleting it")
                    existing_order.delete()

            # Validate inventory for Pick and Pay products
            for cart_item in cart.items.all():
                if cart_item.product.is_pick_and_pay:
                    inventory = Inventory.objects.filter(product=cart_item.product).select_for_update().first()
                    if not inventory:
                        raise ValueError(f"No inventory record found for Pick and Pay product {cart_item.product.name}")
                    if cart_item.quantity > inventory.quantity:
                        raise ValueError(f"Insufficient stock for {cart_item.product.name}: {inventory.quantity} available, {cart_item.quantity} requested")

            # Create order without items
            order = Order(
                user=request.user,
                shipping_method=None if all_pick_and_pay else shipping_method,
                payment_status='pending',
                delivery_status='ready_for_pickup' if all_pick_and_pay else 'processing',
            )
            logger.info(f"Saving new order for user {request.user.username}")
            order.save()
            logger.info(f"Order saved with ID {order.id}, order_number MI{order.id}")

            if not order.pk:
                raise ValueError("Order was not saved properly, no primary key assigned")

            # Create order items and update inventory
            for cart_item in cart.items.all():
                logger.info(f"Creating OrderItem for product {cart_item.product.name}")
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    attributes=cart_item.attributes,
                    quantity=cart_item.quantity,
                    price=cart_item.price_per_piece,
                )
                if cart_item.product.is_pick_and_pay:
                    inventory = Inventory.objects.get(product=cart_item.product)
                    inventory.quantity -= cart_item.quantity
                    inventory.last_updated = timezone.now()
                    inventory.save()
                    logger.info(f"Updated inventory for {cart_item.product.name}: quantity={inventory.quantity}, last_updated={inventory.last_updated}")

            # Update total price after adding items
            order.update_total_price()
            # Clear cart items
            cart.items.all().delete()

            return order

    try:
        order = create_order()
        # Invalidate cache
        cache_key_orders = f'user_orders_{request.user.id}'
        cache_key_order = f'user_order_{request.user.id}_{order.id}'
        try:
            cache.delete(cache_key_orders)
            cache.delete(cache_key_order)
        except (InvalidCacheBackendError, Exception) as e:
            logger.error(f"Failed to invalidate cache: {e}")

        serializer = OrderSerializer(order)
        logger.info(f"Order created successfully: MI{order.id}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValueError as e:
        logger.error(f"Validation error during order creation: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Unexpected error during order creation: {str(e)}", exc_info=True)
        return Response({"error": f"Failed to create order: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_order_shipping(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    shipping_method_id = request.data.get('shipping_method_id')
    delivery_location_id = request.data.get('delivery_location_id')

    if shipping_method_id:
        try:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
            order.shipping_method = shipping_method
        except ShippingMethod.DoesNotExist:
            return Response({"error": "Shipping method not found"}, status=status.HTTP_404_NOT_FOUND)

    if delivery_location_id:
        try:
            delivery_location = DeliveryLocation.objects.get(id=delivery_location_id, user=request.user)
            order.delivery_location = delivery_location
        except DeliveryLocation.DoesNotExist:
            return Response({"error": "Delivery location not found"}, status=status.HTTP_404_NOT_FOUND)

    order.save()

    # Invalidate orders cache
    cache_key_orders = f'user_orders_{request.user.id}'
    cache_key_order = f'user_order_{request.user.id}_{order_id}'
    try:
        cache.delete(cache_key_orders)
        cache.delete(cache_key_order)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to invalidate cache: {e}")

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)


# Payment Processing

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
        if not isinstance(response, dict):
            logger.error("Invalid STK push response format")
            return Response({"error": "Invalid response from payment gateway"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if response.get("ResponseCode") == "0" and "CheckoutRequestID" in response:
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
    try:
        payment = Payment.objects.get(order_id=order_id, order__user=request.user)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

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
def mpesa_callback(request):
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
            from ecommerce.models import Payment  # Import here to avoid circular imports
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

            # Send order confirmation email
            try:
                order = payment.order
                user = order.user
                if user.email:
                    items = [
                        {
                            'product_name': item.product.name,
                            'quantity': item.quantity,
                            'price': str(item.price),
                            'line_total': str(item.quantity * item.price)
                        }
                        for item in order.items.all()
                    ]
                    email_context = {
                        'user_name': user.get_full_name() or user.username,
                        'order_id': order.order_number,
                        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'payment_status': order.get_payment_status_display(),
                        'delivery_status': order.get_delivery_status_display(),
                        'total_price': str(order.total_price),
                        'items': items,
                        'shipping_method': order.shipping_method.name if order.shipping_method else 'N/A',
                        'delivery_location': order.delivery_location.address if order.delivery_location else 'N/A',
                        'site_url': settings.SITE_URL,
                    }
                    # Build items string for plain text email
                    items_text = '\n'.join(
                        f"- {item['product_name']} (Qty: {item['quantity']}, Price: ${item['price']}, Total: ${item['line_total']})"
                        for item in items
                    )
                    html_message = render_to_string('order_confirmation.html', email_context)
                    plain_message = f"""
Dear {user.get_full_name() or user.username},

Thank you for your order! Below are the details of your purchase:

Order #{order.order_number}
Placed on: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
Payment Status: {order.get_payment_status_display()}
Delivery Status: {order.get_delivery_status_display()}
Total: ${order.total_price}

Items:
{items_text}

Shipping Method: {order.shipping_method.name if order.shipping_method else 'N/A'}
Address: {order.delivery_location.address if order.delivery_location else 'N/A'}

Regards,
Mustard Imports Team
"""
                    send_mail(
                        subject=f"Order Confirmation #{order.order_number}",
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    logger.info(f"Order confirmation email sent to {user.email} for Order #{order.order_number}")
                else:
                    logger.warning(f"No email address for user {user.username} for Order #{order.order_number}")
            except Exception as e:
                logger.error(f"Failed to send order confirmation email for Order #{order.order_number}: {str(e)}", exc_info=True)

            # Invalidate orders cache
            invalidate_order_caches(order.user.id, order.id)

            logger.info(f"Payment completed for Order {order.id} - M-Pesa Receipt: {mpesa_receipt}")
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"}, status=status.HTTP_200_OK)
        else:
            payment.payment_status = "failed"
            payment.error_message = result_desc
            payment.save()

            # Invalidate orders cache
            invalidate_order_caches(payment.order.user.id, payment.order.id)

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


# Utility Functions

@csrf_protect
def test_image(request):
    image_path = os.path.join(settings.MEDIA_ROOT, 'category_images', 'agriculture.jpeg')
    if os.path.exists(image_path):
        return FileResponse(open(image_path, 'rb'), content_type='image/jpeg')
    else:
        return JsonResponse({"error": "File not found"}, status=404)

def reset_order_id_sequence():
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(id) FROM ecommerce_order")
        max_id = cursor.fetchone()[0] or 0
        cursor.execute(f"SELECT setval('ecommerce_order_id_seq', {max_id + 1}, false)")


# Order Retrieval

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request, order_id=None, user_id=None):
    if order_id:
        cache_key = f'user_order_{request.user.id}_{order_id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            serializer = OrderSerializer(order)
            response_data = serializer.data

            try:
                cache.set(cache_key, response_data, timeout=60 * 5)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        cache_key = f'user_orders_{request.user.id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            orders = Order.objects.filter(user=request.user).prefetch_related('items', 'items__product').order_by('-created_at')
            serializer = OrderSerializer(orders, many=True)
            response_data = serializer.data

            try:
                cache.set(cache_key, response_data, timeout=60 * 5)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """Cancel an order and restore inventory for Pick & Pay products"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    if order.delivery_status not in ['processing', 'pending']:
        return Response(
            {"error": "Only pending or processing orders can be cancelled"},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        # Restore inventory for Pick & Pay products
        for item in order.items.all():
            if hasattr(item.product, 'is_pick_and_pay') and item.product.is_pick_and_pay:
                try:
                    inventory = Inventory.objects.get(product=item.product)
                    inventory.quantity += item.quantity
                    inventory.save()
                    logger.info(f"Restored {item.quantity} units to inventory for product {item.product.id}")
                except Inventory.DoesNotExist:
                    logger.warning(f"No inventory record for product {item.product.id}")

        order.is_cancelled = True
        order.delivery_status = 'cancelled'
        order.save()

        # Invalidate caches
        invalidate_order_caches(order.user.id, order.id)

    return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)


# Order ViewSets

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
        if order.delivery_status not in ['processing', 'pending']:
            return Response(
                {"error": "Only pending or processing orders can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Restore inventory for Pick & Pay products
            for item in order.items.all():
                if hasattr(item.product, 'is_pick_and_pay') and item.product.is_pick_and_pay:
                    try:
                        inventory = Inventory.objects.get(product=item.product)
                        inventory.quantity += item.quantity
                        inventory.save()
                        logger.info(f"Restored {item.quantity} units to inventory for product {item.product.id}")
                    except Inventory.DoesNotExist:
                        logger.warning(f"No inventory record for product {item.product.id}")

            order.is_cancelled = True
            order.delivery_status = 'cancelled'
            order.save()

            # Invalidate caches
            invalidate_order_caches(order.user.id, order.id)

        return Response({"message": "Order cancelled successfully"}, status=status.HTTP_200_OK)

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

    def list(self, request, *args, **kwargs):
        cache_key = f'completed_orders_{request.user.id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'completed_order_{request.user.id}_{instance.pk}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        serializer = self.get_serializer(instance)
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)


# Review Management

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

class ProductReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, product_id):
        cache_key = f'product_reviews_{product_id}_page_{request.query_params.get("page", 1)}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            product = Product.objects.get(id=product_id)
            reviews = product.reviews.all()
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 5))
            total = reviews.count()
            start = (page - 1) * per_page
            end = start + per_page
            reviews = reviews[start:end]
            serializer = CustomerReviewSerializer(reviews, many=True, context={'request': request})
            response_data = {'reviews': serializer.data, 'total': total}

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, product_id):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            product = Product.objects.get(id=product_id)
            serializer = CustomerReviewSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(user=request.user, product=product)

                # Invalidate reviews cache
                cache_key_reviews = f'product_reviews_{product_id}_page_1'
                try:
                    cache.delete(cache_key_reviews)
                except (InvalidCacheBackendError, Exception) as e:
                    print(f"Failed to invalidate reviews cache: {e}")

                # Invalidate product detail cache
                cache_key_product = f'product_detail_{product.category.slug}_{product.slug}'
                try:
                    cache.delete(cache_key_product)
                except (InvalidCacheBackendError, Exception) as e:
                    print(f"Failed to invalidate product cache: {e}")

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


# MOQ Request Management

class MOQRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MOQRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        if self.request.user.is_staff:
            return MOQRequest.objects.all()
        return MOQRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        moq_request = self.get_object()
        status_value = request.data.get('status')

        if status_value not in [choice[0] for choice in MOQRequest.STATUS_CHOICES]:
            return Response(
                {"error": "Invalid status value"},
                status=status.HTTP_400_BAD_REQUEST
            )

        moq_request.status = status_value
        moq_request.save()
        serializer = MOQRequestSerializer(moq_request)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get current user's MOQ requests with status summary"""
        queryset = self.get_queryset()

        # Get counts by status
        status_counts = {}
        for choice in MOQRequest.STATUS_CHOICES:
            status_counts[choice[0]] = queryset.filter(status=choice[0]).count()

        # Get recent requests
        recent_requests = queryset[:MAX_DASHBOARD_ITEMS]
        serializer = self.get_serializer(recent_requests, many=True)

        return Response({
            'status_counts': status_counts,
            'recent_requests': serializer.data,
            'total_requests': queryset.count()
        })


# User Profile & Delivery Location Views

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cache_key = f'user_profile_{request.user.id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        user = request.user
        response_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number or '',
            'date_joined': user.date_joined,
            'profile_photo': getattr(user, 'avatar', ''),
            'points': getattr(user, 'points', 0),
            'affiliate_code': getattr(user, 'affiliate_code', ''),
        }

        try:
            cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

    def put(self, request):
        user = request.user
        data = request.data
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.phone_number = data.get('phone_number', user.phone_number)
        if 'profile_photo' in data:
            user.avatar = data['profile_photo']
        user.save()

        # Invalidate cache
        cache_key_profile = f'user_profile_{user.id}'
        cache_key_current = f'current_user_{user.id}'
        try:
            cache.delete(cache_key_profile)
            cache.delete(cache_key_current)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'profile_photo': user.avatar,
            'points': getattr(user, 'points', 0),
            'affiliate_code': getattr(user, 'affiliate_code', ''),
        })


class DeliveryLocationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, location_id=None):
        locations = DeliveryLocation.objects.filter(Q(user=request.user) | Q(user__isnull=True))
        serializer = DeliveryLocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CountiesView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        counties = list(COUNTIES_AND_WARDS.keys())
        return Response({"counties": counties}, status=status.HTTP_200_OK)

class WardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        county = request.query_params.get("county")
        if county in COUNTIES_AND_WARDS:
            wards = COUNTIES_AND_WARDS[county]
            return Response({"wards": wards}, status=status.HTTP_200_OK)
        return Response({"error": "County not found"}, status=status.HTTP_404_NOT_FOUND)


# Admin Order Management

@api_view(['GET'])
@permission_classes([IsAdminUser])
@cache_page(60 * 15)
def get_all_orders(request):
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 10))
    payment_status = request.query_params.get('payment_status')
    delivery_status = request.query_params.get('delivery_status')
    search = request.query_params.get('search')

    orders = Order.objects.all().select_related('user', 'delivery_location').prefetch_related('items').order_by('-created_at')
    if payment_status:
        orders = orders.filter(payment_status=payment_status)
    if delivery_status:
        orders = orders.filter(delivery_status=delivery_status)
    if search:
        orders = orders.filter(order_number__icontains=search)

    paginator = Paginator(orders, per_page)
    page_obj = paginator.get_page(page)
    serializer = OrderSerializer(page_obj, many=True)
    return Response({
        'results': serializer.data,
        'total': paginator.count,
        'pages': paginator.num_pages,
        'current_page': page
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
@cache_page(60 * 15)
def get_moq_fulfilled_products(request):
    products = Product.objects.filter(moq_status='active').annotate(
        current_moq=Sum('orderitem__quantity', filter=Q(orderitem__order__payment_status='paid'))
    ).filter(current_moq__gte=F('moq'))
    from .serializers import ProductSerializer
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def place_order_for_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    orders = Order.objects.filter(items__product=product, payment_status='paid')
    if not orders.exists():
        return Response({'error': 'No paid orders for this product'}, status=status.HTTP_400_BAD_REQUEST)

    orders.update(delivery_status='processing')
    cache_key = 'admin_orders'
    try:
        cache.delete(cache_key)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to invalidate cache: {e}")
    return Response({'message': 'Orders updated to processing'})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def bulk_update_order_status(request):
    order_ids = request.data.get('order_ids', [])
    delivery_status = request.data.get('delivery_status')

    logger.info(f"Bulk update requested: order_ids={order_ids}, delivery_status={delivery_status}")

    if not order_ids or not delivery_status:
        logger.error("Missing order_ids or delivery_status")
        return Response(
            {'error': 'Missing order_ids or delivery_status'},
            status=status.HTTP_400_BAD_REQUEST
        )

    valid_statuses = [choice[0] for choice in Order.DELIVERY_STATUS_CHOICES]
    logger.info(f"Valid statuses: {valid_statuses}")
    if delivery_status not in valid_statuses:
        logger.error(f"Invalid delivery status: {delivery_status}")
        return Response(
            {'error': f"Invalid delivery status. Must be one of: {', '.join(valid_statuses)}"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        with transaction.atomic():
            orders = Order.objects.select_for_update().filter(id__in=order_ids)
            if not orders.exists():
                logger.error("No orders found for the provided IDs")
                return Response(
                    {'error': 'No orders found for the provided IDs'},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info(f"Found {orders.count()} orders: {[o.id for o in orders]}")

            updated_count = orders.update(delivery_status=delivery_status)
            logger.info(f"Updated {updated_count} orders to {delivery_status}")

            if updated_count == 0:
                logger.error("No orders were updated")
                return Response(
                    {'error': 'No orders were updated'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            updated_orders = Order.objects.filter(id__in=order_ids)
            serializer = OrderSerializer(updated_orders, many=True)

            user_ids = set(orders.values_list('user_id', flat=True))
            for user_id in user_ids:
                invalidate_order_caches(user_id)
                for order in orders.filter(user_id=user_id):
                    invalidate_order_caches(user_id, order.id)

        return Response(
            {
                'message': f'Successfully updated {updated_count} orders to {delivery_status}',
                'orders': serializer.data
            },
            status=status.HTTP_200_OK
        )
    except IntegrityError as e:
        logger.error(f"IntegrityError in bulk_update_order_status: {str(e)}, order_ids={order_ids}", exc_info=True)
        return Response(
            {'error': 'Database conflict occurred. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Error in bulk_update_order_status: {str(e)}, order_ids={order_ids}", exc_info=True)
        return Response(
            {'error': f'Failed to update orders: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAdminUser])
def update_single_order_status(request, order_id):
    delivery_status = request.data.get('delivery_status')

    logger.info(f"Single update requested: order_id={order_id}, delivery_status={delivery_status}")

    if not delivery_status:
        logger.error("Missing delivery_status")
        return Response({'error': 'Missing delivery_status'}, status=status.HTTP_400_BAD_REQUEST)

    valid_statuses = [choice[0] for choice in Order.DELIVERY_STATUS_CHOICES]
    if delivery_status not in valid_statuses:
        logger.error(f"Invalid delivery status: {delivery_status}")
        return Response({'error': 'Invalid delivery status'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order not found: {order_id}")
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        with transaction.atomic():
            order.delivery_status = delivery_status
            order.save()
            logger.info(f"Order {order_id} updated to {delivery_status}")
            order.refresh_from_db()
            if order.delivery_status != delivery_status:
                logger.error(f"Order {order_id} status mismatch: expected {delivery_status}, got {order.delivery_status}")
                return Response(
                    {'error': f"Status update failed for order {order_id}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        cache_key = 'admin_orders'
        try:
            cache.delete(cache_key)
            logger.info(f"Cache invalidated: {cache_key}")
        except (InvalidCacheBackendError, Exception) as e:
            logger.error(f"Failed to invalidate cache: {e}")

        serializer = OrderSerializer(order)
        return Response({
            'message': f'Order {order_id} updated to {delivery_status}',
            'order': serializer.data
        })
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {str(e)}")
        return Response({'error': f'Failed to update order: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
