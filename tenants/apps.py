from shaboom.ready import ReadyAppConfig

class TenantsConfig(ReadyAppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenants'
    
    def ready(self):
        # Call parent ready method to ensure proper initialization
        super().ready()
        
        # Defer connecting signals until Django is fully initialized
        self.defer_database_operation('tenants.signals', 'connect_signals')
