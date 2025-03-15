from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.files import File
from PIL import Image
from io import BytesIO


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length = 50, blank = True, null = True, unique = True)
    email = models.EmailField(unique=True)
    location = models.CharField(max_length=255, blank=True)
    user_type = models.CharField(max_length=50, default='customer')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Remove username from REQUIRED_FIELDS

    objects = CustomUserManager()  # Use the custom manager

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(null=True, blank=True)
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}'


class Product(models.Model):
    MOQ_STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
        ('not_applicable', 'Not Applicable'),
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    below_moq_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    moq = models.IntegerField(default=1, help_text="Minimum Order Quantity required for group buy")
    moq_status = models.CharField(max_length=20, choices=MOQ_STATUS_CHOICES, default='not_applicable')
    moq_per_person = models.IntegerField(default=1, help_text="Minimum quantity allowed per person in group buy")
    picture = models.ImageField(upload_to='product_images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='product_images/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class  Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

    def current_moq_count(self):
        """Calculate current ordered quantity towards MOQ completion"""
        if self.moq_status != 'active':
            return 0

        active_orders = Order.objects.filter(
            product=self,
            payment_status='pending',
            is_cancelled=False
        )
        return sum(order.quantity for order in active_orders)

    def moq_progress_percentage(self):
        """Calculate MOQ completion percentage"""
        if self.moq <= 1 or self.moq_status != 'active':
            return 100

        current = self.current_moq_count()
        return min(100, int((current / self.moq) * 100))


    
    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'

    def get_image(self):
        if self.picture:
            return 'http://127.0.0.1:8000' + self.picture.url
        return ''

    def get_thumbnail(self):
        if self.thumbnail:
            return 'http://127.0.0.1:8000' + self.thumbnail.url
        else:
            if self.picture:
                self.thumbnail = self.make_thumbnail(self.picture)
                self.save()

                return 'http://127.0.0.1:8000' + self.thumbnail.url
            else:
                return ''
    
    def make_thumbnail(self, picture, size=(200, 100)):
        img = Image.open(picture)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=picture.name)

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
    def line_total(self):
        # Calculate price based on MOQ status
        if self.product.moq_status == 'active' and self.product.current_moq_count() < self.product.moq:
            price = self.product.below_moq_price or self.product.price
        else:
            price = self.product.price
        return price * self.quantity


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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_method = models.CharField(max_length=20, choices=SHIPPING_METHOD_CHOICES, default='standard')
    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='processing')
    collection_status = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def save(self, *args, **kwargs):
        # If this is a new order, set price based on current product pricing and MOQ status
        if not self.id:
            product = self.product
            if product.moq_status == 'active' and product.current_moq_count() < product.moq:
                self.price = product.below_moq_price or product.price
            else:
                self.price = product.price

            # Set shipping address from user's location if not provided
            if not self.shipping_address and self.shipping_method != 'pickup':
                self.shipping_address = self.user.location

        super().save(*args, **kwargs)

    def move_to_completed(self):
        """
        Move an order to the completed orders table once it's delivered
        """
        if self.delivery_status == 'delivered' and self.payment_status == 'paid':
            # Create completed order record
            completed = CompletedOrder.objects.create(
                order_number=f"ORD-{self.id}",
                user=self.user,
                product=self.product,
                variant_details={
                    'color': self.variant.color,
                    'size': self.variant.size,
                },
                quantity=self.quantity,
                price_paid=self.price,
                shipping_method=self.shipping_method,
                payment_method=self.payment_method or 'Not recorded',
                was_moq_order=self.product.moq_status == 'active',
                order_date=self.created_at
            )
            return completed
        return None


class CompletedOrder(models.Model):
    """
    Stores orders that have been fully processed and delivered.
    This provides order history and keeps the main Order table focused on active orders.
    """
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='completed_orders')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant_details = models.JSONField(help_text="Stores color, size and other variant details")
    quantity = models.IntegerField()
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_method = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    was_moq_order = models.BooleanField(default=False)
    order_date = models.DateTimeField()
    completion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Completed Order #{self.order_number}"


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


