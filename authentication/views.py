import logging

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from authentication.serializers import (
    RegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)

logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        html_body = render_to_string(
            'authentication/welcome_email.html',
            {'username': user.username},
        )
        plain_body = (
            f'Welcome to Rendezvous, {user.username}!\n\n'
            'Thanks for joining Rendezvous — where every place has a story, '
            'told by the people who know it best.\n\n'
            'Locals, travellers, explorers — they all have somewhere special. '
            'Discover somewhere new, share somewhere meaningful, and plan your '
            'next rendezvous with the people who matter most.\n\n'
            'See you out there.'
        )
        email = EmailMultiAlternatives(
            subject='Welcome to Rendezvous!',
            body=plain_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_body, 'text/html')
        try:
            email.send()
        except Exception:
            logger.exception('Failed to send welcome email to %s', user.email)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'If an account with that email exists, a password reset email has been sent.'},
                status=status.HTTP_200_OK,
            )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        reset_link = f'{frontend_url}/reset-password/{uid}/{token}/'

        html_body = render_to_string(
            'authentication/password_reset_email.html',
            {'username': user.username, 'reset_link': reset_link},
        )
        plain_body = (
            f'Hi {user.username},\n\n'
            'We received a request to reset your Rendezvous password.\n\n'
            f'Click the link below to set a new password:\n{reset_link}\n\n'
            'If you didn\'t request this, you can safely ignore this email.'
        )
        msg = EmailMultiAlternatives(
            subject='Rendezvous Password Reset',
            body=plain_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        try:
            msg.send()
        except Exception:
            logger.exception('Failed to send password reset email to %s', user.email)

        return Response(
            {'detail': 'If an account with that email exists, a password reset email has been sent.'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(
            {'detail': 'Password has been reset successfully.'},
            status=status.HTTP_200_OK,
        )


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        })