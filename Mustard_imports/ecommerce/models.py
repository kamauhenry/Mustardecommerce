from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin, AbstractBaseUser
import string
import random
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.files import File
from PIL import Image
from io import BytesIO
from django.db.models import Sum
from django.conf import settings
from django.utils.text import slugify
import logging
import os





class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('is_verified', True) # Superusers are always verified

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    user_type = models.CharField(max_length=20, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    points = models.IntegerField(default=0)
    affiliate_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    reset_token = models.CharField(max_length=32, blank=True, null=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.affiliate_code:
            self.affiliate_code = self.generate_affiliate_code()
        super().save(*args, **kwargs)

    def generate_affiliate_code(self):
        length = 4
        characters = string.ascii_uppercase + string.digits
        max_attempts = 10
        for _ in range(max_attempts):
            code = ''.join(random.choice(characters) for _ in range(length))
            if not User.objects.filter(affiliate_code=code).exists():
                return code
        raise ValueError('Unable to generate unique affiliate code after multiple attempts')

class AdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    admin_level = models.CharField(max_length=20, default='senior', choices=[
        ('standard', 'Standard Admin'),
        ('senior', 'Senior Admin'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.user.user_type = 'admin'
        self.user.is_staff = True
        self.user.is_active = True
        self.user.is_verified = True
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Admin: {self.user.username}"

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

class DeliveryLocation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_locations', null=True, blank=True)

    county = models.CharField(max_length=100, default="shop pick up")
    ward = models.CharField(max_length=100, default="shop pick up")
    is_shop_pickup = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username if self.user else 'Global'})"

    def save(self, *args, **kwargs):
        if self.is_default and self.user:
            DeliveryLocation.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}'
    
class CategoryImage(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def __str__(self):
        return f"Image for {self.category.name}"
  
    def get_image(self):
        if self.image:
            return 'https://mustardimports.co.ke/' + self.image.url
        return ''

    def get_primary_image(self):
        first_image = self.category.images.first()
        return first_image.get_image() if first_image else ''

class Attribute(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)

    class Meta:
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class Product(models.Model):
    MOQ_STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
        ('not_applicable', 'Not Applicable'),
    )

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    below_moq_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    moq = models.IntegerField(default=1, help_text="Minimum Order Quantity required for group buy")
    moq_status = models.CharField(max_length=20, choices=MOQ_STATUS_CHOICES, default='active')
    moq_per_person = models.IntegerField(default=1, help_text="Minimum quantity allowed per person in group buy")
    is_pick_and_pay = models.BooleanField(default=False, help_text="Indicates if product is available for immediate purchase without MOQ")
    attribute_values = models.ManyToManyField('AttributeValue', related_name='products', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        # Ensure MOQ fields are set to default for Pick and Pay products
        if self.is_pick_and_pay:
            self.moq = 1
            self.moq_status = 'not_applicable'
            self.moq_per_person = 1
            self.below_moq_price = None
        super().save(*args, **kwargs)

    def current_moq_count(self):
        if self.moq_status != 'active' or self.is_pick_and_pay:
            return 0
        order_items = OrderItem.objects.filter(
            product=self,
            order__payment_status='paid'
        )
        return sum(item.quantity for item in order_items)

    def moq_progress_percentage(self):
        if self.is_pick_and_pay or self.moq <= 1 or self.moq_status != 'active':
            return 100
        current = self.current_moq_count()
        return min(300, int((current / self.moq) * 100))

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'

    def get_primary_image(self):
        first_image = self.images.first()
        return first_image.get_image() if first_image else ''

    def get_primary_thumbnail(self):
        first_image = self.images.first()
        return first_image.get_thumbnail() if first_image else ''

    def available_stock(self):
        if not self.is_pick_and_pay:
            return None  # Stock tracking only for Pick and Pay
        return self.inventory.quantity if self.inventory else 0

class Inventory(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory',
        limit_choices_to={'is_pick_and_pay': True}
    )
    quantity = models.PositiveIntegerField(default=0, help_text="Current stock level")
    low_stock_threshold = models.PositiveIntegerField(default=10, help_text="Threshold for low stock alerts")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inventory for {self.product.name} (Stock: {self.quantity})"

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def reduce_stock(self, quantity):
        if not self.product.is_pick_and_pay:
            raise ValueError("Stock reduction only applies to Pick and Pay products")
        if self.quantity < quantity:
            raise ValueError(f"Insufficient stock for {self.product.name}. Available: {self.quantity}, Requested: {quantity}")
        self.quantity -= quantity
        self.save()

    def restock(self, quantity):
        if not self.product.is_pick_and_pay:
            raise ValueError("Restocking only applies to Pick and Pay products")
        self.quantity += quantity
        self.save()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)

    def get_image(self):
        if self.image:
            return settings.SITE_URL + self.image.url.lstrip('/')
        return ''

    def get_thumbnail(self):
        if self.thumbnail:
            return settings.SITE_URL + self.thumbnail.url.lstrip('/')
        elif self.image:
            try:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()
                return settings.SITE_URL + self.thumbnail.url.lstrip('/')
            except Exception as e:

                return self.get_image()  # Fallback to main image
        return ''

    def make_thumbnail(self, image, size=(200, 100)):
        try:
            img = Image.open(image)
            img.verify()  # Verify image integrity
            img = Image.open(image)  # Reopen after verify
            img = img.convert('RGB')
            img.thumbnail(size)
            thumb_io = BytesIO()
            img.save(thumb_io, 'JPEG', quality=85)
            filename = os.path.splitext(os.path.basename(image.name))[0] + '.jpg'
            thumbnail = File(thumb_io, name=filename)
            return thumbnail
        except Exception as e:

            raise

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (KES {self.price})"

    class Meta:
        ordering = ['name']

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def shipping_cost(self):
        # No shipping cost if all items are Pick and Pay
        if all(item.product.is_pick_and_pay for item in self.items.all()):
            return 0
        return self.shipping_method.price if self.shipping_method else 0

    @property
    def total(self):
        return self.subtotal + self.shipping_cost

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attributes = models.JSONField(default=dict, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        pass

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

    def save(self, *args, **kwargs):
        if self.product.is_pick_and_pay:
            available = self.product.available_stock()
            if available < self.quantity:
                raise ValueError(f"Cannot add {self.quantity} of {self.product.name}. Only {available} in stock.")
        super().save(*args, **kwargs)

    @property
    def price_per_piece(self):
        if self.product.is_pick_and_pay:
            return self.product.price
        if self.product.moq_status == 'active':
            if self.quantity < self.product.moq_per_person:
                price = self.product.below_moq_price if self.product.below_moq_price is not None else self.product.price
            else:
                price = self.product.price
        else:
            price = self.product.price
        return price

    @property
    def line_total(self):
        return self.price_per_piece * self.quantity

class Order(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    )

    DELIVERY_STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('ready_for_pickup', 'Ready for Pickup'),  # Added for Pick and Pay
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_method = models.ForeignKey(
        ShippingMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_location = models.ForeignKey('DeliveryLocation', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        is_pick_and_pay_order = all(item.product.is_pick_and_pay for item in self.items.all()) if self.pk else False
        if is_pick_and_pay_order:
            self.shipping_cost = Decimal('0.00')
            self.shipping_method = None
            self.delivery_status = 'ready_for_pickup'
        elif not self.pk and self.shipping_method:
            self.shipping_cost = Decimal(str(self.shipping_method.price))

        super().save(*args, **kwargs)
        if self.pk:
            self.total_price = self.calculate_total_price()
            super().save(update_fields=['total_price'])

    def calculate_total_price(self):
        items_total = sum(item.quantity * item.price for item in self.items.all())
        shipping_cost = Decimal(str(self.shipping_cost))

        return items_total + shipping_cost

    def update_total_price(self):
        self.total_price = self.calculate_total_price()
        self.save(update_fields=['total_price'])

    def remove_item(self, order_item):
        order_item.delete()
        self.update_total_price()

    def mark_as_completed(self):
        if self.delivery_status in ('delivered', 'ready_for_pickup') and self.payment_status == 'paid':
            try:
                completed_order = CompletedOrder.objects.create(
                    order_number=f"ORD-MI{self.id}",
                    user=self.user,
                    shipping_method=self.shipping_method.name if self.shipping_method else 'Pick and Pay',
                    order_date=self.created_at,
                    original_order=self,
                    delivery_location=self.delivery_location
                )
                return completed_order
            except Exception as e:
                print(f"Error creating completed order: {e}")
        return None

    @property
    def order_number(self):
        return f"MI{self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['delivery_status']),
        ]

    def __str__(self):
        return f"Order #MI{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attributes = models.JSONField(default=dict, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.product.is_pick_and_pay:
            available = self.product.available_stock()
            if available < self.quantity:
                raise ValueError(f"Cannot order {self.quantity} of {self.product.name}. Only {available} in stock.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('mpesa', 'M-Pesa'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment',
        primary_key=True
    )
    phone_number = models.CharField(
        max_length=20,
        null=False,
        blank=False
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='mpesa'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    mpesa_checkout_request_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        unique=True,
        help_text="Unique ID from M-Pesa STK Push request"
    )
    mpesa_receipt_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        unique=True,
        help_text="M-Pesa transaction receipt number (e.g., QJ1234567890)"
    )
    error_message = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Reason for payment failure, if any"
    )

    def __str__(self):
        return f"Payment for Order #{self.order.id}"

    def save(self, *args, **kwargs):
        if not self.amount:
            self.amount = self.order.total_price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

class CompletedOrder(models.Model):
    original_order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, related_name='completed_order')
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_orders')
    shipping_method = models.CharField(max_length=100)  # Store name instead of ForeignKey
    mpesa_confirmation_code = models.CharField(max_length=50, null=True, blank=True)
    order_date = models.DateTimeField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    completion_date = models.DateTimeField(auto_now_add=True)
    delivery_location = models.ForeignKey(DeliveryLocation, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Completed Order #{self.order_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user.points = int(self.user.points + 1.5)
        self.user.save(update_fields=['points'])

    @property
    def items(self):
        return self.original_order.items.all()

    @property
    def total_price(self):
        return self.original_order.total_price

class CustomerReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        product = self.product
        avg_rating = CustomerReview.objects.filter(product=product).aggregate(
            models.Avg('rating')
        )['rating__avg'] or 0
        product.rating = round(avg_rating, 2)
        product.save(update_fields=['rating'])

class MOQRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moq_requests')
    product_name = models.CharField(max_length=255)
    product_link = models.URLField()
    quantity = models.IntegerField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MOQ Request: {self.product_name}"