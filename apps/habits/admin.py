"""
Habits App - Admin Configuration

This module registers the Habit and HabitCompletion models
with Django's admin interface.
"""

from django.contrib import admin
from .models import Habit, HabitCompletion


@admin.register(Habit)
class HabitAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Habit model.
    """
    
    list_display = ('name', 'user', 'frequency', 'is_active', 'created_at')
    list_filter = ('frequency', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Habit Information', {
            'fields': ('user', 'name', 'description', 'frequency')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(HabitCompletion)
class HabitCompletionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the HabitCompletion model.
    """
    
    list_display = ('habit', 'date', 'completed_at')
    list_filter = ('date',)
    search_fields = ('habit__name', 'notes')
    readonly_fields = ('completed_at',)
    
    fieldsets = (
        ('Completion Details', {
            'fields': ('habit', 'date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('completed_at',),
            'classes': ('collapse',)
        }),
    )
