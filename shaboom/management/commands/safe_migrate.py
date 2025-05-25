import warnings
import re
from django.core.management.commands.migrate import Command as MigrateCommand


class Command(MigrateCommand):
    """
    Custom command that runs migrate while suppressing the database
    access warning during app initialization.
    """
    
    help = "Synchronizes the database state with your current models and migrations, without database access warnings."
    
    def handle(self, *args, **options):
        # Add warning filter to ignore database access warnings
        with warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                message='Accessing the database during app initialization is discouraged',
                category=RuntimeWarning,
                module='django.db.backends.utils'
            )
            
            # Call the original migrate command
            return super().handle(*args, **options)
