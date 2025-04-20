from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fixes PostgreSQL sequences for all tables'

    def handle(self, *args, **kwargs):
        tables = ['ecommerce_order']
        for table in tables:
            sequence = f"{table}_id_seq"
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {table}")
                next_id = cursor.fetchone()[0]
                cursor.execute(f"ALTER SEQUENCE {sequence} RESTART WITH %s", [next_id])
                cursor.execute(f"SELECT last_value FROM {sequence}")
                new_value = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f"Set {sequence} to {new_value}"))