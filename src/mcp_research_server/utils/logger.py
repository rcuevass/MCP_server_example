"""Logging utilities for MCP Research Server."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from ..config import get_config


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{self.RESET}"


def setup_logger(
    name: str = "mcp_research_server",
    config: Optional[object] = None
) -> logging.Logger:
    """Set up logger with file and console handlers."""
    
    if config is None:
        config = get_config()
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, config.log_level))
    
    # Create formatters
    file_formatter = logging.Formatter(config.log_format)
    console_formatter = ColoredFormatter(config.log_format)
    
    # File handler with rotation
    log_file = config.logs_dir / f"{name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=config.log_max_bytes,
        backupCount=config.log_backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, config.log_level))
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "mcp_research_server") -> logging.Logger:
    """Get or create a logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")


def log_function_call(func):
    """Decorator to log function calls with arguments and results."""
    def wrapper(*args, **kwargs):
        logger = get_logger(f"{func.__module__}.{func.__name__}")
        
        # Log function call
        args_str = ", ".join([repr(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
        
        logger.debug(f"Calling {func.__name__}({all_args})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    
    return wrapper


def log_execution_time(func):
    """Decorator to log function execution time."""
    import time
    
    def wrapper(*args, **kwargs):
        logger = get_logger(f"{func.__module__}.{func.__name__}")
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.3f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f} seconds: {e}")
            raise
    
    return wrapper
