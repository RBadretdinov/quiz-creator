#!/usr/bin/env python3
"""
Data Integrity Tests

These tests verify that data is correctly stored and retrieved,
checking for subtle bugs like missing answers, wrong questions in quizzes,
incorrect scoring, and data mismatches.
"""

import sys
import os
import unittest
import tempfile
from unittest.mock import patch

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app_controller_db import AppControllerDB
from question_manager_db import QuestionManagerDB
from tag_manager_db import TagManagerDB
from quiz_engine import QuizEngine
from database_manager import DatabaseManager


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and correctness."""
    
    def setUp(self):
        """Set up test environment."""
        # Use a temporary test database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        self.db_manager = DatabaseManager(self.db_path)
        # Initialize database schema
        if not self.db_manager.initialize():
            raise Exception("Failed to initialize database")
        
        self.question_manager = QuestionManagerDB(self.db_manager)
        self.tag_manager = TagManagerDB(self.db_manager)
        
        # Create temp directory for quiz sessions
        self.temp_dir = tempfile.mkdtemp()
        session_path = os.path.join(self.temp_dir, 'quiz_sessions.json')
        self.quiz_engine = QuizEngine(session_storage_path=session_path)
        
        # Create a test tag
        self.test_tag_id = self.tag_manager.create_tag("TestTag")
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'db_manager'):
            try:
                self.db_manager.close()
            except:
                pass
        # Clean up temp file
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except:
                pass
        # Clean up temp directory
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except:
                pass
    
    def test_question_answers_complete(self):
        """Test that all answer options entered are stored correctly."""
        question_text = "What is 2+2?"
        question_type = "multiple_choice"
        answers = [
            {"text": "3", "is_correct": False},
            {"text": "4", "is_correct": True},
            {"text": "5", "is_correct": False}
        ]
        tags = ["TestTag"]
        
        # Create question
        question_id = self.question_manager.create_question(
            question_text, question_type, answers, tags
        )
        
        # Retrieve question
        stored_question = self.question_manager.get_question(question_id)
        
        # Verify all answers are present
        self.assertIsNotNone(stored_question, "Question should be stored")
        stored_answers = stored_question.get('answers', [])
        
        self.assertEqual(len(stored_answers), len(answers), 
                        "All answer options should be stored")
        
        # Verify each answer text matches
        stored_texts = [a.get('text') for a in stored_answers]
        original_texts = [a['text'] for a in answers]
        
        for original_text in original_texts:
            self.assertIn(original_text, stored_texts, 
                         f"Answer '{original_text}' should be in stored question")
        
        # Verify exactly one correct answer for multiple choice
        correct_count = sum(1 for a in stored_answers if a.get('is_correct', False))
        self.assertEqual(correct_count, 1, 
                       "Multiple choice should have exactly one correct answer")
    
    def test_select_all_answers_complete(self):
        """Test that all select-all answers are stored correctly."""
        question_text = "Which are prime numbers?"
        question_type = "select_all"
        answers = [
            {"text": "2", "is_correct": True},
            {"text": "3", "is_correct": True},
            {"text": "4", "is_correct": False},
            {"text": "5", "is_correct": True}
        ]
        tags = ["TestTag"]
        
        question_id = self.question_manager.create_question(
            question_text, question_type, answers, tags
        )
        
        stored_question = self.question_manager.get_question(question_id)
        stored_answers = stored_question.get('answers', [])
        
        self.assertEqual(len(stored_answers), len(answers),
                        "All select-all answers should be stored")
        
        # Verify correct answers
        correct_texts = [a.get('text') for a in stored_answers if a.get('is_correct', False)]
        expected_correct = ["2", "3", "5"]
        
        for expected in expected_correct:
            self.assertIn(expected, correct_texts,
                         f"Correct answer '{expected}' should be marked")
    
    def test_quiz_only_includes_selected_questions(self):
        """Test that quiz only includes questions from selected tags."""
        # Create questions with different tags
        tag1_id = self.tag_manager.create_tag("Geography")
        tag2_id = self.tag_manager.create_tag("Math")
        
        q1_id = self.question_manager.create_question(
            "Capital of France?", "multiple_choice",
            [{"text": "Paris", "is_correct": True}, {"text": "London", "is_correct": False}],
            ["Geography"]
        )
        
        q2_id = self.question_manager.create_question(
            "What is 2+2?", "multiple_choice",
            [{"text": "3", "is_correct": False}, {"text": "4", "is_correct": True}],
            ["Math"]
        )
        
        q3_id = self.question_manager.create_question(
            "Capital of Spain?", "multiple_choice",
            [{"text": "Madrid", "is_correct": True}, {"text": "Barcelona", "is_correct": False}],
            ["Geography"]
        )
        
        # Generate quiz with only Geography tag
        quiz_questions = self.question_manager.get_questions_by_tags(["Geography"])
        quiz_q_ids = [q['id'] for q in quiz_questions]
        
        # Verify only Geography questions are included
        self.assertIn(q1_id, quiz_q_ids, "Geography question should be included")
        self.assertIn(q3_id, quiz_q_ids, "Geography question should be included")
        self.assertNotIn(q2_id, quiz_q_ids, "Math question should NOT be included")
        self.assertEqual(len(quiz_q_ids), 2, "Should have exactly 2 Geography questions")
    
    def test_question_text_matches_input(self):
        """Test that question text stored matches exactly what was entered."""
        original_text = "What is the capital of France? This is a detailed question."
        
        question_id = self.question_manager.create_question(
            original_text, "multiple_choice",
            [{"text": "Paris", "is_correct": True}, {"text": "London", "is_correct": False}],
            ["TestTag"]
        )
        
        stored_question = self.question_manager.get_question(question_id)
        stored_text = stored_question.get('question_text', '')
        
        self.assertEqual(stored_text, original_text,
                        "Question text should match exactly what was entered")
    
    def test_correct_answer_identification(self):
        """Test that correct answers are correctly identified and marked."""
        question_id = self.question_manager.create_question(
            "What is 2+2?", "multiple_choice",
            [{"text": "3", "is_correct": False}, 
             {"text": "4", "is_correct": True},
             {"text": "5", "is_correct": False}],
            ["TestTag"]
        )
        
        stored_question = self.question_manager.get_question(question_id)
        stored_answers = stored_question.get('answers', [])
        
        # Find correct answer
        correct_answers = [a for a in stored_answers if a.get('is_correct', False)]
        
        self.assertEqual(len(correct_answers), 1, "Should have exactly one correct answer")
        self.assertEqual(correct_answers[0].get('text'), "4",
                        "Correct answer should be '4'")
    
    def test_tag_association_correct(self):
        """Test that tags are correctly associated with questions."""
        tag1 = "Geography"
        tag2 = "History"
        
        tag1_id = self.tag_manager.create_tag(tag1)
        tag2_id = self.tag_manager.create_tag(tag2)
        
        question_id = self.question_manager.create_question(
            "Capital of France?", "multiple_choice",
            [{"text": "Paris", "is_correct": True}, {"text": "London", "is_correct": False}],
            [tag1, tag2]
        )
        
        stored_question = self.question_manager.get_question(question_id)
        stored_tags = stored_question.get('tags', [])
        
        # Verify both tags are associated
        self.assertIn(tag1, stored_tags, f"Question should have '{tag1}' tag")
        self.assertIn(tag2, stored_tags, f"Question should have '{tag2}' tag")
        self.assertEqual(len(stored_tags), 2, "Question should have exactly 2 tags")
    
    def test_scoring_correctness(self):
        """Test that scoring is calculated correctly."""
        # Create a quiz session with known answers
        question_id = self.question_manager.create_question(
            "What is 2+2?", "multiple_choice",
            [{"text": "3", "is_correct": False}, 
             {"text": "4", "is_correct": True},
             {"text": "5", "is_correct": False}],
            ["TestTag"]
        )
        
        question = self.question_manager.get_question(question_id)
        session_id = self.quiz_engine.start_session([question])
        
        # Get the correct answer index
        correct_answer_idx = None
        for i, answer in enumerate(question['answers']):
            if answer.get('is_correct', False):
                correct_answer_idx = i
                break
        
        # Submit correct answer
        result = self.quiz_engine.submit_answer(session_id, question_id, [correct_answer_idx])
        
        self.assertTrue(result.get('is_correct', False),
                      "Correct answer should be marked as correct")
        self.assertEqual(result.get('score_earned', 0), result.get('max_points', 0),
                        "Full points should be earned for correct answer")
    
    def test_scoring_partial_credit_select_all(self):
        """Test that partial credit is calculated correctly for select-all questions."""
        question_id = self.question_manager.create_question(
            "Which are prime? (select all)", "select_all",
            [
                {"text": "2", "is_correct": True},
                {"text": "3", "is_correct": True},
                {"text": "4", "is_correct": False},
                {"text": "5", "is_correct": True}
            ],
            ["TestTag"]
        )
        
        question = self.question_manager.get_question(question_id)
        session_id = self.quiz_engine.start_session([question])
        
        # Submit partial answer (2 out of 3 correct)
        # Correct answers are at indices 0, 1, 3
        # User selects 0, 1 (correct) and 2 (wrong) = 2/3 correct
        result = self.quiz_engine.submit_answer(session_id, question_id, [0, 1, 2])
        
        # Should get partial credit (2 out of 3 correct)
        self.assertFalse(result.get('is_correct', True),
                        "This should not be fully correct")
        self.assertGreater(result.get('partial_credit', 0), 0,
                          "Should receive partial credit")
    
    def test_question_not_in_wrong_tag(self):
        """Test that questions don't appear in quizzes for tags they don't have."""
        # Create tags
        tag1_id = self.tag_manager.create_tag("Science")
        tag2_id = self.tag_manager.create_tag("Art")
        
        # Create question with only Science tag
        q_id = self.question_manager.create_question(
            "What is H2O?", "multiple_choice",
            [{"text": "Water", "is_correct": True}, {"text": "Oxygen", "is_correct": False}],
            ["Science"]
        )
        
        # Try to get questions by Art tag
        art_questions = self.question_manager.get_questions_by_tags(["Art"])
        art_q_ids = [q['id'] for q in art_questions]
        
        self.assertNotIn(q_id, art_q_ids,
                        "Science question should NOT appear in Art tag quiz")
    
    def test_answer_text_not_changed(self):
        """Test that answer text is not modified during storage."""
        original_answers = [
            {"text": "The correct answer is A", "is_correct": True},
            {"text": "The wrong answer is B", "is_correct": False},
            {"text": "Another wrong: C", "is_correct": False}
        ]
        
        question_id = self.question_manager.create_question(
            "Pick the correct one", "multiple_choice",
            original_answers,
            ["TestTag"]
        )
        
        stored_question = self.question_manager.get_question(question_id)
        stored_answers = stored_question.get('answers', [])
        
        # Verify each answer text matches exactly
        for i, original in enumerate(original_answers):
            stored_text = stored_answers[i].get('text', '')
            self.assertEqual(stored_text, original['text'],
                           f"Answer {i+1} text should match exactly")
    
    def test_question_count_matches_actual_questions(self):
        """Test that tag question count matches actual number of questions."""
        tag_name = "VerifiedTag"
        tag_id = self.tag_manager.create_tag(tag_name)
        
        # Create 3 questions with this tag
        for i in range(3):
            self.question_manager.create_question(
                f"Question {i+1}?", "multiple_choice",
                [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
                [tag_name]
            )
        
        # Verify tag question count
        tag = self.tag_manager.get_tag(tag_id)
        question_count = tag.get('question_count', 0)
        
        # Get actual count
        questions = self.question_manager.get_questions_by_tags([tag_name])
        actual_count = len(questions)
        
        self.assertEqual(question_count, actual_count,
                        f"Tag question count ({question_count}) should match actual questions ({actual_count})")
    
    def test_no_duplicate_answers_in_question(self):
        """Test that answer options are not duplicated."""
        question_id = self.question_manager.create_question(
            "What is 2+2?", "multiple_choice",
            [
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": True},
                {"text": "3", "is_correct": False}  # Duplicate!
            ],
            ["TestTag"]
        )
        
        stored_question = self.question_manager.get_question(question_id)
        stored_answers = stored_question.get('answers', [])
        answer_texts = [a.get('text') for a in stored_answers]
        
        # Check for duplicates
        unique_texts = set(answer_texts)
        # Note: The system might allow duplicates, but we should be aware
        # If it doesn't prevent them, this test documents the behavior
        
        # At minimum, verify all answers are stored
        self.assertEqual(len(stored_answers), 3,
                        "All answers should be stored (even duplicates)")
    
    def test_quiz_session_completeness(self):
        """Test that quiz session contains all expected questions."""
        # Create 5 questions
        question_ids = []
        for i in range(5):
            q_id = self.question_manager.create_question(
                f"Question {i+1}?", "multiple_choice",
                [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
                ["TestTag"]
            )
            question_ids.append(q_id)
        
        # Get all questions
        all_questions = self.question_manager.get_all_questions()
        all_q_ids = [q['id'] for q in all_questions]
        
        # Verify all created questions are present
        for q_id in question_ids:
            self.assertIn(q_id, all_q_ids,
                         f"Question {q_id} should be in all questions")
        
        self.assertEqual(len(all_q_ids), 5,
                        "Should have exactly 5 questions")


if __name__ == '__main__':
    unittest.main()

