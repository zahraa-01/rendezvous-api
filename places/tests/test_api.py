from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from places.models import Place


class TestCreatePlace(TestCase):
    # Tests for POST /api/places/

    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            'name': 'Café Lumière',
            'city': 'Paris',
            'country': 'France',
            'description': 'A cozy café near the Seine.',
        }

    # Happy path

    def test_create_place_with_valid_data(self):
        response = self.client.post('/api/places/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Place.objects.count(), 1)
        self.assertEqual(Place.objects.first().name, 'Café Lumière')

    def test_create_place_returns_all_fields(self):
        response = self.client.post('/api/places/', self.valid_data, format='json')
        self.assertEqual(
            set(response.data.keys()),
            {'id', 'name', 'city', 'country', 'description', 'image', 'created_at'},
        )

    def test_create_place_with_valid_image_url(self):
        data = {**self.valid_data, 'image': 'https://res.cloudinary.com/demo/image/upload/sample.jpg'}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Place.objects.first().image, 'https://res.cloudinary.com/demo/image/upload/sample.jpg')

    def test_create_place_image_defaults_to_empty(self):
        response = self.client.post('/api/places/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['image'], '')

    # Missing required fields

    def test_create_place_missing_name(self):
        data = {**self.valid_data, 'name': ''}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_place_missing_city(self):
        data = {**self.valid_data, 'city': ''}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('city', response.data)

    def test_create_place_missing_country(self):
        data = {**self.valid_data, 'country': ''}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('country', response.data)

    def test_create_place_omitting_name_key(self):
        data = {**self.valid_data}
        del data['name']
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    # Whitespace-only fields

    def test_create_place_whitespace_only_name(self):
        data = {**self.valid_data, 'name': '   '}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_place_whitespace_only_city(self):
        data = {**self.valid_data, 'city': '   '}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('city', response.data)

    def test_create_place_whitespace_only_country(self):
        data = {**self.valid_data, 'country': '   '}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('country', response.data)

    # Invalid image URL

    def test_create_place_invalid_image_url(self):
        data = {**self.valid_data, 'image': 'not-a-url'}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)

    def test_create_place_image_missing_scheme(self):
        data = {**self.valid_data, 'image': 'www.example.com/photo.jpg'}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)

    # Field length constraints

    def test_create_place_name_exceeds_max_length(self):
        data = {**self.valid_data, 'name': 'A' * 256}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_place_city_exceeds_max_length(self):
        data = {**self.valid_data, 'city': 'B' * 256}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('city', response.data)

    # Extra / unexpected fields

    def test_create_place_ignores_extra_fields(self):
        data = {**self.valid_data, 'rating': 5, 'secret': 'hack'}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('rating', response.data)
        self.assertNotIn('secret', response.data)

    # Read-only field protection

    def test_create_place_cannot_set_id(self):
        data = {**self.valid_data, 'id': 9999}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['id'], 9999)

    def test_create_place_cannot_set_created_at(self):
        data = {**self.valid_data, 'created_at': '2000-01-01T00:00:00Z'}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['created_at'], '2000-01-01T00:00:00Z')


class TestListPlaces(TestCase):
    # Tests for GET /api/places/

    def setUp(self):
        self.client = APIClient()
        self.place_a = Place.objects.create(
            name='Café Lumière', city='Paris', country='France', description='A café.',
        )
        self.place_b = Place.objects.create(
            name='Hyde Park', city='London', country='UK', description='A park.',
        )

    def test_list_returns_all_places(self):
        response = self.client.get('/api/places/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_contains_expected_fields(self):
        response = self.client.get('/api/places/')
        place = response.data[0]
        self.assertEqual(
            set(place.keys()),
            {'id', 'name', 'city', 'country', 'description', 'image', 'created_at'},
        )

    def test_list_returns_newest_first(self):
        response = self.client.get('/api/places/')
        self.assertEqual(response.data[0]['name'], 'Hyde Park')
        self.assertEqual(response.data[1]['name'], 'Café Lumière')

    def test_list_empty_database(self):
        Place.objects.all().delete()
        response = self.client.get('/api/places/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class TestRetrievePlace(TestCase):
    # Tests for GET /api/places/<id>/

    def setUp(self):
        self.client = APIClient()
        self.place = Place.objects.create(
            name='Café Lumière',
            city='Paris',
            country='France',
            description='A cozy café near the Seine.',
        )

    def test_retrieve_existing_place(self):
        response = self.client.get(f'/api/places/{self.place.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Café Lumière')
        self.assertEqual(response.data['city'], 'Paris')

    def test_retrieve_returns_all_fields(self):
        response = self.client.get(f'/api/places/{self.place.id}/')
        self.assertEqual(
            set(response.data.keys()),
            {'id', 'name', 'city', 'country', 'description', 'image', 'created_at'},
        )

    def test_retrieve_nonexistent_place_returns_404(self):
        response = self.client.get('/api/places/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
