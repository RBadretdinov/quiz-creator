"""
Question Type Validator

This module provides comprehensive validation for different question types
with type-specific rules and validation logic.
"""

from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class QuestionTypeValidator:
    """Validates questions based on their type with specific rules."""
    
    # Define valid question types and their requirements
    QUESTION_TYPES = {
        'multiple_choice': {
            'min_answers': 2,
            'max_answers': 6,
            'correct_answers': 1,
            'description': 'Choose one correct answer from multiple options'
        },
        'true_false': {
            'min_answers': 2,
            'max_answers': 2,
            'correct_answers': 1,
            'description': 'Choose True or False'
        },
        'select_all': {
            'min_answers': 2,
            'max_answers': 8,
            'correct_answers': 'at_least_one',
            'description': 'Select all correct answers from multiple options'
        }
    }
    
    @classmethod
    def validate_question_type(cls, question_type: str) -> Dict[str, Any]:
        """
        Validate if question type is supported.
        
        Args:
            question_type: Type of question to validate
            
        Returns:
            Validation result with is_valid flag and details
        """
        if question_type not in cls.QUESTION_TYPES:
            return {
                'is_valid': False,
                'error': f"Unsupported question type: {question_type}",
                'supported_types': list(cls.QUESTION_TYPES.keys())
            }
        
        return {
            'is_valid': True,
            'type_info': cls.QUESTION_TYPES[question_type]
        }
    
    @classmethod
    def validate_answers_for_type(cls, question_type: str, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate answers based on question type requirements.
        
        Args:
            question_type: Type of question
            answers: List of answer dictionaries
            
        Returns:
            Validation result with is_valid flag and errors
        """
        errors = []
        
        # Get type requirements
        type_info = cls.QUESTION_TYPES.get(question_type)
        if not type_info:
            return {
                'is_valid': False,
                'errors': [f"Unknown question type: {question_type}"]
            }
        
        # Validate answer count
        answer_count = len(answers)
        if answer_count < type_info['min_answers']:
            errors.append(f"At least {type_info['min_answers']} answers required for {question_type}")
        elif answer_count > type_info['max_answers']:
            errors.append(f"Maximum {type_info['max_answers']} answers allowed for {question_type}")
        
        # Validate answer structure
        correct_count = 0
        for i, answer in enumerate(answers):
            if not isinstance(answer, dict):
                errors.append(f"Answer {i+1} must be a dictionary")
                continue
            
            # Validate text
            if 'text' not in answer or not answer['text'].strip():
                errors.append(f"Answer {i+1} text cannot be empty")
            elif len(answer['text'].strip()) > 200:
                errors.append(f"Answer {i+1} text cannot exceed 200 characters")
            
            # Validate is_correct field
            if 'is_correct' not in answer:
                errors.append(f"Answer {i+1} must specify if it's correct")
            elif not isinstance(answer['is_correct'], bool):
                errors.append(f"Answer {i+1} is_correct must be boolean")
            elif answer['is_correct']:
                correct_count += 1
        
        # Validate correct answer count based on type
        if question_type == 'multiple_choice':
            if correct_count != 1:
                errors.append("Multiple choice questions must have exactly one correct answer")
        elif question_type == 'true_false':
            if correct_count != 1:
                errors.append("True/false questions must have exactly one correct answer")
            # Additional validation for true/false
            if answer_count == 2:
                true_false_texts = [answer.get('text', '').lower().strip() for answer in answers]
                if not ('true' in true_false_texts and 'false' in true_false_texts):
                    errors.append("True/false questions should have 'True' and 'False' as answer options")
        elif question_type == 'select_all':
            if correct_count == 0:
                errors.append("Select all questions must have at least one correct answer")
            elif correct_count == answer_count:
                errors.append("Select all questions should not have all answers as correct")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'correct_count': correct_count,
            'total_count': answer_count
        }
    
    @classmethod
    def validate_answer_selection(cls, question_type: str, selected_answers: List[int], 
                                total_answers: int) -> Dict[str, Any]:
        """
        Validate user's answer selection for a question type.
        
        Args:
            question_type: Type of question
            selected_answers: List of selected answer indices (0-based)
            total_answers: Total number of answer options
            
        Returns:
            Validation result with is_valid flag and details
        """
        errors = []
        
        # Validate selection indices
        if not isinstance(selected_answers, list):
            errors.append("Selected answers must be a list")
            return {'is_valid': False, 'errors': errors}
        
        # Check for valid indices
        for answer_idx in selected_answers:
            if not isinstance(answer_idx, int):
                errors.append("Answer indices must be integers")
            elif answer_idx < 0 or answer_idx >= total_answers:
                errors.append(f"Answer index {answer_idx} is out of range (0-{total_answers-1})")
        
        # Type-specific validation
        if question_type == 'multiple_choice':
            if len(selected_answers) != 1:
                errors.append("Multiple choice questions require exactly one selection")
        elif question_type == 'true_false':
            if len(selected_answers) != 1:
                errors.append("True/false questions require exactly one selection")
        elif question_type == 'select_all':
            if len(selected_answers) == 0:
                errors.append("Select all questions require at least one selection")
            elif len(selected_answers) > total_answers:
                errors.append("Cannot select more answers than available")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'selection_count': len(selected_answers)
        }
    
    @classmethod
    def get_question_type_info(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all supported question types.
        
        Returns:
            Dictionary with question type information
        """
        return cls.QUESTION_TYPES.copy()
    
    @classmethod
    def get_validation_rules(cls, question_type: str) -> Dict[str, Any]:
        """
        Get validation rules for a specific question type.
        
        Args:
            question_type: Type of question
            
        Returns:
            Validation rules for the question type
        """
        return cls.QUESTION_TYPES.get(question_type, {})
    
    @classmethod
    def suggest_question_improvements(cls, question_type: str, 
                                    answers: List[Dict[str, Any]]) -> List[str]:
        """
        Suggest improvements for a question based on its type.
        
        Args:
            question_type: Type of question
            answers: List of answer dictionaries
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        if question_type == 'multiple_choice':
            if len(answers) < 4:
                suggestions.append("Consider adding more answer options for better challenge")
            if len(answers) > 5:
                suggestions.append("Consider reducing answer options for clarity")
        
        elif question_type == 'true_false':
            # Check if answers are clearly True/False
            true_false_texts = [answer.get('text', '').lower().strip() for answer in answers]
            if not ('true' in true_false_texts and 'false' in true_false_texts):
                suggestions.append("Ensure answer options are clearly 'True' and 'False'")
        
        elif question_type == 'select_all':
            correct_count = sum(1 for answer in answers if answer.get('is_correct', False))
            total_count = len(answers)
            
            if correct_count == 1:
                suggestions.append("Consider if this should be a multiple choice question instead")
            elif correct_count == total_count - 1:
                suggestions.append("Consider if this should be a true/false question instead")
            elif correct_count < total_count * 0.3:
                suggestions.append("Consider if the question is too difficult with few correct answers")
            elif correct_count > total_count * 0.7:
                suggestions.append("Consider if the question is too easy with many correct answers")
        
        return suggestions
