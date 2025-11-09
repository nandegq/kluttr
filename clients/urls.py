from django.urls import path
from . import views

app_name = 'clients'
# url configuration
urlpatterns = [
    path('', views.landing, name='landing'),
    path('plan/', views.select_plan, name='select_plan'),
    path('pay/', views.payment_info, name='payment_info'),
    path('schedule/', views.schedule_pickup, name='schedule'),
    path('confirmation/', views.success, name='success'),
    path('dashboard/', views.business_dashboard, name='business_dashboard'),
    path('pay-ipn/', views.payfast_ipn, name='payfast_ipn'),
    path('manage_plan/', views.manage_plan, name='manage_plan'),]
