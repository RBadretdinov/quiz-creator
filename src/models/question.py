"""
Question Model

This module defines the Question data model with validation and serialization.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Question:
    """Represents a quiz question with validation and serialization."""
    
    def __init__(self, question_text: str, question_type: str, 
                 answers: List[Dict[str, Any]], tags: List[str], 
                 question_id: Optional[str] = None):
        """
        Initialize a Question object.
        
        Args:
            question_text: The question content
            question_type: Type of question ('multiple_choice', 'true_false', 'select_all')
            answers: List of answer dictionaries
            tags: List of tag names
            question_id: Optional question ID (generated if not provided)
        """
        self.id = question_id or str(uuid.uuid4())
        self.question_text = question_text
        self.question_type = question_type
        self.answers = answers
        self.tags = tags
        self.created_at = datetime.now().isoformat()
        self.last_modified = datetime.now().isoformat()
        self.usage_count = 0
        
        # Validate the question
        validation_result = self.validate()
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid question: {validation_result['errors']}")
        
        logger.debug(f"Created question: {self.id}")
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the question data.
        
        Returns:
            Dictionary with validation result and errors
        """
        errors = []
        
        # Validate question text
        if not self.question_text or not self.question_text.strip():
            errors.append("Question text cannot be empty")
        elif len(self.question_text.strip()) < 10:
            errors.append("Question text must be at least 10 characters")
        elif len(self.question_text.strip()) > 500:
            errors.append("Question text cannot exceed 500 characters")
        
        # Validate question type
        valid_types = ['multiple_choice', 'true_false', 'select_all']
        if self.question_type not in valid_types:
            errors.append(f"Question type must be one of: {', '.join(valid_types)}")
        
        # Validate answers
        if not self.answers or len(self.answers) < 2:
            errors.append("At least 2 answer options are required")
        elif len(self.answers) > 6:
            errors.append("Maximum 6 answer options allowed")
        
        # Validate answer structure
        correct_count = 0
        for i, answer in enumerate(self.answers):
            if not isinstance(answer, dict):
                errors.append(f"Answer {i+1} must be a dictionary")
                continue
            
            if 'text' not in answer or not answer['text'].strip():
                errors.append(f"Answer {i+1} text cannot be empty")
            
            if 'is_correct' not in answer:
                errors.append(f"Answer {i+1} must specify if it's correct")
            elif answer['is_correct']:
                correct_count += 1
        
        # Validate correct answer count based on question type
        if self.question_type == 'multiple_choice' and correct_count != 1:
            errors.append("Multiple choice questions must have exactly one correct answer")
        elif self.question_type == 'true_false' and correct_count != 1:
            errors.append("True/false questions must have exactly one correct answer")
        elif self.question_type == 'select_all' and correct_count == 0:
            errors.append("Select all questions must have at least one correct answer")
        
        # Validate tags
        if not self.tags:
            errors.append("At least one tag is required")
        elif len(self.tags) > 10:
            errors.append("Maximum 10 tags allowed")
        
        for tag in self.tags:
            if not tag or not tag.strip():
                errors.append("Tag names cannot be empty")
            elif len(tag.strip()) > 20:
                errors.append("Tag names cannot exceed 20 characters")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert question to dictionary for serialization.
        
        Returns:
            Dictionary representation of the question
        """
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'answers': self.answers,
            'tags': self.tags,
            'created_at': self.created_at,
            'last_modified': self.last_modified,
            'usage_count': self.usage_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """
        Create Question object from dictionary.
        
        Args:
            data: Dictionary containing question data
            
        Returns:
            Question object
        """
        question = cls.__new__(cls)
        question.id = data.get('id', str(uuid.uuid4()))
        question.question_text = data['question_text']
        question.question_type = data['question_type']
        question.answers = data['answers']
        question.tags = data['tags']
        question.created_at = data.get('created_at', datetime.now().isoformat())
        question.last_modified = data.get('last_modified', datetime.now().isoformat())
        question.usage_count = data.get('usage_count', 0)
        
        return question
    
    def update(self, **updates) -> None:
        """
        Update question fields.
        
        Args:
            **updates: Fields to update
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.last_modified = datetime.now().isoformat()
        
        # Re-validate after update
        validation_result = self.validate()
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid update: {validation_result['errors']}")
        
        logger.debug(f"Updated question: {self.id}")
    
    def increment_usage(self) -> None:
        """Increment the usage count for this question."""
        self.usage_count += 1
        self.last_modified = datetime.now().isoformat()
        logger.debug(f"Incremented usage for question: {self.id}")
    
    def get_correct_answers(self) -> List[str]:
        """
        Get list of correct answer IDs.
        
        Returns:
            List of correct answer IDs
        """
        return [answer['id'] for answer in self.answers if answer.get('is_correct')]
    
    def get_answer_by_id(self, answer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get answer by ID.
        
        Args:
            answer_id: Answer ID to find
            
        Returns:
            Answer dictionary or None if not found
        """
        for answer in self.answers:
            if answer.get('id') == answer_id:
                return answer
        return None
    
    def __eq__(self, other) -> bool:
        """Check equality with another question."""
        if not isinstance(other, Question):
            return False
        
        return (self.id == other.id and 
                self.question_text == other.question_text and
                self.question_type == other.question_type and
                self.answers == other.answers and
                self.tags == other.tags)
    
    def __str__(self) -> str:
        """String representation of the question."""
        return f"Question(id={self.id[:8]}..., text='{self.question_text[:50]}...', type={self.question_type})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Question(id='{self.id}', question_text='{self.question_text}', "
                f"question_type='{self.question_type}', answers={len(self.answers)}, "
                f"tags={self.tags}, usage_count={self.usage_count})")
