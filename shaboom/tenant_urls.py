from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .admin import tenant_admin_site
from . import views

# No app_name here, as this is a ROOT_URLCONF for tenants

# This is critical for django-tenants to work properly with authentication
# Set the login URL pattern for LoginRequiredMixin redirects
LOGIN_URL = 'accounts:login'

urlpatterns = [
    path('admin/', tenant_admin_site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('studio/', include('studio.urls', namespace='studio')),
    path('videos/', include('videos.urls', namespace='videos')),
    path('', views.tenant_home, name='tenant_home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
