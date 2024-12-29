from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomPasswordChangeForm, CustomAuthenticationForm
from .models import GymProfile  # Import GymProfile model

# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.user_type == 'owner':
                return redirect('gym_profile_setup')
            return redirect('marketing:landing')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.user_type == 'owner':
                # Check if gym owner has a profile
                try:
                    user.gym_profile
                    return redirect('gym_dashboard')
                except GymProfile.DoesNotExist:
                    return redirect('gym_profile_setup')
            return redirect('marketing:landing')
    else:
        form = CustomAuthenticationForm(request)
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('home')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'accounts/password_change.html', {'form': form})
