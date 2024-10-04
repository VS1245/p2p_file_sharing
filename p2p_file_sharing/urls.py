from django.contrib import admin
from django.urls import path
from users import views as user_views
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('dashboard/', user_views.dashboard, name='dashboard'), 
]
