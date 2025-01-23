from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

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
    business_name = models.CharField(max_length=255)
    business_description = models.TextField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='studio_logos/', blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    business_hours = models.JSONField(default=dict)
    amenities = models.JSONField(default=list)
    social_media = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} - {self.owner.email}"

class StudioLocation(models.Model):
    studio = models.ForeignKey(StudioProfile, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    is_main_location = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['studio', 'is_main_location']]

    def __str__(self):
        return f"{self.name} - {self.studio.business_name}"

class StudioMembership(models.Model):
    MEMBERSHIP_STATUS = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Approval'),
    )

    studio = models.ForeignKey(StudioProfile, on_delete=models.CASCADE, related_name='memberships')
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='studio_memberships')
    status = models.CharField(max_length=20, choices=MEMBERSHIP_STATUS, default='pending')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['studio', 'member']]

    def __str__(self):
        return f"{self.member.email} at {self.studio.business_name}"
