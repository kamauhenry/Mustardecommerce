from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from ..models import Cart, CartItem, Product, ShippingMethod, Inventory, User
from .serializers import CartSerializer, CartItemSerializer, ShippingMethodSerializer
from .permissions import IsAdminUser
import logging

logger = logging.getLogger(__name__)


def create_cart(request, user_id=None):
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user

    if not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_cart(request, user_id):
    if request.user.id != user_id and not request.user.is_staff:
        return Response(
            {"detail": "You do not have permission to access this cart."},
            status=status.HTTP_403_FORBIDDEN
        )

    cache_key = f'user_cart_{user_id}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    try:
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        serializer = CartSerializer(cart)
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 2)  # Cache for 2 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_item_to_cart(request, cart_id):
    try:
        product_id = request.data.get('productId')
        attributes = request.data.get('attributes', {})
        quantity = request.data.get('quantity', 1)
        shipping_method_id = request.data.get('shippingMethodId')

        cart = Cart.objects.get(id=cart_id, user=request.user)
        product = Product.objects.get(id=product_id)

        # Validate attributes against product attribute_values
        if attributes:
            product_attribute_values = product.attribute_values.all()
            product_attributes = {}
            for attr_value in product_attribute_values:
                attr_name = attr_value.attribute.name
                if attr_name not in product_attributes:
                    product_attributes[attr_name] = []
                product_attributes[attr_name].append(attr_value.value)

            for attr_name, attr_value in attributes.items():
                if attr_name not in product_attributes:
                    return Response(
                        {"error": f"Invalid attribute: {attr_name}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                if attr_value not in product_attributes[attr_name]:
                    return Response(
                        {"error": f"Invalid value for {attr_name}: {attr_value}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        # Validate inventory for Pick and Pay products
        quantity = int(quantity)
        if product.is_pick_and_pay:
            if not product.inventory:
                return Response(
                    {"error": "No inventory available for this product"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if quantity > product.inventory.quantity:
                return Response(
                    {"error": f"Requested quantity ({quantity}) exceeds available stock ({product.inventory.quantity})"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Update shipping method if provided
        if shipping_method_id:
            try:
                shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
                cart.shipping_method = shipping_method
                cart.save()
            except ShippingMethod.DoesNotExist:
                return Response(
                    {"error": "Shipping method not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif product.is_pick_and_pay:
            cart.shipping_method = None
            cart.save()

        # Determine price based on quantity and MOQ
        moq_per_person = product.moq_per_person or 1
        price = product.price if quantity >= moq_per_person else product.below_moq_price or product.price

        # Create or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            attributes=attributes,
            defaults={'quantity': quantity, 'attributes': attributes}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.attributes = attributes
            cart_item.save()

        # Invalidate cart cache
        cache_key = f'user_cart_{cart.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_shipping_method(request, cart_id):
    try:
        shipping_method_id = request.data.get('shippingMethodId')
        cart = Cart.objects.get(id=cart_id, user=request.user)

        if shipping_method_id:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id, is_active=True)
            cart.shipping_method = shipping_method
        else:
            cart.shipping_method = None
        cart.save()

        # Invalidate cart cache
        cache_key = f'user_cart_{cart.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    except ShippingMethod.DoesNotExist:
        return Response({"error": "Shipping method not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_item_quantity(request, item_id):
    try:
        cart_id = request.data.get('cart_id')
        new_quantity = request.data.get('quantity')

        if not isinstance(new_quantity, int) or new_quantity < 1:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)

        if cart_id:
            cart_item = CartItem.objects.get(id=item_id, cart_id=cart_id)
        else:
            cart_item = CartItem.objects.get(id=item_id)

        if cart_item.cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        cart_item.quantity = new_quantity
        cart_item.save()

        # Invalidate cart cache
        cache_key = f'user_cart_{cart_item.cart.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_cart_item(request, cart_id):
    try:
        item_id = request.data.get('item_id')

        if not item_id:
            return Response({"error": "Item ID required"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item = CartItem.objects.get(id=item_id, cart_id=cart_id)

        if cart_item.cart.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        cart_item.delete()

        # Invalidate cart cache
        cache_key = f'user_cart_{cart_item.cart.user.id}'
        try:
            cache.delete(cache_key)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to invalidate cache: {e}")

        cart = Cart.objects.get(id=cart_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Shipping Methods

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shipping_methods(request):
    try:
        shipping_methods = ShippingMethod.objects.filter(is_active=True)
        serializer = ShippingMethodSerializer(shipping_methods, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def shipping_methods1(request):
    if request.method == 'GET':
        try:
            shipping_methods = ShippingMethod.objects.filter(is_active=True)
            serializer = ShippingMethodSerializer(shipping_methods, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        try:
            serializer = ShippingMethodSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def shipping_method_detail1(request, shipping_method_id):
    try:
        shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
    except ShippingMethod.DoesNotExist:
        return Response({"error": "Shipping method not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        try:
            serializer = ShippingMethodSerializer(shipping_method, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        try:
            shipping_method.delete()
            return Response({"message": "Shipping method deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
