from django.db import models
from django.contrib.auth.models import User
from users.models import Profile
from household.models import CustomerPickups


# Create your models here.

class Collector(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=300, null=True, blank=True)
    contact_number = models.CharField(max_length=100, null=True, blank=True)
    preferred_waste = models.CharField(max_length=500, null=True, blank=True)

    @property
    def earnings(self):
        completed_pickups = self.pickup_set.filter(status='completed')
        total = sum(p.price * 0.20 for p in completed_pickups)
        return round(total, 2)

    def save(self, *args, **kwargs):
        if not self.company_name:
            self.company_name = self.user.username
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.company_name}({self.user.username})'
