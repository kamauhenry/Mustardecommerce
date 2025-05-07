from django.contrib import admin
from .models import *

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_status', 'mpesa_receipt_number', 'phone_number', 'amount')

admin.site.register(User)   
admin.site.register(Category)
admin.site.register(Product)

admin.site.register(Order)
admin.site.register(CompletedOrder)
admin.site.register(CustomerReview)
admin.site.register(MOQRequest)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(DeliveryLocation)

admin.site.register(AdminUser)







admin.site.register(OrderItem)
admin.site.register(Supplier)

    # Register your models here.


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'thumbnail']
    list_filter = ['product']
    readonly_fields = ['thumbnail']