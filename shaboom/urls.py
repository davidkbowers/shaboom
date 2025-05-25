"""
URL configuration for shaboom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django_tenants.utils import remove_www_and_dev, get_public_schema_name
from .admin import tenant_admin_site

from . import views
from accounts.views_landing import LandingPageView

# Public URLs (no tenant)
public_patterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(('accounts.public_urls', 'public'), namespace='public')),  # Public account views
    # Redirect root to landing page in public namespace
    path('', RedirectView.as_view(url='/accounts/', permanent=False)),
]

# Tenant-specific URLs
tenant_patterns = [
    path('admin/', tenant_admin_site.urls),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),  # Tenant account views
    path('studio/', include(('studio.urls', 'studio'), namespace='studio')),  # Studio management
    path('videos/', include(('videos.urls', 'videos'), namespace='videos')),
    path('', views.tenant_home, name='tenant_home'),
]

def tenant_public_view(view):
    """Mark a view as public (no tenant required)."""
    view.tenant_public_view = True
    return view

def tenant_required(view):
    """Mark a view as requiring a tenant."""
    view.tenant_required = True
    return view

# Main URL dispatcher
urlpatterns = [
    # Public URLs (no tenant required)
    path('', include(public_patterns)),
    
    # Tenant-specific URLs (handled by tenant middleware)
    path('', include(tenant_patterns)),
]

# Add media files serving in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
# Error handlers
handler404 = 'shaboom.views.handler404'
handler500 = 'shaboom.views.handler500'
