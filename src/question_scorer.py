"""
Question Scorer

This module provides scoring logic for different question types with
partial credit support and simple feedback (correct/incorrect only).
"""

from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class QuestionScorer:
    """Handles scoring for different question types with partial credit support."""
    
    @staticmethod
    def calculate_score(question_type: str, correct_answers: List[Dict[str, Any]], 
                       user_selections: List[int]) -> Dict[str, Any]:
        """
        Calculate score for a question based on type and user selections.
        
        Args:
            question_type: Type of question
            correct_answers: List of correct answer dictionaries
            user_selections: List of user's selected answer indices (0-based)
            
        Returns:
            Score information with points, feedback, and details
        """
        if question_type == 'multiple_choice':
            return QuestionScorer._score_multiple_choice(correct_answers, user_selections)
        elif question_type == 'true_false':
            return QuestionScorer._score_true_false(correct_answers, user_selections)
        elif question_type == 'select_all':
            return QuestionScorer._score_select_all(correct_answers, user_selections)
        else:
            return {
                'points_earned': 0,
                'max_points': 1,
                'is_correct': False,
                'feedback': 'Incorrect',
                'details': {'error': 'Unknown question type'}
            }
    
    @staticmethod
    def _score_multiple_choice(correct_answers: List[Dict[str, Any]], 
                              user_selections: List[int]) -> Dict[str, Any]:
        """Score multiple choice questions."""
        if len(user_selections) != 1:
            return {
                'points_earned': 0,
                'max_points': 1,
                'is_correct': False,
                'feedback': 'Incorrect',
                'details': {'error': 'Multiple choice requires exactly one selection'}
            }
        
        # Find correct answer index
        correct_index = None
        for i, answer in enumerate(correct_answers):
            if answer.get('is_correct', False):
                correct_index = i
                break
        
        if correct_index is None:
            return {
                'points_earned': 0,
                'max_points': 1,
                'is_correct': False,
                'feedback': 'Incorrect',
                'details': {'error': 'No correct answer found in question'}
            }
        
        is_correct = user_selections[0] == correct_index
        
        return {
            'points_earned': 1 if is_correct else 0,
            'max_points': 1,
            'is_correct': is_correct,
            'feedback': 'Correct' if is_correct else 'Incorrect',
            'details': {'selected': user_selections[0], 'correct': correct_index}
        }
    
    @staticmethod
    def _score_true_false(correct_answers: List[Dict[str, Any]], 
                         user_selections: List[int]) -> Dict[str, Any]:
        """Score true/false questions."""
        if len(user_selections) != 1:
            return {
                'points_earned': 0,
                'max_points': 1,
                'is_correct': False,
                'feedback': 'Incorrect',
                'details': {'error': 'True/false requires exactly one selection'}
            }
        
        # Find correct answer index
        correct_index = None
        for i, answer in enumerate(correct_answers):
            if answer.get('is_correct', False):
                correct_index = i
                break
        
        if correct_index is None:
            return {
                'points_earned': 0,
                'max_points': 1,
                'is_correct': False,
                'feedback': 'Incorrect',
                'details': {'error': 'No correct answer found in question'}
            }
        
        is_correct = user_selections[0] == correct_index
        
        return {
            'points_earned': 1 if is_correct else 0,
            'max_points': 1,
            'is_correct': is_correct,
            'feedback': 'Correct' if is_correct else 'Incorrect',
            'details': {'selected': user_selections[0], 'correct': correct_index}
        }
    
    @staticmethod
    def _score_select_all(correct_answers: List[Dict[str, Any]], 
                         user_selections: List[int]) -> Dict[str, Any]:
        """Score select all questions with partial credit."""
        if len(user_selections) == 0:
            return {
                'points_earned': 0,
                'max_points': 1,
                'is_correct': False,
                'feedback': 'Incorrect',
                'details': {'error': 'No selections made'}
            }
        
        # Find correct and incorrect answer indices
        correct_indices = set()
        incorrect_indices = set()
        
        for i, answer in enumerate(correct_answers):
            if answer.get('is_correct', False):
                correct_indices.add(i)
            else:
                incorrect_indices.add(i)
        
        if not correct_indices:
            return {
                'points_earned': 0,
                'max_points': 1,
                'is_correct': False,
                'feedback': 'Incorrect',
                'details': {'error': 'No correct answers found in question'}
            }
        
        user_selection_set = set(user_selections)
        
        # Calculate partial credit
        correct_selections = user_selection_set.intersection(correct_indices)
        incorrect_selections = user_selection_set.intersection(incorrect_indices)
        missed_correct = correct_indices - user_selection_set
        
        # Calculate score based on partial credit system
        total_correct = len(correct_indices)
        total_incorrect = len(incorrect_indices)
        
        # Points for correct selections
        correct_points = len(correct_selections) / total_correct if total_correct > 0 else 0
        
        # Penalty for incorrect selections
        incorrect_penalty = len(incorrect_selections) / total_incorrect if total_incorrect > 0 else 0
        
        # Final score (minimum 0)
        final_score = max(0, correct_points - (incorrect_penalty * 0.5))
        
        # Determine if fully correct
        is_fully_correct = (len(correct_selections) == total_correct and 
                           len(incorrect_selections) == 0)
        
        # Generate feedback
        if is_fully_correct:
            feedback = 'Correct'
        elif final_score >= 0.5:
            feedback = 'Partially Correct'
        else:
            feedback = 'Incorrect'
        
        return {
            'points_earned': final_score,
            'max_points': 1,
            'is_correct': is_fully_correct,
            'feedback': feedback,
            'details': {
                'correct_selections': len(correct_selections),
                'incorrect_selections': len(incorrect_selections),
                'missed_correct': len(missed_correct),
                'total_correct': total_correct,
                'partial_credit': final_score
            }
        }
    
    @staticmethod
    def get_scoring_info(question_type: str) -> Dict[str, Any]:
        """
        Get scoring information for a question type.
        
        Args:
            question_type: Type of question
            
        Returns:
            Scoring information and rules
        """
        scoring_info = {
            'multiple_choice': {
                'max_points': 1,
                'scoring_type': 'binary',
                'partial_credit': False,
                'description': 'All or nothing scoring'
            },
            'true_false': {
                'max_points': 1,
                'scoring_type': 'binary',
                'partial_credit': False,
                'description': 'All or nothing scoring'
            },
            'select_all': {
                'max_points': 1,
                'scoring_type': 'partial',
                'partial_credit': True,
                'description': 'Partial credit based on correct/incorrect selections'
            }
        }
        
        return scoring_info.get(question_type, {
            'max_points': 1,
            'scoring_type': 'unknown',
            'partial_credit': False,
            'description': 'Unknown scoring type'
        })
    
    @staticmethod
    def calculate_quiz_score(question_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall quiz score from individual question results.
        
        Args:
            question_results: List of question scoring results
            
        Returns:
            Overall quiz score information
        """
        if not question_results:
            return {
                'total_points': 0,
                'max_points': 0,
                'percentage': 0,
                'correct_count': 0,
                'total_questions': 0
            }
        
        total_points = sum(result.get('points_earned', 0) for result in question_results)
        max_points = sum(result.get('max_points', 1) for result in question_results)
        correct_count = sum(1 for result in question_results if result.get('is_correct', False))
        total_questions = len(question_results)
        
        percentage = (total_points / max_points * 100) if max_points > 0 else 0
        
        return {
            'total_points': total_points,
            'max_points': max_points,
            'percentage': round(percentage, 2),
            'correct_count': correct_count,
            'total_questions': total_questions,
            'average_per_question': total_points / total_questions if total_questions > 0 else 0
        }
