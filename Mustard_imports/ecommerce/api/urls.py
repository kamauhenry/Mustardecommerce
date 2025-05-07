from django.urls import path, include
from rest_framework import routers
from .views import (
    CategoryViewSet, UserProfileView, search, OrderViewSet, 
    CompletedOrderViewSet, CustomerReviewViewSet, 
    MOQRequestViewSet, UserViewSet, RegisterView, 
    LoginView, get_current_user, ProductDetail, 
    CategoryListView, CategoriesWithProductsViewSet, 
    CategoryProductsView, AllCategoriesWithProductsView, 
    create_cart, get_user_cart, add_item_to_cart, 
    update_cart_item_quantity, remove_cart_item, 
    get_user_orders, test_image, 
    process_payment, get_payment_details, DeliveryLocationView,
    autocomplete, place_details, logout_view, mpesa_callback, 
    create_order_from_cart, update_order_shipping, GoogleAuthView,
    ChangePasswordView, latest_products, random_products,
    AdminRegisterView, AdminLoginView, AdminLogoutView, 
    AdminProfileView, admin_dashboard, ProductReviewsView,
    RelatedProductsView, get_all_orders, get_moq_fulfilled_products,
    place_order_for_product, bulk_update_order_status,update_single_order_status,ProductViewSet, SupplierView, AttributeView, AttributeValueView,HomeCategoriesView,BulkProductImportView,AttributeValueByAttributeView,ScrapeProductsView, update_cart_shipping_method, get_shipping_methods,shipping_methods1, shipping_method_detail1,
)

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'admin/products', ProductViewSet, basename='product') 

urlpatterns = [
    path('', include(router.urls)),
    
    # Admin endpoints
    path('admin-page/register/', AdminRegisterView.as_view(), name='admin_register'),
    path('admin-page/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-page/logout/', AdminLogoutView.as_view(), name='admin_logout'),
    path('admin-page/profile/', AdminProfileView.as_view(), name='admin_profile'),
    path('admin-page/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/orders/', get_all_orders, name='get_all_orders'),
    path('admin/moq-fulfilled-products/', get_moq_fulfilled_products, name='get_moq_fulfilled_products'),
    path('admin/products/<int:product_id>/place-order/', place_order_for_product, name='place_order_for_product'),
    path('admin/orders/bulk-update/', bulk_update_order_status, name='bulk_update_order_status'),
    path('admin/orders/<int:order_id>/update-status/', update_single_order_status, name='update_single_order_status'),
    path('admin/suppliers/', SupplierView.as_view(), name='supplier-list'),
    path('admin/suppliers/<int:pk>/', SupplierView.as_view(), name='supplier-detail'),
    path('admin/attributes/', AttributeView.as_view(), name='attribute-list'),
    path('admin/attributes/<int:pk>/', AttributeView.as_view(), name='attribute-detail'),
    path('admin/attribute-values/', AttributeValueView.as_view(), name='attribute-value-list'),
    path('admin/attribute-values/<int:pk>/', AttributeValueView.as_view(), name='attribute-value-detail'),
    path('admin/attribute-values/by-attribute/<int:attribute_id>/', AttributeValueByAttributeView.as_view(), name='attribute-values-by-attribute'),
    path('admin/bulk-import/', BulkProductImportView.as_view(), name='bulk-import'),
    path('admin/scrape-products/', ScrapeProductsView.as_view(), name='scrape-products'),
    path('shipping_methods1/', shipping_methods1, name='shipping_methods1'),
    path('shipping_methods1/<int:shipping_method_id>/', shipping_method_detail1, name='shipping_method_detail1'),


    # Authentication
    path('auth/logout/', logout_view, name='logout'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/user/me', get_current_user, name='get_current_user'),

    # Products and search
    path('products/search/', search, name='search'), 
    path('products/random/', random_products, name='random-products'),
    path('products/latest/', latest_products, name='latest-products'),
    path('products/<int:product_id>/reviews/', ProductReviewsView.as_view(), name='product-reviews'),
    path('products/<slug:category_slug>/<slug:product_slug>/', ProductDetail.as_view(), name='product-detail'),
    path('categories-with-products/', CategoriesWithProductsViewSet.as_view(), name='categories-with-products'),
    path('category/<slug:category_slug>/products/<int:product_id>/related/', RelatedProductsView.as_view(), name='related-products'),
    path('category/<slug:category_slug>/products/', CategoryProductsView.as_view(), name='category-products'),
    path('all-categories-with-products/', AllCategoriesWithProductsView.as_view(), name='all-categories-with-products'),
    path('test-image/', test_image, name='test-image'),
    path('home-categories/', HomeCategoriesView.as_view(), name='home-categories'),

    # Cart and orders
    path('users/<int:user_id>/create_cart/', create_cart, name='create-cart-for-user'),
    path('users/<int:user_id>/cart/', get_user_cart, name='get-user-cart'),
    path('orders/', get_user_orders, name='get-user-orders'),
    path('orders/<int:order_id>/', get_user_orders, name='get-order-detail'),
    path('create_cart/', create_cart, name='create-cart'),
    path('carts/<int:cart_id>/add_item/', add_item_to_cart, name='add-item-to-cart'),
    path('cart-items/<int:item_id>/update_cart_item_quantity/', update_cart_item_quantity, name='update-cart-item-quantity'),
    path('carts/<int:cart_id>/remove_item/', remove_cart_item, name='remove-cart-item'),

    path('carts/<int:cart_id>/create-order/', create_order_from_cart, name='create-order-from-cart'),
 
    path('cart/<int:cart_id>/update-shipping/', update_cart_shipping_method, name='update_cart_shipping_method'),
    path('shipping-methods/', get_shipping_methods, name='get_shipping_methods'),
    path('orders/<int:order_id>/update-shipping/', update_order_shipping, name='update-order-shipping'),

    # Payment
    path('process-payment/', process_payment, name='process_payment'),
    path('payment-details/<int:order_id>/', get_payment_details, name='get_payment_details'),
    path('mpesa-callback/', mpesa_callback, name='mpesa-callback'),

    # Profile
    path('user/profile/me', UserProfileView.as_view(), name='user-profile'),
    path('user/update-user/', UserViewSet.as_view({'put': 'update'}), name='user-update'),
    path('user/delivery-locations/', DeliveryLocationView.as_view(), name='delivery_locations'),
    path('user/delivery-locations/<int:location_id>/', DeliveryLocationView.as_view(), name='delivery_location_detail'),
    path('user/delivery-locations/<int:location_id>/set-default/', DeliveryLocationView.as_view(), name='set_default_location'),
    path('autocomplete/', autocomplete, name='autocomplete'),
    path('place-details/', place_details, name='place_details'),
]