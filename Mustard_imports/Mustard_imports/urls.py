from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
import logging

logger = logging.getLogger(__name__)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ecommerce.api.urls')),  # API routes
    path('api/auth/', include('djoser.urls')),  # Djoser auth
    path('api/auth/', include('djoser.urls.authtoken')),
    path('ecommerce/', include('ecommerce.urls')),  # Ecommerce routes
]

# Serve static and media files in development
if settings.DEBUG:
    logger.info(f"Serving media files from {settings.MEDIA_ROOT} at {settings.MEDIA_URL}")
    logger.info(f"Serving static files from {settings.STATIC_ROOT} at {settings.STATIC_URL}")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)