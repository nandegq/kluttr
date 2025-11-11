from django.shortcuts import render, redirect
from django.http import HttpResponse
from clients.models import Client
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from household.models import Customer
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from recycler.models import Collector

# Create your views here.
# main page of app = index
# using model API to get objects from database


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            user_type = form.cleaned_data.get('user_type')

            # Create related profile automatically
            try:

                if user_type == 'business':
                    Client.objects.create(user=user)
                elif user_type == 'household':
                    Customer.objects.create(user=user)
                elif user_type == 'collector':
                    Collector.objects.create(user=user)
                print('User created', user.username, user_type)

            except Exception as e:
                print(f'Failed to create profile for {user.username}: {e}')
                user.delete()
                print('Registration incomplete: please contact support')

            messages.success(
                request, 'Registration successful! You can now log in.')
            return redirect('login')
        else:
            print('Registration errors', form.errors)
            messages.error(request, 'Invalid data submitted.')

    else:
        form = RegistrationForm()

        return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if hasattr(user, 'client'):
                    return redirect('clients:business_dashboard')
                elif hasattr(user, 'customer'):
                    return redirect('household:household_dashboard')

                elif hasattr(user, 'collector'):
                    return redirect('recycler:upcycler_dashboard')
                else:
                    return redirect('landing')

            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    return redirect('login')
