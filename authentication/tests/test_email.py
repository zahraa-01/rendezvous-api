from django.test import TestCase, override_settings
from django.core import mail
from rest_framework.test import APIClient
from rest_framework import status


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TestWelcomeEmail(TestCase):
    # Welcome email sent on successful registration

    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
        }

    def test_email_sent_on_successful_registration(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertEqual(len(mail.outbox), 1)

    def test_email_sent_to_correct_address(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertEqual(mail.outbox[0].to, ['newuser@example.com'])

    def test_email_subject_contains_welcome(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertIn('Welcome', mail.outbox[0].subject)

    def test_email_body_contains_username(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertIn('newuser', mail.outbox[0].body)

    def test_email_has_html_alternative(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        msg = mail.outbox[0]
        html_parts = [alt[0] for alt in msg.alternatives if alt[1] == 'text/html']
        self.assertEqual(len(html_parts), 1)

    def test_html_body_contains_username(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        msg = mail.outbox[0]
        html = [alt[0] for alt in msg.alternatives if alt[1] == 'text/html'][0]
        self.assertIn('newuser', html)

    def test_no_email_sent_on_failed_registration(self):
        bad_data = {
            'username': '',
            'email': 'bad@example.com',
            'password': 'SecurePass123!',
        }
        self.client.post('/api/auth/register/', bad_data, format='json')
        self.assertEqual(len(mail.outbox), 0)

    def test_no_email_sent_on_duplicate_username(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        mail.outbox.clear()
        response = self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_registration_still_succeeds(self):
        response = self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)