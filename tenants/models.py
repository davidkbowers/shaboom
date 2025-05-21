from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    
    # Default true, schema will be automatically created and synced when it is saved
    auto_create_schema = True
    
    # Studio-specific fields
    business_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='studio_logos/', null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.business_name or self.name

class Domain(DomainMixin):
    # Override the default domain mixin to make it work with our Client model
    pass
