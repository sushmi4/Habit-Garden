"""
Habits App - Utility Functions

This module contains helper functions for habit tracking,
including streak calculation logic.
"""

from datetime import date, timedelta
from .models import HabitCompletion


def calculate_streak(habit):
    """
    Calculate the current streak for a habit.
    
    A streak is the number of consecutive days a habit has been completed,
    counting backwards from today (or yesterday if today isn't done yet).
    
    Args:
        habit: The Habit object to calculate streak for
        
    Returns:
        int: Number of consecutive days completed
        
    Example:
        If a user completed their habit on Mon, Tue, Wed, and today is Thu,
        the streak would be 3 (if Thu isn't done yet) or 4 (if Thu is done).
    """
    today = date.today()
    streak = 0
    current_date = today
    
    # Check if today is completed
    today_completed = HabitCompletion.objects.filter(
        habit=habit,
        date=today
    ).exists()
    
    # If today isn't completed, start checking from yesterday
    if not today_completed:
        current_date = today - timedelta(days=1)
    
    # Count consecutive completed days
    while True:
        if HabitCompletion.objects.filter(
            habit=habit,
            date=current_date
        ).exists():
            streak += 1
            current_date -= timedelta(days=1)
        else:
            # Streak broken
            break
    
    return streak


def get_best_streak(habit):
    """
    Calculate the best (longest) streak ever achieved for a habit.
    
    Args:
        habit: The Habit object to calculate best streak for
        
    Returns:
        int: Longest streak ever achieved
    """
    # Get all completion dates for this habit, ordered oldest first
    completions = HabitCompletion.objects.filter(
        habit=habit
    ).order_by('date').values_list('date', flat=True)
    
    if not completions:
        return 0
    
    best_streak = 0
    current_streak = 1
    
    # Compare consecutive dates
    for i in range(1, len(completions)):
        # Check if this completion is exactly one day after the previous
        if completions[i] - completions[i-1] == timedelta(days=1):
            current_streak += 1
        else:
            # Streak broken, update best if current is better
            best_streak = max(best_streak, current_streak)
            current_streak = 1
    
    # Don't forget to check the last streak
    best_streak = max(best_streak, current_streak)
    
    return best_streak


def get_completion_dates(habit, year=None, month=None):
    """
    Get all completion dates for a habit in a given month.
    
    Useful for displaying a calendar view of completions.
    
    Args:
        habit: The Habit object
        year: Year to check (defaults to current year)
        month: Month to check (defaults to current month)
        
    Returns:
        list: List of date objects when the habit was completed
    """
    today = date.today()
    
    if year is None:
        year = today.year
    if month is None:
        month = today.month
    
    # Filter completions for the specified month
    completions = HabitCompletion.objects.filter(
        habit=habit,
        date__year=year,
        date__month=month
    ).values_list('date', flat=True)
    
    return list(completions)


def get_habit_stats(habit):
    """
    Get comprehensive statistics for a habit.
    
    Args:
        habit: The Habit object
        
    Returns:
        dict: Dictionary containing various statistics
    """
    today = date.today()
    
    # Calculate all stats
    streak = calculate_streak(habit)
    best_streak = get_best_streak(habit)
    total_completions = habit.completions.count()
    
    # Calculate completion rate for the last 30 days
    thirty_days_ago = today - timedelta(days=30)
    recent_completions = HabitCompletion.objects.filter(
        habit=habit,
        date__gte=thirty_days_ago
    ).count()
    completion_rate = (recent_completions / 30) * 100 if thirty_days_ago else 0
    
    return {
        'current_streak': streak,
        'best_streak': best_streak,
        'total_completions': total_completions,
        'completion_rate': round(completion_rate, 1),
    }
