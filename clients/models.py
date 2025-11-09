from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class Plans(models.Model):

    pickups_per_month = models.PositiveIntegerField()
    pickups_done = models.PositiveIntegerField(default=0)
    all_locations = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    name = models.CharField(max_length=300, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=2000)

    def __str__(self):
        return f"{self.name} - R{self.price}"


class Client(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=250,  null=True, blank=True)
    contact_email = models.EmailField(max_length=250,  null=True, blank=True)
    address = models.TextField()
    selected_plan = models.ForeignKey(
        Plans, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=250,  null=True, blank=True)
    material_type = models.CharField(
        max_length=300,  null=True, blank=True)
    date_requested = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username}- Business Profile'


class PickupPlan(models.Model):
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, null=True, blank=True)
    plan = models.ForeignKey(
        Plans, on_delete=models.CASCADE, null=True, blank=True)
    month = models.DateField()
    pickups_done = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.client.company_name} - {self.plan.name} ({self.month.strftime('%B %Y')})"


class Pickups(models.Model):
    WASTE_CHOICES = [('plastic', 'Plastic'),
                     ('paper_cardboard', 'Paper & Cardboard'),
                     ('glass', 'Glass'),
                     ('metal', 'Metal'),
                     ('organic', 'Organic / Food Waste'),
                     ('e_waste', 'E-Waste'),
                     ('textiles', 'Textiles / Fabric'),
                     ('hazardous', 'Hazardous Waste'),
                     ('medical', 'Medical Waste'),
                     ('construction', 'Construction / Rubble'),
                     ('mixed', 'Mixed Waste'),]
    PICKUP_STATUSES = [('completed', 'Completed'),
                       ('pending', 'Pending'),
                       ('cancelled', ' Cancelled')]
    pickup_plan = models.ForeignKey(PickupPlan, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    pickup_time = models.TimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    # make it choice field later
    waste_type = models.CharField(
        null=True, blank=True, choices=WASTE_CHOICES, max_length=100)
    # used later to pass to API for waste type recognition
    images = models.ImageField(
        upload_to='pickup_images/', null=True, blank=True)
    weight = models.PositiveIntegerField(default=0)  # weight in kg
    collected_by = models.CharField(max_length=250,  null=True, blank=True)

    def __str__(self):
        return f"{self.pickup_plan.client.company_name} - {self.scheduled_date}"
