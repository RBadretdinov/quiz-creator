"""
Comprehensive Error Handling and Validation System

This module provides robust error handling, input validation, and data integrity
checks for the quiz application.
"""

import logging
import traceback
import sys
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class QuizError(Exception):
    """Base exception class for quiz application errors."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details,
            'timestamp': self.timestamp
        }

class ValidationError(QuizError):
    """Exception raised for validation errors."""
    pass

class DataIntegrityError(QuizError):
    """Exception raised for data integrity issues."""
    pass

class FileOperationError(QuizError):
    """Exception raised for file operation errors."""
    pass

class DatabaseError(QuizError):
    """Exception raised for database operation errors."""
    pass

class UserInputError(QuizError):
    """Exception raised for user input errors."""
    pass

class SystemError(QuizError):
    """Exception raised for system-level errors."""
    pass

class ErrorHandler:
    """Comprehensive error handling system."""
    
    def __init__(self, log_file: str = "data/logs/error.log"):
        """Initialize error handler."""
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Error statistics
        self.error_stats = {
            'total_errors': 0,
            'error_types': {},
            'recent_errors': []
        }
        
        # Setup error logging
        self._setup_error_logging()
    
    def handle_error(self, error: Exception, context: str = None, user_friendly: bool = True) -> Dict[str, Any]:
        """
        Handle and log errors with appropriate response.
        
        Args:
            error: Exception to handle
            context: Additional context information
            user_friendly: Whether to return user-friendly error message
            
        Returns:
            Error response dictionary
        """
        # Log error
        self._log_error(error, context)
        
        # Update statistics
        self._update_error_stats(error)
        
        # Generate response
        if user_friendly:
            return self._generate_user_friendly_response(error)
        else:
            return self._generate_technical_response(error)
    
    def validate_input(self, value: Any, validation_rules: Dict[str, Any], field_name: str = None) -> bool:
        """
        Validate input against rules.
        
        Args:
            value: Value to validate
            validation_rules: Validation rules dictionary
            field_name: Name of field being validated
            
        Returns:
            True if valid, raises ValidationError if invalid
        """
        try:
            # Required field check
            if validation_rules.get('required', False) and (value is None or value == ''):
                raise ValidationError(f"Field '{field_name}' is required")
            
            # Type validation
            expected_type = validation_rules.get('type')
            if expected_type and not isinstance(value, expected_type):
                raise ValidationError(f"Field '{field_name}' must be of type {expected_type.__name__}")
            
            # String length validation
            if isinstance(value, str):
                min_length = validation_rules.get('min_length', 0)
                max_length = validation_rules.get('max_length')
                
                if len(value) < min_length:
                    raise ValidationError(f"Field '{field_name}' must be at least {min_length} characters")
                
                if max_length and len(value) > max_length:
                    raise ValidationError(f"Field '{field_name}' must be no more than {max_length} characters")
            
            # Numeric range validation
            if isinstance(value, (int, float)):
                min_value = validation_rules.get('min_value')
                max_value = validation_rules.get('max_value')
                
                if min_value is not None and value < min_value:
                    raise ValidationError(f"Field '{field_name}' must be at least {min_value}")
                
                if max_value is not None and value > max_value:
                    raise ValidationError(f"Field '{field_name}' must be no more than {max_value}")
            
            # Custom validation
            custom_validator = validation_rules.get('validator')
            if custom_validator and not custom_validator(value):
                raise ValidationError(f"Field '{field_name}' failed custom validation")
            
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(f"Validation error for field '{field_name}': {str(e)}")
    
    def validate_question_data(self, question_data: Dict[str, Any]) -> bool:
        """Validate question data structure."""
        required_fields = ['question_text', 'question_type', 'answers', 'correct_answers']
        
        for field in required_fields:
            if field not in question_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate question text
        self.validate_input(
            question_data['question_text'],
            {'required': True, 'type': str, 'min_length': 1, 'max_length': 1000},
            'question_text'
        )
        
        # Validate question type
        valid_types = ['multiple_choice', 'true_false', 'select_all']
        if question_data['question_type'] not in valid_types:
            raise ValidationError(f"Invalid question type: {question_data['question_type']}")
        
        # Validate answers
        answers = question_data['answers']
        if not isinstance(answers, list) or len(answers) < 2:
            raise ValidationError("Answers must be a list with at least 2 items")
        
        # Validate correct answers
        correct_answers = question_data['correct_answers']
        if not isinstance(correct_answers, list):
            raise ValidationError("Correct answers must be a list")
        
        if question_data['question_type'] == 'multiple_choice' and len(correct_answers) != 1:
            raise ValidationError("Multiple choice questions must have exactly one correct answer")
        
        return True
    
    def validate_tag_data(self, tag_data: Dict[str, Any]) -> bool:
        """Validate tag data structure."""
        required_fields = ['name', 'description']
        
        for field in required_fields:
            if field not in tag_data:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate tag name
        self.validate_input(
            tag_data['name'],
            {'required': True, 'type': str, 'min_length': 1, 'max_length': 50},
            'name'
        )
        
        # Validate description
        self.validate_input(
            tag_data['description'],
            {'required': True, 'type': str, 'min_length': 1, 'max_length': 200},
            'description'
        )
        
        return True
    
    def validate_file_operation(self, file_path: str, operation: str) -> bool:
        """Validate file operation."""
        try:
            path = Path(file_path)
            
            if operation == 'read':
                if not path.exists():
                    raise FileOperationError(f"File does not exist: {file_path}")
                if not path.is_file():
                    raise FileOperationError(f"Path is not a file: {file_path}")
                if not os.access(file_path, os.R_OK):
                    raise FileOperationError(f"No read permission for file: {file_path}")
            
            elif operation == 'write':
                parent_dir = path.parent
                if not parent_dir.exists():
                    parent_dir.mkdir(parents=True, exist_ok=True)
                if not os.access(parent_dir, os.W_OK):
                    raise FileOperationError(f"No write permission for directory: {parent_dir}")
            
            return True
            
        except Exception as e:
            raise FileOperationError(f"File operation validation failed: {str(e)}")
    
    def validate_database_operation(self, operation: str, table: str, data: Dict[str, Any] = None) -> bool:
        """Validate database operation."""
        try:
            if operation == 'insert':
                if not data:
                    raise DatabaseError("Data required for insert operation")
                
                # Validate required fields based on table
                if table == 'questions':
                    required_fields = ['question_text', 'question_type', 'answers', 'correct_answers']
                elif table == 'tags':
                    required_fields = ['name', 'description']
                else:
                    required_fields = []
                
                for field in required_fields:
                    if field not in data:
                        raise DatabaseError(f"Missing required field for {table}: {field}")
            
            return True
            
        except Exception as e:
            raise DatabaseError(f"Database operation validation failed: {str(e)}")
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            'total_errors': self.error_stats['total_errors'],
            'error_types': self.error_stats['error_types'],
            'recent_errors': self.error_stats['recent_errors'][-10:],  # Last 10 errors
            'most_common_error': max(self.error_stats['error_types'].items(), key=lambda x: x[1])[0] if self.error_stats['error_types'] else None
        }
    
    def clear_error_log(self) -> None:
        """Clear error log file."""
        try:
            if self.log_file.exists():
                self.log_file.unlink()
            logger.info("Error log cleared")
        except Exception as e:
            logger.error(f"Error clearing log file: {e}")
    
    def _setup_error_logging(self) -> None:
        """Setup error logging configuration."""
        try:
            # Create error log handler
            error_handler = logging.FileHandler(self.log_file)
            error_handler.setLevel(logging.ERROR)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            error_handler.setFormatter(formatter)
            
            # Add handler to logger
            logger.addHandler(error_handler)
            
        except Exception as e:
            print(f"Error setting up logging: {e}")
    
    def _log_error(self, error: Exception, context: str = None) -> None:
        """Log error with context."""
        try:
            error_info = {
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context,
                'timestamp': datetime.now().isoformat(),
                'traceback': traceback.format_exc()
            }
            
            logger.error(f"Error occurred: {json.dumps(error_info, indent=2)}")
            
        except Exception as e:
            print(f"Error logging failed: {e}")
    
    def _update_error_stats(self, error: Exception) -> None:
        """Update error statistics."""
        error_type = type(error).__name__
        
        self.error_stats['total_errors'] += 1
        self.error_stats['error_types'][error_type] = self.error_stats['error_types'].get(error_type, 0) + 1
        
        # Add to recent errors
        self.error_stats['recent_errors'].append({
            'error_type': error_type,
            'message': str(error),
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 errors
        if len(self.error_stats['recent_errors']) > 100:
            self.error_stats['recent_errors'] = self.error_stats['recent_errors'][-100:]
    
    def _generate_user_friendly_response(self, error: Exception) -> Dict[str, Any]:
        """Generate user-friendly error response."""
        if isinstance(error, ValidationError):
            return {
                'success': False,
                'error_type': 'validation',
                'message': 'Please check your input and try again.',
                'details': str(error)
            }
        elif isinstance(error, FileOperationError):
            return {
                'success': False,
                'error_type': 'file_operation',
                'message': 'There was a problem with the file operation. Please try again.',
                'details': 'File operation failed'
            }
        elif isinstance(error, DatabaseError):
            return {
                'success': False,
                'error_type': 'database',
                'message': 'There was a problem with the database. Please try again.',
                'details': 'Database operation failed'
            }
        else:
            return {
                'success': False,
                'error_type': 'system',
                'message': 'An unexpected error occurred. Please try again.',
                'details': 'System error'
            }
    
    def _generate_technical_response(self, error: Exception) -> Dict[str, Any]:
        """Generate technical error response."""
        return {
            'success': False,
            'error_type': type(error).__name__,
            'message': str(error),
            'details': {
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }
        }

class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_question_text(text: str) -> bool:
        """Validate question text."""
        if not text or not isinstance(text, str):
            return False
        if len(text.strip()) < 1:
            return False
        if len(text) > 1000:
            return False
        return True
    
    @staticmethod
    def validate_answer_options(answers: List[str]) -> bool:
        """Validate answer options."""
        if not isinstance(answers, list):
            return False
        if len(answers) < 2:
            return False
        for answer in answers:
            if not isinstance(answer, str) or len(answer.strip()) < 1:
                return False
        return True
    
    @staticmethod
    def validate_correct_answers(correct_answers: List[int], total_answers: int) -> bool:
        """Validate correct answer indices."""
        if not isinstance(correct_answers, list):
            return False
        for index in correct_answers:
            if not isinstance(index, int) or index < 0 or index >= total_answers:
                return False
        return True
    
    @staticmethod
    def validate_tag_name(name: str) -> bool:
        """Validate tag name."""
        if not name or not isinstance(name, str):
            return False
        if len(name.strip()) < 1 or len(name) > 50:
            return False
        return True
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """Validate file path."""
        try:
            path = Path(file_path)
            return path.is_absolute() or path.is_relative_to(Path.cwd())
        except:
            return False

class DataIntegrityChecker:
    """Data integrity checking utilities."""
    
    @staticmethod
    def check_question_integrity(question_data: Dict[str, Any]) -> bool:
        """Check question data integrity."""
        try:
            # Check required fields
            required_fields = ['question_text', 'question_type', 'answers', 'correct_answers']
            for field in required_fields:
                if field not in question_data:
                    return False
            
            # Check data types
            if not isinstance(question_data['question_text'], str):
                return False
            if not isinstance(question_data['answers'], list):
                return False
            if not isinstance(question_data['correct_answers'], list):
                return False
            
            # Check answer indices
            total_answers = len(question_data['answers'])
            for index in question_data['correct_answers']:
                if not isinstance(index, int) or index < 0 or index >= total_answers:
                    return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def check_tag_integrity(tag_data: Dict[str, Any]) -> bool:
        """Check tag data integrity."""
        try:
            # Check required fields
            required_fields = ['name', 'description']
            for field in required_fields:
                if field not in tag_data:
                    return False
            
            # Check data types
            if not isinstance(tag_data['name'], str):
                return False
            if not isinstance(tag_data['description'], str):
                return False
            
            return True
            
        except Exception:
            return False
    
    @staticmethod
    def check_file_integrity(file_path: str) -> bool:
        """Check file integrity."""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                return False
            
            # Check file size (not too large)
            file_size = os.path.getsize(file_path)
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                return False
            
            return True
            
        except Exception:
            return False

# Global error handler instance
error_handler = ErrorHandler()

def handle_error(error: Exception, context: str = None, user_friendly: bool = True) -> Dict[str, Any]:
    """Global error handling function."""
    return error_handler.handle_error(error, context, user_friendly)

def validate_input(value: Any, validation_rules: Dict[str, Any], field_name: str = None) -> bool:
    """Global input validation function."""
    return error_handler.validate_input(value, validation_rules, field_name)
