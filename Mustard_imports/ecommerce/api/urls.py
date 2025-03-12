from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    ProductViewSet,
    CartViewSet,
    OrderViewSet,
    CompletedOrderViewSet,
    CustomerReviewViewSet,
    MOQRequestViewSet,
)

# Creating DRF router
router = routers.DefaultRouter()

# Registers viewsets with the router
router.register(r'categories', CategoryViewSet, basename="categories")
router.register(r'products', ProductViewSet, basename="products")
router.register(r'carts', CartViewSet, basename="cart")
router.register(r'orders', OrderViewSet, basename="order")
router.register(r'completed-orders', CompletedOrderViewSet, basename="completed-order")
router.register(r'reviews', CustomerReviewViewSet, basename="reviews")
router.register(r'moq-requests', MOQRequestViewSet, basename="moq-requests")

# Define URL patterns
urlpatterns = [
    # Include all router-generated routes
    path('', include(router.urls)),

    # Optional: Include DRF's authentication endpoints (e.g., login/logout)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
