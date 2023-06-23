# admin.py

from django.contrib import admin
from alerts.models import UserAlerts

admin.site.register(UserAlerts)
