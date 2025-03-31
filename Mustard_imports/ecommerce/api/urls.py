from django.urls import path, include
from rest_framework import routers
from .views import (CategoryViewSet,UserProfileView, search , OrderViewSet, 
                   CompletedOrderViewSet, CustomerReviewViewSet, 
                   MOQRequestViewSet, UserViewSet, RegisterView, 
                   LoginView, get_current_user, ProductDetail, 
                   CategoryListView, CategoriesWithProductsViewSet, 
                   CategoryProductsView, AllCategoriesWithProductsView, 
                   create_cart, get_user_cart, add_item_to_cart, 
                   update_cart_item_quantity, remove_cart_item, 
                   process_checkout, get_user_orders, test_image, 
                   process_payment, get_payment_details,DeliveryLocationView,autocomplete,place_details)


# Creating DRF router
router = routers.DefaultRouter()

# Register viewsets with the router
router.register(r'categories', CategoryViewSet, basename='category')




#router.register(r'completed-orders', CompletedOrderViewSet, basename='completed-order')
#router.register(r'reviews', CustomerReviewViewSet, basename='review')
#router.register(r'moq-requests', MOQRequestViewSet, basename='moq-request')
#router.register(r'users', UserViewSet, basename='user')

# Define URL patterns
urlpatterns = [
    # Prefix all API routes under /api/
    path('api/', include(router.urls)),
    
    # Custom authentication views
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/user/', get_current_user, name='get_current_user'),

    # Remove default DRF auth URLs to avoid conflicts with custom LoginView
    # path('auth/', include('rest_framework.urls', namespace='rest_framework')),  # Commented out
    path('products/search/', search, name='search'), 
    # Product and category-related URLs
    path('products/<slug:category_slug>/<slug:product_slug>/', ProductDetail.as_view(), name='product-detail'),

    path('categories-with-products/', CategoriesWithProductsViewSet.as_view(), name='categories-with-products'),
    path('category/<slug:category_slug>/products/', CategoryProductsView.as_view(), name='category-products'),
    path('all-categories-with-products/', AllCategoriesWithProductsView.as_view(), name='all-categories-with-products'),
    path('test-image/', test_image, name='test-image'),

    # Custom cart and order actions
    path('users/<int:user_id>/create_cart/', create_cart, name='create-cart-for-user'),
    path('users/<int:user_id>/cart/', get_user_cart, name='get-user-cart'),
    path('orders/', get_user_orders, name='get-user-orders'),
    path('orders/<int:order_id>', get_user_orders, name='get-user-orders'),
    path('create_cart/', create_cart, name='create-cart'),
    path('carts/<int:cart_id>/add_item/', add_item_to_cart, name='add-item-to-cart'),
    path('cart-items/<int:item_id>/update_cart_item_quantity/', update_cart_item_quantity, name='update-cart-item-quantity'),
    path('carts/<int:cart_id>/remove_item/', remove_cart_item, name='remove-cart-item'),
    path('carts/<int:cart_id>/checkout/', process_checkout, name='process-checkout'),

    #custom  payment actions 
  
    path('process-payment/', process_payment, name='process_payment'),
    path('payment-details/<int:order_id>/', get_payment_details, name='get_payment_details'),

# Profile
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/delivery-locations/', DeliveryLocationView.as_view(), name='delivery_locations'),
    path('user/delivery-locations/<int:location_id>/', DeliveryLocationView.as_view(), name='delivery_location_detail'),
    path('user/delivery-locations/<int:location_id>/set-default/', DeliveryLocationView.as_view(), name='set_default_location'),
    path('autocomplete/', autocomplete, name='autocomplete'),
    path('place-details/', place_details, name='place_details'),
]