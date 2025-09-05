"""
Question Manager Module

This module handles question CRUD operations, validation, and management
of the question bank with support for different question types.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class QuestionManager:
    """Manages question bank operations and validation."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the question manager."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.questions_file = self.data_dir / "questions.json"
        self.questions: List[Dict] = []
        self._load_questions()
        logger.info("Question manager initialized")
    
    def create_question(self, question_text: str, question_type: str, 
                       answers: List[Dict], tags: List[str]) -> Dict:
        """
        Create a new question with validation.
        
        Args:
            question_text: The question content
            question_type: Type of question ('multiple_choice', 'true_false', 'select_all')
            answers: List of answer dictionaries
            tags: List of tag names
            
        Returns:
            Created question dictionary
        """
        # Validate inputs
        validation_result = self.validate_question_data(question_text, question_type, answers, tags)
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid question data: {validation_result['errors']}")
        
        # Create question object
        question = {
            'id': str(uuid.uuid4()),
            'question_text': question_text.strip(),
            'question_type': question_type,
            'answers': answers,
            'tags': tags,
            'created_at': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat(),
            'usage_count': 0
        }
        
        self.questions.append(question)
        self._save_questions()
        
        logger.info(f"Created question: {question['id']}")
        return question
    
    def get_question(self, question_id: str) -> Optional[Dict]:
        """Get a question by its ID."""
        for question in self.questions:
            if question['id'] == question_id:
                return question
        return None
    
    def get_all_questions(self) -> List[Dict]:
        """Get all questions in the question bank."""
        return self.questions.copy()
    
    def get_questions_by_tag(self, tag: str) -> List[Dict]:
        """Get all questions with a specific tag."""
        return [q for q in self.questions if tag in q.get('tags', [])]
    
    def update_question(self, question_id: str, **updates) -> bool:
        """
        Update an existing question.
        
        Args:
            question_id: ID of question to update
            **updates: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        question = self.get_question(question_id)
        if not question:
            return False
        
        # Validate updates if they include core fields
        if 'question_text' in updates or 'question_type' in updates or 'answers' in updates:
            validation_result = self.validate_question_data(
                updates.get('question_text', question['question_text']),
                updates.get('question_type', question['question_type']),
                updates.get('answers', question['answers']),
                updates.get('tags', question.get('tags', []))
            )
            if not validation_result['is_valid']:
                raise ValueError(f"Invalid update data: {validation_result['errors']}")
        
        # Apply updates
        for key, value in updates.items():
            if key in question:
                question[key] = value
        
        question['last_modified'] = datetime.now().isoformat()
        self._save_questions()
        
        logger.info(f"Updated question: {question_id}")
        return True
    
    def delete_question(self, question_id: str) -> bool:
        """Delete a question from the question bank."""
        for i, question in enumerate(self.questions):
            if question['id'] == question_id:
                del self.questions[i]
                self._save_questions()
                logger.info(f"Deleted question: {question_id}")
                return True
        return False
    
    def search_questions(self, search_term: str) -> List[Dict]:
        """Search questions by text content."""
        search_term = search_term.lower()
        results = []
        
        for question in self.questions:
            if (search_term in question['question_text'].lower() or
                any(search_term in answer.get('text', '').lower() 
                    for answer in question.get('answers', []))):
                results.append(question)
        
        return results
    
    def validate_question_data(self, question_text: str, question_type: str, 
                              answers: List[Dict], tags: List[str]) -> Dict:
        """
        Validate question data structure and content.
        
        Args:
            question_text: The question content
            question_type: Type of question
            answers: List of answer dictionaries
            tags: List of tag names
            
        Returns:
            Validation result with is_valid flag and errors list
        """
        errors = []
        
        # Validate question text
        if not question_text or not question_text.strip():
            errors.append("Question text cannot be empty")
        elif len(question_text.strip()) < 10:
            errors.append("Question text must be at least 10 characters")
        elif len(question_text.strip()) > 500:
            errors.append("Question text cannot exceed 500 characters")
        
        # Validate question type
        valid_types = ['multiple_choice', 'true_false', 'select_all']
        if question_type not in valid_types:
            errors.append(f"Question type must be one of: {', '.join(valid_types)}")
        
        # Validate answers
        if not answers or len(answers) < 2:
            errors.append("At least 2 answer options are required")
        elif len(answers) > 6:
            errors.append("Maximum 6 answer options allowed")
        
        # Validate answer structure and correctness
        correct_count = 0
        for i, answer in enumerate(answers):
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
        if question_type == 'multiple_choice' and correct_count != 1:
            errors.append("Multiple choice questions must have exactly one correct answer")
        elif question_type == 'true_false' and correct_count != 1:
            errors.append("True/false questions must have exactly one correct answer")
        elif question_type == 'select_all' and correct_count == 0:
            errors.append("Select all questions must have at least one correct answer")
        
        # Validate tags
        if not tags:
            errors.append("At least one tag is required")
        elif len(tags) > 10:
            errors.append("Maximum 10 tags allowed")
        
        for tag in tags:
            if not tag or not tag.strip():
                errors.append("Tag names cannot be empty")
            elif len(tag.strip()) > 20:
                errors.append("Tag names cannot exceed 20 characters")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _load_questions(self):
        """Load questions from JSON file."""
        if self.questions_file.exists():
            try:
                with open(self.questions_file, 'r', encoding='utf-8') as f:
                    self.questions = json.load(f)
                logger.info(f"Loaded {len(self.questions)} questions from {self.questions_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading questions: {e}")
                self.questions = []
        else:
            self.questions = []
            logger.info("No questions file found, starting with empty question bank")
    
    def _save_questions(self):
        """Save questions to JSON file."""
        try:
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self.questions)} questions to {self.questions_file}")
        except IOError as e:
            logger.error(f"Error saving questions: {e}")
            raise
