from django import forms
from .models import CustomerPickups


class CustomerSchedulingForm(forms.ModelForm):
    class Meta:
        model = CustomerPickups
        fields = ['customer_scheduled_date', 'customer_pickup_time',
                  'customer_waste_type', 'customer_notes', 'customer_waste_size', 'customer_images']
        widgets = {
            'customer_scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded-lg'}),
            'customer_pickup_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-2 border rounded-lg'}),
            'customer_notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-2 border rounded-lg'}),
            'customer_images': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }

    def __init__(self, *args, customer_plan=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_plan = customer_plan  # ✅ store the pickup_plan passed in view

    def save(self, commit=True):
        pickup = super().save(commit=False)
        if self.customer_plan:
            pickup.customer_pickup_plan = self.customer_plan  # ✅ use correct attribute
        if commit:
            pickup.save()
        return pickup

    def clean_customer_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('customer_scheduled_date')
        if self.customer_plan and self.customer_plan.household_pickups_done >= self.customer_plan.household_plan.customer_pickups_per_month:
            raise forms.ValidationError(
                "You have already scheduled all your pickups for this month."
            )
        return scheduled_date
