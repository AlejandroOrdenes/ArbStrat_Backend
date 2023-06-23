# admin.py

from django.contrib import admin
from cointegration_arbitrage.models import Cointegrated_Pairs

admin.site.register(Cointegrated_Pairs)
