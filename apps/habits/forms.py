"""
Habits App - Forms

This module defines forms for creating and editing habits.
"""

from django import forms
from django.utils import timezone
from .models import Habit, HabitCompletion


class HabitForm(forms.ModelForm):
    """
    Form for creating and editing habits.
    
    Uses Django's ModelForm to automatically generate form fields
    from the Habit model.
    """
    
    class Meta:
        """Meta class defines which model and fields to use."""
        model = Habit
        fields = ['name', 'description', 'frequency']
        
        # Custom widget attributes for better styling
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g., Drink water, Exercise, Read',
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Optional: Why is this habit important to you?',
                'rows': 3,
                'class': 'form-input'
            }),
            'frequency': forms.Select(attrs={
                'class': 'form-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form.
        
        The user argument is needed to associate the habit with the correct user.
        We remove it before passing to ModelForm since it's not a form field.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        """
        Save the habit, associating it with the current user.
        
        This override ensures the habit is linked to the user who created it.
        """
        habit = super().save(commit=False)
        
        # Associate with the user if this is a new habit
        if self.user and not habit.pk:
            habit.user = self.user
        
        if commit:
            habit.save()
        
        return habit


class HabitCompletionForm(forms.Form):
    """
    Form for marking a habit as complete for a specific date.
    
    This is a simple form - it just needs the date field.
    The habit is passed separately since it's not a user-editable field.
    """
    
    date = forms.DateField(
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Any notes about today\'s completion?',
            'rows': 2,
            'class': 'form-input'
        })
    )
