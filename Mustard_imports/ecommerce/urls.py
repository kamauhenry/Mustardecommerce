from django.urls import path
from .views import VueAppView

urlpatterns = [
    path('', VueAppView.as_view(), name='vue-app'),
]