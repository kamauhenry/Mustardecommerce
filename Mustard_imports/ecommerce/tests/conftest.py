import os
import django
import pytest

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Mustard_imports.settings")

# Initialize Django before any tests are run
django.setup()

@pytest.fixture(scope="session")
def django_db_setup():
    """Set up Django database configuration."""
    pass