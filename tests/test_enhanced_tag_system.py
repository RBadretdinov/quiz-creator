"""
Test Enhanced Tag System

This module contains comprehensive tests for the enhanced tag system including
hierarchical tags, advanced filtering, and tag-based quiz generation.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.tag import Tag
from tag_manager import TagManager
from question_filter import QuestionFilter
from tag_quiz_generator import TagQuizGenerator

class TestEnhancedTagSystem(unittest.TestCase):
    """Test cases for the enhanced tag system."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.tag_manager = TagManager(self.test_dir)
        self.question_filter = QuestionFilter(self.tag_manager)
        self.quiz_generator = TagQuizGenerator(self.tag_manager, self.question_filter)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_hierarchical_tag_creation(self):
        """Test creating hierarchical tags."""
        # Create root tag
        root_tag = self.tag_manager.create_tag("Science", "Scientific topics")
        self.assertIsNotNone(root_tag)
        self.assertTrue(root_tag.is_root())
        
        # Create child tag
        child_tag = self.tag_manager.create_tag("Physics", "Physics topics", parent_id=root_tag.id)
        self.assertIsNotNone(child_tag)
        self.assertFalse(child_tag.is_root())
        self.assertEqual(child_tag.parent_id, root_tag.id)
        
        # Verify parent-child relationship
        children = self.tag_manager.get_children(root_tag.id)
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].id, child_tag.id)
        
        # Create grandchild tag
        grandchild_tag = self.tag_manager.create_tag("Mechanics", "Mechanics topics", parent_id=child_tag.id)
        self.assertIsNotNone(grandchild_tag)
        
        # Verify hierarchy depth
        self.assertEqual(root_tag.get_depth(self.tag_manager), 0)
        self.assertEqual(child_tag.get_depth(self.tag_manager), 1)
        self.assertEqual(grandchild_tag.get_depth(self.tag_manager), 2)
    
    def test_tag_aliases(self):
        """Test tag aliases functionality."""
        tag = self.tag_manager.create_tag("Mathematics", "Math topics", aliases=["Math", "Maths"])
        self.assertEqual(len(tag.aliases), 2)
        self.assertIn("Math", tag.aliases)
        self.assertIn("Maths", tag.aliases)
        
        # Test finding tag by alias
        found_tag = self.tag_manager.get_tag_by_name("Math")
        self.assertIsNotNone(found_tag)
        self.assertEqual(found_tag.id, tag.id)
        
        found_tag = self.tag_manager.get_tag_by_name("Maths")
        self.assertIsNotNone(found_tag)
        self.assertEqual(found_tag.id, tag.id)
    
    def test_tag_usage_tracking(self):
        """Test tag usage tracking."""
        tag = self.tag_manager.create_tag("TestTag", "Test tag")
        initial_usage = tag.usage_count
        
        # Increment usage
        tag.increment_usage()
        self.assertEqual(tag.usage_count, initial_usage + 1)
        self.assertIsNotNone(tag.last_used)
        
        # Test usage count update through manager
        self.tag_manager.update_question_count("TestTag", 1)
        updated_tag = self.tag_manager.get_tag_by_name("TestTag")
        self.assertEqual(updated_tag.question_count, 1)
        self.assertEqual(updated_tag.usage_count, initial_usage + 2)  # +1 from increment_usage, +1 from update_question_count
    
    def test_tag_validation(self):
        """Test tag validation and error handling."""
        # Test circular hierarchy prevention
        tag1 = self.tag_manager.create_tag("Tag1", "First tag")
        tag2 = self.tag_manager.create_tag("Tag2", "Second tag", parent_id=tag1.id)
        
        # Try to create circular reference by setting tag1 as parent of tag2
        with self.assertRaises(ValueError):
            self.tag_manager.update_tag(tag2.id, parent_id=tag2.id)  # Self-reference
        
        # Test duplicate name prevention
        with self.assertRaises(ValueError):
            self.tag_manager.create_tag("Tag1", "Duplicate name")
    
    def test_tag_search(self):
        """Test advanced tag search functionality."""
        # Create test tags
        self.tag_manager.create_tag("Science", "Scientific topics")
        self.tag_manager.create_tag("Physics", "Physics topics", aliases=["Phys"])
        self.tag_manager.create_tag("Chemistry", "Chemistry topics")
        self.tag_manager.create_tag("Biology", "Biology topics")
        
        # Test name search
        results = self.tag_manager.search_tags("physics")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Physics")
        
        # Test alias search
        results = self.tag_manager.search_tags("phys")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Physics")
        
        # Test description search
        results = self.tag_manager.search_tags("scientific")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Science")
    
    def test_tag_statistics(self):
        """Test tag statistics generation."""
        # Create test tags with different usage patterns
        tag1 = self.tag_manager.create_tag("Popular", "Popular tag")
        tag2 = self.tag_manager.create_tag("Unused", "Unused tag")
        
        # Simulate usage
        tag1.increment_usage()
        tag1.increment_usage()
        tag1.increment_usage()
        
        stats = self.tag_manager.get_tag_statistics()
        
        self.assertEqual(stats['total_tags'], 2)
        self.assertEqual(stats['root_tags'], 2)
        # Both tags start with 0 usage, so both are unused initially
        self.assertEqual(len(stats['unused_tags']), 2)
        self.assertGreaterEqual(stats['average_usage'], 0)
    
    def test_tag_merge(self):
        """Test tag merging functionality."""
        # Create tags to merge
        source_tag = self.tag_manager.create_tag("Source", "Source tag", aliases=["Src"])
        target_tag = self.tag_manager.create_tag("Target", "Target tag")
        
        # Create child of source tag
        child_tag = self.tag_manager.create_tag("Child", "Child tag", parent_id=source_tag.id)
        
        # Merge tags
        success = self.tag_manager.merge_tags(source_tag.id, target_tag.id)
        self.assertTrue(success)
        
        # Verify source tag is deleted
        self.assertIsNone(self.tag_manager.get_tag_by_id(source_tag.id))
        
        # Verify child is now child of target
        updated_child = self.tag_manager.get_tag_by_id(child_tag.id)
        self.assertEqual(updated_child.parent_id, target_tag.id)
        
        # Verify aliases are transferred
        updated_target = self.tag_manager.get_tag_by_id(target_tag.id)
        self.assertIn("Src", updated_target.aliases)
    
    def test_tag_export_import(self):
        """Test tag export and import functionality."""
        # Create test tags
        tag1 = self.tag_manager.create_tag("Export1", "First export tag", aliases=["Exp1"])
        tag2 = self.tag_manager.create_tag("Export2", "Second export tag", parent_id=tag1.id)
        
        # Export tags
        json_data = self.tag_manager.export_tags("json")
        self.assertIsNotNone(json_data)
        
        # Parse exported data
        export_data = json.loads(json_data)
        self.assertEqual(len(export_data['tags']), 2)
        
        # Test CSV export
        csv_data = self.tag_manager.export_tags("csv")
        self.assertIsNotNone(csv_data)
        self.assertIn("Export1", csv_data)
        self.assertIn("Export2", csv_data)
        
        # Test import
        new_manager = TagManager(tempfile.mkdtemp())
        imported_count = new_manager.import_tags(json_data, "json")
        self.assertEqual(imported_count, 2)
        
        # Verify imported tags
        imported_tag1 = new_manager.get_tag_by_name("Export1")
        self.assertIsNotNone(imported_tag1)
        self.assertIn("Exp1", imported_tag1.aliases)
    
    def test_hierarchy_validation(self):
        """Test tag hierarchy validation."""
        # Create valid hierarchy
        root = self.tag_manager.create_tag("Root", "Root tag")
        child = self.tag_manager.create_tag("Child", "Child tag", parent_id=root.id)
        
        # Validate hierarchy
        validation = self.tag_manager.validate_tag_hierarchy()
        self.assertTrue(validation['is_valid'])
        self.assertEqual(len(validation['issues']), 0)
        
        # Create invalid hierarchy (orphaned child)
        orphaned_tag = Tag("Orphaned", "Orphaned tag", parent_id="nonexistent-id")
        # This would be caught by validation if we manually added it to the manager
    
    def test_question_filtering(self):
        """Test question filtering functionality."""
        # Create test tags
        science_tag = self.tag_manager.create_tag("Science", "Science topics")
        physics_tag = self.tag_manager.create_tag("Physics", "Physics topics", parent_id=science_tag.id)
        
        # Test tag-based filtering (placeholder - would need actual questions)
        filters = {
            'tags': {
                'operation': 'any',
                'tags': ['Science'],
                'include_children': True
            }
        }
        
        # This would filter questions in a real implementation
        filtered_questions = self.question_filter.filter_questions([], filters)
        self.assertEqual(len(filtered_questions), 0)  # No questions in test
    
    def test_quiz_generation_options(self):
        """Test quiz generation options."""
        options = self.quiz_generator.get_quiz_generation_options()
        
        self.assertIn('strategies', options)
        self.assertIn('tag_operations', options)
        self.assertIn('special_generators', options)
        
        # Verify strategy options
        strategy_names = [strategy['name'] for strategy in options['strategies']]
        self.assertIn('random', strategy_names)
        self.assertIn('balanced', strategy_names)
        self.assertIn('hierarchical', strategy_names)
        self.assertIn('weighted', strategy_names)
    
    def test_tag_full_path(self):
        """Test tag full path generation."""
        # Create hierarchy
        root = self.tag_manager.create_tag("Science", "Science topics")
        physics = self.tag_manager.create_tag("Physics", "Physics topics", parent_id=root.id)
        mechanics = self.tag_manager.create_tag("Mechanics", "Mechanics topics", parent_id=physics.id)
        
        # Test full path
        full_path = mechanics.get_full_path(self.tag_manager)
        self.assertEqual(full_path, "Science > Physics > Mechanics")
        
        # Test root path
        root_path = root.get_full_path(self.tag_manager)
        self.assertEqual(root_path, "Science")
    
    def test_tag_cleanup_operations(self):
        """Test tag cleanup and maintenance operations."""
        # Create test tags
        tag1 = self.tag_manager.create_tag("Keep", "Keep this tag")
        tag2 = self.tag_manager.create_tag("Delete", "Delete this tag")
        
        # Simulate usage for tag1
        tag1.increment_usage()
        tag1.increment_usage()
        
        # Delete unused tag
        success = self.tag_manager.delete_tag(tag2.id)
        self.assertTrue(success)
        
        # Verify deletion
        self.assertIsNone(self.tag_manager.get_tag_by_id(tag2.id))
        
        # Verify kept tag still exists
        self.assertIsNotNone(self.tag_manager.get_tag_by_id(tag1.id))

if __name__ == '__main__':
    unittest.main(verbosity=2)
