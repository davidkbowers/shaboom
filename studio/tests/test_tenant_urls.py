from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.conf import settings
from django_tenants.test.cases import FastTenantTestCase as BaseFastTenantTestCase
from django_tenants.test.client import TenantClient
from django_tenants.utils import schema_context
from studio.models import StudioProfile
from tenants.models import Client, Domain
import datetime

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

class TenantURLTests(FastTenantTestCase):
    """Test tenant-specific URL routing"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a test user in the public schema
        with schema_context('public'):
            cls.public_user = User.objects.create_user(
                email='public@example.com',
                password='testpass123',
                first_name='Public',
                last_name='User',
                user_type='user'
            )
    
    def setUp(self):
        super().setUp()
        
        # Create a test user in the tenant schema with necessary permissions
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='owner',  # Set user type to owner (from USER_TYPE_CHOICES)
            is_staff=True,  # Make the user a staff member
            is_active=True  # Ensure the user is active
        )
        
        # Add the is_studio_owner property to the user
        from django.utils.functional import cached_property
        User.is_studio_owner = property(lambda u: u.user_type == 'owner')
        
        # Create a studio profile for the user
        self.studio_profile = StudioProfile.objects.create(
            owner=self.user,
            subdomain='teststudio',
            description='Test Studio',
            tenant=self.tenant
        )
        
        # Add necessary permissions for the user
        self.user.user_permissions.add(
            Permission.objects.get(codename='view_studioprofile'),
            Permission.objects.get(codename='change_studioprofile'),
        )
        self.user.save()
        
        # Create a domain for the current test tenant
        self.domain = Domain.objects.create(
            domain='teststudio.example.com',
            tenant=self.tenant,
            is_primary=True
        )
        
        # Use TenantClient for proper tenant handling
        self.client = TenantClient(self.tenant)
        
        # Refresh the user to ensure the studio profile is accessible
        self.user.refresh_from_db()
        
        # Debug output
        print(f"User type: {self.user.user_type}")
        print(f"Is studio owner: {self.user.is_studio_owner}")
        print(f"Has studio profile: {hasattr(self.user, 'studio_profile')}")
        if hasattr(self.user, 'studio_profile'):
            print(f"Studio profile: {self.user.studio_profile}")
        else:
            print("No studio profile found")
        
        # Create a test client for the public schema
        with schema_context('public'):
            # Create a public client if it doesn't exist
            self.public_client, _ = Client.objects.get_or_create(
                schema_name='public',
                defaults={
                    'name': 'Public',
                    'paid_until': '2100-12-31',
                    'business_name': 'Public Business',
                    'description': 'Public Description'
                }
            )
            
            # Create a domain for the public client if it doesn't exist
            Domain.objects.get_or_create(
                domain='public.example.com',
                tenant=self.public_client,
                defaults={'is_primary': True}
            )
    
    def test_tenant_dashboard_url(self):
        """Test that the tenant dashboard URL resolves to the correct view."""
        # Use the studio profile created in setUp
        studio_profile = self.studio_profile
        
        # Test the URL resolution
        url = reverse('studio:dashboard')
        self.assertEqual(url, '/studio/')
        
        # Resolve the URL to check the view
        resolver = resolve(url)
        self.assertEqual(resolver.view_name, 'studio:dashboard')
        
        # Check that the URL redirects to login when not authenticated
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertIn('/accounts/login/', response.url)
        
        # Check that the URL is accessible when authenticated and has permissions
        self.client.force_login(self.user)
        response = self.client.get(url)
        # Should be 200 or 302 (if there's a redirect after login)
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 302:
            response = self.client.get(response.url)
            self.assertEqual(response.status_code, 200)
    
    @override_settings(ALLOWED_HOSTS=['*'])
    def test_tenant_subdomain_routing(self):
        """Test that subdomains are properly routed to the correct tenant"""
        # Use the studio profile created in setUp
        studio_profile = self.studio_profile
        
        # Test accessing the studio dashboard without authentication
        response = self.client.get(
            '/studio/',
            follow=True  # Follow any redirects
        )
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 200)  # Should be 200 after following redirect
        self.assertIn('login', response.wsgi_request.path)
        
        # Login and try again
        self.assertTrue(self.client.login(email='test@example.com', password='testpass123'), 
                      "Failed to log in user")
        
        # Make the request to the studio dashboard
        response = self.client.get(
            '/studio/',
            follow=True  # Follow any redirects
        )
        
        # Check if we got a 200 OK
        self.assertEqual(response.status_code, 200, 
                       f"Expected status code 200, got {response.status_code}. Response content: {response.content}")
        
        # Test that the request has the correct tenant set
        self.assertEqual(response.wsgi_request.tenant, self.tenant, 
                       f"Expected tenant {self.tenant.schema_name}, got {response.wsgi_request.tenant.schema_name if hasattr(response.wsgi_request.tenant, 'schema_name') else 'None'}")
        
        # Test that the tenant's data is accessible
        self.assertContains(response, studio_profile.description, status_code=200)
        
        # Test that the response is from the correct tenant
        self.assertEqual(response.wsgi_request.tenant.schema_name, self.tenant.schema_name)
        
        # Test that a non-existent subdomain returns a 404
        response = self.client.get(
            '/studio/',
            HTTP_HOST='nonexistent.example.com',
            follow=True
        )
        self.assertEqual(response.status_code, 404)
