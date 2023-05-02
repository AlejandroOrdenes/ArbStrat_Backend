from django.db import models
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class Crypto(models.Model):
    Nombre = models.CharField(max_length=255)
    Simbolo = models.CharField(max_length=10)
    Rank_Mercado = models.IntegerField()
    Precio = models.DecimalField(max_digits=18, decimal_places=8)

    def __str__(self):
        return f"{self.Nombre} ({self.Simbolo})"


class Cointegrated_Pairs(models.Model):
    Crypto1_ID = models.CharField(max_length=255)
    Crypto2_ID = models.CharField(max_length=255)
    Date_detection = models.DateTimeField()
    Spread = ArrayField(models.FloatField())
    z_score = ArrayField(models.FloatField())
    hedge_ratio = models.FloatField()
    half_life = models.FloatField()
    last_price_1 = models.FloatField()
    last_price_2 = models.FloatField()

    def __str__(self):
        return f"{self.Crypto1_ID} - {self.Crypto2_ID}"
    

# Pares_Cointegrados

# ID_Par (PK)
# Crypto1_ID (FK - Crypto)
# Crypto2_ID (FK - Crypto)
# Date_detection
# Spread
# z-score
# hedge_ratio
# half_life

# Criptomonedas

# ID_Criptomoneda (PK)
# Nombre
# Símbolo
# Rank_Mercado

