from django.test import TestCase, RequestFactory, override_settings
from django.test.client import Client as TestClient
from django.contrib.auth import get_user_model
from django_tenants.test.cases import TenantTestCase
from django_tenants.utils import get_public_schema_name, schema_context
from django.db import connection

from .models import Client, Domain
from .middleware import TenantMiddleware

class TenantResolutionTests(TenantTestCase):
    """Test tenant resolution logic."""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up the public tenant (created automatically by TenantTestCase)
        cls.public_tenant = Client.objects.get(schema_name=get_public_schema_name())
        
        # Create a test tenant
        cls.tenant1 = Client(
            schema_name='tenant1',
            name='Tenant One',
            business_name='Tenant One Business',
            paid_until='2030-01-01',
            on_trial=False
        )
        cls.tenant1.save()
        
        # Create domains for the test tenant
        Domain.objects.create(
            domain='tenant1.localhost',
            tenant=cls.tenant1,
            is_primary=True
        )
        
        # Create a superuser for testing
        cls.superuser = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='password',
            username='admin'
        )
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(get_response=None)
        self.client = TestClient()
    
    def test_public_tenant_resolution(self):
        """Test that public tenant is resolved correctly."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'localhost'
        
        self.middleware.process_request(request)
        
        self.assertEqual(request.tenant.schema_name, get_public_schema_name())
        self.assertTrue(request.is_public)
    
    def test_tenant_resolution_by_domain(self):
        """Test tenant resolution by domain."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'tenant1.localhost'
        
        self.middleware.process_request(request)
        
        self.assertEqual(request.tenant.schema_name, 'tenant1')
        self.assertFalse(request.is_public)
    
    def test_tenant_resolution_by_subdomain(self):
        """Test tenant resolution by subdomain."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'tenant1.example.com'
        
        self.middleware.process_request(request)
        
        self.assertEqual(request.tenant.schema_name, 'tenant1')
        self.assertFalse(request.is_public)
    
    def test_non_existent_tenant_falls_back_to_public(self):
        """Test that non-existent tenant falls back to public."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'nonexistent.localhost'
        
        self.middleware.process_request(request)
        
        self.assertEqual(request.tenant.schema_name, get_public_schema_name())
        self.assertTrue(request.is_public)
    
    def test_www_subdomain_falls_back_to_public(self):
        """Test that www subdomain falls back to public."""
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'www.tenant1.localhost'
        
        self.middleware.process_request(request)
        
        self.assertEqual(request.tenant.schema_name, get_public_schema_name())
        self.assertTrue(request.is_public)
    
    @override_settings(ALLOWED_HOSTS=['*'])
    def test_https_access(self):
        """Test tenant resolution with HTTPS."""
        request = self.factory.get('/', secure=True)
        request.META['HTTP_HOST'] = 'tenant1.localhost'
        request.META['SERVER_PORT'] = '443'
        
        self.middleware.process_request(request)
        
        self.assertEqual(request.tenant.schema_name, 'tenant1')
        self.assertFalse(request.is_public)
    
    def test_public_tenant_creation(self):
        """Test that public tenant is created if it doesn't exist."""
        # Delete the public tenant for this test
        with schema_context(get_public_schema_name()):
            Domain.objects.all().delete()
            Client.objects.filter(schema_name=get_public_schema_name()).delete()
        
        # This should create the public tenant
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'localhost'
        
        self.middleware.process_request(request)
        
        self.assertEqual(request.tenant.schema_name, get_public_schema_name())
        self.assertTrue(Client.objects.filter(schema_name=get_public_schema_name()).exists())

class TenantModelTests(TenantTestCase):
    """Test tenant model functionality."""
    
    def test_create_tenant(self):
        """Test creating a new tenant and accessing it."""
        # Create a new tenant
        tenant = Client(
            schema_name='newtenant',
            name='New Tenant',
            business_name='New Tenant Business',
            paid_until='2030-01-01',
            on_trial=True
        )
        tenant.save()
        
        # Create a domain for the tenant
        domain = Domain.objects.create(
            domain='newtenant.localhost',
            tenant=tenant,
            is_primary=True
        )
        
        # Test accessing the tenant
        with tenant.schema_context():
            # This runs in the tenant's schema
            self.assertTrue(Client.objects.filter(schema_name='newtenant').exists())
        
        # Test tenant resolution
        request = RequestFactory().get('/')
        request.META['HTTP_HOST'] = 'newtenant.localhost'
        
        middleware = TenantMiddleware(get_response=None)
        middleware.process_request(request)
        
        self.assertEqual(request.tenant.schema_name, 'newtenant')
        self.assertEqual(request.tenant.business_name, 'New Tenant Business')
