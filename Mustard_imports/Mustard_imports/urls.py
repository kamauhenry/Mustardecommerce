# Mustard_imports/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve
import logging

logger = logging.getLogger(__name__)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ecommerce.api.urls')),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
    path('ecommerce', include('ecommerce.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    # Catch-all route for Vue.js frontend
    re_path(r'^(?!api/).*$', TemplateView.as_view(template_name='index.html')),
]

# Serve static and media files in development
if settings.DEBUG:
    logger.info(f"Serving media files from {settings.MEDIA_ROOT} at {settings.MEDIA_URL}")
    # Use a custom view to serve media files with logging
    def serve_media(request, path):
        logger.info(f"Attempting to serve media file: {path}")
        response = serve(request, path, document_root=settings.MEDIA_ROOT)
        logger.info(f"Served media file: {path}, Status: {response.status_code}")
        return response
    
    # Wrap path() in a list to make it iterable
    urlpatterns += [path('media/<path:path>', serve_media, name='serve_media')]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)