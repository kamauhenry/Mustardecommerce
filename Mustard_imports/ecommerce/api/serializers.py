from rest_framework import serializers
from ecommerce.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'user_type', 'points', 'affiliate_code', 'location', ]
        read_only_fields = ['points', 'affiliate_code']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


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
