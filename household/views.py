
# Create your views here.
import logging
from django.shortcuts import render, redirect, get_object_or_404
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
import hashlib
from django.urls import reverse
from .models import Customer, CustomerPlans, CustomerPickups, CustomerPickupPlan
import urllib.parse

# make sure this form exists
from household.household_form import CustomerSchedulingForm
import traceback
logger = logging.getLogger(__name__)


# 🏠 1️⃣ Onboarding View
def household_onboarding(request):
    profile = request.user.profile

    if request.method == 'POST':
        profile.onboarding_complete = True
        profile.save()
        return redirect('household_dashboard')

    return render(request, 'household_dashboard.html')


logger = logging.getLogger(__name__)


@login_required
def household_plan(request):
    # Get all plans
    plans = CustomerPlans.objects.all()

    try:
        # Ensure user has a customer profile
        customer = getattr(request.user, 'customer', None)
        if not customer:
            logger.error(f"No customer profile for user {request.user}")
            messages.error(request, "No customer profile found.")
            return redirect('landing')  # or wherever makes sense

        if request.method == 'POST':
            plan_id = request.POST.get('plan')
            if plan_id:
                selected_plan = get_object_or_404(CustomerPlans, id=plan_id)

                # Assign selected plan to customer
                customer.customer_plan = selected_plan
                customer.save()

                # Redirect to payment page with plan_id in URL
                payment_url = f"{reverse('household:household_payment_info')}?plan={selected_plan.id}"
                return redirect(payment_url)
            else:
                messages.error(request, "Please select a plan.")
                return redirect('household:household_plan')

    except Exception as e:
        logger.exception("Error in household_plan view")
        messages.error(request, "There was an error loading the plan page.")
        return redirect('landing')  # fallback page

    return render(request, 'household_onboard_plan.html', {'plans': plans})


# def generate_signature(data, passphrase):
    # 1. Remove empty fields
    # clean_data = {k: v for k, v in data.items() if v}

    # 2. Sort alphabetically
    # items = sorted(clean_data.items())

    # 3. Create query string manually (no urlencode!)
    # sig = "&".join(f"{k}={v}" for k, v in items)

    # 4. Add passphrase
    # sig = f"{sig}&passphrase={passphrase}"

    # 5. MD5 hash
    # return hashlib.md5(sig.encode('utf-8')).hexdigest()


@login_required
def household_payment_info(request):
    client = request.user.customer
    plan = client.customer_plan

    if not plan:
        return redirect('household:household_plan')

    plan_name_lower = plan.plan_name.lower() if plan.plan_name else ""

    if request.method == 'POST':
        # URLs
        return_url = request.build_absolute_uri(
            reverse('household:household_schedule'))
        cancel_url = request.build_absolute_uri(
            reverse('household:household_payment_info'))
        notify_url = request.build_absolute_uri(
            reverse('household:household_payfast_ipn'))

        # Email & plan name for IPN email logic
        custom_str1 = client.customer_email or client.user.email
        custom_str2 = plan.plan_name

        # ON-DEMAND
        if plan_name_lower == 'on-demand':
            waste_size = request.POST.get('waste_size')
            if not waste_size:
                return render(request, 'household_onboard_pay.html', {
                    'plan': plan,
                    'error': "Please select a waste size."
                })

            price_map = {'small': 499, 'medium': 799, 'large': 1999}
            amount = price_map.get(waste_size)

            client.customer_material_type = waste_size
            client.save()

            payfast_url = (
                f"https://www.payfast.co.za/eng/process?"
                f"merchant_id={settings.PAYFAST_MERCHANT_ID}&"
                f"merchant_key={settings.PAYFAST_MERCHANT_KEY}&"
                f"amount={amount}&"
                f"item_name=On-Demand+Waste+Removal&"
                f"custom_str1={custom_str1}&"
                f"custom_str2={custom_str2}&"
                f"custom_int1={client.id}&"
                f"return_url={return_url}&"
                f"cancel_url={cancel_url}&"
                f"notify_url={notify_url}"
            )
            return redirect(payfast_url)

        # SUBSCRIPTIONS
        elif plan_name_lower in ['eco', 'eco pro']:
            amount = plan.plan_price
            plan_name_url = plan.plan_name.replace(" ", "+")

            payfast_url = (
                f"https://www.payfast.co.za/eng/process?"
                f"merchant_id={settings.PAYFAST_MERCHANT_ID}&"
                f"merchant_key={settings.PAYFAST_MERCHANT_KEY}&"
                f"subscription_type=1&"
                f"item_name={plan_name_url}&"
                f"amount={amount}&"
                f"frequency=30&cycles=0&"
                f"custom_str1={custom_str1}&"
                f"custom_str2={custom_str2}&"
                f"custom_int1={client.id}&"
                f"return_url={return_url}&"
                f"cancel_url={cancel_url}&"
                f"notify_url={notify_url}"
            )
            return redirect(payfast_url)

        return render(request, 'household_onboard_pay.html', {
            'plan': plan,
            'error': "Unknown plan type."
        })

    return render(request, 'household_onboard_pay.html', {'plan': plan})


@csrf_exempt
def household_payfast_ipn(request):
    if request.method == 'POST':
        # Raw data from PayFast
        data = request.POST.copy()

        # Convert to proper encoded string
        encoded_data = urllib.parse.urlencode(data)

        # Verify with PayFast (LIVE)
        verify_url = "https://www.payfast.co.za/eng/query/validate"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        verify_response = requests.post(
            verify_url,
            data=encoded_data,
            headers=headers
        )

        if verify_response.text.strip() == "VALID":
            user_email = data.get("custom_str1")
            plan_name = data.get("custom_str2")

            send_confirmation_email_html(user_email, plan_name)

            return HttpResponse("OK")

        return HttpResponse("INVALID", status=400)

    return HttpResponse("Method not allowed", status=405)


def send_confirmation_email_html(user_email, plan_name):
    subject = "Your Kluttr Subscription is Confirmed ✅"
    html_content = render_to_string(
        'household_email_confirm.html', {'plan_name': plan_name})
    email = EmailMessage(subject, html_content, to=[user_email])
    email.content_subtype = "html"
    email.send()


@login_required
def household_schedule(request):
    try:
        customer = request.user.customer

        if not customer.customer_plan:
            messages.error(
                request, "Please select a plan before scheduling a pickup."
            )
            return redirect('household:household_plan')

        today = date.today()
        current_month = date(today.year, today.month, 1)

        # get or create the monthly pickup plan for this customer
        pickup_plan, created = CustomerPickupPlan.objects.get_or_create(
            household_customer=customer,
            household_month=current_month,
            defaults={
                'household_plan': customer.customer_plan,
                'household_pickups_done': 0
            }
        )

        if request.method == 'POST':
            form = CustomerSchedulingForm(
                request.POST, request.FILES, pickup_plan=pickup_plan
            )
            if form.is_valid():
                pickup = form.save()  # customer_pickup_plan is assigned inside form
                pickup_plan.household_pickups_done += 1
                pickup_plan.save()

                messages.success(request, "Pickup scheduled successfully!")
                return redirect('household:household_success')
            else:
                print(form.errors)  # debug validation errors
        else:
            form = CustomerSchedulingForm(pickup_plan=pickup_plan)

        return render(request, 'household_onboard_schedule.html', {
            'form': form,
            'selected_plan': pickup_plan.household_plan,
            'pickup_plan': pickup_plan
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {e}")


def household_success(request):
    return render(request, 'household_success.html')


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
