"""
Accounts App - URL Configuration

This module defines the URL patterns for the accounts app.
Each pattern maps a URL to a specific view function.
"""

from django.urls import path
from . import views

# URL patterns for the accounts app
urlpatterns = [
    # Registration page
    # URL: /accounts/register/
    path('register/', views.register_view, name='register'),
    
    # Login page
    # URL: /accounts/login/
    path('login/', views.login_view, name='login'),
    
    # Logout (POST only for security)
    # URL: /accounts/logout/
    path('logout/', views.logout_view, name='logout'),
    
    # User profile page (requires login)
    # URL: /accounts/profile/
    path('profile/', views.profile_view, name='profile'),
]
