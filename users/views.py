from django.shortcuts import render, redirect
from django.http import HttpResponse
from clients.models import Client
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from household.models import Customer
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile
from recycler.models import Collector
from django.db import transaction
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

            try:
                profile = Profile.objects.create(
                    user=user, user_type=user_type)

                with transaction.atomic():
                    print(
                        f"Creating user: {user.username}, type: {user_type}, profile ID:{profile}")

                    if user_type == 'business':
                        Client.objects.create(user=user)
                        print("Created Client profile")
                    elif user_type == 'household':
                        Customer.objects.create(user=user)
                        print("Created Customer profile")
                    elif user_type == 'recycler':
                        Collector.objects.create(user=user)
                        print("Created Collector profile")
                    else:
                        print(
                            f"No profile created — user_type = {user_type}")

            except Exception as e:
                print(f"Failed to create profile for {user.username}: {e}")
                import traceback
                traceback.print_exc()  # show full traceback
                user.delete()
                print("Registration rolled back")

            messages.success(
                request, "Registration successful! You can now log in.")
            return redirect("login")

        else:
            print("Registration form errors:", form.errors)
            messages.error(request, "Invalid data submitted.")
    else:
        form = RegistrationForm()

    return render(request, "users/register.html", {"form": form})


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
    logout(request)
    return redirect('users:login')
