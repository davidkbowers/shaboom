from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomPasswordChangeForm, CustomAuthenticationForm
from .models import StudioProfile  # Import StudioProfile model

# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:studio_profile_setup')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        print(f"Received POST request: {request.POST}")
        form = CustomAuthenticationForm(request, data=request.POST)
        print(f"Form data: {request.POST}")
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            user = form.get_user()
            print(f"Authenticated user: {user.email}, type: {user.user_type}")
            login(request, user)
            if user.user_type == 'owner':
                print("User is owner, checking for profile")
                # Check if studio owner has a profile
                try:
                    user.studio_profile
                    print("Found studio profile, redirecting to dashboard")
                    return redirect('accounts:studio_dashboard')
                except StudioProfile.DoesNotExist:
                    print("No studio profile found, redirecting to setup")
                    return redirect('accounts:studio_profile_setup')
            print("User is not owner, redirecting to landing")
            return redirect('marketing:landing')
    else:
        form = CustomAuthenticationForm(request)
    
    template_name = 'accounts/test_login.html' if 'test' in request.GET else 'accounts/login.html'
    return render(request, template_name, {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('accounts:login')

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
