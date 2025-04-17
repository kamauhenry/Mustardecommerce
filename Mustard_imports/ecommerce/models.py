from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin,AbstractBaseUser
import string
import random
from django.db import models
from django.utils import timezone
from django.core.files import File
from PIL import Image
from io import BytesIO
from django.db.models import Sum 
from django.conf import settings

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


    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Generate affiliate code if none exists
        if not self.affiliate_code:
            self.affiliate_code = self.generate_affiliate_code()
        super().save(*args, **kwargs)

    def generate_affiliate_code(self):
        """Generate a unique 8-character affiliate code."""
        length = 8
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
        self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Admin: {self.user.username}"

class DeliveryLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_locations')
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)  # Add latitude field
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def save(self, *args, **kwargs):
        # Ensure only one location is default per user
        if self.is_default:
            DeliveryLocation.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)  # Add description field
    is_active = models.BooleanField(default=True)  # Added is_active field
    
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
            return 'http://127.0.0.1:8000/' + self.image.url
        return ''

    def get_primary_image(self):
        """Get the first image as a fallback"""
        first_image = self.category.images.first()
        return first_image.get_image() if first_image else ''



class Product(models.Model):
    MOQ_STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
        ('not_applicable', 'Not Applicable'),
    )

    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField(db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    below_moq_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    moq = models.IntegerField(default=1, help_text="Minimum Order Quantity required for group buy")
    moq_status = models.CharField(max_length=20, choices=MOQ_STATUS_CHOICES, default='active')
    moq_per_person = models.IntegerField(default=1, help_text="Minimum quantity allowed per person in group buy")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class  Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def current_moq_count(self):
        """Calculate current ordered quantity towards MOQ completion"""
        if self.moq_status != 'active':
            return 0
    
        order_items = OrderItem.objects.filter(
            product=self,
             order__payment_status='paid'
              )
        return sum(item.quantity for item in order_items)

    def moq_progress_percentage(self):
        """Calculate MOQ completion percentage"""
        if self.moq <= 1 or self.moq_status != 'active':
            return 100

        current = self.current_moq_count()
        return min(300, int((current / self.moq) * 100))


    
    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'

    def get_primary_image(self):
        """Get the first image as a fallback for compatibility"""
        first_image = self.images.first()
        return first_image.get_image() if first_image else ''

    def get_primary_thumbnail(self):
        """Get the first thumbnail as a fallback for compatibility"""
        first_image = self.images.first()
        return first_image.get_thumbnail() if first_image else ''


    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)

    def get_image(self):
        if self.image:
            return 'http://127.0.0.1:8000/' + self.image.url
        return ''

    def get_thumbnail(self):
        if self.thumbnail:
            
            return settings.SITE_URL + self.thumbnail.url.lstrip('/')
        elif self.image:
            self.thumbnail = self.make_thumbnail(self.image)
            self.save()
            
            return settings.SITE_URL + self.thumbnail.url.lstrip('/')
        return ''

    def make_thumbnail(self, image, size=(200, 100)):
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        
        filename = os.path.basename(image.name)
        thumbnail = File(thumb_io, name=filename)
        return thumbnail


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)

    class Meta:
        unique_together = ('product', 'color', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"



class Cart(models.Model):
    """
    Shopping cart to hold items before they become orders
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
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


class CartItem(models.Model):
    """
    Individual items in a shopping cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'variant')

    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.variant.color}, {self.variant.size})"
        
    @property
    def price_per_piece(self):
        """
        Calculate the price per unit for this cart item based on its own quantity
        compared to the product's moq_per_person.
        """
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
        """
        Calculate the total price for this cart item based on its own quantity
        compared to the product's moq_per_person.
        """
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
    )

    SHIPPING_METHOD_CHOICES = (
        ('standard', 'Standard Shipping'),
        ('express', 'Express Shipping'),
        ('pickup', 'Local Pickup'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHOD_CHOICES, default='standard')
    delivery_location = models.ForeignKey(DeliveryLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

 

    def save(self, *args, **kwargs):
        if not self.pk:  # Only calculate on first save
            super().save(*args, **kwargs)
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def calculate_total_price(self):
        """
        Calculate the total price of all items in the order
        """
        total = sum(
            item.quantity * item.price 
            for item in self.items.all()
        )
        return total

    def update_total_price(self):
        """
        Manually update total price (useful after adding/removing items)
        """
        self.total_price = self.calculate_total_price()
        self.save()


    def remove_item(self, order_item):
        """
        Convenience method to remove an item and update total price
        """
        order_item.delete()
        self.update_total_price()


    def mark_as_completed(self):
        """
        Method to handle order completion logic
        """
        if self.delivery_status == 'delivered' and self.payment_status == 'paid':
            # Create CompletedOrder if conditions are met
            try:
                completed_order = CompletedOrder.objects.create(
                    order_number=f"ORD-{self.id}",
                    user=self.user,
                    shipping_method=self.shipping_method,
                    order_date=self.created_at,
                    original_order=self,
                    delivery_location=self.delivery_location
                )
                return completed_order
            except Exception as e:
                # Log the error or handle it appropriately
                print(f"Error creating completed order: {e}")
        return None

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('mpesa', 'M-Pesa'),  # Updated to lowercase 'mpesa' for consistency
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
        default='mpesa'  # Changed default to 'mpesa' since this is M-Pesa focused
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
    
    # New fields for M-Pesa integration
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
        """
        Set amount from order total price if not already set
        """
        if not self.amount:
            self.amount = self.order.total_price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
class CompletedOrder(models.Model):
    """
    Stores orders that have been fully processed and delivered.
    This provides order history and keeps the main Order table focused on active orders.
    """
    original_order = models.OneToOneField(Order, on_delete=models.CASCADE, null =True,related_name='completed_order')
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_orders')
    shipping_method = models.CharField(max_length=50)
    mpesa_confirmation_code = models.CharField(max_length=50, null=True, blank=True)
    order_date = models.DateTimeField()
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    completion_date = models.DateTimeField(auto_now_add=True)
    delivery_location = models.ForeignKey(DeliveryLocation, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"Completed Order #{self.order_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Add 1.5 points to user's points
        self.user.points = int(self.user.points + Decimal('1.5'))
        self.user.save(update_fields=['points'])

    @property
    def items(self):
        """
        Returns the original order items
        """
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
        # Update product rating when review is saved
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


