from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from .models import StudioProfile, StudioLocation, StudioMembership
from .forms_studio import StudioProfileForm, StudioLocationForm, BusinessHoursForm, SocialMediaForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def is_studio_owner(user):
    return user.is_authenticated and user.is_studio_owner

@login_required
def studio_profile_setup(request):
    if not request.user.user_type == 'owner':
        print("User is not owner, redirecting to login")
        return redirect('accounts:login')
    
    if request.method == 'POST':
        print(f"Received POST data: {request.POST}")
        form = StudioProfileForm(request.POST, request.FILES)
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            profile = form.save(commit=False)
            profile.owner = request.user
            profile.save()
            messages.success(request, 'Studio profile created successfully!')
            print("Profile created successfully, redirecting to hours setup")
            return redirect('accounts:studio_hours_setup')
    else:
        form = StudioProfileForm()
    
    context = {'form': form}
    template_name = 'accounts/studio/test_profile_setup.html' if 'test' in request.GET else 'accounts/studio/profile_setup.html'
    print(f"Rendering template: {template_name}")
    return render(request, template_name, context)

@login_required
def studio_location_setup(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    
    if request.method == 'POST':
        form = StudioLocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.studio = studio_profile
            location.save()
            messages.success(request, 'Studio location added successfully!')
            return redirect('accounts:studio_social_setup')
    else:
        form = StudioLocationForm()
    
    context = {'form': form}
    return render(request, 'accounts/studio/location_setup.html', context)

@login_required
def studio_hours_setup(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    
    if request.method == 'POST':
        form = BusinessHoursForm(request.POST)
        if form.is_valid():
            hours = {}
            for day, _ in form.DAYS_OF_WEEK:
                is_closed = form.cleaned_data.get(f'{day}_closed', False)
                if is_closed:
                    hours[day] = {'closed': True}
                else:
                    open_time = form.cleaned_data.get(f'{day}_open')
                    close_time = form.cleaned_data.get(f'{day}_close')
                    hours[day] = {
                        'open': open_time.strftime('%H:%M') if open_time else None,
                        'close': close_time.strftime('%H:%M') if close_time else None,
                        'closed': False
                    }
            
            studio_profile.business_hours = hours
            studio_profile.save()
            messages.success(request, 'Business hours saved successfully!')
            return redirect('accounts:studio_location_setup')
    else:
        initial = {}
        if studio_profile.business_hours:
            for day, hours in studio_profile.business_hours.items():
                if hours.get('closed'):
                    initial[f'{day}_closed'] = True
                else:
                    initial[f'{day}_open'] = hours.get('open')
                    initial[f'{day}_close'] = hours.get('close')
        form = BusinessHoursForm(initial=initial)
    
    context = {'form': form}
    return render(request, 'accounts/studio/hours_setup.html', context)

@login_required
def studio_social_setup(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    
    if request.method == 'POST':
        form = SocialMediaForm(request.POST, instance=studio_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Social media information updated successfully!')
            return redirect('accounts:studio_dashboard')
    else:
        form = SocialMediaForm(instance=studio_profile)
    
    context = {'form': form}
    return render(request, 'accounts/studio/social_setup.html', context)

@login_required
@user_passes_test(is_studio_owner)
def studio_dashboard(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    context = {'studio_profile': studio_profile}
    return render(request, 'accounts/studio/dashboard.html', context)

@login_required
@user_passes_test(is_studio_owner)
def studio_admin_dashboard(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    memberships = studio_profile.memberships.all().order_by('-created_at')
    
    paginator = Paginator(memberships, 10)
    page = request.GET.get('page')
    
    try:
        memberships = paginator.page(page)
    except PageNotAnInteger:
        memberships = paginator.page(1)
    except EmptyPage:
        memberships = paginator.page(paginator.num_pages)
    
    context = {
        'studio_profile': studio_profile,
        'memberships': memberships
    }
    return render(request, 'accounts/studio/admin_dashboard.html', context)

@login_required
@user_passes_test(is_studio_owner)
def approve_membership(request, membership_id):
    membership = get_object_or_404(StudioMembership, id=membership_id, studio__owner=request.user)
    membership.status = 'active'
    membership.save()
    messages.success(request, 'Membership approved successfully!')
    return redirect('accounts:studio_admin_dashboard')

@login_required
@user_passes_test(is_studio_owner)
def deactivate_membership(request, membership_id):
    membership = get_object_or_404(StudioMembership, id=membership_id, studio__owner=request.user)
    membership.status = 'inactive'
    membership.save()
    messages.success(request, 'Membership deactivated successfully!')
    return redirect('accounts:studio_admin_dashboard')

@login_required
@user_passes_test(is_studio_owner)
def activate_membership(request, membership_id):
    membership = get_object_or_404(StudioMembership, id=membership_id, studio__owner=request.user)
    membership.status = 'active'
    membership.save()
    messages.success(request, 'Membership activated successfully!')
    return redirect('accounts:studio_admin_dashboard')

@login_required
@user_passes_test(is_studio_owner)
def upload_video(request):
    if request.method == 'POST':
        # Handle video upload
        pass
    return render(request, 'accounts/studio/upload_video.html')
