from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from . import views_public
from .views import plan_selection_view
from .views_landing import LandingPageView

# Public account URLs (signup, login, password reset, etc.)
urlpatterns = [
    # Landing page
    path('', LandingPageView.as_view(), name='landing'),
    # Authentication
    path('plan-selection/', plan_selection_view, name='plan_selection'),
    path('signup/', views_public.SignUpView.as_view(), name='signup'),
    path('login/', views_public.user_login, name='login'),
    path('logout/', views_public.user_logout, name='logout'),
    # Studio-specific signup (keeps the old URL pattern for studio-specific signups)
    path('signup/<slug:studio_slug>/', views_public.public_studio_signup, name='studio_signup'),
    
    # Password reset
    # Password reset
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/public/password_reset.html',
             email_template_name='accounts/emails/password_reset_email.html',
             subject_template_name='accounts/emails/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done')
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
             success_url=reverse_lazy('password_reset_complete')
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/public/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Public studio pages
    path('studio/<slug:studio_slug>/', include([
        path('', views_public.public_studio_videos, name='public_studio_videos'),
        path('signup/', views_public.public_studio_signup, name='public_studio_signup'),
    ])),
    
    # Redirect root to login
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
]
