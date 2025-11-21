
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
import hashlib
from django.urls import reverse

from .models import Customer, CustomerPlans, CustomerPickups, CustomerPickupPlan
# make sure this form exists
from household.household_form import CustomerSchedulingForm
import traceback


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
            return redirect('household_payment_info')

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
            return redirect('household:household_plan')

    if not plan:
        messages.error(request, "Please select a plan first.")
        return redirect('household:household_plan')

    if request.method == 'POST':
        price = 0
        waste_size = None

        # On-demand plan pricing
        if plan.plan_name.lower() == 'on-demand':
            waste_size = request.POST.get('waste_size')
            if not waste_size:
                messages.error(request, "Please select a waste size.")
                return redirect('household:household_payment_info')

            waste_size = waste_size.lower()
            if waste_size == 'small':
                price = 99
            elif waste_size == 'medium':
                price = 149
            elif waste_size == 'large':
                price = 399
            else:
                messages.error(request, "Invalid waste size selected.")
                return redirect('household:household_payment_info')
        else:
            # Non-on-demand plans use plan price
            try:
                price = float(plan.plan_price or 0)
            except:
                price = 0

        # FREE PLAN HANDLER
        if price == 0:
            messages.success(request, "Free plan activated successfully.")
            return redirect('household:household_schedule')

        # PAYFAST PAYMENT DATA
        data = {
            "merchant_id": settings.PAYFAST_MERCHANT_ID,
            "merchant_key": settings.PAYFAST_MERCHANT_KEY,
            "amount": str(price),
            "item_name": f"{plan.plan_name}" + (f" ({waste_size})" if waste_size else ""),
            "return_url": request.build_absolute_uri(reverse('household:household_schedule')),
            "cancel_url": request.build_absolute_uri(reverse('household:household_plan')),
            "notify_url": request.build_absolute_uri(reverse('household:payfast_ipn')),
            "custom_str1": request.user.email,
            "custom_str2": plan.plan_name,
        }

        # SUBSCRIPTION LOGIC
        if plan.plan_name.lower() != "on-demand":
            data.update({
                "subscription_type": 1,
                "recurring_amount": str(plan.plan_price),
                "frequency": 3,
                "cycles": 0,
                "billing_date": date.today().isoformat(),
            })

        # Redirect to PayFast
        payfast_url = "https://sandbox.payfast.co.za/eng/process?" + \
            urlencode(data)
        return redirect(payfast_url)

    # Render payment page
    return render(request, 'household_onboard_pay.html', {
        'plan': plan,
        'on_demand': plan.plan_name.lower() == 'on-demand'
    })


# 📩 4️⃣ PayFast IPN Listener
@csrf_exempt
def household_payfast_ipn(request):
    if request.method == 'POST':
        data = request.POST.copy()

        verify_url = "https://sandbox.payfast.co.za/eng/query/validate"  # FIXED

        verify_response = requests.post(verify_url, data=data)

        if verify_response.text == "VALID":
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
