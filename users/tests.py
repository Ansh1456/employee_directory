from django.test import TestCase
from django.urls import reverse
from users.models import User


class AuthTests(TestCase):
    def setUp(self):
        User.objects.create_user('testuser', password='correctpass', role='employee')

    def test_correct_login_redirects_to_dashboard(self):
        r = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'correctpass'})
        self.assertRedirects(r, reverse('dashboard'))

    def test_wrong_password_returns_form_error(self):
        r = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Incorrect password')

    def test_unauthenticated_redirects_to_login(self):
        r = self.client.get(reverse('directory'))
        self.assertRedirects(r, f"{reverse('login')}?next={reverse('directory')}")
