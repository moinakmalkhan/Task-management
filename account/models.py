from django.db import models
from django.contrib.auth import get_user_model


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='user_profile')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user

