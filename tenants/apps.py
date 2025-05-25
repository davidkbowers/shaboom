from django.apps import AppConfig

class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenants'
    
    def ready(self):
        # Use a more reliable way to import signals
        # that won't cause database access during import
        import django
        if not getattr(django, 'setup_complete', False):
            return
            
        # Only import signals after Django is fully loaded
        from . import signals
        from django.apps import apps
        
        # Connect signals after Django is fully loaded
        signals.connect_signals()
