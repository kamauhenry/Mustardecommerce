from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .permissions import IsOwnerOrAdmin, IsAdminUser

from ..models import (
    User, Category, Product, ProductVariant,
    Order, CompletedOrder, CustomerReview, MOQRequest,
    Cart, CartItem
)
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer, 
    ProductVariantSerializer, OrderSerializer, CompletedOrderSerializer,
    CustomerReviewSerializer, MOQRequestSerializer, CartSerializer,
    CartItemSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()[0:10]
    serializer_class = ProductSerializer  # Fixed
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'moq_status']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'rating', 'created_at']

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        product = self.get_object()
        variants = ProductVariant.objects.filter(product=product)
        serializer = ProductVariantSerializer(variants, many=True)  # Fixed
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        product = self.get_object()
        reviews = CustomerReview.objects.filter(product=product)
        serializer = CustomerReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='category/(?P<category_name>[^/.]+)')
    def products_by_category(self, request, category_name=None):
        category = get_object_or_404(Category, name=category_name.replace("-", " "))
        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Find or create cart for the user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(user=self.request.user)  # Fixed
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()

        # Verify product and variant exist
        product_id = request.data.get('product')
        variant_id = request.data.get('variant')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(pk=product_id)
            variant = ProductVariant.objects.get(pk=variant_id, product=product)
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            return Response(
                {"error": "Product or variant not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check MOQ constraints
        if product.moq_status == 'active' and quantity > product.moq_per_person:
            return Response(
                {"error": f"Maximum {product.moq_per_person} items allowed per person for this group buy"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get('item_id')

        try:
            item = CartItem.objects.get(pk=item_id, cart=cart)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        cart = self.get_object()

        # Verify cart has items
        if cart.items.count() == 0:
            return Response(
                {"error": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create orders from cart items
        orders = []
        for item in cart.items.all():
            order = Order.objects.create(
                user=request.user,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                shipping_method=request.data.get('shipping_method', 'standard'),
                shipping_address=request.data.get('shipping_address', request.user.location),
                payment_method=request.data.get('payment_method')
            )
            orders.append(order)

        # Clear cart
        cart.items.all().delete()

        # Return created orders
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'delivery_status', 'is_cancelled']
    ordering_fields = ['created_at', 'price']

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()

        # Check if order can be cancelled
        if order.delivery_status not in ['processing', 'shipped']:
            return Response(
                {"error": "Order cannot be cancelled in its current state"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.is_cancelled = True
        order.delivery_status = 'cancelled'
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data)


class CompletedOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompletedOrderSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        if self.request.user.is_staff:
            return CompletedOrder.objects.all()
        return CompletedOrder.objects.filter(user=self.request.user)


class CustomerReviewViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'rating']
    ordering_fields = ['created_at', 'rating']

    def get_queryset(self):
        return CustomerReview.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MOQRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MOQRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if self.request.user.is_staff:
            return MOQRequest.objects.all()
        return MOQRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def update_status(self, request, pk=None):
        moq_request = self.get_object()
        status = request.data.get('status')

        if status not in [choice[0] for choice in MOQRequest.STATUS_CHOICES]:
            return Response(
                {"error": "Invalid status value"},
                status=status.HTTP_400_BAD_REQUEST
            )

        moq_request.status = status
        moq_request.save()

        serializer = MOQRequestSerializer(moq_request)
        return Response(serializer.data)