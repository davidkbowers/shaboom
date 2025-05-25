from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from studio.models import StudioProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create StudioProfile for existing studio owners who don\'t have one'

    def handle(self, *args, **options):
        # Get all studio owners without a studio profile
        users_without_profile = User.objects.filter(
            user_type='owner'
        ).exclude(
            studio_profile__isnull=False
        )
        
        count = 0
        for user in users_without_profile:
            StudioProfile.objects.create(owner=user)
            self.stdout.write(self.style.SUCCESS(f'Created StudioProfile for {user.email}'))
            count += 1
            
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} StudioProfile(s)'))
