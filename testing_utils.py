from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from PIL import Image


def get_test_image(name='test.jpg', size=(100, 100), fmt='JPEG'):
    buffer = BytesIO()
    image = Image.new('RGB', size, color='red')
    image.save(buffer, format=fmt)
    buffer.seek(0)
    return SimpleUploadedFile(
        name,
        buffer.read(),
        content_type=f'image/{fmt.lower()}',
    )


def get_auth_client(username='owner', email='owner@example.com', password='SecurePass123!'):
    client = APIClient()
    user = User.objects.create_user(username=username, email=email, password=password)
    response = client.post('/api/auth/token/', {
        'username': username,
        'password': password,
    }, format='json')
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return client, user