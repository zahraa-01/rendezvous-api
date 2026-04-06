from rest_framework import serializers
from places.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Place
        fields = ['id', 'owner', 'name', 'city', 'country', 'description', 'image', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at']

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

    def validate_description(self, value):
        if len(value) > 2000:
            raise serializers.ValidationError('Ensure this field has no more than 2000 characters.')
        return value

    def validate_image(self, value):
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('Image must be under 2MB.')
        return value
