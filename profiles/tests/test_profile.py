from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status


def get_auth_client(username='owner', email='owner@example.com', password='SecurePass123!'):
    client = APIClient()
    user = User.objects.create_user(username=username, email=email, password=password)
    response = client.post('/api/auth/token/', {
        'username': username,
        'password': password,
    }, format='json')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return client, user


class TestRetrieveProfile(TestCase):
    # GET /api/profile/

    def test_authenticated_user_can_retrieve_profile(self):
        client, user = get_auth_client()
        response = client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('bio', response.data)
        self.assertIn('avatar', response.data)
        self.assertIn('location', response.data)

    def test_profile_contains_expected_fields(self):
        client, user = get_auth_client()
        response = client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {'id', 'user', 'bio', 'avatar', 'location'},
        )

    def test_unauthenticated_retrieve_returns_401(self):
        client = APIClient()
        response = client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUpdateProfile(TestCase):
    # PATCH /api/profile/

    def test_authenticated_user_can_update_bio(self):
        client, user = get_auth_client()
        response = client.patch('/api/profile/', {'bio': 'Hello world.'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bio'], 'Hello world.')

    def test_authenticated_user_can_update_location(self):
        client, user = get_auth_client()
        response = client.patch('/api/profile/', {'location': 'Paris'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['location'], 'Paris')

    def test_authenticated_user_can_update_avatar(self):
        client, user = get_auth_client()
        response = client.patch(
            '/api/profile/',
            {'avatar': 'https://res.cloudinary.com/demo/image/upload/avatar.jpg'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['avatar'],
            'https://res.cloudinary.com/demo/image/upload/avatar.jpg',
        )

    def test_unauthenticated_update_returns_401(self):
        client = APIClient()
        response = client.patch('/api/profile/', {'bio': 'Hacked.'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestProfileOwnerOnly(TestCase):
    # A user cannot read or update another user's profile via this endpoint

    def test_cannot_see_other_users_profile(self):
        client_a, user_a = get_auth_client(username='alice', email='alice@example.com')
        client_b, user_b = get_auth_client(username='bob', email='bob@example.com')
        # PATCH alice's profile so it has data
        client_a.patch('/api/profile/', {'bio': 'I am Alice.'}, format='json')
        # Bob retrieves /api/profile/ and should only see his own
        response = client_b.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['bio'], 'I am Alice.')

    def test_patch_only_updates_own_profile(self):
        client_a, user_a = get_auth_client(username='alice', email='alice@example.com')
        client_b, user_b = get_auth_client(username='bob', email='bob@example.com')
        # Bob tries to PATCH
        client_b.patch('/api/profile/', {'bio': 'Bob was here.'}, format='json')
        # Alice's profile should be unchanged
        response = client_a.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['bio'], 'Bob was here.')


class TestProfileValidation(TestCase):
    # Field validation for profile updates

    def test_bio_exceeds_500_chars_rejected(self):
        client, user = get_auth_client()
        response = client.patch('/api/profile/', {'bio': 'A' * 501}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('bio', response.data)

    def test_bio_at_500_chars_accepted(self):
        client, user = get_auth_client()
        response = client.patch('/api/profile/', {'bio': 'A' * 500}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_location_exceeds_255_chars_rejected(self):
        client, user = get_auth_client()
        response = client.patch('/api/profile/', {'location': 'B' * 256}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('location', response.data)

    def test_location_at_255_chars_accepted(self):
        client, user = get_auth_client()
        response = client.patch('/api/profile/', {'location': 'B' * 255}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_avatar_url_rejected(self):
        client, user = get_auth_client()
        response = client.patch('/api/profile/', {'avatar': 'not-a-url'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('avatar', response.data)

    def test_valid_avatar_url_accepted(self):
        client, user = get_auth_client()
        response = client.patch(
            '/api/profile/',
            {'avatar': 'https://example.com/photo.jpg'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)