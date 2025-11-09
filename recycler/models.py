from django.db import models
from django.contrib.auth.models import User
from users.models import Profile


# Create your models here.

class Collector(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=300, null=True, blank=True)
    contact_number = models.CharField(max_length=100, null=True, blank=True)
    preferred_waste = models.CharField(max_length=200, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.company_name:
            self.company_name = self.user.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.company_name}({self.user.username})'
