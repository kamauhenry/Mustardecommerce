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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from decimal import Decimal
from .permissions import IsOwnerOrAdmin, IsAdminUser
from ..models import *
from .serializers import *
from django.http import JsonResponse, Http404
from django.db import IntegrityError
from django.db import transaction
from django.utils import timezone
import logging
from django.db import connection, transaction
from django.db.models import Max


def reset_order_id_sequence():
    with connection.cursor() as cursor:
        # Get the current maximum ID
        cursor.execute("SELECT MAX(id) FROM ecommerce_order")
        max_id = cursor.fetchone()[0] or 0
        # Reset the sequence to be higher than the current maximum
        cursor.execute(f"SELECT setval('ecommerce_order_id_seq', {max_id + 1}, false)")


User = get_user_model()

# Authentication Views

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return super().get_serializer_class()

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Create or get a token for this user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'username': user.username,
                'token': token.key  # Return the token to the client
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # Token validation should be handled by permission classes in each view
        # This endpoint is kept for compatibility
        if request.user.is_authenticated:
            return Response({
                'message': 'Logged in',
                'user_id': request.user.id,
                'username': request.user.username
            }, status=status.HTTP_200_OK)
        return Response({'message': 'Not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create a token for the new user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username,
                'token': token.key  # Return the token to the client
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):

    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
    })


@api_view(['POST'])
def create_cart(request, user_id=None):
    # If user_id is provided, use that. Otherwise, use current user
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user
    
    # Check if user is authenticated
    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Use get_or_create to avoid duplicate carts for the user
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_cart(request, user_id):
    # Ensure the requesting user is either the cart owner or an admin
    if request.user.id != user_id and not request.user.is_staff:
        return Response(
            {"detail": "You do not have permission to access this cart."}, 
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        # Try to get an existing cart or create a new one
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item_to_cart(request, cart_id):
    try:
        # cart_id is now coming from the URL parameter
        product_id = request.data.get('productId')
        variant_id = request.data.get('variantId')
        quantity = request.data.get('quantity', 1)

        cart = Cart.objects.get(id=cart_id)
        product = Product.objects.get(id=product_id)
        variant = ProductVariant.objects.get(id=variant_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product, 
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Product variant not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_item_quantity(request, item_id):  # Add item_id as URL param
    try:
        # Get cart_id from request data (optional, depending on your needs)
        cart_id = request.data.get('cart_id')
        new_quantity = request.data.get('quantity')

        # Validate new_quantity
        if not isinstance(new_quantity, int) or new_quantity < 1:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch cart item using item_id and optionally cart_id
        if cart_id:
            cart_item = CartItem.objects.get(id=item_id, cart_id=cart_id)
        else:
            cart_item = CartItem.objects.get(id=item_id)

        # Check authorization
        if cart_item.cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        cart_item.quantity = new_quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, cart_id):  # Add cart_id as URL param
    try:
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({"error": "Item ID required"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the cart item
        cart_item = CartItem.objects.get(id=item_id, cart_id=cart_id)
        
        # Authorization check
        if cart_item.cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Delete the cart item
        cart_item.delete()

        # Return updated cart
        cart = Cart.objects.get(id=cart_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


logger = logging.getLogger(__name__)
@api_view(['POST']) 
@permission_classes([IsAuthenticated]) 
def process_checkout(request, cart_id): 
    try:

        # Log incoming request data
        logger.info(f"Processing checkout for cart {cart_id}. Data: {request.data}")
        reset_order_id_sequence()
        # Extract checkout data with defaults
        shipping_method = request.data.get('shipping_method', 'standard') 
        shipping_address = request.data.get('shipping_address', 'shop pick up')

        # Retrieve the cart
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the user owns the cart
        if cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        # Check if the cart has items
        if cart.items.count() == 0:
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Log cart items before processing
        logger.info(f"Cart contains {cart.items.count()} items")
        highest_id = Order.objects.aggregate(Max('id'))['id__max'] or 0
        next_id = highest_id + 1
        # Use a database transaction to ensure atomicity
        with transaction.atomic():
            # Check if an order was already created for this cart but not completed
            existing_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
            for existing_order in existing_orders:
                # If we find a recent order with no items, it might be a failed checkout
                if not existing_order.items.exists() and (timezone.now() - existing_order.created_at).seconds < 300:  # 5 min
                    logger.info(f"Found incomplete order #{existing_order.id}, deleting it")
                    existing_order.delete()
            
            # Create order with all necessary details
            order = Order.objects.create(
                id=next_id, 
                user=cart.user,
                shipping_method=shipping_method,
                shipping_address=shipping_address,
            )
            
            # Prepare order items
            order_items = []
            total_price = Decimal('0.00')

            for cart_item in cart.items.all():
                # Calculate price per unit (check for division by zero)
                if cart_item.quantity > 0:
                    price_per_unit = cart_item.line_total / cart_item.quantity
                else:
                    price_per_unit = Decimal('0.00')
                    logger.warning(f"Cart item {cart_item.id} has quantity 0")

                # Log values before creating order item
                logger.info(f"Creating order item: product={cart_item.product.id}, " 
                           f"quantity={cart_item.quantity}, price={price_per_unit}")

                # Create order item
                order_item = OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=price_per_unit
                )
                
                # Calculate total price
                total_price += cart_item.line_total
                order_items.append(order_item)

            # Update order with total price
            logger.info(f"Total price calculated: {total_price}")
            order.total_price = total_price
            order.save()

            # Clear the cart after checkout
            cart.items.all().delete()

            # Serialize and return the order
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except IntegrityError as e:
        logger.error(f"IntegrityError during checkout: {str(e)}")
        return Response(
            {"error": "Failed to create order due to a database conflict. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        logger.error(f"Unexpected error during checkout: {str(e)}", exc_info=True)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def format_phone_number(phone_number):
    """
    Format phone number to start with 254 if it starts with 0
    
    Args:
        phone_number (str): Input phone number
    
    Returns:
        str: Formatted phone number
    """
    # Remove any spaces or dashes
    phone_number = ''.join(phone_number.split())
    
    # Check if number starts with 0
    if phone_number.startswith('0'):
        # Replace leading 0 with 254
        return f'254{phone_number[1:]}'
    
    # If already starts with 254, return as is
    if phone_number.startswith('254'):
        return phone_number
    
    # If no country code, assume local number and add 254
    if len(phone_number) == 9 and phone_number[0] in '17':
        return f'254{phone_number}'
    
    # If number is too short or invalid, raise an error
    if len(phone_number) < 9:
        raise ValueError("Invalid phone number: number is too short")
    
    # If number doesn't match expected formats, return original
    return phone_number


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    """
    View to process payment for an order
    """
    try:
        order_id = request.data.get('order_id')
        phone_number = request.data.get('phone_number')
        payment_method = request.data.get('payment_method', 'other')


                # Format phone number
        try:
            formatted_phone_number = format_phone_number(phone_number)
        except ValueError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the order
        order = Order.objects.get(
            id=order_id, 
            user=request.user, 
            payment_status='pending'
        )

        # Create payment record
        payment = Payment.objects.create(
            order=order,
            phone_number=phone_number,
            payment_method=payment_method,
            amount=order.total_price,
            payment_status='pending'
        )

        # Update order payment status
        order.payment_status = 'paid'
        order.save()

        # Update payment status
        payment.payment_status = 'completed'
        payment.save()

        return Response({
            'order_id': order.id,
            'amount': payment.amount,
            'phone_number': payment.phone_number,
            'payment_method': payment.payment_method,
            'payment_status': payment.payment_status
        }, status=status.HTTP_200_OK)

    except Order.DoesNotExist:
        return Response(
            {"error": "Order not found or already paid"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_details(request, order_id):
    """
    View to retrieve payment details for a specific order
    """
    try:
        payment = Payment.objects.get(
            order_id=order_id, 
            order__user=request.user
        )
        
        return Response({
            'order_id': payment.order.id,
            'amount': payment.amount,
            'phone_number': payment.phone_number,
            'payment_method': payment.payment_method,
            'payment_status': payment.payment_status,
            'payment_date': payment.payment_date
        }, status=status.HTTP_200_OK)

    except Payment.DoesNotExist:
        return Response(
            {"error": "Payment not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_orders(request):
    """
    Retrieve all orders for the authenticated user
    """
    try:
        orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



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
    
