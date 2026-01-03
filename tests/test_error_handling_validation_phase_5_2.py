"""
Comprehensive Test Suite for Phase 5.2: Error Handling & Validation

This module tests the error handling, validation, and logging systems
implemented in Phase 5.2.
"""

import unittest
import sys
import os
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from error_handling import (
    QuizError, ValidationError, DataIntegrityError, FileOperationError,
    DatabaseError, UserInputError, SystemError, ErrorHandler,
    InputValidator, DataIntegrityChecker, error_handler, handle_error, validate_input
)
from ui.error_feedback import ErrorFeedback, ValidationFeedback, ProgressIndicator
from logging_system import QuizLogger, PerformanceMonitor, AuditTrail

class TestErrorHandling(unittest.TestCase):
    """Test error handling system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize error handler
        self.error_handler = ErrorHandler(os.path.join(self.data_dir, 'error.log'))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_quiz_error_creation(self):
        """Test QuizError creation."""
        error = QuizError("Test error", "TEST001", {"field": "value"})
        
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.error_code, "TEST001")
        self.assertEqual(error.details, {"field": "value"})
        self.assertIsNotNone(error.timestamp)
    
    def test_quiz_error_to_dict(self):
        """Test QuizError serialization."""
        error = QuizError("Test error", "TEST001", {"field": "value"})
        error_dict = error.to_dict()
        
        self.assertEqual(error_dict['error_type'], 'QuizError')
        self.assertEqual(error_dict['message'], 'Test error')
        self.assertEqual(error_dict['error_code'], 'TEST001')
        self.assertEqual(error_dict['details'], {"field": "value"})
        self.assertIn('timestamp', error_dict)
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Validation failed")
        
        self.assertIsInstance(error, QuizError)
        self.assertEqual(error.message, "Validation failed")
    
    def test_data_integrity_error(self):
        """Test DataIntegrityError."""
        error = DataIntegrityError("Data integrity violation")
        
        self.assertIsInstance(error, QuizError)
        self.assertEqual(error.message, "Data integrity violation")
    
    def test_file_operation_error(self):
        """Test FileOperationError."""
        error = FileOperationError("File operation failed")
        
        self.assertIsInstance(error, QuizError)
        self.assertEqual(error.message, "File operation failed")
    
    def test_database_error(self):
        """Test DatabaseError."""
        error = DatabaseError("Database operation failed")
        
        self.assertIsInstance(error, QuizError)
        self.assertEqual(error.message, "Database operation failed")
    
    def test_user_input_error(self):
        """Test UserInputError."""
        error = UserInputError("Invalid user input")
        
        self.assertIsInstance(error, QuizError)
        self.assertEqual(error.message, "Invalid user input")
    
    def test_system_error(self):
        """Test SystemError."""
        error = SystemError("System error occurred")
        
        self.assertIsInstance(error, QuizError)
        self.assertEqual(error.message, "System error occurred")
    
    def test_error_handler_initialization(self):
        """Test ErrorHandler initialization."""
        self.assertIsNotNone(self.error_handler)
        self.assertIsInstance(self.error_handler.error_stats, dict)
        self.assertEqual(self.error_handler.error_stats['total_errors'], 0)
    
    def test_handle_error_validation(self):
        """Test error handling for validation errors."""
        error = ValidationError("Invalid input")
        response = self.error_handler.handle_error(error, "test_context")
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error_type'], 'validation')
        self.assertIn('Please check your input', response['message'])
    
    def test_handle_error_file_operation(self):
        """Test error handling for file operation errors."""
        error = FileOperationError("File not found")
        response = self.error_handler.handle_error(error, "file_operation")
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error_type'], 'file_operation')
        self.assertIn('file operation', response['message'])
    
    def test_handle_error_database(self):
        """Test error handling for database errors."""
        error = DatabaseError("Connection failed")
        response = self.error_handler.handle_error(error, "database_operation")
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error_type'], 'database')
        self.assertIn('database', response['message'])
    
    def test_handle_error_system(self):
        """Test error handling for system errors."""
        error = SystemError("System failure")
        response = self.error_handler.handle_error(error, "system")
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error_type'], 'system')
        self.assertIn('unexpected error', response['message'])
    
    def test_validate_input_required(self):
        """Test input validation with required field."""
        # Test required field
        with self.assertRaises(ValidationError):
            self.error_handler.validate_input(None, {'required': True}, 'test_field')
        
        # Test valid required field
        result = self.error_handler.validate_input("test", {'required': True}, 'test_field')
        self.assertTrue(result)
    
    def test_validate_input_type(self):
        """Test input validation with type checking."""
        # Test correct type
        result = self.error_handler.validate_input("test", {'type': str}, 'test_field')
        self.assertTrue(result)
        
        # Test incorrect type
        with self.assertRaises(ValidationError):
            self.error_handler.validate_input(123, {'type': str}, 'test_field')
    
    def test_validate_input_string_length(self):
        """Test input validation with string length."""
        # Test minimum length
        with self.assertRaises(ValidationError):
            self.error_handler.validate_input("a", {'min_length': 2}, 'test_field')
        
        # Test maximum length
        with self.assertRaises(ValidationError):
            self.error_handler.validate_input("a" * 101, {'max_length': 100}, 'test_field')
        
        # Test valid length
        result = self.error_handler.validate_input("test", {'min_length': 1, 'max_length': 10}, 'test_field')
        self.assertTrue(result)
    
    def test_validate_input_numeric_range(self):
        """Test input validation with numeric range."""
        # Test minimum value
        with self.assertRaises(ValidationError):
            self.error_handler.validate_input(5, {'min_value': 10}, 'test_field')
        
        # Test maximum value
        with self.assertRaises(ValidationError):
            self.error_handler.validate_input(15, {'max_value': 10}, 'test_field')
        
        # Test valid range
        result = self.error_handler.validate_input(5, {'min_value': 1, 'max_value': 10}, 'test_field')
        self.assertTrue(result)
    
    def test_validate_question_data(self):
        """Test question data validation."""
        # Valid question data
        valid_data = {
            'question_text': 'What is 2+2?',
            'question_type': 'multiple_choice',
            'answers': ['3', '4', '5'],
            'correct_answers': [1]
        }
        
        result = self.error_handler.validate_question_data(valid_data)
        self.assertTrue(result)
        
        # Invalid question data - missing field
        invalid_data = {
            'question_text': 'What is 2+2?',
            'question_type': 'multiple_choice',
            'answers': ['3', '4', '5']
            # Missing correct_answers
        }
        
        with self.assertRaises(ValidationError):
            self.error_handler.validate_question_data(invalid_data)
    
    def test_validate_tag_data(self):
        """Test tag data validation."""
        # Valid tag data
        valid_data = {
            'name': 'math',
            'description': 'Mathematics questions'
        }
        
        result = self.error_handler.validate_tag_data(valid_data)
        self.assertTrue(result)
        
        # Invalid tag data - missing field
        invalid_data = {
            'name': 'math'
            # Missing description
        }
        
        with self.assertRaises(ValidationError):
            self.error_handler.validate_tag_data(invalid_data)
    
    def test_validate_file_operation(self):
        """Test file operation validation."""
        # Test read operation
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        result = self.error_handler.validate_file_operation(test_file, 'read')
        self.assertTrue(result)
        
        # Test write operation
        result = self.error_handler.validate_file_operation(test_file, 'write')
        self.assertTrue(result)
    
    def test_validate_database_operation(self):
        """Test database operation validation."""
        # Test insert operation
        data = {'name': 'test', 'value': 'test_value'}
        result = self.error_handler.validate_database_operation('insert', 'test_table', data)
        self.assertTrue(result)
        
        # Test insert with missing data
        with self.assertRaises(DatabaseError):
            self.error_handler.validate_database_operation('insert', 'test_table', None)
    
    def test_get_error_statistics(self):
        """Test error statistics."""
        # Generate some errors
        self.error_handler.handle_error(ValidationError("Test error 1"))
        self.error_handler.handle_error(ValidationError("Test error 2"))
        self.error_handler.handle_error(FileOperationError("Test error 3"))
        
        stats = self.error_handler.get_error_statistics()
        
        self.assertEqual(stats['total_errors'], 3)
        self.assertEqual(stats['error_types']['ValidationError'], 2)
        self.assertEqual(stats['error_types']['FileOperationError'], 1)
        self.assertEqual(len(stats['recent_errors']), 3)
    
    def test_clear_error_log(self):
        """Test error log clearing."""
        # Generate an error to create log
        self.error_handler.handle_error(ValidationError("Test error"))
        
        # Clear log
        self.error_handler.clear_error_log()
        
        # Log file should be removed or empty
        if self.error_handler.log_file.exists():
            self.assertEqual(self.error_handler.log_file.stat().st_size, 0)


class TestInputValidator(unittest.TestCase):
    """Test input validation utilities."""
    
    def test_validate_question_text(self):
        """Test question text validation."""
        # Valid text
        self.assertTrue(InputValidator.validate_question_text("What is 2+2?"))
        
        # Invalid text - empty
        self.assertFalse(InputValidator.validate_question_text(""))
        self.assertFalse(InputValidator.validate_question_text(None))
        
        # Invalid text - too long
        long_text = "A" * 1001
        self.assertFalse(InputValidator.validate_question_text(long_text))
    
    def test_validate_answer_options(self):
        """Test answer options validation."""
        # Valid options
        self.assertTrue(InputValidator.validate_answer_options(["A", "B", "C"]))
        
        # Invalid options - not a list
        self.assertFalse(InputValidator.validate_answer_options("not a list"))
        
        # Invalid options - too few
        self.assertFalse(InputValidator.validate_answer_options(["A"]))
        
        # Invalid options - empty option
        self.assertFalse(InputValidator.validate_answer_options(["A", ""]))
    
    def test_validate_correct_answers(self):
        """Test correct answers validation."""
        # Valid answers
        self.assertTrue(InputValidator.validate_correct_answers([0, 1], 3))
        
        # Invalid answers - not a list
        self.assertFalse(InputValidator.validate_correct_answers(0, 3))
        
        # Invalid answers - out of range
        self.assertFalse(InputValidator.validate_correct_answers([5], 3))
        
        # Invalid answers - negative index
        self.assertFalse(InputValidator.validate_correct_answers([-1], 3))
    
    def test_validate_tag_name(self):
        """Test tag name validation."""
        # Valid name
        self.assertTrue(InputValidator.validate_tag_name("math"))
        
        # Invalid name - empty
        self.assertFalse(InputValidator.validate_tag_name(""))
        self.assertFalse(InputValidator.validate_tag_name(None))
        
        # Invalid name - too long
        long_name = "A" * 51
        self.assertFalse(InputValidator.validate_tag_name(long_name))
    
    def test_validate_file_path(self):
        """Test file path validation."""
        # Valid path
        self.assertTrue(InputValidator.validate_file_path("test.txt"))
        self.assertTrue(InputValidator.validate_file_path("/absolute/path.txt"))
        
        # Invalid path - None
        self.assertFalse(InputValidator.validate_file_path(None))


class TestDataIntegrityChecker(unittest.TestCase):
    """Test data integrity checking."""
    
    def test_check_question_integrity(self):
        """Test question data integrity."""
        # Valid question data
        valid_data = {
            'question_text': 'What is 2+2?',
            'question_type': 'multiple_choice',
            'answers': ['3', '4', '5'],
            'correct_answers': [1]
        }
        
        self.assertTrue(DataIntegrityChecker.check_question_integrity(valid_data))
        
        # Invalid question data - missing field
        invalid_data = {
            'question_text': 'What is 2+2?',
            'question_type': 'multiple_choice',
            'answers': ['3', '4', '5']
            # Missing correct_answers
        }
        
        self.assertFalse(DataIntegrityChecker.check_question_integrity(invalid_data))
    
    def test_check_tag_integrity(self):
        """Test tag data integrity."""
        # Valid tag data
        valid_data = {
            'name': 'math',
            'description': 'Mathematics questions'
        }
        
        self.assertTrue(DataIntegrityChecker.check_tag_integrity(valid_data))
        
        # Invalid tag data - missing field
        invalid_data = {
            'name': 'math'
            # Missing description
        }
        
        self.assertFalse(DataIntegrityChecker.check_tag_integrity(invalid_data))
    
    def test_check_file_integrity(self):
        """Test file integrity."""
        # Create test file
        test_file = os.path.join(tempfile.mkdtemp(), 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        
        # Valid file
        self.assertTrue(DataIntegrityChecker.check_file_integrity(test_file))
        
        # Invalid file - doesn't exist
        self.assertFalse(DataIntegrityChecker.check_file_integrity('nonexistent.txt'))
        
        # Clean up
        os.unlink(test_file)


class TestErrorFeedback(unittest.TestCase):
    """Test error feedback system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.error_feedback = ErrorFeedback()
    
    def test_get_error_feedback(self):
        """Test error feedback generation."""
        # Test validation error
        feedback = self.error_feedback.get_error_feedback('validation')
        self.assertIn('check your input', feedback)
        
        # Test file operation error
        feedback = self.error_feedback.get_error_feedback('file_operation')
        self.assertIn('file operation', feedback)
        
        # Test database error
        feedback = self.error_feedback.get_error_feedback('database_operation')
        self.assertIn('database', feedback)
    
    def test_get_validation_feedback(self):
        """Test validation feedback."""
        # Test question text validation
        feedback = self.error_feedback.get_validation_feedback('question_text', 'required')
        self.assertIn('question', feedback)
        
        # Test answers validation
        feedback = self.error_feedback.get_validation_feedback('answers', 'too_few')
        self.assertIn('answer options', feedback)
    
    def test_get_success_feedback(self):
        """Test success feedback."""
        # Test question creation
        feedback = self.error_feedback.get_success_feedback('question_created')
        self.assertIn('created successfully', feedback)
        
        # Test quiz completion
        feedback = self.error_feedback.get_success_feedback('quiz_completed')
        self.assertIn('completed', feedback)
    
    def test_get_help_feedback(self):
        """Test help feedback."""
        # Test question creation help
        feedback = self.error_feedback.get_help_feedback('question_creation')
        self.assertIn('create a question', feedback)
        
        # Test quiz taking help
        feedback = self.error_feedback.get_help_feedback('quiz_taking')
        self.assertIn('take a quiz', feedback)
    
    def test_get_progress_feedback(self):
        """Test progress feedback."""
        # Test importing progress
        feedback = self.error_feedback.get_progress_feedback(5, 10, 'importing')
        self.assertIn('Importing', feedback)
        self.assertIn('5/10', feedback)
        self.assertIn('50.0%', feedback)
    
    def test_set_user_preferences(self):
        """Test user preferences."""
        preferences = {
            'show_detailed_errors': True,
            'suggest_solutions': False
        }
        
        self.error_feedback.set_user_preferences(preferences)
        
        self.assertTrue(self.error_feedback.user_preferences['show_detailed_errors'])
        self.assertFalse(self.error_feedback.user_preferences['suggest_solutions'])


class TestValidationFeedback(unittest.TestCase):
    """Test validation feedback utilities."""
    
    def test_get_field_validation_message(self):
        """Test field validation messages."""
        # Test question text validation
        message = ValidationFeedback.get_field_validation_message('question_text', 'required')
        self.assertIn('required', message)
        
        # Test answers validation
        message = ValidationFeedback.get_field_validation_message('answers', 'too_few')
        self.assertIn('answer options', message)


class TestProgressIndicator(unittest.TestCase):
    """Test progress indicator utilities."""
    
    def test_create_progress_bar(self):
        """Test progress bar creation."""
        # Test 50% progress
        bar = ProgressIndicator.create_progress_bar(5, 10, 10)
        self.assertIn('[', bar)
        self.assertIn(']', bar)
        self.assertIn('50.0%', bar)
        
        # Test 0% progress
        bar = ProgressIndicator.create_progress_bar(0, 10, 10)
        self.assertIn('0%', bar)
        
        # Test 100% progress
        bar = ProgressIndicator.create_progress_bar(10, 10, 10)
        self.assertIn('100.0%', bar)
    
    def test_create_spinner(self):
        """Test spinner creation."""
        # Test different positions
        spinner1 = ProgressIndicator.create_spinner(0, 10)
        spinner2 = ProgressIndicator.create_spinner(1, 10)
        spinner3 = ProgressIndicator.create_spinner(2, 10)
        spinner4 = ProgressIndicator.create_spinner(3, 10)
        
        self.assertIn(spinner1, '|/-\\')
        self.assertIn(spinner2, '|/-\\')
        self.assertIn(spinner3, '|/-\\')
        self.assertIn(spinner4, '|/-\\')


class TestLoggingSystem(unittest.TestCase):
    """Test logging system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = os.path.join(self.temp_dir, 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize logger
        self.logger = QuizLogger(self.log_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        self.assertIsNotNone(self.logger)
        self.assertIsNotNone(self.logger.error_logger)
        self.assertIsNotNone(self.logger.info_logger)
        self.assertIsNotNone(self.logger.debug_logger)
        self.assertIsNotNone(self.logger.audit_logger)
        self.assertIsNotNone(self.logger.performance_logger)
    
    def test_log_error(self):
        """Test error logging."""
        error = ValidationError("Test error")
        self.logger.log_error("Test error message", error, {"context": "test"})
        
        # Check if error log was created
        self.assertTrue(self.logger.error_log.exists())
    
    def test_log_info(self):
        """Test info logging."""
        self.logger.log_info("Test info message", {"context": "test"})
        
        # Check if info log was created
        self.assertTrue(self.logger.info_log.exists())
    
    def test_log_debug(self):
        """Test debug logging."""
        self.logger.log_debug("Test debug message", {"context": "test"})
        
        # Check if debug log was created
        self.assertTrue(self.logger.debug_log.exists())
    
    def test_log_audit(self):
        """Test audit logging."""
        self.logger.log_audit("test_action", "test_user", {"details": "test"})
        
        # Check if audit log was created
        self.assertTrue(self.logger.audit_log.exists())
    
    def test_log_performance(self):
        """Test performance logging."""
        self.logger.log_performance("test_operation", 1.5, {"details": "test"})
        
        # Check if performance log was created
        self.assertTrue(self.logger.performance_log.exists())
        
        # Check performance data
        self.assertEqual(len(self.logger.performance_data), 1)
        self.assertEqual(self.logger.performance_data[0]['operation'], 'test_operation')
        self.assertEqual(self.logger.performance_data[0]['duration'], 1.5)
    
    def test_get_log_statistics(self):
        """Test log statistics."""
        # Generate some logs
        self.logger.log_error("Test error")
        self.logger.log_info("Test info")
        self.logger.log_performance("test_op", 1.0)
        
        stats = self.logger.get_log_statistics()
        
        self.assertIn('log_files', stats)
        self.assertIn('performance_summary', stats)
        self.assertIn('error_summary', stats)
    
    def test_cleanup_old_logs(self):
        """Test log cleanup."""
        # Create old log file
        old_log = self.logger.error_log
        old_log.touch()
        
        # Clean up logs older than 0 days (should clean all)
        self.logger.cleanup_old_logs(0)
        
        # Log file should be removed
        self.assertFalse(old_log.exists())
    
    def test_export_logs(self):
        """Test log export."""
        # Generate some logs
        self.logger.log_error("Test error")
        self.logger.log_info("Test info")
        
        # Export logs
        export_file = os.path.join(self.temp_dir, 'exported_logs.txt')
        result = self.logger.export_logs(export_file, 'all')
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(export_file))


class TestPerformanceMonitor(unittest.TestCase):
    """Test performance monitoring."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = QuizLogger(os.path.join(self.temp_dir, 'logs'))
        self.monitor = PerformanceMonitor(self.logger)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_start_timer(self):
        """Test timer start."""
        self.monitor.start_timer("test_operation")
        
        self.assertIn("test_operation", self.monitor.start_times)
        self.assertIsInstance(self.monitor.start_times["test_operation"], type(self.monitor.start_times["test_operation"]))
    
    def test_end_timer(self):
        """Test timer end."""
        self.monitor.start_timer("test_operation")
        
        # Wait a bit
        import time
        time.sleep(0.01)
        
        duration = self.monitor.end_timer("test_operation", {"test": "data"})
        
        self.assertGreater(duration, 0)
        self.assertNotIn("test_operation", self.monitor.start_times)
    
    def test_measure_operation(self):
        """Test operation measurement."""
        def test_func():
            import time
            time.sleep(0.01)
            return "test_result"
        
        result = self.monitor.measure_operation("test_operation", test_func)
        
        self.assertEqual(result, "test_result")
        self.assertEqual(len(self.logger.performance_data), 1)


class TestAuditTrail(unittest.TestCase):
    """Test audit trail."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = QuizLogger(os.path.join(self.temp_dir, 'logs'))
        self.audit = AuditTrail(self.logger)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_question_creation(self):
        """Test question creation audit."""
        self.audit.log_question_creation("q123", "test_user")
        
        # Check audit log
        self.assertTrue(self.logger.audit_log.exists())
    
    def test_log_question_update(self):
        """Test question update audit."""
        self.audit.log_question_update("q123", "test_user")
        
        # Check audit log
        self.assertTrue(self.logger.audit_log.exists())
    
    def test_log_question_deletion(self):
        """Test question deletion audit."""
        self.audit.log_question_deletion("q123", "test_user")
        
        # Check audit log
        self.assertTrue(self.logger.audit_log.exists())
    
    def test_log_quiz_session(self):
        """Test quiz session audit."""
        self.audit.log_quiz_session("s123", "test_user", 85.5)
        
        # Check audit log
        self.assertTrue(self.logger.audit_log.exists())
    
    def test_log_data_export(self):
        """Test data export audit."""
        self.audit.log_data_export("/path/to/file.json", "json", "test_user")
        
        # Check audit log
        self.assertTrue(self.logger.audit_log.exists())
    
    def test_log_data_import(self):
        """Test data import audit."""
        self.audit.log_data_import("/path/to/file.json", "json", "test_user")
        
        # Check audit log
        self.assertTrue(self.logger.audit_log.exists())


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run tests
    unittest.main(verbosity=2)
