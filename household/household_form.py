from django import forms
from .models import CustomerPickups, CustomerPickupPlan


class CustomerSchedulingForm(forms.ModelForm):
    class Meta:
        model = CustomerPickups
        fields = [
            'customer_scheduled_date',
            'customer_pickup_time',
            'customer_waste_type',
            'customer_notes',
            'customer_images'
        ]
        widgets = {
            'customer_scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded-lg'}),
            'customer_pickup_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-2 border rounded-lg'}),
            'customer_notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-2 border rounded-lg'}),
            'customer_images': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }

    def __init__(self, *args, customer_pickup_plan=None, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ This is the CustomerPickupPlan instance
        self.customer_pickup_plan = customer_pickup_plan

    def save(self, commit=True):
        pickup = super().save(commit=False)

        # attach subscription plan (CustomerPlans)
        if self.customer_pickup_plan:
            pickup.customer_pickup_plan = self.customer_pickup_plan.household_plan

        if commit:
            pickup.save()
        return pickup

    def clean_customer_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('customer_scheduled_date')

        # check if user exceeded allowed pickups for the month
        if (
            self.customer_pickup_plan and
            self.customer_pickup_plan.household_pickups_done >=
            self.customer_pickup_plan.household_plan.customer_pickups_per_month
        ):
            raise forms.ValidationError(
                "You have already scheduled all your pickups for this month."
            )

        return scheduled_date
