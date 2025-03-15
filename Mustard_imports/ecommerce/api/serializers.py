from rest_framework import serializers
from ..models import *
import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    re_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 're_password', 'first_name', 'last_name', 'location', 'user_type']
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, data):
        errors = {}

        # Email validation
        if not data.get('email'):
            errors["email"] = "This field is required."
        if User.objects.filter(email=data['email']).exists():
            errors["email"] = "A user with this email already exists."

        # Password validation
        if data['password'] != data['re_password']:
            errors["password"] = "Passwords must match."

        # User type validation
        user_type = data.get('user_type', 'customer')
        if user_type not in ['customer', 'admin']:
            errors["user_type"] = "Invalid user type."

        # Log errors before raising an exception
        if errors:
            logger.error(f"Validation Errors: {errors}")  # Logs to Django console
            print("Validation Errors:", errors)  # Debugging in console
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        try:
            validated_data.pop('re_password')
            user = User(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                location=validated_data.get('location', ''),
                user_type=validated_data.get('user_type', 'customer'),
            )
            user.set_password(validated_data['password'])
            user.username = validated_data['email'].split('@')[0]
            user.save()

            return user
        except Exception as e:
            raise serializers.ValidationError({"detail": str(e)})


class CategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name','products']

    def get_products(self, obj):
        latest_products = Product.object.filter(category=obj).order_by('-created_at')[:4]
        return ProductSerializer(latest_products, many=True, context=self.context).data

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size']




class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
   
    category_name = serializers.ReadOnlyField(source='category.name')
    moq_progress = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'below_moq_price',
                 'moq', 'moq_status', 'moq_per_person', 'picture',
                 'rating', 'category', 'category_name', 'variants', 
                 'thumbnail', 'moq_progress', 'created_at']
    
    def get_moq_progress(self, obj):
        if obj.moq_status == 'active':
            return {
                'current': obj.current_moq_count(),
                'target': obj.moq,
                'percentage': obj.moq_progress_percentage()
            }
        return None

    def get_thumbnail(self, obj):
        return obj.get_thumbnail()

    def get_thumbnail(self, obj):
        return obj.get_thumbnail()


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


class MOQRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MOQRequest
        fields = ['id', 'user', 'product_name', 'product_link',
                  'quantity', 'description', 'status', 'created_at']
        read_only_fields = ['user', 'status']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
