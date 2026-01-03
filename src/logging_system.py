"""
Enhanced Logging System

This module provides comprehensive logging functionality for the quiz application
including error tracking, performance monitoring, and audit trails.
"""

import logging
import logging.handlers
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import traceback

class QuizLogger:
    """Enhanced logging system for quiz application."""
    
    def __init__(self, log_dir: str = "data/logs"):
        """Initialize logging system."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log rotation settings
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.backup_count = 5
        
        # Log file paths
        self.error_log = self.log_dir / "error.log"
        self.info_log = self.log_dir / "info.log"
        self.debug_log = self.log_dir / "debug.log"
        self.audit_log = self.log_dir / "audit.log"
        self.performance_log = self.log_dir / "performance.log"
        
        # Setup loggers
        self._setup_loggers()
        
        # Performance tracking
        self.performance_data = []
    
    def _setup_loggers(self) -> None:
        """Setup all loggers with appropriate handlers."""
        # Error logger
        self.error_logger = self._create_logger(
            'error',
            self.error_log,
            logging.ERROR,
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Info logger
        self.info_logger = self._create_logger(
            'info',
            self.info_log,
            logging.INFO,
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Debug logger
        self.debug_logger = self._create_logger(
            'debug',
            self.debug_log,
            logging.DEBUG,
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Audit logger
        self.audit_logger = self._create_logger(
            'audit',
            self.audit_log,
            logging.INFO,
            '%(asctime)s - %(message)s'
        )
        
        # Performance logger
        self.performance_logger = self._create_logger(
            'performance',
            self.performance_log,
            logging.INFO,
            '%(asctime)s - %(message)s'
        )
    
    def _create_logger(self, name: str, log_file: Path, level: int, format_string: str) -> logging.Logger:
        """Create a logger with file handler."""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create rotating file handler
        handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_log_size,
            backupCount=self.backup_count
        )
        handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger
    
    def log_error(self, message: str, error: Exception = None, context: Dict[str, Any] = None) -> None:
        """Log error with context."""
        try:
            log_data = {
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }
            
            if error:
                log_data.update({
                    'error_type': type(error).__name__,
                    'error_message': str(error),
                    'traceback': traceback.format_exc()
                })
            
            self.error_logger.error(json.dumps(log_data, indent=2))
            
        except Exception as e:
            print(f"Error logging failed: {e}")
    
    def log_info(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log info message."""
        try:
            log_data = {
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }
            
            self.info_logger.info(json.dumps(log_data, indent=2))
            
        except Exception as e:
            print(f"Info logging failed: {e}")
    
    def log_debug(self, message: str, context: Dict[str, Any] = None) -> None:
        """Log debug message."""
        try:
            log_data = {
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }
            
            self.debug_logger.debug(json.dumps(log_data, indent=2))
            
        except Exception as e:
            print(f"Debug logging failed: {e}")
    
    def log_audit(self, action: str, user: str = None, details: Dict[str, Any] = None) -> None:
        """Log audit trail."""
        try:
            audit_data = {
                'action': action,
                'user': user or 'system',
                'timestamp': datetime.now().isoformat(),
                'details': details or {}
            }
            
            self.audit_logger.info(json.dumps(audit_data, indent=2))
            
        except Exception as e:
            print(f"Audit logging failed: {e}")
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None) -> None:
        """Log performance metrics."""
        try:
            performance_data = {
                'operation': operation,
                'duration': duration,
                'timestamp': datetime.now().isoformat(),
                'details': details or {}
            }
            
            self.performance_logger.info(json.dumps(performance_data, indent=2))
            
            # Store for analysis
            self.performance_data.append(performance_data)
            
            # Keep only last 1000 entries
            if len(self.performance_data) > 1000:
                self.performance_data = self.performance_data[-1000:]
            
        except Exception as e:
            print(f"Performance logging failed: {e}")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        try:
            stats = {
                'log_files': {},
                'performance_summary': {},
                'error_summary': {}
            }
            
            # Check log file sizes
            for log_file in [self.error_log, self.info_log, self.debug_log, self.audit_log, self.performance_log]:
                if log_file.exists():
                    stats['log_files'][log_file.name] = {
                        'size': log_file.stat().st_size,
                        'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                    }
            
            # Performance summary
            if self.performance_data:
                durations = [entry['duration'] for entry in self.performance_data]
                stats['performance_summary'] = {
                    'total_operations': len(self.performance_data),
                    'average_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations)
                }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup_old_logs(self, days: int = 30) -> None:
        """Clean up log files older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    self.log_info(f"Cleaned up old log file: {log_file.name}")
            
        except Exception as e:
            self.log_error(f"Error cleaning up logs: {e}")
    
    def export_logs(self, output_file: str, log_type: str = 'all') -> bool:
        """Export logs to file."""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                if log_type == 'all' or log_type == 'error':
                    if self.error_log.exists():
                        f.write("=== ERROR LOG ===\n")
                        f.write(self.error_log.read_text(encoding='utf-8'))
                        f.write("\n\n")
                
                if log_type == 'all' or log_type == 'info':
                    if self.info_log.exists():
                        f.write("=== INFO LOG ===\n")
                        f.write(self.info_log.read_text(encoding='utf-8'))
                        f.write("\n\n")
                
                if log_type == 'all' or log_type == 'audit':
                    if self.audit_log.exists():
                        f.write("=== AUDIT LOG ===\n")
                        f.write(self.audit_log.read_text(encoding='utf-8'))
                        f.write("\n\n")
                
                if log_type == 'all' or log_type == 'performance':
                    if self.performance_log.exists():
                        f.write("=== PERFORMANCE LOG ===\n")
                        f.write(self.performance_log.read_text(encoding='utf-8'))
                        f.write("\n\n")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error exporting logs: {e}")
            return False

class PerformanceMonitor:
    """Performance monitoring utilities."""
    
    def __init__(self, logger: QuizLogger):
        """Initialize performance monitor."""
        self.logger = logger
        self.start_times = {}
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_times[operation] = datetime.now()
    
    def end_timer(self, operation: str, details: Dict[str, Any] = None) -> float:
        """End timing an operation and log performance."""
        if operation not in self.start_times:
            return 0.0
        
        start_time = self.start_times[operation]
        duration = (datetime.now() - start_time).total_seconds()
        
        # Log performance
        self.logger.log_performance(operation, duration, details)
        
        # Clean up
        del self.start_times[operation]
        
        return duration
    
    def measure_operation(self, operation: str, func: callable, *args, **kwargs) -> Any:
        """Measure the performance of an operation."""
        self.start_timer(operation)
        try:
            result = func(*args, **kwargs)
            self.end_timer(operation, {'success': True})
            return result
        except Exception as e:
            self.end_timer(operation, {'success': False, 'error': str(e)})
            raise

class AuditTrail:
    """Audit trail utilities."""
    
    def __init__(self, logger: QuizLogger):
        """Initialize audit trail."""
        self.logger = logger
    
    def log_question_creation(self, question_id: str, user: str = None) -> None:
        """Log question creation."""
        self.logger.log_audit(
            'question_created',
            user,
            {'question_id': question_id}
        )
    
    def log_question_update(self, question_id: str, user: str = None) -> None:
        """Log question update."""
        self.logger.log_audit(
            'question_updated',
            user,
            {'question_id': question_id}
        )
    
    def log_question_deletion(self, question_id: str, user: str = None) -> None:
        """Log question deletion."""
        self.logger.log_audit(
            'question_deleted',
            user,
            {'question_id': question_id}
        )
    
    def log_quiz_session(self, session_id: str, user: str = None, score: float = None) -> None:
        """Log quiz session."""
        self.logger.log_audit(
            'quiz_session',
            user,
            {'session_id': session_id, 'score': score}
        )
    
    def log_data_export(self, file_path: str, format_type: str, user: str = None) -> None:
        """Log data export."""
        self.logger.log_audit(
            'data_exported',
            user,
            {'file_path': file_path, 'format': format_type}
        )
    
    def log_data_import(self, file_path: str, format_type: str, user: str = None) -> None:
        """Log data import."""
        self.logger.log_audit(
            'data_imported',
            user,
            {'file_path': file_path, 'format': format_type}
        )

# Global logger instance
quiz_logger = QuizLogger()
performance_monitor = PerformanceMonitor(quiz_logger)
audit_trail = AuditTrail(quiz_logger)

def log_error(message: str, error: Exception = None, context: Dict[str, Any] = None) -> None:
    """Global error logging function."""
    quiz_logger.log_error(message, error, context)

def log_info(message: str, context: Dict[str, Any] = None) -> None:
    """Global info logging function."""
    quiz_logger.log_info(message, context)

def log_debug(message: str, context: Dict[str, Any] = None) -> None:
    """Global debug logging function."""
    quiz_logger.log_debug(message, context)

def log_audit(action: str, user: str = None, details: Dict[str, Any] = None) -> None:
    """Global audit logging function."""
    quiz_logger.log_audit(action, user, details)

def log_performance(operation: str, duration: float, details: Dict[str, Any] = None) -> None:
    """Global performance logging function."""
    quiz_logger.log_performance(operation, duration, details)
