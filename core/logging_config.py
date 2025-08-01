"""
Centralized logging configuration for the image translation system.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    console_output: bool = True,
    file_output: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """
    Setup comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        console_output: Enable console logging
        file_output: Enable file logging
        max_file_size: Maximum log file size in bytes
        backup_count: Number of backup log files to keep
    """
    # Create logs directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File handlers
    if file_output:
        # General application log
        app_log_file = log_path / "app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        app_handler.setLevel(numeric_level)
        app_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(app_handler)
        
        # Error-only log
        error_log_file = log_path / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Performance log (handled by PerformanceMonitor)
        # Memory log (handled by MemoryTracker)
    
    # Configure specific loggers
    configure_module_loggers(numeric_level)
    
    logging.info(f"Logging configured - Level: {log_level}, Dir: {log_dir}")


def configure_module_loggers(log_level: int):
    """Configure logging for specific modules."""
    
    # Image processing logger
    img_logger = logging.getLogger('core.image_processor')
    img_logger.setLevel(log_level)
    
    # Translation logger
    trans_logger = logging.getLogger('core.translator')
    trans_logger.setLevel(log_level)
    
    # OCR logger
    ocr_logger = logging.getLogger('core.ocr_engine')
    ocr_logger.setLevel(log_level)
    
    # Memory tracker logger
    memory_logger = logging.getLogger('core.memory_tracker')
    memory_logger.setLevel(log_level)
    
    # Performance monitor logger
    perf_logger = logging.getLogger('core.performance_monitor')
    perf_logger.setLevel(log_level)
    
    # Streamlit logger (reduce verbosity)
    streamlit_logger = logging.getLogger('streamlit')
    streamlit_logger.setLevel(logging.WARNING)
    
    # PIL logger (reduce verbosity)
    pil_logger = logging.getLogger('PIL')
    pil_logger.setLevel(logging.WARNING)
    
    # OpenCV logger (reduce verbosity) 
    cv2_logger = logging.getLogger('cv2')
    cv2_logger.setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_system_info():
    """Log system information for debugging."""
    logger = get_logger(__name__)
    
    try:
        import platform
        import psutil
        
        logger.info("=== System Information ===")
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Python: {platform.python_version()}")
        logger.info(f"CPU Count: {psutil.cpu_count()}")
        logger.info(f"Memory: {psutil.virtual_memory().total // (1024**3)}GB total")
        logger.info(f"Working Directory: {os.getcwd()}")
        
        # Log environment variables (excluding sensitive ones)
        sensitive_keys = ['KEY', 'SECRET', 'TOKEN', 'PASSWORD']
        env_vars = {
            k: v for k, v in os.environ.items() 
            if not any(sensitive in k.upper() for sensitive in sensitive_keys)
        }
        logger.debug(f"Environment variables: {len(env_vars)} set")
        
    except Exception as e:
        logger.error(f"Failed to log system info: {e}")


def setup_error_handling():
    """Setup global error handling and logging."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = get_logger("uncaught_exception")
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception


class LoggingContext:
    """Context manager for temporary logging configuration changes."""
    
    def __init__(self, logger_name: str, level: int):
        self.logger = logging.getLogger(logger_name)
        self.original_level = self.logger.level
        self.new_level = level
    
    def __enter__(self):
        self.logger.setLevel(self.new_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)


def with_logging(log_level: str = "INFO"):
    """
    Decorator to setup logging for a function.
    
    Args:
        log_level: Temporary log level for the function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Setup logging if not already configured
            if not logging.getLogger().handlers:
                setup_logging(log_level)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Utility functions for common logging patterns
def log_function_call(logger: logging.Logger, func_name: str, *args, **kwargs):
    """Log function call with arguments."""
    args_str = ', '.join(str(arg) for arg in args)
    kwargs_str = ', '.join(f"{k}={v}" for k, v in kwargs.items())
    all_args = ', '.join(filter(None, [args_str, kwargs_str]))
    logger.debug(f"Calling {func_name}({all_args})")


def log_execution_time(logger: logging.Logger, operation: str, duration: float):
    """Log execution time for an operation."""
    logger.info(f"{operation} completed in {duration:.3f}s")


def log_memory_usage(logger: logging.Logger, operation: str, memory_mb: float):
    """Log memory usage for an operation."""
    logger.info(f"{operation} memory usage: {memory_mb:.1f}MB")


def log_error_with_context(logger: logging.Logger, error: Exception, context: dict):
    """Log error with additional context."""
    logger.error(f"Error: {error}", extra={"context": context}, exc_info=True)