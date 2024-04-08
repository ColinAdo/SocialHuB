from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from core.models import Post, EmailVerification

class TestHomeViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='user', password='password')
        self.home_url = reverse('home')

    def test_home_view_with_authenticated_user(self):
        self.client.login(username=self.user.username, password=self.user.password)
        EmailVerification.objects.filter(user=self.user, is_verified=True).exists()
        response = self.client.get(self.home_url)

        self.assertEquals(response.status_code, 302)
