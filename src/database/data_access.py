"""
SQLite Data Access Layer

This module provides data access functions for SQLite database operations
with prepared statements and optimized queries.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .connection import DatabaseConnectionManager

logger = logging.getLogger(__name__)

class QuestionDataAccess:
    """Data access layer for questions in SQLite."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize question data access."""
        self.db_manager = db_manager
    
    def create_question(self, question_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new question in the database.
        
        Args:
            question_data: Question data dictionary
            
        Returns:
            Question ID if successful, None otherwise
        """
        try:
            query = """
                INSERT INTO questions 
                (id, question_text, question_type, answers, tags, usage_count, 
                 quality_score, created_at, last_modified, created_by, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                question_data.get('id'),
                question_data.get('question_text'),
                question_data.get('question_type'),
                json.dumps(question_data.get('answers', [])),
                json.dumps(question_data.get('tags', [])),
                question_data.get('usage_count', 0),
                question_data.get('quality_score', 0.0),
                question_data.get('created_at', datetime.now().isoformat()),
                question_data.get('last_modified', datetime.now().isoformat()),
                question_data.get('created_by'),
                question_data.get('version', 1)
            )
            
            cursor = self.db_manager.execute_with_retry(query, params)
            if cursor:
                logger.info(f"Created question: {question_data.get('id')}")
                return question_data.get('id')
            return None
            
        except Exception as e:
            logger.error(f"Failed to create question: {e}")
            return None
    
    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a question by ID.
        
        Args:
            question_id: Question ID
            
        Returns:
            Question data or None if not found
        """
        try:
            query = "SELECT * FROM questions WHERE id = ?"
            row = self.db_manager.fetch_one(query, (question_id,))
            
            if row:
                return self._row_to_question(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get question by ID: {e}")
            return None
    
    def get_all_questions(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all questions with optional pagination.
        
        Args:
            limit: Maximum number of questions to return
            offset: Number of questions to skip
            
        Returns:
            List of question data
        """
        try:
            query = "SELECT * FROM questions ORDER BY created_at DESC"
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            rows = self.db_manager.fetch_all(query)
            return [self._row_to_question(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get all questions: {e}")
            return []
    
    def update_question(self, question_id: str, question_data: Dict[str, Any]) -> bool:
        """
        Update a question in the database.
        
        Args:
            question_id: Question ID
            question_data: Updated question data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE questions SET 
                question_text = ?, question_type = ?, answers = ?, tags = ?,
                usage_count = ?, quality_score = ?, last_modified = ?, version = ?
                WHERE id = ?
            """
            
            params = (
                question_data.get('question_text'),
                question_data.get('question_type'),
                json.dumps(question_data.get('answers', [])),
                json.dumps(question_data.get('tags', [])),
                question_data.get('usage_count', 0),
                question_data.get('quality_score', 0.0),
                datetime.now().isoformat(),
                question_data.get('version', 1),
                question_id
            )
            
            cursor = self.db_manager.execute_with_retry(query, params)
            if cursor and cursor.rowcount > 0:
                logger.info(f"Updated question: {question_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update question: {e}")
            return False
    
    def delete_question(self, question_id: str) -> bool:
        """
        Delete a question from the database.
        
        Args:
            question_id: Question ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = "DELETE FROM questions WHERE id = ?"
            cursor = self.db_manager.execute_with_retry(query, (question_id,))
            
            if cursor and cursor.rowcount > 0:
                logger.info(f"Deleted question: {question_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete question: {e}")
            return False
    
    def search_questions(self, search_term: str, question_type: str = None, 
                        tags: List[str] = None) -> List[Dict[str, Any]]:
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
            query = "SELECT * FROM questions WHERE question_text LIKE ?"
            params = [f"%{search_term}%"]
            
            if question_type:
                query += " AND question_type = ?"
                params.append(question_type)
            
            if tags:
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
            
            query += " ORDER BY created_at DESC"
            
            rows = self.db_manager.fetch_all(query, tuple(params))
            return [self._row_to_question(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to search questions: {e}")
            return []
    
    def get_questions_by_type(self, question_type: str) -> List[Dict[str, Any]]:
        """
        Get questions by type.
        
        Args:
            question_type: Type of questions to get
            
        Returns:
            List of questions
        """
        try:
            query = "SELECT * FROM questions WHERE question_type = ? ORDER BY created_at DESC"
            rows = self.db_manager.fetch_all(query, (question_type,))
            return [self._row_to_question(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get questions by type: {e}")
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
            query = "UPDATE questions SET usage_count = usage_count + 1 WHERE id = ?"
            cursor = self.db_manager.execute_with_retry(query, (question_id,))
            
            if cursor:
                logger.debug(f"Incremented usage count for question: {question_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to increment usage count: {e}")
            return False
    
    def get_question_statistics(self) -> Dict[str, Any]:
        """
        Get question statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            stats = {}
            
            # Total questions
            query = "SELECT COUNT(*) as count FROM questions"
            result = self.db_manager.fetch_one(query)
            stats['total_questions'] = result['count'] if result else 0
            
            # Questions by type
            query = "SELECT question_type, COUNT(*) as count FROM questions GROUP BY question_type"
            rows = self.db_manager.fetch_all(query)
            stats['by_type'] = {row['question_type']: row['count'] for row in rows}
            
            # Most used questions
            query = "SELECT id, question_text, usage_count FROM questions ORDER BY usage_count DESC LIMIT 10"
            rows = self.db_manager.fetch_all(query)
            stats['most_used'] = [{'id': row['id'], 'text': row['question_text'][:50], 'usage': row['usage_count']} for row in rows]
            
            # Average quality score
            query = "SELECT AVG(quality_score) as avg_quality FROM questions"
            result = self.db_manager.fetch_one(query)
            stats['average_quality'] = round(result['avg_quality'], 2) if result and result['avg_quality'] else 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get question statistics: {e}")
            return {}
    
    def _row_to_question(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database row to question dictionary."""
        return {
            'id': row['id'],
            'question_text': row['question_text'],
            'question_type': row['question_type'],
            'answers': json.loads(row['answers']),
            'tags': json.loads(row['tags']),
            'usage_count': row['usage_count'],
            'quality_score': row['quality_score'],
            'created_at': row['created_at'],
            'last_modified': row['last_modified'],
            'created_by': row['created_by'],
            'version': row['version']
        }


class TagDataAccess:
    """Data access layer for tags in SQLite."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """Initialize tag data access."""
        self.db_manager = db_manager
    
    def create_tag(self, tag_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a new tag in the database.
        
        Args:
            tag_data: Tag data dictionary
            
        Returns:
            Tag ID if successful, None otherwise
        """
        try:
            query = """
                INSERT INTO tags 
                (id, name, description, color, parent_id, usage_count, last_used,
                 children, aliases, question_count, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                tag_data.get('id'),
                tag_data.get('name'),
                tag_data.get('description'),
                tag_data.get('color'),
                tag_data.get('parent_id'),
                tag_data.get('usage_count', 0),
                tag_data.get('last_used'),
                json.dumps(tag_data.get('children', [])),
                json.dumps(tag_data.get('aliases', [])),
                tag_data.get('question_count', 0),
                tag_data.get('created_at', datetime.now().isoformat()),
                tag_data.get('created_by')
            )
            
            cursor = self.db_manager.execute_with_retry(query, params)
            if cursor:
                logger.info(f"Created tag: {tag_data.get('id')}")
                return tag_data.get('id')
            return None
            
        except Exception as e:
            logger.error(f"Failed to create tag: {e}")
            return None
    
    def get_tag_by_id(self, tag_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a tag by ID.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            Tag data or None if not found
        """
        try:
            query = "SELECT * FROM tags WHERE id = ?"
            row = self.db_manager.fetch_one(query, (tag_id,))
            
            if row:
                return self._row_to_tag(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get tag by ID: {e}")
            return None
    
    def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a tag by name.
        
        Args:
            name: Tag name
            
        Returns:
            Tag data or None if not found
        """
        try:
            query = "SELECT * FROM tags WHERE name = ?"
            row = self.db_manager.fetch_one(query, (name,))
            
            if row:
                return self._row_to_tag(row)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get tag by name: {e}")
            return None
    
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """
        Get all tags.
        
        Returns:
            List of tag data
        """
        try:
            query = "SELECT * FROM tags ORDER BY name"
            rows = self.db_manager.fetch_all(query)
            return [self._row_to_tag(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get all tags: {e}")
            return []
    
    def update_tag(self, tag_id: str, tag_data: Dict[str, Any]) -> bool:
        """
        Update a tag in the database.
        
        Args:
            tag_id: Tag ID
            tag_data: Updated tag data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE tags SET 
                name = ?, description = ?, color = ?, parent_id = ?, usage_count = ?,
                last_used = ?, children = ?, aliases = ?, question_count = ?
                WHERE id = ?
            """
            
            params = (
                tag_data.get('name'),
                tag_data.get('description'),
                tag_data.get('color'),
                tag_data.get('parent_id'),
                tag_data.get('usage_count', 0),
                tag_data.get('last_used'),
                json.dumps(tag_data.get('children', [])),
                json.dumps(tag_data.get('aliases', [])),
                tag_data.get('question_count', 0),
                tag_id
            )
            
            cursor = self.db_manager.execute_with_retry(query, params)
            if cursor and cursor.rowcount > 0:
                logger.info(f"Updated tag: {tag_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update tag: {e}")
            return False
    
    def delete_tag(self, tag_id: str) -> bool:
        """
        Delete a tag from the database.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = "DELETE FROM tags WHERE id = ?"
            cursor = self.db_manager.execute_with_retry(query, (tag_id,))
            
            if cursor and cursor.rowcount > 0:
                logger.info(f"Deleted tag: {tag_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete tag: {e}")
            return False
    
    def search_tags(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search tags by name or description.
        
        Args:
            search_term: Text to search for
            
        Returns:
            List of matching tags
        """
        try:
            query = """
                SELECT * FROM tags 
                WHERE name LIKE ? OR description LIKE ? OR aliases LIKE ?
                ORDER BY name
            """
            search_pattern = f"%{search_term}%"
            rows = self.db_manager.fetch_all(query, (search_pattern, search_pattern, search_pattern))
            return [self._row_to_tag(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to search tags: {e}")
            return []
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Get tag statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            stats = {}
            
            # Total tags
            query = "SELECT COUNT(*) as count FROM tags"
            result = self.db_manager.fetch_one(query)
            stats['total_tags'] = result['count'] if result else 0
            
            # Most used tags
            query = "SELECT name, usage_count FROM tags ORDER BY usage_count DESC LIMIT 10"
            rows = self.db_manager.fetch_all(query)
            stats['most_used'] = [{'name': row['name'], 'usage': row['usage_count']} for row in rows]
            
            # Tags with most questions
            query = "SELECT name, question_count FROM tags ORDER BY question_count DESC LIMIT 10"
            rows = self.db_manager.fetch_all(query)
            stats['most_questions'] = [{'name': row['name'], 'count': row['question_count']} for row in rows]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get tag statistics: {e}")
            return {}
    
    def _row_to_tag(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert database row to tag dictionary."""
        return {
            'id': row['id'],
            'name': row['name'],
            'description': row['description'],
            'color': row['color'],
            'parent_id': row['parent_id'],
            'usage_count': row['usage_count'],
            'last_used': row['last_used'],
            'children': json.loads(row['children']) if row['children'] else [],
            'aliases': json.loads(row['aliases']) if row['aliases'] else [],
            'question_count': row['question_count'],
            'created_at': row['created_at'],
            'created_by': row['created_by']
        }
