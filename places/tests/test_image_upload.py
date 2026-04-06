from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from testing_utils import get_test_image, get_auth_client


def create_place_data(image=None):
    data = {
        'name': 'Test Place',
        'city': 'London',
        'country': 'UK',
        'description': 'A lovely spot.',
    }
    if image:
        data['image'] = image
    return data


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

class TestPlaceImageCreate(TestCase):
    # POST /api/places/

    def test_authenticated_user_can_create_place_with_image(self):
        client, user = get_auth_client()
        image = get_test_image()
        data = create_place_data(image=image)
        response = client.post('/api/places/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_created_place_image_field_is_populated(self):
        client, user = get_auth_client()
        image = get_test_image()
        data = create_place_data(image=image)
        response = client.post('/api/places/', data, format='multipart')
        self.assertTrue(response.data['image'])

    def test_unauthenticated_user_cannot_create_place_with_image(self):
        client = APIClient()
        image = get_test_image()
        data = create_place_data(image=image)
        response = client.post('/api/places/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_file_type_rejected(self):
        client, user = get_auth_client()
        bad_file = SimpleUploadedFile(
            'test.txt',
            b'this is not an image',
            content_type='text/plain',
        )
        data = create_place_data(image=bad_file)
        response = client.post('/api/places/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

class TestPlaceImageUpdate(TestCase):
    # PATCH /api/places/<id>/

    def test_owner_can_update_place_image(self):
        client, user = get_auth_client()
        data = create_place_data()
        create_response = client.post('/api/places/', data, format='multipart')
        place_id = create_response.data['id']
        new_image = get_test_image(name='updated.jpg')
        response = client.patch(
            f'/api/places/{place_id}/',
            {'image': new_image},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['image'])

    def test_non_owner_cannot_update_place_image(self):
        client_a, user_a = get_auth_client(username='alice', email='alice@example.com')
        data = create_place_data()
        create_response = client_a.post('/api/places/', data, format='multipart')
        place_id = create_response.data['id']
        client_b, user_b = get_auth_client(username='bob', email='bob@example.com')
        new_image = get_test_image(name='hack.jpg')
        response = client_b.patch(
            f'/api/places/{place_id}/',
            {'image': new_image},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)