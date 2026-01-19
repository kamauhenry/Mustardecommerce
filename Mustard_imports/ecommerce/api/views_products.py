"""
Product-related views for the Mustard Imports ecommerce API.
This module contains all product, category, and product-related endpoints.
"""

import random
import re
import logging
import pandas as pd
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import InvalidCacheBackendError
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from ..models import (
    Product, Category, Attribute, AttributeValue,
    ProductImage, Supplier, Inventory
)
from .serializers import (
    ProductSerializer, CategorySerializer, AttributeSerializer,
    AttributeValueSerializer, SupplierSerializer,
    CategoriesProductsSerializer, HomeCategorySerializer,
    HomeCategoriesPagination
)
from .permissions import IsAdminUser


logger = logging.getLogger(__name__)


# ==================== SEARCH & DISCOVERY ENDPOINTS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def search(request):
    """
    Search for products by name or description.
    Supports pagination and ordering.
    """
    query = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    ordering = request.GET.get('ordering', '-created_at')

    cache_key = f'search_{query}_{page}_{per_page}_{ordering}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).order_by(ordering)

        paginator = Paginator(products, per_page)
        page_obj = paginator.get_page(page)

        serializer = ProductSerializer(page_obj, many=True, context={'request': request})

        response_data = {
            'results': serializer.data,
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page
        }
    else:
        response_data = {
            "results": [],
            "total": 0,
            "pages": 0,
            "current_page": 1
        }

    try:
        cache.set(cache_key, response_data, timeout=60 * 10)  # Cache for 10 minutes
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to cache response: {e}")

    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def random_products(request):
    """
    Get a random selection of products (default 3).
    """
    cache_key = 'random_products'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    products = list(Product.objects.all())
    random_products_list = random.sample(products, min(3, len(products)))
    serializer = ProductSerializer(random_products_list, many=True, context={'request': request})
    response_data = {
        'results': serializer.data,
        'total': len(random_products_list)
    }

    try:
        cache.set(cache_key, response_data, timeout=60 * 30)  # Cache for 30 minutes
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to cache response: {e}")

    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])
def latest_products(request):
    """
    Get the latest products ordered by creation date.
    Supports a 'limit' parameter (default 3).
    """
    limit = int(request.GET.get('limit', 3))
    cache_key = f'latest_products_{limit}'
    try:
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Cache error: {e}. Falling back to direct query.")

    products = Product.objects.order_by('-created_at')[:limit]
    serializer = ProductSerializer(products, many=True, context={'request': request})
    response_data = {
        'results': serializer.data,
        'total': len(products)
    }

    try:
        cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
    except (InvalidCacheBackendError, Exception) as e:
        print(f"Failed to cache response: {e}")

    return Response(response_data)


# ==================== PRODUCT DETAIL & RELATED ====================

class RelatedProductsView(APIView):
    """
    Get related products from the same category, excluding the current product.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_slug, product_id):
        cache_key = f'related_products_{category_slug}_{product_id}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            queryset = Product.objects.filter(
                category__slug=category_slug,
                moq_status='active'
            ).exclude(id=product_id)[:5]
            if not queryset.exists():
                response_data = {"detail": "No related products found."}
                status_code = status.HTTP_204_NO_CONTENT
            else:
                serializer = ProductSerializer(queryset, many=True, context={'request': request})
                response_data = serializer.data
                status_code = status.HTTP_200_OK

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data, status=status_code)
        except ObjectDoesNotExist:
            raise Http404("Category or product not found.")


class ProductDetail(APIView):
    """
    Get detailed information about a specific product.
    """
    permission_classes = [permissions.AllowAny]

    def get_object(self, category_slug, product_slug):
        try:
            return Product.objects.select_related(
                'category', 'supplier'
            ).prefetch_related(
                'images', 'attribute_values__attribute', 'reviews__user'
            ).filter(
                category__slug=category_slug
            ).get(
                slug=product_slug
            )
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, category_slug, product_slug, format=None):
        cache_key = f'product_detail_{category_slug}_{product_slug}'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            logger.warning(f"Cache error: {e}. Falling back to direct query.")

        try:
            product = self.get_object(category_slug, product_slug)
            serializer = ProductSerializer(product, context={'request': request})
            response_data = serializer.data

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
            except (InvalidCacheBackendError, Exception) as e:
                logger.warning(f"Failed to cache response: {e}")

            return Response(response_data)
        except Exception as e:
            logger.error(f"Error serializing product {category_slug}/{product_slug}: {e}")
            return Response({"detail": "Error processing product data."}, status=500)


# ==================== CATEGORY VIEWS ====================

class CategoryProductsView(APIView):
    """
    Get all products for a specific category with pagination.
    """
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

            category_serializer = CategorySerializer(category, context={'request': request})
            product_serializer = ProductSerializer(products, many=True, context={'request': request})

            response_data = {
                'category': category_serializer.data,
                'products': product_serializer.data,
                'total': total,
            }

            try:
                cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data)
        except Http404:
            return Response({'error': 'Category not found or inactive'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for categories.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Category.objects.all().select_related().prefetch_related('images')
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = None
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Optimize queryset for list view"""
        if self.action == 'list':
            return Category.objects.all().only('id', 'name', 'slug').prefetch_related('images')
        return Category.objects.all().prefetch_related('images')

    def list(self, request, *args, **kwargs):
        cache_key = 'categories_list'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Invalidate category caches
        cache_keys = ['categories_list', 'category_list', 'categories_with_products', 'all_categories_with_products']
        for key in cache_keys:
            try:
                cache.delete(key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache {key}: {e}")
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        # Invalidate category caches
        cache_keys = ['categories_list', 'category_list', 'categories_with_products', 'all_categories_with_products']
        for key in cache_keys:
            try:
                cache.delete(key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache {key}: {e}")
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        # Invalidate category caches
        cache_keys = ['categories_list', 'category_list', 'categories_with_products', 'all_categories_with_products']
        for key in cache_keys:
            try:
                cache.delete(key)
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to invalidate cache {key}: {e}")
        return response


class CategoriesWithProductsViewSet(APIView):
    """
    Get all categories with their associated products.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        cache_key = 'categories_with_products'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        categories = Category.objects.prefetch_related('products')
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)


class CategoryListView(APIView):
    """
    Simple list of all categories.
    """
    def get(self, request):
        cache_key = 'category_list'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            categories = Category.objects.all().order_by('id')
            serializer = CategorySerializer(categories, many=True, context={'request': request})
            response_data = serializer.data

            try:
                cache.set(cache_key, response_data, timeout=60 * 30)  # Cache for 30 minutes
            except (InvalidCacheBackendError, Exception) as e:
                print(f"Failed to cache response: {e}")

            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllCategoriesWithProductsView(APIView):
    """
    Get all categories with their products (ignoring default manager filters).
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        cache_key = 'all_categories_with_products'
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        # Fetch all categories and their products, ignoring default manager filters
        categories = Category.objects.prefetch_related(
            Prefetch('products', queryset=Product.objects.all())
        ).all()

        serializer = CategoriesProductsSerializer(categories, many=True, context={'request': request})
        response_data = serializer.data

        try:
            cache.set(cache_key, response_data, timeout=60 * 15)  # Cache for 15 minutes
        except (InvalidCacheBackendError, Exception) as e:
            print(f"Failed to cache response: {e}")

        return Response(response_data)


@api_view(['GET'])
def pickup_home_categories(request):
    """
    Get categories that have pick-and-pay products.
    """
    page = request.query_params.get('page', '1')
    products = Product.objects.filter(is_pick_and_pay=True)
    category_ids = products.values_list('category_id', flat=True).distinct()
    categories = Category.objects.filter(id__in=category_ids)

    paginator = PageNumberPagination()
    paginator.page_size = 8  # Match HomePage.vue
    result_page = paginator.paginate_queryset(categories, request)

    serializer = HomeCategorySerializer(result_page, many=True, context={'pickup_only': True})
    return paginator.get_paginated_response(serializer.data)


class HomeCategoriesView(APIView):
    """
    Get categories with products for the home page with pagination.
    """
    permission_classes = [AllowAny]
    pagination_class = HomeCategoriesPagination

    def get(self, request, *args, **kwargs):
        cache_key = f'home_categories_with_products_page_{request.query_params.get("page", 1)}'

        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                return Response(cached_data)
        except Exception as e:
            print(f"Cache error: {e}. Falling back to direct query.")

        try:
            # Fetch all active categories ordered by id
            categories = Category.objects.all().order_by('id')

            # Debug: Print the count
            print(f"Found {categories.count()} active categories")

            # Apply pagination
            paginator = self.pagination_class()
            paginated_categories = paginator.paginate_queryset(categories, request)

            # Debug: Print paginated count
            print(f"Paginated categories count: {len(paginated_categories) if paginated_categories else 0}")

            # Serialize the paginated queryset
            serializer = HomeCategorySerializer(
                paginated_categories,
                many=True,
                context={'request': request}
            )

            # Debug: Print serialized data
            print(f"Serialized data: {serializer.data}")

            # Get the paginated response
            response = paginator.get_paginated_response(serializer.data)

            # Cache the response data (optional, but good for performance)
            try:
                cache.set(cache_key, response.data, timeout=300)  # Cache for 5 minutes
            except Exception as e:
                print(f"Cache set error: {e}")

            return response

        except Exception as e:
            print(f"HomeCategoriesView error: {str(e)}")
            return Response(
                {'error': f'Server error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== PRODUCT MANAGEMENT (ADMIN) ====================

class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for products (admin only).
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        logger.info(f"Create request data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        logger.info(f"Created product {product.id} with attribute_values: {list(product.attribute_values.all())}")
        if product.is_pick_and_pay:
            inventory = Inventory.objects.filter(product=product).first()
            logger.info(f"Inventory for product {product.id}: {inventory.quantity if inventory else 'None'}")

        # Handle multiple images
        images = request.FILES.getlist('images')
        logger.info(f"Creating product {product.name} with {len(images)} images: {[img.name for img in images]}")
        for image in images:
            try:
                ProductImage.objects.create(product=product, image=image)
                logger.info(f"Created ProductImage for {product.name}: {image.name}")
            except Exception as e:
                logger.error(f"Failed to create ProductImage for {product.name}: {image.name}, error: {str(e)}")

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        logger.info(f"Update request data: {request.data}")
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        logger.info(f"Updated product {product.id} with attribute_values: {list(product.attribute_values.all())}")
        if product.is_pick_and_pay:
            inventory = Inventory.objects.filter(product=product).first()
            logger.info(f"Inventory for product {product.id}: {inventory.quantity if inventory else 'None'}")

        # Handle multiple images
        images = request.FILES.getlist('images')
        logger.info(f"Updating product {product.name} with {len(images)} images: {[img.name for img in images]}")
        if images:
            for image in images:
                try:
                    ProductImage.objects.create(product=product, image=image)
                    logger.info(f"Created ProductImage for {product.name}: {image.name}")
                except Exception as e:
                    logger.error(f"Failed to create ProductImage for {product.name}: {image.name}, error: {str(e)}")
        else:
            logger.warning(f"No images provided for product {product.name} update")

        return Response(serializer.data)


# ==================== SUPPLIER MANAGEMENT ====================

class SupplierView(APIView):
    """
    CRUD operations for suppliers (admin only).
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            try:
                supplier = Supplier.objects.get(pk=pk)
                serializer = SupplierSerializer(supplier)
                return Response(serializer.data)
            except Supplier.DoesNotExist:
                return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            supplier = Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            supplier = Supplier.objects.get(pk=pk)
            supplier.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Supplier.DoesNotExist:
            return Response({"error": "Supplier not found"}, status=status.HTTP_404_NOT_FOUND)


# ==================== ATTRIBUTE MANAGEMENT ====================

class AttributeView(APIView):
    """
    CRUD operations for product attributes (admin only).
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            try:
                attribute = Attribute.objects.get(pk=pk)
                serializer = AttributeSerializer(attribute)
                return Response(serializer.data)
            except Attribute.DoesNotExist:
                return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)
        attributes = Attribute.objects.all()
        serializer = AttributeSerializer(attributes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AttributeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            attribute = Attribute.objects.get(pk=pk)
        except Attribute.DoesNotExist:
            return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AttributeSerializer(attribute, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            attribute = Attribute.objects.get(pk=pk)
            attribute.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Attribute.DoesNotExist:
            return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)


class AttributeValueView(APIView):
    """
    CRUD operations for attribute values (admin only).
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            try:
                attribute_value = AttributeValue.objects.get(pk=pk)
                serializer = AttributeValueSerializer(attribute_value)
                return Response(serializer.data)
            except AttributeValue.DoesNotExist:
                return Response({"error": "Attribute value not found"}, status=status.HTTP_404_NOT_FOUND)
        attribute_values = AttributeValue.objects.select_related('attribute').all()
        serializer = AttributeValueSerializer(attribute_values, many=True)
        return Response(serializer.data)

    def post(self, request):
        attribute_id = request.data.get('attribute_id')
        values = request.data.get('values', [])  # Expect a list of values
        if not attribute_id or not values:
            return Response(
                {'error': 'Both attribute_id and values are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            attribute = Attribute.objects.get(id=attribute_id)
        except Attribute.DoesNotExist:
            return Response(
                {'error': 'Attribute not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        created_values = []
        for value in values:
            value = value.strip()
            if not value or AttributeValue.objects.filter(attribute=attribute, value=value).exists():
                continue
            attribute_value = AttributeValue.objects.create(attribute=attribute, value=value)
            created_values.append(AttributeValueSerializer(attribute_value).data)
        return Response(created_values, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        try:
            attribute_value = AttributeValue.objects.get(pk=pk)
        except AttributeValue.DoesNotExist:
            return Response({"error": "Attribute value not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = AttributeValueSerializer(attribute_value, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            attribute_value = AttributeValue.objects.get(pk=pk)
            attribute_value.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AttributeValue.DoesNotExist:
            return Response({"error": "Attribute value not found"}, status=status.HTTP_404_NOT_FOUND)


class AttributeValueByAttributeView(APIView):
    """
    Get all attribute values for a specific attribute.
    """
    permission_classes = [permissions.IsAdminUser]

    def get(self, request, attribute_id):
        try:
            attribute = Attribute.objects.get(id=attribute_id)
            attribute_values = AttributeValue.objects.filter(attribute=attribute)
            serializer = AttributeValueSerializer(attribute_values, many=True)
            return Response(serializer.data)
        except Attribute.DoesNotExist:
            return Response({"error": "Attribute not found"}, status=status.HTTP_404_NOT_FOUND)


# ==================== BULK IMPORT ====================

class BulkProductImportView(APIView):
    """
    Bulk import products from CSV or Excel file.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
            else:
                return Response({"error": "Unsupported file format. Use CSV or Excel."}, status=status.HTTP_400_BAD_REQUEST)

            # Replace NaN with None for nullable fields
            df = df.replace({pd.NA: None})

            created_products = []
            errors = []

            for index, row in df.iterrows():
                try:
                    # Required fields validation
                    if not row.get('name') or not isinstance(row.get('price'), (int, float)) or pd.isna(row.get('category_id')):
                        errors.append({"row": index + 2, "error": "Missing required fields: name, price, or category_id"})
                        continue

                    is_pick_and_pay = bool(row.get('is_pick_and_pay', False))
                    product_data = {
                        'name': str(row.get('name', '')),
                        'slug': row.get('slug', slugify(row.get('name', ''))),
                        'description': str(row.get('description', '')) if row.get('description') else '',
                        'price': float(row.get('price', 0)),
                        'below_moq_price': None if is_pick_and_pay else row.get('below_moq_price', None),
                        'moq': int(row.get('moq', 1)) if not is_pick_and_pay else 1,
                        'moq_per_person': int(row.get('moq_per_person', 1)) if not is_pick_and_pay else 1,
                        'moq_status': row.get('moq_status', 'active') if not is_pick_and_pay else 'not_applicable',
                        'is_pick_and_pay': is_pick_and_pay,
                        'category_id': int(row['category_id']),
                        'supplier_id': int(row['supplier_id']) if row.get('supplier_id') and not pd.isna(row['supplier_id']) else None,
                        'meta_title': str(row.get('meta_title', '')) if row.get('meta_title') else '',
                        'meta_description': str(row.get('meta_description', '')) if row.get('meta_description') else '',
                    }

                    # Attribute processing
                    attributes_str = row.get('attributes', '')
                    attribute_value_ids = []
                    if attributes_str:
                        attributes_list = str(attributes_str).split(';')
                        for attr in attributes_list:
                            if ':' in attr:
                                name, values_str = attr.split(':', 1)
                                name = name.strip().capitalize()
                                values = [v.strip() for v in values_str.split(',') if v.strip()]
                                attribute, _ = Attribute.objects.get_or_create(name=name)
                                for value in values:
                                    attr_value, _ = AttributeValue.objects.get_or_create(attribute=attribute, value=value)
                                    attribute_value_ids.append(attr_value.id)
                    product_data['attribute_value_ids'] = attribute_value_ids

                    serializer = ProductSerializer(data=product_data)
                    if serializer.is_valid():
                        product = serializer.save()
                        # Image processing
                        image_urls = str(row.get('image_urls', '')).split(',') if row.get('image_urls') else []
                        for url in image_urls:
                            url = url.strip()
                            if url:
                                try:
                                    response = requests.get(url, timeout=10)
                                    response.raise_for_status()
                                    image_name = url.split('/')[-1] or f"image_{product.id}.jpg"
                                    ProductImage.objects.create(
                                        product=product,
                                        image=ContentFile(response.content, name=image_name)
                                    )
                                except Exception as e:
                                    logger.warning(f"Failed to download image {url} for product {product.name}: {str(e)}")
                        created_products.append(serializer.data)
                    else:
                        errors.append({"row": index + 2, "errors": serializer.errors})
                except Exception as e:
                    errors.append({"row": index + 2, "error": f"Processing error: {str(e)}"})

            response_data = {
                "created": len(created_products),
                "products": created_products,
                "errors": errors
            }
            status_code = status.HTTP_201_CREATED if created_products else status.HTTP_400_BAD_REQUEST
            return Response(response_data, status=status_code)

        except Exception as e:
            logger.error(f"Failed to process file: {str(e)}")
            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


# ==================== WEB SCRAPING ====================

class ScrapeProductsView(APIView):
    """
    Scrape products from external platforms (Shein, Alibaba).
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        platform = request.data.get('platform')
        url = request.data.get('url')
        import_type = request.data.get('import_type', 'single')
        import_count = int(request.data.get('import_count', 1)) if import_type == 'category' else 1

        if not platform or not url:
            return Response({"error": "Both 'platform' and 'url' are required."}, status=status.HTTP_400_BAD_REQUEST)

        if platform not in ['shein', 'alibaba']:
            return Response({"error": "Invalid platform."}, status=status.HTTP_400_BAD_REQUEST)

        if import_type not in ['single', 'category']:
            return Response({"error": "Invalid import_type. Must be 'single' or 'category'."}, status=status.HTTP_400_BAD_REQUEST)

        FIRECRAWL_API_KEY = settings.FIRECRAWL_API_KEY
        headers = {'Authorization': f'Bearer {FIRECRAWL_API_KEY}'}

        try:
            if import_type == 'single':
                product = self.fetch_single_product(platform, url, headers)
                if not product:
                    return Response({"error": "No product found."}, status=status.HTTP_404_NOT_FOUND)
                products = [product]
            else:  # category
                product_urls = self.fetch_category_product_urls(platform, url, import_count, headers)
                products = []
                for product_url in product_urls:
                    product = self.fetch_single_product(platform, product_url, headers)
                    if product:
                        products.append(product)
                    if len(products) >= import_count:
                        break
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        saved_products = []
        for product in products:
            serializer = ProductSerializer(data=product, context={'request': request})
            if serializer.is_valid():
                product_instance = serializer.save()
                saved_products.append(serializer.data)
            else:
                logger.error(f"Serialization error: {serializer.errors}")

        return Response({
            "message": f"Successfully saved {len(saved_products)} products.",
            "products": saved_products
        }, status=status.HTTP_201_CREATED)

    def fetch_single_product(self, platform, url, headers):
        if platform == 'shein':
            return self.fetch_shein_single_product(url, headers)
        elif platform == 'alibaba':
            return self.fetch_alibaba_single_product(url, headers)

    def fetch_category_product_urls(self, platform, url, count, headers):
        response = requests.get(
            'https://api.firecrawl.dev/scrape',
            headers=headers,
            params={'url': url, 'format': 'extract', 'extract': {'selector': 'a[href*="/product/"]'}}
        )
        response.raise_for_status()
        data = response.json()
        product_links = [link['href'] for link in data.get('extracted', []) if 'href' in link][:count]
        return product_links

    def fetch_alibaba_single_product(self, url, headers):
        response = requests.get(
            'https://api.firecrawl.dev/scrape',
            headers=headers,
            params={
                'url': url,
                'format': 'extract',
                'extract': {
                    'name': 'h1.module-pdp-title',
                    'price': 'span.price-number',
                    'moq': 'div.moq-value',
                    'description': 'div.module-pdp-description',
                    'thumbnail': 'img.magnifier-image',
                    'images': 'div.product-images img',
                    'supplier': 'a.supplier-name',
                    'attributes': 'div.sku-item'
                }
            }
        )
        response.raise_for_status()
        data = response.json()['extracted']

        if not data.get('name'):
            return None

        category_name = "Alibaba"  # Simplified; adjust as needed
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={"slug": slugify(category_name), "description": f"Category for {category_name}", "is_active": True}
        )

        price_text = data.get('price', '0.0').replace('$', '').replace('US', '').replace(',', '')
        try:
            if '-' in price_text:
                prices = price_text.split('-')
                price_usd = float(prices[0].strip()) * 1.35
                below_moq_price_usd = float(prices[1].strip()) * 1.35
            else:
                price_usd = float(price_text) * 1.35
                below_moq_price_usd = price_usd * 1.2
        except ValueError:
            price_usd = below_moq_price_usd = 0.0
        USD_TO_KES_RATE = 130.50
        price_kes = round(price_usd * USD_TO_KES_RATE)
        below_moq_price_kes = round(below_moq_price_usd * USD_TO_KES_RATE)

        moq_text = data.get('moq', '1')
        try:
            moq = int(re.search(r'\d+', moq_text).group())
        except (AttributeError, ValueError):
            moq = 1

        supplier_name = data.get('supplier', 'N/A')
        supplier, _ = Supplier.objects.get_or_create(
            name=supplier_name,
            defaults={"contact_email": "", "phone": "", "address": ""}
        )

        attribute_value_ids = []
        attributes = data.get('attributes', [])
        for attr in attributes:
            attr_name = attr.get('sku-title', '').replace(':', '').lower()
            if not attr_name:
                continue
            attribute, _ = Attribute.objects.get_or_create(name=attr_name)
            attr_values = attr.get('sku-item-option', [])
            for value in attr_values:
                attr_value = value.strip().lower()
                if not attr_value:
                    continue
                attribute_value, _ = AttributeValue.objects.get_or_create(attribute=attribute, value=attr_value)
                attribute_value_ids.append(attribute_value.id)

        product = {
            'name': data.get('name', 'Unknown Product'),
            'slug': slugify(data.get('name', 'Unknown Product'))[:50],
            'description': data.get('description', 'No description available'),
            'price': price_kes,
            'below_moq_price': below_moq_price_kes,
            'moq': moq,
            'moq_per_person': 1,
            'moq_status': 'not_applicable',
            'category_id': category.id,
            'supplier_id': supplier.id,
            'meta_title': data.get('name', 'Unknown Product'),
            'meta_description': data.get('description', 'No description available')[:150] + "...",
            'attribute_value_ids': attribute_value_ids,
            'thumbnail': data.get('thumbnail', ''),
            'images': data.get('images', [data.get('thumbnail', '')]) if data.get('thumbnail') else []
        }
        return product

    def fetch_shein_single_product(self, url, headers):
        response = requests.get(
            'https://api.firecrawl.dev/scrape',
            headers=headers,
            params={
                'url': url,
                'format': 'extract',
                'extract': {
                    'name': 'h1.product-intro__head-name',
                    'price': 'div.product-intro__head-mainprice',
                    'description': 'div.product-intro__description',
                    'thumbnail': 'img.product-intro__main-image',
                    'attributes': 'div.product-intro__sku-item'
                }
            }
        )
        response.raise_for_status()
        data = response.json()['extracted']

        if not data.get('name'):
            return None

        category, _ = Category.objects.get_or_create(
            name="Shein",
            defaults={"slug": "shein", "description": "Products scraped from Shein", "is_active": True}
        )

        price_text = data.get('price', '0.0').replace('€', '').replace('$', '').replace(',', '')
        try:
            if '-' in price_text:
                prices = price_text.split('-')
                price_usd = float(prices[0].strip())
                below_moq_price_usd = float(prices[1].strip())
            else:
                price_usd = float(price_text)
                below_moq_price_usd = price_usd * 1.2
        except ValueError:
            price_usd = below_moq_price_usd = 0.0
        USD_TO_KES_RATE = 130.50
        price_kes = round(price_usd * USD_TO_KES_RATE)
        below_moq_price_kes = round(below_moq_price_usd * USD_TO_KES_RATE)

        attribute_value_ids = []
        attributes = data.get('attributes', [])
        for attr in attributes:
            attr_name = attr.get('sku-title', '').replace(':', '').lower()
            if not attr_name:
                continue
            attribute, _ = Attribute.objects.get_or_create(name=attr_name)
            attr_values = attr.get('sku-item-option', [])
            for value in attr_values:
                attr_value = value.strip().lower()
                if not attr_value:
                    continue
                attribute_value, _ = AttributeValue.objects.get_or_create(attribute=attribute, value=attr_value)
                attribute_value_ids.append(attribute_value.id)

        product = {
            'name': data.get('name', 'Unknown Product'),
            'slug': slugify(data.get('name', 'Unknown Product'))[:50],
            'description': data.get('description', 'No description available'),
            'price': price_kes,
            'below_moq_price': below_moq_price_kes,
            'moq': 1,
            'moq_per_person': 1,
            'moq_status': 'not_applicable',
            'category_id': category.id,
            'supplier_id': None,
            'meta_title': data.get('name', 'Unknown Product'),
            'meta_description': data.get('description', 'No description available')[:150] + "...",
            'attribute_value_ids': attribute_value_ids,
            'thumbnail': data.get('thumbnail', ''),
            'images': [data.get('thumbnail', '')] if data.get('thumbnail') else []
        }
        return product
