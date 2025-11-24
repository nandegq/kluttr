from django.shortcuts import render, redirect
from clients.schedulepickup import PickUpScheduling
from clients.models import Client, PickupPlan, Pickups, Plans
from datetime import date
from django.contrib.auth.decorators import login_required
from django.conf import settings
from urllib.parse import urlencode
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.shortcuts import get_object_or_404
from django.urls import reverse
import urllib.parse
# Create your views here.


def landing(request):
    return render(request, 'landing.html')


def business_onboarding(request):
    profile = request.user.profile

    if request.method == 'POST':

        profile.onboarding_complete = True
        profile.save()
        return redirect('clients:business_dashboard')

    return render(request, 'business_dashboard.html')


@login_required
def select_plan(request):
    try:
        plans = Plans.objects.all()

        if request.method == 'POST':
            plan_id = request.POST.get('plan')
            if not plan_id:
                return HttpResponse("No plan selected", status=400)

            selected_plan = get_object_or_404(Plans, id=plan_id)
            client = request.user.client
            client.selected_plan = selected_plan
            client.save()
            return redirect('clients:payment_info')

        return render(request, 'client_onboard_plan.html', {'plans': plans})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Error: {e}")


@login_required
def payment_info(request):
    client = request.user.client
    plan = client.selected_plan   # FIXED

    if not plan:
        return redirect('clients:select_plan')

    name_lower = (plan.name or "").lower()

    if request.method == 'POST':
        # Build URLs
        return_url = request.build_absolute_uri(reverse('clients:schedule'))
        cancel_url = request.build_absolute_uri(
            reverse('clients:payment_info'))
        notify_url = request.build_absolute_uri(reverse('clients:payfast_ipn'))

        # Correct field name
        custom_str1 = client.contact_email or client.user.email
        custom_str2 = plan.name

        # ON-DEMAND LOGIC
        if name_lower == 'on-demand':
            waste_size = request.POST.get('waste_size')
            if not waste_size:
                return render(request, 'client_onboard_pay.html', {
                    'plan': plan,
                    'error': "Please select a waste size."
                })

            price_map = {'small': 999, 'medium': 1599, 'large': 2999}
            amount = price_map.get(waste_size)

            # FIXED field name
            client.material_type = waste_size
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

        # SUBSCRIPTION LOGIC
        elif name_lower in ['business eco', 'business eco pro']:
            amount = plan.price
            plan_name_url = plan.name.replace(" ", "+")

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

        return render(request, 'client_onboard_pay.html', {
            'plan': plan,
            'error': "Unknown plan type."
        })

    return render(request, 'client_onboard_pay.html', {'plan': plan})


@csrf_exempt
def payfast_ipn(request):
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
    subject = "Your kluttr Subscription is Confirmed ✅"
    html_content = render_to_string(
        'email_confirm.html', {'plan_name': plan_name})
    email = EmailMessage(subject, html_content, to=[user_email])
    email.content_subtype = "html"  # Important
    email.send()


@login_required
def schedule_pickup(request):
    client = request.user.client

    # 🧩 Ensure client has selected a plan first
    if not client.selected_plan:
        messages.error(
            request, "Please select a plan before scheduling a pickup.")
        return redirect('clients:select_plan')

    today = date.today()
    current_month = date(today.year, today.month, 1)

    # ✅ Get or create the PickupPlan properly
    pickup_plan, created = PickupPlan.objects.get_or_create(
        client=client,
        month=current_month,
        defaults={
            'plan': client.selected_plan,
            'pickups_done': 0
        }
    )

    # 🧾 Handle form submission
    if request.method == 'POST':
        print('POST data:', request.POST)  # Debugging line
        form = PickUpScheduling(
            request.POST, request.FILES, pickup_plan=pickup_plan)
        if form.is_valid():
            pickup = form.save()
            # ✅ Update pickup count
            pickup_plan.pickups_done += 1
            pickup_plan.save()

            messages.success(request, "Pickup scheduled successfully!")
            return redirect('clients:success')
        else:
            print('Form errors:', form.errors)
    else:
        form = PickUpScheduling(pickup_plan=pickup_plan)

    return render(request, 'client_onboard_schedule.html', {
        'form': form,
        'selected_plan': pickup_plan.plan,
        'pickup_plan': pickup_plan
    })


def success(request):
    return render(request, 'success.html')


def business_dashboard(request):

    return render(request, 'business_dashboard.html')


def manage_plan(request):
    return render(request, 'manage_plan.html')
