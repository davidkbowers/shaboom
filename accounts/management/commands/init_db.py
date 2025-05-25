from django.core.management.base import BaseCommand
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

class Command(BaseCommand):
    help = 'Initialize the database with the correct migration order'

    def handle(self, *args, **options):
        self.stdout.write('Initializing database with correct migration order...')
        
        # First, create the public schema tables
        with connection.schema_editor() as schema_editor:
            schema_editor.execute('CREATE SCHEMA IF NOT EXISTS public')
        
        # Apply migrations in the correct order
        self.call_command('migrate', 'contenttypes', verbosity=0)
        self.call_command('migrate', 'auth', verbosity=0)
        self.call_command('migrate', 'accounts', verbosity=0)
        self.call_command('migrate', 'admin', verbosity=0)
        self.call_command('migrate', 'sessions', verbosity=0)
        self.call_command('migrate', 'studio', verbosity=0)
        
        # Now apply tenant migrations
        self.call_command('migrate_schemas', '--shared')
        
        self.stdout.write(self.style.SUCCESS('Database initialized successfully!'))
    
    def call_command(self, name, *args, **kwargs):
        """Helper to call a management command"""
        from django.core.management import call_command
        self.stdout.write(f'Running {name}...')
        call_command(name, *args, **kwargs)
