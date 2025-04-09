from rest_framework import serializers
from ecommerce.models import *
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class DeliveryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLocation
        fields = ('id', 'name', 'address', 'latitude', 'longitude', 'is_default', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')




class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        return {'user': user}




class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    variant_info = serializers.SerializerMethodField()
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_per_piece = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'variant',
                  'variant_info', 'quantity', 'line_total', 'added_at','price_per_piece']
        read_only_fields = ['line_total']

    def get_variant_info(self, obj):
        return {
            'color': obj.variant.color,
            'size': obj.variant.size
        }



class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'subtotal',
                  'created_at', 'last_updated']
        read_only_fields = ['user', 'items', 'total_items', 'subtotal']
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id', 
            'product', 
            'product_name',   
            'variant',
            'quantity', 
            'price', 
            'line_total'
        ]

    def get_line_total(self, obj):
        return obj.quantity * obj.price

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    delivery_location = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryLocation.objects.all(), 
        allow_null=True  # Add this if nullable
    )
    class Meta:
        model = Order
        fields = [
            'id','user', 'shipping_method', 'delivery_location', 
            'payment_status', 'delivery_status', 'created_at', 
             'items', 'total_price'
        ]
        read_only_fields = ['id','user', 'total_price']


class CompletedOrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CompletedOrder
        fields = [
            'id', 'original_order', 'order_number', 'user', 
            'shipping_method', 'payment_method', 
            'mpesa_confirmation_code', 'order_date', 
            'completion_date', 'items', 'total_price','delivery_location'
        ]
        read_only_fields = [
            'order_number', 'user', 'shipping_method', 
            'payment_method', 'completion_date', 'total_price'
        ]

    def get_items(self, obj):
        """
        Retrieve items from the original order
        """
        return OrderItemSerializer(obj.items, many=True).data
class CustomerReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = CustomerReview
        fields = ['id', 'user', 'username', 'product', 'content',
                  'rating', 'created_at']
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)




class CategoryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryImage
        fields = ['image']

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'is_active', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        image = obj.images.first()
        if image and image.image:
            return request.build_absolute_uri(image.image.url) if request else image.image.url
        return None

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size']

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'thumbnail']

    def get_image(self, obj):
        return obj.get_image()

    def get_thumbnail(self, obj):
        return obj.get_thumbnail()

class ProductSerializer(serializers.ModelSerializer):
    category_slug = serializers.SlugField(source='category.slug', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    moq_progress = serializers.SerializerMethodField()
    # thumbnail = serializers.SerializerMethodField()
    variants  = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'below_moq_price',
            'moq', 'moq_per_person', 'moq_status', 'moq_progress',
            'category_slug', 'created_at', 'variants'
        ]

    def get_moq_progress(self, obj):
        if obj.moq_status == 'active':
            return {
                'current': obj.current_moq_count(),
                'target': obj.moq,
                'percentage': obj.moq_progress_percentage()
            }
        return None

    # def get_thumbnail(self, obj):
    #     if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
    #         return settings.SITE_URL + obj.thumbnail.url.lstrip('/')
    #     elif obj.picture and hasattr(obj.picture, 'url'):
    #         return settings.SITE_URL + obj.picture.url.lstrip('/')
    #     return ''


class CategoriesProductsSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug','products']



class MOQRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MOQRequest
        fields = ['id', 'user', 'product_name', 'product_link',
                  'quantity', 'description', 'status', 'created_at']
        read_only_fields = ['user', 'status']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)




class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'order',                # Primary key, linked to Order
            'phone_number',         # Required field
            'payment_method',       # Matches model field name
            'payment_status',       # Matches model field name
            'amount',               # Amount from order total or set manually
            'payment_date',         # Matches model field name (replaces 'created_at')
            'mpesa_checkout_request_id',  # M-Pesa STK Push request ID
            'mpesa_receipt_number',       # M-Pesa transaction receipt
            'error_message',        # Reason for failure, if any
        ]
        read_only_fields = [
            'payment_status',       # Status should be updated by the system, not the client
            'payment_date',         # Auto-set on creation
            'mpesa_checkout_request_id',  # Set by M-Pesa integration
            'mpesa_receipt_number',       # Set by M-Pesa callback
            'error_message',        # Set by payment processing logic
        ]

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ( 'username', 'email', 'first_name', 'last_name', 
            'phone_number',) # Include fields you want to allow updating
        read_only_fields = ('id', 'user_type','points', 'affiliate_code')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'phone_number', 'points', 'affiliate_code', 'password']
        read_only_fields = ['id', 'points', 'affiliate_code']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user_type = validated_data.pop('user_type', 'customer')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            user_type=user_type,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number'],
        )
        return user



class UserSerializer(serializers.ModelSerializer):
    delivery_locations = DeliveryLocationSerializer(many=True, read_only=True)
    cart = CartSerializer(read_only=True)
    orders = OrderSerializer(many=True, read_only=True, source='order_set')
    completed_orders = CompletedOrderSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'user_type', 'phone_number', 'points', 'affiliate_code', 
            'cart', 'orders', 'completed_orders','date_joined'  ,'delivery_locations'
        ]
        read_only_fields = ['points', 'affiliate_code', 'cart', 'orders', 'completed_orders','date_joined']
        extra_kwargs = {'password': {'write_only': True}}

