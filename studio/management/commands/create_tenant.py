from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import tenant_context
from django.contrib.auth import get_user_model
from studio.models import StudioProfile
from tenants.models import Client, Domain

class Command(BaseCommand):
    help = 'Create a new tenant with a domain and associate it with a studio profile'

    def add_arguments(self, parser):
        parser.add_argument('subdomain', type=str, help='Subdomain for the tenant (e.g., mystudio)')
        parser.add_argument('email', type=str, help='Email of the studio owner')
        parser.add_argument('--domain', type=str, default='localhost', help='Base domain (default: localhost)')
        parser.add_argument('--name', type=str, help='Studio name (default: subdomain)')
        parser.add_argument('--description', type=str, default='', help='Studio description')
        parser.add_argument('--paid-until', type=str, default='2100-12-31', help='Paid until date (YYYY-MM-DD)')

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        email = options['email']
        domain = options['domain']
        name = options.get('name') or subdomain
        description = options['description']
        paid_until = options['paid_until']

        # Get or create user
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User with email {email} does not exist'))
            return

        # Check if studio profile already exists
        if hasattr(user, 'studio_profile'):
            self.stderr.write(self.style.ERROR(f'User {email} already has a studio profile'))
            return

        # Check if subdomain is already taken
        if StudioProfile.objects.filter(subdomain=subdomain).exists():
            self.stderr.write(self.style.ERROR(f'Subdomain {subdomain} is already taken'))
            return

        try:
            # Create tenant
            tenant = Client(
                name=name,
                business_name=name,
                description=description,
                schema_name=subdomain,
                paid_until=paid_until,
                on_trial=True
            )
            tenant.save()

            # Create domain
            domain_obj = Domain()
            domain_obj.domain = f"{subdomain}.{domain}"
            domain_obj.tenant = tenant
            domain_obj.is_primary = True
            domain_obj.save()

            # Create studio profile
            studio_profile = StudioProfile(
                owner=user,
                subdomain=subdomain,
                description=description,
                tenant=tenant
            )
            studio_profile.save()

            # Update user type to studio owner if needed
            if not user.is_studio_owner:
                user.user_type = 'owner'
                user.save()

            self.stdout.write(self.style.SUCCESS(f'Successfully created tenant with subdomain: {subdomain}'))
            self.stdout.write(self.style.SUCCESS(f'Studio URL: https://{subdomain}.{domain}'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error creating tenant: {str(e)}'))
            # Clean up if anything went wrong
            if 'tenant' in locals():
                tenant.delete(force_drop=True)
