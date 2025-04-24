
from django.db.models import Q, Sum, Count, Max , F
from django.contrib.auth import login, logout, authenticate, get_user_model, update_session_auth_hash
from django.core.paginator import Paginator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from rest_framework.authtoken.models import Token
from decimal import Decimal
from .permissions import IsOwnerOrAdmin, IsAdminUser
from datetime import datetime, timedelta
from django.shortcuts import render
from ..models import *
from .serializers import *
from django.http import JsonResponse, Http404, FileResponse, HttpResponseBadRequest
from django.db import IntegrityError, transaction, connection
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import requests, os, logging, re, json, base64
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from google.oauth2 import id_token
from google.auth.transport import requests
import random
from django.core.mail import send_mail
from django.template.loader import render_to_string
import logging
from django.core.files.base import ContentFile
import pandas as pd
import io
import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify
import time
import json
import requests
import re

logger = logging.getLogger(__name__)
User = get_user_model()
load_dotenv()

# Retrieve secrets from .env
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
CALLBACK_URL = os.getenv('CALLBACK_URL')
MPESA_BASE_URL = os.getenv('MPESA_BASE_URL')

logger = logging.getLogger(__name__)

# M-Pesa Helper Functions
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
            amount = Decimal(str(amount))
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
def create_order_from_cart(request, cart_id):
    try:
        cart = Cart.objects.get(id=cart_id, user=request.user)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    if cart.items.count() == 0:
        return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    shipping_method = request.data.get('shipping_method', 'standard')
    logger.info(f"Cart contains {cart.items.count()} items")

    def create_order():
        with transaction.atomic():
            # Clean up incomplete orders
            existing_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
            for existing_order in existing_orders:
                if not existing_order.items.exists() and (timezone.now() - existing_order.created_at).seconds < 300:
                    logger.info(f"Found incomplete order #{existing_order.id}, deleting it")
                    existing_order.delete()

            # Calculate next ID
            highest_id = Order.objects.aggregate(Max('id'))['id__max'] or 0
            next_id = highest_id + 1

            # Create order with explicit ID
            order = Order.objects.create(
                id=next_id,
                user=request.user,
                shipping_method=shipping_method,
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except IntegrityError as e:
        logger.error(f"IntegrityError during order creation: {str(e)}, cart_id={cart_id}, user_id={request.user.id}", exc_info=True)
        if "duplicate key value violates unique constraint" in str(e):
            from django.db import connection
            with connection.cursor() as cursor:
                # Get next safe ID from database
                cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM ecommerce_order")
                next_id = cursor.fetchone()[0]
                # Skip known problematic IDs (e.g., 47, 48)
                if next_id in {47, 48}:
                    next_id = max(next_id, 48) + 1
                cursor.execute("ALTER SEQUENCE ecommerce_order_id_seq RESTART WITH %s", [next_id])
                cursor.execute("SELECT last_value FROM ecommerce_order_id_seq")
                new_seq_value = cursor.fetchone()[0]
                logger.info(f"Sequence reset to {new_seq_value}")
            # Retry order creation (without explicit ID to use sequence)
            try:
                # Temporarily switch to sequence-based creation for retry
                def create_order_retry():
                    with transaction.atomic():
                        existing_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
                        for existing_order in existing_orders:
                            if not existing_order.items.exists() and (timezone.now() - existing_order.created_at).seconds < 300:
                                logger.info(f"Found incomplete order #{existing_order.id}, deleting it")
                                existing_order.delete()

                        order = Order.objects.create(
                            user=request.user,
                            shipping_method=shipping_method,
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
                    return order

                order = create_order_retry()
                cache_key_orders = f'user_orders_{request.user.id}'
                cache_key_order = f'user_order_{request.user.id}_{order.id}'
                try:
                    cache.delete(cache_key_orders)
                    cache.delete(cache_key_order)
                except (InvalidCacheBackendError, Exception) as e:
                    logger.error(f"Failed to invalidate cache: {e}")

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as retry_e:
                logger.error(f"Retry failed: {str(retry_e)}", exc_info=True)
                return Response(
                    {"error": "Failed to create order after sequence adjustment."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"error": "Failed to create order due to a database conflict."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Unexpected error during order creation: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
@csrf_exempt
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

            # Send email with order details
            try:
                order = payment.order
                user = order.user
                items = order.items.all()
                item_details = [
                    {
                        'product_name': item.product.name,
                        'quantity': item.quantity,
                        'price': float(item.price),
                        'line_total': float(item.quantity * item.price),
                    }
                    for item in items
                ]

                email_context = {
                    'order_id': order.id,
                    'created_at': order.created_at.strftime('%B %d, %Y'),
                    'items': item_details,
                    'total_price': float(order.total_price),
                    'shipping_method': order.shipping_method,
                    'delivery_location': order.delivery_location.address if order.delivery_location else 'Not specified',
                    'payment_status': order.payment_status,
                    'delivery_status': order.delivery_status,
                    'user_name': user.first_name or user.username,
                }

                # Format items list with newlines
                items_text = ''.join(
                    f"- {item['product_name']} (Qty: {item['quantity']}, Price: ${item['price']}, Total: ${item['line_total']})\n"
                    for item in item_details
                )

                subject = f'Order #{order.id} Confirmation'
                html_message = render_to_string('order_confirmation_email.html', email_context)
                plain_message = f"""
            Dear {user.first_name or user.username},

            Thank you for your order! Below are the details:

            Order #{order.id}
            Placed on: {order.created_at.strftime('%B %d, %Y')}
            Total: ${order.total_price}
            Payment Status: {order.payment_status}
            Delivery Status: {order.delivery_status}

            Items:
            {items_text}
            Shipping: {order.shipping_method}
            Address: {order.delivery_location.address if order.delivery_location else 'Not specified'}

            Regards,
            Your Ecommerce Team
            """

                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(f"Order confirmation email sent to {user.email} for Order #{order.id}")
            except Exception as e:
                logger.error(f"Failed to send order confirmation email for Order #{payment.order.id}: {str(e)}")



            # Invalidate orders cache
            cache_key_orders = f'user_orders_{payment.order.user.id}'
            cache_key_order = f'user_order_{payment.order.user.id}_{payment.order.id}'
            try:
                cache.delete(cache_key_orders)
                cache.delete(cache_key_order)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache: {e}")

            logger.info(f"Payment completed for Order {payment.order.id} - M-Pesa Receipt: {mpesa_receipt}")
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"}, status=status.HTTP_200_OK)
        else:
            payment.payment_status = "failed"
            payment.error_message = result_desc
            payment.save()

            # Invalidate orders cache
            cache_key_orders = f'user_orders_{payment.order.user.id}'
            cache_key_order = f'user_order_{payment.order.user.id}_{payment.order.id}'
            try:
                cache.delete(cache_key_orders)
                cache.delete(cache_key_order)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache: {e}")

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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_checkout(request, cart_id):
    try:
        logger.info(f"Processing checkout for cart {cart_id}. Data: {request.data}")
        reset_order_id_sequence()
        shipping_method = request.data.get('shipping_method', 'standard')


        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        if cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        if cart.items.count() == 0:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
            
        logger.info(f"Cart contains {cart.items.count()} items")
        highest_id = Order.objects.aggregate(Max('id'))['id__max'] or 0
        next_id = highest_id + 1
        with transaction.atomic():
            existing_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
            for existing_order in existing_orders:
                if not existing_order.items.exists() and (timezone.now() - existing_order.created_at).seconds < 300:
                    logger.info(f"Found incomplete order #{existing_order.id}, deleting it")
                    existing_order.delete()
            


            order = Order.objects.create(
                id=next_id,
                user=cart.user,
                shipping_method=shipping_method,
            
            )
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.price_per_piece  # Use price_per_piece from CartItem
                )
            order.save()

            cart.items.all().delete()

            # Invalidate orders cache
            cache_key_orders = f'user_orders_{request.user.id}'
            cache_key_order = f'user_order_{request.user.id}_{next_id}'
            try:
                cache.delete(cache_key_orders)
                cache.delete(cache_key_order)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache: {e}")

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
        cursor.execute("SELECT MAX(id) FROM ecommerce_order")
        max_id = cursor.fetchone()[0] or 0
        cursor.execute(f"SELECT setval('ecommerce_order_id_seq', {max_id + 1}, false)")

# Authentication Views
class AdminRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Admin registration successful',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'token': token.key,
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Admin login successful',
                'user_id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'token': token.key,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'message': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can use this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        return Response({
            'message': 'Logged in as admin',
            'user_id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'user_type': request.user.user_type,
        }, status=status.HTTP_200_OK)

class AdminLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can use this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        logout(request)
        return Response({'message': 'Admin logged out successfully'}, status=status.HTTP_200_OK)

class AdminProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        
        cache_key = f'admin_profile_{request.user.id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        serializer = UserSerializer(request.user)
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

    def put(self, request):
        if request.user.user_type != 'admin':
            return Response({'error': 'Only admins can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Invalidate cache
            cache_key = f'admin_profile_{request.user.id}'
            try:
                cache.delete(cache_key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache: {e}")

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_dashboard(request):
    logger.info(f"Admin dashboard accessed by user: {request.user.username} (ID: {request.user.id}, Type: {request.user.user_type})")

    if request.user.user_type != 'admin':
        logger.warning(f"Non-admin user {request.user.username} attempted to access the dashboard")
        return Response(
            {'error': 'Only admins can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )

    cache_key = 'admin_dashboard'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    try:
        total_sales = Order.objects.count()
        total_revenue = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
        total_customers = User.objects.filter(user_type='customer').count()
        top_products = Product.objects.select_related('category').annotate(
            moq_count=Count('orderitem', filter=Q(orderitem__order__delivery_status__in=['processing', 'shipped']))
        ).order_by('-moq_count')[:5]
        top_products_data = ProductSerializer(top_products, many=True, context={'request': request}).data

        today = datetime.today()
        revenue_trend = {'current': [], 'previous': []}
        for i in range(6):
            month = today - timedelta(days=30 * i)
            current_month_revenue = Order.objects.filter(
                created_at__month=month.month, created_at__year=month.year
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            previous_month = month - timedelta(days=30)
            previous_month_revenue = Order.objects.filter(
                created_at__month=previous_month.month, created_at__year=previous_month.year
            ).aggregate(Sum('total_price'))['total_price__sum'] or 0
            revenue_trend['current'].insert(0, float(current_month_revenue))
            revenue_trend['previous'].insert(0, float(previous_month_revenue))

        sales_by_location = Order.objects.filter(delivery_location__isnull=False).values('delivery_location__address').annotate(sales=Count('id')).order_by('-sales')[:3]
        sales_by_location = [
            {'location': item['delivery_location__address'] or 'Unknown', 'sales': item['sales']}
            for item in sales_by_location
        ]

        total_sales_breakdown = [
            {'channel': 'Direct', 'sales': 38},
            {'channel': 'Affiliate', 'sales': 15},
            {'channel': 'Sponsored', 'sales': 14},
            {'channel': 'E-mail', 'sales': 48},
        ]

        active_orders = Order.objects.filter(delivery_status__in=['processing', 'shipped']).count()
        recent_orders = Order.objects.order_by('-created_at')[:5].values('id', 'total_price', 'created_at')

        response_data = {
            'total_sales': total_sales,
            'total_revenue': float(total_revenue),
            'total_customers': total_customers,
            'top_products': top_products_data,
            'revenue_trend': revenue_trend,
            'sales_by_location': sales_by_location,
            'total_sales_breakdown': total_sales_breakdown,
            'active_orders': active_orders,
            'recent_orders': list(recent_orders),
        }

        try:
            cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        logger.info(f"Dashboard data retrieved successfully for user: {request.user.username}")
        return Response(response_data)
    except Exception as e:
        logger.error(f"Error retrieving dashboard data for user {request.user.username}: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Internal server error while fetching dashboard data'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        id_token_str = request.data.get('access_token')
        try:
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            email = idinfo['email']
            name = idinfo.get('name', '')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                    user_type='customer',
                )
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
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Invalidate user profile and current user cache
        cache_key_profile = f'user_profile_{request.user.id}'
        cache_key_current = f'current_user_{request.user.id}'
        try:
            cache.delete(cache_key_profile)
            cache.delete(cache_key_current)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        return Response(serializer.data)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
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
        if not request.user.is_authenticated:
            return JsonResponse({
                'status': 'error',
                'message': 'Authentication required'
            }, status=status.HTTP_401_UNAUTHORIZED)

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
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'New passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    cache_key = f'current_user_{request.user.id}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    user = request.user
    response_data = {
        'id': user.id,
        'username': user.username,
    }

    try:
        cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to cache response: {e}")

    return JsonResponse(response_data)

@api_view(['POST'])
def create_cart(request, user_id=None):
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user
    
    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_cart(request, user_id):
    if request.user.id != user_id and not request.user.is_staff:
        return Response(
            {"detail": "You do not have permission to access this cart."},
            status=status.HTTP_403_FORBIDDEN
        )

    cache_key = f'user_cart_{user_id}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    try:
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        serializer = CartSerializer(cart)
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 2)  # Cache for 2 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item_to_cart(request, cart_id):
    try:
        product_id = request.data.get('productId')
        variant_id = request.data.get('variantId')
        quantity = request.data.get('quantity', 1)
        shipping_method_id = request.data.get('shippingMethodId')  # New field

        cart = Cart.objects.get(id=cart_id, user=request.user)
        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.get(id=variant_id)

        # Update shipping method if provided
        if shipping_method_id:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
            cart.shipping_method = shipping_method
            cart.save()

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Invalidate cart cache
        cache_key = f'user_cart_{cart.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Product variant not found"}, status=status.HTTP_404_NOT_FOUND)
    except ShippingMethod.DoesNotExist:
        return Response({"error": "Shipping method not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_shipping_method(request, cart_id):
    try:
        shipping_method_id = request.data.get('shippingMethodId')
        cart = Cart.objects.get(id=cart_id, user=request.user)

        if shipping_method_id:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
            cart.shipping_method = shipping_method
        else:
            cart.shipping_method = None
        cart.save()

        # Invalidate cart cache
        cache_key = f'user_cart_{cart.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except ShippingMethod.DoesNotExist:
        return Response({"error": "Shipping method not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_shipping_methods(request):
    try:
        shipping_methods = ShippingMethod.objects.filter(is_active=True)
        serializer = ShippingMethodSerializer(shipping_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_item_quantity(request, item_id):
    try:
        cart_id = request.data.get('cart_id')
        new_quantity = request.data.get('quantity')

        if not isinstance(new_quantity, int) or new_quantity < 1:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        if cart_id:
            cart_item = CartItem.objects.get(id=item_id, cart_id=cart_id)
        else:
            cart_item = CartItem.objects.get(id=item_id)

        if cart_item.cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        cart_item.quantity = new_quantity
        cart_item.save()

        # Invalidate cart cache
        cache_key = f'user_cart_{cart_item.cart.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, cart_id):
    try:
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({"error": "Item ID required"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = CartItem.objects.get(id=item_id, cart_id=cart_id)
        
        if cart_item.cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        cart_item.delete()

        # Invalidate cart cache
        cache_key = f'user_cart_{cart_item.cart.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

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
                cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            logger.info(f"Order {order_id} not found for user {request.user.id}")
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        cache_key = f'user_orders_{request.user.id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
            serializer = OrderSerializer(orders, many=True)
            response_data = serializer.data

            try:
                cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data, status=status.HTTP_200_OK)
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
    
    cache_key = f'search_{query}_{page}_{per_page}_{ordering}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by(ordering)
        
        paginator = Paginator(products, per_page)
        page_obj = paginator.get_page(page)
        
        serializer = ProductSerializer(page_obj, many=True, context={'request': request})
        
        response_data = {
            'results': serializer.data,
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page
        }
    else:
        response_data = {
            "results": [],
            "total": 0,
            "pages": 0,
            "current_page": 1
        }

    try:
        cache.set(cache_key, response_data, timeout=60 * 10)  # Cache for 10 minutes
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to cache response: {e}")

    return Response(response_data)

@api_view(['GET'])
@permission_classes([AllowAny])
def random_products(request):
    cache_key = 'random_products'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    products = list(Product.objects.all())
    random_products = random.sample(products, min(3, len(products)))
    serializer = ProductSerializer(random_products, many=True, context={'request': request})
    response_data = {
        'results': serializer.data,
        'total': len(random_products)
    }

    try:
        cache.set(cache_key, response_data, timeout=60 * 30)  # Cache for 30 minutes
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to cache response: {e}")

    return Response(response_data)

@api_view(['GET'])
@permission_classes([AllowAny])
def latest_products(request):
    limit = int(request.GET.get('limit', 3))
    cache_key = f'latest_products_{limit}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    products = Product.objects.order_by('-created_at')[:limit]
    serializer = ProductSerializer(products, many=True, context={'request': request})
    response_data = {
        'results': serializer.data,
        'total': len(products)
    }

    try:
        cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to cache response: {e}")

    return Response(response_data)

class RelatedProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_slug, product_id):
        cache_key = f'related_products_{category_slug}_{product_id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            queryset = Product.objects.filter(
                category__slug=category_slug,
                moq_status='active'
            ).exclude(id=product_id)[:5]
            if not queryset.exists():
                response_data = {"detail": "No related products found."}
                status_code = status.HTTP_204_NO_CONTENT
            else:
                serializer = ProductSerializer(queryset, many=True, context={'request': request})
                response_data = serializer.data
                status_code = status.HTTP_200_OK

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data, status=status_code)
        except ObjectDoesNotExist:
            raise Http404("Category or product not found.")

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
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            products = Product.objects.filter(category=category).order_by('-created_at')

            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 5))
            total = products.count()
            start = (page - 1) * per_page
            end = start + per_page
            products = products[start:end]

            category_serializer = CategorySerializer(category, context={'request': request})
            product_serializer = ProductSerializer(products, many=True, context={'request': request})

            response_data = {
                'category': category_serializer.data,
                'products': product_serializer.data,
                'total': total,
            }

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
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
        cache_key = 'categories_with_products'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        categories = Category.objects.prefetch_related('products')
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

class CategoryListView(APIView):
    def get(self, request):
        cache_key = 'category_list'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            categories = Category.objects.all().order_by('id')
            serializer = CategorySerializer(categories, many=True, context={'request': request})
            response_data = serializer.data

            try:
                cache.set(cache_key, response_data, timeout=60 * 30)  # Cache for 30 minutes
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AllCategoriesWithProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cache_key = 'all_categories_with_products'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        categories = Category.objects.prefetch_related('products')
        serializer = CategoriesProductsSerializer(categories, many=True, context={'request': request})
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().only('id', 'name', 'slug')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None

    def list(self, request, *args, **kwargs):
        cache_key = 'categories_list'
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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Invalidate category caches
        cache_keys = ['category_list', 'categories_with_products', 'all_categories_with_products']
        for key in cache_keys:
            try:
                cache.delete(key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache {key}: {e}")
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Invalidate category caches
        cache_keys = ['category_list', 'categories_with_products', 'all_categories_with_products']
        for key in cache_keys:
            try:
                cache.delete(key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache {key}: {e}")
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Invalidate category caches
        cache_keys = ['category_list', 'categories_with_products', 'all_categories_with_products']
        for key in cache_keys:
            try:
                cache.delete(key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache {key}: {e}")
        return response

class ProductDetail(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.filter(category__slug=category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, product_slug, format=None):
        cache_key = f'product_detail_{category_slug}_{product_slug}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        product = self.get_object(category_slug, product_slug)
        serializer = ProductSerializer(product, context={'request': request})
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

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

        # Invalidate orders cache
        cache_key_orders = f'user_orders_{request.user.id}'
        cache_key_order = f'user_order_{request.user.id}_{pk}'
        try:
            cache.delete(cache_key_orders)
            cache.delete(cache_key_order)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

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
        cache_key = f'user_profile_{request.user.id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        user = request.user
        response_data = {
            'username': user.username,
            'email': user.email,
            'name': user.first_name,
            'phone': user.phone_number,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'avatar': getattr(user, 'avatar', ''),
        }

        try:
            cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

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

        # Invalidate cache
        cache_key_profile = f'user_profile_{user.id}'
        cache_key_current = f'current_user_{user.id}'
        try:
            cache.delete(cache_key_profile)
            cache.delete(cache_key_current)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

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
        cache_key = f'delivery_locations_{request.user.id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        locations = DeliveryLocation.objects.filter(user=request.user)
        serializer = DeliveryLocationSerializer(locations, many=True)
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 5)  # Cache for 5 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, location_id=None):
        data = request.data
        serializer = DeliveryLocationSerializer(data={
            'name': data.get('name'),
            'address': data.get('address'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'is_default': data.get('is_default', False),
            'user': request.user.id
        })
        if serializer.is_valid():
            serializer.save(user=request.user)

            # Invalidate cache
            cache_key = f'delivery_locations_{request.user.id}'
            try:
                cache.delete(cache_key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache: {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, location_id=None):
        if not location_id:
            return Response({'message': 'Location ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = DeliveryLocation.objects.get(id=location_id, user=request.user)
        except DeliveryLocation.DoesNotExist:
            return Response({'message': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        location.is_default = True
        location.save()

        # Invalidate cache
        cache_key = f'delivery_locations_{request.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        return Response({'message': 'Set as default'}, status=status.HTTP_200_OK)

    def delete(self, request, location_id=None):
        if not location_id:
            return Response({'message': 'Location ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            location = DeliveryLocation.objects.get(id=location_id, user=request.user)
        except DeliveryLocation.DoesNotExist:
            return Response({'message': 'Location not found'}, status=status.HTTP_404_NOT_FOUND)

        location.delete()

        # Invalidate cache
        cache_key = f'delivery_locations_{request.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        return Response(status=status.HTTP_204_NO_CONTENT)

def autocomplete(request):
    query = request.GET.get('input', '')
    if not query:
        return JsonResponse({'status': 'error', 'message': 'No input provided'}, status=400)

    cache_key = f'autocomplete_{query}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    api_key = 'AIzaSyAmhYzyxBYyvs0sFbVVbXCnEdTbEgO1Tz8'
    url = (
        f"https://maps.googleapis.com/maps/api/place/autocomplete/json?"
        f"input={query}&key={api_key}&types=geocode"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        response_data = response.json()

        try:
            cache.set(cache_key, response_data, timeout=60 * 60)  # Cache for 1 hour
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return JsonResponse(response_data)
    except requests.RequestException as e:
        print(f"Error fetching autocomplete data: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

def place_details(request):
    place_id = request.GET.get('place_id', '')
    if not place_id:
        return JsonResponse({'status': 'error', 'message': 'No place_id provided'}, status=400)

    cache_key = f'place_details_{place_id}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return JsonResponse(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    api_key = 'AIzaSyAmhYzyxBYyvs0sFbVVbXCnEdTbEgO1Tz8'
    url = (
        f"https://maps.googleapis.com/maps/api/place/details/json?"
        f"place_id={place_id}&key={api_key}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        response_data = response.json()

        try:
            cache.set(cache_key, response_data, timeout=60 * 60)  # Cache for 1 hour
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return JsonResponse(response_data)
    except requests.RequestException as e:
        print(f"Error fetching place details: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



@api_view(['GET'])
@permission_classes([IsAdminUser])
@cache_page(60 * 15)  # Cache for 15 minutes
def get_all_orders(request):
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 10))
    payment_status = request.query_params.get('payment_status')
    delivery_status = request.query_params.get('delivery_status')

    orders = Order.objects.all().select_related('user', 'delivery_location').prefetch_related('items').order_by('-created_at')
    if payment_status:
        orders = orders.filter(payment_status=payment_status)
    if delivery_status:
        orders = orders.filter(delivery_status=delivery_status)

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
@cache_page(60 * 15)  # Cache for 15 minutes
def get_moq_fulfilled_products(request):
    products = Product.objects.filter(moq_status='active').annotate(
        current_moq=Sum('orderitem__quantity', filter=Q(orderitem__order__payment_status='paid'))
    ).filter(current_moq__gte=F('moq'))
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

def invalidate_order_caches(user_id, order_id=None):
    """Centralized function to invalidate order-related caches."""
    cache_keys = [f'user_orders_{user_id}']
    if order_id:
        cache_keys.append(f'user_order_{user_id}_{order_id}')
    cache_keys.append('admin_orders')  # Invalidate admin cache as well
    for key in cache_keys:
        try:
            cache.delete(key)
            logger.info(f"Cache invalidated: {key}")
        except (InvalidCacheBackendError, Exception) as e:
            logger.error(f"Failed to invalidate cache {key}: {e}")

@api_view(['POST'])
@permission_classes([IsAdminUser])
def bulk_update_order_status(request):
    order_ids = request.data.get('order_ids', [])
    delivery_status = request.data.get('delivery_status')  # Match field name with Order model

    logger.info(f"Bulk update requested: order_ids={order_ids}, delivery_status={delivery_status}")

    # Validate input
    if not order_ids or not delivery_status:
        logger.error("Missing order_ids or delivery_status")
        return Response(
            {'error': 'Missing order_ids or delivery_status'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate delivery status against choices
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
            # Lock orders to prevent concurrent updates
            orders = Order.objects.select_for_update().filter(id__in=order_ids)
            if not orders.exists():
                logger.error("No orders found for the provided IDs")
                return Response(
                    {'error': 'No orders found for the provided IDs'},
                    status=status.HTTP_404_NOT_FOUND
                )

            logger.info(f"Found {orders.count()} orders: {[o.id for o in orders]}")

            # Update orders
            updated_count = orders.update(delivery_status=delivery_status)
            logger.info(f"Updated {updated_count} orders to {delivery_status}")

            if updated_count == 0:
                logger.error("No orders were updated")
                return Response(
                    {'error': 'No orders were updated'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Invalidate caches for affected orders
            user_ids = set(orders.values_list('user_id', flat=True))
            for user_id in user_ids:
                # Invalidate user-specific caches
                invalidate_order_caches(user_id)
                # Invalidate individual order caches
                for order in orders.filter(user_id=user_id):
                    invalidate_order_caches(user_id, order.id)

        return Response(
            {'message': f'Successfully updated {updated_count} orders to {delivery_status}'},
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
    delivery_status = request.data.get('delivery_status')  # Updated field name

    logger.info(f"Single update requested: order_id={order_id}, delivery_status={delivery_status}")

    # Validate input
    if not delivery_status:
        logger.error("Missing delivery_status")
        return Response({'error': 'Missing delivery_status'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate delivery status against choices
    valid_statuses = [choice[0] for choice in Order.DELIVERY_STATUS_CHOICES]
    if delivery_status not in valid_statuses:
        logger.error(f"Invalid delivery status: {delivery_status}")
        return Response({'error': 'Invalid delivery status'}, status=status.HTTP_400_BAD_REQUEST)

    # Find the order
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order not found: {order_id}")
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    # Update order
    try:
        with transaction.atomic():
            order.delivery_status = delivery_status
            order.save()
            logger.info(f"Order {order_id} updated to {delivery_status}")
            # Verify update
            order.refresh_from_db()
            if order.delivery_status != delivery_status:
                logger.error(f"Order {order_id} status mismatch: expected {delivery_status}, got {order.delivery_status}")
                return Response(
                    {'error': f"Status update failed for order {order_id}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        # Invalidate cache
        cache_key = 'admin_orders'
        try:
            cache.delete(cache_key)
            logger.info(f"Cache invalidated: {cache_key}")
        except (InvalidCacheBackendError, Exception) as e:
            logger.error(f"Failed to invalidate cache: {e}")

        return Response({'message': f'Order {order_id} updated to {delivery_status}'})
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {str(e)}")
        return Response({'error': f'Failed to update order: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        logger.info(f"Create request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        logger.info(f"Created product {product.id} with attribute_values: {list(product.attribute_values.all())}")
        
        # Handle multiple images
        images = request.FILES.getlist('images')
        logger.info(f"Creating product {product.name} with {len(images)} images: {[img.name for img in images]}")
        for image in images:
            try:
                ProductImage.objects.create(product=product, image=image)
                logger.info(f"Created ProductImage for {product.name}: {image.name}")
            except Exception as e:
                logger.error(f"Failed to create ProductImage for {product.name}: {image.name}, error: {str(e)}")
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        logger.info(f"Update request data: {request.data}")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        logger.info(f"Updated product {product.id} with attribute_values: {list(product.attribute_values.all())}")
        
        # Handle multiple images
        images = request.FILES.getlist('images')
        logger.info(f"Updating product {product.name} with {len(images)} images: {[img.name for img in images]}")
        if images:
            for image in images:
                try:
                    ProductImage.objects.create(product=product, image=image)
                    logger.info(f"Created ProductImage for {product.name}: {image.name}")
                except Exception as e:
                    logger.error(f"Failed to create ProductImage for {product.name}: {image.name}, error: {str(e)}")
        else:
            logger.warning(f"No images provided for product {product.name} update")
        
        return Response(serializer.data)


class SupplierView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            try:
                supplier = Supplier.objects.get(pk=pk)
                serializer = SupplierSerializer(supplier)
                return Response(serializer.data)
            except Supplier.DoesNotExist:
                return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            supplier = Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            supplier = Supplier.objects.get(pk=pk)
            supplier.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)

class AttributeView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            try:
                attribute = Attribute.objects.get(pk=pk)
                serializer = AttributeSerializer(attribute)
                return Response(serializer.data)
            except Attribute.DoesNotExist:
                return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)
        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AttributeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            attribute = Attribute.objects.get(pk=pk)
        except Attribute.DoesNotExist:
            return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AttributeSerializer(attribute, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            attribute = Attribute.objects.get(pk=pk)
            attribute.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Attribute.DoesNotExist:
            return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)

class AttributeValueView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            try:
                attribute_value = AttributeValue.objects.get(pk=pk)
                serializer = AttributeValueSerializer(attribute_value)
                return Response(serializer.data)
            except AttributeValue.DoesNotExist:
                return Response({"error": "Attribute value not found"}, status=status.HTTP_404_NOT_FOUND)
        attribute_values = AttributeValue.objects.select_related('attribute').all()
        serializer = AttributeValueSerializer(attribute_values, many=True)
        return Response(serializer.data)

    def post(self, request):
        attribute_id = request.data.get('attribute_id')
        values = request.data.get('values', [])  # Expect a list of values
        if not attribute_id or not values:
            return Response(
                {'error': 'Both attribute_id and values are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            attribute = Attribute.objects.get(id=attribute_id)
        except Attribute.DoesNotExist:
            return Response(
                {'error': 'Attribute not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        created_values = []
        for value in values:
            value = value.strip()
            if not value or AttributeValue.objects.filter(attribute=attribute, value=value).exists():
                continue
            attribute_value = AttributeValue.objects.create(attribute=attribute, value=value)
            created_values.append(AttributeValueSerializer(attribute_value).data)
        return Response(created_values, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        try:
            attribute_value = AttributeValue.objects.get(pk=pk)
        except AttributeValue.DoesNotExist:
            return Response({"error": "Attribute value not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AttributeValueSerializer(attribute_value, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            attribute_value = AttributeValue.objects.get(pk=pk)
            attribute_value.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AttributeValue.DoesNotExist:
            return Response({"error": "Attribute value not found"}, status=status.HTTP_404_NOT_FOUND)


class AttributeValueByAttributeView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, attribute_id):
        try:
            attribute = Attribute.objects.get(id=attribute_id)
            attribute_values = AttributeValue.objects.filter(attribute=attribute)
            serializer = AttributeValueSerializer(attribute_values, many=True)
            return Response(serializer.data)
        except Attribute.DoesNotExist:
            return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)
class BulkProductImportView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read CSV or Excel
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return Response({"error": "Unsupported file format. Use CSV or Excel."}, status=status.HTTP_400_BAD_REQUEST)

            created_products = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Prepare product data
                    product_data = {
                        'name': row.get('name', ''),
                        'slug': row.get('slug', row.get('name', '').lower().replace(' ', '-')),
                        'description': row.get('description', ''),
                        'price': row.get('price', 0),
                        'below_moq_price': row.get('below_moq_price', None),
                        'moq': int(row.get('moq', 1)),
                        'moq_per_person': int(row.get('moq_per_person', 1)),
                        'moq_status': row.get('moq_status', 'active'),
                        'category_id': int(row.get('category_id', 0)),
                        'supplier_id': int(row.get('supplier_id', None)) if row.get('supplier_id') else None,
                        'meta_title': row.get('meta_title', ''),
                        'meta_description': row.get('meta_description', ''),
                        'attribute_ids': row.get('attribute_ids', '').split(',') if row.get('attribute_ids') else [],
                    }

                    # Validate and create product
                    serializer = ProductSerializer(data=product_data)
                    if serializer.is_valid():
                        product = serializer.save()
                        
                        # Handle images (URLs in CSV)
                        image_urls = row.get('image_urls', '').split(',') if row.get('image_urls') else []
                        for url in image_urls:
                            url = url.strip()
                            if url:
                                try:
                                    response = requests.get(url)
                                    if response.status_code == 200:
                                        image_name = url.split('/')[-1]
                                        ProductImage.objects.create(
                                            product=product,
                                            image=ContentFile(response.content, name=image_name)
                                        )
                                except Exception as e:
                                    logger.error(f"Failed to download image {url} for product {product.name}: {str(e)}")
                        
                        created_products.append(serializer.data)
                    else:
                        errors.append({"row": index + 2, "errors": serializer.errors})
                except Exception as e:
                    errors.append({"row": index + 2, "error": str(e)})
            
            response_data = {
                "created": len(created_products),
                "products": created_products,
                "errors": errors
            }
            return Response(response_data, status=status.HTTP_201_CREATED if created_products else status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Failed to process file: {str(e)}")
            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class HomeCategoriesPagination(PageNumberPagination):
    page_size = 4  # Load 4 categories per page
    page_size_query_param = 'page_size'
    max_page_size = 20

class HomeCategoriesView(APIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = HomeCategoriesPagination

    def get(self, request, *args, **kwargs):
        cache_key = f'home_categories_with_products_page_{request.query_params.get("page", 1)}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except Exception as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            # Fetch all active categories ordered by id
            categories = Category.objects.filter(is_active=True).order_by('id')
            # Apply pagination
            paginator = self.pagination_class()
            paginated_categories = paginator.paginate_queryset(categories, request)
            # Serialize the paginated queryset
            serializer = HomeCategorySerializer(paginated_categories, many=True, context={'request': request})
            # Return paginated response
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ScrapeProductsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Starting POST request processing in ScrapeProductsView")
        platform = request.data.get('platform')
        url = request.data.get('url')
        logger.info(f"Request received - Platform: {platform}, URL: {url}")

        if not platform or not url:
            logger.error("Missing platform or URL in request")
            return Response(
                {"error": "Both 'platform' and 'url' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if platform not in ['shein', 'alibaba']:
            logger.error(f"Invalid platform: {platform}")
            return Response(
                {"error": "Please provide a valid platform ('shein' or 'alibaba')."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if platform == 'shein':
                logger.info("Calling fetch_shein_single_product")
                product = self.fetch_shein_single_product(url)
            else:
                logger.info("Calling fetch_alibaba_single_product")
                product = self.fetch_alibaba_single_product(url)
        except Exception as e:
            logger.error(f"Error during scraping for {platform}: {str(e)}")
            return Response(
                {"error": f"Failed to scrape product from {platform}: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        logger.info(f"Scraped product: {product.get('name', 'Unknown') if product else 'None'}")
        if not product:
            logger.warning(f"No product found on {platform} page")
            return Response(
                {"error": f"No product found on the {platform} page."},
                status=status.HTTP_404_NOT_FOUND
            )

        logger.info("Starting product serialization and saving process")
        logger.info(f"Serializing product: {product.get('name', 'Unknown')}")
        serializer = ProductSerializer(data=product, context={'request': request})
        if serializer.is_valid():
            logger.info(f"Product data valid: {product.get('name', 'Unknown')}")
            product_instance = serializer.save()
            saved_product = serializer.data
            logger.info(f"Successfully saved product: {product.get('name', 'Unknown')}")
        else:
            logger.error(f"Failed to save product: {serializer.errors}")
            return Response(
                {"error": f"Failed to save product: {serializer.errors}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info("Returning saved product")
        return Response(
            {
                "message": "Successfully saved 1 product.",
                "product": saved_product
            },
            status=status.HTTP_201_CREATED
        )

    def fetch_shein_single_product(self, url):
        logger.info("Starting fetch_shein_single_product method")
        logger.warning("Shein single product fetching may require JavaScript rendering")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            logger.info("Sending GET request to Shein product page")
            response = requests.get(url, headers=headers, timeout=30)
            logger.info(f"Shein response status: {response.status_code}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            logger.info("Parsed Shein product page HTML with BeautifulSoup")
            return self.parse_shein_single_product(soup)
        except requests.RequestException as e:
            logger.error(f"Shein product page request failed: {str(e)}")
            return None

    def fetch_alibaba_single_product(self, url):
        logger.info("Starting fetch_alibaba_single_product method")
        OXYLABS_USERNAME = getattr(settings, 'OXYLABS_USERNAME', 'your_username')
        OXYLABS_PASSWORD = getattr(settings, 'OXYLABS_PASSWORD', 'your_password')
        logger.info(f"Using Oxylabs credentials: {OXYLABS_USERNAME}")
        payload = {
            "source": "universal",
            "url": url,
            "render": "html"
        }
        logger.info(f"Oxylabs payload: {payload}")
        try:
            logger.info("Sending POST request to Oxylabs API")
            response = requests.post(
                "https://realtime.oxylabs.io/v1/queries",
                auth=(OXYLABS_USERNAME, OXYLABS_PASSWORD),
                json=payload,
                timeout=30
            )
            logger.info(f"Oxylabs API response status: {response.status_code}")
            response.raise_for_status()
            logger.info("Parsing Oxylabs API response")
            data = response.json()
            logger.info(f"Oxylabs response: {data.get('results', 'No results')[:1000]}")
            logger.info("Validating Oxylabs API response structure")
            if 'results' not in data or not data['results']:
                logger.error("No content returned from Oxylabs API")
                return None
            html_content = data['results'][0].get('content', '')
            logger.info(f"Oxylabs HTML length: {len(html_content)}")
            if not html_content:
                logger.error("Empty content returned from Oxylabs API")
                return None
            logger.info("Parsing HTML with BeautifulSoup")
            soup = BeautifulSoup(html_content, 'html.parser')
            logger.info("BeautifulSoup parsed HTML successfully")
            logger.info("Calling parse_alibaba_single_product")
            return self.parse_alibaba_single_product(soup)
        except requests.RequestException as e:
            logger.error(f"Oxylabs API request failed: {str(e)}")
            if e.response is not None:
                logger.error(f"Oxylabs response: {e.response.text}")
            return None

    def parse_alibaba_single_product(self, soup):
        logger.info("Starting parse_alibaba_single_product method")
        logger.info("Creating or retrieving Alibaba category")
        default_category, _ = Category.objects.get_or_create(
            name="Alibaba",
            defaults={"slug": "alibaba", "description": "Products scraped from Alibaba", "is_active": True}
        )
        default_category_id = default_category.id
        default_supplier_id = None
        logger.info(f"Default category ID for Alibaba: {default_category_id}")

        product_data = {}

        # Extract product name
        logger.info("Extracting product name")
        name_elem = soup.select_one('h1.module-pdp-title')
        product_data['name'] = name_elem.text.strip() if name_elem else 'Unknown Product'
        logger.info(f"Product name: {product_data['name']}")

        # Extract price and below MOQ price
        logger.info("Extracting product price")
        price_elem = soup.select_one('span.price-number')
        price_text = price_elem.text.strip().replace('$', '').replace('US', '').replace(',', '') if price_elem else '0.0'
        try:
            if '-' in price_text:
                prices = price_text.split('-')
                price_usd = float(prices[0].strip())
                below_moq_price_usd = float(prices[1].strip())
            else:
                price_usd = float(price_text)
                below_moq_price_usd = price_usd * 1.2  # Default multiplier if no range
        except ValueError:
            logger.warning(f"Invalid price format: {price_text}, defaulting to 0.0")
            price_usd = 0.0
            below_moq_price_usd = 0.0

        # Apply Alibaba multiplier (1.35)
        price_usd *= 1.35
        below_moq_price_usd *= 1.35
        logger.info(f"Price after 1.35 multiplier: {price_usd} USD, Below MOQ: {below_moq_price_usd} USD")

        # Convert USD to KES (as of April 2025, using a realistic rate; in practice, fetch from an API)
        USD_TO_KES_RATE = 130.50  # Example rate; replace with real-time fetch if needed
        price_kes = price_usd * USD_TO_KES_RATE
        below_moq_price_kes = below_moq_price_usd * USD_TO_KES_RATE

        # Round to 2 decimal places, then to nearest shilling if needed
        price_kes = round(price_kes, 2)
        below_moq_price_kes = round(below_moq_price_kes, 2)
        if price_kes % 1 > 0:  # If there are decimals
            price_kes = round(price_kes)
        if below_moq_price_kes % 1 > 0:
            below_moq_price_kes = round(below_moq_price_kes)
        product_data['price'] = price_kes
        product_data['below_moq_price'] = below_moq_price_kes
        logger.info(f"Price in KES: {product_data['price']}, Below MOQ in KES: {product_data['below_moq_price']}")

        # Extract description
        logger.info("Extracting product description")
        desc_elem = soup.select_one('div.module-pdp-description')
        product_data['description'] = desc_elem.text.strip() if desc_elem else 'No description available'
        logger.info(f"Description: {product_data['description']}")

        # Extract thumbnail
        logger.info("Extracting thumbnail")
        thumbnail_elem = soup.select_one('img.magnifier-image')
        product_data['thumbnail'] = thumbnail_elem['src'] if thumbnail_elem and 'src' in thumbnail_elem.attrs else ""
        logger.info(f"Thumbnail URL: {product_data['thumbnail']}")

        # Extract supplier information
        logger.info("Extracting supplier information")
        supplier_elem = soup.select_one('a.supplier-name')
        product_data['supplier_name'] = supplier_elem.text.strip() if supplier_elem else "N/A"
        product_data['supplier_link'] = supplier_elem['href'] if supplier_elem and 'href' in supplier_elem.attrs else None
        logger.info(f"Supplier: {product_data['supplier_name']} - {product_data['supplier_link']}")

        # Extract supplier info (years, country)
        logger.info("Extracting supplier info")
        supplier_info_elem = soup.select_one('div.supplier-year')
        product_data['supplier_info'] = supplier_info_elem.text.strip() if supplier_info_elem else "N/A"
        logger.info(f"Supplier Info: {product_data['supplier_info']}")

        # Extract MOQ
        logger.info("Extracting MOQ")
        moq_elem = soup.select_one('div.moq-value')
        moq_text = moq_elem.text.strip() if moq_elem else "1"
        try:
            product_data['moq'] = int(re.sub(r'\D', '', moq_text))  # Extract digits only
        except ValueError:
            product_data['moq'] = 1
        logger.info(f"MOQ: {product_data['moq']}")

        # Extract product ID
        logger.info("Extracting product ID")
        product_id_elem = soup.select_one('meta[itemprop="productID"]')
        product_data['product_id'] = product_id_elem['content'] if product_id_elem and 'content' in product_id_elem.attrs else None
        logger.info(f"Product ID: {product_data['product_id']}")

        # Extract attributes (variations)
        logger.info("Extracting product variations")
        attribute_value_ids = []
        variation_sections = soup.select('div.sku-item')  # Common Alibaba variation container
        for variation in variation_sections:
            # Extract attribute name (e.g., "Color", "Model")
            attr_name_elem = variation.select_one('span.sku-title')
            attr_name = attr_name_elem.text.strip().replace(':', '').lower() if attr_name_elem else None
            if not attr_name:
                continue
            logger.info(f"Found variation attribute: {attr_name}")

            # Find or create the attribute
            try:
                attribute = Attribute.objects.filter(name__iexact=attr_name).first()
                if not attribute:
                    logger.info(f"Creating new attribute: {attr_name}")
                    attribute = Attribute.objects.create(name=attr_name)
            except Exception as e:
                logger.error(f"Error creating attribute {attr_name}: {str(e)}")
                continue

            # Extract attribute values (e.g., "Red", "Blue" for Color)
            attr_values = variation.select('div.sku-item-option')
            for value_elem in attr_values:
                attr_value = value_elem.text.strip().lower()
                if not attr_value:
                    continue
                logger.info(f"Found attribute value: {attr_value} for attribute: {attr_name}")

                # Find or create the attribute value
                try:
                    attribute_value = AttributeValue.objects.filter(attribute=attribute, value__iexact=attr_value).first()
                    if not attribute_value:
                        logger.info(f"Creating new attribute value: {attr_value} for attribute: {attr_name}")
                        attribute_value = AttributeValue.objects.create(attribute=attribute, value=attr_value)
                    attribute_value_ids.append(attribute_value.id)
                except Exception as e:
                    logger.error(f"Error creating attribute value {attr_value} for {attr_name}: {str(e)}")
                    continue

        product_data['attribute_value_ids'] = attribute_value_ids
        logger.info(f"Attribute value IDs: {attribute_value_ids}")

        # Prepare metadata
        logger.info("Preparing metadata")
        meta_title = f"{product_data['name']} - Wholesale Deals"
        meta_description = f"Get {product_data['name']} at competitive prices. {product_data['description'][:150]}..."
        logger.info(f"Meta title: {meta_title}, Meta description: {meta_description[:50]}...")

        if product_data['name'] == "Unknown Product":
            logger.warning("Product name not found, returning None")
            return None

        product = {
            'name': product_data['name'],
            'slug': product_data['name'].lower().replace(' ', '-').replace('/', '-')[:50],
            'description': product_data['description'],
            'price': product_data['price'],
            'below_moq_price': product_data['below_moq_price'],
            'moq': product_data['moq'],
            'moq_per_person': 1,
            'moq_status': 'not_applicable',
            'category_id': default_category_id,
            'supplier_id': default_supplier_id,
            'supplier_name': product_data['supplier_name'],
            'supplier_link': product_data['supplier_link'],
            'supplier_info': product_data['supplier_info'],
            'meta_title': meta_title,
            'meta_description': meta_description,
            'attribute_value_ids': product_data['attribute_value_ids'],
            'thumbnail': product_data['thumbnail'],
            'images': [product_data['thumbnail']] if product_data['thumbnail'] else [],
            'alibaba_product_id': product_data['product_id']
        }
        logger.info(f"Returning product: {product_data['name']}")
        return product

    def parse_shein_single_product(self, soup):
        logger.info("Starting parse_shein_single_product method")
        logger.info("Creating or retrieving Shein category")
        default_category, _ = Category.objects.get_or_create(
            name="Shein",
            defaults={"slug": "shein", "description": "Products scraped from Shein", "is_active": True}
        )
        default_category_id = default_category.id
        default_supplier_id = None
        logger.info(f"Default category ID for Shein: {default_category_id}")

        product_data = {}

        # Extract product name
        logger.info("Extracting product name")
        name_elem = soup.select_one('h1.product-intro__head-name')
        product_data['name'] = name_elem.text.strip() if name_elem else 'Unknown Product'
        logger.info(f"Product name: {product_data['name']}")

        # Extract price
        logger.info("Extracting product price")
        price_elem = soup.select_one('div.product-intro__head-mainprice')
        price_text = price_elem.text.strip().replace('€', '').replace('$', '').replace(',', '') if price_elem else '0.0'
        try:
            if '-' in price_text:
                prices = price_text.split('-')
                price_usd = float(prices[0].strip())
                below_moq_price_usd = float(prices[1].strip())
            else:
                price_usd = float(price_text)
                below_moq_price_usd = price_usd * 1.2
        except ValueError:
            logger.warning(f"Invalid price format: {price_text}, defaulting to 0.0")
            price_usd = 0.0
            below_moq_price_usd = 0.0

        # Convert USD to KES
        USD_TO_KES_RATE = 130.50
        price_kes = price_usd * USD_TO_KES_RATE
        below_moq_price_kes = below_moq_price_usd * USD_TO_KES_RATE

        # Round to 2 decimal places, then to nearest shilling if needed
        price_kes = round(price_kes, 2)
        below_moq_price_kes = round(below_moq_price_kes, 2)
        if price_kes % 1 > 0:
            price_kes = round(price_kes)
        if below_moq_price_kes % 1 > 0:
            below_moq_price_kes = round(below_moq_price_kes)
        product_data['price'] = price_kes
        product_data['below_moq_price'] = below_moq_price_kes
        logger.info(f"Price in KES: {product_data['price']}, Below MOQ in KES: {product_data['below_moq_price']}")

        # Extract description
        logger.info("Extracting product description")
        desc_elem = soup.select_one('div.product-intro__description')
        product_data['description'] = desc_elem.text.strip() if desc_elem else 'No description available'
        logger.info(f"Description: {product_data['description']}")

        # Extract thumbnail
        logger.info("Extracting thumbnail")
        thumbnail_elem = soup.select_one('img.product-intro__main-image')
        product_data['thumbnail'] = thumbnail_elem['src'] if thumbnail_elem and 'src' in thumbnail_elem.attrs else ""
        logger.info(f"Thumbnail URL: {product_data['thumbnail']}")

        # Extract attributes (variations)
        logger.info("Extracting product variations")
        attribute_value_ids = []
        variation_sections = soup.select('div.product-intro__sku-item')  # Shein variation container
        for variation in variation_sections:
            attr_name_elem = variation.select_one('span.sku-title')
            attr_name = attr_name_elem.text.strip().replace(':', '').lower() if attr_name_elem else None
            if not attr_name:
                continue
            logger.info(f"Found variation attribute: {attr_name}")

            try:
                attribute = Attribute.objects.filter(name__iexact=attr_name).first()
                if not attribute:
                    logger.info(f"Creating new attribute: {attr_name}")
                    attribute = Attribute.objects.create(name=attr_name)
            except Exception as e:
                logger.error(f"Error creating attribute {attr_name}: {str(e)}")
                continue

            attr_values = variation.select('div.sku-item-option')
            for value_elem in attr_values:
                attr_value = value_elem.text.strip().lower()
                if not attr_value:
                    continue
                logger.info(f"Found attribute value: {attr_value} for attribute: {attr_name}")

                try:
                    attribute_value = AttributeValue.objects.filter(attribute=attribute, value__iexact=attr_value).first()
                    if not attribute_value:
                        logger.info(f"Creating new attribute value: {attr_value} for attribute: {attr_name}")
                        attribute_value = AttributeValue.objects.create(attribute=attribute, value=attr_value)
                    attribute_value_ids.append(attribute_value.id)
                except Exception as e:
                    logger.error(f"Error creating attribute value {attr_value} for {attr_name}: {str(e)}")
                    continue

        product_data['attribute_value_ids'] = attribute_value_ids
        logger.info(f"Attribute value IDs: {attribute_value_ids}")

        # Prepare metadata
        logger.info("Preparing metadata")
        meta_title = f"{product_data['name']} - Shop Now at Great Prices"
        meta_description = f"Discover {product_data['name']} at our store. {product_data['description'][:150]}..."
        logger.info(f"Meta title: {meta_title}, Meta description: {meta_description[:50]}...")

        if product_data['name'] == "Unknown Product":
            logger.warning("Product name not found, returning None")
            return None

        product = {
            'name': product_data['name'],
            'slug': product_data['name'].lower().replace(' ', '-').replace('/', '-')[:50],
            'description': product_data['description'],
            'price': product_data['price'],
            'below_moq_price': product_data['below_moq_price'],
            'moq': 1,
            'moq_per_person': 1,
            'moq_status': 'not_applicable',
            'category_id': default_category_id,
            'supplier_id': default_supplier_id,
            'meta_title': meta_title,
            'meta_description': meta_description,
            'attribute_value_ids': product_data['attribute_value_ids'],
            'thumbnail': product_data['thumbnail'],
            'images': [product_data['thumbnail']] if product_data['thumbnail'] else []
        }
        logger.info(f"Returning product: {product_data['name']}")
        return product