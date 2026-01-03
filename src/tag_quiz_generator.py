"""
Tag-Based Quiz Generator

This module provides algorithms for generating quizzes based on tag criteria,
including hierarchical tag selection and balanced question distribution.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
import random
import logging
from datetime import datetime

from models.question import Question
from models.tag import Tag
from models.quiz_session import QuizSession
from tag_manager import TagManager
from question_filter import QuestionFilter

logger = logging.getLogger(__name__)

class TagQuizGenerator:
    """Generates quizzes based on tag criteria and hierarchical selection."""
    
    def __init__(self, tag_manager: TagManager, question_filter: QuestionFilter):
        """Initialize the tag quiz generator."""
        self.tag_manager = tag_manager
        self.question_filter = question_filter
        self.logger = logging.getLogger(__name__)
    
    def generate_quiz_by_tags(self, tag_criteria: Dict[str, Any], 
                            question_count: int = 10) -> List[Question]:
        """
        Generate a quiz based on tag criteria.
        
        Args:
            tag_criteria: Dictionary specifying tag selection criteria
            question_count: Number of questions to generate
            
        Returns:
            List of selected questions
        """
        # Get all available questions (placeholder - would need QuestionManager)
        all_questions = self._get_all_questions()
        
        if not all_questions:
            return []
        
        # Apply tag filters
        filtered_questions = self.question_filter.filter_questions(
            all_questions, {'tags': tag_criteria}
        )
        
        if not filtered_questions:
            return []
        
        # Select questions based on strategy
        selection_strategy = tag_criteria.get('strategy', 'random')
        
        if selection_strategy == 'random':
            return self._select_random_questions(filtered_questions, question_count)
        elif selection_strategy == 'balanced':
            return self._select_balanced_questions(filtered_questions, tag_criteria, question_count)
        elif selection_strategy == 'hierarchical':
            return self._select_hierarchical_questions(filtered_questions, tag_criteria, question_count)
        elif selection_strategy == 'weighted':
            return self._select_weighted_questions(filtered_questions, tag_criteria, question_count)
        else:
            return self._select_random_questions(filtered_questions, question_count)
    
    def generate_quiz_by_hierarchy(self, root_tag_name: str, 
                                 question_count: int = 10,
                                 include_children: bool = True) -> List[Question]:
        """
        Generate a quiz from a tag hierarchy.
        
        Args:
            root_tag_name: Name of the root tag
            question_count: Number of questions to generate
            include_children: Whether to include questions from child tags
            
        Returns:
            List of selected questions
        """
        root_tag = self.tag_manager.get_tag_by_name(root_tag_name)
        if not root_tag:
            return []
        
        # Get questions from hierarchy
        hierarchy_questions = self.question_filter.get_questions_by_tag_hierarchy(root_tag_name)
        
        if not hierarchy_questions:
            return []
        
        # Flatten all questions
        all_questions = []
        for tag_name, questions in hierarchy_questions.items():
            all_questions.extend(questions)
        
        # Remove duplicates
        seen_ids = set()
        unique_questions = []
        for question in all_questions:
            if question.id not in seen_ids:
                unique_questions.append(question)
                seen_ids.add(question.id)
        
        # Select questions
        return self._select_random_questions(unique_questions, question_count)
    
    def generate_balanced_quiz(self, tag_weights: Dict[str, float], 
                             question_count: int = 10) -> List[Question]:
        """
        Generate a quiz with balanced representation from multiple tags.
        
        Args:
            tag_weights: Dictionary mapping tag names to weights
            question_count: Number of questions to generate
            
        Returns:
            List of selected questions
        """
        # Normalize weights
        total_weight = sum(tag_weights.values())
        if total_weight == 0:
            return []
        
        normalized_weights = {tag: weight / total_weight for tag, weight in tag_weights.items()}
        
        # Get questions for each tag
        tag_questions = {}
        for tag_name in tag_weights.keys():
            questions = self.question_filter.get_questions_by_tag(tag_name)
            if questions:
                tag_questions[tag_name] = questions
        
        if not tag_questions:
            return []
        
        # Calculate target question count per tag
        selected_questions = []
        remaining_count = question_count
        
        for tag_name, weight in normalized_weights.items():
            if tag_name not in tag_questions:
                continue
            
            target_count = max(1, int(question_count * weight))
            actual_count = min(target_count, len(tag_questions[tag_name]), remaining_count)
            
            if actual_count > 0:
                selected = random.sample(tag_questions[tag_name], actual_count)
                selected_questions.extend(selected)
                remaining_count -= actual_count
            
            if remaining_count <= 0:
                break
        
        # If we need more questions, fill from remaining
        if remaining_count > 0:
            all_remaining = []
            for questions in tag_questions.values():
                all_remaining.extend(questions)
            
            # Remove already selected questions
            selected_ids = {q.id for q in selected_questions}
            available = [q for q in all_remaining if q.id not in selected_ids]
            
            if available and remaining_count > 0:
                additional = random.sample(available, min(remaining_count, len(available)))
                selected_questions.extend(additional)
        
        return selected_questions
    
    def generate_adaptive_quiz(self, user_performance: Dict[str, Any], 
                             question_count: int = 10) -> List[Question]:
        """
        Generate an adaptive quiz based on user performance.
        
        Args:
            user_performance: Dictionary with user performance data
            question_count: Number of questions to generate
            
        Returns:
            List of selected questions
        """
        # Analyze user performance to identify weak areas
        weak_tags = self._identify_weak_tags(user_performance)
        strong_tags = self._identify_strong_tags(user_performance)
        
        # Generate quiz focusing on weak areas with some strong areas for confidence
        weak_weight = 0.7  # 70% focus on weak areas
        strong_weight = 0.3  # 30% focus on strong areas
        
        tag_weights = {}
        
        # Add weak tags with higher weight
        for tag_name in weak_tags:
            tag_weights[tag_name] = weak_weight / len(weak_tags) if weak_tags else 0
        
        # Add strong tags with lower weight
        for tag_name in strong_tags:
            tag_weights[tag_name] = strong_weight / len(strong_tags) if strong_tags else 0
        
        if not tag_weights:
            # Fallback to random selection
            all_questions = self._get_all_questions()
            return self._select_random_questions(all_questions, question_count)
        
        return self.generate_balanced_quiz(tag_weights, question_count)
    
    def generate_progressive_quiz(self, base_tag: str, 
                                question_count: int = 10) -> List[Question]:
        """
        Generate a progressive quiz that builds from basic to advanced concepts.
        
        Args:
            base_tag: Base tag to start from
            question_count: Number of questions to generate
            
        Returns:
            List of selected questions in progressive order
        """
        base_tag_obj = self.tag_manager.get_tag_by_name(base_tag)
        if not base_tag_obj:
            return []
        
        # Get all questions from the tag hierarchy
        all_questions = []
        
        # Start with base tag
        base_questions = self.question_filter.get_questions_by_tag(base_tag)
        all_questions.extend(base_questions)
        
        # Add questions from children (more specific/specialized)
        descendants = self.tag_manager.get_descendants(base_tag_obj.id)
        for descendant in descendants:
            descendant_questions = self.question_filter.get_questions_by_tag(descendant.name)
            all_questions.extend(descendant_questions)
        
        # Remove duplicates
        seen_ids = set()
        unique_questions = []
        for question in all_questions:
            if question.id not in seen_ids:
                unique_questions.append(question)
                seen_ids.add(question.id)
        
        if not unique_questions:
            return []
        
        # Sort by creation date for progression (newer questions first)
        unique_questions.sort(key=lambda q: q.created_at, reverse=True)
        
        # Select questions maintaining progression
        if len(unique_questions) <= question_count:
            return unique_questions
        
        # Select questions with even distribution across the progression
        step = len(unique_questions) / question_count
        selected_questions = []
        
        for i in range(question_count):
            index = int(i * step)
            selected_questions.append(unique_questions[index])
        
        return selected_questions
    
    def _select_random_questions(self, questions: List[Question], 
                               count: int) -> List[Question]:
        """Select random questions from the list."""
        if len(questions) <= count:
            return questions.copy()
        
        return random.sample(questions, count)
    
    def _select_balanced_questions(self, questions: List[Question], 
                                 tag_criteria: Dict[str, Any], 
                                 count: int) -> List[Question]:
        """Select questions with balanced representation across tags."""
        # Group questions by tag
        tag_groups = {}
        for question in questions:
            for tag_id in question.tags:
                tag = self.tag_manager.get_tag_by_id(tag_id)
                if tag:
                    if tag.name not in tag_groups:
                        tag_groups[tag.name] = []
                    tag_groups[tag.name].append(question)
        
        if not tag_groups:
            return self._select_random_questions(questions, count)
        
        # Calculate target count per tag
        num_tags = len(tag_groups)
        base_count = count // num_tags
        remainder = count % num_tags
        
        selected_questions = []
        tag_names = list(tag_groups.keys())
        
        for i, tag_name in enumerate(tag_names):
            tag_questions = tag_groups[tag_name]
            target_count = base_count + (1 if i < remainder else 0)
            actual_count = min(target_count, len(tag_questions))
            
            if actual_count > 0:
                selected = random.sample(tag_questions, actual_count)
                selected_questions.extend(selected)
        
        return selected_questions
    
    def _select_hierarchical_questions(self, questions: List[Question], 
                                     tag_criteria: Dict[str, Any], 
                                     count: int) -> List[Question]:
        """Select questions maintaining hierarchical balance."""
        # Group questions by tag hierarchy level
        hierarchy_groups = {}
        
        for question in questions:
            for tag_id in question.tags:
                tag = self.tag_manager.get_tag_by_id(tag_id)
                if tag:
                    depth = tag.get_depth(self.tag_manager)
                    if depth not in hierarchy_groups:
                        hierarchy_groups[depth] = []
                    hierarchy_groups[depth].append(question)
        
        if not hierarchy_groups:
            return self._select_random_questions(questions, count)
        
        # Distribute questions across hierarchy levels
        selected_questions = []
        depths = sorted(hierarchy_groups.keys())
        
        # Weight towards deeper levels (more specific topics)
        total_weight = sum(depth + 1 for depth in depths)
        
        for depth in depths:
            weight = (depth + 1) / total_weight
            target_count = max(1, int(count * weight))
            available_questions = hierarchy_groups[depth]
            actual_count = min(target_count, len(available_questions))
            
            if actual_count > 0:
                selected = random.sample(available_questions, actual_count)
                selected_questions.extend(selected)
        
        # If we need more questions, fill randomly
        if len(selected_questions) < count:
            remaining = [q for q in questions if q not in selected_questions]
            needed = count - len(selected_questions)
            if remaining and needed > 0:
                additional = random.sample(remaining, min(needed, len(remaining)))
                selected_questions.extend(additional)
        
        return selected_questions[:count]
    
    def _select_weighted_questions(self, questions: List[Question], 
                                 tag_criteria: Dict[str, Any], 
                                 count: int) -> List[Question]:
        """Select questions based on tag weights and usage statistics."""
        # Calculate weights for each question based on tag usage
        question_weights = []
        
        for question in questions:
            weight = 1.0  # Base weight
            
            # Adjust weight based on tag usage statistics
            for tag_id in question.tags:
                tag = self.tag_manager.get_tag_by_id(tag_id)
                if tag:
                    # Lower usage = higher weight (focus on less used tags)
                    usage_factor = 1.0 / (tag.usage_count + 1)
                    weight *= usage_factor
            
            question_weights.append(weight)
        
        # Normalize weights
        total_weight = sum(question_weights)
        if total_weight == 0:
            return self._select_random_questions(questions, count)
        
        normalized_weights = [w / total_weight for w in question_weights]
        
        # Select questions based on weights
        selected_questions = []
        remaining_questions = questions.copy()
        remaining_weights = normalized_weights.copy()
        
        for _ in range(min(count, len(questions))):
            if not remaining_questions:
                break
            
            # Select based on weighted probability
            selected_index = random.choices(
                range(len(remaining_questions)), 
                weights=remaining_weights
            )[0]
            
            selected_questions.append(remaining_questions[selected_index])
            
            # Remove selected question
            remaining_questions.pop(selected_index)
            remaining_weights.pop(selected_index)
            
            # Renormalize remaining weights
            if remaining_weights:
                total_remaining = sum(remaining_weights)
                remaining_weights = [w / total_remaining for w in remaining_weights]
        
        return selected_questions
    
    def _identify_weak_tags(self, user_performance: Dict[str, Any]) -> List[str]:
        """Identify tags where user performance is weak."""
        # This would analyze user performance data
        # For now, return empty list
        return []
    
    def _identify_strong_tags(self, user_performance: Dict[str, Any]) -> List[str]:
        """Identify tags where user performance is strong."""
        # This would analyze user performance data
        # For now, return empty list
        return []
    
    def _get_all_questions(self) -> List[Question]:
        """Get all available questions (placeholder)."""
        # This would integrate with QuestionManager
        # For now, return empty list
        return []
    
    def get_quiz_generation_options(self) -> Dict[str, Any]:
        """Get available quiz generation options and strategies."""
        return {
            'strategies': [
                {
                    'name': 'random',
                    'description': 'Random selection of questions',
                    'parameters': []
                },
                {
                    'name': 'balanced',
                    'description': 'Balanced representation across tags',
                    'parameters': []
                },
                {
                    'name': 'hierarchical',
                    'description': 'Maintains hierarchical balance',
                    'parameters': []
                },
                {
                    'name': 'weighted',
                    'description': 'Weighted by tag usage statistics',
                    'parameters': []
                }
            ],
            'tag_operations': [
                {
                    'name': 'any',
                    'description': 'Questions with any of the specified tags'
                },
                {
                    'name': 'all',
                    'description': 'Questions with all specified tags'
                },
                {
                    'name': 'none',
                    'description': 'Questions without any specified tags'
                }
            ],
            'special_generators': [
                {
                    'name': 'hierarchical',
                    'description': 'Generate from tag hierarchy'
                },
                {
                    'name': 'balanced',
                    'description': 'Generate with balanced tag representation'
                },
                {
                    'name': 'adaptive',
                    'description': 'Generate based on user performance'
                },
                {
                    'name': 'progressive',
                    'description': 'Generate with chronological progression'
                }
            ]
        }
