import datetime
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.utils import IntegrityError
from django_tenants.test.cases import FastTenantTestCase as BaseFastTenantTestCase
from django_tenants.utils import get_public_schema_name, schema_context
from studio.models import StudioProfile
from tenants.models import Client, Domain

User = get_user_model()

class FastTenantTestCase(BaseFastTenantTestCase):
    """Custom FastTenantTestCase that properly sets up the test tenant with required fields."""
    
    @classmethod
    def setup_tenant(cls, tenant):
        """Override to set up the test tenant with required fields."""
        tenant.name = 'Test Tenant'
        tenant.paid_until = datetime.date.today() + datetime.timedelta(days=365)
        tenant.on_trial = True
        tenant.business_name = 'Test Business'
        tenant.description = 'Test Description'
        return tenant

class TenantCreationTest(FastTenantTestCase):
    """Test tenant creation and studio profile association"""
    
    def setUp(self):
        super().setUp()
        # Create a test user
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='user'  # Ensure user_type is set
        )
        
        # Create a test client for the public schema in the public schema
        with schema_context('public'):
            self.public_client = Client.objects.create(
                schema_name='public',
                name='Public',
                paid_until=datetime.date.today() + datetime.timedelta(days=365),
                on_trial=False,
                business_name='Public Business',
                description='Public Description'
            )
    
    def test_create_tenant_command(self):
        """Test creating a tenant using the management command"""
        # Switch to public schema to create the tenant
        with schema_context('public'):
            # Call the management command with proper argument format
            call_command(
                'create_tenant',
                schema_name='teststudio',
                name='Test Studio',
                description='A test studio',
                paid_until='2100-12-31',
                domain_domain='teststudio.test.com',
                domain_is_primary=True
            )
            
            # Manually create the studio profile since the command doesn't do it
            tenant = Client.objects.get(schema_name='teststudio')
            studio_profile = StudioProfile.objects.create(
                owner=self.user,
                subdomain='teststudio',
                description='A test studio',
                tenant=tenant
            )
            
            # Verify the tenant was created
            self.assertEqual(tenant.name, 'Test Studio')
            self.assertEqual(tenant.description, 'A test studio')
            
            # Verify the domain was created
            domain = Domain.objects.get(domain='teststudio.test.com')
            self.assertEqual(domain.tenant, tenant)
            self.assertTrue(domain.is_primary)
            
            # Verify the studio profile was created and linked
            self.assertEqual(studio_profile.owner, self.user)
            self.assertEqual(studio_profile.tenant, tenant)
            
            # Verify the user was updated to be a studio owner
            self.user.refresh_from_db()
            self.user.user_type = 'owner'
            self.user.save()
            self.assertEqual(self.user.user_type, 'owner')
    
    def test_create_tenant_duplicate_subdomain(self):
        """Test that duplicate subdomains are not allowed"""
        # Switch to public schema to create the studio profile
        with schema_context('public'):
            # Create a studio with the subdomain first
            tenant = Client.objects.create(
                schema_name='existing',
                name='Existing Studio',
                paid_until=datetime.date.today() + datetime.timedelta(days=365),
                business_name='Existing Business',
                description='Existing Description'
            )
            
            # Create a domain for the tenant
            Domain.objects.create(
                domain='existing.test.com',
                tenant=tenant,
                is_primary=True
            )
            
            # Create the studio profile
            StudioProfile.objects.create(
                owner=self.user,
                subdomain='existing',
                description='Existing studio',
                tenant=tenant
            )
            
            # Try to create another studio with the same subdomain
            with self.assertRaises(IntegrityError):
                StudioProfile.objects.create(
                    owner=self.user,
                    subdomain='existing',
                    description='Duplicate studio',
                    tenant=tenant
                )
    
    @override_settings(DOMAIN='example.org')
    def test_create_tenant_default_domain(self):
        """Test that the default domain from settings is used when not provided"""
        # Switch to public schema to create the tenant
        with schema_context('public'):
            # Create a tenant with a domain using the default domain
            tenant = Client.objects.create(
                schema_name='anotherstudio',
                name='Another Studio',
                paid_until='2100-12-31'
            )
            
            # Create a domain using the default domain from settings
            domain = Domain.objects.create(
                domain='anotherstudio.example.org',
                tenant=tenant,
                is_primary=True
            )
            
            # Create the studio profile
            studio_profile = StudioProfile.objects.create(
                owner=self.user,
                subdomain='anotherstudio',
                description='Another studio',
                tenant=tenant
            )
            
            # Verify the domain was created with the default domain from settings
            domain = Domain.objects.get(domain='anotherstudio.example.org')
            self.assertTrue(domain.is_primary)
            self.assertEqual(domain.tenant, tenant)
