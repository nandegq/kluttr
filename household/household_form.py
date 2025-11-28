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
            'customer_images',
            'customer_address',
        ]
        widgets = {
            'customer_scheduled_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'w-full p-2 border rounded-lg'}
            ),
            'customer_pickup_time': forms.TimeInput(
                attrs={'type': 'time', 'class': 'w-full p-2 border rounded-lg'}
            ),
            'customer_notes': forms.Textarea(
                attrs={'rows': 3, 'class': 'w-full p-2 border rounded-lg'}
            ),
            'customer_address': forms.Textarea(
                attrs={'rows': 3, 'class': 'w-full p-2 border rounded-lg'}
            ),
            'customer_images': forms.ClearableFileInput(
                attrs={'class': 'w-full p-2 border rounded-lg'}
            ),
        }

    def __init__(self, *args, pickup_plan=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.pickup_plan = pickup_plan  # CustomerPickupPlan instance

    def clean_customer_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('customer_scheduled_date')

    # Only enforce limits for subscription plans with > 0 pickups per month
        if (
            self.pickup_plan
            and self.pickup_plan.household_plan.customer_pickups_per_month > 0
            and self.pickup_plan.household_pickups_done >= self.pickup_plan.household_plan.customer_pickups_per_month
        ):
            raise forms.ValidationError(
                "You have already scheduled all your pickups for this month."
            )

        return scheduled_date

    def save(self, commit=True):
        pickup = super().save(commit=False)
        if self.pickup_plan:
            # assign the correct CustomerPlans instance
            pickup.customer_pickup_plan = self.pickup_plan.household_plan
        if commit:
            pickup.save()
        return pickup
