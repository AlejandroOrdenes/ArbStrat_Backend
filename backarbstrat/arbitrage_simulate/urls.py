from . import views
from django.urls import path

urlpatterns = [
    path('csrf/', views.csrf, name='get_csrf_token'),
    path('simulateTrades/', views.simulateTrades, name='simulate'),
    path('getTrades/', views.getAllTrades, name='getTrades'),
    path('closeTrade/', views.closeTrade, name='closeTrade'),
    path('saveCloseTrade/', views.saveCloseTrade, name='saveCloseTrade'),
    path('getClosedTrades/', views.getClosedTradesByUser, name='getClosedTrades'),
]


