from django.test.runner import DiscoverRunner

class NoDbTestRunner(DiscoverRunner):
    """A test runner that doesn't create a test database."""
    def setup_databases(self, **kwargs):
        # Override database creation
        pass

    def teardown_databases(self, old_config, **kwargs):
        # Override database teardown
        pass
