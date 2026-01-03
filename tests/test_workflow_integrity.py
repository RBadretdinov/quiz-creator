#!/usr/bin/env python3
"""
Workflow Integrity Tests

Tests complete user workflows to catch bugs that only appear
when operations are combined or done in sequence.
"""

import sys
import os
import unittest
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app_controller_db import AppControllerDB
from question_manager_db import QuestionManagerDB
from tag_manager_db import TagManagerDB
from quiz_engine import QuizEngine
from database_manager import DatabaseManager


class TestWorkflowIntegrity(unittest.TestCase):
    """Test complete workflows for data integrity."""
    
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
        
        self.app = AppControllerDB()
        # Replace with test database
        self.app.db_manager = self.db_manager
        self.app.question_manager = self.question_manager
        self.app.tag_manager = self.tag_manager
        self.app.quiz_engine = self.quiz_engine
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'db_manager'):
            try:
                self.db_manager.close()
            except:
                pass
        if hasattr(self.app, 'db_manager'):
            try:
                self.app.db_manager.close()
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
    
    def test_create_take_quiz_workflow(self):
        """Test complete workflow: create question → take quiz → verify data."""
        # Step 1: Create question
        tag_name = "WorkflowTag"
        tag_id = self.tag_manager.create_tag(tag_name)
        
        question_id = self.question_manager.create_question(
            "What is 2+2?", "multiple_choice",
            [
                {"text": "3", "is_correct": False},
                {"text": "4", "is_correct": True},
                {"text": "5", "is_correct": False}
            ],
            [tag_name]
        )
        
        # Step 2: Verify question was created correctly
        stored = self.question_manager.get_question(question_id)
        self.assertIsNotNone(stored, "Question should exist")
        self.assertEqual(len(stored.get('answers', [])), 3,
                        "Question should have 3 answers")
        
        # Step 3: Start quiz session
        questions = self.question_manager.get_questions_by_tags([tag_name])
        self.assertEqual(len(questions), 1, "Should find 1 question")
        
        session_id = self.quiz_engine.start_session(questions)
        session = self.quiz_engine.active_sessions.get(session_id)
        
        # Step 4: Verify quiz session has correct question
        session_q_ids = [q['id'] for q in session.get('questions', [])]
        self.assertIn(question_id, session_q_ids,
                     "Quiz should include the created question")
        
        # Step 5: Answer the question correctly
        correct_idx = next((i for i, a in enumerate(stored['answers'])
                          if a.get('is_correct', False)), None)
        
        result = self.quiz_engine.submit_answer(session_id, question_id, [correct_idx])
        
        # Step 6: Verify answer was scored correctly
        self.assertTrue(result.get('is_correct', False),
                        "Correct answer should be marked correct")
    
    def test_tag_question_count_consistency(self):
        """Test that tag question counts stay consistent through workflow."""
        tag_name = "CountTest"
        tag_id = self.tag_manager.create_tag(tag_name)
        
        # Create 2 questions
        q1_id = self.question_manager.create_question(
            "Q1?", "multiple_choice",
            [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
            [tag_name]
        )
        
        q2_id = self.question_manager.create_question(
            "Q2?", "multiple_choice",
            [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
            [tag_name]
        )
        
        # Verify tag count matches actual questions
        tag = self.tag_manager.get_tag(tag_id)
        tag_count = tag.get('question_count', 0)
        
        actual_questions = self.question_manager.get_questions_by_tags([tag_name])
        actual_count = len(actual_questions)
        
        self.assertEqual(tag_count, actual_count,
                        f"Tag count ({tag_count}) should match actual ({actual_count})")
        
        # Both questions should be found
        q_ids = [q['id'] for q in actual_questions]
        self.assertIn(q1_id, q_ids, "Q1 should be found")
        self.assertIn(q2_id, q_ids, "Q2 should be found")
    
    def test_multiple_tags_question_appears_correctly(self):
        """Test question with multiple tags appears in correct quizzes."""
        tag1 = "Math"
        tag2 = "Easy"
        
        tag1_id = self.tag_manager.create_tag(tag1)
        tag2_id = self.tag_manager.create_tag(tag2)
        
        # Create question with both tags
        q_id = self.question_manager.create_question(
            "What is 2+2?", "multiple_choice",
            [{"text": "4", "is_correct": True}, {"text": "5", "is_correct": False}],
            [tag1, tag2]
        )
        
        # Should appear in Math quiz
        math_questions = self.question_manager.get_questions_by_tags([tag1])
        math_q_ids = [q['id'] for q in math_questions]
        self.assertIn(q_id, math_q_ids, "Should appear in Math quiz")
        
        # Should appear in Easy quiz
        easy_questions = self.question_manager.get_questions_by_tags([tag2])
        easy_q_ids = [q['id'] for q in easy_questions]
        self.assertIn(q_id, easy_q_ids, "Should appear in Easy quiz")
        
        # Should appear in both tags quiz
        both_questions = self.question_manager.get_questions_by_tags([tag1, tag2])
        both_q_ids = [q['id'] for q in both_questions]
        self.assertIn(q_id, both_q_ids, "Should appear in combined quiz")
    
    def test_quiz_doesnt_include_unselected_tags(self):
        """Test that quiz for one tag doesn't include questions from other tags."""
        tag1_id = self.tag_manager.create_tag("History")
        tag2_id = self.tag_manager.create_tag("Science")
        
        # Create History question
        h_q = self.question_manager.create_question(
            "History question?", "multiple_choice",
            [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
            ["History"]
        )
        
        # Create Science question
        s_q = self.question_manager.create_question(
            "Science question?", "multiple_choice",
            [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
            ["Science"]
        )
        
        # Get History quiz
        history_questions = self.question_manager.get_questions_by_tags(["History"])
        history_q_ids = [q['id'] for q in history_questions]
        
        # Verify Science question NOT in History quiz
        self.assertNotIn(s_q, history_q_ids,
                        "Science question should NOT be in History quiz")
        self.assertIn(h_q, history_q_ids,
                   "History question should be in History quiz")
    
    def test_answer_text_integrity_through_workflow(self):
        """Test that answer text doesn't change through create → quiz → score workflow."""
        original_answers = [
            {"text": "The first option", "is_correct": False},
            {"text": "The correct option", "is_correct": True},
            {"text": "The third option", "is_correct": False}
        ]
        
        question_id = self.question_manager.create_question(
            "Pick the right one", "multiple_choice",
            original_answers,
            ["Test"]
        )
        
        # Retrieve from database
        stored = self.question_manager.get_question(question_id)
        stored_answers = stored.get('answers', [])
        
        # Verify answers match
        for i, original in enumerate(original_answers):
            stored_text = stored_answers[i].get('text', '')
            self.assertEqual(stored_text, original['text'],
                           f"Answer {i+1} text should match: '{stored_text}' != '{original['text']}'")
        
        # Use in quiz
        questions = [stored]
        session_id = self.quiz_engine.start_session(questions)
        
        # Get question from session
        session = self.quiz_engine.active_sessions.get(session_id)
        session_q = session.get('questions', [])[0]
        session_answers = session_q.get('answers', [])
        
        # Verify answers still match in session
        for i, original in enumerate(original_answers):
            session_text = session_answers[i].get('text', '')
            self.assertEqual(session_text, original['text'],
                           f"Answer {i+1} in session should match: '{session_text}'")
    
    def test_scoring_correctness_with_multiple_questions(self):
        """Test scoring is correct when quiz has multiple questions."""
        # Create 4 questions
        questions = []
        for i in range(4):
            q_id = self.question_manager.create_question(
                f"Q{i+1}?", "multiple_choice",
                [{"text": "Wrong", "is_correct": False},
                 {"text": "Correct", "is_correct": True}],
                ["Test"]
            )
            q = self.question_manager.get_question(q_id)
            questions.append(q)
        
        # Start quiz
        session_id = self.quiz_engine.start_session(questions)
        
        # Answer 2 correct, 2 wrong
        for i, q in enumerate(questions):
            answers = q.get('answers', [])
            if i < 2:  # First 2: answer correctly
                correct_idx = next((j for j, a in enumerate(answers)
                                  if a.get('is_correct', False)), None)
                self.quiz_engine.submit_answer(session_id, q['id'], [correct_idx])
            else:  # Last 2: answer incorrectly
                wrong_idx = next((j for j, a in enumerate(answers)
                                if not a.get('is_correct', False)), None)
                self.quiz_engine.submit_answer(session_id, q['id'], [wrong_idx])
        
        # Check final score
        session = self.quiz_engine.active_sessions.get(session_id)
        final_score = session.get('score', 0)
        
        # Should be 50% (2 out of 4 correct)
        self.assertGreaterEqual(final_score, 49.0,
                               "2/4 correct should score ~50%")
        self.assertLessEqual(final_score, 51.0,
                            "2/4 correct should score ~50%")
    
    def test_no_data_corruption_after_multiple_operations(self):
        """Test that multiple operations don't corrupt data."""
        tag_name = "StressTest"
        tag_id = self.tag_manager.create_tag(tag_name)
        
        # Create multiple questions
        question_ids = []
        for i in range(5):
            q_id = self.question_manager.create_question(
                f"Stress test Q{i+1}?", "multiple_choice",
                [
                    {"text": f"Option A{i}", "is_correct": False},
                    {"text": f"Option B{i}", "is_correct": True}
                ],
                [tag_name]
            )
            question_ids.append(q_id)
        
        # Verify all questions still correct
        for i, q_id in enumerate(question_ids):
            stored = self.question_manager.get_question(q_id)
            self.assertIsNotNone(stored, f"Question {i+1} should still exist")
            
            stored_answers = stored.get('answers', [])
            self.assertEqual(len(stored_answers), 2,
                           f"Question {i+1} should have 2 answers")
            
            # Verify correct answer is marked
            correct_answers = [a for a in stored_answers if a.get('is_correct', False)]
            self.assertEqual(len(correct_answers), 1,
                           f"Question {i+1} should have 1 correct answer")
    
    def test_tag_association_persists(self):
        """Test that tag associations don't get lost."""
        tag_name = "PersistTest"
        tag_id = self.tag_manager.create_tag(tag_name)
        
        # Create question with tag
        q_id = self.question_manager.create_question(
            "Test question?", "multiple_choice",
            [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
            [tag_name]
        )
        
        # Retrieve multiple times
        for _ in range(3):
            stored = self.question_manager.get_question(q_id)
            stored_tags = stored.get('tags', [])
            self.assertIn(tag_name, stored_tags,
                         "Tag should persist through retrievals")
    
    def test_question_not_duplicated_in_quiz(self):
        """Test that same question doesn't appear multiple times in quiz."""
        tag_name = "NoDupTest"
        tag_id = self.tag_manager.create_tag(tag_name)
        
        # Create question
        q_id = self.question_manager.create_question(
            "Single question?", "multiple_choice",
            [{"text": "A", "is_correct": True}, {"text": "B", "is_correct": False}],
            [tag_name]
        )
        
        # Get questions for quiz
        quiz_questions = self.question_manager.get_questions_by_tags([tag_name])
        quiz_q_ids = [q['id'] for q in quiz_questions]
        
        # Count occurrences of our question
        occurrences = quiz_q_ids.count(q_id)
        self.assertEqual(occurrences, 1,
                        f"Question should appear exactly once, found {occurrences} times")


if __name__ == '__main__':
    unittest.main()

