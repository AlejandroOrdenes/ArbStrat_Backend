from . import views
from django.urls import path

urlpatterns = [
    path('csrf/', views.csrf, name='get_csrf_token'),
    path('simulateTrades/', views.simulateTrades, name='simulate'),
]