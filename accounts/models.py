from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
import uuid

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    """
    Custom user model with additional fields for studio owners.

    Additional fields:

    - `user_type`: a choice between 'member' and 'owner', to distinguish between studio members and studio owners
    - `studio_name`: the name of the studio, if the user is an owner
    - `phone_number`: the phone number of the studio, if the user is an owner
    - `address`: the address of the studio, if the user is an owner
    - `onboarding_completed`: a boolean indicating whether the user has completed the onboarding process

    """
    USER_TYPE_CHOICES = (
        ('member', 'Studio Member'),
        ('owner', 'Studio Owner'),
    )

    username = None
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='member')
    studio_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    onboarding_completed = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        if self.user_type == 'owner' and self.studio_name:
            return f"{self.email} ({self.studio_name})"
        return self.email

    @property
    def is_studio_owner(self):
        return self.user_type == 'owner'

    def get_absolute_url(self):
        return reverse('studio_profile') if self.is_studio_owner else reverse('home')

class StudioProfile(models.Model):
    owner = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='studio_profile')
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='studio_logos/', blank=True, null=True)
    business_hours = models.JSONField(default=dict)
    amenities = models.JSONField(default=list)
    social_media = models.JSONField(default=dict)
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
    MEMBERSHIP_STATUS = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    )

    studio = models.ForeignKey(StudioProfile, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='studio_memberships')
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['studio', 'member']]

    def __str__(self):
        return f"{self.member.email} at {self.studio.owner.email}"
