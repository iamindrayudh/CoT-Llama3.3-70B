"""
This module provides logging functionality for the application.
"""

import logging
import sys
from typing import Optional

from src.config import LOG_LEVEL

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name and level.
    
    Args:
        name: The name of the logger
        level: The logging level (defaults to LOG_LEVEL from config)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Set level from parameter or config
    log_level = level or LOG_LEVEL
    logger.setLevel(getattr(logging, log_level))
    
    # Create handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
