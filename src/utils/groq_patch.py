"""
Patch for the Groq client to fix the 'proxies' parameter issue.
"""

import importlib
from src.utils.logger import get_logger

logger = get_logger(__name__)

def patch_groq_client():
    """
    Patch the Groq client to fix the 'proxies' parameter issue.
    
    This function modifies the SyncHttpxClientWrapper.__init__ method
    to ignore the 'proxies' parameter that causes the TypeError.
    """
    try:
        # Import the base client module
        base_client = importlib.import_module('groq._base_client')
        
        # Get the SyncHttpxClientWrapper class
        wrapper_class = getattr(base_client, 'SyncHttpxClientWrapper', None)
        
        if wrapper_class:
            # Save the original __init__
            original_init = wrapper_class.__init__
            
            # Define a new __init__ that filters out the proxies parameter
            def new_init(self, *args, **kwargs):
                # Remove proxies if present
                if 'proxies' in kwargs:
                    logger.debug("Removing 'proxies' parameter from SyncHttpxClientWrapper kwargs")
                    del kwargs['proxies']
                return original_init(self, *args, **kwargs)
            
            # Replace the __init__ method
            wrapper_class.__init__ = new_init
            
            logger.info("Successfully patched Groq client")
            return True
        else:
            logger.warning("Could not find SyncHttpxClientWrapper class")
            return False
    
    except Exception as e:
        logger.error(f"Failed to patch Groq client: {e}")
        return False
