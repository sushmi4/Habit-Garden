"""
Accounts App - Forms

This module defines forms for user registration and profile management.
Forms handle input validation and data cleaning.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class UserRegistrationForm(UserCreationForm):
    """
    Form for new user registration.
    
    Extends Django's built-in UserCreationForm to include email field.
    The UserCreationForm already handles username, password1, and password2.
    """
    
    # Additional field not included in UserCreationForm
    email = forms.EmailField(
        required=True,
        help_text="Required. We'll use this for password recovery.",
        widget=forms.EmailInput(attrs={
            'placeholder': 'your.email@example.com'
        })
    )
    
    class Meta:
        """Meta class defines which model and fields to use."""
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the form with custom placeholders and help text.
        
        This method customizes the appearance of form fields.
        """
        super().__init__(*args, **kwargs)
        
        # Add placeholders and help text to fields
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Choose a username'
        })
        self.fields['username'].help_text = (
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        )
        
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Create a password'
        })
        self.fields['password1'].help_text = (
            "Your password must contain at least 8 characters."
        )
        
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password'
        })
        self.fields['password2'].help_text = (
            "Enter the same password as before, for verification."
        )
    
    def clean_email(self):
        """
        Validate that the email is unique.
        
        This method is called during form validation to ensure
        no two users have the same email address.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "A user with this email already exists."
            )
        return email


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating user information (email, username).
    
    Uses ModelForm to automatically generate form fields from the User model.
    """
    
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email address'
        })


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating profile information (garden name).
    
    This form handles the Profile-specific fields.
    """
    
    class Meta:
        model = Profile
        fields = ['garden_name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['garden_name'].widget.attrs.update({
            'placeholder': 'My Garden'
        })
