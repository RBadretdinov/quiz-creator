"""
Test suite for Phase 1.5 Data Persistence module.

Tests atomic writes, validation, encryption, backup/restore, and data integrity.
"""

import unittest
import json
import os
import tempfile
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_persistence import DataPersistence


class TestDataPersistence(unittest.TestCase):
    """Test Phase 1.5 Data Persistence functionality."""
    
    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.persistence = DataPersistence(data_dir=self.temp_dir)
        
        # Sample test data
        self.sample_questions = [
            {
                'id': 'q1',
                'question_text': 'What is 2+2?',
                'question_type': 'multiple_choice',
                'answers': [
                    {'id': 'a1', 'text': '3', 'is_correct': False},
                    {'id': 'a2', 'text': '4', 'is_correct': True},
                    {'id': 'a3', 'text': '5', 'is_correct': False}
                ],
                'tags': ['math', 'basic']
            },
            {
                'id': 'q2',
                'question_text': 'Select all prime numbers:',
                'question_type': 'select_all',
                'answers': [
                    {'id': 'a1', 'text': '2', 'is_correct': True},
                    {'id': 'a2', 'text': '4', 'is_correct': False},
                    {'id': 'a3', 'text': '7', 'is_correct': True}
                ],
                'tags': ['math', 'prime']
            }
        ]
        
        self.sample_sessions = {
            'session1': {
                'id': 'session1',
                'questions': self.sample_questions,
                'current_question_index': 1,
                'answers': [{'question_id': 'q1', 'selected_answers': 'a2', 'is_correct': True}],
                'score': 50.0,
                'start_time': datetime.now().isoformat(),
                'is_complete': False
            }
        }
    
    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_atomic_write_and_read(self):
        """Test atomic write and read operations."""
        test_data = "Test data for atomic operations"
        
        # Test atomic write
        success = self.persistence._atomic_write(self.persistence.questions_file, test_data)
        self.assertTrue(success)
        
        # Test atomic read
        read_data = self.persistence._atomic_read(self.persistence.questions_file)
        self.assertEqual(read_data, test_data)
    
    def test_question_validation(self):
        """Test comprehensive question validation."""
        # Test valid question
        valid_question = self.sample_questions[0]
        result = self.persistence._validate_question(valid_question)
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        
        # Test invalid question (missing required field)
        invalid_question = {'id': 'q1', 'question_text': 'Test?'}
        result = self.persistence._validate_question(invalid_question)
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
        
        # Test invalid question (text too short)
        invalid_question = {
            'id': 'q1',
            'question_text': 'Short',
            'question_type': 'multiple_choice',
            'answers': [{'text': 'A', 'is_correct': True}, {'text': 'B', 'is_correct': False}],
            'tags': ['test']
        }
        result = self.persistence._validate_question(invalid_question)
        self.assertFalse(result['is_valid'])
        self.assertIn('at least 10 characters', result['errors'][0])
        
        # Test invalid question (too many answers)
        invalid_question = {
            'id': 'q1',
            'question_text': 'What is the correct answer?',
            'question_type': 'multiple_choice',
            'answers': [{'text': f'Option {i}', 'is_correct': i == 0} for i in range(7)],
            'tags': ['test']
        }
        result = self.persistence._validate_question(invalid_question)
        self.assertFalse(result['is_valid'])
        self.assertIn('Maximum 6 answer options', result['errors'][0])
    
    def test_save_and_load_questions(self):
        """Test saving and loading questions with validation."""
        # Save questions
        success = self.persistence.save_questions(self.sample_questions)
        self.assertTrue(success)
        
        # Load questions
        loaded_questions = self.persistence.load_questions()
        self.assertEqual(len(loaded_questions), 2)
        self.assertEqual(loaded_questions[0]['id'], 'q1')
        self.assertEqual(loaded_questions[1]['id'], 'q2')
        
        # Verify data integrity
        for original, loaded in zip(self.sample_questions, loaded_questions):
            self.assertEqual(original['question_text'], loaded['question_text'])
            self.assertEqual(original['question_type'], loaded['question_type'])
            self.assertEqual(len(original['answers']), len(loaded['answers']))
    
    def test_checksum_validation(self):
        """Test data integrity with checksums."""
        # Save questions
        self.persistence.save_questions(self.sample_questions)
        
        # Load questions (should work with valid checksum)
        loaded_questions = self.persistence.load_questions()
        self.assertEqual(len(loaded_questions), 2)
        
        # Corrupt the file
        with open(self.persistence.questions_file, 'w') as f:
            f.write("corrupted data")
        
        # Load should fail and attempt recovery
        loaded_questions = self.persistence.load_questions()
        # Should return empty list or recovered data
        self.assertIsInstance(loaded_questions, list)
    
    def test_session_compression(self):
        """Test session storage with compression."""
        # Save sessions
        success = self.persistence.save_sessions(self.sample_sessions)
        self.assertTrue(success)
        
        # Check that compressed file exists
        compressed_file = self.persistence.sessions_file.with_suffix('.json.gz')
        self.assertTrue(compressed_file.exists())
        
        # Load sessions
        loaded_sessions = self.persistence.load_sessions()
        self.assertEqual(len(loaded_sessions), 1)
        self.assertIn('session1', loaded_sessions)
        
        # Verify data integrity
        original_session = self.sample_sessions['session1']
        loaded_session = loaded_sessions['session1']
        self.assertEqual(original_session['id'], loaded_session['id'])
        self.assertEqual(original_session['score'], loaded_session['score'])
    
    def test_backup_and_restore(self):
        """Test backup and restore functionality."""
        # Save some data first
        self.persistence.save_questions(self.sample_questions)
        self.persistence.save_sessions(self.sample_sessions)
        
        # Create backup
        success = self.persistence.backup_data()
        self.assertTrue(success)
        
        # Check backup directory exists
        self.assertTrue(self.persistence.backup_dir.exists())
        
        # Find the backup
        backup_dirs = [d for d in self.persistence.backup_dir.iterdir() if d.is_dir() and d.name.startswith('backup_')]
        self.assertGreater(len(backup_dirs), 0)
        
        backup_name = backup_dirs[0].name
        
        # Clear original data
        self.persistence.questions_file.unlink(missing_ok=True)
        self.persistence.sessions_file.with_suffix('.json.gz').unlink(missing_ok=True)
        
        # Restore from backup
        success = self.persistence.restore_data(backup_name)
        self.assertTrue(success)
        
        # Verify data was restored
        loaded_questions = self.persistence.load_questions()
        self.assertEqual(len(loaded_questions), 2)
        
        loaded_sessions = self.persistence.load_sessions()
        self.assertEqual(len(loaded_sessions), 1)
    
    def test_export_and_import(self):
        """Test data export and import functionality."""
        # Save some data
        self.persistence.save_questions(self.sample_questions)
        self.persistence.save_sessions(self.sample_sessions)
        
        # Export data
        exported_json = self.persistence.export_data("json")
        self.assertIsNotNone(exported_json)
        
        # Parse exported data
        exported_data = json.loads(exported_json)
        self.assertIn('questions', exported_data)
        self.assertIn('sessions', exported_data)
        self.assertEqual(len(exported_data['questions']), 2)
        self.assertEqual(len(exported_data['sessions']), 1)
        
        # Test CSV export
        exported_csv = self.persistence.export_data("csv")
        self.assertIsNotNone(exported_csv)
        self.assertIn('Question', exported_csv)
        self.assertIn('q1', exported_csv)
        
        # Test import
        # Clear data first
        self.persistence.questions_file.unlink(missing_ok=True)
        
        # Import data
        success = self.persistence.import_data(exported_json, "json")
        self.assertTrue(success)
        
        # Verify import
        loaded_questions = self.persistence.load_questions()
        self.assertEqual(len(loaded_questions), 2)
    
    def test_session_cleanup(self):
        """Test session cleanup functionality."""
        # Create sessions with different ages
        old_sessions = {}
        recent_sessions = {}
        
        # Old session (100 days ago)
        old_time = datetime.now() - timedelta(days=100)
        old_sessions['old_session'] = {
            'id': 'old_session',
            'end_time': old_time.isoformat(),
            'score': 80.0
        }
        
        # Recent session (10 days ago)
        recent_time = datetime.now() - timedelta(days=10)
        recent_sessions['recent_session'] = {
            'id': 'recent_session',
            'end_time': recent_time.isoformat(),
            'score': 90.0
        }
        
        # Incomplete session (no end_time)
        recent_sessions['incomplete_session'] = {
            'id': 'incomplete_session',
            'start_time': datetime.now().isoformat(),
            'is_complete': False
        }
        
        all_sessions = {**old_sessions, **recent_sessions}
        self.persistence.save_sessions(all_sessions)
        
        # Clean up sessions older than 30 days
        cleaned_count = self.persistence.cleanup_old_sessions(days=30)
        self.assertEqual(cleaned_count, 1)  # Only old_session should be cleaned
        
        # Verify remaining sessions
        remaining_sessions = self.persistence.load_sessions()
        self.assertEqual(len(remaining_sessions), 2)  # recent_session + incomplete_session
        self.assertIn('recent_session', remaining_sessions)
        self.assertIn('incomplete_session', remaining_sessions)
        self.assertNotIn('old_session', remaining_sessions)
    
    def test_data_integrity_report(self):
        """Test data integrity reporting."""
        # Save some data
        self.persistence.save_questions(self.sample_questions)
        self.persistence.save_sessions(self.sample_sessions)
        
        # Generate integrity report
        report = self.persistence.get_data_integrity_report()
        
        # Check report structure
        self.assertIn('timestamp', report)
        self.assertIn('version', report)
        self.assertIn('files', report)
        self.assertIn('overall_status', report)
        
        # Check file statuses
        self.assertIn('questions', report['files'])
        self.assertIn('sessions', report['files'])
        
        questions_status = report['files']['questions']
        self.assertTrue(questions_status['exists'])
        self.assertTrue(questions_status['checksum_valid'])
        self.assertTrue(questions_status['data_valid'])
        self.assertEqual(questions_status['valid_questions'], 2)
        self.assertEqual(questions_status['total_questions'], 2)
    
    def test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Test recovery from corrupted file
        with open(self.persistence.questions_file, 'w') as f:
            f.write("invalid json data")
        
        # Load should attempt recovery
        loaded_questions = self.persistence.load_questions()
        self.assertIsInstance(loaded_questions, list)
        
        # Test recovery from missing file
        self.persistence.questions_file.unlink(missing_ok=True)
        loaded_questions = self.persistence.load_questions()
        self.assertEqual(loaded_questions, [])
    
    def test_encryption_functionality(self):
        """Test encryption and decryption (if available)."""
        if not self.persistence._get_fernet():
            self.skipTest("Encryption not available")
        
        # Test encryption/decryption
        test_data = "Sensitive quiz data"
        encrypted_data = self.persistence._encrypt_data(test_data)
        decrypted_data = self.persistence._decrypt_data(encrypted_data)
        
        self.assertNotEqual(test_data, encrypted_data)  # Should be different
        self.assertEqual(test_data, decrypted_data)  # Should match original
    
    def test_invalid_import_data(self):
        """Test handling of invalid import data."""
        # Test invalid JSON
        invalid_json = "{ invalid json }"
        success = self.persistence.import_data(invalid_json, "json")
        self.assertFalse(success)
        
        # Test invalid question data
        invalid_data = {
            'questions': [{'id': 'q1', 'question_text': 'Short'}]  # Missing required fields
        }
        invalid_json = json.dumps(invalid_data)
        success = self.persistence.import_data(invalid_json, "json")
        self.assertFalse(success)
    
    def test_file_permissions_and_atomic_operations(self):
        """Test atomic operations with file permission issues."""
        # Test atomic write to read-only directory (should fail gracefully)
        read_only_dir = Path(self.temp_dir) / "readonly"
        read_only_dir.mkdir()
        
        try:
            read_only_dir.chmod(0o444)  # Read-only
            persistence_ro = DataPersistence(data_dir=str(read_only_dir))
            success = persistence_ro.save_questions(self.sample_questions)
            # On Windows, this might still succeed due to different permission handling
            # So we just verify the operation completes without crashing
            self.assertIsInstance(success, bool)
        except (OSError, PermissionError):
            # Expected on some systems
            pass
        finally:
            # Restore permissions for cleanup
            try:
                read_only_dir.chmod(0o755)
            except (OSError, PermissionError):
                pass
    
    def test_large_data_handling(self):
        """Test handling of large datasets."""
        # Create a large number of questions
        large_questions = []
        for i in range(100):
            question = {
                'id': f'q{i}',
                'question_text': f'Question {i}: What is the answer to question {i}?',
                'question_type': 'multiple_choice',
                'answers': [
                    {'id': f'a{i}_1', 'text': f'Option A for question {i}', 'is_correct': False},
                    {'id': f'a{i}_2', 'text': f'Option B for question {i}', 'is_correct': True},
                    {'id': f'a{i}_3', 'text': f'Option C for question {i}', 'is_correct': False}
                ],
                'tags': [f'tag{i}', 'test']
            }
            large_questions.append(question)
        
        # Save large dataset
        success = self.persistence.save_questions(large_questions)
        self.assertTrue(success)
        
        # Load large dataset
        loaded_questions = self.persistence.load_questions()
        self.assertEqual(len(loaded_questions), 100)
        
        # Verify data integrity
        for i, question in enumerate(loaded_questions):
            self.assertEqual(question['id'], f'q{i}')
            self.assertEqual(len(question['answers']), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
