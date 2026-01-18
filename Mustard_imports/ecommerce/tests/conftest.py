import os
import django
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Mustard_imports.settings")

# Initialize Django before any tests are run
django.setup()

from ecommerce.models import (
    Category, Product, Inventory, ShippingMethod,
    Cart, Order, DeliveryLocation
)

User = get_user_model()


@pytest.fixture(scope="session")
def django_db_setup():
    """Set up Django database configuration."""
    pass


@pytest.fixture
def user_factory(db):
    """Factory for creating test users."""
    def create_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        password = defaults.pop('password')
        user = User.objects.create_user(password=password, **defaults)
        return user
    return create_user


@pytest.fixture
def category(db):
    """Create default category."""
    return Category.objects.create(name='Electronics', slug='electronics')


@pytest.fixture
def product_factory(db, category):
    """Factory for creating test products."""
    def create_product(**kwargs):
        defaults = {
            'name': 'Test Product',
            'price': Decimal('1000.00'),
            'category': category,
            'moq': 1
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)
    return create_product


@pytest.fixture
def pick_and_pay_product(db, product_factory):
    """Create Pick & Pay product with inventory."""
    product = product_factory(
        name='Pick & Pay Product',
        price=Decimal('500.00'),
        is_pick_and_pay=True
    )
    Inventory.objects.create(product=product, quantity=20)
    return product


@pytest.fixture
def moq_product(db, product_factory):
    """Create MOQ group buy product."""
    return product_factory(
        name='MOQ Product',
        price=Decimal('5000.00'),
        below_moq_price=Decimal('6000.00'),
        moq=50,
        moq_per_person=5,
        moq_status='active',
        is_pick_and_pay=False
    )


@pytest.fixture
def shipping_method(db):
    """Create default shipping method."""
    return ShippingMethod.objects.create(
        name='Standard Shipping',
        price=Decimal('200.00'),
        is_active=True
    )


@pytest.fixture
def user(db, user_factory):
    """Create default test user."""
    return user_factory()


@pytest.fixture
def admin_user(db, user_factory):
    """Create admin user."""
    return user_factory(
        username='adminuser',
        email='admin@example.com',
        user_type='admin',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def cart(db, user):
    """Create cart for user."""
    return Cart.objects.create(user=user)


@pytest.fixture
def delivery_location(db, user):
    """Create delivery location for user."""
    return DeliveryLocation.objects.create(
        user=user,
        county='Nairobi',
        ward='Westlands',
        address='123 Test Street',
        is_default=True
    )