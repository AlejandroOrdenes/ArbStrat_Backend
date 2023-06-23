from django.urls import path
from . import views

urlpatterns = [
    # path('sendEmailAlert/', views.sendAlertsEmails, name='sendEmailAlert'),
    path('updateEmailAlerts/', views.updateEmailAlerts, name='updateEmailAlerts'),
    path('updateDiscordAlerts/', views.updateDiscordAlerts, name='updateDiscordAlerts'),
    path('getUserAlerts/', views.getUserAlerts, name='getUserAlerts'),
    
]