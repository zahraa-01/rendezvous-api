from django.test import TestCase
from django.utils import timezone
from places.models import Place


class TestPlaceModel(TestCase):

    def setUp(self):
        self.place = Place.objects.create(
            name='Café Lumière',
            city='Paris',
            country='France',
            description='A cozy café near the Seine.',
        )

    def test_can_create_place(self):
        self.assertEqual(self.place.name, 'Café Lumière')
        self.assertEqual(self.place.city, 'Paris')
        self.assertEqual(self.place.country, 'France')
        self.assertEqual(self.place.description, 'A cozy café near the Seine.')

    def test_image_defaults_to_empty_string(self):
        self.assertEqual(self.place.image, '')

    def test_created_at_is_auto_set(self):
        self.assertIsNotNone(self.place.created_at)
        self.assertLessEqual(self.place.created_at, timezone.now())

    def test_str_returns_name(self):
        self.assertEqual(str(self.place), 'Café Lumière')