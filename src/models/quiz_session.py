"""
Quiz Session Model

This module defines the QuizSession data model with state management,
answer tracking, and progress calculation.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QuizSession:
    """Represents a quiz session with state management and progress tracking."""
    
    def __init__(self, questions: List[Dict[str, Any]], session_id: Optional[str] = None):
        """
        Initialize a QuizSession object.
        
        Args:
            questions: List of question dictionaries for this quiz
            session_id: Optional session ID (generated if not provided)
        """
        self.id = session_id or str(uuid.uuid4())
        self.questions = questions
        self.current_question_index = 0
        self.answers = []
        self.score = 0.0
        self.start_time = datetime.now()
        self.end_time = None
        self.is_complete = False
        self.total_questions = len(questions)
        
        # Validate the session
        validation_result = self.validate()
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid quiz session: {validation_result['errors']}")
        
        logger.debug(f"Created quiz session: {self.id}")
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the quiz session data.
        
        Returns:
            Dictionary with validation result and errors
        """
        errors = []
        
        # Validate questions
        if not self.questions:
            errors.append("Quiz session must have at least one question")
        
        if len(self.questions) > 100:
            errors.append("Quiz session cannot have more than 100 questions")
        
        # Validate question structure
        for i, question in enumerate(self.questions):
            if not isinstance(question, dict):
                errors.append(f"Question {i+1} must be a dictionary")
                continue
            
            required_fields = ['id', 'question_text', 'question_type', 'answers']
            for field in required_fields:
                if field not in question:
                    errors.append(f"Question {i+1} missing required field: {field}")
        
        # Validate current question index
        if self.current_question_index < 0:
            errors.append("Current question index cannot be negative")
        
        if self.current_question_index >= len(self.questions):
            errors.append("Current question index exceeds number of questions")
        
        # Validate answers
        for i, answer in enumerate(self.answers):
            if not isinstance(answer, dict):
                errors.append(f"Answer {i+1} must be a dictionary")
                continue
            
            required_fields = ['question_id', 'selected_answers', 'is_correct', 'timestamp']
            for field in required_fields:
                if field not in answer:
                    errors.append(f"Answer {i+1} missing required field: {field}")
        
        # Validate score
        if self.score < 0 or self.score > 100:
            errors.append("Score must be between 0 and 100")
        
        # Validate timestamps
        if self.end_time and self.end_time < self.start_time:
            errors.append("End time cannot be before start time")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def add_answer(self, question_id: str, selected_answers: Any, is_correct: bool) -> None:
        """
        Add an answer to the quiz session.
        
        Args:
            question_id: ID of the question being answered
            selected_answers: User's selected answer(s)
            is_correct: Whether the answer is correct
        """
        answer = {
            'question_id': question_id,
            'selected_answers': selected_answers,
            'is_correct': is_correct,
            'timestamp': datetime.now()
        }
        
        self.answers.append(answer)
        self.current_question_index += 1
        
        # Check if quiz is complete
        if self.current_question_index >= len(self.questions):
            self.is_complete = True
            self.end_time = datetime.now()
            self.score = self.calculate_score()
        
        logger.debug(f"Added answer for question {question_id}, session {self.id}")
    
    def calculate_score(self) -> float:
        """
        Calculate the quiz score as a percentage.
        
        Returns:
            Score percentage (0-100)
        """
        if not self.answers:
            return 0.0
        
        correct_count = sum(1 for answer in self.answers if answer['is_correct'])
        total_questions = len(self.answers)
        
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0.0
        self.score = score
        
        logger.debug(f"Calculated score for session {self.id}: {score:.1f}%")
        return score
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get current quiz progress information.
        
        Returns:
            Dictionary with progress information
        """
        total_questions = len(self.questions)
        answered_questions = len(self.answers)
        remaining_questions = total_questions - answered_questions
        
        progress_percentage = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        
        return {
            'current_question': self.current_question_index + 1,
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'remaining_questions': remaining_questions,
            'progress_percentage': progress_percentage,
            'is_complete': self.is_complete
        }
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Get the current question.
        
        Returns:
            Current question dictionary or None if quiz is complete
        """
        if self.is_complete or self.current_question_index >= len(self.questions):
            return None
        
        return self.questions[self.current_question_index]
    
    def get_next_question(self) -> Optional[Dict[str, Any]]:
        """
        Get the next question and advance the session.
        
        Returns:
            Next question dictionary or None if quiz is complete
        """
        if self.is_complete:
            return None
        
        if self.current_question_index >= len(self.questions):
            self.is_complete = True
            self.end_time = datetime.now()
            self.score = self.calculate_score()
            return None
        
        return self.questions[self.current_question_index]
    
    def pause_session(self) -> None:
        """Pause the quiz session."""
        if not self.is_complete:
            logger.info(f"Paused quiz session: {self.id}")
    
    def resume_session(self) -> None:
        """Resume the quiz session."""
        if not self.is_complete:
            logger.info(f"Resumed quiz session: {self.id}")
    
    def get_duration(self) -> Optional[float]:
        """
        Get the duration of the quiz session in seconds.
        
        Returns:
            Duration in seconds or None if quiz not started
        """
        if not self.start_time:
            return None
        
        end_time = self.end_time or datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        return duration
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive quiz session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        correct_answers = sum(1 for answer in self.answers if answer['is_correct'])
        total_answers = len(self.answers)
        
        # Calculate average time per question
        duration = self.get_duration()
        avg_time_per_question = duration / total_answers if total_answers > 0 and duration else 0
        
        return {
            'session_id': self.id,
            'total_questions': self.total_questions,
            'answered_questions': total_answers,
            'correct_answers': correct_answers,
            'incorrect_answers': total_answers - correct_answers,
            'score_percentage': self.score,
            'duration_seconds': duration,
            'average_time_per_question': avg_time_per_question,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_complete': self.is_complete
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert quiz session to dictionary for serialization.
        
        Returns:
            Dictionary representation of the quiz session
        """
        return {
            'id': self.id,
            'questions': self.questions,
            'current_question_index': self.current_question_index,
            'answers': self.answers,
            'score': self.score,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_complete': self.is_complete,
            'total_questions': self.total_questions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuizSession':
        """
        Create QuizSession object from dictionary.
        
        Args:
            data: Dictionary containing quiz session data
            
        Returns:
            QuizSession object
        """
        session = cls.__new__(cls)
        session.id = data.get('id', str(uuid.uuid4()))
        session.questions = data['questions']
        session.current_question_index = data.get('current_question_index', 0)
        session.answers = data.get('answers', [])
        session.score = data.get('score', 0.0)
        session.start_time = datetime.fromisoformat(data['start_time']) if data.get('start_time') else datetime.now()
        session.end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else None
        session.is_complete = data.get('is_complete', False)
        session.total_questions = data.get('total_questions', len(session.questions))
        
        return session
    
    def __eq__(self, other) -> bool:
        """Check equality with another quiz session."""
        if not isinstance(other, QuizSession):
            return False
        
        return (self.id == other.id and 
                self.questions == other.questions and
                self.answers == other.answers and
                self.score == other.score and
                self.is_complete == other.is_complete)
    
    def __str__(self) -> str:
        """String representation of the quiz session."""
        return f"QuizSession(id={self.id[:8]}..., questions={len(self.questions)}, score={self.score:.1f}%)"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"QuizSession(id='{self.id}', questions={len(self.questions)}, "
                f"current_index={self.current_question_index}, answers={len(self.answers)}, "
                f"score={self.score}, complete={self.is_complete})")
