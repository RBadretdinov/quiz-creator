"""
Quiz Engine Module

This module contains the core quiz logic including question randomization,
answer validation, scoring calculation, and quiz session management.
"""

import random
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QuizEngine:
    """Core quiz engine for managing quiz sessions and logic."""
    
    def __init__(self):
        """Initialize the quiz engine."""
        self.active_sessions: Dict[str, Dict] = {}
        logger.info("Quiz engine initialized")
    
    def randomize_questions(self, questions: List[Dict]) -> List[Dict]:
        """
        Randomize the order of questions using Fisher-Yates shuffle.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            List of questions in randomized order
        """
        if not questions:
            return []
        
        randomized = questions.copy()
        random.shuffle(randomized)
        logger.debug(f"Randomized {len(randomized)} questions")
        return randomized
    
    def randomize_answers(self, question: Dict) -> Dict:
        """
        Randomize the order of answer options for a question.
        
        Args:
            question: Question dictionary with answers array
            
        Returns:
            Question with randomized answer order
        """
        if 'answers' not in question or not question['answers']:
            return question
        
        question_copy = question.copy()
        answers = question_copy['answers'].copy()
        random.shuffle(answers)
        question_copy['answers'] = answers
        
        logger.debug(f"Randomized answers for question: {question.get('id', 'unknown')}")
        return question_copy
    
    def create_randomized_quiz(self, question_bank: List[Dict], question_count: int) -> List[Dict]:
        """
        Create a new quiz with randomized questions and answers.
        
        Args:
            question_bank: Source questions
            question_count: Number of questions to include
            
        Returns:
            List of randomized questions with randomized answers
        """
        if not question_bank:
            return []
        
        # Select random questions
        selected_questions = random.sample(question_bank, min(question_count, len(question_bank)))
        
        # Randomize question order
        randomized_questions = self.randomize_questions(selected_questions)
        
        # Randomize answers for each question
        final_quiz = [self.randomize_answers(q) for q in randomized_questions]
        
        logger.info(f"Created randomized quiz with {len(final_quiz)} questions")
        return final_quiz
    
    def start_quiz(self, questions: List[Dict]) -> str:
        """
        Initialize a new quiz session.
        
        Args:
            questions: List of questions for the quiz
            
        Returns:
            Session ID for the new quiz session
        """
        session_id = str(uuid.uuid4())
        
        session = {
            'id': session_id,
            'questions': questions,
            'current_question_index': 0,
            'answers': [],
            'score': 0,
            'start_time': datetime.now(),
            'end_time': None,
            'is_complete': False
        }
        
        self.active_sessions[session_id] = session
        logger.info(f"Started quiz session: {session_id}")
        return session_id
    
    def submit_answer(self, session_id: str, question_id: str, selected_answers: Any) -> Dict:
        """
        Process user's answer submission.
        
        Args:
            session_id: Unique session identifier
            question_id: Question being answered
            selected_answers: User's selected answer(s)
            
        Returns:
            Answer result with correctness and feedback
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        question = self._find_question_by_id(session['questions'], question_id)
        
        if not question:
            raise ValueError(f"Question {question_id} not found")
        
        # Validate answer
        is_correct = self._validate_answer(question, selected_answers)
        
        # Record answer
        answer_record = {
            'question_id': question_id,
            'selected_answers': selected_answers,
            'is_correct': is_correct,
            'timestamp': datetime.now()
        }
        
        session['answers'].append(answer_record)
        
        # Move to next question
        session['current_question_index'] += 1
        
        # Check if quiz is complete
        if session['current_question_index'] >= len(session['questions']):
            session['is_complete'] = True
            session['end_time'] = datetime.now()
            session['score'] = self.calculate_score(session)
        
        logger.debug(f"Answer submitted for session {session_id}, question {question_id}")
        
        return {
            'is_correct': is_correct,
            'correct_answers': self._get_correct_answers(question),
            'feedback': self._generate_feedback(is_correct)
        }
    
    def calculate_score(self, session: Dict) -> float:
        """
        Calculate final quiz score and statistics.
        
        Args:
            session: Completed quiz session
            
        Returns:
            Score percentage
        """
        if not session['answers']:
            return 0.0
        
        correct_count = sum(1 for answer in session['answers'] if answer['is_correct'])
        total_questions = len(session['answers'])
        
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0.0
        
        logger.info(f"Calculated score: {score:.1f}% ({correct_count}/{total_questions})")
        return score
    
    def _find_question_by_id(self, questions: List[Dict], question_id: str) -> Optional[Dict]:
        """Find a question by its ID."""
        for question in questions:
            if question.get('id') == question_id:
                return question
        return None
    
    def _validate_answer(self, question: Dict, selected_answers: Any) -> bool:
        """Validate user's answer against correct answers."""
        correct_answers = self._get_correct_answers(question)
        
        if question.get('question_type') == 'select_all':
            # For select all questions, check if all correct answers are selected
            return set(selected_answers) == set(correct_answers)
        else:
            # For single choice questions
            return selected_answers in correct_answers
    
    def _get_correct_answers(self, question: Dict) -> List[str]:
        """Get list of correct answer IDs for a question."""
        correct_answers = []
        for answer in question.get('answers', []):
            if answer.get('is_correct'):
                correct_answers.append(answer.get('id'))
        return correct_answers
    
    def _generate_feedback(self, is_correct: bool) -> str:
        """Generate immediate feedback for user answers."""
        if is_correct:
            return "Correct! Well done!"
        else:
            return "Incorrect. The correct answer has been highlighted."
