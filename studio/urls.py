from django.urls import path
from .views.base import StudioDashboardView
import studio.views  # Import the module containing the function

app_name = 'studio'

urlpatterns = [
    path('', StudioDashboardView.as_view(), name='dashboard'),
    path('profile-setup/', studio.views.studio_profile_setup, name='studio_profile_setup'),
]