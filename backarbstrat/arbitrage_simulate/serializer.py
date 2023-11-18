from rest_framework import serializers
from .models import CloseTrade, Trade

class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = ['id', 'user', 'idPair', 'coin1', 'coin2', 'direction', 'price1', 'price2', 'amount1', 'amount2', 'zScore', 'spread', 'hedgeRatio']

class CloseTradeSerializer(serializers.ModelSerializer):
     class Meta:
        model = CloseTrade
        fields = ['id', 'user', 'coin1', 'coin2', 'amount1', 'amount2', 'price1', 'price2', 'profit1', 'profit2', 'close_timestamp']
