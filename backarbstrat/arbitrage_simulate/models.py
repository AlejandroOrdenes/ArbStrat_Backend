from django.utils import timezone
from django.db import models
from cointegration_arbitrage.models import Cointegrated_Pairs
from users.models import CustomUser

class Trade(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    idPair = models.ForeignKey(Cointegrated_Pairs, on_delete=models.CASCADE)
    direction = models.CharField(max_length=255)
    coin1 = models.CharField(max_length=255)
    coin2 = models.CharField(max_length=255)
    price1 = models.DecimalField(max_digits=10, decimal_places=2)
    price2 = models.DecimalField(max_digits=10, decimal_places=2)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2)
    amount2 = models.DecimalField(max_digits=10, decimal_places=2)
    zScore = models.DecimalField(max_digits=10, decimal_places=2)
    spread = models.DecimalField(max_digits=10, decimal_places=2)
    hedgeRatio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'MyModel - ID: {self.id} - User: {self.user.email}'

class CloseTrade(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coin1 = models.CharField(max_length=100)
    amount1 = models.DecimalField(max_digits=50, decimal_places=16)
    price1 = models.DecimalField(max_digits=50, decimal_places=16)
    profit1 = models.DecimalField(max_digits=50, decimal_places=16)
    coin2 = models.CharField(max_length=100)
    amount2 = models.DecimalField(max_digits=50, decimal_places=16)
    price2 = models.DecimalField(max_digits=50, decimal_places=16)
    profit2 = models.DecimalField(max_digits=50, decimal_places=16)
    close_timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Trade: {self.coin1} - {self.coin2}"