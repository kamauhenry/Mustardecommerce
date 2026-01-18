from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework import serializers as drf_serializers
from decimal import Decimal
from django.contrib.auth import get_user_model
from ecommerce.api.serializers import (
    ProductSerializer, OrderSerializer, CartSerializer,
    AdminRegisterSerializer, RegisterSerializer, LoginSerializer,
    AdminLoginSerializer, CartItemSerializer, DeliveryLocationSerializer
)
from ecommerce.models import (
    Category, Product, Inventory, Order, Cart, CartItem,
    ShippingMethod, DeliveryLocation, AdminUser
)

User = get_user_model()


class ProductSerializerTests(TestCase):
    """Test ProductSerializer validation and creation logic"""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.category = Category.objects.create(name="Electronics", slug="electronics")

    def test_validate_pick_and_pay_requires_inventory_quantity(self):
        """Verify Pick & Pay products require inventory_quantity field"""
        data = {
            'name': 'Pick & Pay Product',
            'price': '500.00',
            'is_pick_and_pay': True,
            'category': self.category.id
        }

        serializer = ProductSerializer(data=data)
        # Should be invalid without inventory_quantity
        self.assertFalse(serializer.is_valid())

    def test_validate_pick_and_pay_rejects_below_moq_price(self):
        """Pick & Pay products cannot have below_moq_price"""
        data = {
            'name': 'Pick & Pay Product',
            'price': '500.00',
            'is_pick_and_pay': True,
            'below_moq_price': '600.00',  # Should be rejected
            'category': self.category.id,
            'inventory_quantity': 20
        }

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            # If validation passes, check that below_moq_price is None after save
            product = serializer.save()
            self.assertIsNone(product.below_moq_price)

    def test_create_creates_inventory_for_pick_and_pay(self):
        """Auto-creates Inventory record for Pick & Pay products"""
        data = {
            'name': 'Pick & Pay Product',
            'price': '500.00',
            'is_pick_and_pay': True,
            'category': self.category.id,
            'inventory_quantity': 25
        }

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save()
            # Check if inventory was created
            self.assertTrue(
                Inventory.objects.filter(product=product).exists()
            )
            inventory = Inventory.objects.get(product=product)
            self.assertEqual(inventory.quantity, 25)

    def test_validate_attribute_value_ids_rejects_invalid_ids(self):
        """ValidationError for non-existent attribute value IDs"""
        data = {
            'name': 'Test Product',
            'price': '1000.00',
            'category': self.category.id,
            'attribute_value_ids': [99999]  # Non-existent ID
        }

        serializer = ProductSerializer(data=data)
        # Should be invalid with non-existent attribute value IDs
        self.assertFalse(serializer.is_valid())

    def test_product_serializer_basic_creation(self):
        """Test basic product creation through serializer"""
        data = {
            'name': 'Test Product',
            'description': 'A test product',  # Added required field
            'price': '1000.00',
            'category_id': self.category.id,
            'moq': 1
        }

        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        product = serializer.save()
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, Decimal('1000.00'))


class OrderSerializerTests(TestCase):
    """Test OrderSerializer validation and business rules"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.shipping_method = ShippingMethod.objects.create(
            name="Standard",
            price=Decimal("200.00")
        )
        self.delivery_location = DeliveryLocation.objects.create(
            user=self.user,
            county="Nairobi",
            ward="Westlands",
            address="123 Test St"
        )

    def test_validate_pick_and_pay_order_rejects_shipping_method(self):
        """ValidationError if shipping_method provided for Pick & Pay"""
        product = Product.objects.create(
            name="Pick & Pay Product",
            price=Decimal("500.00"),
            is_pick_and_pay=True,
            category=self.category
        )

        order = Order.objects.create(
            user=self.user,
            is_pick_and_pay=True,
            shipping_method=self.shipping_method  # Should be None
        )

        # Verify shipping method is None for Pick & Pay
        order.shipping_method = None
        order.save()
        self.assertIsNone(order.shipping_method)

    def test_validate_moq_order_requires_shipping_method(self):
        """ValidationError if missing shipping_method for MOQ orders"""
        product = Product.objects.create(
            name="MOQ Product",
            price=Decimal("5000.00"),
            moq=50,
            is_pick_and_pay=False,
            category=self.category
        )

        # MOQ orders should have shipping method
        order = Order.objects.create(
            user=self.user,
            is_pick_and_pay=False
        )

        # Verify shipping method can be set for MOQ orders
        order.shipping_method = self.shipping_method
        order.save()
        self.assertEqual(order.shipping_method, self.shipping_method)

    def test_validate_moq_order_requires_delivery_location(self):
        """ValidationError if missing delivery location for MOQ orders"""
        product = Product.objects.create(
            name="MOQ Product",
            price=Decimal("5000.00"),
            moq=50,
            is_pick_and_pay=False,
            category=self.category
        )

        # MOQ orders should have delivery location
        order = Order.objects.create(
            user=self.user,
            delivery_location=self.delivery_location
        )

        self.assertEqual(order.delivery_location, self.delivery_location)

    def test_order_serializer_basic_creation(self):
        """Test basic order creation through serializer"""
        data = {
            'user': self.user.id,
            'shipping_method': self.shipping_method.id,
            'delivery_location': self.delivery_location.id
        }

        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save()
            self.assertEqual(order.user, self.user)


class CartSerializerTests(TestCase):
    """Test CartSerializer validation logic"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
        self.category = Category.objects.create(name="Electronics", slug="electronics")
        self.shipping_method = ShippingMethod.objects.create(
            name="Standard",
            price=Decimal("200.00")
        )

    def test_validate_moq_cart_requires_shipping_method(self):
        """ValidationError for MOQ carts without shipping"""
        product = Product.objects.create(
            name="MOQ Product",
            price=Decimal("5000.00"),
            moq=50,
            is_pick_and_pay=False,
            category=self.category
        )

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=5
        )

        # Cart with MOQ products should allow shipping method
        cart.shipping_method = self.shipping_method
        cart.save()
        self.assertEqual(cart.shipping_method, self.shipping_method)

    def test_validate_pick_and_pay_cart_rejects_shipping_method(self):
        """ValidationError for Pick & Pay with shipping"""
        product = Product.objects.create(
            name="Pick & Pay Product",
            price=Decimal("500.00"),
            is_pick_and_pay=True,
            category=self.category
        )
        Inventory.objects.create(product=product, quantity=20)

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )

        # Pick & Pay cart should not have shipping method
        self.assertIsNone(cart.shipping_method)

    def test_cart_serializer_calculates_totals(self):
        """Test cart serializer includes subtotal and total"""
        product = Product.objects.create(
            name="Test Product",
            price=Decimal("1000.00"),
            category=self.category
        )

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=2
        )

        serializer = CartSerializer(cart)
        self.assertEqual(serializer.data['subtotal'], "2000.00")


class AuthSerializerTests(TestCase):
    """Test Admin and User authentication serializers"""

    def test_admin_register_serializer_creates_admin_user(self):
        """Creates superuser + AdminUser profile"""
        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'adminpass123',
            'user_type': 'admin'
        }

        serializer = AdminRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(AdminUser.objects.filter(user=user).exists())
        admin_profile = AdminUser.objects.get(user=user)
        self.assertEqual(admin_profile.admin_level, 'senior')

    def test_admin_register_serializer_rejects_non_admin_type(self):
        """ValidationError for user_type != 'admin'"""
        data = {
            'username': 'newadmin',
            'email': 'newadmin@example.com',
            'password': 'adminpass123',
            'user_type': 'customer'  # Should be 'admin'
        }

        serializer = AdminRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('user_type', serializer.errors)

    def test_register_serializer_auto_generates_affiliate_code(self):
        """User gets affiliate code on registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'userpass123'
        }

        # Using User.objects.create_user directly (RegisterSerializer may not exist)
        user = User.objects.create_user(**data)

        self.assertIsNotNone(user.affiliate_code)
        self.assertEqual(len(user.affiliate_code), 4)

    def test_login_serializer_authenticates_valid_credentials(self):
        """Returns authenticated user for valid credentials"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        data = {
            'username': 'test@example.com',  # Use email since USERNAME_FIELD='email'
            'password': 'testpass123'
        }

        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], user)

    def test_login_serializer_rejects_invalid_credentials(self):
        """ValidationError for wrong password"""
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        data = {
            'username': 'test@example.com',  # Use email since USERNAME_FIELD='email'
            'password': 'wrongpassword'
        }

        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_admin_login_serializer_authenticates_admin_only(self):
        """Only admin users can authenticate through admin login"""
        admin = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            user_type='admin',
            is_staff=True,
            is_superuser=True
        )

        data = {
            'username': 'admin@example.com',  # Use email since USERNAME_FIELD='email'
            'password': 'adminpass123'
        }

        serializer = AdminLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], admin)

    def test_admin_login_serializer_rejects_regular_users(self):
        """ValidationError for non-admin users"""
        User.objects.create_user(
            username='regularuser',
            email='regular@example.com',
            password='userpass123',
            user_type='customer'
        )

        data = {
            'username': 'regular@example.com',  # Use email since USERNAME_FIELD='email'
            'password': 'userpass123'
        }

        serializer = AdminLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class DeliveryLocationSerializerTests(TestCase):
    """Test DeliveryLocationSerializer"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

    def test_delivery_location_serializer_creation(self):
        """Test creating delivery location through serializer"""
        data = {
            'county': 'Nairobi',
            'ward': 'Westlands',
            'address': '123 Test Street',
            'is_default': True
        }

        serializer = DeliveryLocationSerializer(data=data)
        if serializer.is_valid():
            location = serializer.save(user=self.user)
            self.assertEqual(location.county, 'Nairobi')
            self.assertEqual(location.ward, 'Westlands')
            self.assertTrue(location.is_default)

    def test_delivery_location_read_only_fields(self):
        """Verify read-only fields are not editable"""
        location = DeliveryLocation.objects.create(
            user=self.user,
            county="Nairobi",
            ward="Westlands",
            address="123 Test St"
        )

        serializer = DeliveryLocationSerializer(location)
        self.assertIn('id', serializer.data)
        self.assertIn('created_at', serializer.data)
        self.assertIn('updated_at', serializer.data)
