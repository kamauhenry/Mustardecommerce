from django.core.management.base import BaseCommand
from ...models import Product

class Command(BaseCommand):
    help = 'Updates the picture field for all products to blank'

    def handle(self, *args, **options):
        # Get all products
        products = Product.objects.all()
        count = 0
        
        # Update each product's picture field to empty/blank
        for product in products:
            product.picture = ''  # Set to empty string
            product.save()
            count += 1
            self.stdout.write(self.style.SUCCESS(f"Updated picture for product: {product.name}"))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully cleared images for {count} products'))