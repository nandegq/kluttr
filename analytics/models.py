from django.db import models
from clients.models import PickupPlan, Pickups
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
