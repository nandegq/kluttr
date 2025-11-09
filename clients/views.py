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

# Create your views here.


def landing(request):
    return render(request, 'landing.html')


def business_onboarding(request):
    profile = request.user.profile

    if request.method == 'POST':

        profile.onboarding_complete = True
        profile.save()
        return redirect('clients:business_dashboard')

    return render(request, 'client_onboard_plan.html')


@login_required
def select_plan(request):
    plans = Plans.objects.all()
    if request.method == 'POST':

        selected_plan_id = request.POST.get('plans')
        selected_plan = Plans.objects.get(id=selected_plan_id)
        request.user.profile.plan = selected_plan
        request.user.profile.save()
        return redirect('clients:payment_info')
    return render(request, 'client_onboard_plan.html', {'plans': plans})


@login_required
def payment_info(request):
    user = request.user
    client = user.client
    plan = client.selected_plan

    if not plan:
        return redirect('clients:select_plan')

    if request.method == 'POST':
        data = {'merchant_id': settings.PAYFAST_MERCHANT_ID,
                'merchant_key': settings.PAYFAST_MERCHANT_KEY,
                'amount': str(plan.price),
                'item_name': plan.name,
                'return_url': request.build_absolute_uri('/clients/schedule/'),
                'cancel_url': request.build_absolute_uri('/clients/pay/'),
                'notify_url': 'http://127.0.0.1:8000/payfast-ipn/',
                'custom_str1': request.user.email,
                'custom_str2': plan.name,
                # Subscription fields
                'subscription_type': 1,           # 1 = subscription
                'recurring_amount': str(plan.price),
                'frequency': 3,                   # 3 = monthly
                'cycles': 0,                      # 0 = indefinite
                'billing_date': date.today().isoformat(),  # first billing date (today)
                }
        query_string = urlencode(data)
        payfast_url = f'https://sandbox.payfast.co.za/eng/process?{query_string}'
        return redirect(payfast_url)

    return render(request, 'client_onboard_pay.html')


@csrf_exempt
def payfast_ipn(request):
    if request.method == 'POST':
        # Step 1: Grab the data PayFast sent
        data = request.POST.copy()

        # Step 2: Verify the payment with PayFast
        verify_url = 'https://sandbox.payfast.co.za/eng/process'  # sandbox
        verify_response = requests.post(verify_url, data=data)
        if verify_response.text == 'VALID':
            # Payment is verified
            # You pass this in 'custom' field in payment
            user_email = data.get('custom_str1')
            plan_name = data.get('custom_str2')
            send_confirmation_email_html(user_email, plan_name)
            return HttpResponse('OK')
        else:
            return HttpResponse('INVALID')
    return HttpResponse('Method not allowed', status=405)


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
