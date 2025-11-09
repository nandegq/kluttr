from django.db import models
from clients.models import PickupPlan, Pickups
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class WasteAnalyticsData(models.Model):
    pickup = models.ForeignKey(
        Pickups, on_delete=models.CASCADE, null=True, blank=True)
    co2_saved = models.PositiveIntegerField(default=0)


@receiver(post_save, sender=Pickups)
def create_or_update_waste_analytics(sender, instance, created, **kwargs):
    """
    Automatically create or update WasteAnalyticsData 
    whenever a Pickup is saved.
    """
    from .models import WasteAnalyticsData  # avoid circular import

    co2_saved = instance.weight * 1.8  # Simple conversion formula

    # If it's a new pickup, create analytics data
    if created:
        WasteAnalyticsData.objects.create(
            pickup=instance,
            co2_saved=co2_saved
        )
    else:
        # If the pickup already exists, update the CO₂ saved
        WasteAnalyticsData.objects.update_or_create(
            pickup=instance,
            defaults={'co2_saved': co2_saved}
        )
