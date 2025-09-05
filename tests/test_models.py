#!/usr/bin/env python3
"""
Test suite for data models

This module tests the Question and Tag models for validation,
serialization, and basic functionality.
"""

import sys
import os
import unittest
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.question import Question
from models.tag import Tag

class TestQuestionModel(unittest.TestCase):
    """Test cases for Question model."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_answers = [
            {"id": "answer_1", "text": "Option A", "is_correct": True},
            {"id": "answer_2", "text": "Option B", "is_correct": False},
            {"id": "answer_3", "text": "Option C", "is_correct": False}
        ]
        self.valid_tags = ["test", "sample"]
    
    def test_create_valid_question(self):
        """Test creating a valid question."""
        question = Question(
            question_text="What is the capital of France?",
            question_type="multiple_choice",
            answers=self.valid_answers,
            tags=self.valid_tags
        )
        
        self.assertEqual(question.question_text, "What is the capital of France?")
        self.assertEqual(question.question_type, "multiple_choice")
        self.assertEqual(len(question.answers), 3)
        self.assertEqual(question.tags, ["test", "sample"])
        self.assertTrue(question.validate()['is_valid'])
    
    def test_question_validation_empty_text(self):
        """Test question validation with empty text."""
        with self.assertRaises(ValueError):
            Question(
                question_text="",
                question_type="multiple_choice",
                answers=self.valid_answers,
                tags=self.valid_tags
            )
    
    def test_question_validation_short_text(self):
        """Test question validation with text too short."""
        with self.assertRaises(ValueError):
            Question(
                question_text="Short",
                question_type="multiple_choice",
                answers=self.valid_answers,
                tags=self.valid_tags
            )
    
    def test_question_validation_invalid_type(self):
        """Test question validation with invalid type."""
        with self.assertRaises(ValueError):
            Question(
                question_text="What is the capital of France?",
                question_type="invalid_type",
                answers=self.valid_answers,
                tags=self.valid_tags
            )
    
    def test_question_validation_no_correct_answer(self):
        """Test question validation with no correct answer."""
        invalid_answers = [
            {"id": "answer_1", "text": "Option A", "is_correct": False},
            {"id": "answer_2", "text": "Option B", "is_correct": False}
        ]
        
        with self.assertRaises(ValueError):
            Question(
                question_text="What is the capital of France?",
                question_type="multiple_choice",
                answers=invalid_answers,
                tags=self.valid_tags
            )
    
    def test_question_serialization(self):
        """Test question serialization to/from dictionary."""
        question = Question(
            question_text="What is the capital of France?",
            question_type="multiple_choice",
            answers=self.valid_answers,
            tags=self.valid_tags
        )
        
        # Test to_dict
        question_dict = question.to_dict()
        self.assertIsInstance(question_dict, dict)
        self.assertEqual(question_dict['question_text'], "What is the capital of France?")
        self.assertEqual(question_dict['question_type'], "multiple_choice")
        
        # Test from_dict
        new_question = Question.from_dict(question_dict)
        self.assertEqual(new_question.question_text, question.question_text)
        self.assertEqual(new_question.question_type, question.question_type)
        self.assertEqual(new_question.answers, question.answers)
        self.assertEqual(new_question.tags, question.tags)
    
    def test_get_correct_answers(self):
        """Test getting correct answers."""
        question = Question(
            question_text="What is the capital of France?",
            question_type="multiple_choice",
            answers=self.valid_answers,
            tags=self.valid_tags
        )
        
        correct_answers = question.get_correct_answers()
        self.assertEqual(correct_answers, ["answer_1"])
    
    def test_true_false_question(self):
        """Test creating a true/false question."""
        tf_answers = [
            {"id": "answer_1", "text": "True", "is_correct": True},
            {"id": "answer_2", "text": "False", "is_correct": False}
        ]
        
        question = Question(
            question_text="Paris is the capital of France.",
            question_type="true_false",
            answers=tf_answers,
            tags=["geography"]
        )
        
        self.assertEqual(question.question_type, "true_false")
        self.assertTrue(question.validate()['is_valid'])

class TestTagModel(unittest.TestCase):
    """Test cases for Tag model."""
    
    def test_create_valid_tag(self):
        """Test creating a valid tag."""
        tag = Tag(name="geography", description="Geography questions", color="#FF0000")
        
        self.assertEqual(tag.name, "geography")
        self.assertEqual(tag.description, "Geography questions")
        self.assertEqual(tag.color, "#FF0000")
        self.assertEqual(tag.question_count, 0)
        self.assertTrue(tag.validate()['is_valid'])
    
    def test_tag_validation_empty_name(self):
        """Test tag validation with empty name."""
        with self.assertRaises(ValueError):
            Tag(name="", description="Test tag")
    
    def test_tag_validation_invalid_name(self):
        """Test tag validation with invalid characters."""
        with self.assertRaises(ValueError):
            Tag(name="invalid name!", description="Test tag")
    
    def test_tag_validation_invalid_color(self):
        """Test tag validation with invalid color."""
        with self.assertRaises(ValueError):
            Tag(name="test", description="Test tag", color="invalid_color")
    
    def test_tag_serialization(self):
        """Test tag serialization to/from dictionary."""
        tag = Tag(name="geography", description="Geography questions", color="#FF0000")
        
        # Test to_dict
        tag_dict = tag.to_dict()
        self.assertIsInstance(tag_dict, dict)
        self.assertEqual(tag_dict['name'], "geography")
        self.assertEqual(tag_dict['description'], "Geography questions")
        
        # Test from_dict
        new_tag = Tag.from_dict(tag_dict)
        self.assertEqual(new_tag.name, tag.name)
        self.assertEqual(new_tag.description, tag.description)
        self.assertEqual(new_tag.color, tag.color)
    
    def test_tag_question_count_operations(self):
        """Test tag question count operations."""
        tag = Tag(name="test", description="Test tag")
        
        # Test increment
        tag.increment_question_count()
        self.assertEqual(tag.question_count, 1)
        
        # Test decrement
        tag.decrement_question_count()
        self.assertEqual(tag.question_count, 0)
        
        # Test decrement below zero
        tag.decrement_question_count()
        self.assertEqual(tag.question_count, 0)  # Should not go below 0
        
        # Test set count
        tag.set_question_count(5)
        self.assertEqual(tag.question_count, 5)
    
    def test_tag_is_unused(self):
        """Test tag unused status."""
        tag = Tag(name="test", description="Test tag")
        self.assertTrue(tag.is_unused())
        
        tag.increment_question_count()
        self.assertFalse(tag.is_unused())

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
