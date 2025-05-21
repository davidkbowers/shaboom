import os
import sys
import django
from django.conf import settings

def run_tests():
    # Configure Django settings for tests
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shaboom.test_settings')
    
    # Initialize Django
    django.setup()
    
    # Import the test loader and runner
    from django.test.utils import get_runner
    from django.test.runner import DiscoverRunner
    
    # Create a test runner that doesn't create a test database
    class NoDbTestRunner(DiscoverRunner):
        def setup_databases(self, **kwargs):
            pass
            
        def teardown_databases(self, old_config, **kwargs):
            pass
    
    # Run the tests
    test_runner = NoDbTestRunner()
    failures = test_runner.run_tests(['tenants.test_middleware'])
    
    sys.exit(bool(failures))

if __name__ == '__main__':
    run_tests()
