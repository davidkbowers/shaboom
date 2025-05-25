from django.apps import AppConfig


class StudioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'studio'
    verbose_name = 'Studio Management'

    def ready(self):
        # Import signals to register them
        import studio.signals  # noqa
