from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save

User = get_user_model()


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return str(self.user)


@receiver(pre_save, sender=User)
def user_pre_save(sender, instance, *args, **kwargs):
    instance.username = instance.email
