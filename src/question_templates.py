"""
Question Templates

This module provides templates and presets for different question types
to help users create questions more easily.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class QuestionTemplates:
    """Provides templates and presets for question creation."""
    
    # Question type templates
    TEMPLATES = {
        'multiple_choice': {
            'name': 'Multiple Choice',
            'description': 'Choose one correct answer from multiple options',
            'template': {
                'question_text': 'What is the correct answer?',
                'question_type': 'multiple_choice',
                'answers': [
                    {'text': 'Option A', 'is_correct': True},
                    {'text': 'Option B', 'is_correct': False},
                    {'text': 'Option C', 'is_correct': False},
                    {'text': 'Option D', 'is_correct': False}
                ],
                'tags': ['general']
            },
            'examples': [
                {
                    'question_text': 'What is the capital of France?',
                    'answers': [
                        {'text': 'Paris', 'is_correct': True},
                        {'text': 'London', 'is_correct': False},
                        {'text': 'Berlin', 'is_correct': False},
                        {'text': 'Madrid', 'is_correct': False}
                    ]
                },
                {
                    'question_text': 'Which programming language is known for its simplicity?',
                    'answers': [
                        {'text': 'Python', 'is_correct': True},
                        {'text': 'C++', 'is_correct': False},
                        {'text': 'Assembly', 'is_correct': False},
                        {'text': 'Fortran', 'is_correct': False}
                    ]
                }
            ]
        },
        
        'true_false': {
            'name': 'True/False',
            'description': 'Choose True or False',
            'template': {
                'question_text': 'This statement is true or false?',
                'question_type': 'true_false',
                'answers': [
                    {'text': 'True', 'is_correct': True},
                    {'text': 'False', 'is_correct': False}
                ],
                'tags': ['general']
            },
            'examples': [
                {
                    'question_text': 'The Earth is round.',
                    'answers': [
                        {'text': 'True', 'is_correct': True},
                        {'text': 'False', 'is_correct': False}
                    ]
                },
                {
                    'question_text': 'Water boils at 100°C at sea level.',
                    'answers': [
                        {'text': 'True', 'is_correct': True},
                        {'text': 'False', 'is_correct': False}
                    ]
                }
            ]
        },
        
        'select_all': {
            'name': 'Select All That Apply',
            'description': 'Select all correct answers from multiple options',
            'template': {
                'question_text': 'Which of the following are correct? (Select all that apply)',
                'question_type': 'select_all',
                'answers': [
                    {'text': 'Option A', 'is_correct': True},
                    {'text': 'Option B', 'is_correct': False},
                    {'text': 'Option C', 'is_correct': True},
                    {'text': 'Option D', 'is_correct': False},
                    {'text': 'Option E', 'is_correct': True}
                ],
                'tags': ['general']
            },
            'examples': [
                {
                    'question_text': 'Which of the following are programming languages? (Select all that apply)',
                    'answers': [
                        {'text': 'Python', 'is_correct': True},
                        {'text': 'HTML', 'is_correct': False},
                        {'text': 'JavaScript', 'is_correct': True},
                        {'text': 'CSS', 'is_correct': False},
                        {'text': 'Java', 'is_correct': True}
                    ]
                },
                {
                    'question_text': 'Which of the following are primary colors? (Select all that apply)',
                    'answers': [
                        {'text': 'Red', 'is_correct': True},
                        {'text': 'Blue', 'is_correct': True},
                        {'text': 'Green', 'is_correct': False},
                        {'text': 'Yellow', 'is_correct': False}
                    ]
                }
            ]
        }
    }
    
    # Subject-specific presets
    SUBJECT_PRESETS = {
        'science': {
            'name': 'Science',
            'tags': ['science', 'general'],
            'templates': {
                'multiple_choice': {
                    'question_text': 'What is the scientific explanation for...?',
                    'answers': [
                        {'text': 'Correct scientific answer', 'is_correct': True},
                        {'text': 'Common misconception', 'is_correct': False},
                        {'text': 'Unrelated fact', 'is_correct': False},
                        {'text': 'Opposite of truth', 'is_correct': False}
                    ]
                },
                'true_false': {
                    'question_text': 'Scientific statement: ...',
                    'answers': [
                        {'text': 'True', 'is_correct': True},
                        {'text': 'False', 'is_correct': False}
                    ]
                }
            }
        },
        
        'mathematics': {
            'name': 'Mathematics',
            'tags': ['mathematics', 'math'],
            'templates': {
                'multiple_choice': {
                    'question_text': 'What is the solution to...?',
                    'answers': [
                        {'text': 'Correct answer', 'is_correct': True},
                        {'text': 'Common calculation error', 'is_correct': False},
                        {'text': 'Wrong formula result', 'is_correct': False},
                        {'text': 'Random number', 'is_correct': False}
                    ]
                },
                'select_all': {
                    'question_text': 'Which of the following are valid solutions? (Select all that apply)',
                    'answers': [
                        {'text': 'Solution 1', 'is_correct': True},
                        {'text': 'Solution 2', 'is_correct': True},
                        {'text': 'Common mistake', 'is_correct': False},
                        {'text': 'Invalid approach', 'is_correct': False}
                    ]
                }
            }
        },
        
        'history': {
            'name': 'History',
            'tags': ['history', 'social-studies'],
            'templates': {
                'multiple_choice': {
                    'question_text': 'What happened in...?',
                    'answers': [
                        {'text': 'Correct historical fact', 'is_correct': True},
                        {'text': 'Wrong time period', 'is_correct': False},
                        {'text': 'Different event', 'is_correct': False},
                        {'text': 'Myth or legend', 'is_correct': False}
                    ]
                },
                'true_false': {
                    'question_text': 'Historical statement: ...',
                    'answers': [
                        {'text': 'True', 'is_correct': True},
                        {'text': 'False', 'is_correct': False}
                    ]
                }
            }
        },
        
        'programming': {
            'name': 'Programming',
            'tags': ['programming', 'computer-science', 'coding'],
            'templates': {
                'multiple_choice': {
                    'question_text': 'What is the output of this code?',
                    'answers': [
                        {'text': 'Correct output', 'is_correct': True},
                        {'text': 'Syntax error result', 'is_correct': False},
                        {'text': 'Wrong logic result', 'is_correct': False},
                        {'text': 'Runtime error', 'is_correct': False}
                    ]
                },
                'select_all': {
                    'question_text': 'Which of the following are valid programming concepts? (Select all that apply)',
                    'answers': [
                        {'text': 'Variable', 'is_correct': True},
                        {'text': 'Function', 'is_correct': True},
                        {'text': 'Syntax error', 'is_correct': False},
                        {'text': 'Logic error', 'is_correct': False}
                    ]
                }
            }
        }
    }
    
    @classmethod
    def get_template(cls, question_type: str) -> Optional[Dict[str, Any]]:
        """
        Get template for a specific question type.
        
        Args:
            question_type: Type of question
            
        Returns:
            Template dictionary or None if not found
        """
        return cls.TEMPLATES.get(question_type)
    
    @classmethod
    def get_all_templates(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get all available templates.
        
        Returns:
            Dictionary of all templates
        """
        return cls.TEMPLATES.copy()
    
    @classmethod
    def get_subject_preset(cls, subject: str) -> Optional[Dict[str, Any]]:
        """
        Get subject-specific preset.
        
        Args:
            subject: Subject name
            
        Returns:
            Subject preset or None if not found
        """
        return cls.SUBJECT_PRESETS.get(subject)
    
    @classmethod
    def get_all_subject_presets(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get all available subject presets.
        
        Returns:
            Dictionary of all subject presets
        """
        return cls.SUBJECT_PRESETS.copy()
    
    @classmethod
    def create_question_from_template(cls, question_type: str, 
                                    custom_text: str = None,
                                    custom_answers: List[Dict[str, Any]] = None,
                                    custom_tags: List[str] = None) -> Dict[str, Any]:
        """
        Create a question from a template with custom modifications.
        
        Args:
            question_type: Type of question
            custom_text: Custom question text (optional)
            custom_answers: Custom answers (optional)
            custom_tags: Custom tags (optional)
            
        Returns:
            Question dictionary based on template
        """
        template = cls.get_template(question_type)
        if not template:
            raise ValueError(f"No template found for question type: {question_type}")
        
        question = template['template'].copy()
        
        if custom_text:
            question['question_text'] = custom_text
        
        if custom_answers:
            question['answers'] = custom_answers
        
        if custom_tags:
            question['tags'] = custom_tags
        
        return question
    
    @classmethod
    def get_examples(cls, question_type: str) -> List[Dict[str, Any]]:
        """
        Get example questions for a question type.
        
        Args:
            question_type: Type of question
            
        Returns:
            List of example questions
        """
        template = cls.get_template(question_type)
        if not template:
            return []
        
        return template.get('examples', [])
    
    @classmethod
    def suggest_question_structure(cls, question_type: str, 
                                 subject: str = None) -> Dict[str, Any]:
        """
        Suggest question structure based on type and subject.
        
        Args:
            question_type: Type of question
            subject: Optional subject area
            
        Returns:
            Suggested structure and tips
        """
        template = cls.get_template(question_type)
        if not template:
            return {}
        
        suggestions = {
            'question_type': question_type,
            'description': template['description'],
            'tips': [],
            'structure': template['template']
        }
        
        # Add type-specific tips
        if question_type == 'multiple_choice':
            suggestions['tips'] = [
                'Use 4-5 answer options for optimal difficulty',
                'Make incorrect options plausible but clearly wrong',
                'Avoid "all of the above" or "none of the above"',
                'Keep answer options similar in length'
            ]
        elif question_type == 'true_false':
            suggestions['tips'] = [
                'Make statements clearly true or false',
                'Avoid ambiguous or partially true statements',
                'Use simple, direct language',
                'Avoid double negatives'
            ]
        elif question_type == 'select_all':
            suggestions['tips'] = [
                'Include 2-4 correct answers',
                'Make incorrect options clearly wrong',
                'Use "Select all that apply" in the question',
                'Balance the number of correct and incorrect options'
            ]
        
        # Add subject-specific tips if provided
        if subject:
            subject_preset = cls.get_subject_preset(subject)
            if subject_preset:
                suggestions['subject_tags'] = subject_preset['tags']
                suggestions['subject_name'] = subject_preset['name']
        
        return suggestions
