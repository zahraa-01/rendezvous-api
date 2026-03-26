from rest_framework import serializers
from places.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'city', 'country', 'description', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']
