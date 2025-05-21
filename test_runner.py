import os
import sys
from django.test.runner import DiscoverRunner
from django.conf import settings
from django.db import connections

class TenantAwareTestRunner(DiscoverRunner):
    """Test runner that sets up the test database with the public schema."""
    
    def setup_databases(self, **kwargs):
        # First create the test database
        test_db = super().setup_databases(**kwargs)
        
        # Set the test database name in the environment so we can use it in tests
        os.environ['TEST_DATABASE_NAME'] = settings.DATABASES['default']['NAME']
        
        # Set up the public schema
        from django_tenants.utils import get_public_schema_name, schema_context
        from tenants.models import Client, Domain
        
        # Ensure the public schema exists and is set up
        with schema_context(get_public_schema_name()):
            # Create a public tenant if it doesn't exist
            public_tenant, created = Client.objects.get_or_create(
                schema_name=get_public_schema_name(),
                defaults={
                    'name': 'Public Tenant',
                    'on_trial': False,
                    'is_active': True,
                }
            )
            
            # Ensure the public tenant has a domain
            Domain.objects.get_or_create(
                domain='test.localhost',
                tenant=public_tenant,
                is_primary=True
            )
        
        return test_db
