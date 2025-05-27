from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views, views_public

app_name = 'accounts'

# Authentication URLs
auth_urlpatterns = [
    # Login/Logout
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/', views.register_view, name='register'),
    path('plan-selection/', views.plan_selection_view, name='plan_selection'),
    
    # User profile
    path('profile/', views.profile_view, name='profile'),
    
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

# Main URL patterns
urlpatterns = [
    # Include authentication URLs directly without extra nesting
    path('', include(auth_urlpatterns)),
]
