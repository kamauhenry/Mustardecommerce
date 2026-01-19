"""Test settings for running tests with SQLite."""
from .settings import *

# Override database to use SQLite for tests
import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(os.path.dirname(__file__), '..', 'test_db.sqlite3'),
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

# MIGRATION_MODULES = DisableMigrations()

# Disable password hashers for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Simplify logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

# Disable debug mode for tests
DEBUG = False

# Disable SSL redirects for tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Allow testserver for API client tests
ALLOWED_HOSTS = ['*']

# Disable email sending during tests
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
