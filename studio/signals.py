from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import StudioProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_studio_profile(sender, instance, created, **kwargs):
    """
    Create a StudioProfile when a new user with user_type='owner' is created.
    """
    if created and instance.user_type == 'owner':
        StudioProfile.objects.create(owner=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_studio_profile(sender, instance, **kwargs):
    """
    Save the StudioProfile when the user is saved.
    """
    if hasattr(instance, 'studio_profile'):
        instance.studio_profile.save()
