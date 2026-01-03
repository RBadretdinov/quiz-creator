"""
Database-Integrated Tag Manager

This module provides a database-integrated tag manager that uses SQLite
for persistent storage while maintaining compatibility with the existing interface.
"""

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from database_manager import DatabaseManager
from models.tag import Tag

logger = logging.getLogger(__name__)

class TagManagerDB:
    """Database-integrated tag manager."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the database-integrated tag manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        logger.info("Database-integrated tag manager initialized")
    
    def create_tag(self, name: str, description: str = None, color: str = None, 
                   parent_id: str = None, aliases: List[str] = None) -> Optional[str]:
        """
        Create a new tag.
        
        Args:
            name: Tag name
            description: Tag description
            color: Tag color
            parent_id: Parent tag ID for hierarchical tags
            aliases: List of tag aliases
            
        Returns:
            Tag ID if successful, None otherwise
        """
        try:
            # Validate inputs
            validation_result = self.validate_tag_data(name, description, color, parent_id, aliases)
            if not validation_result['is_valid']:
                logger.error(f"Invalid tag data: {validation_result['errors']}")
                return None
            
            # Check for duplicate names
            existing_tag = self.db_manager.get_tag_by_name(name)
            if existing_tag:
                logger.error(f"Tag with name '{name}' already exists")
                return None
            
            # Create tag object
            tag_data = {
                'id': str(uuid.uuid4()),
                'name': name,
                'description': description or '',
                'color': color,
                'parent_id': parent_id,
                'usage_count': 0,
                'last_used': None,
                'children': [],
                'aliases': aliases or [],
                'question_count': 0,
                'created_at': datetime.now().isoformat(),
                'created_by': None
            }
            
            # Save to database
            tag_id = self.db_manager.create_tag(tag_data)
            if not tag_id:
                logger.error("Failed to save tag to database")
                return None
            
            # Update parent's children list if parent exists
            if parent_id:
                self._update_parent_children(parent_id, tag_id, add=True)
            
            logger.info(f"Created tag: {tag_id} ({name})")
            return tag_id
            
        except Exception as e:
            logger.error(f"Failed to create tag: {e}")
            return None
    
    def get_tag(self, tag_id: str) -> Optional[Dict]:
        """
        Get a tag by ID.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            Tag dictionary or None if not found
        """
        try:
            return self.db_manager.get_tag(tag_id)
        except Exception as e:
            logger.error(f"Failed to get tag {tag_id}: {e}")
            return None
    
    def get_tag_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a tag by name.
        
        Args:
            name: Tag name
            
        Returns:
            Tag dictionary or None if not found
        """
        try:
            return self.db_manager.get_tag_by_name(name)
        except Exception as e:
            logger.error(f"Failed to get tag by name {name}: {e}")
            return None
    
    def get_all_tags(self) -> List[Dict]:
        """
        Get all tags.
        
        Returns:
            List of tag dictionaries
        """
        try:
            return self.db_manager.get_all_tags()
        except Exception as e:
            logger.error(f"Failed to get all tags: {e}")
            return []
    
    def update_tag(self, tag_id: str, name: str = None, description: str = None, 
                   color: str = None, parent_id: str = None, aliases: List[str] = None) -> bool:
        """
        Update a tag.
        
        Args:
            tag_id: Tag ID
            name: Updated tag name
            description: Updated description
            color: Updated color
            parent_id: Updated parent ID
            aliases: Updated aliases
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing tag
            existing_tag = self.get_tag(tag_id)
            if not existing_tag:
                logger.error(f"Tag not found: {tag_id}")
                return False
            
            # Update fields if provided
            updated_data = existing_tag.copy()
            if name is not None:
                updated_data['name'] = name
            if description is not None:
                updated_data['description'] = description
            if color is not None:
                updated_data['color'] = color
            if parent_id is not None:
                updated_data['parent_id'] = parent_id
            if aliases is not None:
                updated_data['aliases'] = aliases
            
            # Validate updated data
            validation_result = self.validate_tag_data(
                updated_data['name'],
                updated_data['description'],
                updated_data['color'],
                updated_data['parent_id'],
                updated_data['aliases']
            )
            if not validation_result['is_valid']:
                logger.error(f"Invalid updated tag data: {validation_result['errors']}")
                return False
            
            # Check for name conflicts (excluding current tag)
            if name and name != existing_tag['name']:
                existing_by_name = self.db_manager.get_tag_by_name(name)
                if existing_by_name and existing_by_name['id'] != tag_id:
                    logger.error(f"Tag with name '{name}' already exists")
                    return False
            
            # Handle parent changes
            old_parent_id = existing_tag.get('parent_id')
            if parent_id != old_parent_id:
                # Remove from old parent's children
                if old_parent_id:
                    self._update_parent_children(old_parent_id, tag_id, add=False)
                
                # Add to new parent's children
                if parent_id:
                    self._update_parent_children(parent_id, tag_id, add=True)
            
            # Save to database
            success = self.db_manager.update_tag(tag_id, updated_data)
            if success:
                logger.info(f"Updated tag: {tag_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to update tag {tag_id}: {e}")
            return False
    
    def delete_tag(self, tag_id: str) -> bool:
        """
        Delete a tag.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get tag to check for children
            tag = self.get_tag(tag_id)
            if not tag:
                logger.error(f"Tag not found: {tag_id}")
                return False
            
            # Check if tag has children
            if tag.get('children'):
                logger.error(f"Cannot delete tag '{tag['name']}' - it has child tags")
                return False
            
            # Remove from parent's children list
            parent_id = tag.get('parent_id')
            if parent_id:
                self._update_parent_children(parent_id, tag_id, add=False)
            
            # Delete from database
            success = self.db_manager.delete_tag(tag_id)
            if success:
                logger.info(f"Deleted tag: {tag_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete tag {tag_id}: {e}")
            return False
    
    def search_tags(self, search_term: str) -> List[Dict]:
        """
        Search tags by name, description, or aliases.
        
        Args:
            search_term: Text to search for
            
        Returns:
            List of matching tags
        """
        try:
            return self.db_manager.search_tags(search_term)
        except Exception as e:
            logger.error(f"Failed to search tags: {e}")
            return []
    
    def get_root_tags(self) -> List[Dict]:
        """
        Get all root tags (tags without parents).
        
        Returns:
            List of root tag dictionaries
        """
        try:
            all_tags = self.get_all_tags()
            return [tag for tag in all_tags if not tag.get('parent_id')]
        except Exception as e:
            logger.error(f"Failed to get root tags: {e}")
            return []
    
    def get_children(self, parent_id: str) -> List[Dict]:
        """
        Get direct children of a tag.
        
        Args:
            parent_id: Parent tag ID
            
        Returns:
            List of child tag dictionaries
        """
        try:
            all_tags = self.get_all_tags()
            return [tag for tag in all_tags if tag.get('parent_id') == parent_id]
        except Exception as e:
            logger.error(f"Failed to get children for tag {parent_id}: {e}")
            return []
    
    def get_descendants(self, parent_id: str) -> List[Dict]:
        """
        Get all descendants of a tag (children, grandchildren, etc.).
        
        Args:
            parent_id: Parent tag ID
            
        Returns:
            List of descendant tag dictionaries
        """
        try:
            descendants = []
            children = self.get_children(parent_id)
            
            for child in children:
                descendants.append(child)
                descendants.extend(self.get_descendants(child['id']))
            
            return descendants
        except Exception as e:
            logger.error(f"Failed to get descendants for tag {parent_id}: {e}")
            return []
    
    def get_ancestors(self, tag_id: str) -> List[Dict]:
        """
        Get all ancestors of a tag (parent, grandparent, etc.).
        
        Args:
            tag_id: Tag ID
            
        Returns:
            List of ancestor tag dictionaries
        """
        try:
            ancestors = []
            tag = self.get_tag(tag_id)
            
            while tag and tag.get('parent_id'):
                parent = self.get_tag(tag['parent_id'])
                if parent:
                    ancestors.append(parent)
                    tag = parent
                else:
                    break
            
            return ancestors
        except Exception as e:
            logger.error(f"Failed to get ancestors for tag {tag_id}: {e}")
            return []
    
    def merge_tags(self, source_id: str, target_id: str) -> bool:
        """
        Merge a source tag into a target tag.
        
        Args:
            source_id: Source tag ID to merge
            target_id: Target tag ID to merge into
            
        Returns:
            True if successful, False otherwise
        """
        try:
            source_tag = self.get_tag(source_id)
            target_tag = self.get_tag(target_id)
            
            if not source_tag or not target_tag:
                logger.error("Source or target tag not found")
                return False
            
            # Move children from source to target
            source_children = self.get_children(source_id)
            for child in source_children:
                self.update_tag(child['id'], parent_id=target_id)
            
            # Merge aliases
            merged_aliases = list(set(target_tag.get('aliases', []) + source_tag.get('aliases', [])))
            if source_tag['name'] not in merged_aliases:
                merged_aliases.append(source_tag['name'])
            
            self.update_tag(target_id, aliases=merged_aliases)
            
            # Delete source tag
            self.delete_tag(source_id)
            
            logger.info(f"Merged tag {source_id} into {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge tags: {e}")
            return False
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Get tag statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            return self.db_manager.get_tag_statistics()
        except Exception as e:
            logger.error(f"Failed to get tag statistics: {e}")
            return {}
    
    def increment_usage_count(self, tag_id: str) -> bool:
        """
        Increment usage count for a tag.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            tag = self.get_tag(tag_id)
            if not tag:
                return False
            
            updated_data = tag.copy()
            updated_data['usage_count'] = tag.get('usage_count', 0) + 1
            updated_data['last_used'] = datetime.now().isoformat()
            
            return self.db_manager.update_tag(tag_id, updated_data)
        except Exception as e:
            logger.error(f"Failed to increment usage count for {tag_id}: {e}")
            return False
    
    def update_question_count(self, tag_id: str, count: int) -> bool:
        """
        Update question count for a tag.
        
        Args:
            tag_id: Tag ID
            count: New question count
            
        Returns:
            True if successful, False otherwise
        """
        try:
            tag = self.get_tag(tag_id)
            if not tag:
                return False
            
            updated_data = tag.copy()
            updated_data['question_count'] = count
            
            return self.db_manager.update_tag(tag_id, updated_data)
        except Exception as e:
            logger.error(f"Failed to update question count for {tag_id}: {e}")
            return False
    
    def recalculate_question_count(self, tag_id: str) -> bool:
        """
        Recalculate question count for a tag by querying actual questions.
        
        Args:
            tag_id: Tag ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            tag = self.get_tag(tag_id)
            if not tag:
                return False
            
            tag_name = tag.get('name')
            if not tag_name:
                return False
            
            # Get actual count from questions with this tag
            # Use the question manager to search for questions with this tag
            from question_manager_db import QuestionManagerDB
            # We need access to question_manager, but we don't have it here
            # Instead, query directly from database
            questions = self.db_manager.search_questions("", None, [tag_name])
            actual_count = len(questions)
            
            # Update the count
            updated_data = tag.copy()
            updated_data['question_count'] = actual_count
            
            return self.db_manager.update_tag(tag_id, updated_data)
        except Exception as e:
            logger.error(f"Failed to recalculate question count for {tag_id}: {e}")
            return False
    
    def validate_tag_data(self, name: str, description: str = None, color: str = None, 
                         parent_id: str = None, aliases: List[str] = None) -> Dict[str, Any]:
        """
        Validate tag data.
        
        Args:
            name: Tag name
            description: Tag description
            color: Tag color
            parent_id: Parent tag ID
            aliases: List of aliases
            
        Returns:
            Validation result dictionary
        """
        errors = []
        
        # Validate name
        if not name or not name.strip():
            errors.append("Tag name cannot be empty")
        elif len(name) > 100:
            errors.append("Tag name cannot exceed 100 characters")
        elif len(name.strip()) < 2:
            errors.append("Tag name must be at least 2 characters long")
        
        # Prevent common accidental tag names
        reserved_words = ['y', 'n', 'yes', 'no', 'true', 'false', 'cancel', 'c', 'q', 
                         'quit', 'exit', 'back', 'ok', 'okay']
        name_lower = name.strip().lower()
        if name_lower in reserved_words:
            errors.append(f"'{name}' is a reserved word and cannot be used as a tag name")
        
        # Validate description
        if description and len(description) > 500:
            errors.append("Tag description cannot exceed 500 characters")
        
        # Validate color
        if color and not self._is_valid_color(color):
            errors.append("Invalid color format")
        
        # Validate parent_id
        if parent_id:
            if parent_id == name:  # This would be caught later, but good to check
                errors.append("Tag cannot be its own parent")
            else:
                # Check if parent exists
                parent_tag = self.get_tag(parent_id)
                if not parent_tag:
                    errors.append("Parent tag not found")
        
        # Validate aliases
        if aliases:
            if not isinstance(aliases, list):
                errors.append("Aliases must be a list")
            else:
                for alias in aliases:
                    if not isinstance(alias, str) or not alias.strip():
                        errors.append("All aliases must be non-empty strings")
                    elif len(alias) > 100:
                        errors.append("Aliases cannot exceed 100 characters")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def _is_valid_color(self, color: str) -> bool:
        """Check if color is in valid format (hex color)."""
        import re
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))
    
    def _update_parent_children(self, parent_id: str, child_id: str, add: bool = True) -> bool:
        """
        Update parent's children list.
        
        Args:
            parent_id: Parent tag ID
            child_id: Child tag ID
            add: True to add, False to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            parent_tag = self.get_tag(parent_id)
            if not parent_tag:
                return False
            
            children = parent_tag.get('children', [])
            
            if add:
                if child_id not in children:
                    children.append(child_id)
            else:
                if child_id in children:
                    children.remove(child_id)
            
            updated_data = parent_tag.copy()
            updated_data['children'] = children
            
            return self.db_manager.update_tag(parent_id, updated_data)
        except Exception as e:
            logger.error(f"Failed to update parent children: {e}")
            return False
    
    def get_tag_count(self) -> int:
        """
        Get total number of tags.
        
        Returns:
            Number of tags
        """
        try:
            stats = self.get_tag_statistics()
            return stats.get('total_tags', 0)
        except Exception as e:
            logger.error(f"Failed to get tag count: {e}")
            return 0
    
    def get_most_used_tags(self, limit: int = 10) -> List[Dict]:
        """
        Get most used tags.
        
        Args:
            limit: Maximum number of tags to return
            
        Returns:
            List of most used tags
        """
        try:
            stats = self.get_tag_statistics()
            return stats.get('most_used', [])[:limit]
        except Exception as e:
            logger.error(f"Failed to get most used tags: {e}")
            return []
    
    def export_tags(self, file_path: str, format: str = 'json') -> bool:
        """
        Export tags to file.
        
        Args:
            file_path: Path to export file
            format: Export format ('json', 'csv')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            tags = self.get_all_tags()
            
            if format.lower() == 'json':
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(tags, f, indent=2, default=str)
            
            elif format.lower() == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if tags:
                        writer = csv.DictWriter(f, fieldnames=tags[0].keys())
                        writer.writeheader()
                        writer.writerows(tags)
            
            else:
                logger.error(f"Unsupported export format: {format}")
                return False
            
            logger.info(f"Exported {len(tags)} tags to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export tags: {e}")
            return False
    
    def import_tags(self, file_path: str, format: str = 'json') -> Dict[str, Any]:
        """
        Import tags from file.
        
        Args:
            file_path: Path to import file
            format: Import format ('json', 'csv')
            
        Returns:
            Import result with statistics
        """
        result = {
            'success': False,
            'imported_count': 0,
            'failed_count': 0,
            'errors': []
        }
        
        try:
            tags = []
            
            if format.lower() == 'json':
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    tags = json.load(f)
            
            elif format.lower() == 'csv':
                import csv
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    tags = list(reader)
            
            else:
                result['errors'].append(f"Unsupported import format: {format}")
                return result
            
            # Import each tag
            for tag_data in tags:
                try:
                    # Validate and create tag
                    validation_result = self.validate_tag_data(
                        tag_data.get('name', ''),
                        tag_data.get('description'),
                        tag_data.get('color'),
                        tag_data.get('parent_id'),
                        tag_data.get('aliases', [])
                    )
                    
                    if validation_result['is_valid']:
                        tag_id = self.create_tag(
                            tag_data['name'],
                            tag_data.get('description'),
                            tag_data.get('color'),
                            tag_data.get('parent_id'),
                            tag_data.get('aliases', [])
                        )
                        if tag_id:
                            result['imported_count'] += 1
                        else:
                            result['failed_count'] += 1
                    else:
                        result['failed_count'] += 1
                        result['errors'].extend(validation_result['errors'])
                
                except Exception as e:
                    result['failed_count'] += 1
                    result['errors'].append(f"Failed to import tag: {e}")
            
            result['success'] = result['failed_count'] == 0
            logger.info(f"Imported {result['imported_count']} tags, {result['failed_count']} failed")
            return result
            
        except Exception as e:
            result['errors'].append(f"Import failed: {e}")
            logger.error(f"Failed to import tags: {e}")
            return result
