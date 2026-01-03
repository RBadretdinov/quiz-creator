"""
Test Enhanced Question Management Phase 2.3

This module contains comprehensive tests for the enhanced question management system
including browsing, editing, bulk operations, versioning, and quality analysis.
"""

import unittest
import tempfile
import shutil
import json
import os
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from question_versioning import QuestionVersioning
from question_quality_analyzer import QuestionQualityAnalyzer
from question_import_export import QuestionImportExport
from question_manager import QuestionManager
from tag_manager import TagManager

class TestEnhancedQuestionManagementPhase23(unittest.TestCase):
    """Test cases for Phase 2.3 enhanced question management."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.question_manager = QuestionManager()
        self.tag_manager = TagManager()
        self.versioning = QuestionVersioning(os.path.join(self.temp_dir, 'versions.json'))
        self.quality_analyzer = QuestionQualityAnalyzer()
        self.import_export = QuestionImportExport(self.question_manager, self.tag_manager)
        
        # Create test questions
        self.test_questions = [
            {
                'id': 'test-1',
                'question_text': 'What is the capital of France?',
                'question_type': 'multiple_choice',
                'answers': [
                    {'text': 'Paris', 'is_correct': True},
                    {'text': 'London', 'is_correct': False},
                    {'text': 'Berlin', 'is_correct': False}
                ],
                'tags': ['geography', 'europe'],
                'created_at': '2023-01-01T00:00:00',
                'last_modified': '2023-01-01T00:00:00',
                'usage_count': 5
            },
            {
                'id': 'test-2',
                'question_text': 'Is the Earth round?',
                'question_type': 'true_false',
                'answers': [
                    {'text': 'True', 'is_correct': True},
                    {'text': 'False', 'is_correct': False}
                ],
                'tags': ['science', 'astronomy'],
                'created_at': '2023-01-02T00:00:00',
                'last_modified': '2023-01-02T00:00:00',
                'usage_count': 3
            }
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_question_versioning(self):
        """Test question versioning functionality."""
        question = self.test_questions[0]
        
        # Create initial version
        version_id = self.versioning.create_version(question, "Initial version")
        self.assertIsNotNone(version_id)
        
        # Get version history
        history = self.versioning.get_question_history(question['id'])
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['version_id'], version_id)
        
        # Get latest version
        latest = self.versioning.get_latest_version(question['id'])
        self.assertIsNotNone(latest)
        self.assertEqual(latest['version_id'], version_id)
        
        # Create another version
        modified_question = question.copy()
        modified_question['question_text'] = 'What is the capital of France? (Modified)'
        version_id2 = self.versioning.create_version(modified_question, "Modified version")
        
        # Check history
        history = self.versioning.get_question_history(question['id'])
        self.assertEqual(len(history), 2)
        
        # Compare versions
        comparison = self.versioning.compare_versions(version_id, version_id2)
        self.assertTrue(comparison['has_changes'])
        self.assertGreaterEqual(len(comparison['changes']), 1)
        # Check if question_text change is in the changes
        change_fields = [change['field'] for change in comparison['changes']]
        self.assertIn('question_text', change_fields)
    
    def test_question_quality_analysis(self):
        """Test question quality analysis."""
        question = self.test_questions[0]
        
        # Analyze question quality
        analysis = self.quality_analyzer.analyze_question_quality(question)
        
        # Check analysis structure
        self.assertIn('overall_score', analysis)
        self.assertIn('scores', analysis)
        self.assertIn('suggestions', analysis)
        self.assertIn('strengths', analysis)
        self.assertIn('weaknesses', analysis)
        
        # Check individual scores
        self.assertIn('clarity', analysis['scores'])
        self.assertIn('difficulty_balance', analysis['scores'])
        self.assertIn('answer_quality', analysis['scores'])
        self.assertIn('tagging', analysis['scores'])
        self.assertIn('structure', analysis['scores'])
        
        # Check score ranges
        for score in analysis['scores'].values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
        
        # Test quality grade
        grade = self.quality_analyzer.get_quality_grade(analysis['overall_score'])
        self.assertIn(grade, ['A', 'B', 'C', 'D', 'F'])
    
    def test_question_bank_quality_analysis(self):
        """Test question bank quality analysis."""
        analysis = self.quality_analyzer.analyze_question_bank_quality(self.test_questions)
        
        # Check analysis structure
        self.assertIn('total_questions', analysis)
        self.assertIn('average_quality_score', analysis)
        self.assertIn('grade_distribution', analysis)
        self.assertIn('component_averages', analysis)
        self.assertIn('common_suggestions', analysis)
        
        # Check values
        self.assertEqual(analysis['total_questions'], 2)
        self.assertGreaterEqual(analysis['average_quality_score'], 0.0)
        self.assertLessEqual(analysis['average_quality_score'], 1.0)
        
        # Check grade distribution
        total_grades = sum(analysis['grade_distribution'].values())
        self.assertEqual(total_grades, 2)
    
    def test_question_export_json(self):
        """Test JSON export functionality."""
        output_path = os.path.join(self.temp_dir, 'export.json')
        
        # Export questions
        success = self.import_export.export_questions_json(self.test_questions, output_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify export content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('export_info', data)
        self.assertIn('questions', data)
        self.assertEqual(len(data['questions']), 2)
        self.assertEqual(data['export_info']['question_count'], 2)
    
    def test_question_export_csv(self):
        """Test CSV export functionality."""
        output_path = os.path.join(self.temp_dir, 'export.csv')
        
        # Export questions
        success = self.import_export.export_questions_csv(self.test_questions, output_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify export content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('Question Text', content)
        self.assertIn('Question Type', content)
        self.assertIn('What is the capital of France?', content)
        self.assertIn('Is the Earth round?', content)
    
    def test_question_export_html(self):
        """Test HTML export functionality."""
        output_path = os.path.join(self.temp_dir, 'export.html')
        
        # Export questions
        success = self.import_export.export_questions_html(self.test_questions, output_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        
        # Verify export content
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn('<html>', content)
        self.assertIn('<title>', content)
        self.assertIn('What is the capital of France?', content)
        self.assertIn('Is the Earth round?', content)
    
    def test_question_import_json(self):
        """Test JSON import functionality."""
        # Create test export file
        export_path = os.path.join(self.temp_dir, 'test_export.json')
        self.import_export.export_questions_json(self.test_questions, export_path)
        
        # Import questions
        result = self.import_export.import_questions_json(export_path, validate=True)
        
        # Check import result
        self.assertTrue(result['success'])
        self.assertEqual(result['imported_count'], 2)
        self.assertEqual(result['failed_count'], 0)
        self.assertEqual(len(result['errors']), 0)
    
    def test_question_import_csv(self):
        """Test CSV import functionality."""
        # Create test CSV file
        csv_path = os.path.join(self.temp_dir, 'test_import.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            import csv
            writer = csv.writer(f)
            writer.writerow(['Question Text', 'Question Type', 'Answers', 'Correct Answers', 'Tags'])
            writer.writerow([
                'What is 2+2?',
                'multiple_choice',
                '3|4|5|6',
                '4',
                'math,arithmetic'
            ])
        
        # Import questions
        result = self.import_export.import_questions_csv(csv_path, validate=True)
        
        # Check import result
        self.assertTrue(result['success'])
        self.assertEqual(result['imported_count'], 1)
        self.assertEqual(result['failed_count'], 0)
    
    def test_import_validation(self):
        """Test import file validation."""
        # Test valid JSON file
        valid_json_path = os.path.join(self.temp_dir, 'valid.json')
        self.import_export.export_questions_json(self.test_questions, valid_json_path)
        
        validation = self.import_export.validate_import_file(valid_json_path, 'json')
        self.assertTrue(validation['is_valid'])
        self.assertEqual(validation['question_count'], 2)
        self.assertEqual(len(validation['errors']), 0)
        
        # Test invalid JSON file
        invalid_json_path = os.path.join(self.temp_dir, 'invalid.json')
        with open(invalid_json_path, 'w') as f:
            f.write('{"invalid": "json"}')
        
        validation = self.import_export.validate_import_file(invalid_json_path, 'json')
        self.assertFalse(validation['is_valid'])
        self.assertGreater(len(validation['errors']), 0)
    
    def test_version_statistics(self):
        """Test version statistics functionality."""
        # Create some versions
        for i, question in enumerate(self.test_questions):
            self.versioning.create_version(question, f"Version {i+1}")
        
        # Get statistics
        stats = self.versioning.get_version_statistics()
        
        # Check statistics structure
        self.assertIn('total_questions_with_versions', stats)
        self.assertIn('total_versions', stats)
        self.assertIn('average_versions_per_question', stats)
        self.assertIn('most_versions', stats)
        self.assertIn('recent_activity', stats)
        
        # Check values
        self.assertEqual(stats['total_questions_with_versions'], 2)
        self.assertEqual(stats['total_versions'], 2)
        self.assertEqual(stats['average_versions_per_question'], 1.0)
    
    def test_version_cleanup(self):
        """Test version cleanup functionality."""
        # Create multiple versions for one question
        question = self.test_questions[0]
        for i in range(8):  # Create 8 versions
            modified_question = question.copy()
            modified_question['question_text'] = f"Question {i+1}"
            self.versioning.create_version(modified_question, f"Version {i+1}")
        
        # Check initial count
        history = self.versioning.get_question_history(question['id'])
        self.assertEqual(len(history), 8)
        
        # Cleanup old versions (keep 5)
        removed_count = self.versioning.cleanup_old_versions(keep_versions=5)
        self.assertEqual(removed_count, 3)
        
        # Check final count
        history = self.versioning.get_question_history(question['id'])
        self.assertEqual(len(history), 5)
    
    def test_version_revert(self):
        """Test version revert functionality."""
        question = self.test_questions[0]
        
        # Create initial version
        version_id = self.versioning.create_version(question, "Initial version")
        
        # Modify question
        modified_question = question.copy()
        modified_question['question_text'] = 'Modified question'
        self.versioning.create_version(modified_question, "Modified version")
        
        # Revert to initial version
        reverted_question = self.versioning.revert_to_version(version_id)
        
        # Check revert result
        self.assertIsNotNone(reverted_question)
        self.assertEqual(reverted_question['question_text'], question['question_text'])
        
        # Check that new version was created
        history = self.versioning.get_question_history(question['id'])
        self.assertEqual(len(history), 3)  # Initial + Modified + Revert
    
    def test_export_formats(self):
        """Test export format information."""
        formats = self.import_export.get_export_formats()
        
        self.assertEqual(len(formats), 3)
        format_names = [fmt['format'] for fmt in formats]
        self.assertIn('json', format_names)
        self.assertIn('csv', format_names)
        self.assertIn('html', format_names)
    
    def test_import_formats(self):
        """Test import format information."""
        formats = self.import_export.get_import_formats()
        
        self.assertEqual(len(formats), 2)
        format_names = [fmt['format'] for fmt in formats]
        self.assertIn('json', format_names)
        self.assertIn('csv', format_names)
    
    def test_quality_analysis_edge_cases(self):
        """Test quality analysis with edge cases."""
        # Test with minimal question
        minimal_question = {
            'question_text': 'Test?',
            'question_type': 'multiple_choice',
            'answers': [
                {'text': 'A', 'is_correct': True},
                {'text': 'B', 'is_correct': False}
            ],
            'tags': ['test']
        }
        
        analysis = self.quality_analyzer.analyze_question_quality(minimal_question)
        self.assertIsNotNone(analysis)
        self.assertIn('overall_score', analysis)
        
        # Test with empty question
        empty_question = {
            'question_text': '',
            'question_type': 'multiple_choice',
            'answers': [],
            'tags': []
        }
        
        analysis = self.quality_analyzer.analyze_question_quality(empty_question)
        self.assertIsNotNone(analysis)
        self.assertIn('overall_score', analysis)
    
    def test_version_export_import(self):
        """Test version export and import functionality."""
        question = self.test_questions[0]
        
        # Create versions
        self.versioning.create_version(question, "Version 1")
        modified_question = question.copy()
        modified_question['question_text'] = 'Modified'
        self.versioning.create_version(modified_question, "Version 2")
        
        # Export version history
        export_path = os.path.join(self.temp_dir, 'version_history.json')
        success = self.versioning.export_question_history(question['id'], export_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_path))
        
        # Import version history (use the exported file)
        success = self.versioning.import_question_history(export_path)
        self.assertTrue(success)

if __name__ == '__main__':
    unittest.main(verbosity=2)
