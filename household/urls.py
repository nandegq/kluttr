from django.urls import path
from . import views


app_name = 'household'
urlpatterns = [
    path('plan/', views.household_plan, name='household_plan'),
    path('pay/', views.household_payment_info, name='household_payment_info'),
    path('schedule/', views.household_schedule, name='household_schedule'),
    path('confirmation/', views.household_success, name='household_success'),
    path('dashboard/', views.household_dashboard, name='household_dashboard'),
    path('pay-ipn/', views.household_payfast_ipn, name='household_payfast_ipn'),
    path('manage_plan/', views.household_manage_plan,
         name='household_manage_plan'),]
