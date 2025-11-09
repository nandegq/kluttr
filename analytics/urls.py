from django.urls import path
from . import views

app_name = 'analytics'
urlpatterns = [path('client_dashboard/', views.client_dashboard, name='client_dashboard'),
               path('household_analytics/', views.household_analytics,
                    name='household_analytics'),
               path('upcycler_analytics/', views.upcycler_analytics,
                    name='upcycler_analytics'),
               ]
