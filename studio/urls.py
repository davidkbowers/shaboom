from django.urls import path
# Updated import to reflect consolidated views.py and add all necessary views
from .views import (
    StudioDashboardView, studio_profile_setup, studio_admin_dashboard, 
    toggle_public_videos, toggle_public_signup, approve_membership,
    deactivate_membership, activate_membership
)

app_name = 'studio'

urlpatterns = [
    path('', StudioDashboardView.as_view(), name='dashboard'),
    # Reference studio_profile_setup directly
    path('profile-setup/', studio_profile_setup, name='studio_profile_setup'),
    # Add other studio URLs previously in accounts.urls
    path('admin/', studio_admin_dashboard, name='admin_dashboard'), # Changed name to avoid conflict if accounts also has 'studio_admin_dashboard'
    path('toggle-public-videos/', toggle_public_videos, name='toggle_public_videos'),
    path('toggle-public-signup/', toggle_public_signup, name='toggle_public_signup'),
    path('memberships/approve/<int:membership_id>/', approve_membership, name='approve_membership'),
    path('memberships/deactivate/<int:membership_id>/', deactivate_membership, name='deactivate_membership'),
    path('memberships/activate/<int:membership_id>/', activate_membership, name='activate_membership'),
]