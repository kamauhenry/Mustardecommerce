from django.urls import include, path
from rest_framework import routers
from .views import *
from ..views import index
# Creating DRF router
router = routers.DefaultRouter()

# Registers viewsets with the router
router.register(r'categories', CategoryViewSet)  # Has queryset, no basename needed
router.register(r'products', ProductViewSet)    
router.register(r'carts', CartViewSet, basename='cart')  
router.register(r'orders', OrderViewSet, basename='order')  
router.register(r'completed-orders', CompletedOrderViewSet, basename='completed-order')
router.register(r'reviews', CustomerReviewViewSet , basename='review')  
router.register(r'moq-requests', MOQRequestViewSet, basename='moq-request')  

# Define URL patterns
urlpatterns = [
    path('', include(router.urls)),  
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    
    path('', include(router.urls)),
    path('products/<slug:category_slug>/<slug:product_slug>/', ProductDetail.as_view(), name='product-detail'),
    path('categories-with-products/', CategoriesWithProductsViewSet.as_view(), name='categories-with-products'),
    path('category/<int:category_id>/products/', CategoryProductsView.as_view(), name='category-products'),
    path('all-categories-with-products/', AllCategoriesWithProductsView.as_view(), name='all-categories-with-products'),
    


]