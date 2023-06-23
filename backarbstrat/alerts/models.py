from django.db import models

from users.models import CustomUser

# Create your models here.
class UserAlerts(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    email_alerts = models.BooleanField(default=True)
    discord_alerts = models.BooleanField(default=False)