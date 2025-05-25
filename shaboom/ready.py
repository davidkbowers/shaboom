"""
Django app ready callback system to prevent early database access warnings.
"""
from django.apps import AppConfig
import importlib
import logging

logger = logging.getLogger(__name__)

_callbacks = []
_ready = False

def register_callback(callback):
    """
    Register a callback to be executed when Django is fully initialized.
    
    Args:
        callback: A callable to execute when Django is fully loaded.
    """
    global _ready, _callbacks
    
    if _ready:
        # If Django is already ready, execute the callback immediately
        try:
            callback()
        except Exception as e:
            logger.exception(f"Error executing callback: {e}")
    else:
        # Otherwise, store the callback for later execution
        _callbacks.append(callback)

def mark_ready():
    """Mark Django as ready and execute all registered callbacks."""
    global _ready, _callbacks
    
    _ready = True
    
    # Execute all registered callbacks
    for callback in _callbacks:
        try:
            callback()
        except Exception as e:
            logger.exception(f"Error executing callback: {e}")
    
    # Clear the callbacks list
    _callbacks = []

class ReadyAppConfig(AppConfig):
    """Base AppConfig that provides a safe ready method to avoid database warnings."""
    
    def ready(self):
        """
        Django's app ready method that ensures we don't access the database too early.
        
        Override this in your app's AppConfig and call super().ready() to ensure
        proper initialization order.
        """
        # Mark the app as ready
        from django.core.checks import registry
        
        # Register a callback to mark_ready when all checks are done
        def on_checks_ready(app_configs, **kwargs):
            mark_ready()
            return []
            
        registry.register(on_checks_ready)
        
    def defer_database_operation(self, module_path, function_name=None):
        """
        Defer a database operation until Django is fully initialized.
        
        Args:
            module_path: Path to the module containing the operation.
            function_name: Optional name of the function to call.
        """
        def callback():
            module = importlib.import_module(module_path)
            if function_name:
                getattr(module, function_name)()
        
        register_callback(callback)
