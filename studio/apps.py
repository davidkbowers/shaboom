from shaboom.ready import ReadyAppConfig


class StudioConfig(ReadyAppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studio'
    verbose_name = 'Studio Management'

    def ready(self):
        # Call parent ready method to ensure proper initialization
        super().ready()
        
        # Defer connecting signals until Django is fully initialized
        self.defer_database_operation('studio.signals', 'connect_signals')
