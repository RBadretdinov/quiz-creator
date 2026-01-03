"""
Test Suite for Phase 4.2: File Import/Export System

This module contains comprehensive unit tests for the import/export functionality
implemented in Phase 4.2.
"""

import unittest
import sys
import os
import tempfile
import shutil
import json
import csv
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from import_export import FileImporter, FileExporter, DataMigration, ImportExportTemplates

class TestFileImporter(unittest.TestCase):
    """Test cases for FileImporter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.import_dir = os.path.join(self.temp_dir, 'imports')
        
        self.importer = FileImporter(self.import_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_importer_initialization(self):
        """Test file importer initialization."""
        self.assertIsNotNone(self.importer)
        self.assertEqual(self.importer.import_dir, Path(self.import_dir))
        self.assertEqual(len(self.importer.supported_formats), 4)
        self.assertIn('.json', self.importer.supported_formats)
        self.assertIn('.csv', self.importer.supported_formats)
    
    def test_import_json_file(self):
        """Test importing JSON file."""
        # Create test JSON file
        test_data = {
            'questions': [
                {
                    'id': 'q1',
                    'question_text': 'What is the capital of France?',
                    'question_type': 'multiple_choice',
                    'answers': [
                        {'text': 'Paris', 'is_correct': True},
                        {'text': 'London', 'is_correct': False}
                    ],
                    'tags': ['geography', 'capitals']
                }
            ],
            'tags': [
                {'id': 't1', 'name': 'geography', 'description': 'Geography questions'}
            ]
        }
        
        json_file = os.path.join(self.temp_dir, 'test.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        result = self.importer.import_file(json_file, 'json')
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['imported_data']['questions']), 1)
        self.assertEqual(len(result['imported_data']['tags']), 1)
        self.assertEqual(result['import_type'], 'json')
    
    def test_import_csv_file(self):
        """Test importing CSV file."""
        # Create test CSV file
        csv_file = os.path.join(self.temp_dir, 'test.csv')
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['question_text', 'answer_1', 'correct_1', 'answer_2', 'correct_2', 'tags'])
            writer.writerow(['What is 2+2?', '3', 'false', '4', 'true', 'math,arithmetic'])
        
        result = self.importer.import_file(csv_file, 'csv')
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['imported_data']['questions']), 1)
        self.assertEqual(result['import_type'], 'csv')
    
    def test_import_nonexistent_file(self):
        """Test importing non-existent file."""
        result = self.importer.import_file('nonexistent.json', 'json')
        
        self.assertFalse(result['success'])
        self.assertIn('File not found', result['error'])
    
    def test_import_unsupported_format(self):
        """Test importing unsupported format."""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
        
        result = self.importer.import_file(test_file, 'auto')
        
        self.assertFalse(result['success'])
        self.assertIn('Unsupported file format', result['error'])
    
    def test_batch_import_files(self):
        """Test batch importing multiple files."""
        # Create test files
        test_files = []
        for i in range(3):
            json_file = os.path.join(self.temp_dir, f'test_{i}.json')
            test_data = {
                'questions': [
                    {
                        'id': f'q{i}',
                        'question_text': f'Test question {i}?',
                        'question_type': 'multiple_choice',
                        'answers': [
                            {'text': f'Answer {i}', 'is_correct': True}
                        ]
                    }
                ]
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)
            
            test_files.append(json_file)
        
        result = self.importer.batch_import_files(test_files, 'json')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['summary']['total_files'], 3)
        self.assertEqual(result['summary']['successful'], 3)
        self.assertEqual(len(result['results']), 3)
    
    def test_import_statistics(self):
        """Test import statistics tracking."""
        # Import a file
        test_data = {'questions': [{'id': 'q1', 'question_text': 'Test?'}]}
        json_file = os.path.join(self.temp_dir, 'test.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        self.importer.import_file(json_file, 'json')
        
        stats = self.importer.get_import_statistics()
        self.assertEqual(stats['total_imports'], 1)
        self.assertEqual(stats['successful_imports'], 1)
        self.assertEqual(stats['total_questions_imported'], 1)
    
    def test_clear_import_statistics(self):
        """Test clearing import statistics."""
        # Import a file first
        test_data = {'questions': [{'id': 'q1', 'question_text': 'Test?'}]}
        json_file = os.path.join(self.temp_dir, 'test.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        self.importer.import_file(json_file, 'json')
        
        # Clear statistics
        self.importer.clear_import_statistics()
        
        stats = self.importer.get_import_statistics()
        self.assertEqual(stats['total_imports'], 0)
        self.assertEqual(stats['successful_imports'], 0)


class TestFileExporter(unittest.TestCase):
    """Test cases for FileExporter."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.export_dir = os.path.join(self.temp_dir, 'exports')
        
        self.exporter = FileExporter(self.export_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_exporter_initialization(self):
        """Test file exporter initialization."""
        self.assertIsNotNone(self.exporter)
        self.assertEqual(self.exporter.export_dir, Path(self.export_dir))
        self.assertEqual(len(self.exporter.supported_formats), 5)
        self.assertIn('json', self.exporter.supported_formats)
        self.assertIn('csv', self.exporter.supported_formats)
        self.assertIn('pdf', self.exporter.supported_formats)
    
    def test_export_json(self):
        """Test exporting to JSON format."""
        test_data = {
            'questions': [
                {
                    'id': 'q1',
                    'question_text': 'What is the capital of France?',
                    'question_type': 'multiple_choice',
                    'answers': [
                        {'text': 'Paris', 'is_correct': True},
                        {'text': 'London', 'is_correct': False}
                    ]
                }
            ],
            'tags': [
                {'id': 't1', 'name': 'geography', 'description': 'Geography questions'}
            ]
        }
        
        result = self.exporter.export_data(test_data, 'json')
        
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(result['output_path']))
        self.assertEqual(result['export_format'], 'json')
    
    def test_export_csv(self):
        """Test exporting to CSV format."""
        test_data = {
            'questions': [
                {
                    'id': 'q1',
                    'question_text': 'What is 2+2?',
                    'question_type': 'multiple_choice',
                    'answers': [
                        {'text': '3', 'is_correct': False},
                        {'text': '4', 'is_correct': True}
                    ]
                }
            ]
        }
        
        result = self.exporter.export_data(test_data, 'csv')
        
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(result['output_path']))
        self.assertEqual(result['export_format'], 'csv')
    
    def test_export_unsupported_format(self):
        """Test exporting to unsupported format."""
        test_data = {'questions': []}
        
        result = self.exporter.export_data(test_data, 'unsupported')
        
        self.assertFalse(result['success'])
        self.assertIn('Unsupported export format', result['error'])
    
    def test_batch_export_data(self):
        """Test batch exporting multiple datasets."""
        test_data_list = [
            {'questions': [{'id': 'q1', 'question_text': 'Question 1?'}]},
            {'questions': [{'id': 'q2', 'question_text': 'Question 2?'}]},
            {'questions': [{'id': 'q3', 'question_text': 'Question 3?'}]}
        ]
        
        result = self.exporter.batch_export_data(test_data_list, 'json')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['summary']['total_datasets'], 3)
        self.assertEqual(result['summary']['successful'], 3)
        self.assertEqual(len(result['results']), 3)
    
    def test_export_statistics(self):
        """Test export statistics tracking."""
        # Export data
        test_data = {'questions': [{'id': 'q1', 'question_text': 'Test?'}]}
        self.exporter.export_data(test_data, 'json')
        
        stats = self.exporter.get_export_statistics()
        self.assertEqual(stats['total_exports'], 1)
        self.assertEqual(stats['successful_exports'], 1)
        self.assertEqual(stats['total_questions_exported'], 1)
    
    def test_clear_export_statistics(self):
        """Test clearing export statistics."""
        # Export data first
        test_data = {'questions': [{'id': 'q1', 'question_text': 'Test?'}]}
        self.exporter.export_data(test_data, 'json')
        
        # Clear statistics
        self.exporter.clear_export_statistics()
        
        stats = self.exporter.get_export_statistics()
        self.assertEqual(stats['total_exports'], 0)
        self.assertEqual(stats['successful_exports'], 0)


class TestDataMigration(unittest.TestCase):
    """Test cases for DataMigration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.migration_dir = os.path.join(self.temp_dir, 'migrations')
        
        self.migration = DataMigration(self.migration_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_migration_initialization(self):
        """Test data migration initialization."""
        self.assertIsNotNone(self.migration)
        self.assertEqual(self.migration.migration_dir, Path(self.migration_dir))
        self.assertEqual(self.migration.current_version, "1.0")
        self.assertEqual(len(self.migration.migration_history), 0)
    
    def test_migrate_data(self):
        """Test data migration."""
        # Create source data
        source_data = {
            'questions': [
                {
                    'id': 'q1',
                    'question_text': 'What is the capital of France?',
                    'question_type': 'multiple_choice',
                    'answers': [
                        {'text': 'Paris', 'is_correct': True},
                        {'text': 'London', 'is_correct': False}
                    ]
                }
            ],
            'tags': [
                {'id': 't1', 'name': 'geography', 'description': 'Geography questions'}
            ]
        }
        
        source_file = os.path.join(self.temp_dir, 'source.json')
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(source_data, f)
        
        target_file = os.path.join(self.temp_dir, 'target.json')
        
        result = self.migration.migrate_data(source_file, target_file, 'json_to_sqlite')
        
        self.assertTrue(result['success'])
        self.assertTrue(os.path.exists(target_file))
        self.assertIsNotNone(result['migration_id'])
    
    def test_migrate_nonexistent_source(self):
        """Test migration with non-existent source."""
        result = self.migration.migrate_data('nonexistent.json', 'target.json', 'json_to_sqlite')
        
        self.assertFalse(result['success'])
        self.assertIn('Source path does not exist', result['error'])
    
    def test_rollback_migration(self):
        """Test migration rollback."""
        # First perform a migration
        source_data = {'questions': [{'id': 'q1', 'question_text': 'Test?'}]}
        source_file = os.path.join(self.temp_dir, 'source.json')
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(source_data, f)
        
        target_file = os.path.join(self.temp_dir, 'target.json')
        migration_result = self.migration.migrate_data(source_file, target_file, 'json_to_sqlite')
        
        self.assertTrue(migration_result['success'])
        
        # Now rollback
        rollback_result = self.migration.rollback_migration(migration_result['migration_id'])
        
        self.assertTrue(rollback_result['success'])
        self.assertEqual(rollback_result['migration_id'], migration_result['migration_id'])
    
    def test_rollback_nonexistent_migration(self):
        """Test rollback of non-existent migration."""
        result = self.migration.rollback_migration('nonexistent_migration')
        
        self.assertFalse(result['success'])
        self.assertIn('Migration nonexistent_migration not found', result['error'])
    
    def test_batch_migrate_data(self):
        """Test batch data migration."""
        # Create source data files
        migration_tasks = []
        for i in range(3):
            source_data = {'questions': [{'id': f'q{i}', 'question_text': f'Question {i}?'}]}
            source_file = os.path.join(self.temp_dir, f'source_{i}.json')
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(source_data, f)
            
            target_file = os.path.join(self.temp_dir, f'target_{i}.json')
            migration_tasks.append({
                'source_path': source_file,
                'target_path': target_file,
                'migration_type': 'json_to_sqlite'
            })
        
        result = self.migration.batch_migrate_data(migration_tasks)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['summary']['total_tasks'], 3)
        self.assertEqual(result['summary']['successful'], 3)
        self.assertEqual(len(result['results']), 3)
    
    def test_migration_statistics(self):
        """Test migration statistics tracking."""
        # Perform a migration
        source_data = {'questions': [{'id': 'q1', 'question_text': 'Test?'}]}
        source_file = os.path.join(self.temp_dir, 'source.json')
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(source_data, f)
        
        target_file = os.path.join(self.temp_dir, 'target.json')
        self.migration.migrate_data(source_file, target_file, 'json_to_sqlite')
        
        stats = self.migration.get_migration_statistics()
        self.assertEqual(stats['total_migrations'], 1)
        self.assertEqual(stats['successful_migrations'], 1)
    
    def test_clear_migration_history(self):
        """Test clearing migration history."""
        # Perform a migration first
        source_data = {'questions': [{'id': 'q1', 'question_text': 'Test?'}]}
        source_file = os.path.join(self.temp_dir, 'source.json')
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(source_data, f)
        
        target_file = os.path.join(self.temp_dir, 'target.json')
        self.migration.migrate_data(source_file, target_file, 'json_to_sqlite')
        
        # Clear history
        self.migration.clear_migration_history()
        
        history = self.migration.get_migration_history()
        self.assertEqual(len(history), 0)


class TestImportExportTemplates(unittest.TestCase):
    """Test cases for ImportExportTemplates."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.templates_dir = os.path.join(self.temp_dir, 'templates')
        
        self.templates = ImportExportTemplates(self.templates_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_templates_initialization(self):
        """Test templates initialization."""
        self.assertIsNotNone(self.templates)
        self.assertEqual(self.templates.templates_dir, Path(self.templates_dir))
        self.assertIsNotNone(self.templates._templates)
        self.assertIsNotNone(self.templates._import_templates)
    
    def test_get_export_template(self):
        """Test getting export template."""
        template = self.templates.get_export_template('basic_export')
        
        self.assertIsNotNone(template)
        self.assertEqual(template['name'], 'Basic Export')
        self.assertEqual(template['format'], 'json')
    
    def test_get_import_template(self):
        """Test getting import template."""
        template = self.templates.get_import_template('basic_import')
        
        self.assertIsNotNone(template)
        self.assertEqual(template['name'], 'Basic Import')
        self.assertEqual(template['format'], 'json')
    
    def test_get_nonexistent_template(self):
        """Test getting non-existent template."""
        template = self.templates.get_export_template('nonexistent')
        
        self.assertIsNone(template)
    
    def test_create_custom_template(self):
        """Test creating custom template."""
        template_data = {
            'name': 'Custom Export',
            'description': 'Custom export template',
            'format': 'json',
            'options': {
                'include_metadata': True,
                'compress': False
            }
        }
        
        result = self.templates.create_custom_template('custom_export', template_data, 'export')
        
        self.assertTrue(result)
        
        # Verify template was created
        template = self.templates.get_export_template('custom_export')
        self.assertIsNotNone(template)
        self.assertEqual(template['name'], 'Custom Export')
    
    def test_get_available_templates(self):
        """Test getting available templates."""
        templates = self.templates.get_available_templates()
        
        self.assertIn('export_templates', templates)
        self.assertIn('import_templates', templates)
        self.assertIsInstance(templates['export_templates'], list)
        self.assertIsInstance(templates['import_templates'], list)
    
    def test_get_template_schema(self):
        """Test getting template schema."""
        schema = self.templates.get_template_schema('basic_export')
        
        self.assertIsNotNone(schema)
        self.assertIn('name', schema)
        self.assertIn('description', schema)
        self.assertIn('format', schema)
        self.assertIn('options', schema)
    
    def test_validate_template(self):
        """Test template validation."""
        # Valid template
        valid_template = {
            'name': 'Test Template',
            'description': 'Test description',
            'format': 'json',
            'options': {'include_metadata': True}
        }
        
        result = self.templates.validate_template(valid_template)
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        
        # Invalid template
        invalid_template = {
            'name': 'Test Template',
            'format': 'invalid_format'
        }
        
        result = self.templates.validate_template(invalid_template)
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_export_templates(self):
        """Test exporting templates."""
        result = self.templates.export_templates()
        
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists(result))
    
    def test_import_templates(self):
        """Test importing templates."""
        # First export templates
        export_path = self.templates.export_templates()
        
        # Create new template system
        new_templates = ImportExportTemplates(os.path.join(self.temp_dir, 'new_templates'))
        
        # Import templates
        result = new_templates.import_templates(export_path)
        
        self.assertTrue(result)


class TestImportExportIntegration(unittest.TestCase):
    """Integration tests for import/export functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        self.importer = FileImporter(os.path.join(self.temp_dir, 'imports'))
        self.exporter = FileExporter(os.path.join(self.temp_dir, 'exports'))
        self.migration = DataMigration(os.path.join(self.temp_dir, 'migrations'))
        self.templates = ImportExportTemplates(os.path.join(self.temp_dir, 'templates'))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_import_export_workflow(self):
        """Test complete import/export workflow."""
        # Create test data
        test_data = {
            'questions': [
                {
                    'id': 'q1',
                    'question_text': 'What is the capital of France?',
                    'question_type': 'multiple_choice',
                    'answers': [
                        {'text': 'Paris', 'is_correct': True},
                        {'text': 'London', 'is_correct': False}
                    ]
                }
            ],
            'tags': [
                {'id': 't1', 'name': 'geography', 'description': 'Geography questions'}
            ]
        }
        
        # Export data
        export_result = self.exporter.export_data(test_data, 'json')
        self.assertTrue(export_result['success'])
        
        # Import data
        import_result = self.importer.import_file(export_result['output_path'], 'json')
        self.assertTrue(import_result['success'])
        
        # Verify data integrity
        self.assertEqual(len(import_result['imported_data']['questions']), 1)
        self.assertEqual(len(import_result['imported_data']['tags']), 1)
    
    def test_migration_workflow(self):
        """Test complete migration workflow."""
        # Create source data
        source_data = {
            'questions': [
                {
                    'id': 'q1',
                    'question_text': 'What is 2+2?',
                    'question_type': 'multiple_choice',
                    'answers': [
                        {'text': '3', 'is_correct': False},
                        {'text': '4', 'is_correct': True}
                    ]
                }
            ]
        }
        
        source_file = os.path.join(self.temp_dir, 'source.json')
        with open(source_file, 'w', encoding='utf-8') as f:
            json.dump(source_data, f)
        
        target_file = os.path.join(self.temp_dir, 'target.json')
        
        # Perform migration
        migration_result = self.migration.migrate_data(source_file, target_file, 'json_to_sqlite')
        self.assertTrue(migration_result['success'])
        
        # Verify target file exists
        self.assertTrue(os.path.exists(target_file))
        
        # Rollback migration
        rollback_result = self.migration.rollback_migration(migration_result['migration_id'])
        self.assertTrue(rollback_result['success'])
    
    def test_template_integration(self):
        """Test template integration with import/export."""
        # Get export template
        template = self.templates.get_export_template('basic_export')
        self.assertIsNotNone(template)
        
        # Use template for export
        test_data = {'questions': [{'id': 'q1', 'question_text': 'Test?'}]}
        export_result = self.exporter.export_data(test_data, 'json')
        self.assertTrue(export_result['success'])
        
        # Get import template
        import_template = self.templates.get_import_template('basic_import')
        self.assertIsNotNone(import_template)
        
        # Use template for import
        import_result = self.importer.import_file(export_result['output_path'], 'json')
        self.assertTrue(import_result['success'])


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run tests
    unittest.main(verbosity=2)
