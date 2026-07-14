"""
Habits App - Models

This module defines the Habit and HabitCompletion models.
These models are the core of the application - they track user habits
and record when habits are completed.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Habit(models.Model):
    """
    A habit that a user wants to track.
    
    Each habit belongs to a user and has properties like name, description,
    and frequency. Habits can be active or inactive.
    """
    
    # Choices for the frequency field
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    
    # Foreign key links this habit to a specific user
    # on_delete=CASCADE means if user is deleted, their habits are too
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits'  # Access via user.habits.all()
    )
    
    # Habit details
    name = models.CharField(
        max_length=200,
        help_text="What habit do you want to track?"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional description of your habit"
    )
    
    frequency = models.CharField(
        max_length=10,
        choices=FREQUENCY_CHOICES,
        default='daily',
        help_text="How often do you want to do this habit?"
    )
    
    # Status and timestamps
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive habits won't show in your daily dashboard"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Metadata for the Habit model."""
        ordering = ['-created_at']  # Newest habits first
        verbose_name = 'Habit'
        verbose_name_plural = 'Habits'
    
    def __str__(self):
        """String representation - shows the habit name."""
        return self.name
    
    def get_today_completed(self):
        """
        Check if this habit is completed today.
        
        Returns:
            bool: True if completed today, False otherwise
        """
        today = timezone.now().date()
        return HabitCompletion.objects.filter(
            habit=self,
            date=today
        ).exists()
    
    def get_completion_count(self):
        """Get total number of times this habit has been completed."""
        return self.completions.count()


class HabitCompletion(models.Model):
    """
    Records when a habit is completed on a specific date.
    
    Each completion is linked to a habit and has a date.
    The unique_together constraint ensures one completion per habit per day.
    """
    
    # Foreign key links to the Habit model
    habit = models.ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name='completions'  # Access via habit.completions.all()
    )
    
    # The date this habit was completed
    date = models.DateField(
        help_text="The date the habit was completed"
    )
    
    # Optional notes for this completion
    notes = models.TextField(
        blank=True,
        help_text="Any notes about this completion"
    )
    
    # Timestamp when this record was created
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Metadata for the HabitCompletion model."""
        # Ensure only one completion per habit per day
        unique_together = ('habit', 'date')
        ordering = ['-date']  # Most recent completions first
        verbose_name = 'Habit Completion'
        verbose_name_plural = 'Habit Completions'
    
    def __str__(self):
        """String representation - shows habit name and date."""
        return f"{self.habit.name} - {self.date}"
