"""
Test Suite for Phase 4.3: Enhanced Console UI

This module contains comprehensive unit tests for the enhanced console UI
functionality implemented in Phase 4.3.
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ui.enhanced_console import EnhancedConsole
from ui.command_history import CommandHistory
from ui.user_preferences import UserPreferences

class TestEnhancedConsole(unittest.TestCase):
    """Test cases for EnhancedConsole."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        
        # Mock colorama
        with patch.dict('sys.modules', {'colorama': Mock()}):
            self.console = EnhancedConsole(self.config_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_console_initialization(self):
        """Test enhanced console initialization."""
        self.assertIsNotNone(self.console)
        self.assertEqual(self.console.config_dir, Path(self.config_dir))
        self.assertIsInstance(self.console.breadcrumbs, list)
        self.assertIsInstance(self.console.navigation_history, list)
        self.assertIsInstance(self.console.preferences, dict)
    
    def test_display_breadcrumb(self):
        """Test breadcrumb display."""
        # Add some breadcrumbs
        self.console.breadcrumbs = ['Main', 'Questions', 'Create']
        
        # Mock print function
        with patch('builtins.print') as mock_print:
            self.console.display_breadcrumb()
            mock_print.assert_called_once()
    
    def test_navigate_to(self):
        """Test navigation to location."""
        self.console.navigate_to('Questions', 'question_creation')
        
        self.assertIn('Questions', self.console.breadcrumbs)
        self.assertEqual(self.console.current_context, 'question_creation')
        self.assertEqual(len(self.console.navigation_history), 1)
    
    def test_navigate_back(self):
        """Test navigation back."""
        # Set up navigation history
        self.console.breadcrumbs = ['Main', 'Questions', 'Create']
        self.console.navigation_history = [
            {'location': 'Main', 'context': 'main'},
            {'location': 'Questions', 'context': 'questions'},
            {'location': 'Create', 'context': 'question_creation'}
        ]
        
        # Navigate back
        previous = self.console.navigate_back()
        
        self.assertEqual(previous, 'Questions')
        self.assertEqual(len(self.console.breadcrumbs), 2)
        self.assertEqual(len(self.console.navigation_history), 2)
    
    def test_handle_keyboard_shortcuts(self):
        """Test keyboard shortcut handling."""
        # Test valid shortcut
        result = self.console.handle_keyboard_shortcuts('ctrl+h')
        self.assertTrue(result)
        
        # Test invalid shortcut
        result = self.console.handle_keyboard_shortcuts('invalid')
        self.assertFalse(result)
    
    def test_get_context_help(self):
        """Test context-sensitive help."""
        help_info = self.console.get_context_help('main')
        
        self.assertIsInstance(help_info, dict)
        self.assertIn('title', help_info)
    
    def test_show_help(self):
        """Test help display."""
        with patch('builtins.print') as mock_print:
            self.console.show_help('main')
            self.assertTrue(mock_print.called)
    
    def test_save_user_preferences(self):
        """Test saving user preferences."""
        preferences = {'theme': 'dark', 'accessibility': True}
        result = self.console.save_user_preferences(preferences)
        
        self.assertTrue(result)
        self.assertEqual(self.console.preferences['theme'], 'dark')
        self.assertEqual(self.console.preferences['accessibility'], True)
    
    def test_load_user_preferences(self):
        """Test loading user preferences."""
        preferences = self.console.load_user_preferences()
        
        self.assertIsInstance(preferences, dict)
        self.assertIn('theme', preferences)
    
    def test_reset_preferences(self):
        """Test resetting preferences."""
        result = self.console.reset_preferences()
        
        self.assertTrue(result)
        self.assertIn('theme', self.console.preferences)
    
    def test_setup_user_onboarding(self):
        """Test user onboarding setup."""
        with patch('builtins.print') as mock_print:
            self.console.setup_user_onboarding()
            self.assertTrue(mock_print.called)
    
    def test_run_tutorial(self):
        """Test running tutorials."""
        with patch('builtins.print') as mock_print:
            self.console.run_tutorial('basic')
            self.assertTrue(mock_print.called)
    
    def test_customize_theme(self):
        """Test theme customization."""
        result = self.console.customize_theme('dark')
        
        self.assertTrue(result)
        self.assertEqual(self.console.current_theme, 'dark')
    
    def test_validate_terminal_capabilities(self):
        """Test terminal capabilities validation."""
        capabilities = self.console.validate_terminal_capabilities()
        
        self.assertIsInstance(capabilities, dict)
        self.assertIn('platform', capabilities)
        self.assertIn('width', capabilities)
        self.assertIn('height', capabilities)
    
    def test_adapt_ui_to_terminal(self):
        """Test UI adaptation to terminal."""
        with patch('builtins.print') as mock_print:
            self.console.adapt_ui_to_terminal()
            # Should not raise any exceptions
    
    def test_enable_accessibility_features(self):
        """Test enabling accessibility features."""
        self.console.enable_accessibility_features(True)
        
        self.assertTrue(self.console.accessibility_enabled)
        self.assertTrue(self.console.preferences['accessibility'])


class TestCommandHistory(unittest.TestCase):
    """Test cases for CommandHistory."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.history_file = os.path.join(self.temp_dir, 'command_history.json')
        
        self.history = CommandHistory(self.history_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_history_initialization(self):
        """Test command history initialization."""
        self.assertIsNotNone(self.history)
        self.assertEqual(self.history.history_file, Path(self.history_file))
        self.assertIsInstance(self.history.history, list)
        self.assertEqual(self.history.current_index, -1)
    
    def test_add_command(self):
        """Test adding command to history."""
        self.history.add_command('help', 'main')
        
        self.assertEqual(len(self.history.history), 1)
        self.assertEqual(self.history.history[0]['command'], 'help')
        self.assertEqual(self.history.history[0]['context'], 'main')
    
    def test_get_previous_command(self):
        """Test getting previous command."""
        # Add some commands
        self.history.add_command('help')
        self.history.add_command('quit')
        
        # Get previous commands
        prev1 = self.history.get_previous_command()
        prev2 = self.history.get_previous_command()
        
        self.assertEqual(prev1, 'quit')
        self.assertEqual(prev2, 'help')
    
    def test_get_next_command(self):
        """Test getting next command."""
        # Add some commands
        self.history.add_command('help')
        self.history.add_command('quit')
        
        # Navigate to previous
        self.history.get_previous_command()
        self.history.get_previous_command()
        
        # Get next commands
        next1 = self.history.get_next_command()
        next2 = self.history.get_next_command()
        
        self.assertEqual(next1, 'quit')
        self.assertEqual(next2, None)
    
    def test_search_history(self):
        """Test searching command history."""
        # Add some commands
        self.history.add_command('help')
        self.history.add_command('help navigation')
        self.history.add_command('quit')
        
        # Search for help commands
        results = self.history.search_history('help')
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['command'], 'help navigation')
        self.assertEqual(results[1]['command'], 'help')
    
    def test_get_auto_completions(self):
        """Test getting auto-completions."""
        completions = self.history.get_auto_completions('hel')
        
        self.assertIsInstance(completions, list)
        self.assertIn('help', completions)
    
    def test_get_command_suggestions(self):
        """Test getting command suggestions."""
        suggestions = self.history.get_command_suggestions('hel')
        
        self.assertIsInstance(suggestions, list)
        if suggestions:
            self.assertIn('command', suggestions[0])
            self.assertIn('description', suggestions[0])
    
    def test_get_command_help(self):
        """Test getting command help."""
        help_info = self.history.get_command_help('help')
        
        self.assertIsNotNone(help_info)
        self.assertIn('command', help_info)
        self.assertIn('description', help_info)
    
    def test_get_recent_commands(self):
        """Test getting recent commands."""
        # Add some commands
        self.history.add_command('help')
        self.history.add_command('quit')
        
        recent = self.history.get_recent_commands(5)
        
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]['command'], 'help')
        self.assertEqual(recent[1]['command'], 'quit')
    
    def test_clear_history(self):
        """Test clearing command history."""
        # Add some commands
        self.history.add_command('help')
        self.history.add_command('quit')
        
        # Clear history
        self.history.clear_history()
        
        self.assertEqual(len(self.history.history), 0)
        self.assertEqual(self.history.current_index, -1)
    
    def test_export_history(self):
        """Test exporting command history."""
        # Add some commands
        self.history.add_command('help')
        self.history.add_command('quit')
        
        # Export history
        output_file = self.history.export_history()
        
        self.assertIsInstance(output_file, str)
        self.assertTrue(os.path.exists(output_file))
    
    def test_import_history(self):
        """Test importing command history."""
        # Create test history file
        test_data = {
            'history': [
                {'command': 'help', 'context': 'main', 'timestamp': '2023-01-01T00:00:00'},
                {'command': 'quit', 'context': 'main', 'timestamp': '2023-01-01T00:01:00'}
            ]
        }
        
        test_file = os.path.join(self.temp_dir, 'test_history.json')
        with open(test_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(test_data, f)
        
        # Import history
        result = self.history.import_history(test_file)
        
        self.assertTrue(result)
        self.assertEqual(len(self.history.history), 2)
    
    def test_get_statistics(self):
        """Test getting command history statistics."""
        # Add some commands
        self.history.add_command('help')
        self.history.add_command('help')
        self.history.add_command('quit')
        
        stats = self.history.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_commands'], 3)
        self.assertEqual(stats['unique_commands'], 2)
        self.assertEqual(stats['most_used_command'], 'help')


class TestUserPreferences(unittest.TestCase):
    """Test cases for UserPreferences."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        
        self.preferences = UserPreferences(self.config_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_preferences_initialization(self):
        """Test user preferences initialization."""
        self.assertIsNotNone(self.preferences)
        self.assertEqual(self.preferences.config_dir, Path(self.config_dir))
        self.assertIsInstance(self.preferences.preferences, dict)
        self.assertIsInstance(self.preferences.themes, dict)
        self.assertIsInstance(self.preferences.shortcuts, dict)
        self.assertIsInstance(self.preferences.settings, dict)
    
    def test_get_preference(self):
        """Test getting preference value."""
        value = self.preferences.get_preference('theme', 'default')
        
        self.assertEqual(value, 'default')
    
    def test_set_preference(self):
        """Test setting preference value."""
        result = self.preferences.set_preference('theme', 'dark')
        
        self.assertTrue(result)
        self.assertEqual(self.preferences.preferences['theme'], 'dark')
    
    def test_get_all_preferences(self):
        """Test getting all preferences."""
        all_prefs = self.preferences.get_all_preferences()
        
        self.assertIsInstance(all_prefs, dict)
        self.assertIn('theme', all_prefs)
    
    def test_reset_preferences(self):
        """Test resetting preferences."""
        result = self.preferences.reset_preferences()
        
        self.assertTrue(result)
        self.assertIn('theme', self.preferences.preferences)
    
    def test_export_preferences(self):
        """Test exporting preferences."""
        output_file = self.preferences.export_preferences()
        
        self.assertIsInstance(output_file, str)
        self.assertTrue(os.path.exists(output_file))
    
    def test_import_preferences(self):
        """Test importing preferences."""
        # Create test preferences file
        test_data = {
            'preferences': {'theme': 'dark', 'accessibility': True},
            'themes': {'custom': {'name': 'Custom Theme'}},
            'shortcuts': {'ctrl+x': {'description': 'Custom shortcut'}},
            'settings': {'debug_mode': True}
        }
        
        test_file = os.path.join(self.temp_dir, 'test_preferences.json')
        with open(test_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(test_data, f)
        
        # Import preferences
        result = self.preferences.import_preferences(test_file)
        
        self.assertTrue(result)
        self.assertEqual(self.preferences.preferences['theme'], 'dark')
    
    def test_get_theme(self):
        """Test getting theme configuration."""
        theme = self.preferences.get_theme('default')
        
        self.assertIsInstance(theme, dict)
        self.assertIn('name', theme)
        self.assertIn('colors', theme)
    
    def test_set_theme(self):
        """Test setting theme."""
        result = self.preferences.set_theme('dark')
        
        self.assertTrue(result)
        self.assertEqual(self.preferences.preferences['theme'], 'dark')
    
    def test_create_custom_theme(self):
        """Test creating custom theme."""
        theme_config = {
            'name': 'Custom Theme',
            'description': 'A custom theme',
            'colors': {
                'primary': '#FF0000',
                'secondary': '#00FF00'
            }
        }
        
        result = self.preferences.create_custom_theme('custom', theme_config)
        
        self.assertTrue(result)
        self.assertIn('custom', self.preferences.themes)
    
    def test_get_shortcut(self):
        """Test getting shortcut configuration."""
        shortcut = self.preferences.get_shortcut('ctrl+h')
        
        self.assertIsNotNone(shortcut)
        self.assertIn('description', shortcut)
        self.assertIn('action', shortcut)
    
    def test_set_shortcut(self):
        """Test setting shortcut configuration."""
        shortcut_config = {
            'description': 'Custom shortcut',
            'action': 'custom_action',
            'enabled': True
        }
        
        result = self.preferences.set_shortcut('ctrl+x', shortcut_config)
        
        self.assertTrue(result)
        self.assertIn('ctrl+x', self.preferences.shortcuts)
    
    def test_get_setting(self):
        """Test getting application setting."""
        setting = self.preferences.get_setting('debug_mode', False)
        
        self.assertIsInstance(setting, bool)
    
    def test_set_setting(self):
        """Test setting application setting."""
        result = self.preferences.set_setting('debug_mode', True)
        
        self.assertTrue(result)
        self.assertEqual(self.preferences.settings['debug_mode'], True)
    
    def test_validate_all_preferences(self):
        """Test validating all preferences."""
        errors = self.preferences.validate_all_preferences()
        
        self.assertIsInstance(errors, dict)
        # Should have no errors for default preferences
        self.assertEqual(len(errors), 0)


class TestEnhancedConsoleIntegration(unittest.TestCase):
    """Integration tests for enhanced console functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock colorama
        with patch.dict('sys.modules', {'colorama': Mock()}):
            self.console = EnhancedConsole(os.path.join(self.temp_dir, 'config'))
            self.history = CommandHistory(os.path.join(self.temp_dir, 'history.json'))
            self.preferences = UserPreferences(os.path.join(self.temp_dir, 'prefs'))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_console_with_history(self):
        """Test console integration with command history."""
        # Add command to history
        self.history.add_command('help', 'main')
        
        # Get auto-completions
        completions = self.history.get_auto_completions('hel')
        
        self.assertIsInstance(completions, list)
        self.assertIn('help', completions)
    
    def test_console_with_preferences(self):
        """Test console integration with user preferences."""
        # Set preferences
        self.preferences.set_preference('theme', 'dark')
        self.preferences.set_preference('accessibility', True)
        
        # Get preferences
        theme = self.preferences.get_preference('theme')
        accessibility = self.preferences.get_preference('accessibility')
        
        self.assertEqual(theme, 'dark')
        self.assertTrue(accessibility)
    
    def test_complete_workflow(self):
        """Test complete enhanced console workflow."""
        # Setup user onboarding
        with patch('builtins.print'):
            self.console.setup_user_onboarding()
        
        # Navigate to different locations
        self.console.navigate_to('Questions', 'question_creation')
        self.console.navigate_to('Create', 'question_form')
        
        # Add commands to history
        self.history.add_command('create question', 'question_creation')
        self.history.add_command('save question', 'question_form')
        
        # Set preferences
        self.preferences.set_preference('theme', 'dark')
        self.preferences.set_preference('accessibility', True)
        
        # Verify state
        self.assertEqual(len(self.console.breadcrumbs), 2)
        self.assertEqual(self.console.current_context, 'question_form')
        self.assertEqual(len(self.history.history), 2)
        self.assertEqual(self.preferences.get_preference('theme'), 'dark')
    
    def test_error_handling(self):
        """Test error handling in enhanced console."""
        # Test invalid preference (should pass validation for unknown keys)
        result = self.preferences.set_preference('invalid_key', 'invalid_value')
        self.assertTrue(result)  # Unknown keys are allowed
        
        # Test invalid theme
        result = self.preferences.set_theme('nonexistent_theme')
        self.assertFalse(result)
        
        # Test invalid shortcut (should fail validation for missing required fields)
        result = self.preferences.set_shortcut('invalid', {'invalid': 'config'})
        self.assertFalse(result)  # Missing required fields should fail


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run tests
    unittest.main(verbosity=2)
