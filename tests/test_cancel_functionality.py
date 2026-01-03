#!/usr/bin/env python3
"""
Test Cancel Functionality in Question Creation

Tests that users can cancel question creation at any step.
"""

import sys
import os
import unittest
from unittest.mock import patch

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app_controller_db import AppControllerDB
from ui.prompts import InputPrompts


class TestCancelFunctionality(unittest.TestCase):
    """Test cancel functionality in question creation."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = AppControllerDB()
        self.prompts = InputPrompts()
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self.app, 'db_manager'):
            try:
                self.app.db_manager.close()
            except:
                pass
    
    def test_cancel_at_question_text(self):
        """Test cancelling at question text prompt."""
        with patch('builtins.input', return_value='cancel'):
            result = self.prompts.prompt_question_text()
            self.assertIsNone(result, "Should return None when cancelled")
    
    def test_cancel_at_question_type(self):
        """Test cancelling at question type prompt."""
        with patch('builtins.input', return_value='cancel'):
            result = self.prompts.prompt_question_type()
            self.assertIsNone(result, "Should return None when cancelled")
    
    def test_cancel_at_answer_entry(self):
        """Test cancelling during answer entry."""
        with patch('builtins.input', side_effect=['Answer 1', 'cancel']):
            result = self.prompts.get_answers_for_type('multiple_choice')
            self.assertIsNone(result, "Should return None when cancelled")
    
    def test_cancel_at_tag_selection(self):
        """Test cancelling during tag selection."""
        with patch('builtins.input', return_value='cancel'):
            result = self.prompts.get_tag_selection()
            self.assertIsNone(result, "Should return None when cancelled")
    
    def test_multiple_cancel_commands(self):
        """Test that various cancel commands work."""
        cancel_commands = ['cancel', 'c', 'q', 'quit', 'exit', 'back']
        
        for cmd in cancel_commands:
            with patch('builtins.input', return_value=cmd):
                result = self.prompts.prompt_question_text()
                self.assertIsNone(result, f"'{cmd}' should cancel")


if __name__ == '__main__':
    unittest.main()

