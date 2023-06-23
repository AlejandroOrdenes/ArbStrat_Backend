from django.contrib.postgres.fields import ArrayField
from rest_framework import serializers
from .models import Crypto, Cointegrated_Pairs

class CointegratedPairsSerializer(serializers.ModelSerializer):
    Spread = serializers.ListField(child=serializers.FloatField())
    z_score = serializers.ListField(child=serializers.FloatField())

    class Meta:
        model = Cointegrated_Pairs
        fields = [ 'id', 'Crypto1_ID', 'Crypto2_ID', 'Date_detection', 'Spread', 'z_score', 'hedge_ratio', 'half_life', 'last_price_1', 'last_price_2']
