from django.urls import include, path, re_path
from rest_framework import routers
from .views import *
from ..views import index
# Creating DRF router
router = routers.DefaultRouter()

# Registers viewsets with the router
router.register(r'categories', CategoryViewSet)  # Has queryset, no basename needed
router.register(r'products', ProductViewSet)     # Has queryset, no basename needed
router.register(r'carts', CartViewSet, basename='cart')  # No queryset, needs basename
router.register(r'orders', OrderViewSet, basename='order')  # No queryset, needs basename
router.register(r'completed-orders', CompletedOrderViewSet, basename='completed-order')  # No queryset, needs basename
router.register(r'reviews', CustomerReviewViewSet , basename='review')  # Has queryset, no basename needed
router.register(r'moq-requests', MOQRequestViewSet, basename='moq-request')  # No queryset, needs basename

# Define URL patterns
urlpatterns = [
    path('api/', include(router.urls)),  # Prefix all API routes with /api/
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Catch-all route for Vue.js frontend
    re_path(r'^(?!api/).*$', index),
]