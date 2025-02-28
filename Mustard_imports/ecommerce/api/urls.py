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
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'carts', CartViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'completed-orders', CompletedOrderViewSet)
router.register(r'reviews', CustomerReviewViewSet)
router.register(r'moq-requests', MOQRequestViewSet)

# Define URL patterns
urlpatterns = [
    # Include all router-generated routes
    path('', include(router.urls)),
    
    # Optional: Include DRF's authentication endpoints (e.g., login/logout)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]