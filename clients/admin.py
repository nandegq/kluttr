from django.contrib import admin
from .models import Client, PickupPlan, Pickups, Plans

# Register your models here.

admin.site.register(Client)
admin.site.register(PickupPlan)
admin.site.register(Pickups)
admin.site.register(Plans)
