from django.test import TestCase, RequestFactory
from django.urls import reverse
from .models import Cointegrated_Pairs
from .views import getCryptos, cointegration_view, getAllCointegratedPairs, getCointegratedPairById, getCryptoPrices, getPrice, getCurrentPrices


class TestGetCryptos(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_getCryptos(self):
        url = reverse('cryptos')  
        request = self.factory.get(url)
        response = getCryptos(request)
        self.assertEqual(response.status_code, 200)


class TestCointegrationView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cointegration_view(self):
        url = reverse('cointegration')  
        request = self.factory.get(url)
        response = cointegration_view(request)
        self.assertEqual(response.status_code, 200)


class TestGetAllCointegratedPairs(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_getAllCointegratedPairs(self):
        url = reverse('cointegratedPairs')
        request = self.factory.get(url)
        response = getAllCointegratedPairs(request)
        self.assertEqual(response.status_code, 200)


class TestGetCointegratedPairById(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.pair = Cointegrated_Pairs.objects.create(Crypto1_ID="test1", Crypto2_ID="test2", Date_detection="2023-06-14T00:00Z", Spread=[1.0], z_score=[1.0], hedge_ratio=1.0, half_life=1.0, last_price_1=1.0, last_price_2=1.0)

    def test_getCointegratedPairById(self):
        url = reverse('cointegratedPairId', args=[self.pair.id])
        request = self.factory.get(url)
        response = getCointegratedPairById(request, self.pair.id)
        self.assertEqual(response.status_code, 200)


class TestGetCryptoPrices(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_getCryptoPrices(self):
        url = reverse('cryptoPrices')  
        request = self.factory.get(url)
        response = getCryptoPrices(request)
        self.assertEqual(response.status_code, 200)


class TestGetPrice(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
    def test_getPrice(self):
        url = reverse('price', args=['market_name'])
        request = self.factory.get(url)
        response = getPrice(request, 'BTC-USD')
        self.assertEqual(response.status_code, 200)


class TestGetCurrentPrices(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.pair = Cointegrated_Pairs.objects.create(Crypto1_ID="test1", Crypto2_ID="test2", Date_detection="2023-06-14T00:00Z", Spread=[1.0], z_score=[1.0], hedge_ratio=1.0, half_life=1.0, last_price_1=1.0, last_price_2=1.0)

    def test_getCurrentPrices(self):
        url = reverse('currentPrices', args=[str(self.pair.id)])
        request = self.factory.get(url)
        response = getCurrentPrices(request, str(self.pair.id))
        self.assertEqual(response.status_code, 200)
