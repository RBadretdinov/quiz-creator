"""
Tag Model

This module defines the Tag data model with validation and serialization.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)

class Tag:
    """Represents a tag for organizing questions."""
    
    def __init__(self, name: str, description: str = "", color: str = "", 
                 tag_id: Optional[str] = None):
        """
        Initialize a Tag object.
        
        Args:
            name: Tag name (must be unique)
            description: Optional description
            color: Optional hex color code
            tag_id: Optional tag ID (generated if not provided)
        """
        self.id = tag_id or str(uuid.uuid4())
        self.name = name.strip()
        self.description = description.strip()
        self.color = color.strip()
        self.question_count = 0
        self.created_at = datetime.now().isoformat()
        self.created_by = 'system'  # TODO: Add user management
        
        # Validate the tag
        validation_result = self.validate()
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid tag: {validation_result['errors']}")
        
        logger.debug(f"Created tag: {self.name}")
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the tag data.
        
        Returns:
            Dictionary with validation result and errors
        """
        errors = []
        
        # Validate name
        if not self.name:
            errors.append("Tag name cannot be empty")
        elif len(self.name) > 20:
            errors.append("Tag name cannot exceed 20 characters")
        elif not self._is_valid_tag_name(self.name):
            errors.append("Tag name can only contain alphanumeric characters, hyphens, and underscores")
        
        # Validate description
        if len(self.description) > 100:
            errors.append("Description cannot exceed 100 characters")
        
        # Validate color
        if self.color and not self._is_valid_color(self.color):
            errors.append("Color must be a valid hex color code (e.g., #FF0000)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _is_valid_tag_name(self, name: str) -> bool:
        """Check if tag name contains only valid characters."""
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if color is a valid hex color code."""
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tag to dictionary for serialization.
        
        Returns:
            Dictionary representation of the tag
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'question_count': self.question_count,
            'created_at': self.created_at,
            'created_by': self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Tag':
        """
        Create Tag object from dictionary.
        
        Args:
            data: Dictionary containing tag data
            
        Returns:
            Tag object
        """
        tag = cls.__new__(cls)
        tag.id = data.get('id', str(uuid.uuid4()))
        tag.name = data['name']
        tag.description = data.get('description', '')
        tag.color = data.get('color', '')
        tag.question_count = data.get('question_count', 0)
        tag.created_at = data.get('created_at', datetime.now().isoformat())
        tag.created_by = data.get('created_by', 'system')
        
        return tag
    
    def update(self, **updates) -> None:
        """
        Update tag fields.
        
        Args:
            **updates: Fields to update
        """
        for key, value in updates.items():
            if hasattr(self, key) and key != 'id':  # Don't allow ID changes
                setattr(self, key, value.strip() if isinstance(value, str) else value)
        
        # Re-validate after update
        validation_result = self.validate()
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid update: {validation_result['errors']}")
        
        logger.debug(f"Updated tag: {self.name}")
    
    def increment_question_count(self) -> None:
        """Increment the question count for this tag."""
        self.question_count += 1
        logger.debug(f"Incremented question count for tag: {self.name}")
    
    def decrement_question_count(self) -> None:
        """Decrement the question count for this tag."""
        self.question_count = max(0, self.question_count - 1)
        logger.debug(f"Decremented question count for tag: {self.name}")
    
    def set_question_count(self, count: int) -> None:
        """
        Set the question count for this tag.
        
        Args:
            count: New question count
        """
        self.question_count = max(0, count)
        logger.debug(f"Set question count for tag {self.name}: {self.question_count}")
    
    def is_unused(self) -> bool:
        """
        Check if the tag is unused.
        
        Returns:
            True if tag has no questions, False otherwise
        """
        return self.question_count == 0
    
    def __eq__(self, other) -> bool:
        """Check equality with another tag."""
        if not isinstance(other, Tag):
            return False
        
        return (self.id == other.id and 
                self.name == other.name and
                self.description == other.description and
                self.color == other.color)
    
    def __str__(self) -> str:
        """String representation of the tag."""
        return f"Tag(name='{self.name}', count={self.question_count})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Tag(id='{self.id}', name='{self.name}', "
                f"description='{self.description}', color='{self.color}', "
                f"question_count={self.question_count})")
    
    def __hash__(self) -> int:
        """Hash function for use in sets and dictionaries."""
        return hash(self.id)
