from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views, views_studio, views_public

app_name = 'accounts'

# Authentication URLs
auth_urlpatterns = [
    # Login/Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/', views.register_view, name='register'),
    path('plan-selection/', views.plan_selection_view, name='plan_selection'),
    
    # Password management
    path('password/change/', views.password_change_view, name='password_change'),
    
    # Password reset (using Django's built-in views with custom templates)
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/public/password_reset.html',
             email_template_name='accounts/emails/password_reset_email.html',
             subject_template_name='accounts/emails/password_reset_subject.txt',
             success_url='done/'
         ), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/public/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/public/password_reset_confirm.html',
             success_url='/accounts/reset/done/'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/public/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]

# Studio Profile URLs
studio_urlpatterns = [
    path('profile/setup/', views_studio.studio_profile_setup, name='studio_profile_setup'),
    path('dashboard/', views_studio.studio_dashboard, name='studio_dashboard'),
    path('admin/', views_studio.studio_admin_dashboard, name='studio_admin_dashboard'),
    path('toggle-public-videos/', views_studio.toggle_public_videos, name='toggle_public_videos'),
    path('toggle-public-signup/', views_studio.toggle_public_signup, name='toggle_public_signup'),
]

# Main URL patterns
urlpatterns = [
    # Include authentication URLs
    path('', include((auth_urlpatterns, 'accounts'))),
    
    # Include studio URLs under /studio/
    path('studio/', include((studio_urlpatterns, 'studio'))),
]
