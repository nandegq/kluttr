from django import forms
from .models import Pickups


class PickUpScheduling(forms.ModelForm):

    class Meta:
        model = Pickups
        fields = ['scheduled_date', 'pickup_time',
                  'waste_type', 'notes', 'weight', 'images']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-2 border rounded-lg'}),
            'pickup_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-2 border rounded-lg'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'w-full p-2 border rounded-lg'}),
            'weight': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'images': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
        }

    def __init__(self, *args, **kwargs):
        self.pickup_plan = kwargs.pop('pickup_plan', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        pickup = super().save(commit=False)
        if self.pickup_plan:
            pickup.pickup_plan = self.pickup_plan  # ✅ correct field name
        if commit:
            pickup.save()
        return pickup

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data['scheduled_date']

        if self.pickup_plan:
            from .models import Pickups

        # Count how many pickups exist for this plan *this month*
            existing_count = Pickups.objects.filter(
                pickup_plan=self.pickup_plan,
                scheduled_date__year=scheduled_date.year,
                scheduled_date__month=scheduled_date.month).count()

            limit = self.pickup_plan.plan.pickups_per_month

            if existing_count >= limit:
                raise forms.ValidationError(
                    f"You've reached your {limit} pickup(s) limit for this month.")

        return scheduled_date
