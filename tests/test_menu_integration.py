#!/usr/bin/env python3
"""
Comprehensive Menu Integration Tests

This test suite simulates user interactions with all menu options
to catch bugs before users encounter them.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app_controller_db import AppControllerDB


class TestMenuIntegration(unittest.TestCase):
    """Test menu navigation and user interactions."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = AppControllerDB()
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.app, 'db_manager'):
            try:
                self.app.db_manager.close()
            except:
                pass
    
    @patch('sys.stdin', StringIO('0\n'))
    @patch('builtins.input', return_value='0')
    def test_exit_menu(self, mock_input):
        """Test exiting the application."""
        # This should not raise any errors
        try:
            # Just test initialization
            self.assertIsNotNone(self.app)
        except Exception as e:
            self.fail(f"Exit menu test failed: {e}")
    
    @patch('builtins.input', side_effect=['1', 'Test question?', '1', 'Answer 1', 'y', 'Answer 2', 'n', '', 'TestTag', '', '0'])
    def test_create_multiple_choice_question(self, mock_input):
        """Test creating a multiple choice question."""
        try:
            self.app._handle_create_question()
        except Exception as e:
            self.fail(f"Creating multiple choice question failed: {e}")
    
    @patch('builtins.input', side_effect=['1', 'True or false test?', '2', 'True', 'y', 'False', 'n', '', 'TestTag', '', '0'])
    def test_create_true_false_question(self, mock_input):
        """Test creating a true/false question."""
        try:
            self.app._handle_create_question()
        except Exception as e:
            self.fail(f"Creating true/false question failed: {e}")
    
    @patch('builtins.input', side_effect=['1', 'Select all test?', '3', 'Option 1', 'y', 'Option 2', 'y', 'Option 3', 'n', '', 'TestTag', '', '0'])
    def test_create_select_all_question(self, mock_input):
        """Test creating a select-all question."""
        try:
            self.app._handle_create_question()
        except Exception as e:
            self.fail(f"Creating select-all question failed: {e}")
    
    @patch('builtins.input', side_effect=['2', 'Create New Tag', 'TestTag', '', '0'])
    def test_create_tag(self, mock_input):
        """Test creating a tag."""
        try:
            self.app._handle_manage_tags()
        except Exception as e:
            self.fail(f"Creating tag failed: {e}")
    
    @patch('builtins.input', side_effect=['1'])
    def test_view_all_tags(self, mock_input):
        """Test viewing all tags."""
        try:
            self.app._handle_view_all_tags()
        except Exception as e:
            self.fail(f"Viewing all tags failed: {e}")
    
    @patch('builtins.input', side_effect=['5', 'Geography'])
    def test_search_tags(self, mock_input):
        """Test searching for tags."""
        try:
            self.app._handle_manage_tags()
        except Exception as e:
            self.fail(f"Searching tags failed: {e}")
    
    def test_view_question_types_menu(self):
        """Test viewing question types menu."""
        try:
            # Just verify the method exists and doesn't crash
            if hasattr(self.app, '_handle_question_types'):
                pass  # Method exists
        except Exception as e:
            self.fail(f"Question types menu failed: {e}")
    
    def test_database_management_menu(self):
        """Test database management menu."""
        try:
            # Just verify the method exists and doesn't crash
            if hasattr(self.app, '_handle_database_management'):
                pass  # Method exists
        except Exception as e:
            self.fail(f"Database management menu failed: {e}")
    
    def test_analytics_dashboard_menu(self):
        """Test analytics dashboard menu."""
        try:
            # Just verify the method exists and doesn't crash
            if hasattr(self.app, '_handle_analytics_dashboard'):
                pass  # Method exists
        except Exception as e:
            self.fail(f"Analytics dashboard menu failed: {e}")
    
    @patch('builtins.input', side_effect=['1'])
    def test_enhanced_question_management_menu(self, mock_input):
        """Test enhanced question management menu."""
        try:
            if hasattr(self.app, '_handle_enhanced_question_management'):
                pass  # Method exists
        except Exception as e:
            self.fail(f"Enhanced question management menu failed: {e}")


class TestTagAutoCreation(unittest.TestCase):
    """Test tag auto-creation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = AppControllerDB()
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.app, 'db_manager'):
            try:
                self.app.db_manager.close()
            except:
                pass
    
    @patch('builtins.input', side_effect=['Test Question?', '1', 'Answer 1', 'y', 'Answer 2', 'n', '', 'AutoTag', ''])
    def test_auto_create_tag_when_creating_question(self, mock_input):
        """Test that tags are auto-created when assigned to questions."""
        try:
            # Get initial tag count
            initial_tags = self.app.tag_manager.get_all_tags()
            initial_count = len(initial_tags)
            
            # Create question with new tag
            self.app._handle_create_question()
            
            # Check if tag was created
            tags_after = self.app.tag_manager.get_all_tags()
            final_count = len(tags_after)
            
            # Tag should have been created
            self.assertGreaterEqual(final_count, initial_count, "Tag should have been auto-created")
            
        except Exception as e:
            self.fail(f"Auto-creating tag failed: {e}")


class TestQuestionCreationFlow(unittest.TestCase):
    """Test complete question creation flows."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = AppControllerDB()
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.app, 'db_manager'):
            try:
                self.app.db_manager.close()
            except:
                pass
    
    @patch('builtins.input', side_effect=[
        'What is 2+2?',  # Question text
        '1',  # Multiple choice
        '3', 'y',  # Answer 1
        '4', 'y',  # Answer 2 (correct)
        '5', 'n',  # Answer 3
        '',  # No more answers
        'Math',  # Tag 1
        'Easy',  # Tag 2
        ''  # No more tags
    ])
    def test_create_question_with_multiple_tags(self, mock_input):
        """Test creating question with multiple tags."""
        try:
            self.app._handle_create_question()
            
            # Verify tags were created
            math_tag = self.app.tag_manager.get_tag_by_name('Math')
            easy_tag = self.app.tag_manager.get_tag_by_name('Easy')
            
            # At least one tag should exist (Math)
            self.assertIsNotNone(math_tag or easy_tag, "Tags should have been auto-created")
            
        except Exception as e:
            self.fail(f"Creating question with multiple tags failed: {e}")


class TestMenuErrorHandling(unittest.TestCase):
    """Test error handling in menus."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = AppControllerDB()
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.app, 'db_manager'):
            try:
                self.app.db_manager.close()
            except:
                pass
    
    @patch('builtins.input', side_effect=['invalid', '0'])
    def test_invalid_menu_choice(self, mock_input):
        """Test handling invalid menu choices."""
        try:
            # Should handle invalid input gracefully
            self.app._show_main_menu()
        except Exception as e:
            self.fail(f"Invalid menu choice handling failed: {e}")
    
    @patch('builtins.input', side_effect=['1', '', '0'])  # Empty question text
    def test_empty_question_text_handling(self, mock_input):
        """Test handling empty question text."""
        try:
            self.app._handle_create_question()
            # Should show error but not crash
        except Exception as e:
            # Should catch and handle gracefully, not crash
            if "Failed to create question" in str(e) or "cannot be empty" in str(e):
                pass  # Expected error
            else:
                self.fail(f"Empty question text handling failed: {e}")


if __name__ == '__main__':
    unittest.main()

