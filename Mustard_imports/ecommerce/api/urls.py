from django.urls import path, include
from rest_framework import routers
from .views import (
    CategoryViewSet, ProductViewSet, ProductDetail, CategoryProductsView,
    CategoriesWithProductsViewSet, AllCategoriesWithProductsView,
    CartViewSet, OrderViewSet, CompletedOrderViewSet, CustomerReviewViewSet,
    MOQRequestViewSet, RegisterView, LoginView, AdminRegisterView, AdminLoginView, AdminLogoutView, AdminProfileView, admin_dashboard
)

# Creating DRF router
router = routers.DefaultRouter()

# Register viewsets with the router
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')  # Added basename for ProductViewSet
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'completed-orders', CompletedOrderViewSet, basename='completed-order')
router.register(r'reviews', CustomerReviewViewSet, basename='review')
router.register(r'moq-requests', MOQRequestViewSet, basename='moq-request')

# Define URL patterns
urlpatterns = [
    # Prefix all API routes under /api/
    path('api/', include(router.urls)),
    
    # Custom authentication views
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('admin-page/register/', AdminRegisterView.as_view(), name='admin_register'),
    path('admin-page/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-page/logout/', AdminLogoutView.as_view(), name='admin_logout'),
    path('admin-page/profile/', AdminProfileView.as_view(), name='admin_profile'),
    path('admin-page/dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # Remove default DRF auth URLs to avoid conflicts with custom LoginView
    # path('auth/', include('rest_framework.urls', namespace='rest_framework')),  # Commented out
    
    # Product and category-related URLs
    path('products/<slug:category_slug>/<slug:product_slug>/', ProductDetail.as_view(), name='product-detail'),
    path('categories-with-products/', CategoriesWithProductsViewSet.as_view(), name='categories-with-products'),
    path('category/<slug:category_slug>/products/', CategoryProductsView.as_view(), name='category-products'),
    path('all-categories-with-products/', AllCategoriesWithProductsView.as_view(), name='all-categories-with-products'),
    
    # Custom cart and order actions
    path('carts/<int:pk>/add_item/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('carts/<int:pk>/remove_item/', CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove-item'),
    path('carts/<int:pk>/checkout/', CartViewSet.as_view({'post': 'checkout'}), name='cart-checkout'),
    path('orders/<int:pk>/cancel/', OrderViewSet.as_view({'post': 'cancel'}), name='order-cancel'),
]