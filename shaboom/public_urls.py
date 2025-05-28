from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib import admin
# from .admin import public_admin_site # Assuming you might want a separate public admin

# If public_admin_site is not different, use admin.site
# from django.contrib import admin

app_name = 'public'

urlpatterns = [
    path('admin/', admin.site.urls), # Or public_admin_site.urls
    path('accounts/', include('accounts.public_urls', namespace='public_accounts')), # Changed namespace to avoid conflict
    path('', RedirectView.as_view(url='/accounts/', permanent=False), name='landing_redirect'),
]
