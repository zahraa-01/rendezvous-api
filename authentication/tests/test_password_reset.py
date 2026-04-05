from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APIClient
from rest_framework import status


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TestPasswordResetRequest(TestCase):
    # POST /api/auth/password-reset/

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='OldSecurePass123!',
        )

    def test_existing_email_returns_200_and_sends_email(self):
        response = self.client.post(
            '/api/auth/password-reset/',
            {'email': 'testuser@example.com'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_nonexistent_email_returns_200_and_sends_no_email(self):
        response = self.client.post(
            '/api/auth/password-reset/',
            {'email': 'nobody@example.com'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)

    def test_email_subject_contains_password_reset(self):
        self.client.post(
            '/api/auth/password-reset/',
            {'email': 'testuser@example.com'},
            format='json',
        )
        self.assertIn('Password Reset', mail.outbox[0].subject)

    def test_email_sent_to_correct_recipient(self):
        self.client.post(
            '/api/auth/password-reset/',
            {'email': 'testuser@example.com'},
            format='json',
        )
        self.assertEqual(mail.outbox[0].to, ['testuser@example.com'])

    def test_email_body_contains_reset_link_with_uid_and_token(self):
        self.client.post(
            '/api/auth/password-reset/',
            {'email': 'testuser@example.com'},
            format='json',
        )
        body = mail.outbox[0].body
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.assertIn(uid, body)
        self.assertIn('/reset-password/', body)

    def test_missing_email_returns_400(self):
        response = self.client.post(
            '/api/auth/password-reset/',
            {},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TestPasswordResetConfirm(TestCase):
    # POST /api/auth/password-reset-confirm/

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='OldSecurePass123!',
        )
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

    def test_valid_reset_returns_200(self):
        response = self.client.post(
            '/api/auth/password-reset-confirm/',
            {'uid': self.uid, 'token': self.token, 'new_password': 'NewSecurePass456!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_old_password_no_longer_works_after_reset(self):
        self.client.post(
            '/api/auth/password-reset-confirm/',
            {'uid': self.uid, 'token': self.token, 'new_password': 'NewSecurePass456!'},
            format='json',
        )
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'OldSecurePass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_new_password_works_after_reset(self):
        self.client.post(
            '/api/auth/password-reset-confirm/',
            {'uid': self.uid, 'token': self.token, 'new_password': 'NewSecurePass456!'},
            format='json',
        )
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'NewSecurePass456!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_invalid_uid_returns_400(self):
        response = self.client.post(
            '/api/auth/password-reset-confirm/',
            {'uid': 'invaliduid', 'token': self.token, 'new_password': 'NewSecurePass456!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_token_returns_400(self):
        response = self.client.post(
            '/api/auth/password-reset-confirm/',
            {'uid': self.uid, 'token': 'invalid-token', 'new_password': 'NewSecurePass456!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_weak_password_returns_400(self):
        response = self.client.post(
            '/api/auth/password-reset-confirm/',
            {'uid': self.uid, 'token': self.token, 'new_password': '123'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)