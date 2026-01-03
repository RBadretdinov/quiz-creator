"""
Test Question Types Phase 2.2

This module contains comprehensive tests for the advanced question type system
including validation, scoring, templates, and conversion functionality.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from question_type_validator import QuestionTypeValidator
from question_scorer import QuestionScorer
from question_templates import QuestionTemplates
from question_type_converter import QuestionTypeConverter

class TestQuestionTypesPhase22(unittest.TestCase):
    """Test cases for Phase 2.2 question type enhancements."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = QuestionTypeValidator()
        self.scorer = QuestionScorer()
        self.templates = QuestionTemplates()
        self.converter = QuestionTypeConverter()
    
    def test_question_type_validation(self):
        """Test question type validation."""
        # Test valid question types
        for question_type in ['multiple_choice', 'true_false', 'select_all']:
            result = self.validator.validate_question_type(question_type)
            self.assertTrue(result['is_valid'])
            self.assertIn('type_info', result)
        
        # Test invalid question type
        result = self.validator.validate_question_type('invalid_type')
        self.assertFalse(result['is_valid'])
        self.assertIn('error', result)
    
    def test_multiple_choice_validation(self):
        """Test multiple choice question validation."""
        # Valid multiple choice
        answers = [
            {'text': 'Option A', 'is_correct': True},
            {'text': 'Option B', 'is_correct': False},
            {'text': 'Option C', 'is_correct': False}
        ]
        
        result = self.validator.validate_answers_for_type('multiple_choice', answers)
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['correct_count'], 1)
        
        # Invalid - no correct answer
        invalid_answers = [
            {'text': 'Option A', 'is_correct': False},
            {'text': 'Option B', 'is_correct': False}
        ]
        
        result = self.validator.validate_answers_for_type('multiple_choice', invalid_answers)
        self.assertFalse(result['is_valid'])
        self.assertIn('exactly one correct answer', result['errors'][0])
        
        # Invalid - multiple correct answers
        invalid_answers = [
            {'text': 'Option A', 'is_correct': True},
            {'text': 'Option B', 'is_correct': True}
        ]
        
        result = self.validator.validate_answers_for_type('multiple_choice', invalid_answers)
        self.assertFalse(result['is_valid'])
        self.assertIn('exactly one correct answer', result['errors'][0])
    
    def test_true_false_validation(self):
        """Test true/false question validation."""
        # Valid true/false
        answers = [
            {'text': 'True', 'is_correct': True},
            {'text': 'False', 'is_correct': False}
        ]
        
        result = self.validator.validate_answers_for_type('true_false', answers)
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['correct_count'], 1)
        
        # Invalid - wrong number of answers
        invalid_answers = [
            {'text': 'True', 'is_correct': True},
            {'text': 'False', 'is_correct': False},
            {'text': 'Maybe', 'is_correct': False}
        ]
        
        result = self.validator.validate_answers_for_type('true_false', invalid_answers)
        self.assertFalse(result['is_valid'])
        self.assertIn('Maximum 2 answers allowed', result['errors'][0])
    
    def test_select_all_validation(self):
        """Test select all question validation."""
        # Valid select all
        answers = [
            {'text': 'Option A', 'is_correct': True},
            {'text': 'Option B', 'is_correct': False},
            {'text': 'Option C', 'is_correct': True},
            {'text': 'Option D', 'is_correct': False}
        ]
        
        result = self.validator.validate_answers_for_type('select_all', answers)
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['correct_count'], 2)
        
        # Invalid - no correct answers
        invalid_answers = [
            {'text': 'Option A', 'is_correct': False},
            {'text': 'Option B', 'is_correct': False}
        ]
        
        result = self.validator.validate_answers_for_type('select_all', invalid_answers)
        self.assertFalse(result['is_valid'])
        self.assertIn('at least one correct answer', result['errors'][0])
    
    def test_multiple_choice_scoring(self):
        """Test multiple choice scoring."""
        correct_answers = [
            {'text': 'Option A', 'is_correct': True},
            {'text': 'Option B', 'is_correct': False},
            {'text': 'Option C', 'is_correct': False}
        ]
        
        # Correct answer
        result = self.scorer.calculate_score('multiple_choice', correct_answers, [0])
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['points_earned'], 1)
        self.assertEqual(result['feedback'], 'Correct')
        
        # Incorrect answer
        result = self.scorer.calculate_score('multiple_choice', correct_answers, [1])
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['points_earned'], 0)
        self.assertEqual(result['feedback'], 'Incorrect')
        
        # Invalid selection count
        result = self.scorer.calculate_score('multiple_choice', correct_answers, [0, 1])
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['points_earned'], 0)
        self.assertIn('exactly one selection', result['details'])
    
    def test_true_false_scoring(self):
        """Test true/false scoring."""
        correct_answers = [
            {'text': 'True', 'is_correct': True},
            {'text': 'False', 'is_correct': False}
        ]
        
        # Correct answer
        result = self.scorer.calculate_score('true_false', correct_answers, [0])
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['points_earned'], 1)
        self.assertEqual(result['feedback'], 'Correct')
        
        # Incorrect answer
        result = self.scorer.calculate_score('true_false', correct_answers, [1])
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['points_earned'], 0)
        self.assertEqual(result['feedback'], 'Incorrect')
    
    def test_select_all_scoring(self):
        """Test select all scoring with partial credit."""
        correct_answers = [
            {'text': 'Option A', 'is_correct': True},
            {'text': 'Option B', 'is_correct': False},
            {'text': 'Option C', 'is_correct': True},
            {'text': 'Option D', 'is_correct': False}
        ]
        
        # Perfect answer
        result = self.scorer.calculate_score('select_all', correct_answers, [0, 2])
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['points_earned'], 1)
        self.assertEqual(result['feedback'], 'Correct')
        
        # Partial credit - correct selections only
        result = self.scorer.calculate_score('select_all', correct_answers, [0])
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['points_earned'], 0.5)  # 1/2 correct
        self.assertEqual(result['feedback'], 'Partially Correct')
        
        # Partial credit - correct and incorrect selections
        result = self.scorer.calculate_score('select_all', correct_answers, [0, 1])
        self.assertFalse(result['is_correct'])
        self.assertLess(result['points_earned'], 0.5)  # Penalty for incorrect
        self.assertEqual(result['feedback'], 'Incorrect')
        
        # No selections
        result = self.scorer.calculate_score('select_all', correct_answers, [])
        self.assertFalse(result['is_correct'])
        self.assertEqual(result['points_earned'], 0)
        self.assertEqual(result['feedback'], 'Incorrect')
    
    def test_question_templates(self):
        """Test question templates functionality."""
        # Test getting all templates
        templates = self.templates.get_all_templates()
        self.assertIn('multiple_choice', templates)
        self.assertIn('true_false', templates)
        self.assertIn('select_all', templates)
        
        # Test getting specific template
        template = self.templates.get_template('multiple_choice')
        self.assertIsNotNone(template)
        self.assertEqual(template['name'], 'Multiple Choice')
        self.assertIn('answers', template['template'])
        
        # Test getting examples
        examples = self.templates.get_examples('multiple_choice')
        self.assertIsInstance(examples, list)
        self.assertGreater(len(examples), 0)
        
        # Test creating question from template
        question = self.templates.create_question_from_template(
            'multiple_choice',
            custom_text="What is the capital of France?",
            custom_tags=['geography']
        )
        self.assertEqual(question['question_text'], "What is the capital of France?")
        self.assertEqual(question['question_type'], 'multiple_choice')
        self.assertEqual(question['tags'], ['geography'])
    
    def test_subject_presets(self):
        """Test subject-specific presets."""
        # Test getting all presets
        presets = self.templates.get_all_subject_presets()
        self.assertIn('science', presets)
        self.assertIn('mathematics', presets)
        self.assertIn('history', presets)
        self.assertIn('programming', presets)
        
        # Test getting specific preset
        science_preset = self.templates.get_subject_preset('science')
        self.assertIsNotNone(science_preset)
        self.assertEqual(science_preset['name'], 'Science')
        self.assertIn('science', science_preset['tags'])
        self.assertIn('templates', science_preset)
    
    def test_question_type_conversion(self):
        """Test question type conversion functionality."""
        # Test conversion possibilities
        self.assertTrue(self.converter.can_convert('multiple_choice', 'true_false'))
        self.assertTrue(self.converter.can_convert('multiple_choice', 'select_all'))
        self.assertTrue(self.converter.can_convert('true_false', 'multiple_choice'))
        self.assertTrue(self.converter.can_convert('select_all', 'multiple_choice'))
        
        self.assertFalse(self.converter.can_convert('true_false', 'select_all'))
        self.assertFalse(self.converter.can_convert('select_all', 'true_false'))
        
        # Test getting conversion options
        options = self.converter.get_conversion_options('multiple_choice')
        self.assertIn('true_false', options)
        self.assertIn('select_all', options)
        
        # Test multiple choice to true/false conversion
        mc_question = {
            'question_text': 'What is 2+2?',
            'question_type': 'multiple_choice',
            'answers': [
                {'text': '4', 'is_correct': True},
                {'text': '3', 'is_correct': False}
            ],
            'tags': ['math']
        }
        
        converted = self.converter.convert_question(mc_question, 'true_false')
        self.assertEqual(converted['question_type'], 'true_false')
        self.assertIn('Statement:', converted['question_text'])
        self.assertEqual(len(converted['answers']), 2)
        self.assertEqual(converted['answers'][0]['text'], 'True')
        self.assertEqual(converted['answers'][1]['text'], 'False')
        
        # Test multiple choice to select all conversion
        converted = self.converter.convert_question(mc_question, 'select_all')
        self.assertEqual(converted['question_type'], 'select_all')
        self.assertIn('(Select all that apply)', converted['question_text'])
        self.assertEqual(len(converted['answers']), 2)
    
    def test_conversion_validation(self):
        """Test conversion validation."""
        # Valid conversion
        question = {
            'question_type': 'multiple_choice',
            'answers': [
                {'text': 'A', 'is_correct': True},
                {'text': 'B', 'is_correct': False}
            ]
        }
        
        result = self.converter.validate_conversion(question, 'true_false')
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        
        # Invalid conversion - wrong number of answers
        invalid_question = {
            'question_type': 'multiple_choice',
            'answers': [
                {'text': 'A', 'is_correct': True},
                {'text': 'B', 'is_correct': False},
                {'text': 'C', 'is_correct': False}
            ]
        }
        
        result = self.converter.validate_conversion(invalid_question, 'true_false')
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_conversion_preview(self):
        """Test conversion preview functionality."""
        question = {
            'question_text': 'What is 2+2?',
            'question_type': 'multiple_choice',
            'answers': [
                {'text': '4', 'is_correct': True},
                {'text': '3', 'is_correct': False}
            ],
            'tags': ['math']
        }
        
        preview = self.converter.get_conversion_preview(question, 'true_false')
        self.assertTrue(preview['can_convert'])
        self.assertIsNotNone(preview['preview'])
        self.assertEqual(preview['preview']['question_type'], 'true_false')
    
    def test_scoring_information(self):
        """Test scoring information retrieval."""
        # Test multiple choice scoring info
        info = self.scorer.get_scoring_info('multiple_choice')
        self.assertEqual(info['max_points'], 1)
        self.assertEqual(info['scoring_type'], 'binary')
        self.assertFalse(info['partial_credit'])
        
        # Test select all scoring info
        info = self.scorer.get_scoring_info('select_all')
        self.assertEqual(info['max_points'], 1)
        self.assertEqual(info['scoring_type'], 'partial')
        self.assertTrue(info['partial_credit'])
        
        # Test unknown type
        info = self.scorer.get_scoring_info('unknown_type')
        self.assertEqual(info['scoring_type'], 'unknown')
    
    def test_quiz_score_calculation(self):
        """Test overall quiz score calculation."""
        question_results = [
            {'points_earned': 1, 'max_points': 1, 'is_correct': True},
            {'points_earned': 0.5, 'max_points': 1, 'is_correct': False},
            {'points_earned': 1, 'max_points': 1, 'is_correct': True},
            {'points_earned': 0, 'max_points': 1, 'is_correct': False}
        ]
        
        quiz_score = self.scorer.calculate_quiz_score(question_results)
        
        self.assertEqual(quiz_score['total_points'], 2.5)
        self.assertEqual(quiz_score['max_points'], 4)
        self.assertEqual(quiz_score['percentage'], 62.5)
        self.assertEqual(quiz_score['correct_count'], 2)
        self.assertEqual(quiz_score['total_questions'], 4)
        self.assertEqual(quiz_score['average_per_question'], 0.625)
    
    def test_question_improvements(self):
        """Test question improvement suggestions."""
        # Test multiple choice suggestions
        answers = [
            {'text': 'A', 'is_correct': True},
            {'text': 'B', 'is_correct': False}
        ]
        
        suggestions = self.validator.suggest_question_improvements('multiple_choice', answers)
        self.assertIn('Consider adding more answer options', suggestions[0])
        
        # Test select all suggestions
        answers = [
            {'text': 'A', 'is_correct': True},
            {'text': 'B', 'is_correct': False},
            {'text': 'C', 'is_correct': False},
            {'text': 'D', 'is_correct': False}
        ]
        
        suggestions = self.validator.suggest_question_improvements('select_all', answers)
        self.assertIn('Consider if this should be a multiple choice question', suggestions[0])

if __name__ == '__main__':
    unittest.main(verbosity=2)
