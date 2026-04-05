from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile',
    )
    bio = models.TextField(max_length=500, blank=True, default='')
    avatar = models.URLField(blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f'{self.user.username} profile'
