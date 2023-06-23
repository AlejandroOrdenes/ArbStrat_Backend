from django.utils import timezone
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from .models import CloseTrade, Trade, Cointegrated_Pairs
from .views import simulateTrades, getAllTrades, closeTrade, saveCloseTrade, getClosedTradesByUser


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@email.com',
            password='testpass123'
        )

        self.cointegrated_pair = Cointegrated_Pairs.objects.create(
            Crypto1_ID='BTC',
            Crypto2_ID='ETH',
            Date_detection=timezone.now(),
            Spread=[0.1, 0.2, 0.3],  # este es un ejemplo, deberías utilizar valores reales
            z_score=[-1.2, -1.1, -0.9],  # este es un ejemplo, deberías utilizar valores reales
            hedge_ratio=0.5,
            half_life=0.7,
            last_price_1=50000.00,
            last_price_2=2500.00
        )

        self.trade = Trade.objects.create(
            user=self.user,
            idPair=self.cointegrated_pair,
            direction='long',
            coin1='BTC',
            coin2='ETH',
            price1=Decimal('50000.00'),
            price2=Decimal('2500.00'),
            amount1=Decimal('0.01'),
            amount2=Decimal('0.4'),
            zScore=Decimal('1.2'),
            spread=Decimal('25000.00'),
            hedgeRatio=Decimal('0.5')
        )

        self.close_trade = CloseTrade.objects.create(
            user=self.user,
            coin1='BTC',
            amount1=Decimal('0.01'),
            price1=Decimal('50000.00'),
            profit1=Decimal('500.00'),  # este es un ejemplo, deberías utilizar valores reales
            coin2='ETH',
            amount2=Decimal('0.4'),
            price2=Decimal('2500.00'),
            profit2=Decimal('1000.00')  # este es un ejemplo, deberías utilizar valores reales
        )

    def test_simulateTrades(self):
        view = simulateTrades
        data = {
            'idPair': self.cointegrated_pair.id,
            'direction': 'long',
            'coin1': 'BTC',
            'coin2': 'ETH',
            'price1': 50000.00,
            'price2': 2500.00,
            'amount1': 0.01,
            'amount2': 0.4,
            'zscore': 1.2,
            'spread': 25000.00,
            'hedgeRatio': 0.5
        }
        request = self.factory.post(reverse('simulate'), data=data, format='json')
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_getAllTrades(self):
        view = getAllTrades
        request = self.factory.get(reverse('getTrades'))
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_closeTrade(self):
        view = closeTrade
        data = {
            'id':1,
            'idPair': self.cointegrated_pair.id,
            'direction': 'long',
            'coin1': 'BTC',
            'coin2': 'ETH',
            'price1': 50000.00,
            'price2': 2500.00,
            'amount1': 0.01,
            'amount2': 0.4,
            'zscore': 1.2,
            'spread': 25000.00,
            'hedgeRatio': 0.5
        }
        request = self.factory.post(reverse('closeTrade'), data=data, format='json')
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_saveCloseTrade(self):
        view = saveCloseTrade
        data = {
            'user': str(self.user.id),
            'coin1': 'BTC',
            'amount1': Decimal('0.01'),
            'price1': Decimal('50000.00'),
            'profit1': Decimal('500.00'),
            'coin2': 'ETH',
            'amount2': Decimal('0.4'),
            'price2': Decimal('2500.00'),
            'profit2': Decimal('1000.00'),
        }
        request = self.factory.post(reverse('saveCloseTrade'), data=data, format='json')
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_getClosedTradesByUser(self):
        view = getClosedTradesByUser
        request = self.factory.get(reverse('getClosedTrades'))
        force_authenticate(request, user=self.user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)