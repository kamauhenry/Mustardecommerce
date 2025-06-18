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
        fields = ('id',  'county', 'ward', 'is_shop_pickup', 'is_default', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_shop_pickup', 'created_at', 'updated_at')

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

class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_name', 'quantity', 'low_stock_threshold', 'last_updated']
        read_only_fields = ['id', 'product_name', 'last_updated']

    def validate(self, data):
        product = data.get('product')
        instance = self.instance
        if product and not product.is_pick_and_pay:
            raise serializers.ValidationError({"product": "Inventory can only be created for Pick and Pay products."})
        if product and Inventory.objects.filter(product=product).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError({"product": "An inventory record already exists for this product."})
        if 'quantity' in data and data['quantity'] < 0:
            raise serializers.ValidationError({"quantity": "Stock quantity cannot be negative."})
        if 'low_stock_threshold' in data and data['low_stock_threshold'] < 0:
            raise serializers.ValidationError({"low_stock_threshold": "Low stock threshold cannot be negative."})
        return data

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
    inventory = InventorySerializer(read_only=True)
    inventory_quantity = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    is_pick_and_pay = serializers.BooleanField(default=False)
    creviews = CustomerReviewSerializer(many=True, read_only=True, source='reviews')
    meta_title = serializers.CharField(allow_null=True, required=False)
    meta_description = serializers.CharField(allow_null=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'below_moq_price',
            'moq', 'moq_per_person', 'moq_status', 'moq_progress', 'category',
            'category_id', 'category_slug', 'created_at', 'thumbnail',
            'rating', 'attributes', 'attribute_value_ids', 'supplier', 'supplier_id',
            'images', 'meta_title', 'meta_description', 'is_pick_and_pay', 'inventory',
            'inventory_quantity', 'creviews'
        ]
        read_only_fields = ['slug', 'category_slug', 'moq_progress', 'thumbnail', 'rating', 'images', 'inventory', 'creviews']

    def validate_attribute_value_ids(self, value):
        logger.info(f"Validating attribute_value_ids: {value}")
        if value:
            valid_ids = AttributeValue.objects.filter(id__in=value).count()
            if valid_ids != len(value):
                logger.error(f"Invalid attribute_value_ids: {value}")
                raise serializers.ValidationError("One or more attribute value IDs are invalid.")
        return value

    def validate(self, data):
        moq_status = data.get('moq_status', 'active')
        is_pick_and_pay = data.get('is_pick_and_pay', False)
        inventory_quantity = data.get('inventory_quantity')
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
        if is_pick_and_pay:
            if 'moq_status' in data and data['moq_status'] != 'not_applicable':
                raise serializers.ValidationError({"moq_status": "Pick and Pay products must have moq_status 'not_applicable'."})
            if 'below_moq_price' in data and data['below_moq_price'] is not None:
                raise serializers.ValidationError({"below_moq_price": "Pick and Pay products cannot have a below MOQ price."})
            if 'moq' in data and data['moq'] != 1:
                raise serializers.ValidationError({"moq": "Pick and Pay products must have MOQ set to 1."})
            if 'moq_per_person' in data and data['moq_per_person'] != 1:
                raise serializers.ValidationError({"moq_per_person": "Pick and Pay products must have MOQ per person set to 1."})
            if inventory_quantity is None:
                raise serializers.ValidationError({"inventory_quantity": "Inventory quantity is required for Pick and Pay products."})
            if inventory_quantity is not None and inventory_quantity < 0:
                raise serializers.ValidationError({"inventory_quantity": "Inventory quantity cannot be negative."})
        else:
            if inventory_quantity is not None:
                raise serializers.ValidationError({"inventory_quantity": "Inventory quantity should only be provided for Pick and Pay products."})
        return data

    def create(self, validated_data):
        attribute_value_ids = validated_data.pop('attribute_value_ids', [])
        inventory_quantity = validated_data.pop('inventory_quantity', None)
        is_pick_and_pay = validated_data.get('is_pick_and_pay', False)
        meta_title = validated_data.get('meta_title') or validated_data.get('name', 'Product')
        meta_description = validated_data.get('meta_description') or validated_data.get('description', 'Discover this product at MustardImports.')
        validated_data['meta_title'] = meta_title
        validated_data['meta_description'] = meta_description
        logger.info(f"Creating product with attribute_value_ids: {attribute_value_ids}, is_pick_and_pay: {is_pick_and_pay}, inventory_quantity: {inventory_quantity}")
        instance = super().create(validated_data)
        if attribute_value_ids:
            attribute_values = AttributeValue.objects.filter(id__in=attribute_value_ids)
            instance.attribute_values.set(attribute_values)
        if is_pick_and_pay:
            Inventory.objects.create(
                product=instance,
                quantity=inventory_quantity or 0,
                low_stock_threshold=10
            )
        logger.info(f"Created product {instance.id} with attribute_values: {list(instance.attribute_values.values_list('id', flat=True))}")
        return instance

    def update(self, instance, validated_data):
        attribute_value_ids = validated_data.pop('attribute_value_ids', None)
        inventory_quantity = validated_data.pop('inventory_quantity', None)
        is_pick_and_pay = validated_data.get('is_pick_and_pay', instance.is_pick_and_pay)
        meta_title = validated_data.get('meta_title') or instance.meta_title or instance.name
        meta_description = validated_data.get('meta_description') or instance.meta_description or instance.description
        validated_data['meta_title'] = meta_title
        validated_data['meta_description'] = meta_description
        logger.info(f"Updating product with attribute_value_ids: {attribute_value_ids}, is_pick_and_pay: {is_pick_and_pay}, inventory_quantity: {inventory_quantity}")
        instance = super().update(instance, validated_data)
        if attribute_value_ids is not None:
            attribute_values = AttributeValue.objects.filter(id__in=attribute_value_ids)
            instance.attribute_values.set(attribute_values)
        if is_pick_and_pay:
            inventory, created = Inventory.objects.get_or_create(
                product=instance,
                defaults={'quantity': inventory_quantity or 0, 'low_stock_threshold': 10}
            )
            if not created and inventory_quantity is not None:
                inventory.quantity = inventory_quantity
                inventory.save()
        logger.info(f"Updated product {instance.id} with attribute_values: {list(instance.attribute_values.values_list('id', flat=True))}")
        return instance

    def get_attributes(self, obj):
        attributes = {}
        for attr_value in obj.attribute_values.select_related('attribute').all():
            attr_name = attr_value.attribute.name
            if attr_name not in attributes:
                attributes[attr_name] = []
            attributes[attr_name].append({
                'id': attr_value.id,
                'value': attr_value.value
            })
        return [
            {
                'id': idx + 1,
                'name': name,
                'values': sorted(values, key=lambda x: x['value'])
            }
            for idx, (name, values) in enumerate(sorted(attributes.items()))
        ]

    def get_moq_progress(self, obj):
        if obj.moq_status == 'active' and not obj.is_pick_and_pay:
            return {
                'current': obj.current_moq_count(),
                'target': obj.moq,
                'percentage': obj.moq_progress_percentage()
            }
        return None

    def get_thumbnail(self, obj):
        return obj.get_primary_thumbnail()
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_per_piece = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'attributes', 'quantity', 'line_total', 'added_at', 'price_per_piece']
        read_only_fields = ['line_total', 'price_per_piece']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        instance = self.instance
        if product.is_pick_and_pay:
            available_stock = product.available_stock()
            if available_stock is None:
                raise serializers.ValidationError({"product": f"No inventory record found for Pick and Pay product {product.name}."})
            # Check stock against the total quantity (new + existing)
            current_quantity = instance.quantity if instance else 0
            total_quantity = current_quantity + quantity if instance else quantity
            if total_quantity > available_stock:
                raise serializers.ValidationError({
                    "quantity": f"Cannot add {total_quantity} of {product.name}. Only {available_stock} in stock."
                })
        return data

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

    def validate(self, data):
        shipping_method = data.get('shipping_method')
        # Check if cart has items (only during update, as create may not have items yet)
        if self.instance and self.instance.items.exists():
            all_pick_and_pay = all(item.product.is_pick_and_pay for item in self.instance.items.all())
            if all_pick_and_pay and shipping_method:
                raise serializers.ValidationError({"shipping_method_id": "Shipping method must be null for carts with only Pick and Pay products."})
            if not all_pick_and_pay and not shipping_method:
                raise serializers.ValidationError({"shipping_method_id": "Shipping method is required for carts with MOQ products."})
        return data

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
        pickup_only = self.context.get('pickup_only', False)
        products = obj.products.all().order_by('-created_at')
        if pickup_only:
            products = products.filter(is_pick_and_pay=True)
        return ProductSerializer(products[:6], many=True, context=self.context).data


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'attributes', 'quantity', 'price', 'line_total']
        read_only_fields = ['price', 'line_total']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        if product.is_pick_and_pay:
            available_stock = product.available_stock()
            if available_stock is None:
                raise serializers.ValidationError({"product": f"No inventory record found for Pick and Pay product {product.name}."})
            if quantity > available_stock:
                raise serializers.ValidationError({
                    "quantity": f"Cannot order {quantity} of {product.name}. Only {available_stock} in stock."
                })
        return data

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

    def validate(self, data):
        shipping_method = data.get('shipping_method')
        delivery_location = data.get('delivery_location')
        delivery_status = data.get('delivery_status', 'processing')
        # Check if order has items (only during update, as create may populate items later)
        if self.instance and self.instance.items.exists():
            all_pick_and_pay = all(item.product.is_pick_and_pay for item in self.instance.items.all())
            if all_pick_and_pay:
                if shipping_method:
                    raise serializers.ValidationError({"shipping_method_id": "Shipping method must be null for orders with only Pick and Pay products."})
                if delivery_location:
                    raise serializers.ValidationError({"delivery_location": "Delivery location must be null for Pick and Pay orders."})
                if delivery_status != 'ready_for_pickup':
                    raise serializers.ValidationError({"delivery_status": "Delivery status must be 'ready_for_pickup' for Pick and Pay orders."})
            else:
                if not shipping_method:
                    raise serializers.ValidationError({"shipping_method_id": "Shipping method is required for orders with MOQ products."})
                if not delivery_location:
                    raise serializers.ValidationError({"delivery_location": "Delivery location is required for orders with MOQ products."})
                if delivery_status == 'ready_for_pickup':
                    raise serializers.ValidationError({"delivery_status": "Delivery status cannot be 'ready_for_pickup' for orders with MOQ products."})
        return data

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