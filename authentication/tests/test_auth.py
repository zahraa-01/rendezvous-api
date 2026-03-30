from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


class TestUserRegistration(TestCase):
    # Tests for POST /api/auth/register/

    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
        }

    # Happy path

    def test_register_with_valid_data(self):
        response = self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')

    def test_password_is_hashed(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        user = User.objects.get(username='testuser')
        self.assertNotEqual(user.password, 'SecurePass123!')
        self.assertTrue(user.check_password('SecurePass123!'))

    def test_response_contains_safe_fields_only(self):
        response = self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)
        self.assertNotIn('password', response.data)

    # Duplicate rejection

    def test_duplicate_username_rejected(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        response = self.client.post('/api/auth/register/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_rejected(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        data = {**self.valid_data, 'username': 'otheruser'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Missing required fields

    def test_missing_username_rejected(self):
        data = {'email': 'test@example.com', 'password': 'SecurePass123!'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_missing_email_rejected(self):
        data = {'username': 'testuser', 'password': 'SecurePass123!'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_missing_password_rejected(self):
        data = {'username': 'testuser', 'email': 'test@example.com'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    # Invalid email

    def test_invalid_email_rejected(self):
        data = {**self.valid_data, 'email': 'not-an-email'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    # Password strength validation

    def test_too_short_password_rejected(self):
        data = {**self.valid_data, 'password': 'Ab1!'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_common_password_rejected(self):
        data = {**self.valid_data, 'password': 'password123'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_numeric_only_password_rejected(self):
        data = {**self.valid_data, 'password': '4839274817263'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_password_similar_to_username_rejected(self):
        data = {**self.valid_data, 'password': 'testuser1'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    # Case-insensitive email uniqueness

    def test_duplicate_email_different_case_rejected(self):
        self.client.post('/api/auth/register/', self.valid_data, format='json')
        data = {**self.valid_data, 'username': 'otheruser', 'email': 'Test@Example.COM'}
        response = self.client.post('/api/auth/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestJWTLogin(TestCase):
    # Tests for POST /api/auth/token/

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
        )

    def test_valid_credentials_return_tokens(self):
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'SecurePass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_invalid_password_returns_401(self):
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'WrongPassword!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_user_returns_401(self):
        response = self.client.post('/api/auth/token/', {
            'username': 'nobody',
            'password': 'SecurePass123!',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAuthenticatedAccess(TestCase):
    # Tests for GET /api/auth/user/ (protected endpoint)

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
        )
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'SecurePass123!',
        }, format='json')
        self.access_token = response.data.get('access', '')

    def test_authenticated_request_succeeds(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get('/api/auth/user/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_unauthenticated_request_rejected(self):
        response = self.client.get('/api/auth/user/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
