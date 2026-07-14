"""
URL configuration for Habit Garden project.

This is the main URL configuration that routes requests to the appropriate apps.
Each app has its own urls.py file for organization.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # Home page (landing page)
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    
    # Include app-specific URL configurations
    # Each app handles its own routing
    path('accounts/', include('apps.accounts.urls')),  # Authentication
    path('habits/', include('apps.habits.urls')),      # Habit tracking
    path('garden/', include('apps.garden.urls')),      # Garden visualization
]
