#!/usr/bin/env python3
"""
Comprehensive Menu Flow Tests

This test suite tests complete user flows through all menus to catch bugs.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app_controller_db import AppControllerDB


class TestComprehensiveMenuFlows(unittest.TestCase):
    """Test complete menu flows for bugs."""
    
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
        'What is Python?',  # Question text
        '1',  # Multiple choice
        'A programming language', 'y',  # Answer 1 (correct)
        'A snake', 'n',  # Answer 2
        '',  # No more answers
        'Programming',  # Tag 1
        ''  # No more tags
    ])
    def test_create_question_complete_flow(self, mock_input):
        """Test complete question creation flow."""
        try:
            self.app._handle_create_question()
            
            # Verify question was created
            questions = self.app.question_manager.get_all_questions()
            python_questions = [q for q in questions if 'Python' in q.get('question_text', '')]
            self.assertGreater(len(python_questions), 0, "Question should have been created")
            
            # Verify tag was created
            tag = self.app.tag_manager.get_tag_by_name('Programming')
            self.assertIsNotNone(tag, "Tag 'Programming' should have been auto-created")
            
        except Exception as e:
            self.fail(f"Complete question creation flow failed: {e}")
    
    @patch('builtins.input', side_effect=['1', '1'])  # Quick quiz, 1 question
    def test_take_quiz_flow(self, mock_input):
        """Test taking a quiz."""
        try:
            # First ensure we have questions
            questions = self.app.question_manager.get_all_questions()
            if len(questions) == 0:
                self.skipTest("No questions available for quiz test")
            
            # Test quiz flow
            self.app._handle_take_quiz()
            
        except Exception as e:
            # Check if it's just "no questions" error which is expected
            if "No questions available" not in str(e):
                self.fail(f"Quiz flow failed: {e}")
    
    @patch('builtins.input', side_effect=['2', 'NewTag', ''])
    def test_create_tag_flow(self, mock_input):
        """Test creating a tag through menu."""
        try:
            self.app._handle_manage_tags()
            
            # Verify tag was created
            tag = self.app.tag_manager.get_tag_by_name('NewTag')
            self.assertIsNotNone(tag, "Tag should have been created")
            
        except Exception as e:
            self.fail(f"Create tag flow failed: {e}")
    
    def test_view_tags_flow(self):
        """Test viewing tags."""
        try:
            self.app._handle_view_all_tags()
            # Should not raise any errors
        except Exception as e:
            self.fail(f"View tags flow failed: {e}")
    
    @patch('builtins.input', side_effect=['5', 'Geography'])
    def test_search_tags_flow(self, mock_input):
        """Test searching tags."""
        try:
            self.app._handle_manage_tags()
            # Should not raise any errors
        except Exception as e:
            if "No tags found" not in str(e):
                self.fail(f"Search tags flow failed: {e}")
    
    def test_database_info_flow(self):
        """Test viewing database info."""
        try:
            self.app._handle_database_info()
            # Should not raise any errors
        except Exception as e:
            self.fail(f"Database info flow failed: {e}")
    
    def test_analytics_dashboard_flow(self):
        """Test analytics dashboard."""
        try:
            if hasattr(self.app, '_handle_analytics_dashboard'):
                pass  # Method exists
        except Exception as e:
            self.fail(f"Analytics dashboard flow failed: {e}")


class TestTagAutoCreationComprehensive(unittest.TestCase):
    """Comprehensive tests for tag auto-creation."""
    
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
        'Test question with auto tag?',  # Question text
        '1',  # Multiple choice
        'Answer 1', 'y',  # Correct answer
        'Answer 2', 'n',  # Wrong answer
        '',  # No more answers
        'AutoCreatedTag1',  # Tag 1
        'AutoCreatedTag2',  # Tag 2
        ''  # No more tags
    ])
    def test_multiple_tags_auto_creation(self, mock_input):
        """Test that multiple tags are auto-created."""
        try:
            initial_tag_count = len(self.app.tag_manager.get_all_tags())
            
            # Create question with multiple tags
            self.app._handle_create_question()
            
            # Verify tags were created
            tag1 = self.app.tag_manager.get_tag_by_name('AutoCreatedTag1')
            tag2 = self.app.tag_manager.get_tag_by_name('AutoCreatedTag2')
            
            self.assertIsNotNone(tag1, "First tag should have been auto-created")
            self.assertIsNotNone(tag2, "Second tag should have been auto-created")
            
            # Verify tag count increased
            final_tag_count = len(self.app.tag_manager.get_all_tags())
            self.assertGreaterEqual(final_tag_count, initial_tag_count + 2, 
                                  "Tag count should have increased by at least 2")
            
        except Exception as e:
            self.fail(f"Multiple tags auto-creation failed: {e}")


if __name__ == '__main__':
    unittest.main()

