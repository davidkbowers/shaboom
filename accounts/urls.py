from django.urls import path
from . import views, views_studio, views_member

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('password/change/', views.password_change_view, name='password_change'),

    # Studio Owner URLs
    path('studio/profile/setup/', views_studio.studio_profile_setup, name='studio_profile_setup'),
    path('studio/location/setup/', views_studio.studio_location_setup, name='studio_location_setup'),
    path('studio/hours/setup/', views_studio.studio_hours_setup, name='studio_hours_setup'),
    path('studio/social/setup/', views_studio.studio_social_setup, name='studio_social_setup'),
    path('studio/dashboard/', views_studio.studio_dashboard, name='studio_dashboard'),
    path('studio/upload/video/', views_studio.upload_video, name='upload_video'),

    # Studio admin dashboard URLs
    path('studio/admin/', views_studio.studio_admin_dashboard, name='studio_admin_dashboard'),
    path('studio/admin/membership/<int:membership_id>/approve/', views_studio.approve_membership, name='approve_membership'),
    path('studio/admin/membership/<int:membership_id>/deactivate/', views_studio.deactivate_membership, name='deactivate_membership'),
    path('studio/admin/membership/<int:membership_id>/activate/', views_studio.activate_membership, name='activate_membership'),

    # Member URLs
    path('member/dashboard/', views_member.member_dashboard, name='member_dashboard'),
]
