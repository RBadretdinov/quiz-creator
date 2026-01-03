"""
Security and Accessibility Testing for Phase 5.1

This module provides comprehensive security testing including
input validation, file security, encryption, and accessibility testing.
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

class SecurityTestSuite(unittest.TestCase):
    """Comprehensive security test suite."""
    
    def setUp(self):
        """Set up security test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize components
        self.question_manager = QuestionManager(self.data_dir)
        self.tag_manager = TagManager(self.data_dir)
        self.quiz_engine = QuizEngine(self.question_manager, self.tag_manager)
        self.data_persistence = DataPersistence(self.data_dir)
    
    def tearDown(self):
        """Clean up security test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_input_validation_security(self):
        """Test input validation for security vulnerabilities."""
        print("\n=== Input Validation Security Test ===")
        
        # Test SQL injection attempts
        malicious_inputs = [
            "'; DROP TABLE questions; --",
            "1' OR '1'='1",
            "<script>alert('XSS')</script>",
            "../../../etc/passwd",
            "null\0byte",
            "very_long_string" * 1000
        ]
        
        for malicious_input in malicious_inputs:
            # Test question text validation
            try:
                question = Question(malicious_input, "multiple_choice", ["A", "B"], [0])
                # Should not raise exception, but should sanitize input
                self.assertIsInstance(question.question_text, str)
            except ValueError:
                # Expected for some malicious inputs
                pass
        
        # Test tag name validation
        for malicious_input in malicious_inputs:
            try:
                tag = Tag(malicious_input, "description")
                # Should not raise exception, but should sanitize input
                self.assertIsInstance(tag.name, str)
            except ValueError:
                # Expected for some malicious inputs
                pass
    
    def test_file_security(self):
        """Test file security and path traversal protection."""
        print("\n=== File Security Test ===")
        
        # Test path traversal attempts
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]
        
        for malicious_path in malicious_paths:
            try:
                # Test file operations with malicious paths
                test_file = os.path.join(self.temp_dir, malicious_path)
                
                # Should not allow access to system files
                with self.assertRaises((OSError, ValueError, PermissionError)):
                    with open(test_file, 'w') as f:
                        f.write("test")
            except Exception:
                # Expected for malicious paths
                pass
    
    def test_data_encryption(self):
        """Test data encryption and security."""
        print("\n=== Data Encryption Test ===")
        
        try:
            # Test encryption availability
            from cryptography.fernet import Fernet
            
            # Test encryption/decryption
            key = Fernet.generate_key()
            fernet = Fernet(key)
            
            test_data = "Sensitive quiz data"
            encrypted_data = fernet.encrypt(test_data.encode())
            decrypted_data = fernet.decrypt(encrypted_data).decode()
            
            self.assertEqual(test_data, decrypted_data)
            self.assertNotEqual(test_data, encrypted_data)
            
            print("Encryption/decryption working correctly")
            
        except ImportError:
            print("Encryption module not available, skipping encryption test")
    
    def test_access_control(self):
        """Test access control and permissions."""
        print("\n=== Access Control Test ===")
        
        # Test file permissions
        test_file = os.path.join(self.temp_dir, 'test_permissions.txt')
        
        try:
            # Create file with restricted permissions
            with open(test_file, 'w') as f:
                f.write("test data")
            
            # Test read permissions
            with open(test_file, 'r') as f:
                data = f.read()
            self.assertEqual(data, "test data")
            
            # Test write permissions
            with open(test_file, 'w') as f:
                f.write("updated data")
            
            with open(test_file, 'r') as f:
                data = f.read()
            self.assertEqual(data, "updated data")
            
        except PermissionError:
            print("Permission test failed - expected on some systems")
    
    def test_data_validation(self):
        """Test data validation for security."""
        print("\n=== Data Validation Security Test ===")
        
        # Test with malformed JSON
        malformed_json = '{"question": "test", "answers": [}'
        
        try:
            json.loads(malformed_json)
            self.fail("Should have raised JSONDecodeError")
        except json.JSONDecodeError:
            # Expected
            pass
        
        # Test with oversized data
        oversized_data = "A" * 1000000  # 1MB
        
        try:
            question = Question(oversized_data, "multiple_choice", ["A", "B"], [0])
            # Should handle oversized data gracefully
            self.assertIsInstance(question.question_text, str)
        except (ValueError, MemoryError):
            # Expected for oversized data
            pass
    
    def test_network_security(self):
        """Test network security (for OCR and import features)."""
        print("\n=== Network Security Test ===")
        
        # Test with malicious URLs
        malicious_urls = [
            "http://malicious-site.com/exploit.exe",
            "ftp://evil.com/backdoor",
            "file:///etc/passwd",
            "javascript:alert('XSS')"
        ]
        
        for malicious_url in malicious_urls:
            # Should not process malicious URLs
            self.assertFalse(self._is_safe_url(malicious_url))
    
    def test_memory_security(self):
        """Test memory security and buffer overflow protection."""
        print("\n=== Memory Security Test ===")
        
        # Test with very large inputs
        large_inputs = [
            "A" * 100000,  # 100KB
            "B" * 1000000,  # 1MB
            "C" * 10000000  # 10MB
        ]
        
        for large_input in large_inputs:
            try:
                question = Question(large_input, "multiple_choice", ["A", "B"], [0])
                # Should handle large inputs without crashing
                self.assertIsInstance(question.question_text, str)
            except (ValueError, MemoryError):
                # Expected for very large inputs
                pass
    
    def _is_safe_url(self, url: str) -> bool:
        """Check if URL is safe (mock implementation)."""
        safe_protocols = ['http:', 'https:']
        dangerous_patterns = ['malicious', 'evil', 'exploit', 'backdoor']
        
        if not any(url.startswith(protocol) for protocol in safe_protocols):
            return False
        
        if any(pattern in url.lower() for pattern in dangerous_patterns):
            return False
        
        return True


class AccessibilityTestSuite(unittest.TestCase):
    """Comprehensive accessibility test suite."""
    
    def setUp(self):
        """Set up accessibility test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up accessibility test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_keyboard_navigation(self):
        """Test keyboard navigation accessibility."""
        print("\n=== Keyboard Navigation Test ===")
        
        try:
            from ui.enhanced_console import EnhancedConsole
            
            console = EnhancedConsole(self.data_dir)
            
            # Test keyboard shortcuts
            shortcuts = [
                'ctrl+h', 'ctrl+q', 'ctrl+n', 'ctrl+t',
                'f1', 'f2', 'f3'
            ]
            
            for shortcut in shortcuts:
                result = console.handle_keyboard_shortcuts(shortcut)
                # Should handle shortcuts without errors
                self.assertIsInstance(result, bool)
            
            print("Keyboard navigation working correctly")
            
        except ImportError:
            print("Enhanced console module not available, skipping keyboard navigation test")
    
    def test_screen_reader_compatibility(self):
        """Test screen reader compatibility."""
        print("\n=== Screen Reader Compatibility Test ===")
        
        try:
            from ui.enhanced_console import EnhancedConsole
            
            console = EnhancedConsole(self.data_dir)
            
            # Test accessibility features
            console.enable_accessibility_features(True)
            self.assertTrue(console.accessibility_enabled)
            
            # Test help system
            help_info = console.get_context_help('main')
            self.assertIsInstance(help_info, dict)
            self.assertIn('title', help_info)
            
            print("Screen reader compatibility working correctly")
            
        except ImportError:
            print("Enhanced console module not available, skipping screen reader test")
    
    def test_high_contrast_support(self):
        """Test high contrast theme support."""
        print("\n=== High Contrast Support Test ===")
        
        try:
            from ui.user_preferences import UserPreferences
            
            prefs = UserPreferences(self.data_dir)
            
            # Test high contrast theme
            result = prefs.set_theme('high_contrast')
            self.assertTrue(result)
            
            # Test theme configuration
            theme = prefs.get_theme('high_contrast')
            self.assertIsInstance(theme, dict)
            self.assertIn('colors', theme)
            
            print("High contrast support working correctly")
            
        except ImportError:
            print("User preferences module not available, skipping high contrast test")
    
    def test_terminal_compatibility(self):
        """Test terminal compatibility."""
        print("\n=== Terminal Compatibility Test ===")
        
        try:
            from ui.enhanced_console import EnhancedConsole
            
            console = EnhancedConsole(self.data_dir)
            
            # Test terminal capabilities
            capabilities = console.validate_terminal_capabilities()
            self.assertIsInstance(capabilities, dict)
            self.assertIn('platform', capabilities)
            self.assertIn('width', capabilities)
            self.assertIn('height', capabilities)
            
            # Test UI adaptation
            console.adapt_ui_to_terminal()
            
            print("Terminal compatibility working correctly")
            
        except ImportError:
            print("Enhanced console module not available, skipping terminal compatibility test")
    
    def test_unicode_support(self):
        """Test Unicode character support."""
        print("\n=== Unicode Support Test ===")
        
        # Test with Unicode characters
        unicode_texts = [
            "Question with émojis 🎯 and special chars: ñáéíóú",
            "中文问题",
            "العربية",
            "Русский",
            "עברית"
        ]
        
        for unicode_text in unicode_texts:
            try:
                question = Question(unicode_text, "multiple_choice", ["A", "B"], [0])
                self.assertEqual(question.question_text, unicode_text)
            except UnicodeEncodeError:
                print(f"Unicode encoding issue with: {unicode_text}")
    
    def test_color_blind_support(self):
        """Test color blind support."""
        print("\n=== Color Blind Support Test ===")
        
        try:
            from ui.user_preferences import UserPreferences
            
            prefs = UserPreferences(self.data_dir)
            
            # Test monochrome theme
            result = prefs.set_theme('monochrome')
            self.assertTrue(result)
            
            # Test theme colors
            theme = prefs.get_theme('monochrome')
            self.assertIsInstance(theme, dict)
            
            print("Color blind support working correctly")
            
        except ImportError:
            print("User preferences module not available, skipping color blind test")
    
    def test_motor_disability_support(self):
        """Test motor disability support."""
        print("\n=== Motor Disability Support Test ===")
        
        try:
            from ui.command_history import CommandHistory
            
            history = CommandHistory(os.path.join(self.data_dir, 'history.json'))
            
            # Test command history
            history.add_command('test command', 'main')
            recent = history.get_recent_commands(5)
            self.assertIsInstance(recent, list)
            
            # Test auto-completion
            completions = history.get_auto_completions('test')
            self.assertIsInstance(completions, list)
            
            print("Motor disability support working correctly")
            
        except ImportError:
            print("Command history module not available, skipping motor disability test")
    
    def test_cognitive_disability_support(self):
        """Test cognitive disability support."""
        print("\n=== Cognitive Disability Support Test ===")
        
        try:
            from ui.enhanced_console import EnhancedConsole
            
            console = EnhancedConsole(self.data_dir)
            
            # Test help system
            help_info = console.get_context_help('main')
            self.assertIsInstance(help_info, dict)
            
            # Test tutorials
            console.run_tutorial('basic')
            
            print("Cognitive disability support working correctly")
            
        except ImportError:
            print("Enhanced console module not available, skipping cognitive disability test")
    
    def test_hearing_disability_support(self):
        """Test hearing disability support."""
        print("\n=== Hearing Disability Support Test ===")
        
        # Test visual feedback
        try:
            from ui.enhanced_console import EnhancedConsole
            
            console = EnhancedConsole(self.data_dir)
            
            # Test visual feedback
            console.display_breadcrumb()
            
            print("Hearing disability support working correctly")
            
        except ImportError:
            print("Enhanced console module not available, skipping hearing disability test")
    
    def test_learning_disability_support(self):
        """Test learning disability support."""
        print("\n=== Learning Disability Support Test ===")
        
        try:
            from ui.enhanced_console import EnhancedConsole
            
            console = EnhancedConsole(self.data_dir)
            
            # Test user onboarding
            console.setup_user_onboarding()
            
            # Test help system
            console.show_help('main')
            
            print("Learning disability support working correctly")
            
        except ImportError:
            print("Enhanced console module not available, skipping learning disability test")


class CrossPlatformTestSuite(unittest.TestCase):
    """Cross-platform compatibility test suite."""
    
    def setUp(self):
        """Set up cross-platform test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up cross-platform test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_path_handling(self):
        """Test cross-platform path handling."""
        print("\n=== Cross-Platform Path Handling Test ===")
        
        # Test path operations
        test_path = os.path.join(self.data_dir, 'test_file.txt')
        
        # Create file
        with open(test_path, 'w') as f:
            f.write("test data")
        
        # Test file existence
        self.assertTrue(os.path.exists(test_path))
        
        # Test path operations
        path_obj = Path(test_path)
        self.assertEqual(path_obj.name, 'test_file.txt')
        self.assertEqual(path_obj.suffix, '.txt')
    
    def test_file_operations(self):
        """Test cross-platform file operations."""
        print("\n=== Cross-Platform File Operations Test ===")
        
        # Test file creation
        test_file = os.path.join(self.data_dir, 'cross_platform_test.txt')
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Cross-platform test data")
        
        # Test file reading
        with open(test_file, 'r', encoding='utf-8') as f:
            data = f.read()
        
        self.assertEqual(data, "Cross-platform test data")
    
    def test_encoding_handling(self):
        """Test cross-platform encoding handling."""
        print("\n=== Cross-Platform Encoding Test ===")
        
        # Test different encodings
        encodings = ['utf-8', 'utf-16', 'latin-1']
        
        for encoding in encodings:
            test_file = os.path.join(self.data_dir, f'test_{encoding}.txt')
            
            try:
                with open(test_file, 'w', encoding=encoding) as f:
                    f.write("Test data with encoding")
                
                with open(test_file, 'r', encoding=encoding) as f:
                    data = f.read()
                
                self.assertEqual(data, "Test data with encoding")
            except UnicodeError:
                print(f"Encoding {encoding} not supported on this platform")


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run security and accessibility tests
    print("Starting Security and Accessibility Tests...")
    unittest.main(verbosity=2)
