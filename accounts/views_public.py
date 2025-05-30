from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponseRedirect
from django.contrib import messages, auth
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from studio.models import StudioProfile, StudioMembership
from .forms import CustomUserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
import logging
# Note: reverse_lazy was already imported, ensure no duplication if this edit is applied after a previous one that also added it.

User = get_user_model()

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('public:login')
    template_name = 'accounts/public/signup_generic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_plan'] = self.request.session.get('selected_plan')
        return context

    def get(self, request, *args, **kwargs):
        logger = logging.getLogger(__name__)
        logger.warning(f"SignUpView GET - User authenticated: {request.user.is_authenticated}")
        logger.warning(f"SignUpView GET - Session data: {request.session.items()}")
        
        if request.user.is_authenticated:
            # If user is already logged in, redirect to their dashboard
            return redirect('studio:dashboard')
            
        selected_plan = request.session.get('selected_plan')
        logger.warning(f"SignUpView GET - Selected plan from session: {selected_plan}")
            
        if not selected_plan:
            messages.warning(request, 'Please select a plan before signing up.')
            return redirect(reverse_lazy('public:public_accounts:plan_selection'))
            
        # Make sure the plan is passed to the context
        context = self.get_context_data(**kwargs)
        context['selected_plan'] = selected_plan
        return self.render_to_response(context)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in after signup
        auth_login(self.request, self.object)
        # Clear the selected plan from the session
        if 'selected_plan' in self.request.session:
            del self.request.session['selected_plan']
        return response

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
    # If user is already authenticated, redirect to appropriate profile
    if request.user.is_authenticated:
        if hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
            return redirect('accounts:profile')
        return redirect('public:profile')
    
    # Handle form submission
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            next_url = request.POST.get('next', request.GET.get('next', ''))
            if next_url:
                return redirect(next_url)
            # Default redirect after login
            if hasattr(request, 'tenant') and request.tenant.schema_name != 'public':
                return redirect('accounts:profile')
            return redirect('public:profile')
    else:
        form = AuthenticationForm()
        next_url = request.GET.get('next', '')
    
    return render(request, 'accounts/public/login.html', {
        'form': form,
        'next': next_url
    })

def user_logout(request):
    auth_logout(request)
    return redirect('public:landing')


def profile_view(request):
    """View for displaying and managing user profile (public version)"""
    if not request.user.is_authenticated:
        return redirect('public:login')
    return render(request, 'accounts/public/profile.html')

# Password reset is now handled by Django's built-in views in public_urls.py
