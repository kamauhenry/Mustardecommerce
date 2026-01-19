from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from ecommerce.models import *
from unittest.mock import patch
import threading
import json

User = get_user_model()

# Order Concurrency Test
class OrderConcurrencyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(name='Test Product', description="Test product", price=10.00, moq=1, category=self.category)
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
        )
    
    def test_concurrent_order_creation(self):
        def create_order():
            response = self.client.post(
                reverse('create-order-from-cart', args=[self.cart.id]),
                {'shipping_method': 'standard'},
                format='json'
            )
            return response

        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_order)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        orders = Order.objects.filter(user=self.user)
        self.assertEqual(orders.count(), 1)  # Adjusted expectation

# Bulk Update Order Status Test
class BulkUpdateOrderStatusTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='mustardimports', email='admin@mustardimports.com', password='mustard1q2w3e4r', user_type='admin'
        )
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.orders = [
            Order.objects.create(user=self.user, delivery_status='processing'),
            Order.objects.create(user=self.user, delivery_status='processing'),
        ]
    
    def test_bulk_update_order_status(self):
        response = self.client.post(
            reverse('bulk_update_order_status'),
            {'order_ids': [o.id for o in self.orders], 'delivery_status': 'shipped'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['message'],
            f"Successfully updated {len(self.orders)} orders to shipped"
        )
        for order in Order.objects.filter(id__in=[o.id for o in self.orders]):
            self.assertEqual(order.delivery_status, 'shipped')

# Authentication Tests
class AuthenticationTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.client = APIClient()

    def test_admin_registration(self):
        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'newadminpass',
            'first_name': 'Admin',
            'last_name': 'User',
            'phone_number': '254712345678',
            'user_type': 'admin'
        }
        response = self.client.post(reverse('admin_register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        user = User.objects.get(username='newadmin')
        self.assertEqual(user.user_type, 'admin')

    def test_admin_login(self):
        admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass',
            user_type='admin'
        )
        data = {
            'username': 'adminuser',
            'password': 'adminpass'
        }
        response = self.client.post(reverse('admin_login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newuserpass',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '254712345678'
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.user_type, 'customer')

    def test_user_login(self):
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    @patch('google.oauth2.id_token.verify_oauth2_token')
    def test_google_auth(self, mock_verify):
        mock_verify.return_value = {
            'email': 'googleuser@example.com',
            'name': 'Google User'
        }
        data = {'access_token': 'fake-token'}
        response = self.client.post(reverse('google-auth'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        user = User.objects.get(email='googleuser@example.com')
        self.assertEqual(user.username, 'googleuser@example.com')

# Cart Management Tests
class CartManagementTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.product = Product.objects.create(name='Test Product', description="Test product", price=10.00, moq=1, category=self.category)
        self.cart = Cart.objects.create(user=self.user)
    
    def test_create_cart(self):
        response = self.client.get(reverse('get-user-cart', args=[self.user.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.cart.id)

    def test_add_item_to_cart(self):
        data = {
            'productId': self.product.id,
            'quantity': 2
        }
        response = self.client.post(reverse('add-item-to-cart', args=[self.cart.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cart_item = CartItem.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(cart_item.quantity, 2)

    def test_update_cart_item_quantity(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        data = {'quantity': 3, 'cart_id': self.cart.id}
        response = self.client.post(reverse('update-cart-item-quantity', args=[cart_item.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)

    def test_remove_cart_item(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        data = {'item_id': cart_item.id}
        response = self.client.post(reverse('remove-cart-item', args=[self.cart.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.assertRaises(CartItem.DoesNotExist):
            CartItem.objects.get(id=cart_item.id)

# Order Management Tests
class OrderManagementTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.shipping = ShippingMethod.objects.create(name='Standard', price=100.00)
        self.order = Order.objects.create(
            user=self.user,
            shipping_method=self.shipping,
            payment_status='pending',
            delivery_status='processing'
        )
    
    def test_update_order_shipping(self):
        express_shipping = ShippingMethod.objects.create(name='Express', price=200.00)
        data = {'shipping_method': express_shipping.id}
        response = self.client.put(reverse('update-order-shipping', args=[self.order.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.shipping_method.id, express_shipping.id)

    def test_get_user_orders(self):
        response = self.client.get(reverse('get-user-orders'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.order.id)

# Payment Processing Tests
class PaymentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.order = Order.objects.create(
            user=self.user,
            total_price=100.00,
            payment_status='pending'
        )

    @patch('ecommerce.api.views_orders.send_stk_push')    
    def test_process_payment(self, mock_send_stk_push):
        mock_send_stk_push.return_value = {
            "ResponseCode": "0",
            "CheckoutRequestID": "ws_CO_123456789"
        }
        data = {
            'order_id': self.order.id,
            'phone_number': '254712345678'
        }
        response = self.client.post(reverse('process_payment'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.payment_status, 'pending')
        self.assertEqual(payment.mpesa_checkout_request_id, 'ws_CO_123456789')

    @patch('ecommerce.api.views_orders.query_stk_push')
    def test_get_payment_details(self, mock_query_stk_push):
        payment = Payment.objects.create(
            order=self.order,
            phone_number='254712345678',
            amount=100.00,
            payment_method='mpesa',
            payment_status='pending',
            mpesa_checkout_request_id='ws_CO_123456789'
        )
        mock_query_stk_push.return_value = {
            "ResultCode": "0",
            "MpesaReceiptNumber": "ABC123"
        }
        response = self.client.get(reverse('get_payment_details', args=[self.order.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(payment.payment_status, 'completed')
        self.assertEqual(payment.mpesa_receipt_number, 'ABC123')

    def test_mpesa_callback(self):
        payment = Payment.objects.create(
            order=self.order,
            phone_number='254712345678',
            amount=100.00,
            payment_method='mpesa',
            payment_status='pending',
            mpesa_checkout_request_id='ws_CO_123456789'
        )
        callback_data = {
            "Body": {
                "stkCallback": {
                    "CheckoutRequestID": "ws_CO_123456789",
                    "ResultCode": 0,
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 100},
                            {"Name": "MpesaReceiptNumber", "Value": "ABC123"},
                            {"Name": "PhoneNumber", "Value": "254712345678"}
                        ]
                    }
                }
            }
        }
        response = self.client.post(
            reverse('mpesa-callback'),
            json.dumps(callback_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        payment.refresh_from_db()
        self.assertEqual(payment.payment_status, 'completed')
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')

# Admin Operation Tests
class AdminOperationTest(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin', email='admin@example.com', password='adminpass', user_type='admin'
        )
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.order = Order.objects.create(user=self.user, delivery_status='processing')
    
    def test_admin_dashboard(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_sales', response.data)

    def test_get_all_orders(self):
        response = self.client.get(reverse('get_all_orders'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['id'], self.order.id)

    def test_update_single_order_status(self):
        data = {'status': 'shipped'}  # Assuming view accepts 'status'
        response = self.client.post(reverse('update_single_order_status', args=[self.order.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.delivery_status, 'shipped')

# Product and Category Tests
class ProductCategoryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product', price=10.00, moq=1, category=self.category, slug='test-product'
        )

    def test_search_products(self):
        response = self.client.get(reverse('search') + '?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['name'], 'Test Product')

    def test_get_product_details(self):
        response = self.client.get(reverse('product-detail', args=['test-category', 'test-product']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')

    def test_get_category_products(self):
        response = self.client.get(reverse('category-products', args=['test-category']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['products'][0]['name'], 'Test Product')

# User Profile and Delivery Location Tests
class UserProfileDeliveryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass'
        )
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_get_user_profile(self):
        response = self.client.get(reverse('user-profile'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_update_user_profile(self):
        data = {'first_name': 'New Name', 'email': 'newemail@example.com'}
        response = self.client.put(reverse('user-profile'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'New Name')
        # Avatar field removed from assertions

    def test_create_delivery_location(self):
        data = {'name': 'Home', 'address': '123 Test St', 'latitude': 1.0, 'longitude': 2.0}
        response = self.client.post(reverse('delivery_locations'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        location = DeliveryLocation.objects.get(user=self.user)
        self.assertEqual(location.address, '123 Test St')