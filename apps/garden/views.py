"""
Garden App - Views

This module contains views for the garden visualization.
The garden shows all of the user's plants and their growth status.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Plant
from .utils import get_garden_stats
from apps.habits.utils import calculate_streak


@login_required
def garden_view(request):
    """
    Main garden view - displays all of the user's plants.
    
    This is the visual representation of the user's habit progress.
    Each plant corresponds to a habit and shows its growth stage.
    """
    # Get all plants for the current user
    plants = Plant.objects.filter(user=request.user)
    
    # Update plant stages based on current streaks
    for plant in plants:
        streak = calculate_streak(plant.habit)
        plant.update_growth(streak)
    
    # Get garden statistics
    stats = get_garden_stats(request.user)
    
    # Group plants by stage for display
    blooming_plants = plants.filter(stage='blooming')
    mature_plants = plants.filter(stage='mature')
    growing_plants = plants.filter(stage='growing')
    sprout_plants = plants.filter(stage='sprout')
    seed_plants = plants.filter(stage='seed')
    
    context = {
        'plants': plants,
        'stats': stats,
        'blooming_plants': blooming_plants,
        'mature_plants': mature_plants,
        'growing_plants': growing_plants,
        'sprout_plants': sprout_plants,
        'seed_plants': seed_plants,
    }
    
    return render(request, 'garden/garden_view.html', context)


@login_required
def plant_detail(request, pk):
    """
    View details of a specific plant.
    
    Shows detailed information about the plant including:
    - Growth stage and history
    - Health status
    - Linked habit information
    - Care tips
    """
    plant = get_object_or_404(Plant, pk=pk, user=request.user)
    
    # Calculate current streak for the linked habit
    streak = calculate_streak(plant.habit)
    
    # Get care tips based on plant status
    tips = get_care_tips(plant, streak)
    
    context = {
        'plant': plant,
        'streak': streak,
        'tips': tips,
    }
    
    return render(request, 'garden/plant_detail.html', context)


def get_care_tips(plant, streak):
    """
    Generate care tips based on plant status.
    
    Args:
        plant: The Plant object
        streak: Current streak count
        
    Returns:
        list: List of care tip strings
    """
    tips = []
    
    if streak == 0:
        tips.append("Complete your habit today to start growing!")
        tips.append("Your plant needs water - don't forget your habit!")
    elif streak < 3:
        tips.append("Great start! Keep going to help your plant sprout!")
        tips.append(f"Your plant will sprout after 3 days of consistency.")
    elif streak < 7:
        tips.append("Your plant is sprouting! Maintain your streak to help it grow.")
        tips.append(f"Only {7 - streak} more days until your plant starts growing!")
    elif streak < 14:
        tips.append("Your plant is growing nicely!")
        tips.append(f"{14 - streak} more days until it becomes mature.")
    elif streak < 30:
        tips.append("Your plant is almost mature! Keep up the great work!")
        tips.append(f"{30 - streak} more days until it blooms!")
    else:
        tips.append("Your plant is blooming! You've achieved an amazing streak!")
        tips.append("Keep maintaining this habit to keep your garden beautiful!")
    
    # Health-based tips
    if plant.health < 50:
        tips.append("Warning: Your plant's health is low. Complete your habit regularly!")
    
    return tips
