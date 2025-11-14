
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.contrib import messages
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from urllib.parse import urlencode
from datetime import date
import requests
from django.contrib.auth.models import User

from .models import Customer, CustomerPlans, CustomerPickups, CustomerPickupPlan
# make sure this form exists
from household.household_form import CustomerSchedulingForm


# 🏠 1️⃣ Onboarding View
def household_onboarding(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.onboarding_complete = True
        profile.save()
        return redirect('household_dashboard')

    return render(request, 'household_dashboard.html')


# 💡 2️⃣ Plan Selection
@login_required
def household_plan(request):
    plans = CustomerPlans.objects.all()
    if request.method == 'POST':
        plan_id = request.POST.get('plan')
        if plan_id:
            selected_plan = CustomerPlans.objects.get(id=plan_id)

        # Ensure the user has a customer profile
            customer = request.user.customer
            customer.customer_plan = selected_plan
            customer.save()
            if selected_plan.plan_name.lower() == 'on-demand':
                return redirect('ondemand_payment')
            else:

                return redirect('household_payment_info')

    return render(request, 'household_onboard_plan.html', {'plans': plans})


# 💳 3️⃣ Payment Page (PayFast Integration)
@login_required
def household_payment_info(request):
    customer = request.user.customer
    plan = customer.customer_plan
    plan_id = request.GET.get('plan')

    if plan_id:
        try:
            plan = CustomerPlans.objects.get(id=plan_id)
            customer.customer_plan = plan
            customer.save()
        except CustomerPlans.DoesNotExist:
            messages.error(request, "Selected plan does not exist.")
            return redirect('household_plan')
    else:
        plan = customer.customer_plan

        if not plan:
            messages.error(request, "Please select a plan first.")
            return redirect('household_plan')

    if request.method == 'POST':
        if plan.plan_name.lower() == 'on-demand':
            data = {'merchant_id': settings.PAYFAST_MERCHANT_ID,
                    'merchant_key': settings.PAYFAST_MERCHANT_KEY,
                    'amount': str(plan.plan_price),  # The one-time payment
                    'item_name': plan.plan_name,
                    'return_url': request.build_absolute_uri('/household_schedule/'),
                    'cancel_url': request.build_absolute_uri('/household/household_plan/'),
                    'notify_url': request.build_absolute_uri('/household/payfast-ipn/'),
                    'custom_str1': request.user.email,
                    'custom_str2': plan.plan_name, }
            query_string = urlencode(data)
            payfast_url = f'https://www.payfast.co.za/eng/process?{query_string}'
            return redirect(payfast_url)
        else:

            data = {
                'merchant_id': settings.PAYFAST_MERCHANT_ID,
                'merchant_key': settings.PAYFAST_MERCHANT_KEY,
                'amount': str(plan.plan_price),
                'item_name': plan.plan_name,
                'return_url': request.build_absolute_uri('/household_schedule/'),
                'cancel_url': request.build_absolute_uri('/household_plan/'),
                'notify_url': 'http://127.0.0.1:8000/payfast-ipn/',
                'custom_str1': request.user.email,
                'custom_str2': plan.plan_name,
                # Subscription fields
                'subscription_type': 1,  # 1 = subscription
                'recurring_amount': str(plan.plan_price),
                'frequency': 3,  # 3 = monthly
                'cycles': 0,  # 0 = indefinite
                'billing_date': date.today().isoformat(),  # first billing date
            }
            query_string = urlencode(data)
            payfast_url = f'https://www.payfast.co.za/eng/process?{query_string}'
            return redirect(payfast_url)

    return render(request, 'household_onboard_pay.html')


# 📩 4️⃣ PayFast IPN Listener
@csrf_exempt
def household_payfast_ipn(request):
    if request.method == 'POST':
        data = request.POST.copy()
        verify_url = 'https://www.payfast.co.za/eng/process'
        verify_response = requests.post(verify_url, data=data)

        if verify_response.text == 'VALID':
            user_email = data.get('custom_str1')
            plan_name = data.get('custom_str2')
            send_confirmation_email_html(user_email, plan_name)
            return HttpResponse('OK')
        else:
            return HttpResponse('INVALID')
    return HttpResponse('Method not allowed', status=405)


def send_confirmation_email_html(user_email, plan_name):
    subject = "Your Kluttr Subscription is Confirmed ✅"
    html_content = render_to_string(
        'household_email_confirm.html', {'plan_name': plan_name})
    email = EmailMessage(subject, html_content, to=[user_email])
    email.content_subtype = "html"
    email.send()


# 🚛 6️⃣ Schedule Pickup
@login_required
def household_schedule(request):
    customer = request.user.customer

    # 🧩 Ensure customer has selected a plan first
    if not customer.customer_plan:
        messages.error(
            request, "Please select a plan before scheduling a pickup.")
        return redirect('household_plan')

    today = date.today()
    current_month = date(today.year, today.month, 1)

    # ✅ Get or create the PickupPlan properly
    pickup_plan, created = CustomerPickupPlan.objects.get_or_create(
        household_customer=customer,
        household_month=current_month,
        defaults={
            'household_plan': customer.customer_plan,
            'household_pickups_done': 0
        }
    )

    # 🧾 Handle form submission
    if request.method == 'POST':
        form = CustomerSchedulingForm(request.POST, customer_plan=pickup_plan)
        if form.is_valid():
            pickup = form.save(commit=False)
            pickup.customer_pickup_plan = pickup_plan  # ✅ correct relation
            pickup.save()

            # ✅ Update pickup count
            pickup_plan.household_pickups_done += 1
            pickup_plan.save()

            messages.success(request, "Pickup scheduled successfully!")
            return redirect('household:household_success')
    else:
        form = CustomerSchedulingForm(customer_plan=pickup_plan)

    return render(request, 'household_onboard_schedule.html', {
        'form': form,
        'selected_plan': pickup_plan.household_plan,
        'pickup_plan': pickup_plan
    })


# ✅ 7️⃣ Success Page
def household_success(request):
    return render(request, 'household_success.html')


# 📊 8️⃣ Dashboard
@login_required
def household_dashboard(request):
    return render(request, 'household_dashboard.html')


# ⚙️ 9️⃣ Manage Plan
@login_required
def household_manage_plan(request):
    return render(request, 'household_manage_plan.html')


def clean_waste_type(self):
    waste_type = self.cleaned_data.get('waste_type')
    # Add any custom validation for waste_type here if needed
    return waste_type.lower()
