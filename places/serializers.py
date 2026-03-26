from rest_framework import serializers
from places.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'city', 'country', 'description', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('This field may not be blank.')
        return value

    def validate_city(self, value):
        if not value.strip():
            raise serializers.ValidationError('This field may not be blank.')
        return value

    def validate_country(self, value):
        if not value.strip():
            raise serializers.ValidationError('This field may not be blank.')
        return value
