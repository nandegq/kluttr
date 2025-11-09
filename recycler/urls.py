from django.urls import path
from . import views

app_name = 'recycler'
urlpatterns = [path('dashboard/', views.upcycler_dashboard, name='upcycler_dashboard'),
               path('info/', views.upcycler_info, name='upcycler_info'),
               path('earnings/', views.upcycler_earnings,
                    name='upcycler_earnings'),
               path('jobs/', views.available_jobs, name='available_jobs'),
               path('onboard/', views.upcycler_onboard, name='upcycler_onboard'),
               ]
