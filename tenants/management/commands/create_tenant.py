from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from tenants.models import Client, Domain
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create a new tenant with a domain'

    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name of the tenant')
        parser.add_argument('domain', type=str, help='Domain for the tenant (e.g., my-tenant.localhost)')
        parser.add_argument('--email', type=str, help='Email for the admin user', default='admin@example.com')
        parser.add_argument('--password', type=str, help='Password for the admin user', default='admin')

    def handle(self, *args, **options):
        name = options['name']
        domain = options['domain']
        email = options['email']
        password = options['password']
        
        # Create the tenant
        tenant = Client.objects.create(
            name=name,
            business_name=name,
            schema_name=name.lower().replace(' ', '_'),
            paid_until=timezone.now() + timedelta(days=365),  # 1 year from now
            on_trial=False,
        )
        
        # Create the domain
        Domain.objects.create(
            domain=domain,
            tenant=tenant,
            is_primary=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created tenant "{name}" with domain "{domain}"'))
        
        # Create a superuser for the tenant
        with tenant_context(tenant):
            User = get_user_model()
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(
                    email=email,
                    password=password,
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created admin user with email: {email} and password: {password}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Admin user {email} already exists for this tenant'))
        
        self.stdout.write(self.style.SUCCESS(f'Tenant setup complete! Access it at: http://{domain}'))
