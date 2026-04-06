from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from testing_utils import get_test_image, get_auth_client


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.InMemoryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})

class TestProfileAvatarUpload(TestCase):
    # PATCH /api/profile/

    def test_authenticated_user_can_upload_avatar(self):
        client, user = get_auth_client()
        image = get_test_image()
        response = client.patch(
            '/api/profile/',
            {'avatar': image},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_uploaded_avatar_field_is_populated(self):
        client, user = get_auth_client()
        image = get_test_image()
        response = client.patch(
            '/api/profile/',
            {'avatar': image},
            format='multipart',
        )
        self.assertTrue(response.data['avatar'])

    def test_unauthenticated_user_cannot_upload_avatar(self):
        client = APIClient()
        image = get_test_image()
        response = client.patch(
            '/api/profile/',
            {'avatar': image},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_file_type_rejected(self):
        client, user = get_auth_client()
        bad_file = SimpleUploadedFile(
            'test.txt',
            b'this is not an image',
            content_type='text/plain',
        )
        response = client.patch(
            '/api/profile/',
            {'avatar': bad_file},
            format='multipart',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)