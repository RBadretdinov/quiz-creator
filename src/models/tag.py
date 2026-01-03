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
    """Represents a tag for organizing questions with hierarchical support."""
    
    def __init__(self, name: str, description: str = "", color: str = "", 
                 tag_id: Optional[str] = None, parent_id: Optional[str] = None,
                 usage_count: int = 0, last_used: Optional[str] = None):
        """
        Initialize a Tag object.
        
        Args:
            name: Tag name (must be unique)
            description: Optional description
            color: Optional hex color code
            tag_id: Optional tag ID (generated if not provided)
            parent_id: Optional parent tag ID for hierarchy
            usage_count: Number of times tag has been used
            last_used: ISO timestamp of last usage
        """
        self.id = tag_id or str(uuid.uuid4())
        self.name = name.strip()
        self.description = description.strip()
        self.color = color.strip()
        self.parent_id = parent_id
        self.question_count = 0
        self.usage_count = usage_count
        self.last_used = last_used
        self.created_at = datetime.now().isoformat()
        self.created_by = 'system'  # TODO: Add user management
        self.children = []  # List of child tag IDs
        self.aliases = []  # Alternative names for the tag
        
        # Validate the tag
        validation_result = self.validate()
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid tag: {validation_result['errors']}")
        
        logger.debug(f"Created tag: {self.name}")
    
    def validate(self) -> Dict[str, Any]:
        """
        Validate the tag data including hierarchy constraints.
        
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
        
        # Validate hierarchy
        if self.parent_id and self.parent_id == self.id:
            errors.append("Tag cannot be its own parent")
        
        # Validate usage count
        if self.usage_count < 0:
            errors.append("Usage count cannot be negative")
        
        # Validate aliases
        for alias in self.aliases:
            if not isinstance(alias, str) or not alias.strip():
                errors.append("Aliases must be non-empty strings")
            elif len(alias.strip()) > 20:
                errors.append("Aliases cannot exceed 20 characters")
            elif not self._is_valid_tag_name(alias.strip()):
                errors.append("Aliases can only contain alphanumeric characters, hyphens, and underscores")
        
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
            'parent_id': self.parent_id,
            'question_count': self.question_count,
            'usage_count': self.usage_count,
            'last_used': self.last_used,
            'created_at': self.created_at,
            'created_by': self.created_by,
            'children': self.children,
            'aliases': self.aliases
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
        tag.parent_id = data.get('parent_id')
        tag.question_count = data.get('question_count', 0)
        tag.usage_count = data.get('usage_count', 0)
        tag.last_used = data.get('last_used')
        tag.created_at = data.get('created_at', datetime.now().isoformat())
        tag.created_by = data.get('created_by', 'system')
        tag.children = data.get('children', [])
        tag.aliases = data.get('aliases', [])
        
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
    
    def add_child(self, child_id: str) -> None:
        """
        Add a child tag ID to this tag.
        
        Args:
            child_id: ID of the child tag
        """
        if child_id not in self.children:
            self.children.append(child_id)
            logger.debug(f"Added child {child_id} to tag {self.name}")
    
    def remove_child(self, child_id: str) -> None:
        """
        Remove a child tag ID from this tag.
        
        Args:
            child_id: ID of the child tag to remove
        """
        if child_id in self.children:
            self.children.remove(child_id)
            logger.debug(f"Removed child {child_id} from tag {self.name}")
    
    def has_children(self) -> bool:
        """
        Check if this tag has children.
        
        Returns:
            True if tag has children, False otherwise
        """
        return len(self.children) > 0
    
    def is_root(self) -> bool:
        """
        Check if this tag is a root tag (no parent).
        
        Returns:
            True if tag has no parent, False otherwise
        """
        return self.parent_id is None
    
    def is_leaf(self) -> bool:
        """
        Check if this tag is a leaf tag (no children).
        
        Returns:
            True if tag has no children, False otherwise
        """
        return len(self.children) == 0
    
    def add_alias(self, alias: str) -> None:
        """
        Add an alias for this tag.
        
        Args:
            alias: Alternative name for the tag
        """
        alias = alias.strip()
        if alias and alias not in self.aliases:
            self.aliases.append(alias)
            logger.debug(f"Added alias '{alias}' to tag {self.name}")
    
    def remove_alias(self, alias: str) -> None:
        """
        Remove an alias from this tag.
        
        Args:
            alias: Alias to remove
        """
        if alias in self.aliases:
            self.aliases.remove(alias)
            logger.debug(f"Removed alias '{alias}' from tag {self.name}")
    
    def increment_usage(self) -> None:
        """Increment the usage count and update last used timestamp."""
        self.usage_count += 1
        self.last_used = datetime.now().isoformat()
        logger.debug(f"Incremented usage count for tag: {self.name}")
    
    def get_full_path(self, tag_manager=None) -> str:
        """
        Get the full hierarchical path of this tag.
        
        Args:
            tag_manager: Optional TagManager to resolve parent names
            
        Returns:
            Full path string (e.g., "Science > Physics > Mechanics")
        """
        if not tag_manager or self.is_root():
            return self.name
        
        try:
            parent = tag_manager.get_tag_by_id(self.parent_id)
            if parent:
                return f"{parent.get_full_path(tag_manager)} > {self.name}"
        except:
            pass
        
        return self.name
    
    def get_depth(self, tag_manager=None) -> int:
        """
        Get the depth of this tag in the hierarchy.
        
        Args:
            tag_manager: Optional TagManager to resolve parent depth
            
        Returns:
            Depth level (0 for root tags)
        """
        if self.is_root():
            return 0
        
        if tag_manager:
            try:
                parent = tag_manager.get_tag_by_id(self.parent_id)
                if parent:
                    return parent.get_depth(tag_manager) + 1
            except:
                pass
        
        return 1  # Default depth if parent resolution fails
    
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
