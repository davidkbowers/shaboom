from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.http import Http404, HttpResponseServerError
from django.conf import settings
from django_tenants.utils import schema_context, get_tenant_model

def tenant_home(request):
    """Default view for tenant-specific home page."""
    return render(request, 'tenant_home.html')

def handler404(request, exception, template_name='404.html'):
    """Custom 404 handler."""
    return render(request, template_name, status=404)

def handler500(request, template_name='500.html'):
    """Custom 500 handler."""
    return render(request, template_name, status=500)

class PublicHomeView(TemplateView):
    """Public home page (no tenant required)."""
    template_name = 'public_home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any public context data here
        return context
