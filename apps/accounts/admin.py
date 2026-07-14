"""
Accounts App - Admin Configuration

This module registers the Profile model with Django's admin interface,
allowing administrators to manage user profiles through the admin panel.
"""

from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Profile model.
    
    Customizes how profiles are displayed and managed in the admin interface.
    """
    
    # Columns to display in the list view
    list_display = ('user', 'garden_name', 'total_xp', 'created_at')
    
    # Allow filtering by these fields
    list_filter = ('created_at',)
    
    # Allow searching by these fields
    search_fields = ('user__username', 'user__email', 'garden_name')
    
    # Read-only fields (can't be edited)
    readonly_fields = ('created_at', 'updated_at')
    
    # Fieldsets organize the edit form into sections
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'garden_name')
        }),
        ('Statistics', {
            'fields': ('total_xp',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Collapsible section
        }),
    )
