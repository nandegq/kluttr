from django import forms
from .models import CustomerPickups


class CustomerSchedulingForm(forms.ModelForm):

    class Meta:
        model = CustomerPickups
        fields = ['customer_scheduled_date', 'customer_pickup_time',
                  'customer_waste_type', 'customer_notes', 'customer_weight', 'customer_images']
        widgets = {
            'customer_scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded-lg'}),
            'customer_pickup_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-2 border rounded-lg'}),
            'customer_notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-2 border rounded-lg'}),
            'customer_weight': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'customer_images': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }

    def __init__(self, *args, customer_plan=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.customer_plan = customer_plan

    def save(self, commit=True):
        pickup = super().save(commit=False)
        if self.customer_pickup_plan:
            pickup.customer_pickup_plan = self.customer_pickup_plan  # ✅ correct field name
        if commit:
            pickup.save()
        return pickup

    def customer_scheduled_date(self):
        date = self.cleaned_data['customer_scheduled_date']
    # Check if already maxed out
        if self.customer_pickup_plan.customer_pickups_done >= self.customer_pickup_plan.plan_name.customer_pickups_per_month:
            raise forms.ValidationError(
                "You have already scheduled all your pickups for this month."
            )
        return date
