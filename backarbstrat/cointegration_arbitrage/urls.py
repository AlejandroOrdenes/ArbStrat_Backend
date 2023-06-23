from . import views
from django.urls import path

urlpatterns = [
    path('cryptos/', views.getCryptos, name='cryptos'),
    path('cointegration/', views.cointegration_view, name='cointegration'),
    path('cointegratedPairs/', views.getAllCointegratedPairs, name='cointegratedPairs'),
    path('cointegratedPair/<int:idPair>', views.getCointegratedPairById, name='cointegratedPairId'),
    path('cryptoPrices/', views.getCryptoPrices, name='cryptoPrices'),
    path('price/<str:market>/', views.getPrice, name='price'),
    path('currentPrices/<str:idPair>', views.getCurrentPrices, name='currentPrices')
]
