"""
Logging Configuration Module

This module provides comprehensive logging configuration for the Quiz Application
with support for different log levels, file rotation, and structured logging.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class LoggingConfig:
    """Handles logging configuration and setup."""
    
    def __init__(self, app_name: str = "quiz_app", log_dir: str = "logs"):
        """
        Initialize logging configuration.
        
        Args:
            app_name: Name of the application for log files
            log_dir: Directory to store log files
        """
        self.app_name = app_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Log file paths
        self.main_log = self.log_dir / f"{app_name}.log"
        self.error_log = self.log_dir / f"{app_name}_errors.log"
        self.debug_log = self.log_dir / f"{app_name}_debug.log"
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up comprehensive logging configuration."""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler (INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        
        # Main log file handler (INFO and above, with rotation)
        main_handler = logging.handlers.RotatingFileHandler(
            self.main_log,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(main_handler)
        
        # Error log file handler (ERROR and above)
        error_handler = logging.handlers.RotatingFileHandler(
            self.error_log,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)
        
        # Debug log file handler (DEBUG and above, only in development)
        if self._is_development_mode():
            debug_handler = logging.handlers.RotatingFileHandler(
                self.debug_log,
                maxBytes=20*1024*1024,  # 20MB
                backupCount=2,
                encoding='utf-8'
            )
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(debug_handler)
        
        # Configure specific loggers
        self._configure_module_loggers()
        
        # Log startup message
        logger = logging.getLogger(__name__)
        logger.info(f"Logging system initialized - Logs: {self.log_dir}")
        logger.debug("Debug logging enabled")
    
    def _configure_module_loggers(self):
        """Configure specific module loggers with appropriate levels."""
        # Quiz engine logger
        quiz_logger = logging.getLogger('quiz_engine')
        quiz_logger.setLevel(logging.INFO)
        
        # Question manager logger
        question_logger = logging.getLogger('question_manager')
        question_logger.setLevel(logging.INFO)
        
        # Tag manager logger
        tag_logger = logging.getLogger('tag_manager')
        tag_logger.setLevel(logging.INFO)
        
        # OCR processor logger
        ocr_logger = logging.getLogger('ocr_processor')
        ocr_logger.setLevel(logging.INFO)
        
        # UI loggers
        ui_logger = logging.getLogger('ui')
        ui_logger.setLevel(logging.WARNING)  # Less verbose for UI
        
        # Model loggers
        model_logger = logging.getLogger('models')
        model_logger.setLevel(logging.DEBUG)
    
    def _is_development_mode(self) -> bool:
        """Check if running in development mode."""
        return (
            os.getenv('QUIZ_DEBUG', '').lower() in ('true', '1', 'yes') or
            os.getenv('ENVIRONMENT', '').lower() == 'development' or
            '--debug' in sys.argv
        )
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (usually __name__)
            
        Returns:
            Configured logger instance
        """
        return logging.getLogger(name)
    
    def set_log_level(self, level: str):
        """
        Set the global log level.
        
        Args:
            level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        numeric_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger().setLevel(numeric_level)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Log level changed to {level.upper()}")
    
    def log_system_info(self):
        """Log system information for debugging."""
        logger = logging.getLogger(__name__)
        
        logger.info("System Information:")
        logger.info(f"  Python version: {sys.version}")
        logger.info(f"  Platform: {sys.platform}")
        logger.info(f"  Working directory: {os.getcwd()}")
        logger.info(f"  Log directory: {self.log_dir.absolute()}")
        logger.info(f"  Development mode: {self._is_development_mode()}")
    
    def cleanup_old_logs(self, days_to_keep: int = 30):
        """
        Clean up old log files.
        
        Args:
            days_to_keep: Number of days to keep log files
        """
        logger = logging.getLogger(__name__)
        
        try:
            cutoff_time = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            deleted_count = 0
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time:
                    log_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old log files")
                
        except Exception as e:
            logger.error(f"Error cleaning up log files: {e}")

# Global logging configuration instance
_logging_config: Optional[LoggingConfig] = None

def setup_logging(app_name: str = "quiz_app", log_dir: str = "logs") -> LoggingConfig:
    """
    Set up global logging configuration.
    
    Args:
        app_name: Name of the application
        log_dir: Directory for log files
        
    Returns:
        LoggingConfig instance
    """
    global _logging_config
    _logging_config = LoggingConfig(app_name, log_dir)
    return _logging_config

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    if _logging_config is None:
        setup_logging()
    
    return _logging_config.get_logger(name)

def log_system_info():
    """Log system information."""
    if _logging_config:
        _logging_config.log_system_info()
