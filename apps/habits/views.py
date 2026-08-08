"""
Habits App - Views

This module contains views for habit management.
Views handle displaying habits, creating/editing them, and marking completions.
"""

from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Habit, HabitCompletion
from .forms import HabitForm
from .utils import calculate_streak, get_habit_stats, is_completed_in_period
from apps.garden.models import Plant
from apps.garden.utils import create_plant_for_habit


@login_required
@ensure_csrf_cookie
def dashboard(request):
    """
    Main dashboard showing today's habits.
    
    This is the primary view users see after logging in.
    It displays all active habits and allows marking them complete.
    """
    # Get all active habits for the current user
    habits = Habit.objects.filter(
        user=request.user,
        is_active=True
    )
    
    # Get today's date
    today = timezone.now().date()
    
    # Add completion status and streak info to each habit
    habits_with_status = []
    for habit in habits:
        # Check if completed in the current period (today for daily,
        # this week for weekly habits)
        completed_today = is_completed_in_period(habit, today)
        
        # Calculate streak
        streak = calculate_streak(habit)
        
        habits_with_status.append({
            'habit': habit,
            'completed_today': completed_today,
            'current_streak': streak,
            'streak_percent': min(streak, 100),
        })
    
    # Calculate overall stats
    total_habits = habits.count()
    completed_today = sum(1 for h in habits_with_status if h['completed_today'])
    completion_rate = (completed_today / total_habits * 100) if total_habits > 0 else 0
    ring_offset = 251.2 * (1 - completion_rate / 100)
    
    context = {
        'habits_with_status': habits_with_status,
        'total_habits': total_habits,
        'completed_today': completed_today,
        'completion_rate': round(completion_rate, 1),
        'ring_offset': round(ring_offset, 2),
        'today': timezone.now(),
    }
    
    return render(request, 'habits/dashboard.html', context)


@login_required
def habit_list(request):
    """
    Display all habits (active and inactive).
    
    Shows a complete list of the user's habits with options to
    edit, delete, or toggle their active status.
    """
    habits = Habit.objects.filter(user=request.user)
    
    # Add stats to each habit
    habits_with_stats = []
    for habit in habits:
        stats = get_habit_stats(habit)
        habits_with_stats.append({
            'habit': habit,
            'stats': stats,
        })
    
    context = {
        'habits_with_stats': habits_with_stats,
    }
    
    return render(request, 'habits/habit_list.html', context)


@login_required
def habit_create(request):
    """
    Create a new habit.
    
    GET: Display the creation form
    POST: Process the form and create the habit
    """
    if request.method == 'POST':
        form = HabitForm(request.POST, user=request.user)
        
        if form.is_valid():
            habit = form.save()
            create_plant_for_habit(habit)
            messages.success(request, f'Habit "{habit.name}" created! Start building your streak!')
            return redirect('habit_detail', pk=habit.pk)
    else:
        form = HabitForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create New Habit',
    }
    
    return render(request, 'habits/habit_form.html', context)


@login_required
def habit_detail(request, pk):
    """
    View details of a specific habit.
    
    Shows the habit's information, completion history, and statistics.
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    stats = get_habit_stats(habit)
    
    # Get recent completions
    recent_completions = HabitCompletion.objects.filter(
        habit=habit
    )[:10]  # Last 10 completions
    
    context = {
        'habit': habit,
        'stats': stats,
        'recent_completions': recent_completions,
    }
    
    return render(request, 'habits/habit_detail.html', context)


@login_required
def habit_edit(request, pk):
    """
    Edit an existing habit.
    
    GET: Display the edit form with current values
    POST: Update the habit
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = HabitForm(request.POST, instance=habit, user=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Habit "{habit.name}" updated!')
            return redirect('habit_detail', pk=habit.pk)
    else:
        form = HabitForm(instance=habit, user=request.user)
    
    context = {
        'form': form,
        'habit': habit,
        'title': 'Edit Habit',
    }
    
    return render(request, 'habits/habit_form.html', context)


@login_required
def habit_delete(request, pk):
    """
    Delete a habit.
    
    GET: Show confirmation page
    POST: Delete the habit and all its completions
    """
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    
    if request.method == 'POST':
        habit_name = habit.name
        habit.delete()
        messages.success(request, f'Habit "{habit_name}" deleted.')
        return redirect('habit_list')
    
    context = {
        'habit': habit,
    }
    
    return render(request, 'habits/habit_confirm_delete.html', context)


@ensure_csrf_cookie
def toggle_complete(request, pk):
    """
    Toggle habit completion for today (AJAX endpoint).
    
    This view is called via JavaScript when the user clicks
    the "complete" button. It returns JSON for dynamic updates.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Login required'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    habit = get_object_or_404(Habit, pk=pk, user=request.user)
    today = timezone.now().date()
    
    # Check if already completed today
    completion = HabitCompletion.objects.filter(
        habit=habit,
        date=today
    ).first()
    
    if completion:
        # Already completed - remove it (uncomplete)
        completion.delete()
        completed = False
        message = f'"{habit.name}" marked as not completed'
    else:
        # Not completed - mark it complete
        HabitCompletion.objects.create(
            habit=habit,
            date=today
        )
        completed = True
        message = f'Great job! "{habit.name}" completed!'
    
    # Calculate new streak
    streak = calculate_streak(habit)
    
    # Keep the plant in sync with the latest streak
    plant = Plant.objects.filter(habit=habit).first()
    if plant is not None:
        if completed:
            plant.water()
        plant.update_growth(streak)
    
    # Recalculate overall stats for the dashboard
    all_habits = Habit.objects.filter(user=request.user, is_active=True)
    total_habits = all_habits.count()
    completed_count = 0
    for h in all_habits:
        if is_completed_in_period(h, today):
            completed_count += 1
    completion_rate = (completed_count / total_habits * 100) if total_habits > 0 else 0
    ring_offset = 251.2 * (1 - completion_rate / 100)
    
    # Return JSON response for AJAX
    return JsonResponse({
        'success': True,
        'completed': completed,
        'streak': streak,
        'message': message,
        'completed_today': completed_count,
        'total_habits': total_habits,
        'completion_rate': round(completion_rate, 1),
        'ring_offset': round(ring_offset, 2),
    })
