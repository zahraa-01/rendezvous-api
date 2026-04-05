from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from authentication.serializers import RegisterSerializer


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
        email.send()


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
        })