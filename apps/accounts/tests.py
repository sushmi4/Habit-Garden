from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            password='testpass123',
        )

    def login_post(self, next_url=None):
        url = reverse('login')
        if next_url is not None:
            url = f'{url}?next={next_url}'
        return self.client.post(url, {
            'username': 'tester',
            'password': 'testpass123',
        })

    def test_login_redirects_to_safe_next(self):
        response = self.login_post('/habits/')
        self.assertRedirects(response, '/habits/', fetch_redirect_response=False)

    def test_login_rejects_external_next(self):
        response = self.login_post('https://evil.example.com')
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_login_rejects_javascript_next(self):
        response = self.login_post('javascript:alert(1)')
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_login_rejects_protocol_relative_next(self):
        response = self.login_post('//evil.example.com')
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_logout_requires_post(self):
        self.client.login(username='tester', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertTrue(self.user.is_authenticated)

    def test_logout_post_logs_out(self):
        self.client.login(username='tester', password='testpass123')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertFalse('_auth_user_id' in self.client.session)
