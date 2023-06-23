import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from alerts.models import UserAlerts

class AlertTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',  # Agrega esta línea
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.alerts = UserAlerts.objects.create(user=self.user, email_alerts=False, discord_alerts=False)


    def test_update_email_alerts(self):
        """Test updating email alerts"""
        url = reverse('updateEmailAlerts')
        payload = {'emailAlert': True}
        response = self.client.post(url, payload, format='json')

        self.alerts.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.alerts.email_alerts, True)

    def test_update_discord_alerts(self):
        """Test updating discord alerts"""
        url = reverse('updateDiscordAlerts')
        payload = {'discordAlert': True}
        response = self.client.post(url, payload, format='json')

        self.alerts.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.alerts.discord_alerts, True)

    def test_get_user_alerts(self):
        """Test getting user alerts"""
        url = reverse('getUserAlerts')
        response = self.client.get(url, format='json')

        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data, {'emailAlert': self.alerts.email_alerts, 'discordAlert': self.alerts.discord_alerts})


