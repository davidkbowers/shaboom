from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from studio.models import StudioProfile, StudioMembership
from .forms import StudioProfileForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.urls import reverse

class StudioAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to ensure user is a studio owner and has an associated studio profile."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_studio_owner
    
    def dispatch(self, request, *args, **kwargs):
        # First, ensure user is authenticated and passes the test_func
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not self.test_func():
            return self.handle_no_permission()
        
        # Check if user has a studio profile
        if not hasattr(request.user, 'studio_profile') or request.user.studio_profile is None:
            # Redirect to profile setup with a message
            return redirect(reverse('studio:studio_profile_setup')) # Ensure namespace for reverse
            
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # At this point, we're sure studio profile exists due to dispatch check
        context['studio'] = self.request.user.studio_profile
        return context

class StudioDashboardView(StudioAccessMixin, TemplateView):
    """Main dashboard view for studio owners."""
    template_name = 'studio/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'dashboard'
        # If 'active_members' is needed for 'studio/dashboard.html', add it here:
        # studio_profile = self.request.user.studio_profile
        # context['active_members'] = StudioMembership.objects.filter(
        #     studio=studio_profile,
        #     status='active'
        # ).count()
        return context

def is_studio_owner(user):
    return user.is_authenticated and user.is_studio_owner

@login_required
def studio_profile_setup(request):
    try:
        # Try to get existing profile
        studio_profile = StudioProfile.objects.get(owner=request.user)
    except StudioProfile.DoesNotExist:
        # Create a new profile if one doesn't exist
        studio_profile = StudioProfile.objects.create(owner=request.user)

    if request.method == 'POST':
        form = StudioProfileForm(request.POST, request.FILES, instance=studio_profile)
        if form.is_valid():
            try:
                with transaction.atomic():
                    profile = form.save(commit=False)
                    profile.owner = request.user
                    
                    # Handle logo upload
                    if 'logo' in request.FILES:
                        profile.logo = request.FILES['logo']
                    
                    profile.save()
                    messages.success(request, 'Studio profile updated successfully!')
                    return redirect('studio:dashboard')
            except Exception as e:
                messages.error(request, f'Error saving profile: {str(e)}')
    else:
        form = StudioProfileForm(instance=studio_profile)

    return render(request, 'accounts/studio/profile_setup.html', {
        'form': form,
        'studio_profile': studio_profile
    })

@login_required
def studio_admin_dashboard(request):
    studio_profile = get_object_or_404(StudioProfile, owner=request.user)
    memberships = StudioMembership.objects.filter(studio=studio_profile)
    return render(request, 'accounts/studio/admin_dashboard.html', {
        'studio_profile': studio_profile,
        'memberships': memberships
    })

@login_required
@user_passes_test(is_studio_owner)
def approve_membership(request, membership_id):
    membership = get_object_or_404(StudioMembership, id=membership_id, studio__owner=request.user)
    membership.status = 'active'
    membership.save()
    messages.success(request, 'Membership approved successfully!')
    return redirect('accounts:studio:studio_admin_dashboard')

@login_required
@user_passes_test(is_studio_owner)
def deactivate_membership(request, membership_id):
    membership = get_object_or_404(StudioMembership, id=membership_id, studio__owner=request.user)
    membership.status = 'inactive'
    membership.save()
    messages.success(request, 'Membership deactivated successfully!')
    return redirect('accounts:studio:studio_admin_dashboard')

@login_required
@user_passes_test(is_studio_owner)
def activate_membership(request, membership_id):
    membership = get_object_or_404(StudioMembership, id=membership_id, studio__owner=request.user)
    membership.status = 'active'
    membership.save()
    messages.success(request, 'Membership activated successfully!')
    return redirect('accounts:studio:studio_admin_dashboard')

@login_required
def toggle_public_videos(request):
    if request.method == 'POST':
        studio_profile = get_object_or_404(StudioProfile, owner=request.user)
        studio_profile.allow_public_videos = not studio_profile.allow_public_videos
        studio_profile.save()
        messages.success(request, 'Public video access has been updated.')
    return redirect('studio:dashboard')

@login_required
def toggle_public_signup(request):
    if request.method == 'POST':
        studio_profile = get_object_or_404(StudioProfile, owner=request.user)
        studio_profile.allow_public_signup = not studio_profile.allow_public_signup
        studio_profile.save()
        messages.success(request, 'Public signup access has been updated.')
    return redirect('studio:dashboard')
