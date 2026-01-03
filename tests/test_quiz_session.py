#!/usr/bin/env python3
"""
Test suite for QuizSession model

This module tests the QuizSession model for state management,
answer tracking, and progress calculation.
"""

import sys
import os
import unittest
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.quiz_session import QuizSession
from models.question import Question
from models.tag import Tag
from models.factories import ModelFactory

class TestQuizSessionModel(unittest.TestCase):
    """Test cases for QuizSession model."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_questions = [
            {
                "id": "q1",
                "question_text": "What is the capital of France?",
                "question_type": "multiple_choice",
                "answers": [
                    {"id": "a1", "text": "Paris", "is_correct": True},
                    {"id": "a2", "text": "London", "is_correct": False}
                ],
                "tags": ["geography"]
            },
            {
                "id": "q2",
                "question_text": "What is 2 + 2?",
                "question_type": "multiple_choice",
                "answers": [
                    {"id": "a3", "text": "3", "is_correct": False},
                    {"id": "a4", "text": "4", "is_correct": True}
                ],
                "tags": ["math"]
            }
        ]
    
    def test_create_valid_quiz_session(self):
        """Test creating a valid quiz session."""
        session = QuizSession(questions=self.sample_questions)
        
        self.assertEqual(len(session.questions), 2)
        self.assertEqual(session.current_question_index, 0)
        self.assertEqual(len(session.answers), 0)
        self.assertEqual(session.score, 0.0)
        self.assertFalse(session.is_complete)
        self.assertIsNotNone(session.start_time)
        self.assertIsNone(session.end_time)
        self.assertTrue(session.validate()['is_valid'])
    
    def test_quiz_session_validation_empty_questions(self):
        """Test quiz session validation with empty questions."""
        with self.assertRaises(ValueError):
            QuizSession(questions=[])
    
    def test_quiz_session_validation_too_many_questions(self):
        """Test quiz session validation with too many questions."""
        many_questions = [{"id": f"q{i}", "question_text": f"Question {i}", 
                          "question_type": "multiple_choice", "answers": []} 
                         for i in range(101)]
        
        with self.assertRaises(ValueError):
            QuizSession(questions=many_questions)
    
    def test_add_answer(self):
        """Test adding answers to quiz session."""
        session = QuizSession(questions=self.sample_questions)
        
        # Add first answer
        session.add_answer("q1", "a1", True)
        
        self.assertEqual(len(session.answers), 1)
        self.assertEqual(session.current_question_index, 1)
        self.assertFalse(session.is_complete)
        
        # Add second answer
        session.add_answer("q2", "a4", True)
        
        self.assertEqual(len(session.answers), 2)
        self.assertEqual(session.current_question_index, 2)
        self.assertTrue(session.is_complete)
        self.assertIsNotNone(session.end_time)
    
    def test_calculate_score(self):
        """Test score calculation."""
        session = QuizSession(questions=self.sample_questions)
        
        # Add correct answers
        session.add_answer("q1", "a1", True)
        session.add_answer("q2", "a4", True)
        
        score = session.calculate_score()
        self.assertEqual(score, 100.0)
        self.assertEqual(session.score, 100.0)
    
    def test_calculate_score_partial(self):
        """Test partial score calculation."""
        session = QuizSession(questions=self.sample_questions)
        
        # Add one correct, one incorrect
        session.add_answer("q1", "a1", True)
        session.add_answer("q2", "a3", False)
        
        score = session.calculate_score()
        self.assertEqual(score, 50.0)
        self.assertEqual(session.score, 50.0)
    
    def test_get_progress(self):
        """Test progress tracking."""
        session = QuizSession(questions=self.sample_questions)
        
        # Initial progress
        progress = session.get_progress()
        self.assertEqual(progress['current_question'], 1)
        self.assertEqual(progress['total_questions'], 2)
        self.assertEqual(progress['answered_questions'], 0)
        self.assertEqual(progress['remaining_questions'], 2)
        self.assertEqual(progress['progress_percentage'], 0.0)
        self.assertFalse(progress['is_complete'])
        
        # After one answer
        session.add_answer("q1", "a1", True)
        progress = session.get_progress()
        self.assertEqual(progress['current_question'], 2)
        self.assertEqual(progress['answered_questions'], 1)
        self.assertEqual(progress['remaining_questions'], 1)
        self.assertEqual(progress['progress_percentage'], 50.0)
        self.assertFalse(progress['is_complete'])
        
        # After completion
        session.add_answer("q2", "a4", True)
        progress = session.get_progress()
        self.assertEqual(progress['answered_questions'], 2)
        self.assertEqual(progress['remaining_questions'], 0)
        self.assertEqual(progress['progress_percentage'], 100.0)
        self.assertTrue(progress['is_complete'])
    
    def test_get_current_question(self):
        """Test getting current question."""
        session = QuizSession(questions=self.sample_questions)
        
        # First question
        current = session.get_current_question()
        self.assertEqual(current['id'], "q1")
        
        # After answering first question
        session.add_answer("q1", "a1", True)
        current = session.get_current_question()
        self.assertEqual(current['id'], "q2")
        
        # After completion
        session.add_answer("q2", "a4", True)
        current = session.get_current_question()
        self.assertIsNone(current)
    
    def test_get_duration(self):
        """Test duration calculation."""
        session = QuizSession(questions=self.sample_questions)
        
        # Should have some duration even immediately
        duration = session.get_duration()
        self.assertIsNotNone(duration)
        self.assertGreaterEqual(duration, 0)
        
        # Complete the session
        session.add_answer("q1", "a1", True)
        session.add_answer("q2", "a4", True)
        
        duration = session.get_duration()
        self.assertIsNotNone(duration)
        self.assertGreater(duration, 0)
    
    def test_get_statistics(self):
        """Test getting session statistics."""
        session = QuizSession(questions=self.sample_questions)
        
        # Add answers
        session.add_answer("q1", "a1", True)
        session.add_answer("q2", "a3", False)
        
        stats = session.get_statistics()
        
        self.assertEqual(stats['session_id'], session.id)
        self.assertEqual(stats['total_questions'], 2)
        self.assertEqual(stats['answered_questions'], 2)
        self.assertEqual(stats['correct_answers'], 1)
        self.assertEqual(stats['incorrect_answers'], 1)
        self.assertEqual(stats['score_percentage'], 50.0)
        self.assertIsNotNone(stats['duration_seconds'])
        self.assertIsNotNone(stats['start_time'])
        self.assertIsNotNone(stats['end_time'])
        self.assertTrue(stats['is_complete'])
    
    def test_serialization(self):
        """Test serialization to/from dictionary."""
        session = QuizSession(questions=self.sample_questions)
        session.add_answer("q1", "a1", True)
        
        # Test to_dict
        session_dict = session.to_dict()
        self.assertIsInstance(session_dict, dict)
        self.assertEqual(session_dict['id'], session.id)
        self.assertEqual(len(session_dict['questions']), 2)
        self.assertEqual(len(session_dict['answers']), 1)
        
        # Test from_dict
        new_session = QuizSession.from_dict(session_dict)
        self.assertEqual(new_session.id, session.id)
        self.assertEqual(len(new_session.questions), 2)
        self.assertEqual(len(new_session.answers), 1)
        self.assertEqual(new_session.current_question_index, 1)
    
    def test_equality(self):
        """Test equality comparison."""
        session1 = QuizSession(questions=self.sample_questions)
        session2 = QuizSession(questions=self.sample_questions)
        
        # Different IDs should not be equal
        self.assertNotEqual(session1, session2)
        
        # Same data should be equal
        session1_dict = session1.to_dict()
        session1_restored = QuizSession.from_dict(session1_dict)
        self.assertEqual(session1, session1_restored)

class TestModelFactory(unittest.TestCase):
    """Test cases for ModelFactory."""
    
    def test_create_question(self):
        """Test creating a question with factory."""
        question = ModelFactory.create_question()
        
        self.assertIsInstance(question, Question)
        self.assertTrue(question.validate()['is_valid'])
        self.assertIn(question.question_type, ["multiple_choice", "true_false", "select_all"])
        self.assertGreater(len(question.answers), 0)
        self.assertGreater(len(question.tags), 0)
    
    def test_create_tag(self):
        """Test creating a tag with factory."""
        tag = ModelFactory.create_tag()
        
        self.assertIsInstance(tag, Tag)
        self.assertTrue(tag.validate()['is_valid'])
        self.assertIsNotNone(tag.name)
        self.assertIsNotNone(tag.description)
    
    def test_create_quiz_session(self):
        """Test creating a quiz session with factory."""
        session = ModelFactory.create_quiz_session(num_questions=3)
        
        self.assertIsInstance(session, QuizSession)
        self.assertEqual(len(session.questions), 3)
        self.assertTrue(session.validate()['is_valid'])
    
    def test_create_question_bank(self):
        """Test creating a question bank."""
        questions = ModelFactory.create_question_bank(num_questions=5)
        
        self.assertEqual(len(questions), 5)
        for question in questions:
            self.assertIsInstance(question, Question)
            self.assertTrue(question.validate()['is_valid'])
    
    def test_create_tag_collection(self):
        """Test creating a tag collection."""
        tags = ModelFactory.create_tag_collection(num_tags=5)
        
        self.assertEqual(len(tags), 5)
        tag_names = [tag.name for tag in tags]
        self.assertEqual(len(set(tag_names)), 5)  # All unique names
        
        for tag in tags:
            self.assertIsInstance(tag, Tag)
            self.assertTrue(tag.validate()['is_valid'])
    
    def test_create_completed_quiz_session(self):
        """Test creating a completed quiz session."""
        session = ModelFactory.create_completed_quiz_session(
            num_questions=4, 
            score_percentage=75.0
        )
        
        self.assertIsInstance(session, QuizSession)
        self.assertTrue(session.is_complete)
        self.assertEqual(len(session.answers), 4)
        self.assertEqual(session.score, 75.0)

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
