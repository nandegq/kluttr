
from django.shortcuts import render
from clients.models import Pickups, Client
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render, get_object_or_404
from datetime import date
import plotly.express as px
import pandas as pd


# Create your views here.

@login_required
def client_dashboard(request):
    # Get the logged-in client
    client = request.user.client

    # Get all pickups linked to this client's pickup plans
    pickups = Pickups.objects.filter(pickup_plan__client=client)

    # Convert the queryset into a DataFrame for easy calculations
    df = pd.DataFrame(list(pickups.values(
        'waste_type',
        'scheduled_date',
        'weight'
    )))

    # Handle case where client has no pickups yet
    if df.empty:
        context = {
            'total_waste': 0,
            'waste_breakdown': {},
            'monthly_totals': {},
            'co2_saved': 0
        }
        return render(request, 'client_dashboard.html', context)

    # --- CALCULATIONS ---
    # 1️⃣ Total waste collected
    total_waste = df['weight'].sum()

    # 2️⃣ Waste breakdown by type
    waste_breakdown = df.groupby('waste_type')['weight'].sum().to_dict()

    # 3️⃣ Monthly totals
    df['scheduled_date'] = pd.to_datetime(
        df['scheduled_date'], errors='coerce')
    df['month'] = df['scheduled_date'].dt.strftime('%B %Y')
    monthly_totals = df.groupby('month')['weight'].sum().to_dict()

    # 4️⃣ CO₂ saved (example: 1kg waste = 1.8kg CO₂ saved)
    co2_saved = total_waste * 1.8

    # --- CONTEXT ---
    context = {
        'total_waste': total_waste,
        'waste_breakdown': waste_breakdown,
        'monthly_totals': monthly_totals,
        'co2_saved': co2_saved
    }

    return render(request, 'client_dashboard.html', context)


def household_analytics(request):
    return render(request, 'household_analytics.html')


def upcycler_analytics(request):
    return render(request, 'upcycler_analytics.html')
