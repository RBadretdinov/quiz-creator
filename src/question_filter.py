"""
Question Filter Module

This module provides advanced question filtering capabilities based on tags,
question types, and other criteria with support for complex queries.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import re
import logging

from models.question import Question
from models.tag import Tag
from tag_manager import TagManager

logger = logging.getLogger(__name__)

class QuestionFilter:
    """Advanced question filtering with tag-based and multi-criteria support."""
    
    def __init__(self, tag_manager: TagManager):
        """Initialize the question filter."""
        self.tag_manager = tag_manager
        self.logger = logging.getLogger(__name__)
    
    def filter_questions(self, questions: List[Question], 
                        filters: Dict[str, Any]) -> List[Question]:
        """
        Filter questions based on multiple criteria.
        
        Args:
            questions: List of questions to filter
            filters: Dictionary of filter criteria
            
        Returns:
            Filtered list of questions
        """
        filtered_questions = questions.copy()
        
        # Apply tag filters
        if 'tags' in filters:
            filtered_questions = self._filter_by_tags(filtered_questions, filters['tags'])
        
        # Apply question type filters
        if 'question_types' in filters:
            filtered_questions = self._filter_by_question_types(filtered_questions, filters['question_types'])
        
        # Apply text search
        if 'search_text' in filters:
            filtered_questions = self._filter_by_text(filtered_questions, filters['search_text'])
        
        
        # Apply date filters
        if 'date_range' in filters:
            filtered_questions = self._filter_by_date_range(filtered_questions, filters['date_range'])
        
        # Apply usage filters
        if 'usage_count' in filters:
            filtered_questions = self._filter_by_usage_count(filtered_questions, filters['usage_count'])
        
        # Apply answer count filters
        if 'answer_count' in filters:
            filtered_questions = self._filter_by_answer_count(filtered_questions, filters['answer_count'])
        
        return filtered_questions
    
    def _filter_by_tags(self, questions: List[Question], tag_criteria: Dict[str, Any]) -> List[Question]:
        """Filter questions by tag criteria."""
        tag_operation = tag_criteria.get('operation', 'any')  # 'any', 'all', 'none'
        tag_names = tag_criteria.get('tags', [])
        include_children = tag_criteria.get('include_children', False)
        
        if not tag_names:
            return questions
        
        # Resolve tag IDs
        tag_ids = set()
        for tag_name in tag_names:
            tag = self.tag_manager.get_tag_by_name(tag_name)
            if tag:
                tag_ids.add(tag.id)
                
                # Include children if requested
                if include_children:
                    descendants = self.tag_manager.get_descendants(tag.id)
                    for descendant in descendants:
                        tag_ids.add(descendant.id)
        
        if not tag_ids:
            return questions
        
        filtered_questions = []
        
        for question in questions:
            question_tag_ids = set(question.tags)
            
            if tag_operation == 'any':
                # Question must have at least one of the specified tags
                if question_tag_ids.intersection(tag_ids):
                    filtered_questions.append(question)
            
            elif tag_operation == 'all':
                # Question must have all specified tags
                if tag_ids.issubset(question_tag_ids):
                    filtered_questions.append(question)
            
            elif tag_operation == 'none':
                # Question must not have any of the specified tags
                if not question_tag_ids.intersection(tag_ids):
                    filtered_questions.append(question)
        
        return filtered_questions
    
    def _filter_by_question_types(self, questions: List[Question], 
                                 question_types: List[str]) -> List[Question]:
        """Filter questions by question types."""
        if not question_types:
            return questions
        
        return [q for q in questions if q.question_type in question_types]
    
    def _filter_by_text(self, questions: List[Question], 
                       search_text: str) -> List[Question]:
        """Filter questions by text content."""
        if not search_text:
            return questions
        
        search_text = search_text.lower()
        filtered_questions = []
        
        for question in questions:
            # Search in question text
            if search_text in question.question_text.lower():
                filtered_questions.append(question)
                continue
            
            # Search in answer options
            for answer in question.answers:
                if search_text in answer['text'].lower():
                    filtered_questions.append(question)
                    break
        
        return filtered_questions
    
    
    def _filter_by_date_range(self, questions: List[Question], 
                             date_range: Dict[str, Any]) -> List[Question]:
        """Filter questions by creation date range."""
        start_date = date_range.get('start')
        end_date = date_range.get('end')
        
        if not start_date and not end_date:
            return questions
        
        filtered_questions = []
        
        for question in questions:
            try:
                question_date = datetime.fromisoformat(question.created_at)
                
                if start_date and question_date < start_date:
                    continue
                
                if end_date and question_date > end_date:
                    continue
                
                filtered_questions.append(question)
                
            except (ValueError, TypeError):
                # Skip questions with invalid dates
                continue
        
        return filtered_questions
    
    def _filter_by_usage_count(self, questions: List[Question], 
                              usage_criteria: Dict[str, Any]) -> List[Question]:
        """Filter questions by usage count."""
        min_usage = usage_criteria.get('min', 0)
        max_usage = usage_criteria.get('max', float('inf'))
        
        return [q for q in questions 
                if min_usage <= getattr(q, 'usage_count', 0) <= max_usage]
    
    def _filter_by_answer_count(self, questions: List[Question], 
                               answer_criteria: Dict[str, Any]) -> List[Question]:
        """Filter questions by number of answer options."""
        min_answers = answer_criteria.get('min', 2)
        max_answers = answer_criteria.get('max', 10)
        
        return [q for q in questions 
                if min_answers <= len(q.answers) <= max_answers]
    
    def get_questions_by_tag(self, tag_name: str, 
                           include_children: bool = False) -> List[Question]:
        """
        Get questions associated with a specific tag.
        
        Args:
            tag_name: Name of the tag
            include_children: Whether to include questions from child tags
            
        Returns:
            List of questions (placeholder - would need QuestionManager integration)
        """
        # This would need to be implemented with QuestionManager integration
        # For now, return empty list
        return []
    
    def get_questions_by_tag_hierarchy(self, root_tag_name: str) -> Dict[str, List[Question]]:
        """
        Get questions organized by tag hierarchy.
        
        Args:
            root_tag_name: Name of the root tag
            
        Returns:
            Dictionary mapping tag names to question lists
        """
        root_tag = self.tag_manager.get_tag_by_name(root_tag_name)
        if not root_tag:
            return {}
        
        result = {}
        
        # Get questions for root tag
        root_questions = self.get_questions_by_tag(root_tag_name)
        if root_questions:
            result[root_tag_name] = root_questions
        
        # Get questions for all descendants
        descendants = self.tag_manager.get_descendants(root_tag.id)
        for descendant in descendants:
            descendant_questions = self.get_questions_by_tag(descendant.name)
            if descendant_questions:
                result[descendant.name] = descendant_questions
        
        return result
    
    def search_questions_advanced(self, questions: List[Question], 
                                query: str) -> List[Question]:
        """
        Advanced search with support for complex queries.
        
        Args:
            questions: List of questions to search
            query: Search query with support for operators
            
        Returns:
            List of matching questions
        """
        # Parse query for operators
        if ' AND ' in query.upper():
            return self._search_with_and(questions, query)
        elif ' OR ' in query.upper():
            return self._search_with_or(questions, query)
        elif ' NOT ' in query.upper():
            return self._search_with_not(questions, query)
        else:
            return self._filter_by_text(questions, query)
    
    def _search_with_and(self, questions: List[Question], query: str) -> List[Question]:
        """Search with AND operator."""
        terms = [term.strip() for term in query.upper().split(' AND ')]
        results = questions.copy()
        
        for term in terms:
            results = self._filter_by_text(results, term)
        
        return results
    
    def _search_with_or(self, questions: List[Question], query: str) -> List[Question]:
        """Search with OR operator."""
        terms = [term.strip() for term in query.upper().split(' OR ')]
        results = []
        seen_ids = set()
        
        for term in terms:
            term_results = self._filter_by_text(questions, term)
            for question in term_results:
                if question.id not in seen_ids:
                    results.append(question)
                    seen_ids.add(question.id)
        
        return results
    
    def _search_with_not(self, questions: List[Question], query: str) -> List[Question]:
        """Search with NOT operator."""
        parts = query.upper().split(' NOT ')
        if len(parts) != 2:
            return self._filter_by_text(questions, query)
        
        include_term = parts[0].strip()
        exclude_term = parts[1].strip()
        
        # Get questions matching include term
        include_results = self._filter_by_text(questions, include_term)
        
        # Remove questions matching exclude term
        exclude_results = self._filter_by_text(include_results, exclude_term)
        exclude_ids = {q.id for q in exclude_results}
        
        return [q for q in include_results if q.id not in exclude_ids]
    
    def get_filter_suggestions(self, questions: List[Question]) -> Dict[str, Any]:
        """
        Get suggestions for available filters based on question data.
        
        Args:
            questions: List of questions to analyze
            
        Returns:
            Dictionary of filter suggestions
        """
        suggestions = {
            'available_tags': set(),
            'question_types': set(),
            'date_range': {'earliest': None, 'latest': None},
            'usage_range': {'min': 0, 'max': 0},
            'answer_count_range': {'min': 0, 'max': 0}
        }
        
        if not questions:
            return suggestions
        
        for question in questions:
            # Collect tags
            for tag_id in question.tags:
                tag = self.tag_manager.get_tag_by_id(tag_id)
                if tag:
                    suggestions['available_tags'].add(tag.name)
            
            # Collect question types
            suggestions['question_types'].add(question.question_type)
            
            
            # Collect dates
            try:
                question_date = datetime.fromisoformat(question.created_at)
                if not suggestions['date_range']['earliest'] or question_date < suggestions['date_range']['earliest']:
                    suggestions['date_range']['earliest'] = question_date
                if not suggestions['date_range']['latest'] or question_date > suggestions['date_range']['latest']:
                    suggestions['date_range']['latest'] = question_date
            except:
                pass
            
            # Collect usage counts
            usage_count = getattr(question, 'usage_count', 0)
            suggestions['usage_range']['min'] = min(suggestions['usage_range']['min'], usage_count)
            suggestions['usage_range']['max'] = max(suggestions['usage_range']['max'], usage_count)
            
            # Collect answer counts
            answer_count = len(question.answers)
            suggestions['answer_count_range']['min'] = min(suggestions['answer_count_range']['min'], answer_count)
            suggestions['answer_count_range']['max'] = max(suggestions['answer_count_range']['max'], answer_count)
        
        # Convert sets to lists for JSON serialization
        suggestions['available_tags'] = sorted(list(suggestions['available_tags']))
        suggestions['question_types'] = sorted(list(suggestions['question_types']))
        
        return suggestions
    
    def create_filter_from_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a standardized filter from user criteria.
        
        Args:
            criteria: User-provided filter criteria
            
        Returns:
            Standardized filter dictionary
        """
        filter_dict = {}
        
        # Handle tag filters
        if 'tags' in criteria:
            if isinstance(criteria['tags'], str):
                # Single tag
                filter_dict['tags'] = {
                    'operation': 'any',
                    'tags': [criteria['tags']],
                    'include_children': criteria.get('include_children', False)
                }
            elif isinstance(criteria['tags'], list):
                # Multiple tags
                filter_dict['tags'] = {
                    'operation': criteria.get('tag_operation', 'any'),
                    'tags': criteria['tags'],
                    'include_children': criteria.get('include_children', False)
                }
        
        # Handle question type filters
        if 'question_types' in criteria:
            if isinstance(criteria['question_types'], str):
                filter_dict['question_types'] = [criteria['question_types']]
            else:
                filter_dict['question_types'] = criteria['question_types']
        
        # Handle text search
        if 'search_text' in criteria:
            filter_dict['search_text'] = criteria['search_text']
        
        
        # Handle date range filters
        if 'date_range' in criteria:
            filter_dict['date_range'] = criteria['date_range']
        
        # Handle usage count filters
        if 'usage_count' in criteria:
            filter_dict['usage_count'] = criteria['usage_count']
        
        # Handle answer count filters
        if 'answer_count' in criteria:
            filter_dict['answer_count'] = criteria['answer_count']
        
        return filter_dict
