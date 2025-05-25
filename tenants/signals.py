from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

def create_public_tenant(apps, schema_editor, **kwargs):
    """
    Create a public tenant when migrations are run.
    """
    from datetime import date, timedelta
    from django_tenants.utils import get_public_schema_name
    
    # Get the tenant model using the apps registry to avoid direct model imports
    TenantModel = apps.get_model('tenants', 'Client')
    Domain = apps.get_model('tenants', 'Domain')
    
    # Only create the public tenant if it doesn't exist
    schema_name = get_public_schema_name()
    
    if not TenantModel.objects.filter(schema_name=schema_name).exists():
        tenant = TenantModel(
            schema_name=schema_name,
            name='Public Tenant',
            business_name='Public Tenant',
            paid_until=date.today() + timedelta(days=365 * 10),  # 10 years
            on_trial=False
        )
        tenant.save(verbosity=0)
        
        # Create a domain for the public tenant
        Domain.objects.create(
            domain='localhost',  # Change this to your domain in production
            tenant=tenant,
            is_primary=True
        )

def connect_signals():
    """Connect signals when the app is ready."""
    from django_tenants.models import TenantMixin
    from django.apps import apps
    
    # Get the actual tenant model class
    try:
        TenantModel = apps.get_model('tenants.Client')
        if TenantModel and issubclass(TenantModel, TenantMixin):
            post_migrate.connect(create_public_tenant, sender=TenantModel)
    except LookupError:
        # Model not loaded yet, will be connected later
        pass
