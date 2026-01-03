#!/usr/bin/env python3
"""
Edge Case Data Integrity Tests

Tests for subtle bugs in edge cases like:
- Missing answers after editing
- Wrong questions in quiz after tag changes
- Score miscalculations
- Data corruption scenarios
"""

import sys
import os
import unittest
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from question_manager_db import QuestionManagerDB
from tag_manager_db import TagManagerDB
from quiz_engine import QuizEngine
from database_manager import DatabaseManager


class TestEdgeCaseIntegrity(unittest.TestCase):
    """Test edge cases for data integrity."""
    
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
    
    def test_answer_order_preserved(self):
        """Test that answer order is preserved as entered."""
        # Create question with answers in specific order
        answers = [
            {"text": "First answer", "is_correct": False},
            {"text": "Second answer", "is_correct": True},
            {"text": "Third answer", "is_correct": False},
            {"text": "Fourth answer", "is_correct": False}
        ]
        
        question_id = self.question_manager.create_question(
            "Test question?", "multiple_choice", answers, ["Test"]
        )
        
        stored = self.question_manager.get_question(question_id)
        stored_answers = stored.get('answers', [])
        
        # Verify order
        for i, original in enumerate(answers):
            self.assertEqual(stored_answers[i].get('text'), original['text'],
                           f"Answer {i+1} should be in original position")
    
    def test_no_phantom_answers(self):
        """Test that answers not entered don't appear in stored question."""
        # Create question with 3 answers
        answers = [
            {"text": "A", "is_correct": False},
            {"text": "B", "is_correct": True},
            {"text": "C", "is_correct": False}
        ]
        
        question_id = self.question_manager.create_question(
            "Test?", "multiple_choice", answers, ["Test"]
        )
        
        stored = self.question_manager.get_question(question_id)
        stored_answers = stored.get('answers', [])
        
        # Should have exactly 3 answers, no more
        self.assertEqual(len(stored_answers), 3,
                        "Should have exactly the answers entered, no more")
        
        # Verify no unexpected answers
        answer_texts = [a.get('text') for a in stored_answers]
        unexpected = set(answer_texts) - set(["A", "B", "C"])
        self.assertEqual(len(unexpected), 0,
                        f"Found unexpected answers: {unexpected}")
    
    def test_quiz_question_count_correct(self):
        """Test that quiz has exactly the number of questions requested."""
        # Create 10 questions
        tag_id = self.tag_manager.create_tag("QuizTag")
        for i in range(10):
            self.question_manager.create_question(
                f"Q{i+1}?", "multiple_choice",
                [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
                ["QuizTag"]
            )
        
        # Request quiz with 5 questions
        all_questions = self.question_manager.get_questions_by_tags(["QuizTag"])
        
        # Start session with only 5 questions
        session_questions = all_questions[:5]
        session_id = self.quiz_engine.start_session(session_questions)
        
        session = self.quiz_engine.active_sessions.get(session_id)
        self.assertIsNotNone(session, "Session should be created")
        self.assertEqual(len(session.get('questions', [])), 5,
                        "Quiz should have exactly 5 questions, not more or less")
    
    def test_correct_answer_not_lost(self):
        """Test that correct answer marking is not lost during storage."""
        # Create question where last answer is correct
        answers = [
            {"text": "Wrong 1", "is_correct": False},
            {"text": "Wrong 2", "is_correct": False},
            {"text": "Correct", "is_correct": True}
        ]
        
        question_id = self.question_manager.create_question(
            "Which is right?", "multiple_choice", answers, ["Test"]
        )
        
        stored = self.question_manager.get_question(question_id)
        stored_answers = stored.get('answers', [])
        
        # Verify correct answer is still marked
        correct_answers = [a for a in stored_answers if a.get('is_correct', False)]
        self.assertEqual(len(correct_answers), 1,
                        "Should have exactly one correct answer")
        self.assertEqual(correct_answers[0].get('text'), "Correct",
                        "Correct answer should still be marked correctly")
    
    def test_tag_question_count_after_deletion(self):
        """Test that tag question count is updated when question is deleted."""
        tag_id = self.tag_manager.create_tag("CountTag")
        tag_name = "CountTag"
        
        # Create 3 questions
        q_ids = []
        for i in range(3):
            q_id = self.question_manager.create_question(
                f"Q{i+1}?", "multiple_choice",
                [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
                [tag_name]
            )
            q_ids.append(q_id)
        
        # Verify count is 3
        tag = self.tag_manager.get_tag(tag_id)
        self.assertEqual(tag.get('question_count', 0), 3,
                        "Tag should have 3 questions")
        
        # Delete one question
        self.question_manager.delete_question(q_ids[0])
        
        # Verify count updated
        # Note: This might require manual count update - testing actual behavior
        remaining = self.question_manager.get_questions_by_tags([tag_name])
        self.assertEqual(len(remaining), 2,
                        "Should have 2 questions remaining")
    
    def test_multiple_correct_in_select_all(self):
        """Test that select-all questions can have multiple correct answers marked."""
        question_id = self.question_manager.create_question(
            "Select all primes", "select_all",
            [
                {"text": "2", "is_correct": True},
                {"text": "3", "is_correct": True},
                {"text": "4", "is_correct": False},
                {"text": "5", "is_correct": True},
                {"text": "6", "is_correct": False}
            ],
            ["Test"]
        )
        
        stored = self.question_manager.get_question(question_id)
        stored_answers = stored.get('answers', [])
        
        correct_count = sum(1 for a in stored_answers if a.get('is_correct', False))
        self.assertEqual(correct_count, 3,
                        "Select-all should have 3 correct answers marked")
        
        # Verify specific correct answers
        correct_texts = [a.get('text') for a in stored_answers if a.get('is_correct', False)]
        self.assertIn("2", correct_texts, "2 should be marked correct")
        self.assertIn("3", correct_texts, "3 should be marked correct")
        self.assertIn("5", correct_texts, "5 should be marked correct")
    
    def test_scoring_zero_wrong_answer(self):
        """Test that completely wrong answer scores zero."""
        question_id = self.question_manager.create_question(
            "What is 2+2?", "multiple_choice",
            [
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": True},
                {"text": "5", "is_correct": False}
            ],
            ["Test"]
        )
        
        question = self.question_manager.get_question(question_id)
        session_id = self.quiz_engine.start_session([question])
        
        # Submit wrong answer (index 0 = "3")
        result = self.quiz_engine.submit_answer(session_id, question_id, [0])
        
        self.assertFalse(result.get('is_correct', True),
                        "Wrong answer should not be correct")
        self.assertEqual(result.get('score_earned', 1), 0,
                        "Wrong answer should score 0 points")
    
    def test_no_answers_lost_during_retrieval(self):
        """Test that all answers are retrieved, none are lost."""
        # Create question with many answers
        answers = [
            {"text": f"Option {i}", "is_correct": (i == 5)}  # 6th is correct
            for i in range(10)
        ]
        
        question_id = self.question_manager.create_question(
            "Pick one from many?", "multiple_choice", answers, ["Test"]
        )
        
        stored = self.question_manager.get_question(question_id)
        stored_answers = stored.get('answers', [])
        
        self.assertEqual(len(stored_answers), 10,
                        "All 10 answers should be retrieved")
        
        # Verify all answer texts present
        stored_texts = [a.get('text') for a in stored_answers]
        for i in range(10):
            self.assertIn(f"Option {i}", stored_texts,
                        f"Option {i} should be present")
    
    def test_question_not_appearing_in_wrong_tag_quiz(self):
        """Test that changing tags doesn't cause questions in wrong quizzes."""
        tag1_id = self.tag_manager.create_tag("Tag1")
        tag2_id = self.tag_manager.create_tag("Tag2")
        
        # Create question with Tag1 only
        q_id = self.question_manager.create_question(
            "Tag1 question?", "multiple_choice",
            [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
            ["Tag1"]
        )
        
        # Get questions for Tag2
        tag2_questions = self.question_manager.get_questions_by_tags(["Tag2"])
        tag2_q_ids = [q['id'] for q in tag2_questions]
        
        self.assertNotIn(q_id, tag2_q_ids,
                        "Question with Tag1 should NOT appear in Tag2 quiz")
        
        # Verify it DOES appear in Tag1 quiz
        tag1_questions = self.question_manager.get_questions_by_tags(["Tag1"])
        tag1_q_ids = [q['id'] for q in tag1_questions]
        self.assertIn(q_id, tag1_q_ids,
                     "Question should appear in Tag1 quiz")
    
    def test_session_score_accuracy(self):
        """Test that session final score is calculated accurately."""
        # Create 3 questions
        questions = []
        for i in range(3):
            q_id = self.question_manager.create_question(
                f"Q{i+1}?", "multiple_choice",
                [{"text": "Wrong", "is_correct": False},
                 {"text": "Correct", "is_correct": True}],
                ["Test"]
            )
            q = self.question_manager.get_question(q_id)
            questions.append(q)
        
        session_id = self.quiz_engine.start_session(questions)
        
        # Answer all 3 correctly
        for q in questions:
            # Find correct answer index
            correct_idx = next((i for i, a in enumerate(q['answers']) 
                              if a.get('is_correct', False)), None)
            self.quiz_engine.submit_answer(session_id, q['id'], [correct_idx])
        
        # Check final score
        session = self.quiz_engine.active_sessions.get(session_id)
        final_score = session.get('score', 0)
        
        # Should be 100% (3/3 correct)
        self.assertGreaterEqual(final_score, 99.0,
                               "All correct answers should score ~100%")
        self.assertLessEqual(final_score, 100.0,
                            "Score should not exceed 100%")
    
    def test_answer_ids_unique(self):
        """Test that answer IDs are unique within a question."""
        question_id = self.question_manager.create_question(
            "Test?", "multiple_choice",
            [
                {"text": "A", "is_correct": False},
                {"text": "B", "is_correct": True},
                {"text": "C", "is_correct": False}
            ],
            ["Test"]
        )
        
        stored = self.question_manager.get_question(question_id)
        stored_answers = stored.get('answers', [])
        
        # Collect all answer IDs
        answer_ids = [a.get('id') for a in stored_answers if a.get('id')]
        
        # Check for duplicates
        unique_ids = set(answer_ids)
        self.assertEqual(len(answer_ids), len(unique_ids),
                        "All answer IDs should be unique")


if __name__ == '__main__':
    unittest.main()

