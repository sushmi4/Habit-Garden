"""
Garden App - Admin Configuration

This module registers the Plant model with Django's admin interface.
"""

from django.contrib import admin
from .models import Plant


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Plant model.
    """
    
    list_display = ('habit', 'user', 'plant_type', 'stage', 'health', 'streak_count')
    list_filter = ('stage', 'plant_type', 'created_at')
    search_fields = ('habit__name', 'user__username')
    readonly_fields = ('created_at', 'last_watered')
    
    fieldsets = (
        ('Plant Information', {
            'fields': ('user', 'habit', 'plant_type', 'stage')
        }),
        ('Health & Growth', {
            'fields': ('health', 'streak_count', 'best_streak')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_watered'),
            'classes': ('collapse',)
        }),
    )
