from django.urls import path
from . import views, views_studio

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('plan-selection/', views.plan_selection_view, name='plan_selection'),
    path('password/change/', views.password_change_view, name='password_change'),
    
    # Studio Profile URLs
    path('studio/profile/setup/', views_studio.studio_profile_setup, name='studio_profile_setup'),
    path('studio/dashboard/', views_studio.studio_dashboard, name='studio_dashboard'),
    path('studio/admin/', views_studio.studio_admin_dashboard, name='studio_admin_dashboard'),
    
    # Public Links URLs
    path('studio/toggle-public-videos/', views_studio.toggle_public_videos, name='toggle_public_videos'),
    path('studio/toggle-public-signup/', views_studio.toggle_public_signup, name='toggle_public_signup'),
]
