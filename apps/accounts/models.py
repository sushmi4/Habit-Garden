"""
Accounts App - Models

This module defines the Profile model that extends Django's User model
with additional fields for the Habit Garden application.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    User profile model that extends Django's built-in User model.
    
    Stores additional user information specific to Habit Garden,
    such as garden statistics and preferences.
    """
    
    # One-to-one relationship with Django's User model
    # Each user has exactly one profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,  # Delete profile when user is deleted
        related_name='profile'     # Access via user.profile
    )
    
    # Garden name - allows users to personalize their garden
    garden_name = models.CharField(
        max_length=100,
        default="My Garden",
        help_text="A personalized name for your garden"
    )
    
    # Total experience points earned (could be used for gamification later)
    total_xp = models.IntegerField(
        default=0,
        help_text="Total experience points earned from completing habits"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Set on creation
    updated_at = models.DateTimeField(auto_now=True)      # Updated on save
    
    class Meta:
        """Metadata for the Profile model."""
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
    
    def __str__(self):
        """String representation - shows the username."""
        return f"{self.user.username}'s Profile"
    
    def get_total_plants(self):
        """Get the total number of plants in this user's garden."""
        return self.user.plants.count()
    
    def get_active_habits(self):
        """Get the number of active habits this user has."""
        return self.user.habits.filter(is_active=True).count()


# ============================================
# Signals - Automatically create/update profiles
# ============================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile when a new User is created.
    
    This signal listens for the post_save signal from the User model.
    When a new user is created, it automatically creates a Profile for them.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Automatically save the Profile when the User is saved.
    
    This ensures the profile is always in sync with the user.
    """
    instance.profile.save()
