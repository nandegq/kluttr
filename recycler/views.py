from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Collector
from household.models import CustomerPickups  # adjust import if needed


def upcycler_onboard(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.onboarding_complete = True
        profile.save()
        return redirect('recycler:upcycler_dashboard')
    return render(request, 'upcycler_dashboard.html')


@login_required
def available_jobs(request):
    collector = request.user.collector
    jobs = CustomerPickups.objects.filter(customer_pickup_completed='Pending')
    return render(request, 'available_jobs.html', {'jobs': jobs})


@login_required
def accept_job(request, pickup_id):
    collector = request.user.collector
    pickup = get_object_or_404(CustomerPickups, id=pickup_id)

    if pickup.status == 'Pending':
        pickup.customer_collected_by = collector
        pickup.customer_pickup_completed = 'Assigned'
        pickup.save()

    return redirect('upcycler_dashboard')


@login_required
def mark_as_completed(request, pickup_id):
    pickup = get_object_or_404(CustomerPickups, id=pickup_id)

    if pickup.customer_pickup_completed == 'Assigned':
        pickup.customer_pickup_completed = 'Completed'
        pickup.save()

    return redirect('upcycler_dashboard')


@login_required
def upcycler_dashboard(request):
    collector = request.user.collector
    assigned = CustomerPickups.objects.filter(
        customer_collected_by=collector, customer_pickup_completed='Assigned')
    completed = CustomerPickups.objects.filter(
        customer_collected_by=collector, customer_pickup_completed='Completed')

    return render(request, 'upcycler_dashboard.html', {
        'assigned': assigned,
        'completed': completed,
    })


@login_required
def upcycler_info(request):
    collector = request.user.collector
    pickups = CustomerPickups.objects.filter(customer_collected_by=collector)
    return render(request, 'upcycler_info.html', {'pickups': pickups})


@login_required
def upcycler_earnings(request):
    collector = request.user.collector
    completed_pickups = CustomerPickups.objects.filter(customer_collected_by=collector,
                                                       customer_pickup_completed='Completed')
    return render(request, 'upcycler_earnings.html', {'completed_pickups': completed_pickups})
