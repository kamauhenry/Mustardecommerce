from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    USER_TYPES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    email = models.EmailField(unique=True)
    points = models.IntegerField(default=0)
    affiliate_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)


    
    picture = models.ImageField(upload_to='user_images/', blank=True, null=True)

    
    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Product(models.Model):
    MOQ_STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('completed', 'Completed'),
        ('not_applicable', 'Not Applicable'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    below_moq_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    moq = models.IntegerField(default=1, help_text="Minimum Order Quantity required for group buy")
    moq_status = models.CharField(max_length=20, choices=MOQ_STATUS_CHOICES, default='not_applicable')
    moq_per_person = models.IntegerField(default=1, help_text="Maximum quantity allowed per person in group buy")
    picture = models.ImageField(upload_to='product_images/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    
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


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20)

    
    class Meta:
        unique_together = ('product', 'color', 'size')
    
    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.product.name}"


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


class MOQRequestImage(models.Model):
    request = models.ForeignKey(MOQRequest, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='moq_request_images/')
    
    def __str__(self):
        return f"Image for MOQ Request #{self.request.id}"
pip