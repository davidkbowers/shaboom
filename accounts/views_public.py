from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from .models import StudioProfile, StudioMembership
from .forms import CustomUserCreationForm

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
