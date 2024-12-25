from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from .models import GymProfile, GymLocation
from .forms_gym import GymProfileForm, GymLocationForm, BusinessHoursForm, SocialMediaForm

def is_gym_owner(user):
    return user.is_authenticated and user.is_gym_owner

@login_required
@user_passes_test(is_gym_owner)
def gym_profile_setup(request):
    try:
        gym_profile = request.user.gym_profile
        messages.info(request, 'You already have a gym profile.')
        return redirect('gym_dashboard')
    except GymProfile.DoesNotExist:
        if request.method == 'POST':
            form = GymProfileForm(request.POST, request.FILES)
            if form.is_valid():
                gym_profile = form.save(commit=False)
                gym_profile.owner = request.user
                gym_profile.save()
                messages.success(request, 'Gym profile created successfully!')
                return redirect('gym_location_setup')
        else:
            form = GymProfileForm()
        
        return render(request, 'accounts/gym/profile_setup.html', {'form': form})

@login_required
@user_passes_test(is_gym_owner)
def gym_location_setup(request):
    gym_profile = get_object_or_404(GymProfile, owner=request.user)
    
    if request.method == 'POST':
        form = GymLocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.gym = gym_profile
            location.save()
            messages.success(request, 'Gym location added successfully!')
            return redirect('gym_hours_setup')
    else:
        form = GymLocationForm()
    
    return render(request, 'accounts/gym/location_setup.html', {'form': form})

@login_required
@user_passes_test(is_gym_owner)
def gym_hours_setup(request):
    gym_profile = get_object_or_404(GymProfile, owner=request.user)
    
    if request.method == 'POST':
        form = BusinessHoursForm(request.POST)
        if form.is_valid():
            hours = {}
            for day, _ in form.DAYS_OF_WEEK:
                if form.cleaned_data[f'{day}_closed']:
                    hours[day] = {'closed': True}
                else:
                    hours[day] = {
                        'open': form.cleaned_data[f'{day}_open'].strftime('%H:%M'),
                        'close': form.cleaned_data[f'{day}_close'].strftime('%H:%M'),
                        'closed': False
                    }
            
            gym_profile.business_hours = hours
            gym_profile.save()
            messages.success(request, 'Business hours saved successfully!')
            return redirect('gym_social_setup')
    else:
        initial = {}
        if gym_profile.business_hours:
            for day, hours in gym_profile.business_hours.items():
                if hours.get('closed'):
                    initial[f'{day}_closed'] = True
                else:
                    initial[f'{day}_open'] = hours.get('open')
                    initial[f'{day}_close'] = hours.get('close')
        form = BusinessHoursForm(initial=initial)
    
    return render(request, 'accounts/gym/hours_setup.html', {'form': form})

@login_required
@user_passes_test(is_gym_owner)
def gym_social_setup(request):
    gym_profile = get_object_or_404(GymProfile, owner=request.user)
    
    if request.method == 'POST':
        form = SocialMediaForm(request.POST)
        if form.is_valid():
            social_media = {
                platform: url
                for platform, url in form.cleaned_data.items()
                if url  # Only include platforms with non-empty URLs
            }
            
            gym_profile.social_media = social_media
            gym_profile.save()
            
            # Mark onboarding as completed
            request.user.onboarding_completed = True
            request.user.save()
            
            messages.success(request, 'Social media links saved successfully! Onboarding completed.')
            return redirect('gym_dashboard')
    else:
        initial = gym_profile.social_media if gym_profile.social_media else {}
        form = SocialMediaForm(initial=initial)
    
    return render(request, 'accounts/gym/social_setup.html', {'form': form})

@login_required
@user_passes_test(is_gym_owner)
def gym_dashboard(request):
    gym_profile = get_object_or_404(GymProfile, owner=request.user)
    locations = gym_profile.locations.all()
    context = {
        'gym_profile': gym_profile,
        'locations': locations,
    }
    return render(request, 'accounts/gym/dashboard.html', context)