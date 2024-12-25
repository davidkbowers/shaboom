from django.urls import path
from . import views, views_gym

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password/change/', views.password_change_view, name='password_change'),
    
    # Gym owner onboarding URLs
    path('gym/setup/profile/', views_gym.gym_profile_setup, name='gym_profile_setup'),
    path('gym/setup/location/', views_gym.gym_location_setup, name='gym_location_setup'),
    path('gym/setup/hours/', views_gym.gym_hours_setup, name='gym_hours_setup'),
    path('gym/setup/social/', views_gym.gym_social_setup, name='gym_social_setup'),
    path('gym/dashboard/', views_gym.gym_dashboard, name='gym_dashboard'),
]
