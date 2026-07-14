"""
Garden App - URL Configuration

This module defines the URL patterns for the garden app.
"""

from django.urls import path
from . import views

# URL patterns for the garden app
urlpatterns = [
    # Main garden view - shows all plants
    # URL: /garden/
    path('', views.garden_view, name='garden'),
    
    # Plant detail view
    # URL: /garden/plant/1/
    path('plant/<int:pk>/', views.plant_detail, name='plant_detail'),
]
