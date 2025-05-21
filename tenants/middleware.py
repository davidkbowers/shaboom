from django.http import Http404
from django.conf import settings
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, get_public_schema_name

class TenantMiddleware(TenantMainMiddleware):
    """
    Extends the default TenantMainMiddleware to handle tenant-specific logic.
    """
    def process_request(self, request):
        # Let the parent class handle the main tenant resolution
        super().process_request(request)
        
        # Set a flag indicating if this is a public schema request
        if hasattr(request, 'tenant') and hasattr(request.tenant, 'schema_name'):
            request.is_public = request.tenant.schema_name == get_public_schema_name()
        else:
            # Default to public if tenant is not set
            request.is_public = True

    def get_tenant(self, model, hostname, request):
        """
        Override to implement custom tenant resolution logic.
        """
        # First, try to get the tenant by domain
        try:
            domain = model.objects.get(domain=hostname)
            return domain.tenant
        except model.DoesNotExist:
            # If no domain is found, try to match a subdomain
            subdomain = hostname.split('.')[0]
            if subdomain and subdomain != 'www':
                try:
                    return model.objects.get(schema_name=subdomain)
                except model.DoesNotExist:
                    pass
            
            # Fall back to public schema
            try:
                return model.objects.get(schema_name=get_public_schema_name())
            except model.DoesNotExist:
                # If public schema doesn't exist, create it
                from datetime import date, timedelta
                from django_tenants.utils import get_public_schema_name
                from .models import Domain
                
                # Create the public tenant
                public_tenant = model(
                    schema_name=get_public_schema_name(),
                    name='Public Tenant',
                    business_name='Public Tenant',
                    paid_until=date.today() + timedelta(days=365 * 10),  # 10 years
                    on_trial=False
                )
                public_tenant.save(verbosity=0)
                
                # Create a domain for the public tenant
                Domain.objects.create(
                    domain=hostname,  # Use the current hostname
                    tenant=public_tenant,
                    is_primary=True
                )
                
                return public_tenant
