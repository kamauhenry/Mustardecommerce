from django.core.management.base import BaseCommand
from ecommerce.models import ShippingMethod

class Command(BaseCommand):
    help = 'Populates the ShippingMethod model with initial data'

    def handle(self, *args, **kwargs):
        shipping_methods = [
            {'name': 'Standard Shipping', 'price': 310.00, 'description': 'Delivery within 5-7 days', 'is_active': True},
            {'name': 'Express Shipping', 'price': 500.00, 'description': 'Delivery within 2-3 days', 'is_active': True},
            {'name': 'Local Pickup', 'price': 0.00, 'description': 'Pick up at our store', 'is_active': True},
        ]

        for method in shipping_methods:
            ShippingMethod.objects.update_or_create(
                name=method['name'],
                defaults={
                    'price': method['price'],
                    'description': method['description'],
                    'is_active': method['is_active'],
                }
            )
            self.stdout.write(self.style.SUCCESS(f"Added/Updated shipping method: {method['name']}"))

        self.stdout.write(self.style.SUCCESS('Successfully populated shipping methods'))
        