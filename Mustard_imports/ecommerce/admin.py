from django.contrib import admin
from .models import *

admin.site.register(User)   
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductVariant)
admin.site.register(Order)
admin.site.register(CompletedOrder)
admin.site.register(CustomerReview)
admin.site.register(MOQRequest)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(DeliveryLocation)
admin.site.register(Payment)


admin.site.register(OrderItem)
admin.site.register(Supplier)

    # Register your models here.
