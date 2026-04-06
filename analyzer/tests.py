from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import AnalysisRecord
from django.urls import reverse

class InsightXBasicTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client = Client()

    def test_landing_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login_redirects(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('analyze'))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access(self):
        response = self.client.get(reverse('history'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)

class InsightXAPITest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password123')
        self.client = Client()
        self.client.login(username='apiuser', password='password123')

    def test_history_api(self):
        AnalysisRecord.objects.create(
            user=self.user,
            job_description_text='Test JD',
            resume_text='Test Resume',
            overall_score=85.0,
            status='COMPLETED'
        )
        response = self.client.get(reverse('api_history'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
