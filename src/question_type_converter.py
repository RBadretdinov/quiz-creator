"""
Question Type Converter

This module provides functionality to convert questions between different types
and validate conversion possibilities.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class QuestionTypeConverter:
    """Converts questions between different types with validation."""
    
    # Define conversion possibilities
    CONVERSION_MATRIX = {
        'multiple_choice': {
            'to': ['true_false', 'select_all'],
            'description': 'Can convert to true/false or select all'
        },
        'true_false': {
            'to': ['multiple_choice'],
            'description': 'Can convert to multiple choice'
        },
        'select_all': {
            'to': ['multiple_choice'],
            'description': 'Can convert to multiple choice'
        }
    }
    
    @classmethod
    def can_convert(cls, from_type: str, to_type: str) -> bool:
        """
        Check if conversion from one type to another is possible.
        
        Args:
            from_type: Source question type
            to_type: Target question type
            
        Returns:
            True if conversion is possible, False otherwise
        """
        if from_type not in cls.CONVERSION_MATRIX:
            return False
        
        return to_type in cls.CONVERSION_MATRIX[from_type]['to']
    
    @classmethod
    def get_conversion_options(cls, question_type: str) -> List[str]:
        """
        Get available conversion options for a question type.
        
        Args:
            question_type: Source question type
            
        Returns:
            List of possible target types
        """
        return cls.CONVERSION_MATRIX.get(question_type, {}).get('to', [])
    
    @classmethod
    def convert_question(cls, question: Dict[str, Any], target_type: str) -> Dict[str, Any]:
        """
        Convert a question to a different type.
        
        Args:
            question: Question dictionary to convert
            target_type: Target question type
            
        Returns:
            Converted question dictionary
        """
        source_type = question.get('question_type')
        
        if not cls.can_convert(source_type, target_type):
            raise ValueError(f"Cannot convert from {source_type} to {target_type}")
        
        if source_type == 'multiple_choice' and target_type == 'true_false':
            return cls._convert_multiple_choice_to_true_false(question)
        elif source_type == 'multiple_choice' and target_type == 'select_all':
            return cls._convert_multiple_choice_to_select_all(question)
        elif source_type == 'true_false' and target_type == 'multiple_choice':
            return cls._convert_true_false_to_multiple_choice(question)
        elif source_type == 'select_all' and target_type == 'multiple_choice':
            return cls._convert_select_all_to_multiple_choice(question)
        else:
            raise ValueError(f"Conversion from {source_type} to {target_type} not implemented")
    
    @classmethod
    def _convert_multiple_choice_to_true_false(cls, question: Dict[str, Any]) -> Dict[str, Any]:
        """Convert multiple choice to true/false."""
        answers = question.get('answers', [])
        
        if len(answers) != 2:
            raise ValueError("Multiple choice question must have exactly 2 answers to convert to true/false")
        
        # Find correct answer
        correct_answer = None
        incorrect_answer = None
        
        for answer in answers:
            if answer.get('is_correct', False):
                correct_answer = answer
            else:
                incorrect_answer = answer
        
        if not correct_answer or not incorrect_answer:
            raise ValueError("Question must have exactly one correct and one incorrect answer")
        
        # Create true/false question
        converted_question = question.copy()
        converted_question['question_type'] = 'true_false'
        converted_question['answers'] = [
            {'text': 'True', 'is_correct': True},
            {'text': 'False', 'is_correct': False}
        ]
        
        # Modify question text to be a statement
        question_text = question.get('question_text', '')
        if not question_text.endswith('.'):
            question_text += '.'
        
        converted_question['question_text'] = f"Statement: {question_text} The correct answer is '{correct_answer['text']}'."
        
        return converted_question
    
    @classmethod
    def _convert_multiple_choice_to_select_all(cls, question: Dict[str, Any]) -> Dict[str, Any]:
        """Convert multiple choice to select all."""
        answers = question.get('answers', [])
        
        if len(answers) < 2:
            raise ValueError("Multiple choice question must have at least 2 answers")
        
        # Create select all question
        converted_question = question.copy()
        converted_question['question_type'] = 'select_all'
        
        # Modify question text
        question_text = question.get('question_text', '')
        if not question_text.endswith('?'):
            question_text += '?'
        
        converted_question['question_text'] = f"{question_text} (Select all that apply)"
        
        # Keep all answers as they are (only one will be correct)
        converted_question['answers'] = answers.copy()
        
        return converted_question
    
    @classmethod
    def _convert_true_false_to_multiple_choice(cls, question: Dict[str, Any]) -> Dict[str, Any]:
        """Convert true/false to multiple choice."""
        answers = question.get('answers', [])
        
        if len(answers) != 2:
            raise ValueError("True/false question must have exactly 2 answers")
        
        # Find correct answer
        correct_answer = None
        for answer in answers:
            if answer.get('is_correct', False):
                correct_answer = answer
                break
        
        if not correct_answer:
            raise ValueError("No correct answer found in true/false question")
        
        # Create multiple choice question
        converted_question = question.copy()
        converted_question['question_type'] = 'multiple_choice'
        
        # Modify question text
        question_text = question.get('question_text', '')
        if 'Statement:' in question_text:
            # Extract the original question from statement format
            original_question = question_text.split('Statement:')[1].split('The correct answer is')[0].strip()
            converted_question['question_text'] = original_question
        else:
            converted_question['question_text'] = question_text
        
        # Create multiple choice answers
        converted_question['answers'] = [
            {'text': 'True', 'is_correct': correct_answer['text'] == 'True'},
            {'text': 'False', 'is_correct': correct_answer['text'] == 'False'},
            {'text': 'Both', 'is_correct': False},
            {'text': 'Neither', 'is_correct': False}
        ]
        
        return converted_question
    
    @classmethod
    def _convert_select_all_to_multiple_choice(cls, question: Dict[str, Any]) -> Dict[str, Any]:
        """Convert select all to multiple choice."""
        answers = question.get('answers', [])
        
        if len(answers) < 2:
            raise ValueError("Select all question must have at least 2 answers")
        
        # Count correct answers
        correct_answers = [answer for answer in answers if answer.get('is_correct', False)]
        
        if len(correct_answers) == 0:
            raise ValueError("Select all question must have at least one correct answer")
        
        # Create multiple choice question
        converted_question = question.copy()
        converted_question['question_type'] = 'multiple_choice'
        
        # Modify question text
        question_text = question.get('question_text', '')
        if '(Select all that apply)' in question_text:
            question_text = question_text.replace('(Select all that apply)', '').strip()
        
        converted_question['question_text'] = question_text
        
        # Create multiple choice answers
        if len(correct_answers) == 1:
            # Single correct answer - use original answers
            converted_question['answers'] = answers.copy()
        else:
            # Multiple correct answers - create new options
            converted_question['answers'] = [
                {'text': 'All of the above', 'is_correct': True},
                {'text': 'None of the above', 'is_correct': False},
                {'text': 'Some of the above', 'is_correct': False},
                {'text': 'Cannot be determined', 'is_correct': False}
            ]
        
        return converted_question
    
    @classmethod
    def validate_conversion(cls, question: Dict[str, Any], target_type: str) -> Dict[str, Any]:
        """
        Validate if a question can be converted to a target type.
        
        Args:
            question: Question to validate
            target_type: Target question type
            
        Returns:
            Validation result with is_valid flag and details
        """
        source_type = question.get('question_type')
        errors = []
        warnings = []
        
        # Check if conversion is possible
        if not cls.can_convert(source_type, target_type):
            errors.append(f"Cannot convert from {source_type} to {target_type}")
            return {
                'is_valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        # Type-specific validation
        if source_type == 'multiple_choice' and target_type == 'true_false':
            answers = question.get('answers', [])
            if len(answers) != 2:
                errors.append("Multiple choice question must have exactly 2 answers to convert to true/false")
        
        elif source_type == 'select_all' and target_type == 'multiple_choice':
            answers = question.get('answers', [])
            correct_count = sum(1 for answer in answers if answer.get('is_correct', False))
            if correct_count == 0:
                errors.append("Select all question must have at least one correct answer")
            elif correct_count > 1:
                warnings.append("Multiple correct answers will be converted to 'All of the above' option")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @classmethod
    def get_conversion_preview(cls, question: Dict[str, Any], target_type: str) -> Dict[str, Any]:
        """
        Get a preview of how the question would look after conversion.
        
        Args:
            question: Question to preview
            target_type: Target question type
            
        Returns:
            Preview of converted question
        """
        validation = cls.validate_conversion(question, target_type)
        
        if not validation['is_valid']:
            return {
                'can_convert': False,
                'errors': validation['errors'],
                'preview': None
            }
        
        try:
            converted_question = cls.convert_question(question, target_type)
            return {
                'can_convert': True,
                'errors': [],
                'warnings': validation['warnings'],
                'preview': converted_question
            }
        except Exception as e:
            return {
                'can_convert': False,
                'errors': [str(e)],
                'preview': None
            }
