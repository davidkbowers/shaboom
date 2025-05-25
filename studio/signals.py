from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Define signal handlers but don't connect them yet
def create_studio_profile(sender, instance, created, **kwargs):
    """
    Create a StudioProfile when a new user with user_type='owner' is created.
    """
    if created and instance.user_type == 'owner':
        # Import here to avoid circular imports
        from .models import StudioProfile
        StudioProfile.objects.create(owner=instance)


def save_studio_profile(sender, instance, **kwargs):
    """
    Save the StudioProfile when the user is saved.
    """
    if hasattr(instance, 'studio_profile'):
        instance.studio_profile.save()


def connect_signals():
    """Connect signals when the app is ready."""
    from django.apps import apps
    
    # Get the User model from the apps registry
    try:
        UserModel = apps.get_model(settings.AUTH_USER_MODEL)
        if UserModel:
            post_save.connect(create_studio_profile, sender=UserModel)
            post_save.connect(save_studio_profile, sender=UserModel)
    except LookupError:
        # Model not loaded yet, will be connected later
        pass
