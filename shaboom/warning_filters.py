"""
Module to suppress specific Django warnings across the entire application.
"""
import warnings
import re

def suppress_db_init_warning():
    """
    Suppress Django's database access warning during app initialization.
    
    This should be called as early as possible in the application startup.
    """
    # Use a specific filter that only targets the database access warning
    warnings.filterwarnings(
        'ignore',
        message='Accessing the database during app initialization is discouraged',
        category=RuntimeWarning,
        module='django.db.backends.utils'
    )
