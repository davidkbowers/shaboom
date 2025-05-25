import warnings
import re
from django.core.management.commands.makemigrations import Command as MakemigrationsCommand


class Command(MakemigrationsCommand):
    """
    Custom command that runs makemigrations while suppressing the database
    access warning during app initialization.
    """
    
    help = "Create new migrations based on changes detected to your models, without database access warnings."
    
    def handle(self, *args, **options):
        # Add warning filter to ignore database access warnings
        with warnings.catch_warnings():
            warnings.filterwarnings(
                'ignore',
                message='Accessing the database during app initialization is discouraged',
                category=RuntimeWarning,
                module='django.db.backends.utils'
            )
            
            # Call the original makemigrations command
            return super().handle(*args, **options)
