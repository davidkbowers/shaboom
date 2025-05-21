from django.core.management.base import BaseCommand
from django_tenants.utils import get_public_schema_name
from django.contrib.auth import get_user_model
from tenants.models import Client, Domain

class Command(BaseCommand):
    help = 'Creates the public tenant and a superuser'

    def handle(self, *args, **options):
        # Create public tenant if it doesn't exist
        public_schema = get_public_schema_name()
        
        # Create or get the public client
        client, created = Client.objects.get_or_create(
            schema_name=public_schema,
            defaults={
                'name': 'Public Tenant',
                'business_name': 'Public Tenant',
                'paid_until': '2030-12-31',
                'on_trial': False,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created public tenant'))
        else:
            self.stdout.write(self.style.SUCCESS('Public tenant already exists'))
        
        # Create or get the domain for the public tenant
        domain, created = Domain.objects.get_or_create(
            domain='localhost',
            tenant=client,
            defaults={
                'is_primary': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created domain for public tenant'))
        else:
            self.stdout.write(self.style.SUCCESS('Domain for public tenant already exists'))
        
        # Create superuser if it doesn't exist
        User = get_user_model()
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(
                email='admin@example.com',
                password='admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Created superuser with email: admin@example.com and password: admin'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists'))
        
        self.stdout.write(self.style.SUCCESS('Setup completed successfully'))
