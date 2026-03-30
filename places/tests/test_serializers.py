from django.test import TestCase
from places.models import Place
from places.serializers import PlaceSerializer


class TestPlaceSerializer(TestCase):

    def setUp(self):
        self.place = Place.objects.create(
            name='Café Lumière',
            city='Paris',
            country='France',
            description='A cozy café near the Seine.',
        )
        self.serializer = PlaceSerializer(instance=self.place)

    def test_serializer_contains_expected_fields(self):
        data = self.serializer.data
        self.assertEqual(
            set(data.keys()),
            {'id', 'name', 'city', 'country', 'description', 'image', 'created_at'},
        )

    def test_serializer_returns_correct_name(self):
        self.assertEqual(self.serializer.data['name'], 'Café Lumière')

    def test_valid_data_passes_validation(self):
        data = {
            'name': 'Hyde Park',
            'city': 'London',
            'country': 'UK',
            'description': 'A large royal park.',
        }
        serializer = PlaceSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_name_cannot_be_blank(self):
        data = {
            'name': '',
            'city': 'London',
            'country': 'UK',
            'description': 'A park.',
        }
        serializer = PlaceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_city_cannot_be_blank(self):
        data = {
            'name': 'Hyde Park',
            'city': '',
            'country': 'UK',
            'description': 'A park.',
        }
        serializer = PlaceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('city', serializer.errors)

    def test_country_cannot_be_blank(self):
        data = {
            'name': 'Hyde Park',
            'city': 'London',
            'country': '',
            'description': 'A park.',
        }
        serializer = PlaceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('country', serializer.errors)

    def test_image_must_be_valid_url(self):
        data = {
            'name': 'Hyde Park',
            'city': 'London',
            'country': 'UK',
            'description': 'A park.',
            'image': 'not-a-url',
        }
        serializer = PlaceSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('image', serializer.errors)
