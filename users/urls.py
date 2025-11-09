from django.urls import path
from .import views
from django.contrib.auth import views as auth_views
# url configuration

app_name = 'users'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
]
