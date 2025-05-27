from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_tenants.utils import tenant_context
from tenants.models import Client, Domain
import uuid
import os


class StudioProfile(models.Model):
    """Model representing a studio in the system."""
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='studio_profile')
    website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, help_text="A brief description of your studio")
    logo = models.ImageField(upload_to='studio_logos/', blank=True, null=True)
    business_hours = models.JSONField(default=dict)
    amenities = models.JSONField(default=list)
    
    # Social media fields
    instagram = models.CharField(max_length=255, blank=True, null=True, help_text="Instagram username without @")
    facebook = models.CharField(max_length=255, blank=True, null=True, help_text="Facebook page name")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Fields for public links and tenant
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    subdomain = models.SlugField(max_length=100, unique=True, blank=True, null=True,
                               help_text="Subdomain for the studio's tenant site")
    public_id = models.UUIDField(unique=True, null=True, blank=True)
    allow_public_videos = models.BooleanField(default=False)
    allow_public_signup = models.BooleanField(default=True)
    
    # Tenant reference
    tenant = models.OneToOneField('tenants.Client', on_delete=models.SET_NULL, 
                                null=True, blank=True, related_name='studio_profile')

    def save(self, *args, **kwargs):
        # Generate slug if not exists
        if not self.slug:
            # Generate a unique slug from the owner's name
            base_slug = slugify(f"{self.owner.first_name}-{self.owner.last_name}")
            unique_slug = base_slug
            counter = 1
            while StudioProfile.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        
        # Generate public_id if not exists
        if not self.public_id:
            self.public_id = uuid.uuid4()
        
        # Generate subdomain if not exists and this is a new instance
        is_new = self._state.adding
        if is_new and not self.subdomain:
            base_subdomain = slugify(f"{self.owner.first_name}-{self.owner.last_name}")
            unique_subdomain = base_subdomain
            counter = 1
            while StudioProfile.objects.filter(subdomain=unique_subdomain).exists():
                unique_subdomain = f"{base_subdomain}{counter}"
                counter += 1
            self.subdomain = unique_subdomain
            
        super().save(*args, **kwargs)

    def get_public_video_url(self):
        return f"https://{self.subdomain}.{os.environ.get('DOMAIN', 'example.com')}/videos/"

    def get_public_signup_url(self):
        return f"https://{self.subdomain}.{os.environ.get('DOMAIN', 'example.com')}/join/"
        
    def get_absolute_url(self):
        return f"https://{self.subdomain}.{os.environ.get('DOMAIN', 'example.com')}"
        
    @property
    def tenant_domain(self):
        """Return the full domain for this tenant"""
        return f"{self.subdomain}.{os.environ.get('DOMAIN', 'example.com')}"

    def __str__(self):
        return f"Studio - {self.owner.email}"


@receiver(post_save, sender=StudioProfile)
def create_tenant_for_studio(sender, instance, created, **kwargs):
    """
    Signal handler to create a tenant when a new studio profile is created.
    """
    if created and not instance.tenant:
        # Create a new tenant
        tenant = Client(
            name=instance.owner.get_full_name() or f"Studio {instance.subdomain}",
            business_name=instance.owner.get_full_name(),
            description=instance.description or "",
            schema_name=instance.subdomain,
            paid_until='2100-12-31',  # Set a far future date
            on_trial=True
        )
        tenant.save()
        
        # Create a domain for the tenant
        domain = Domain()
        domain.domain = instance.tenant_domain
        domain.tenant = tenant
        domain.is_primary = True
        domain.save()
        
        # Associate the tenant with the studio profile
        instance.tenant = tenant
        instance.save(update_fields=['tenant'])
        
        # You might want to set up initial data for the tenant here
        # using tenant_context(tenant):
        #     # Create initial data for the tenant
        #     pass


class StudioMembership(models.Model):
    """Model representing a user's membership to a studio."""
    MEMBERSHIP_STATUS = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    )

    studio = models.ForeignKey(StudioProfile, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='studio_memberships')
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['studio', 'member']]

    def __str__(self):
        return f"{self.member.email} at {self.studio.owner.email}"
