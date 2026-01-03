#!/usr/bin/env python3
"""
Test suite for quiz engine

This module tests the QuizEngine class for randomization,
scoring, and session management.
"""

import sys
import os
import unittest
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from quiz_engine import QuizEngine

class TestQuizEngine(unittest.TestCase):
    """Test cases for QuizEngine."""
    
    def setUp(self):
        """Set up test data."""
        self.engine = QuizEngine()
        
        self.sample_questions = [
            {
                "id": "q1",
                "question_text": "What is the capital of France?",
                "question_type": "multiple_choice",
                "answers": [
                    {"id": "a1", "text": "Paris", "is_correct": True},
                    {"id": "a2", "text": "London", "is_correct": False},
                    {"id": "a3", "text": "Berlin", "is_correct": False}
                ],
                "tags": ["geography"]
            },
            {
                "id": "q2",
                "question_text": "What is 2 + 2?",
                "question_type": "multiple_choice",
                "answers": [
                    {"id": "a4", "text": "3", "is_correct": False},
                    {"id": "a5", "text": "4", "is_correct": True},
                    {"id": "a6", "text": "5", "is_correct": False}
                ],
                "tags": ["math"]
            },
            {
                "id": "q3",
                "question_text": "The sun rises in the east.",
                "question_type": "true_false",
                "answers": [
                    {"id": "a7", "text": "True", "is_correct": True},
                    {"id": "a8", "text": "False", "is_correct": False}
                ],
                "tags": ["science"]
            }
        ]
    
    def test_randomize_questions(self):
        """Test question randomization."""
        original_order = [q["id"] for q in self.sample_questions]
        randomized = self.engine.randomize_questions(self.sample_questions)
        randomized_order = [q["id"] for q in randomized]
        
        # Should have same number of questions
        self.assertEqual(len(randomized), len(self.sample_questions))
        
        # Should contain all original questions
        self.assertEqual(set(original_order), set(randomized_order))
        
        # Run multiple times to ensure randomization works
        different_orders = set()
        for _ in range(10):
            randomized = self.engine.randomize_questions(self.sample_questions)
            order = tuple(q["id"] for q in randomized)
            different_orders.add(order)
        
        # Should have different orders (very high probability)
        self.assertGreater(len(different_orders), 1)
    
    def test_randomize_answers(self):
        """Test answer randomization within a question."""
        question = self.sample_questions[0].copy()
        original_answers = [a["id"] for a in question["answers"]]
        
        randomized_question = self.engine.randomize_answers(question)
        randomized_answers = [a["id"] for a in randomized_question["answers"]]
        
        # Should have same number of answers
        self.assertEqual(len(randomized_answers), len(original_answers))
        
        # Should contain all original answers
        self.assertEqual(set(original_answers), set(randomized_answers))
        
        # Correct answer should still be marked correctly
        correct_answer = next(a for a in randomized_question["answers"] if a["is_correct"])
        self.assertTrue(correct_answer["is_correct"])
    
    def test_create_randomized_quiz(self):
        """Test creating a randomized quiz."""
        quiz = self.engine.create_randomized_quiz(self.sample_questions, 2)
        
        # Should have requested number of questions
        self.assertEqual(len(quiz), 2)
        
        # All questions should have randomized answers
        for question in quiz:
            self.assertIn("answers", question)
            self.assertGreater(len(question["answers"]), 0)
    
    def test_start_quiz(self):
        """Test starting a quiz session."""
        session_id = self.engine.start_quiz(self.sample_questions)
        
        # Should return a valid session ID
        self.assertIsNotNone(session_id)
        self.assertIsInstance(session_id, str)
        
        # Session should be in active sessions
        self.assertIn(session_id, self.engine.active_sessions)
        
        session = self.engine.active_sessions[session_id]
        self.assertEqual(session["current_question_index"], 0)
        self.assertEqual(len(session["answers"]), 0)
        self.assertFalse(session["is_complete"])
        self.assertIsNotNone(session["start_time"])
    
    def test_submit_correct_answer(self):
        """Test submitting a correct answer."""
        session_id = self.engine.start_quiz(self.sample_questions)
        question = self.sample_questions[0]
        
        # Submit correct answer
        result = self.engine.submit_answer(session_id, question["id"], "a1")
        
        self.assertTrue(result["is_correct"])
        self.assertIn("Correct! Well done!", result["feedback"])
        
        # Check session state
        session = self.engine.active_sessions[session_id]
        self.assertEqual(session["current_question_index"], 1)
        self.assertEqual(len(session["answers"]), 1)
        self.assertTrue(session["answers"][0]["is_correct"])
    
    def test_submit_incorrect_answer(self):
        """Test submitting an incorrect answer."""
        session_id = self.engine.start_quiz(self.sample_questions)
        question = self.sample_questions[0]
        
        # Submit incorrect answer
        result = self.engine.submit_answer(session_id, question["id"], "a2")
        
        self.assertFalse(result["is_correct"])
        self.assertIn("Incorrect", result["feedback"])
        self.assertIn("correct answer", result["feedback"])
    
    def test_calculate_score(self):
        """Test score calculation."""
        session_id = self.engine.start_quiz(self.sample_questions)
        
        # Answer first question correctly
        self.engine.submit_answer(session_id, "q1", "a1")
        
        # Answer second question incorrectly
        self.engine.submit_answer(session_id, "q2", "a4")
        
        # Answer third question correctly
        self.engine.submit_answer(session_id, "q3", "a7")
        
        session = self.engine.active_sessions[session_id]
        score_info = self.engine.calculate_score(session)
        
        # Should be 2/3 = 66.7%
        self.assertAlmostEqual(score_info['percentage'], 66.7, places=1)
    
    def test_quiz_completion(self):
        """Test quiz completion flow."""
        session_id = self.engine.start_quiz(self.sample_questions)
        
        # Answer all questions
        self.engine.submit_answer(session_id, "q1", "a1")
        self.engine.submit_answer(session_id, "q2", "a5")
        self.engine.submit_answer(session_id, "q3", "a7")
        
        session = self.engine.active_sessions[session_id]
        
        # Quiz should be complete
        self.assertTrue(session["is_complete"])
        self.assertIsNotNone(session["end_time"])
        self.assertEqual(session["current_question_index"], 3)
        self.assertEqual(len(session["answers"]), 3)
        
        # Score should be calculated
        self.assertEqual(session["score"], 100.0)  # All correct
    
    def test_invalid_session_id(self):
        """Test handling of invalid session ID."""
        with self.assertRaises(ValueError):
            self.engine.submit_answer("invalid_session", "q1", "a1")
    
    def test_invalid_question_id(self):
        """Test handling of invalid question ID."""
        session_id = self.engine.start_quiz(self.sample_questions)
        
        with self.assertRaises(ValueError):
            self.engine.submit_answer(session_id, "invalid_question", "a1")

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
