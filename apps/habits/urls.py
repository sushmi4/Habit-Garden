"""
Habits App - URL Configuration

This module defines the URL patterns for the habits app.
"""

from django.urls import path
from . import views

# URL patterns for the habits app
urlpatterns = [
    # Dashboard - main page showing today's habits
    # URL: /habits/
    path('', views.dashboard, name='dashboard'),
    
    # List all habits
    # URL: /habits/list/
    path('list/', views.habit_list, name='habit_list'),
    
    # Create a new habit
    # URL: /habits/create/
    path('create/', views.habit_create, name='habit_create'),
    
    # View habit details
    # URL: /habits/1/
    path('<int:pk>/', views.habit_detail, name='habit_detail'),
    
    # Edit a habit
    # URL: /habits/1/edit/
    path('<int:pk>/edit/', views.habit_edit, name='habit_edit'),
    
    # Delete a habit
    # URL: /habits/1/delete/
    path('<int:pk>/delete/', views.habit_delete, name='habit_delete'),
    
    # Toggle habit completion (AJAX endpoint)
    # URL: /habits/1/complete/
    path('<int:pk>/complete/', views.toggle_complete, name='toggle_complete'),
]
