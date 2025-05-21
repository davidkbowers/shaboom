from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages, auth
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import StudioProfile, StudioMembership
from .forms import CustomUserCreationForm

User = get_user_model()

def public_studio_videos(request, studio_slug):
    studio = get_object_or_404(StudioProfile, slug=studio_slug)
    
    if not studio.allow_public_videos:
        raise Http404("This page is not available")
    
    # Get all public videos for this studio
    videos = studio.videos.filter(is_public=True).order_by('-created_at')
    
    return render(request, 'accounts/public/videos.html', {
        'studio': studio,
        'videos': videos
    })

def public_studio_signup(request, studio_slug):
    studio = get_object_or_404(StudioProfile, slug=studio_slug)
    
    if not studio.allow_public_signup:
        raise Http404("This page is not available")
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a pending membership for this user
            StudioMembership.objects.create(
                studio=studio,
                member=user,
                status='pending'
            )
            messages.success(request, 'Your membership request has been submitted and is pending approval.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/public/signup.html', {
        'studio': studio,
        'form': form
    })

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.POST.get('next', request.GET.get('next', 'home'))
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    
    # Add the next parameter to the form's hidden fields
    next_url = request.GET.get('next', '')
    context = {
        'form': form,
        'next': next_url
    }
    return render(request, 'accounts/public/login.html', context)

def user_logout(request):
    auth_logout(request)
    return redirect('home')

# Password reset is now handled by Django's built-in views in public_urls.py
