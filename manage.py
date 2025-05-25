#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Suppress database access warning before anything else happens
    try:
        # Try to import our warning suppression module
        from shaboom.warning_filters import suppress_db_init_warning
        suppress_db_init_warning()
    except ImportError:
        # If it fails, we can continue without it
        pass
        
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shaboom.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
