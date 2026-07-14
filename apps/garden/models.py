"""
Garden App - Models

This module defines the Plant model that represents a plant in the user's garden.
Each plant is tied to a habit and grows based on the user's consistency.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Plant(models.Model):
    """
    Represents a plant in the user's garden.
    
    Each plant is linked to a habit. As the user maintains their habit streak,
    the plant grows through different stages and maintains its health.
    """
    
    # Plant type choices - determines the visual appearance
    PLANT_TYPES = [
        ('flower', 'Flower'),
        ('tree', 'Tree'),
        ('herb', 'Herb'),
        ('succulent', 'Succulent'),
    ]
    
    # Growth stage choices - the plant progresses through these
    STAGE_CHOICES = [
        ('seed', 'Seed'),
        ('sprout', 'Sprout'),
        ('growing', 'Growing'),
        ('mature', 'Mature'),
        ('blooming', 'Blooming'),
    ]
    
    # Foreign key to User - each plant belongs to a user
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='plants'  # Access via user.plants.all()
    )
    
    # One-to-one link to Habit - each habit has one plant
    habit = models.OneToOneField(
        'habits.Habit',
        on_delete=models.CASCADE,
        related_name='plant'  # Access via habit.plant
    )
    
    # Plant characteristics
    plant_type = models.CharField(
        max_length=20,
        choices=PLANT_TYPES,
        default='flower',
        help_text="The type of plant (affects visual appearance)"
    )
    
    stage = models.CharField(
        max_length=20,
        choices=STAGE_CHOICES,
        default='seed',
        help_text="Current growth stage"
    )
    
    # Health system (0-100)
    health = models.IntegerField(
        default=100,
        help_text="Plant health (0-100). Decreases when habits are missed."
    )
    
    # Streak tracking
    streak_count = models.IntegerField(
        default=0,
        help_text="Current streak count"
    )
    
    best_streak = models.IntegerField(
        default=0,
        help_text="Best streak ever achieved"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_watered = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the plant was last 'watered' (habit completed)"
    )
    
    class Meta:
        """Metadata for the Plant model."""
        ordering = ['-created_at']
        verbose_name = 'Plant'
        verbose_name_plural = 'Plants'
    
    def __str__(self):
        """String representation - shows plant type and stage."""
        return f"{self.get_plant_type_display()} ({self.get_stage_display()})"
    
    def update_growth(self, streak):
        """
        Update the plant's growth stage based on the current streak.
        
        Growth stages:
        - Seed: 0-2 days streak
        - Sprout: 3-6 days streak
        - Growing: 7-13 days streak
        - Mature: 14-29 days streak
        - Blooming: 30+ days streak
        
        Args:
            streak: The current streak count from the linked habit
        """
        # Update streak records
        self.streak_count = streak
        if streak > self.best_streak:
            self.best_streak = streak
        
        # Determine new stage based on streak
        if streak >= 30:
            self.stage = 'blooming'
        elif streak >= 14:
            self.stage = 'mature'
        elif streak >= 7:
            self.stage = 'growing'
        elif streak >= 3:
            self.stage = 'sprout'
        else:
            self.stage = 'seed'
        
        self.save()
    
    def water(self):
        """
        Water the plant (called when habit is completed).
        
        This resets the health to 100 and updates the last_watered timestamp.
        """
        self.health = 100
        self.last_watered = timezone.now()
        self.save()
    
    def dry_out(self, days_missed=1):
        """
        Reduce health when habits are missed.
        
        Health decreases by 20% per day missed, minimum 0.
        
        Args:
            days_missed: Number of days the habit was missed
        """
        health_loss = days_missed * 20
        self.health = max(0, self.health - health_loss)
        self.save()
    
    def get_emoji(self):
        """
        Get an emoji representation of the plant based on its stage and type.
        
        Returns:
            str: An emoji representing the plant
        """
        emoji_map = {
            'seed': '🌱',
            'sprout': '🌿',
            'growing': {
                'flower': '🌻',
                'tree': '🌳',
                'herb': '🍃',
                'succulent': '🪴',
            },
            'mature': {
                'flower': '🌺',
                'tree': '🌲',
                'herb': '🌿',
                'succulent': '🌵',
            },
            'blooming': {
                'flower': '🌸',
                'tree': '🎄',
                'herb': '🌱',
                'succulent': '🪷',
            },
        }
        
        if self.stage in ('seed', 'sprout'):
            return emoji_map[self.stage]
        
        return emoji_map.get(self.stage, {}).get(self.plant_type, '🌱')
