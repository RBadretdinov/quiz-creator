"""
Tag Manager Module

This module handles tag creation, management, and organization of questions
with support for hierarchical tag structures and tag-based filtering.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TagManager:
    """Manages tag operations and question organization."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the tag manager."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tags_file = self.data_dir / "tags.json"
        self.tags: List[Dict] = []
        self._load_tags()
        logger.info("Tag manager initialized")
    
    def create_tag(self, name: str, description: str = "", color: str = "") -> Dict:
        """
        Create a new tag.
        
        Args:
            name: Tag name (must be unique)
            description: Optional description
            color: Optional hex color code
            
        Returns:
            Created tag dictionary
        """
        # Validate tag name
        if not name or not name.strip():
            raise ValueError("Tag name cannot be empty")
        
        name = name.strip()
        
        # Check for uniqueness
        if self.get_tag_by_name(name):
            raise ValueError(f"Tag '{name}' already exists")
        
        # Validate name format
        if not self._is_valid_tag_name(name):
            raise ValueError("Tag name can only contain alphanumeric characters, hyphens, and underscores")
        
        # Create tag object
        tag = {
            'id': str(uuid.uuid4()),
            'name': name,
            'description': description.strip(),
            'color': color.strip(),
            'question_count': 0,
            'created_at': datetime.now().isoformat(),
            'created_by': 'system'  # TODO: Add user management
        }
        
        self.tags.append(tag)
        self._save_tags()
        
        logger.info(f"Created tag: {name}")
        return tag
    
    def get_tag(self, tag_id: str) -> Optional[Dict]:
        """Get a tag by its ID."""
        for tag in self.tags:
            if tag['id'] == tag_id:
                return tag
        return None
    
    def get_tag_by_name(self, name: str) -> Optional[Dict]:
        """Get a tag by its name."""
        for tag in self.tags:
            if tag['name'].lower() == name.lower():
                return tag
        return None
    
    def get_all_tags(self) -> List[Dict]:
        """Get all tags sorted by name."""
        return sorted(self.tags, key=lambda x: x['name'].lower())
    
    def update_tag(self, tag_id: str, **updates) -> bool:
        """
        Update an existing tag.
        
        Args:
            tag_id: ID of tag to update
            **updates: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        tag = self.get_tag(tag_id)
        if not tag:
            return False
        
        # Validate name uniqueness if name is being updated
        if 'name' in updates:
            new_name = updates['name'].strip()
            if not new_name:
                raise ValueError("Tag name cannot be empty")
            
            existing_tag = self.get_tag_by_name(new_name)
            if existing_tag and existing_tag['id'] != tag_id:
                raise ValueError(f"Tag '{new_name}' already exists")
            
            if not self._is_valid_tag_name(new_name):
                raise ValueError("Tag name can only contain alphanumeric characters, hyphens, and underscores")
        
        # Apply updates
        for key, value in updates.items():
            if key in tag and key != 'id':  # Don't allow ID changes
                tag[key] = value.strip() if isinstance(value, str) else value
        
        self._save_tags()
        logger.info(f"Updated tag: {tag_id}")
        return True
    
    def delete_tag(self, tag_id: str) -> bool:
        """
        Delete a tag and handle question reassignment.
        
        Args:
            tag_id: ID of tag to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        tag = self.get_tag(tag_id)
        if not tag:
            return False
        
        # Check if tag is in use
        if tag['question_count'] > 0:
            raise ValueError(f"Cannot delete tag '{tag['name']}' - it is used by {tag['question_count']} questions")
        
        # Remove tag
        self.tags = [t for t in self.tags if t['id'] != tag_id]
        self._save_tags()
        
        logger.info(f"Deleted tag: {tag['name']}")
        return True
    
    def search_tags(self, search_term: str) -> List[Dict]:
        """Search tags by name or description."""
        search_term = search_term.lower()
        results = []
        
        for tag in self.tags:
            if (search_term in tag['name'].lower() or 
                search_term in tag.get('description', '').lower()):
                results.append(tag)
        
        return sorted(results, key=lambda x: x['name'].lower())
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """Get statistics about tag usage."""
        if not self.tags:
            return {
                'total_tags': 0,
                'most_used_tags': [],
                'least_used_tags': [],
                'unused_tags': []
            }
        
        # Sort tags by usage
        sorted_tags = sorted(self.tags, key=lambda x: x['question_count'], reverse=True)
        
        most_used = sorted_tags[:5] if len(sorted_tags) >= 5 else sorted_tags
        least_used = sorted_tags[-5:] if len(sorted_tags) >= 5 else sorted_tags
        unused = [tag for tag in self.tags if tag['question_count'] == 0]
        
        return {
            'total_tags': len(self.tags),
            'most_used_tags': most_used,
            'least_used_tags': least_used,
            'unused_tags': unused,
            'average_usage': sum(tag['question_count'] for tag in self.tags) / len(self.tags)
        }
    
    def update_question_count(self, tag_name: str, delta: int):
        """
        Update the question count for a tag.
        
        Args:
            tag_name: Name of the tag
            delta: Change in question count (+1 or -1)
        """
        tag = self.get_tag_by_name(tag_name)
        if tag:
            tag['question_count'] = max(0, tag['question_count'] + delta)
            self._save_tags()
            logger.debug(f"Updated question count for tag '{tag_name}': {tag['question_count']}")
    
    def validate_tag_name(self, name: str) -> Dict[str, Any]:
        """
        Validate a tag name.
        
        Args:
            name: Tag name to validate
            
        Returns:
            Validation result with is_valid flag and errors
        """
        errors = []
        
        if not name or not name.strip():
            errors.append("Tag name cannot be empty")
        elif len(name.strip()) > 20:
            errors.append("Tag name cannot exceed 20 characters")
        elif not self._is_valid_tag_name(name):
            errors.append("Tag name can only contain alphanumeric characters, hyphens, and underscores")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _is_valid_tag_name(self, name: str) -> bool:
        """Check if tag name contains only valid characters."""
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', name))
    
    def _load_tags(self):
        """Load tags from JSON file."""
        if self.tags_file.exists():
            try:
                with open(self.tags_file, 'r', encoding='utf-8') as f:
                    self.tags = json.load(f)
                logger.info(f"Loaded {len(self.tags)} tags from {self.tags_file}")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading tags: {e}")
                self.tags = []
        else:
            self.tags = []
            logger.info("No tags file found, starting with empty tag collection")
    
    def _save_tags(self):
        """Save tags to JSON file."""
        try:
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump(self.tags, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self.tags)} tags to {self.tags_file}")
        except IOError as e:
            logger.error(f"Error saving tags: {e}")
            raise
