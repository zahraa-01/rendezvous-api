from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from places.models import Place


def get_auth_client(username='owner', email='owner@example.com', password='SecurePass123!'):
    client = APIClient()
    User.objects.create_user(username=username, email=email, password=password)
    response = client.post('/api/auth/token/', {
        'username': username,
        'password': password,
    }, format='json')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return client


class TestAuthenticatedCreateOnly(TestCase):
    # POST /api/places/ requires authentication

    def setUp(self):
        self.valid_data = {
            'name': 'Café Lumière',
            'city': 'Paris',
            'country': 'France',
            'description': 'A cozy café near the Seine.',
        }

    def test_unauthenticated_create_returns_401(self):
        client = APIClient()
        response = client.post('/api/places/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_create_succeeds(self):
        client = get_auth_client()
        response = client.post('/api/places/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Place.objects.count(), 1)


class TestPlaceOwnership(TestCase):
    # Created places should be associated with the authenticated user

    def setUp(self):
        self.client = get_auth_client()
        self.valid_data = {
            'name': 'Café Lumière',
            'city': 'Paris',
            'country': 'France',
            'description': 'A cozy café near the Seine.',
        }

    def test_created_place_has_owner(self):
        response = self.client.post('/api/places/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        place = Place.objects.first()
        owner = User.objects.get(username='owner')
        self.assertEqual(place.owner, owner)

    def test_owner_field_is_read_only_if_present(self):
        response = self.client.post('/api/places/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        if 'owner' in response.data:
            place = Place.objects.first()
            owner = User.objects.get(username='owner')
            self.assertEqual(place.owner, owner)

    def test_cannot_spoof_owner_field(self):
        other_user = User.objects.create_user(
            username='victim', email='victim@example.com', password='SecurePass123!',
        )
        data = {**self.valid_data, 'owner': other_user.id}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        place = Place.objects.first()
        owner = User.objects.get(username='owner')
        self.assertEqual(place.owner, owner)


class TestOwnerOnlyUpdate(TestCase):
    # Only the owner can update their Place

    def setUp(self):
        self.owner_client = get_auth_client(
            username='owner', email='owner@example.com',
        )
        self.other_client = get_auth_client(
            username='other', email='other@example.com',
        )
        response = self.owner_client.post('/api/places/', {
            'name': 'Café Lumière',
            'city': 'Paris',
            'country': 'France',
            'description': 'A cozy café near the Seine.',
        }, format='json')
        self.place_id = response.data['id']

    def test_owner_can_put(self):
        response = self.owner_client.put(f'/api/places/{self.place_id}/', {
            'name': 'Updated Café',
            'city': 'Lyon',
            'country': 'France',
            'description': 'Now in Lyon.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_patch(self):
        response = self.owner_client.patch(
            f'/api/places/{self.place_id}/', {'name': 'New Name'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_cannot_put(self):
        response = self.other_client.put(f'/api/places/{self.place_id}/', {
            'name': 'Hijacked',
            'city': 'Nowhere',
            'country': 'Nowhere',
            'description': 'Hijacked.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_other_user_cannot_patch(self):
        response = self.other_client.patch(
            f'/api/places/{self.place_id}/', {'name': 'Hijacked'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestOwnerOnlyDelete(TestCase):
    # Only the owner can delete their Place

    def setUp(self):
        self.owner_client = get_auth_client(
            username='owner', email='owner@example.com',
        )
        self.other_client = get_auth_client(
            username='other', email='other@example.com',
        )
        response = self.owner_client.post('/api/places/', {
            'name': 'Café Lumière',
            'city': 'Paris',
            'country': 'France',
            'description': 'A cozy café near the Seine.',
        }, format='json')
        self.place_id = response.data['id']

    def test_owner_can_delete(self):
        response = self.owner_client.delete(f'/api/places/{self.place_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete(self):
        response = self.other_client.delete(f'/api/places/{self.place_id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestUnauthenticatedWriteBlocked(TestCase):
    # PUT, PATCH, DELETE all require authentication

    def setUp(self):
        self.client = APIClient()
        self.owner_client = get_auth_client()
        response = self.owner_client.post('/api/places/', {
            'name': 'Café Lumière',
            'city': 'Paris',
            'country': 'France',
            'description': 'A cozy café near the Seine.',
        }, format='json')
        self.place_id = response.data['id']

    def test_unauthenticated_put_returns_401(self):
        response = self.client.put(f'/api/places/{self.place_id}/', {
            'name': 'Hijacked',
            'city': 'Nowhere',
            'country': 'Nowhere',
            'description': 'Hijacked.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_patch_returns_401(self):
        response = self.client.patch(
            f'/api/places/{self.place_id}/', {'name': 'Hijacked'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_delete_returns_401(self):
        response = self.client.delete(f'/api/places/{self.place_id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestReadAccessUnchanged(TestCase):
    # GET list and retrieve remain publicly accessible

    def setUp(self):
        self.client = APIClient()
        self.owner_client = get_auth_client()
        response = self.owner_client.post('/api/places/', {
            'name': 'Café Lumière',
            'city': 'Paris',
            'country': 'France',
            'description': 'A cozy café near the Seine.',
        }, format='json')
        self.place_id = response.data['id']

    def test_unauthenticated_list_succeeds(self):
        response = self.client.get('/api/places/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_retrieve_succeeds(self):
        response = self.client.get(f'/api/places/{self.place_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestNonExistentResourcePermissions(TestCase):
    # Non-existent places still return 404, not permission errors

    def setUp(self):
        self.auth_client = get_auth_client()

    def test_patch_nonexistent_returns_404(self):
        response = self.auth_client.patch(
            '/api/places/9999/', {'name': 'Ghost'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexistent_returns_404(self):
        response = self.auth_client.delete('/api/places/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
