from django.contrib import admin
from .models import CustomerPlans, Customer, CustomerPickups, CustomerPickupPlan

# Register your models here.
admin.site.register(CustomerPlans)
admin.site.register(Customer)
admin.site.register(CustomerPickups)
admin.site.register(CustomerPickupPlan)
