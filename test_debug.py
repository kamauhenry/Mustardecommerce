import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Mustard_imports.settings")
django.setup()

from ecommerce.models import Category, Product
from ecommerce.api.serializers import ProductSerializer, LoginSerializer, AdminLoginSerializer
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

print("=" * 60)
print("TEST 1: ProductSerializer Basic Creation")
print("=" * 60)
category = Category.objects.create(name="Electronics", slug="electronics")
data = {
    'name': 'Test Product',
    'price': '1000.00',
    'category_id': category.id,
    'moq': 1
}
serializer = ProductSerializer(data=data)
is_valid = serializer.is_valid()
print(f"Is valid: {is_valid}")
if not is_valid:
    print(f"Errors: {serializer.errors}")

print("\n" + "=" * 60)
print("TEST 2: LoginSerializer Valid Credentials")
print("=" * 60)
user = User.objects.create_user(
    username='testuser123',
    email='test123@example.com',
    password='testpass123'
)
data = {
    'username': 'testuser123',
    'password': 'testpass123'
}
serializer = LoginSerializer(data=data)
is_valid = serializer.is_valid()
print(f"Is valid: {is_valid}")
if not is_valid:
    print(f"Errors: {serializer.errors}")

print("\n" + "=" * 60)
print("TEST 3: AdminLoginSerializer")
print("=" * 60)
admin = User.objects.create_user(
    username='adminuser123',
    email='admin123@example.com',
    password='adminpass123',
    user_type='admin',
    is_staff=True,
    is_superuser=True
)
data = {
    'username': 'adminuser123',
    'password': 'adminpass123'
}
serializer = AdminLoginSerializer(data=data)
is_valid = serializer.is_valid()
print(f"Is valid: {is_valid}")
if not is_valid:
    print(f"Errors: {serializer.errors}")

# Cleanup
category.delete()
user.delete()
admin.delete()
