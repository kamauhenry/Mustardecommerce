from rest_framework import serializers
from ecommerce.models import *
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()



class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    variant_info = serializers.SerializerMethodField()
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'variant',
                  'variant_info', 'quantity', 'line_total', 'added_at']
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


class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    variant_info = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'product_name', 'variant',
                  'variant_info', 'quantity', 'price', 'shipping_method',
                  'payment_status', 'delivery_status',
                  'collection_status', 'is_cancelled', 'created_at']
        read_only_fields = ['price']

    def get_variant_info(self, obj):
        return {
            'color': obj.variant.color,
            'size': obj.variant.size
        }


class CompletedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedOrder
        fields = '__all__'
        read_only_fields = ['order_number', 'user', 'product',
                            'variant_details', 'price_paid', 'completion_date']


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

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'phone_number', 'points', 'affiliate_code', 'location', 'password']
        read_only_fields = ['id', 'points', 'affiliate_code']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user_type = validated_data.pop('user_type', 'customer')
        location = validated_data.pop('location', '')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            user_type=user_type,
            location=location,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            # phone_number=validated_data.get('phone_number', ''), # Uncomment if phone_number is required
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        return {'user': user}

class UserSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    orders = OrderSerializer(many=True, read_only=True, source='order_set')
    completed_orders = CompletedOrderSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'user_type', 'phone_number', 'points', 'affiliate_code', 
            'location', 'cart', 'orders', 'completed_orders'
        ]
        read_only_fields = ['points', 'affiliate_code', 'cart', 'orders', 'completed_orders']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class CategorySerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']



class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size']


class ProductSerializer(serializers.ModelSerializer):
    category_slug = serializers.SlugField(source='category.slug', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    moq_progress = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    variants  = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'below_moq_price',
            'moq', 'moq_per_person', 'moq_status', 'moq_progress', 'thumbnail',
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

    def get_thumbnail(self, obj):
        if obj.thumbnail and hasattr(obj.thumbnail, 'url'):
            return settings.SITE_URL + obj.thumbnail.url.lstrip('/')
        elif obj.picture and hasattr(obj.picture, 'url'):
            return settings.SITE_URL + obj.picture.url.lstrip('/')
        return ''


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
