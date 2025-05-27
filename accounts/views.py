from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from studio.models import StudioProfile

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, email=username, password=password)
        
        if user is not None:
            login(request, user)
            # Get the next URL from the session or querystring
            next_url = request.GET.get('next') or request.session.pop('next', None)
            if next_url:
                return redirect(next_url)
            
            # Redirect based on user type
            if user.is_studio_owner:  # Use the property instead of direct field check
                # Check if studio profile exists
                try:
                    studio_profile = StudioProfile.objects.get(owner=user)
                    # Profile exists, redirect to dashboard
                    return redirect('studio:dashboard')
                except StudioProfile.DoesNotExist:
                    # No profile exists, redirect to setup page using the correct namespace
                    return redirect('studio:studio_profile_setup')
            else:
                return redirect('accounts:member_dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please check your credentials and try again.')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

def register_view(request):
    # Check if user has selected a plan
    if not request.session.get('selected_plan'):
        messages.warning(request, 'Please select a plan before registering.')
        return redirect('public:plan_selection')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create the user but don't save to DB yet
            user = form.save(commit=False)
            # Set user type to owner for studio registration
            user.user_type = 'owner'
            # Now save the user
            user.save()
            
            # Create subscription based on selected plan
            selected_plan = request.session.get('selected_plan')
            # TODO: Create subscription with selected plan
            
            # Clear the selected plan from session
            request.session.pop('selected_plan', None)
            
            # Log the user in
            login(request, user)
            
            # Create an empty studio profile
            StudioProfile.objects.create(owner=user)
            
            messages.success(request, 'Registration successful! Please complete your studio profile.')
            return redirect('accounts:studio_profile_setup')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def plan_selection_view(request):
    if request.method == 'POST':
        selected_plan = request.POST.get('plan')
        if selected_plan:
            request.session['selected_plan'] = selected_plan
            messages.success(request, f'You have selected the {selected_plan} plan.')
            return redirect('public:signup')  # Using namespaced URL
        else:
            messages.error(request, 'Please select a valid plan.')
    
    return render(request, 'accounts/plan_selection.html')

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            if request.user.is_studio_owner:
                return redirect('studio:dashboard')
            else:
                return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})


@login_required
def profile_view(request):
    """View for displaying and managing user profile"""
    # You can add any profile-specific logic here
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })
