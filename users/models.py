from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Profile(models.Model):
    USER_TYPES = (('business', 'Business'),
                  ('household', 'Household'),
                  ('recycler', 'Recycler'),)

    user = models.OneToOneField(
        User, on_delete=models.CASCADE)

    user_type = models.CharField(
        max_length=300, choices=USER_TYPES)
    address = models.TextField(null=True, blank=True)

    def __str__(
        self): return f"{self.user} - {self.user_type} Profile" or 'No profile'
