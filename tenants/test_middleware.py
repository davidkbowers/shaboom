from unittest.mock import MagicMock, patch
from django.test import TestCase, RequestFactory
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name

from tenants.middleware import TenantMiddleware

class TestTenantMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(lambda r: None)  # Simple response function
        
        # Create a mock tenant
        self.mock_tenant = MagicMock()
        self.mock_tenant.schema_name = 'test_schema'
        
        # Create a mock public tenant
        self.mock_public_tenant = MagicMock()
        self.mock_public_tenant.schema_name = get_public_schema_name()
        
        # Patch the get_tenant method
        self.get_tenant_patcher = patch.object(
            TenantMiddleware, 
            'get_tenant', 
            return_value=self.mock_public_tenant
        )
        self.mock_get_tenant = self.get_tenant_patcher.start()
        
        # Patch the request.tenant assignment
        self.patcher = patch('django_tenants.utils.get_tenant_model')
        self.mock_tenant_model = self.patcher.start()
        self.mock_tenant_model.objects.get.return_value = self.mock_public_tenant

    def test_public_schema_request(self):
        """Test that requests to the public schema are handled correctly"""
        # Setup mock
        self.mock_get_tenant.return_value = self.mock_public_tenant
        
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'localhost'
        
        # Add tenant attribute to request
        request.tenant = self.mock_public_tenant
        
        # Process the request
        self.middleware.process_request(request)
        
        # Verify the request has the correct attributes
        self.assertTrue(hasattr(request, 'is_public'))
        self.assertTrue(request.is_public)
        self.mock_get_tenant.assert_called_once()

    def test_tenant_schema_request(self):
        """Test that requests to a tenant schema are handled correctly"""
        # Create a request with a tenant hostname
        request = self.factory.get('/')
        request.META['HTTP_HOST'] = 'tenant.localhost'
        
        # Create a mock tenant with a non-public schema name
        mock_tenant = MagicMock()
        mock_tenant.schema_name = 'test_tenant_schema'
        
        # Set up the mock to return our tenant
        self.mock_tenant_model.objects.get.return_value = mock_tenant
        
        # Mock the parent class's process_request to set the tenant on the request
        with patch('django_tenants.middleware.TenantMainMiddleware.process_request') as mock_super_process:
            def set_tenant(request):
                request.tenant = mock_tenant
            
            mock_super_process.side_effect = set_tenant
            
            # Process the request
            self.middleware.process_request(request)
        
        # Verify the request has the is_public attribute
        self.assertTrue(hasattr(request, 'is_public'))
        
        # Verify the tenant was set on the request
        self.assertEqual(request.tenant, mock_tenant)
        
        # The middleware should set is_public based on the tenant's schema name
        expected_public = (mock_tenant.schema_name == get_public_schema_name())
        self.assertEqual(request.is_public, expected_public)
        
    def tearDown(self):
        # Stop all patches
        self.get_tenant_patcher.stop()
        self.patcher.stop()
