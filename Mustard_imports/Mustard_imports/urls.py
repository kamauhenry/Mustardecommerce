# Mustard_imports/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls')),  # Djoser base URLs (includes /users/ for registration)
    path('api/auth/', include('djoser.urls.authtoken')),  # Token-based auth (includes /token/login/)
    path('api/', include('ecommerce.api.urls')),  # Custom API endpoints
    path('', TemplateView.as_view(template_name='index.html'), name='frontend/vue-project'),  # Vue app
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)