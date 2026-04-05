from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from places.models import Place


class TestCreatePlace(TestCase):
    # Tests for POST /api/places/

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.client.force_authenticate(user=self.user)
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
            {'id', 'owner', 'name', 'city', 'country', 'description', 'image', 'created_at'},
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
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.place_a = Place.objects.create(
            name='Café Lumière', city='Paris', country='France', description='A café.',
            owner=self.user,
        )
        self.place_b = Place.objects.create(
            name='Hyde Park', city='London', country='UK', description='A park.',
            owner=self.user,
        )

    def test_list_returns_all_places(self):
        response = self.client.get('/api/places/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_list_contains_expected_fields(self):
        response = self.client.get('/api/places/')
        place = response.data['results'][0]
        self.assertEqual(
            set(place.keys()),
            {'id', 'owner', 'name', 'city', 'country', 'description', 'image', 'created_at'},
        )

    def test_list_returns_newest_first(self):
        response = self.client.get('/api/places/')
        self.assertEqual(response.data['results'][0]['name'], 'Hyde Park')
        self.assertEqual(response.data['results'][1]['name'], 'Café Lumière')

    def test_list_empty_database(self):
        Place.objects.all().delete()
        response = self.client.get('/api/places/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class TestRetrievePlace(TestCase):
    # Tests for GET /api/places/<id>/

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.place = Place.objects.create(
            name='Café Lumière',
            city='Paris',
            country='France',
            description='A cozy café near the Seine.',
            owner=self.user,
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
            {'id', 'owner', 'name', 'city', 'country', 'description', 'image', 'created_at'},
        )

    def test_retrieve_nonexistent_place_returns_404(self):
        response = self.client.get('/api/places/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestPaginatePlaces(TestCase):
    # Tests for paginated GET /api/places/

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        for i in range(15):
            Place.objects.create(
                name=f'Place {i}', city='City', country='Country', description='Desc',
                owner=self.user,
            )

    def test_list_is_paginated(self):
        response = self.client.get('/api/places/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 15)

    def test_page_size_is_10(self):
        response = self.client.get('/api/places/')
        self.assertEqual(len(response.data['results']), 10)

    def test_second_page_returns_remaining(self):
        response = self.client.get('/api/places/?page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_pagination_has_next_link(self):
        response = self.client.get('/api/places/')
        self.assertIsNotNone(response.data['next'])

    def test_pagination_first_page_has_no_previous(self):
        response = self.client.get('/api/places/')
        self.assertIsNone(response.data['previous'])

    def test_invalid_page_returns_404(self):
        response = self.client.get('/api/places/?page=999')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestUpdatePlace(TestCase):
    # Tests for PUT and PATCH /api/places/<id>/

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.client.force_authenticate(user=self.user)
        self.place = Place.objects.create(
            name='Café Lumière',
            city='Paris',
            country='France',
            description='A cozy café near the Seine.',
            owner=self.user,
        )
        self.valid_data = {
            'name': 'Café Lumière Updated',
            'city': 'Lyon',
            'country': 'France',
            'description': 'Now in Lyon.',
        }

    # PUT (full update)

    def test_put_with_valid_data(self):
        response = self.client.put(
            f'/api/places/{self.place.id}/', self.valid_data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.place.refresh_from_db()
        self.assertEqual(self.place.name, 'Café Lumière Updated')
        self.assertEqual(self.place.city, 'Lyon')

    def test_put_missing_required_field_fails(self):
        data = {**self.valid_data}
        del data['name']
        response = self.client.put(
            f'/api/places/{self.place.id}/', data, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_put_nonexistent_place_returns_404(self):
        response = self.client.put('/api/places/9999/', self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # PATCH (partial update)

    def test_patch_single_field(self):
        response = self.client.patch(
            f'/api/places/{self.place.id}/', {'name': 'New Name'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.place.refresh_from_db()
        self.assertEqual(self.place.name, 'New Name')
        self.assertEqual(self.place.city, 'Paris')

    def test_patch_blank_name_fails(self):
        response = self.client.patch(
            f'/api/places/{self.place.id}/', {'name': ''}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_patch_whitespace_only_name_fails(self):
        response = self.client.patch(
            f'/api/places/{self.place.id}/', {'name': '   '}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_patch_invalid_image_url_fails(self):
        response = self.client.patch(
            f'/api/places/{self.place.id}/', {'image': 'not-a-url'}, format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)

    def test_patch_nonexistent_place_returns_404(self):
        response = self.client.patch('/api/places/9999/', {'name': 'X'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # Read-only protection on update

    def test_put_cannot_override_id(self):
        response = self.client.put(
            f'/api/places/{self.place.id}/',
            {**self.valid_data, 'id': 9999},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.place.id)

    def test_patch_cannot_override_created_at(self):
        response = self.client.patch(
            f'/api/places/{self.place.id}/',
            {'created_at': '2000-01-01T00:00:00Z'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['created_at'], '2000-01-01T00:00:00Z')


class TestDeletePlace(TestCase):
    # Tests for DELETE /api/places/<id>/

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.client.force_authenticate(user=self.user)
        self.place = Place.objects.create(
            name='Café Lumière',
            city='Paris',
            country='France',
            description='A cozy café near the Seine.',
            owner=self.user,
        )

    def test_delete_returns_204(self):
        response = self.client.delete(f'/api/places/{self.place.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_removes_from_database(self):
        self.client.delete(f'/api/places/{self.place.id}/')
        self.assertEqual(Place.objects.count(), 0)

    def test_delete_nonexistent_place_returns_404(self):
        response = self.client.delete('/api/places/9999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_twice_returns_404(self):
        self.client.delete(f'/api/places/{self.place.id}/')
        response = self.client.delete(f'/api/places/{self.place.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestUnicodePlaces(TestCase):
    # Verify unicode and emoji are handled correctly

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.client.force_authenticate(user=self.user)

    def test_create_place_with_unicode_name(self):
        data = {
            'name': 'Café Résumé',
            'city': 'Zürich',
            'country': 'Österreich',
            'description': 'A café with accented characters.',
        }
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Café Résumé')

    def test_create_place_with_emoji(self):
        data = {
            'name': 'Sunset Lounge 🌅',
            'city': 'Paris 🇫🇷',
            'country': 'France',
            'description': 'Great vibes.',
        }
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Sunset Lounge 🌅')


class TestUniqueConstraint(TestCase):
    # Duplicate (name, city) pairs should be rejected

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.client.force_authenticate(user=self.user)
        self.data = {
            'name': 'Café Lumière',
            'city': 'Paris',
            'country': 'France',
            'description': 'A cozy café.',
        }

    def test_duplicate_name_and_city_rejected(self):
        self.client.post('/api/places/', self.data, format='json')
        response = self.client.post('/api/places/', self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_name_different_city_allowed(self):
        self.client.post('/api/places/', self.data, format='json')
        data = {**self.data, 'city': 'Lyon'}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestDescriptionMaxLength(TestCase):
    # Description should be capped at 2000 characters

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.client.force_authenticate(user=self.user)
        self.base_data = {
            'name': 'Test Place',
            'city': 'London',
            'country': 'UK',
        }

    def test_description_at_2000_chars_accepted(self):
        data = {**self.base_data, 'description': 'A' * 2000}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_description_over_2000_chars_rejected(self):
        data = {**self.base_data, 'description': 'A' * 2001}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)


class TestImageUrlMaxLength(TestCase):
    # Cloudinary URLs can exceed the default URLField max_length of 200

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        self.client.force_authenticate(user=self.user)
        self.base_data = {
            'name': 'Test Place',
            'city': 'London',
            'country': 'UK',
            'description': 'A place.',
        }

    def test_long_cloudinary_url_accepted(self):
        long_path = 'a' * 250
        url = f'https://res.cloudinary.com/demo/image/upload/{long_path}.jpg'
        data = {**self.base_data, 'image': url}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_image_url_over_500_chars_rejected(self):
        long_path = 'a' * 460
        url = f'https://res.cloudinary.com/demo/image/upload/{long_path}.jpg'
        self.assertGreater(len(url), 500)
        data = {**self.base_data, 'image': url}
        response = self.client.post('/api/places/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image', response.data)


class TestFilterPlaces(TestCase):
    # Filtering by city and country on the list endpoint

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        Place.objects.create(name='Café Lumière', city='Paris', country='France', description='A café.', owner=self.user)
        Place.objects.create(name='Le Marais', city='Paris', country='France', description='A district.', owner=self.user)
        Place.objects.create(name='Hyde Park', city='London', country='UK', description='A park.', owner=self.user)

    def test_filter_by_city(self):
        response = self.client.get('/api/places/?city=Paris')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_country(self):
        response = self.client.get('/api/places/?country=UK')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_city_and_country(self):
        response = self.client.get('/api/places/?city=Paris&country=France')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_filter_no_match_returns_empty(self):
        response = self.client.get('/api/places/?city=Tokyo')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class TestSearchPlaces(TestCase):
    # Text search on name and description

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        Place.objects.create(
            name='Café Lumière', city='Paris', country='France',
            description='A cozy café near the Seine.', owner=self.user,
        )
        Place.objects.create(
            name='Hyde Park', city='London', country='UK',
            description='A large royal park in central London.', owner=self.user,
        )
        Place.objects.create(
            name='Sunset Lounge', city='Barcelona', country='Spain',
            description='Rooftop bar with sea views.', owner=self.user,
        )

    def test_search_by_name(self):
        response = self.client.get('/api/places/?search=Lumière')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_by_description(self):
        response = self.client.get('/api/places/?search=rooftop')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_partial_match(self):
        response = self.client.get('/api/places/?search=park')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_search_no_match(self):
        response = self.client.get('/api/places/?search=sushi')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)


class TestOrderingPlaces(TestCase):
    # Client-controlled ordering via ?ordering= parameter

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='SecurePass123!',
        )
        Place.objects.create(
            name='Beta Place', city='Berlin', country='Germany',
            description='Second.', owner=self.user,
        )
        Place.objects.create(
            name='Alpha Place', city='Amsterdam', country='Netherlands',
            description='First.', owner=self.user,
        )
        Place.objects.create(
            name='Gamma Place', city='Copenhagen', country='Denmark',
            description='Third.', owner=self.user,
        )

    def test_order_by_name_ascending(self):
        response = self.client.get('/api/places/?ordering=name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in response.data['results']]
        self.assertEqual(names, ['Alpha Place', 'Beta Place', 'Gamma Place'])

    def test_order_by_name_descending(self):
        response = self.client.get('/api/places/?ordering=-name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in response.data['results']]
        self.assertEqual(names, ['Gamma Place', 'Beta Place', 'Alpha Place'])

    def test_order_by_city(self):
        response = self.client.get('/api/places/?ordering=city')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cities = [p['city'] for p in response.data['results']]
        self.assertEqual(cities, ['Amsterdam', 'Berlin', 'Copenhagen'])

    def test_order_by_created_at(self):
        response = self.client.get('/api/places/?ordering=created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p['name'] for p in response.data['results']]
        self.assertEqual(names, ['Beta Place', 'Alpha Place', 'Gamma Place'])