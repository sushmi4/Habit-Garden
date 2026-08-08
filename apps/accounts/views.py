"""
Accounts App - Views

This module contains views for user authentication and profile management.
Views handle HTTP requests and return responses (usually rendered templates).
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm


def register_view(request):
    """
    Handle user registration.
    
    GET: Display the registration form
    POST: Process the form data and create a new user
    
    This view uses Django's messages framework to provide feedback.
    """
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Create form instance with submitted data
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            # Save the new user (form.save() handles password hashing)
            user = form.save()
            
            # Get the username for the welcome message
            username = form.cleaned_data.get('username')
            
            # Show success message
            messages.success(
                request,
                f'Account created for {username}! You can now log in.'
            )
            
            # Redirect to login page
            return redirect('login')
    else:
        # GET request - create empty form
        form = UserRegistrationForm()
    
    # Render the registration template with the form
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    
    GET: Display the login form
    POST: Authenticate the user and log them in
    
    Uses Django's built-in authenticate() function to verify credentials.
    """
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Get username and password from form
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user (returns User object or None)
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # User is valid - log them in
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            
            # Redirect to 'next' parameter if it is a safe local URL,
            # otherwise default to the dashboard.
            next_url = request.GET.get('next', '')
            if url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('dashboard')
        else:
            # Invalid credentials
            messages.error(
                request,
                'Invalid username or password. Please try again.'
            )
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """
    Handle user logout.
    
    Only accepts POST requests to prevent CSRF-based logout.
    GET requests are redirected to the home page without logging out.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required  # This decorator requires the user to be logged in
def profile_view(request):
    """
    Display and update user profile.
    
    GET: Show the profile form with current data
    POST: Update the user and profile information
    
    The @login_required decorator redirects unauthenticated users to login page.
    """
    if request.method == 'POST':
        # Create form instances with submitted data
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            # Save both forms
            user_form.save()
            profile_form.save()
            
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        # GET request - create forms with current data
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Calculate stats for the profile page
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'total_habits': request.user.habits.count(),
        'active_habits': request.user.habits.filter(is_active=True).count(),
        'total_plants': request.user.plants.count(),
    }
    
    return render(request, 'accounts/profile.html', context)
