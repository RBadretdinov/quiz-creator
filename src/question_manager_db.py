"""
Database-Integrated Question Manager

This module provides a database-integrated question manager that uses SQLite
for persistent storage while maintaining compatibility with the existing interface.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from database_manager import DatabaseManager
from models.question import Question

logger = logging.getLogger(__name__)

class QuestionManagerDB:
    """Database-integrated question manager."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the database-integrated question manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        logger.info("Database-integrated question manager initialized")
    
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
        try:
            # Validate inputs
            validation_result = self.validate_question_data(question_text, question_type, answers, tags)
            if not validation_result['is_valid']:
                raise ValueError(f"Invalid question data: {validation_result['errors']}")
            
            # Create question object
            question_data = {
                'id': str(uuid.uuid4()),
                'question_text': question_text,
                'question_type': question_type,
                'answers': answers,
                'tags': tags,
                'usage_count': 0,
                'quality_score': 0.0,
                'created_at': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'created_by': None,
                'version': 1
            }
            
            # Save to database
            question_id = self.db_manager.create_question(question_data)
            if not question_id:
                raise RuntimeError("Failed to save question to database")
            
            logger.info(f"Created question: {question_id}")
            return question_data
            
        except Exception as e:
            logger.error(f"Failed to create question: {e}")
            raise
    
    def get_question(self, question_id: str) -> Optional[Dict]:
        """
        Get a question by ID.
        
        Args:
            question_id: Question ID
            
        Returns:
            Question dictionary or None if not found
        """
        try:
            return self.db_manager.get_question(question_id)
        except Exception as e:
            logger.error(f"Failed to get question {question_id}: {e}")
            return None
    
    def get_all_questions(self) -> List[Dict]:
        """
        Get all questions.
        
        Returns:
            List of question dictionaries
        """
        try:
            return self.db_manager.get_all_questions()
        except Exception as e:
            logger.error(f"Failed to get all questions: {e}")
            return []
    
    def update_question(self, question_id: str, question_text: str = None, 
                       question_type: str = None, answers: List[Dict] = None, 
                       tags: List[str] = None) -> bool:
        """
        Update a question.
        
        Args:
            question_id: Question ID
            question_text: Updated question text
            question_type: Updated question type
            answers: Updated answers
            tags: Updated tags
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing question
            existing_question = self.get_question(question_id)
            if not existing_question:
                logger.error(f"Question not found: {question_id}")
                return False
            
            # Update fields if provided
            updated_data = existing_question.copy()
            if question_text is not None:
                updated_data['question_text'] = question_text
            if question_type is not None:
                updated_data['question_type'] = question_type
            if answers is not None:
                updated_data['answers'] = answers
            if tags is not None:
                updated_data['tags'] = tags
            
            # Validate updated data
            validation_result = self.validate_question_data(
                updated_data['question_text'],
                updated_data['question_type'],
                updated_data['answers'],
                updated_data['tags']
            )
            if not validation_result['is_valid']:
                logger.error(f"Invalid updated question data: {validation_result['errors']}")
                return False
            
            # Update version and timestamp
            updated_data['version'] = updated_data.get('version', 1) + 1
            updated_data['last_modified'] = datetime.now().isoformat()
            
            # Save to database
            success = self.db_manager.update_question(question_id, updated_data)
            if success:
                logger.info(f"Updated question: {question_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to update question {question_id}: {e}")
            return False
    
    def delete_question(self, question_id: str) -> bool:
        """
        Delete a question.
        
        Args:
            question_id: Question ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            success = self.db_manager.delete_question(question_id)
            if success:
                logger.info(f"Deleted question: {question_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete question {question_id}: {e}")
            return False
    
    def search_questions(self, search_term: str, question_type: str = None, 
                        tags: List[str] = None) -> List[Dict]:
        """
        Search questions with filters.
        
        Args:
            search_term: Text to search for
            question_type: Filter by question type
            tags: Filter by tags
            
        Returns:
            List of matching questions
        """
        try:
            return self.db_manager.search_questions(search_term, question_type, tags)
        except Exception as e:
            logger.error(f"Failed to search questions: {e}")
            return []
    
    def get_questions_by_type(self, question_type: str) -> List[Dict]:
        """
        Get questions by type.
        
        Args:
            question_type: Type of questions to get
            
        Returns:
            List of questions
        """
        try:
            return self.db_manager.get_questions_by_type(question_type)
        except Exception as e:
            logger.error(f"Failed to get questions by type {question_type}: {e}")
            return []
    
    def get_questions_by_tags(self, tags: List[str]) -> List[Dict]:
        """
        Get questions by tags.
        
        Args:
            tags: List of tag names
            
        Returns:
            List of questions with any of the specified tags
        """
        try:
            # Use search with empty search term to filter by tags only
            return self.db_manager.search_questions("", None, tags)
        except Exception as e:
            logger.error(f"Failed to get questions by tags: {e}")
            return []
    
    def increment_usage_count(self, question_id: str) -> bool:
        """
        Increment usage count for a question.
        
        Args:
            question_id: Question ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return self.db_manager.increment_question_usage(question_id)
        except Exception as e:
            logger.error(f"Failed to increment usage count for {question_id}: {e}")
            return False
    
    def get_question_statistics(self) -> Dict[str, Any]:
        """
        Get question statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            return self.db_manager.get_question_statistics()
        except Exception as e:
            logger.error(f"Failed to get question statistics: {e}")
            return {}
    
    def validate_question_data(self, question_text: str, question_type: str, 
                              answers: List[Dict], tags: List[str]) -> Dict[str, Any]:
        """
        Validate question data.
        
        Args:
            question_text: Question text
            question_type: Question type
            answers: List of answers
            tags: List of tags
            
        Returns:
            Validation result dictionary
        """
        errors = []
        
        # Validate question text
        if not question_text or not question_text.strip():
            errors.append("Question text cannot be empty")
        
        # Validate question type
        valid_types = ['multiple_choice', 'true_false', 'select_all']
        if question_type not in valid_types:
            errors.append(f"Invalid question type. Must be one of: {valid_types}")
        
        # Validate answers
        if not answers or not isinstance(answers, list):
            errors.append("Answers must be a non-empty list")
        else:
            if question_type == 'multiple_choice':
                if len(answers) < 2:
                    errors.append("Multiple choice questions must have at least 2 answers")
                correct_count = sum(1 for answer in answers if answer.get('is_correct', False))
                if correct_count != 1:
                    errors.append("Multiple choice questions must have exactly 1 correct answer")
            
            elif question_type == 'true_false':
                if len(answers) != 2:
                    errors.append("True/false questions must have exactly 2 answers")
                correct_count = sum(1 for answer in answers if answer.get('is_correct', False))
                if correct_count != 1:
                    errors.append("True/false questions must have exactly 1 correct answer")
            
            elif question_type == 'select_all':
                if len(answers) < 2:
                    errors.append("Select all questions must have at least 2 answers")
                correct_count = sum(1 for answer in answers if answer.get('is_correct', False))
                if correct_count < 1:
                    errors.append("Select all questions must have at least 1 correct answer")
            
            # Validate individual answers
            for i, answer in enumerate(answers):
                if not isinstance(answer, dict):
                    errors.append(f"Answer {i+1} must be a dictionary")
                    continue
                
                if 'text' not in answer or not answer['text'].strip():
                    errors.append(f"Answer {i+1} must have non-empty text")
                
                if 'is_correct' not in answer:
                    errors.append(f"Answer {i+1} must specify if it's correct")
        
        # Validate tags
        if not isinstance(tags, list):
            errors.append("Tags must be a list")
        else:
            for tag in tags:
                if not isinstance(tag, str) or not tag.strip():
                    errors.append("All tags must be non-empty strings")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_question_count(self) -> int:
        """
        Get total number of questions.
        
        Returns:
            Number of questions
        """
        try:
            stats = self.get_question_statistics()
            return stats.get('total_questions', 0)
        except Exception as e:
            logger.error(f"Failed to get question count: {e}")
            return 0
    
    def get_questions_by_usage(self, limit: int = 10) -> List[Dict]:
        """
        Get most used questions.
        
        Args:
            limit: Maximum number of questions to return
            
        Returns:
            List of most used questions
        """
        try:
            stats = self.get_question_statistics()
            return stats.get('most_used', [])[:limit]
        except Exception as e:
            logger.error(f"Failed to get questions by usage: {e}")
            return []
    
    def get_question_types_distribution(self) -> Dict[str, int]:
        """
        Get distribution of question types.
        
        Returns:
            Dictionary mapping question types to counts
        """
        try:
            stats = self.get_question_statistics()
            return stats.get('by_type', {})
        except Exception as e:
            logger.error(f"Failed to get question types distribution: {e}")
            return {}
    
    def export_questions(self, file_path: str, format: str = 'json') -> bool:
        """
        Export questions to file.
        
        Args:
            file_path: Path to export file
            format: Export format ('json', 'csv')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            questions = self.get_all_questions()
            
            if format.lower() == 'json':
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(questions, f, indent=2, default=str)
            
            elif format.lower() == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if questions:
                        writer = csv.DictWriter(f, fieldnames=questions[0].keys())
                        writer.writeheader()
                        writer.writerows(questions)
            
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
            
            logger.info(f"Exported {len(questions)} questions to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export questions: {e}")
            return False
    
    def import_questions(self, file_path: str, format: str = 'json') -> Dict[str, Any]:
        """
        Import questions from file.
        
        Args:
            file_path: Path to import file
            format: Import format ('json', 'csv')
            
        Returns:
            Import result with statistics
        """
        result = {
            'success': False,
            'imported_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        try:
            questions = []
            
            if format.lower() == 'json':
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
            
            elif format.lower() == 'csv':
                import csv
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    questions = list(reader)
            
            else:
                result['errors'].append(f"Unsupported import format: {format}")
                return result
            
            # Import each question
            for question_data in questions:
                try:
                    # Validate and create question
                    validation_result = self.validate_question_data(
                        question_data.get('question_text', ''),
                        question_data.get('question_type', ''),
                        question_data.get('answers', []),
                        question_data.get('tags', [])
                    )
                    
                    if validation_result['is_valid']:
                        self.create_question(
                            question_data['question_text'],
                            question_data['question_type'],
                            question_data['answers'],
                            question_data['tags']
                        )
                        result['imported_count'] += 1
                    else:
                        result['failed_count'] += 1
                        result['errors'].extend(validation_result['errors'])
                
                except Exception as e:
                    result['failed_count'] += 1
                    result['errors'].append(f"Failed to import question: {e}")
            
            result['success'] = result['failed_count'] == 0
            logger.info(f"Imported {result['imported_count']} questions, {result['failed_count']} failed")
            return result
            
        except Exception as e:
            result['errors'].append(f"Import failed: {e}")
            logger.error(f"Failed to import questions: {e}")
            return result
