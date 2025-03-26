from django.db.models import Q
from django.core.paginator import Paginator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view ,  permission_classes
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie

from .permissions import IsOwnerOrAdmin, IsAdminUser
from ..models import (
    User, Category, Product, ProductVariant,
    Order, CompletedOrder, CustomerReview, MOQRequest,
    Cart, CartItem
)
from .serializers import (
    UserSerializer, CategorySerializer, ProductSerializer,
    ProductVariantSerializer, OrderSerializer, CompletedOrderSerializer,CategoriesProductsSerializer,
    CustomerReviewSerializer, MOQRequestSerializer, CartSerializer,
    CartItemSerializer, RegisterSerializer, LoginSerializer
)

User = get_user_model()

# Authentication Views

class LoginView(APIView):

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if isinstance(request.user, AnonymousUser):
            return Response({'message': 'Not logged in'}, status=status.HTTP401_UNAUTHORIZED)
        return Response({
            'message': 'Logged in',
            'user_id': request.user.id,
            'username': request.user.username
        }, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    ordering = request.GET.get('ordering', '-created_at')
    
    if query:
        # First apply all filters
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by(ordering)
        
        # Then handle pagination
        paginator = Paginator(products, per_page)
        page_obj = paginator.get_page(page)
        
        serializer = ProductSerializer(page_obj, many=True)
        
        return Response({
            'results': serializer.data,  # Changed from 'products' to 'results' to match frontend expectation
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page
        })
    else:
        return Response({
            "results": [],  # Changed from 'products' to 'results'
            "total": 0, 
            "pages": 0, 
            "current_page": 1
        })

class CategoryProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_slug, *args, **kwargs):
        cache_key = f'category_products_{category_slug}_page_{request.query_params.get("page", 1)}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            category = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(category=category).order_by('-created_at')

            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 5))
            total = products.count()
            start = (page - 1) * per_page
            end = start + per_page
            products = products[start:end]

            serializer = ProductSerializer(products, many=True, context={'request': request})
            response_data = {
                'category': {'slug': category.slug, 'name': category.name},
                'products': serializer.data,
                'total': total,
            }

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data)
        except Http404:
            return Response({'error': 'Category not found'}, status=status.HTTP404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP500_INTERNAL_SERVER_ERROR)

class CategoriesWithProductsViewSet(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)

class ProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        cache_key = f'products_{request.query_params.get("category", "")}_{request.query_params.get("sort", "name_asc")}_page_{request.query_params.get("page", 1)}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            category_slug = request.query_params.get('category')
            sort = request.query_params.get('sort', 'name_asc')
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 5))

            products = Product.objects.all()
            if category_slug:
                products = products.filter(category__slug=category_slug)

            if sort == 'name_asc':
                products = products.order_by('name')
            elif sort == 'name_desc':
                products = products.order_by('-name')
            elif sort == 'price_asc':
                products = products.order_by('price')
            elif sort == 'price_desc':
                products = products.order_by('-price')
            elif sort == 'newest':
                products = products.order_by('-created_at')

            total = products.count()
            start = (page - 1) * per_page
            end = start + per_page
            products = products[start:end]

            serializer = ProductSerializer(products, many=True, context={'request': request})
            response_data = {
                'products': serializer.data,
                'total': total,
            }

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data)
        except Exception as e:
            return Response({'error': f'Failed to fetch products: {str(e)}'}, status=status.HTTP500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def create_cart(request):
    user = request.user  # Assuming authenticated
    try:
        # This will create a cart if it doesn't exist
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AllCategoriesWithProductsView(APIView):
    permission_classes = [permissions.AllowAny]


    def get(self, request, *args, **kwargs):
        cache_key = 'all_categories_with_products'
        result = cache.get(cache_key)
        if not result: 
            categories = Category.objects.prefetch_related('products')
            serializer = CategoriesProductsSerializer(categories, many=True, context={'request': request})
            result = serializer.data
            cache.set(cache_key, result, 60*15)

        return Response(result)


# ViewSets
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().only('id', 'name', 'slug')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None  # Disable pagination

    def list(self, request, *args, **kwargs):
        cache_key = 'categories_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data

        cache.set(cache_key, response_data, timeout=60 * 15)
        return Response(response_data)

class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Product.objects.all() 
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'moq_status']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'rating', 'created_at']
    pagination_class = None  #

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        product = self.get_object()
        variants = ProductVariant.objects.filter(product=product)
        serializer = ProductVariantSerializer(variants, many=True)
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

    def get_queryset(self):
        queryset = super().get_queryset()
        
        page = self.request.query_params.get('page')
        per_page = self.request.query_params.get('per_page')
        
        if page and per_page:
            try:
                page = int(page)
                per_page = int(per_page)
                start = (page - 1) * per_page
                end = start + per_page
                queryset = queryset[start:end]
            except (ValueError, TypeError):
                pass
                
        return queryset

class ProductDetail(APIView):
    permission_classes = [permissions.AllowAny]

    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.filter(category__slug=category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, product_slug, format=None):
        product = self.get_object(category_slug, product_slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsOwnerOrAdmin]

    def list(self, request):
        # Allow filtering carts by user
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = Cart.objects.filter(user_id=user_id)
        else:
            queryset = Cart.objects.filter(user=request.user)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        # Ensure a user can only create a cart for themselves
        serializer = self.get_serializer(data={
            'user': request.user.id
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(user=self.request.user)
    @action(detail=False, methods=['GET'])
    def my_cart(self, request):
        # Endpoint to get current user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def view_items(self, request, pk=None):
        cart = self.get_object()
        cart_items = cart.items.all()
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)


    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product')
        variant_id = request.data.get('variant')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(pk=product_id)
            variant = ProductVariant.objects.get(pk=variant_id, product=product)
        except (Product.DoesNotExist, ProductVariant.DoesNotExist):
            return Response({"error": "Product or variant not found"}, status=status.HTTP_400_BAD_REQUEST)

        if product.moq_status == 'active' and quantity > product.moq_per_person:
            return Response(
                {"error": f"Maximum {product.moq_per_person} items allowed per person for this group buy"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, variant=variant, defaults={'quantity': quantity}
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
            return Response(status=status.HTTP204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=status.HTTP404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        cart = self.get_object()
        if cart.items.count() == 0:
            return Response({"error": "Cart is empty"}, status=status.HTTP400_BAD_REQUEST)

        orders = []
        for item in cart.items.all():
            order = Order.objects.create(
                user=self.request.user,
                product=item.product,
                variant=item.variant,
                quantity=item.quantity,
                price=item.line_total / item.quantity,  # Use line_total logic from model
                shipping_method=request.data.get('shipping_method', 'standard'),
                shipping_address=request.data.get('shipping_address', self.request.user.location or ''),
                payment_method=request.data.get('payment_method')
            )
            if order.product.moq_status == 'active' and order.product.current_moq_count() >= order.product.moq:
                order.delivery_status = 'delivered'  # Auto-complete MOQ orders
                order.payment_status = 'paid'
                order.move_to_completed()
            orders.append(order)

        cart.items.all().delete()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP201_CREATED)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment_status', 'delivery_status', 'is_cancelled']
    ordering_fields = ['created_at', 'price']

    def get_queryset(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id and self.request.user.is_authenticated:
            return Order.objects.filter(user_id=user_id)
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.delivery_status not in ['processing', 'shipped']:
            return Response({"error": "Order cannot be cancelled in its current state"}, status=status.HTTP_400_BAD_REQUEST)
        order.is_cancelled = True
        order.delivery_status = 'cancelled'
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class CompletedOrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompletedOrderSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user_id = self.request.headers.get('X-User-Id')
        if user_id and self.request.user.is_authenticated:
            return CompletedOrder.objects.filter(user_id=user_id)
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
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
        moq_request.status = status
        moq_request.save()
        serializer = MOQRequestSerializer(moq_request)
        return Response(serializer.data)
    
