from django.db import models
from users.models import CustomUser

class MyModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    direction = models.CharField(max_length=255)
    price1 = models.DecimalField(max_digits=10, decimal_places=2)
    price2 = models.DecimalField(max_digits=10, decimal_places=2)
    amount1 = models.DecimalField(max_digits=10, decimal_places=2)
    amount2 = models.DecimalField(max_digits=10, decimal_places=2)
    zScore = models.DecimalField(max_digits=10, decimal_places=2)
    spread = models.DecimalField(max_digits=10, decimal_places=2)
    hedgeRatio = models.DecimalField(max_digits=10, decimal_places=2)
    buyPrice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'MyModel - ID: {self.id} - User: {self.user.email}'

