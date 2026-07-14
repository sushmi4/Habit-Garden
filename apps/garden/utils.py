"""
Garden App - Utility Functions

This module contains helper functions for managing the garden,
including plant creation and growth updates.
"""

from django.utils import timezone
from datetime import timedelta
from .models import Plant
from apps.habits.utils import calculate_streak


def create_plant_for_habit(habit):
    """
    Create a new plant when a new habit is created.
    
    This function is called automatically when a new habit is created.
    It creates a plant with a random type and initial seed stage.
    
    Args:
        habit: The newly created Habit object
        
    Returns:
        Plant: The newly created Plant object
    """
    import random
    
    # Randomly select a plant type for variety
    plant_types = ['flower', 'tree', 'herb', 'succulent']
    plant_type = random.choice(plant_types)
    
    # Create the plant
    plant = Plant.objects.create(
        user=habit.user,
        habit=habit,
        plant_type=plant_type,
        stage='seed',
        health=100,
        streak_count=0,
        best_streak=0,
    )
    
    return plant


def update_all_plants(user):
    """
    Update all plants for a user based on their current streaks.
    
    This function should be called periodically (e.g., daily) to:
    1. Update plant growth stages based on streaks
    2. Reduce health for plants whose habits were missed
    
    Args:
        user: The User object whose plants to update
    """
    from apps.habits.models import Habit
    
    # Get all active habits for the user
    habits = Habit.objects.filter(user=user, is_active=True)
    
    for habit in habits:
        # Get or create the plant for this habit
        plant, created = Plant.objects.get_or_create(
            habit=habit,
            defaults={
                'user': user,
                'plant_type': 'flower',
                'stage': 'seed',
                'health': 100,
            }
        )
        
        # Calculate current streak
        streak = calculate_streak(habit)
        
        # Update plant growth
        plant.update_growth(streak)
        
        # If streak is 0, reduce health
        if streak == 0:
            plant.dry_out(1)


def get_garden_stats(user):
    """
    Get statistics for the user's garden.
    
    Args:
        user: The User object
        
    Returns:
        dict: Garden statistics
    """
    plants = Plant.objects.filter(user=user)
    
    # Count plants by stage
    stages = {}
    for stage_choice in Plant.STAGE_CHOICES:
        stage_name = stage_choice[0]
        stages[stage_name] = plants.filter(stage=stage_name).count()
    
    # Calculate average health
    if plants.exists():
        avg_health = sum(p.health for p in plants) / plants.count()
    else:
        avg_health = 0
    
    return {
        'total_plants': plants.count(),
        'stages': stages,
        'average_health': round(avg_health, 1),
        'blooming_count': stages.get('blooming', 0),
    }
