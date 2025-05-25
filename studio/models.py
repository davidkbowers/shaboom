from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid


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
    
    # Fields for public links
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    public_id = models.UUIDField(unique=True, null=True, blank=True)
    allow_public_videos = models.BooleanField(default=False)
    allow_public_signup = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a unique slug from the owner's name
            base_slug = slugify(f"{self.owner.first_name}-{self.owner.last_name}")
            unique_slug = base_slug
            counter = 1
            while StudioProfile.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
            
        if not self.public_id:
            self.public_id = uuid.uuid4()
            
        super().save(*args, **kwargs)

    def get_public_video_url(self):
        return f"/s/{self.slug}/videos/"

    def get_public_signup_url(self):
        return f"/s/{self.slug}/join/"

    def __str__(self):
        return f"Studio - {self.owner.email}"


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
