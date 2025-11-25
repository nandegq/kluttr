from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class CustomerPlans(models.Model):
    customer_pickups_per_month = models.PositiveIntegerField()
    customer_pickups_done = models.PositiveIntegerField(default=0)
    once_off_service = models.BooleanField(default=False)
    customerplan_is_popular = models.BooleanField(default=False)
    plan_name = models.CharField(max_length=300, null=True, blank=True)
    plan_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=2000)

    def __str__(self):
        return self.plan_name


class CustomerPickups(models.Model):
    WASTE_KINDS = [('plastic', 'Plastic'),
                   ('paper_cardboard', 'Paper & Cardboard'),
                   ('glass', 'Glass'),
                   ('metal', 'Metal'),
                   ('organic/food/garden', 'Organic /Garden/ Food Waste'),
                   ('e_waste', 'E-Waste'),
                   ('textiles/clothing', 'Textiles /Clothing /Fabric'),
                   ('medical', 'Medical Waste'),
                   ('construction', 'Construction / Rubble'),
                   ('mixed', 'Mixed Waste'),
                   ('furniture/appliances', 'Furniture / Appliances'),]
    PICKUP_STATUS = [('completed', 'Completed'),
                     ('pending', 'Pending'),
                     ('cancelled', 'Cancelled')]
    WASTE_SIZES = [('small', 'Small/Light/Equivalent to plastic bag (R499)'),
                   ('medium', 'Medium/Standard/Equivalent to bin bag (R899)'),
                   ('large', 'Large/Bulky items (R1999)'),]
    customer_pickup_plan = models.ForeignKey(
        CustomerPlans, on_delete=models.CASCADE)
    customer_scheduled_date = models.DateField()
    customer_pickup_time = models.TimeField(null=True, blank=True)
    customer_pickup_completed = models.CharField(
        max_length=300, choices=PICKUP_STATUS, default='pending')
    customer_notes = models.TextField(blank=True, null=True)
    # make it choice field later
    customer_waste_type = models.CharField(
        null=True, blank=True, choices=WASTE_KINDS, max_length=100)
    # used later to pass to API for waste type recognition
    customer_images = models.ImageField(
        upload_to='pickup_images/', null=True, blank=True)
    # weight in kg
    waste_size = models.CharField(
        null=True, blank=True, choices=WASTE_SIZES, max_length=300)
    customer_collected_by = models.CharField(
        max_length=250,  null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.customer_pickup_plan} - {self.customer_scheduled_date}"


class Customer(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_name = models.CharField(
        max_length=400,  null=True, blank=True)
    customer_email = models.EmailField(max_length=250,  null=True, blank=True)
    customer_address = models.TextField()
    customer_plan = models.ForeignKey(
        CustomerPlans, on_delete=models.SET_NULL, null=True, blank=True)
    customer_phone_number = models.CharField(
        max_length=250,  null=True, blank=True)
    customer_material_type = models.CharField(
        max_length=300,  null=True, blank=True)
    customer_date_requested = models.DateTimeField(default=timezone.now)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - Household Profile'


class CustomerPickupPlan(models.Model):

    household_customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True)
    household_plan = models.ForeignKey(
        CustomerPlans, on_delete=models.CASCADE, null=True, blank=True)
    household_month = models.DateField()
    household_pickups_done = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.household_customer} - {self.household_plan.plan_name} ({self.household_month.strftime('%B %Y')})"
