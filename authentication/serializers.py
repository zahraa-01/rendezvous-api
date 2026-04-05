from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with that email already exists.')
        return value

    def validate_password(self, value):
        validate_password(value, user=User(**self.initial_data))
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, data):
        try:
            uid = urlsafe_base64_decode(data['uid']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'uid': 'Invalid user ID.'})

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({'token': 'Invalid or expired token.'})

        try:
            validate_password(data['new_password'], user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})

        data['user'] = user
        return data