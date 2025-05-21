from .settings import *

# Override settings for testing
DEBUG = False
TESTING = True

# Use the development database directly
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'shaboom',  # Use the development database directly
        'USER': 'dave',
        'PASSWORD': 'punter89',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'shaboom',  # Use the same database for tests
        },
    }
}

# Disable migrations during testing
MIGRATION_MODULES = {}

# Disable logging for tests
import logging
logging.disable(logging.CRITICAL)

# Disable debug toolbar for tests
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

# Disable cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Use a faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable password validation during testing
AUTH_PASSWORD_VALIDATORS = []

# Use our custom test runner that doesn't create a test database
TEST_RUNNER = 'shaboom.test_runner.NoDbTestRunner'

# Disable migrations during testing
class DisableMigrations(object):
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return "notmigrations"

MIGRATION_MODULES = DisableMigrations()
