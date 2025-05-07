from rest_framework import serializers
from ecommerce.models import *
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

class AdminRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'phone_number', 'points', 'affiliate_code', 'password']
        read_only_fields = ['id', 'points', 'affiliate_code']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_user_type(self, value):
        if value != 'admin':
            raise serializers.ValidationError("User type must be 'admin' for this endpoint.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('user_type', None)
        user = User.objects.create_superuser(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', None),
        )
        AdminUser.objects.create(
            user=user,
            admin_level='senior'
        )
        return user

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        if user.user_type != 'admin':
            raise serializers.ValidationError('Only admins can use this endpoint')
        return {'user': user}

class DeliveryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLocation
        fields = ('id', 'name', 'address', 'latitude', 'longitude', 'is_default', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name', 'price', 'description', 'is_active']
        read_only_fields = ['id']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        return {'user': user}

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_email', 'phone', 'address']

    def validate(self, data):
        name = data.get('name')
        instance = self.instance
        if name and Supplier.objects.filter(name=name).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError({"name": "A supplier with this name already exists."})
        contact_email = data.get('contact_email')
        if contact_email and not contact_email.strip():
            raise serializers.ValidationError({"contact_email": "Email cannot be empty if provided."})
        return data

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']
        read_only_fields = ['id']

    def validate_name(self, value):
        normalized = value.strip().capitalize()
        if not normalized:
            raise serializers.ValidationError("Attribute name cannot be empty.")
        return normalized

class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=Attribute.objects.all(), source='attribute', write_only=True
    )
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    value = serializers.CharField(required=True)

    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute_id', 'attribute_name', 'value']
        read_only_fields = ['id', 'attribute_name']

    def validate(self, data):
        attribute = data.get('attribute')
        value = data.get('value').strip()
        instance = self.instance
        if not value:
            raise serializers.ValidationError({"value": "Value cannot be empty."})
        if AttributeValue.objects.filter(
            attribute=attribute,
            value=value
        ).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError(
                {"value": f"Value '{value}' for attribute '{attribute.name}' already exists."}
            )
        return {**data, 'value': value}

    def create(self, validated_data):
        return AttributeValue.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.attribute = validated_data.get('attribute', instance.attribute)
        instance.value = validated_data.get('value', instance.value)
        instance.save()
        return instance

class CustomerReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = CustomerReview
        fields = ['id', 'user', 'username', 'product', 'content', 'rating', 'created_at']
        read_only_fields = ['user', 'product']

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
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source='supplier', write_only=True, allow_null=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    attributes = serializers.SerializerMethodField()
    attribute_value_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    moq_progress = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'below_moq_price',
            'moq', 'moq_per_person', 'moq_status', 'moq_progress', 'category',
            'category_id', 'category_slug', 'created_at', 'thumbnail',
            'rating', 'attributes', 'attribute_value_ids', 'supplier', 'supplier_id',
            'images', 'meta_title', 'meta_description'
        ]
        read_only_fields = ['slug', 'category_slug', 'moq_progress', 'thumbnail', 'rating', 'images']

    def validate_attribute_value_ids(self, value):
        logger.info(f"Validating attribute_value_ids: {value}")
        if value:
            valid_ids = AttributeValue.objects.filter(id__in=value).count()
            if valid_ids != len(value):
                logger.error(f"Invalid attribute_value_ids: {value}")
                raise serializers.ValidationError("One or more attribute value IDs are invalid.")
        return value

    def create(self, validated_data):
        attribute_value_ids = validated_data.pop('attribute_value_ids', [])
        logger.info(f"Creating product with attribute_value_ids: {attribute_value_ids}")
        instance = super().create(validated_data)
        if attribute_value_ids:
            attribute_values = AttributeValue.objects.filter(id__in=attribute_value_ids)
            instance.attribute_values.set(attribute_values)
        logger.info(f"Created product {instance.id} with attribute_values: {list(instance.attribute_values.values_list('id', flat=True))}")
        return instance

    def update(self, instance, validated_data):
        attribute_value_ids = validated_data.pop('attribute_value_ids', None)
        logger.info(f"Updating product with attribute_value_ids: {attribute_value_ids}")
        instance = super().update(instance, validated_data)
        if attribute_value_ids is not None:
            attribute_values = AttributeValue.objects.filter(id__in=attribute_value_ids)
            instance.attribute_values.set(attribute_values)
        logger.info(f"Updated product {instance.id} with attribute_values: {list(instance.attribute_values.values_list('id', flat=True))}")
        return instance

    def get_attributes(self, obj):
        attributes = {}
        for attr_value in obj.attribute_values.all():
            attr_name = attr_value.attribute.name
            if attr_name not in attributes:
                attributes[attr_name] = []
            attributes[attr_name].append({'id': attr_value.id, 'value': attr_value.value})
        return [{'id': idx + 1, 'name': name, 'values': values} for idx, (name, values) in enumerate(attributes.items())]
        
    def get_moq_progress(self, obj):
        if obj.moq_status == 'active':
            return {
                'current': obj.current_moq_count(),
                'target': obj.moq,
                'percentage': obj.moq_progress_percentage()
            }
        return None

    def get_thumbnail(self, obj):
        return obj.get_primary_thumbnail()

    def validate(self, data):
        moq_status = data.get('moq_status', 'active')
        if moq_status not in ['active', 'closed', 'completed', 'not_applicable']:
            raise serializers.ValidationError({"moq_status": "Invalid MOQ status."})
        if 'price' in data and data['price'] < 0:
            raise serializers.ValidationError({"price": "Price cannot be negative."})
        if 'below_moq_price' in data and data['below_moq_price'] is not None and data['below_moq_price'] < 0:
            raise serializers.ValidationError({"below_moq_price": "Below MOQ price cannot be negative."})
        if 'moq' in data and data['moq'] is not None and data['moq'] < 1:
            raise serializers.ValidationError({"moq": "MOQ must be at least 1."})
        if 'moq_per_person' in data and data['moq_per_person'] is not None and data['moq_per_person'] < 1:
            raise serializers.ValidationError({"moq_per_person": "MOQ per person must be at least 1."})
        return data

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_per_piece = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'attributes', 'quantity', 'line_total', 'added_at', 'price_per_piece']
        read_only_fields = ['line_total']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    shipping_method = ShippingMethodSerializer(read_only=True)
    shipping_method_id = serializers.PrimaryKeyRelatedField(
        queryset=ShippingMethod.objects.filter(is_active=True),
        source='shipping_method',
        write_only=True,
        allow_null=True
    )
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items', 'subtotal',
            'shipping_method', 'shipping_method_id', 'shipping_cost', 'total',
            'created_at', 'last_updated'
        ]
        read_only_fields = ['user', 'items', 'total_items', 'subtotal', 'shipping_cost', 'total']

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number']

class HomeCategorySerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'products']

    def get_products(self, obj):
        products = obj.products.order_by('-created_at')[:6]
        return ProductSerializer(products, many=True, context=self.context).data

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'attributes', 'quantity', 'price', 'line_total']

    def get_line_total(self, obj):
        return obj.quantity * obj.price


class OrderSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    shipping_method = ShippingMethodSerializer(read_only=True)
    shipping_method_id = serializers.PrimaryKeyRelatedField(
        queryset=ShippingMethod.objects.filter(is_active=True),
        source='shipping_method',
        write_only=True,
        allow_null=True
    )
    delivery_location = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryLocation.objects.all(),
        allow_null=True
    )
    shipping_cost = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    order_number = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'shipping_method', 'shipping_method_id', 'shipping_cost',
            'delivery_location', 'payment_status', 'delivery_status', 'created_at',
            'items', 'total_price'
        ]
        read_only_fields = ['id', 'order_number', 'user', 'total_price', 'shipping_cost']

    def get_order_number(self, obj):
        return f"MI{obj.id}" 

class CompletedOrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CompletedOrder
        fields = [
            'id', 'original_order', 'order_number', 'user',
            'shipping_method', 'mpesa_confirmation_code', 'order_date',
            'completion_date', 'items', 'total_price', 'delivery_location'
        ]
        read_only_fields = [
            'order_number', 'user', 'shipping_method', 'completion_date', 'total_price'
        ]

    def get_items(self, obj):
        return OrderItemSerializer(obj.items, many=True).data

class CategoriesProductsSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'products']

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
            'order', 'phone_number', 'payment_method', 'payment_status',
            'amount', 'payment_date', 'mpesa_checkout_request_id',
            'mpesa_receipt_number', 'error_message'
        ]
        read_only_fields = [
            'payment_status', 'payment_date', 'mpesa_checkout_request_id',
            'mpesa_receipt_number', 'error_message'
        ]

    def validate(self, data):
        order = data.get('order')
        if order and data.get('amount') != order.total_price:
            raise serializers.ValidationError({"amount": "Amount must match order total including shipping."})
        return data

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')
        read_only_fields = ('id', 'user_type', 'points', 'affiliate_code')

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
            'cart', 'orders', 'completed_orders', 'date_joined', 'delivery_locations'
        ]
        read_only_fields = ['points', 'affiliate_code', 'cart', 'orders', 'completed_orders', 'date_joined']
        extra_kwargs = {'password': {'write_only': True}}