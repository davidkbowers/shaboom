from django.urls import path
from . import views, views_gym, views_member

urlpatterns = [
    # Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password/change/', views.password_change_view, name='password_change'),
    
    # Gym Owner URLs
    path('gym/profile/setup/', views_gym.gym_profile_setup, name='gym_profile_setup'),
    path('gym/location/setup/', views_gym.gym_location_setup, name='gym_location_setup'),
    path('gym/hours/setup/', views_gym.gym_hours_setup, name='gym_hours_setup'),
    path('gym/social/setup/', views_gym.gym_social_setup, name='gym_social_setup'),
    path('gym/dashboard/', views_gym.gym_dashboard, name='gym_dashboard'),
    path('gym/upload/video/', views_gym.upload_video, name='upload_video'),
    
    # Gym admin dashboard URLs
    path('gym/admin/', views_gym.gym_admin_dashboard, name='gym_admin_dashboard'),
    path('gym/admin/membership/<int:membership_id>/approve/', views_gym.approve_membership, name='approve_membership'),
    path('gym/admin/membership/<int:membership_id>/deactivate/', views_gym.deactivate_membership, name='deactivate_membership'),
    path('gym/admin/membership/<int:membership_id>/activate/', views_gym.activate_membership, name='activate_membership'),
    
    # Member URLs
    path('member/dashboard/', views_member.member_dashboard, name='member_dashboard'),
]
