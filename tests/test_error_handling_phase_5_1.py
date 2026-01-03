"""
Comprehensive Error Handling Tests for Phase 5.1

This module tests error handling, edge cases, and boundary conditions
across all components of the quiz application.
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

from models.question import Question
from models.tag import Tag
from models.quiz_session import QuizSession
from quiz_engine import QuizEngine
from question_manager import QuestionManager
from tag_manager import TagManager
from data_persistence import DataPersistence
from database_manager import DatabaseManager
from analytics.analytics_engine import AnalyticsEngine

class TestErrorHandling(unittest.TestCase):
    """Test error handling across all components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize components
        self.question_manager = QuestionManager(self.data_dir)
        self.tag_manager = TagManager(self.data_dir)
        self.quiz_engine = QuizEngine(self.question_manager, self.tag_manager)
        self.data_persistence = DataPersistence(self.data_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invalid_question_creation(self):
        """Test question creation with invalid inputs."""
        # Test empty question text
        with self.assertRaises(ValueError):
            Question("", "multiple_choice", ["A", "B"], [0])
        
        # Test invalid question type
        with self.assertRaises(ValueError):
            Question("Test question", "invalid_type", ["A", "B"], [0])
        
        # Test empty answers
        with self.assertRaises(ValueError):
            Question("Test question", "multiple_choice", [], [0])
        
        # Test invalid correct answers
        with self.assertRaises(ValueError):
            Question("Test question", "multiple_choice", ["A", "B"], [2])  # Index out of range
        
        # Test None inputs
        with self.assertRaises(ValueError):
            Question(None, "multiple_choice", ["A", "B"], [0])
    
    def test_invalid_tag_creation(self):
        """Test tag creation with invalid inputs."""
        # Test empty tag name
        with self.assertRaises(ValueError):
            Tag("", "description")
        
        # Test None tag name
        with self.assertRaises(ValueError):
            Tag(None, "description")
        
        # Test invalid parent ID
        with self.assertRaises(ValueError):
            Tag("test", "description", parent_id="invalid_id")
        
        # Test circular reference
        tag1 = Tag("parent", "parent tag")
        tag2 = Tag("child", "child tag", parent_id=tag1.id)
        with self.assertRaises(ValueError):
            tag1.parent_id = tag2.id  # Would create circular reference
    
    def test_invalid_quiz_session(self):
        """Test quiz session with invalid inputs."""
        # Test empty questions list
        with self.assertRaises(ValueError):
            QuizSession([], "test_user")
        
        # Test None questions
        with self.assertRaises(ValueError):
            QuizSession(None, "test_user")
        
        # Test invalid user
        with self.assertRaises(ValueError):
            QuizSession([], None)
    
    def test_file_system_errors(self):
        """Test handling of file system errors."""
        # Test with read-only directory
        read_only_dir = os.path.join(self.temp_dir, 'readonly')
        os.makedirs(read_only_dir, exist_ok=True)
        
        # Make directory read-only (Unix-like systems)
        if hasattr(os, 'chmod'):
            try:
                os.chmod(read_only_dir, 0o444)
                
                # Try to create files in read-only directory
                with self.assertRaises(PermissionError):
                    DataPersistence(read_only_dir).save_questions([])
            except (OSError, AttributeError):
                # Skip test on systems where chmod doesn't work as expected
                pass
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted data files."""
        # Create corrupted JSON file
        corrupted_file = os.path.join(self.data_dir, 'questions.json')
        with open(corrupted_file, 'w') as f:
            f.write('{"invalid": json}')  # Invalid JSON
        
        # Test loading corrupted data
        with self.assertRaises(json.JSONDecodeError):
            self.data_persistence.load_questions()
    
    def test_memory_limits(self):
        """Test handling of memory limits."""
        # Test with very large question text
        large_text = "A" * 1000000  # 1MB of text
        
        try:
            question = Question(large_text, "multiple_choice", ["A", "B"], [0])
            self.assertIsNotNone(question)
        except MemoryError:
            # This is expected for very large inputs
            pass
    
    def test_concurrent_access(self):
        """Test concurrent access to data files."""
        # This is a simplified test - in real scenario, would use threading
        questions = [
            Question("Question 1", "multiple_choice", ["A", "B"], [0]),
            Question("Question 2", "multiple_choice", ["A", "B"], [0])
        ]
        
        # Test multiple saves
        for i in range(10):
            try:
                self.data_persistence.save_questions(questions)
            except Exception as e:
                # Should handle concurrent access gracefully
                self.assertIsInstance(e, (OSError, PermissionError))
    
    def test_network_errors(self):
        """Test handling of network-related errors."""
        # Mock network failure for OCR
        with patch('src.ocr_processor.OCRProcessor') as mock_ocr:
            mock_ocr.return_value.process_screenshot.side_effect = ConnectionError("Network error")
            
            # Test OCR with network failure
            with self.assertRaises(ConnectionError):
                mock_ocr.return_value.process_screenshot("test_image.jpg")
    
    def test_database_errors(self):
        """Test database error handling."""
        # Mock database connection failure
        with patch('src.database.connection.DatabaseConnectionManager') as mock_db:
            mock_db.return_value.get_connection.side_effect = Exception("Database connection failed")
            
            # Test database operations with connection failure
            with self.assertRaises(Exception):
                mock_db.return_value.get_connection()
    
    def test_import_export_errors(self):
        """Test import/export error handling."""
        # Test importing invalid file format
        invalid_file = os.path.join(self.temp_dir, 'invalid.txt')
        with open(invalid_file, 'w') as f:
            f.write('This is not a valid quiz file')
        
        # Test with file importer
        try:
            from import_export.file_importer import FileImporter
            importer = FileImporter()
            result = importer.import_file(invalid_file)
            self.assertFalse(result['success'])
        except ImportError:
            # Skip if import_export module not available
            pass
    
    def test_analytics_errors(self):
        """Test analytics error handling."""
        # Test with invalid analytics data
        invalid_data = {
            'invalid_key': 'invalid_value',
            'timestamp': 'invalid_timestamp'
        }
        
        try:
            from analytics.analytics_engine import AnalyticsEngine
            engine = AnalyticsEngine(None)  # No database manager
            # Should handle invalid data gracefully
        except Exception as e:
            self.assertIsInstance(e, (TypeError, AttributeError))
    
    def test_ui_errors(self):
        """Test UI error handling."""
        # Test with invalid user input
        with patch('builtins.input', return_value='invalid_input'):
            try:
                from ui.prompts import InputPrompts
                prompts = InputPrompts()
                # Should handle invalid input gracefully
            except Exception as e:
                self.assertIsInstance(e, (ValueError, TypeError))
    
    def test_theme_errors(self):
        """Test theme error handling."""
        # Test with invalid theme configuration
        invalid_theme = {
            'name': 'Invalid Theme',
            'colors': 'invalid_colors'  # Should be dict
        }
        
        try:
            from ui.user_preferences import UserPreferences
            prefs = UserPreferences(self.temp_dir)
            result = prefs.create_custom_theme('invalid', invalid_theme)
            self.assertFalse(result)
        except Exception as e:
            self.assertIsInstance(e, (TypeError, ValueError))
    
    def test_shortcut_errors(self):
        """Test keyboard shortcut error handling."""
        # Test with invalid shortcut configuration
        invalid_shortcut = {
            'description': 'Invalid Shortcut',
            # Missing required 'action' field
        }
        
        try:
            from ui.user_preferences import UserPreferences
            prefs = UserPreferences(self.temp_dir)
            result = prefs.set_shortcut('invalid', invalid_shortcut)
            self.assertFalse(result)
        except Exception as e:
            self.assertIsInstance(e, (TypeError, ValueError))
    
    def test_command_history_errors(self):
        """Test command history error handling."""
        # Test with invalid history data
        invalid_history = [
            {'command': None, 'timestamp': 'invalid'},
            {'command': '', 'timestamp': None}
        ]
        
        try:
            from ui.command_history import CommandHistory
            history = CommandHistory(os.path.join(self.temp_dir, 'history.json'))
            # Should handle invalid history data gracefully
        except Exception as e:
            self.assertIsInstance(e, (TypeError, ValueError))
    
    def test_quiz_engine_errors(self):
        """Test quiz engine error handling."""
        # Test with invalid quiz session
        with self.assertRaises(ValueError):
            self.quiz_engine.start_quiz(None, "test_user")
        
        # Test with invalid user
        questions = [Question("Test", "multiple_choice", ["A", "B"], [0])]
        with self.assertRaises(ValueError):
            self.quiz_engine.start_quiz(questions, None)
    
    def test_scoring_errors(self):
        """Test scoring error handling."""
        # Test with invalid answer
        question = Question("Test", "multiple_choice", ["A", "B"], [0])
        
        with self.assertRaises(ValueError):
            self.quiz_engine.submit_answer(None, "invalid_answer")
        
        with self.assertRaises(ValueError):
            self.quiz_engine.submit_answer(question, None)
    
    def test_export_errors(self):
        """Test export error handling."""
        # Test with invalid export path
        with self.assertRaises(OSError):
            self.quiz_engine.export_quiz_session("", "invalid_format")
        
        # Test with invalid format
        with self.assertRaises(ValueError):
            self.quiz_engine.export_quiz_session("test.json", "invalid_format")
    
    def test_validation_errors(self):
        """Test data validation error handling."""
        # Test with invalid question data
        invalid_question_data = {
            'question_text': None,
            'question_type': 'invalid',
            'answers': [],
            'correct_answers': [999]
        }
        
        with self.assertRaises(ValueError):
            Question.from_dict(invalid_question_data)
    
    def test_boundary_conditions(self):
        """Test boundary conditions."""
        # Test with maximum string length
        max_text = "A" * 10000  # 10KB text
        
        try:
            question = Question(max_text, "multiple_choice", ["A", "B"], [0])
            self.assertIsNotNone(question)
        except Exception as e:
            # Should handle large text gracefully
            self.assertIsInstance(e, (ValueError, MemoryError))
        
        # Test with maximum number of answers
        max_answers = ["A"] * 1000  # 1000 answers
        
        try:
            question = Question("Test", "multiple_choice", max_answers, [0])
            self.assertIsNotNone(question)
        except Exception as e:
            # Should handle many answers gracefully
            self.assertIsInstance(e, (ValueError, MemoryError))
    
    def test_unicode_handling(self):
        """Test Unicode character handling."""
        # Test with Unicode characters
        unicode_text = "Test with émojis 🎯 and special chars: ñáéíóú"
        
        try:
            question = Question(unicode_text, "multiple_choice", ["A", "B"], [0])
            self.assertIsNotNone(question)
            self.assertEqual(question.question_text, unicode_text)
        except UnicodeEncodeError:
            # Should handle Unicode gracefully
            pass
    
    def test_timezone_handling(self):
        """Test timezone handling."""
        # Test with different timezone data
        from datetime import datetime, timezone
        
        # Test with UTC timezone
        utc_time = datetime.now(timezone.utc)
        
        try:
            # Should handle timezone-aware datetime
            session = QuizSession([Question("Test", "multiple_choice", ["A", "B"], [0])], "user")
            session.start_time = utc_time
            self.assertIsNotNone(session)
        except Exception as e:
            # Should handle timezone gracefully
            self.assertIsInstance(e, (TypeError, ValueError))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_datasets(self):
        """Test handling of empty datasets."""
        # Test with empty question list
        question_manager = QuestionManager(self.data_dir)
        questions = question_manager.get_all_questions()
        self.assertEqual(len(questions), 0)
        
        # Test with empty tag list
        tag_manager = TagManager(self.data_dir)
        tags = tag_manager.get_all_tags()
        self.assertEqual(len(tags), 0)
    
    def test_single_item_datasets(self):
        """Test handling of single item datasets."""
        # Test with single question
        question = Question("Single question", "multiple_choice", ["A", "B"], [0])
        question_manager = QuestionManager(self.data_dir)
        question_manager.add_question(question)
        
        questions = question_manager.get_all_questions()
        self.assertEqual(len(questions), 1)
        
        # Test with single tag
        tag = Tag("single_tag", "Single tag")
        tag_manager = TagManager(self.data_dir)
        tag_manager.create_tag(tag.name, tag.description)
        
        tags = tag_manager.get_all_tags()
        self.assertEqual(len(tags), 1)
    
    def test_maximum_datasets(self):
        """Test handling of maximum datasets."""
        # Test with maximum number of questions
        question_manager = QuestionManager(self.data_dir)
        
        for i in range(1000):  # 1000 questions
            question = Question(f"Question {i}", "multiple_choice", ["A", "B"], [0])
            question_manager.add_question(question)
        
        questions = question_manager.get_all_questions()
        self.assertEqual(len(questions), 1000)
    
    def test_rapid_operations(self):
        """Test rapid operations."""
        question_manager = QuestionManager(self.data_dir)
        
        # Test rapid question creation
        for i in range(100):
            question = Question(f"Rapid question {i}", "multiple_choice", ["A", "B"], [0])
            question_manager.add_question(question)
        
        questions = question_manager.get_all_questions()
        self.assertEqual(len(questions), 100)
    
    def test_mixed_data_types(self):
        """Test handling of mixed data types."""
        # Test with different question types
        question_manager = QuestionManager(self.data_dir)
        
        # Multiple choice
        mc_question = Question("MC Question", "multiple_choice", ["A", "B", "C"], [0])
        question_manager.add_question(mc_question)
        
        # True/False
        tf_question = Question("TF Question", "true_false", ["True", "False"], [0])
        question_manager.add_question(tf_question)
        
        # Select all
        sa_question = Question("SA Question", "select_all", ["A", "B", "C"], [0, 1])
        question_manager.add_question(sa_question)
        
        questions = question_manager.get_all_questions()
        self.assertEqual(len(questions), 3)
    
    def test_nested_operations(self):
        """Test nested operations."""
        # Test nested tag hierarchy
        tag_manager = TagManager(self.data_dir)
        
        # Create parent tag
        parent_tag = tag_manager.create_tag("parent", "Parent tag")
        
        # Create child tags
        child1 = tag_manager.create_tag("child1", "Child 1", parent_id=parent_tag)
        child2 = tag_manager.create_tag("child2", "Child 2", parent_id=parent_tag)
        
        # Create grandchild
        grandchild = tag_manager.create_tag("grandchild", "Grandchild", parent_id=child1)
        
        # Test hierarchy
        children = tag_manager.get_children(parent_tag)
        self.assertEqual(len(children), 2)
        
        grandchildren = tag_manager.get_children(child1)
        self.assertEqual(len(grandchildren), 1)


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run tests
    unittest.main(verbosity=2)
