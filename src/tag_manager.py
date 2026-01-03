"""
Enhanced Tag Manager Module

This module handles tag creation, management, and organization of questions
with support for hierarchical tag structures, advanced search, and analytics.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
import logging
import re

from models.tag import Tag

logger = logging.getLogger(__name__)

class TagManager:
    """Enhanced tag manager with hierarchical support and advanced features."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the enhanced tag manager."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.tags_file = self.data_dir / "tags.json"
        self.tags: Dict[str, Tag] = {}  # ID -> Tag mapping
        self.name_index: Dict[str, str] = {}  # name -> ID mapping
        self.alias_index: Dict[str, str] = {}  # alias -> ID mapping
        self._load_tags()
        logger.info("Enhanced tag manager initialized")
    
    def create_tag(self, name: str, description: str = "", color: str = "", 
                   parent_id: Optional[str] = None, aliases: List[str] = None) -> Tag:
        """
        Create a new tag with hierarchical support.
        
        Args:
            name: Tag name (must be unique)
            description: Optional description
            color: Optional hex color code
            parent_id: Optional parent tag ID
            aliases: Optional list of aliases
            
        Returns:
            Created Tag object
        """
        # Validate tag name
        if not name or not name.strip():
            raise ValueError("Tag name cannot be empty")
        
        name = name.strip()
        
        # Check for uniqueness
        if self.get_tag_by_name(name):
            raise ValueError(f"Tag '{name}' already exists")
        
        # Validate parent if provided
        if parent_id:
            parent = self.get_tag_by_id(parent_id)
            if not parent:
                raise ValueError(f"Parent tag with ID '{parent_id}' not found")
            
            # Check for circular hierarchy
            if self._would_create_circle(parent_id, name):
                raise ValueError("Cannot create circular tag hierarchy")
        
        # Create tag object
        tag = Tag(
            name=name,
            description=description,
            color=color,
            parent_id=parent_id
        )
        
        # Add aliases after creation
        if aliases:
            tag.aliases = aliases
        
        # Add to collections
        self.tags[tag.id] = tag
        self.name_index[name.lower()] = tag.id
        
        # Add aliases to index
        for alias in tag.aliases:
            self.alias_index[alias.lower()] = tag.id
        
        # Update parent's children list
        if parent_id:
            parent = self.tags[parent_id]
            parent.add_child(tag.id)
        
        self._save_tags()
        logger.info(f"Created tag: {name} (ID: {tag.id})")
        return tag
    
    def get_tag_by_id(self, tag_id: str) -> Optional[Tag]:
        """Get a tag by its ID."""
        return self.tags.get(tag_id)
    
    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get a tag by its name or alias."""
        name = name.strip().lower()
        
        # Try direct name lookup
        tag_id = self.name_index.get(name)
        if tag_id:
            return self.tags.get(tag_id)
        
        # Try alias lookup
        tag_id = self.alias_index.get(name)
        if tag_id:
            return self.tags.get(tag_id)
        
        return None
    
    def get_all_tags(self) -> List[Tag]:
        """Get all tags sorted by name."""
        return sorted(self.tags.values(), key=lambda x: x.name.lower())
    
    def get_root_tags(self) -> List[Tag]:
        """Get all root tags (tags with no parent)."""
        return [tag for tag in self.tags.values() if tag.is_root()]
    
    def get_children(self, parent_id: str) -> List[Tag]:
        """Get all direct children of a tag."""
        parent = self.get_tag_by_id(parent_id)
        if not parent:
            return []
        
        children = []
        for child_id in parent.children:
            child = self.get_tag_by_id(child_id)
            if child:
                children.append(child)
        
        return sorted(children, key=lambda x: x.name.lower())
    
    def get_descendants(self, parent_id: str) -> List[Tag]:
        """Get all descendants of a tag (children, grandchildren, etc.)."""
        descendants = []
        children = self.get_children(parent_id)
        
        for child in children:
            descendants.append(child)
            descendants.extend(self.get_descendants(child.id))
        
        return descendants
    
    def get_ancestors(self, tag_id: str) -> List[Tag]:
        """Get all ancestors of a tag (parent, grandparent, etc.)."""
        ancestors = []
        tag = self.get_tag_by_id(tag_id)
        
        while tag and tag.parent_id:
            parent = self.get_tag_by_id(tag.parent_id)
            if parent:
                ancestors.append(parent)
                tag = parent
            else:
                break
        
        return ancestors
    
    def update_tag(self, tag_id: str, **updates) -> bool:
        """
        Update an existing tag.
        
        Args:
            tag_id: ID of tag to update
            **updates: Fields to update
            
        Returns:
            True if update successful, False otherwise
        """
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            return False
        
        # Handle name changes
        if 'name' in updates:
            new_name = updates['name'].strip()
            if not new_name:
                raise ValueError("Tag name cannot be empty")
            
            existing_tag = self.get_tag_by_name(new_name)
            if existing_tag and existing_tag.id != tag_id:
                raise ValueError(f"Tag '{new_name}' already exists")
            
            # Update name index
            old_name = tag.name.lower()
            del self.name_index[old_name]
            self.name_index[new_name.lower()] = tag_id
        
        # Handle parent changes
        if 'parent_id' in updates:
            new_parent_id = updates['parent_id']
            if new_parent_id and self._would_create_circle(new_parent_id, tag_id):
                raise ValueError("Cannot create circular tag hierarchy")
            
            # Update parent relationships
            old_parent_id = tag.parent_id
            if old_parent_id:
                old_parent = self.get_tag_by_id(old_parent_id)
                if old_parent:
                    old_parent.remove_child(tag_id)
            
            if new_parent_id:
                new_parent = self.get_tag_by_id(new_parent_id)
                if new_parent:
                    new_parent.add_child(tag_id)
        
        # Handle alias changes
        if 'aliases' in updates:
            # Remove old aliases from index
            for alias in tag.aliases:
                if alias.lower() in self.alias_index:
                    del self.alias_index[alias.lower()]
            
            # Add new aliases to index
            for alias in updates['aliases']:
                self.alias_index[alias.lower()] = tag_id
        
        # Apply updates
        tag.update(**updates)
        self._save_tags()
        logger.info(f"Updated tag: {tag_id}")
        return True
    
    def delete_tag(self, tag_id: str, reassign_to: Optional[str] = None) -> bool:
        """
        Delete a tag with optional reassignment of questions.
        
        Args:
            tag_id: ID of tag to delete
            reassign_to: Optional tag ID to reassign questions to
            
        Returns:
            True if deletion successful, False otherwise
        """
        tag = self.get_tag_by_id(tag_id)
        if not tag:
            return False
        
        # Check if tag has children
        if tag.has_children():
            raise ValueError(f"Cannot delete tag '{tag.name}' - it has child tags")
        
        # Handle question reassignment
        if tag.question_count > 0:
            if not reassign_to:
                raise ValueError(f"Cannot delete tag '{tag.name}' - it is used by {tag.question_count} questions")
            
            reassign_tag = self.get_tag_by_id(reassign_to)
            if not reassign_tag:
                raise ValueError(f"Reassignment tag with ID '{reassign_to}' not found")
        
        # Remove from parent's children list
        if tag.parent_id:
            parent = self.get_tag_by_id(tag.parent_id)
            if parent:
                parent.remove_child(tag_id)
        
        # Remove from collections
        del self.tags[tag_id]
        del self.name_index[tag.name.lower()]
        
        # Remove aliases from index
        for alias in tag.aliases:
            if alias.lower() in self.alias_index:
                del self.alias_index[alias.lower()]
        
        self._save_tags()
        logger.info(f"Deleted tag: {tag.name}")
        return True
    
    def merge_tags(self, source_id: str, target_id: str) -> bool:
        """
        Merge one tag into another.
        
        Args:
            source_id: ID of tag to merge from
            target_id: ID of tag to merge into
            
        Returns:
            True if merge successful, False otherwise
        """
        source_tag = self.get_tag_by_id(source_id)
        target_tag = self.get_tag_by_id(target_id)
        
        if not source_tag or not target_tag:
            return False
        
        if source_id == target_id:
            raise ValueError("Cannot merge tag with itself")
        
        # Move children to target
        for child_id in source_tag.children:
            child = self.get_tag_by_id(child_id)
            if child:
                child.parent_id = target_id
                target_tag.add_child(child_id)
        
        # Move aliases to target
        for alias in source_tag.aliases:
            target_tag.add_alias(alias)
            self.alias_index[alias.lower()] = target_id
        
        # Remove from parent's children list if source has parent
        if source_tag.parent_id:
            parent = self.get_tag_by_id(source_tag.parent_id)
            if parent:
                parent.remove_child(source_id)
        
        # Delete source tag directly (bypassing children check)
        del self.tags[source_id]
        del self.name_index[source_tag.name.lower()]
        
        # Remove aliases from index
        for alias in source_tag.aliases:
            if alias.lower() in self.alias_index:
                del self.alias_index[alias.lower()]
        
        self._save_tags()
        
        logger.info(f"Merged tag '{source_tag.name}' into '{target_tag.name}'")
        return True
    
    def search_tags(self, search_term: str, include_aliases: bool = True) -> List[Tag]:
        """
        Search tags by name, description, or aliases.
        
        Args:
            search_term: Search term
            include_aliases: Whether to include alias matches
            
        Returns:
            List of matching tags
        """
        search_term = search_term.lower()
        results = []
        
        for tag in self.tags.values():
            # Check name
            if search_term in tag.name.lower():
                results.append(tag)
                continue
            
            # Check description
            if search_term in tag.description.lower():
                results.append(tag)
                continue
            
            # Check aliases
            if include_aliases:
                for alias in tag.aliases:
                    if search_term in alias.lower():
                        results.append(tag)
                        break
        
        return sorted(results, key=lambda x: x.name.lower())
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about tag usage."""
        if not self.tags:
            return {
                'total_tags': 0,
                'root_tags': 0,
                'leaf_tags': 0,
                'max_depth': 0,
                'most_used_tags': [],
                'least_used_tags': [],
                'unused_tags': [],
                'recently_used': [],
                'tag_hierarchy_stats': {}
            }
        
        # Basic counts
        total_tags = len(self.tags)
        root_tags = len(self.get_root_tags())
        leaf_tags = len([tag for tag in self.tags.values() if tag.is_leaf()])
        
        # Calculate max depth
        max_depth = 0
        for tag in self.tags.values():
            depth = tag.get_depth(self)
            max_depth = max(max_depth, depth)
        
        # Usage statistics
        sorted_by_usage = sorted(self.tags.values(), key=lambda x: x.usage_count, reverse=True)
        sorted_by_questions = sorted(self.tags.values(), key=lambda x: x.question_count, reverse=True)
        
        most_used = sorted_by_usage[:5]
        least_used = sorted_by_usage[-5:] if len(sorted_by_usage) >= 5 else sorted_by_usage
        unused = [tag for tag in self.tags.values() if tag.question_count == 0]
        
        # Recently used (last 7 days)
        recent_cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
        recently_used = []
        for tag in self.tags.values():
            if tag.last_used:
                try:
                    last_used_time = datetime.fromisoformat(tag.last_used).timestamp()
                    if last_used_time > recent_cutoff:
                        recently_used.append(tag)
                except:
                    pass
        
        recently_used.sort(key=lambda x: x.last_used or '', reverse=True)
        
        # Hierarchy statistics
        hierarchy_stats = self._get_hierarchy_statistics()
        
        return {
            'total_tags': total_tags,
            'root_tags': root_tags,
            'leaf_tags': leaf_tags,
            'max_depth': max_depth,
            'most_used_tags': most_used,
            'least_used_tags': least_used,
            'unused_tags': unused,
            'recently_used': recently_used[:10],
            'tag_hierarchy_stats': hierarchy_stats,
            'average_usage': sum(tag.usage_count for tag in self.tags.values()) / total_tags,
            'average_questions': sum(tag.question_count for tag in self.tags.values()) / total_tags
        }
    
    def _get_hierarchy_statistics(self) -> Dict[str, Any]:
        """Get statistics about tag hierarchy structure."""
        depth_counts = {}
        children_counts = {}
        
        for tag in self.tags.values():
            depth = tag.get_depth(self)
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
            
            child_count = len(tag.children)
            children_counts[child_count] = children_counts.get(child_count, 0) + 1
        
        return {
            'depth_distribution': depth_counts,
            'children_distribution': children_counts,
            'max_children': max(children_counts.keys()) if children_counts else 0
        }
    
    def get_questions_by_tag(self, tag_id: str, include_children: bool = False) -> List[str]:
        """
        Get question IDs associated with a tag.
        
        Args:
            tag_id: Tag ID
            include_children: Whether to include questions from child tags
            
        Returns:
            List of question IDs
        """
        # This would need to be implemented with QuestionManager integration
        # For now, return empty list
        return []
    
    def update_question_count(self, tag_name: str, delta: int):
        """
        Update the question count for a tag.
        
        Args:
            tag_name: Name of the tag
            delta: Change in question count (+1 or -1)
        """
        tag = self.get_tag_by_name(tag_name)
        if tag:
            tag.question_count = max(0, tag.question_count + delta)
            tag.increment_usage()
            self._save_tags()
            logger.debug(f"Updated question count for tag '{tag_name}': {tag.question_count}")
    
    def validate_tag_hierarchy(self) -> Dict[str, Any]:
        """
        Validate the entire tag hierarchy for consistency.
        
        Returns:
            Validation result with issues found
        """
        issues = []
        
        # Check for circular references
        for tag in self.tags.values():
            if self._has_circular_reference(tag.id):
                issues.append(f"Circular reference detected for tag '{tag.name}'")
        
        # Check for orphaned children
        for tag in self.tags.values():
            for child_id in tag.children:
                child = self.get_tag_by_id(child_id)
                if not child:
                    issues.append(f"Orphaned child reference in tag '{tag.name}': {child_id}")
                elif child.parent_id != tag.id:
                    issues.append(f"Inconsistent parent-child relationship: '{tag.name}' -> '{child.name}'")
        
        # Check for missing parents
        for tag in self.tags.values():
            if tag.parent_id and not self.get_tag_by_id(tag.parent_id):
                issues.append(f"Tag '{tag.name}' references missing parent: {tag.parent_id}")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }
    
    def _would_create_circle(self, parent_id: str, child_id: str) -> bool:
        """Check if setting parent_id would create a circular reference."""
        if parent_id == child_id:
            return True
        
        # Check if child_id is an ancestor of parent_id
        current = self.get_tag_by_id(parent_id)
        while current and current.parent_id:
            if current.parent_id == child_id:
                return True
            current = self.get_tag_by_id(current.parent_id)
        
        return False
    
    def _has_circular_reference(self, tag_id: str) -> bool:
        """Check if a tag has a circular reference in its ancestry."""
        visited = set()
        current = self.get_tag_by_id(tag_id)
        
        while current and current.parent_id:
            if current.id in visited:
                return True
            visited.add(current.id)
            current = self.get_tag_by_id(current.parent_id)
        
        return False
    
    def export_tags(self, format: str = "json") -> str:
        """
        Export all tags in specified format.
        
        Args:
            format: Export format ("json", "csv")
            
        Returns:
            Exported data as string
        """
        if format == "json":
            export_data = {
                'version': '2.0',
                'export_timestamp': datetime.now().isoformat(),
                'tags': [tag.to_dict() for tag in self.tags.values()]
            }
            return json.dumps(export_data, indent=2, default=str)
        elif format == "csv":
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['ID', 'Name', 'Description', 'Color', 'Parent ID', 'Question Count', 'Usage Count', 'Last Used', 'Created At', 'Children', 'Aliases'])
            
            # Write data
            for tag in sorted(self.tags.values(), key=lambda x: x.name):
                writer.writerow([
                    tag.id,
                    tag.name,
                    tag.description,
                    tag.color,
                    tag.parent_id or '',
                    tag.question_count,
                    tag.usage_count,
                    tag.last_used or '',
                    tag.created_at,
                    ';'.join(tag.children),
                    ';'.join(tag.aliases)
                ])
            
            return output.getvalue()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_tags(self, data: str, format: str = "json") -> int:
        """
        Import tags from external source.
        
        Args:
            data: Data to import
            format: Data format ("json", "csv")
            
        Returns:
            Number of tags imported
        """
        imported_count = 0
        
        if format == "json":
            import_data = json.loads(data)
            tags_data = import_data.get('tags', [])
            
            for tag_data in tags_data:
                try:
                    # Create tag from data
                    tag = Tag.from_dict(tag_data)
                    
                    # Check if tag already exists
                    if not self.get_tag_by_name(tag.name):
                        self.tags[tag.id] = tag
                        self.name_index[tag.name.lower()] = tag.id
                        
                        # Add aliases to index
                        for alias in tag.aliases:
                            self.alias_index[alias.lower()] = tag.id
                        
                        imported_count += 1
                        logger.info(f"Imported tag: {tag.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to import tag: {e}")
        
        elif format == "csv":
            import csv
            import io
            
            reader = csv.DictReader(io.StringIO(data))
            for row in reader:
                try:
                    name = row['Name'].strip()
                    if not name or self.get_tag_by_name(name):
                        continue
                    
                    tag = Tag(
                        name=name,
                        description=row.get('Description', ''),
                        color=row.get('Color', ''),
                        parent_id=row.get('Parent ID') or None,
                        aliases=row.get('Aliases', '').split(';') if row.get('Aliases') else []
                    )
                    
                    self.tags[tag.id] = tag
                    self.name_index[tag.name.lower()] = tag.id
                    
                    # Add aliases to index
                    for alias in tag.aliases:
                        self.alias_index[alias.lower()] = tag.id
                    
                    imported_count += 1
                    logger.info(f"Imported tag: {tag.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to import tag from CSV: {e}")
        
        if imported_count > 0:
            self._save_tags()
        
        return imported_count
    
    def _load_tags(self):
        """Load tags from JSON file."""
        if self.tags_file.exists():
            try:
                with open(self.tags_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle both old and new format
                if isinstance(data, list):
                    # Old format - list of dictionaries
                    tags_data = data
                else:
                    # New format - dictionary with metadata
                    tags_data = data.get('tags', [])
                
                for tag_data in tags_data:
                    try:
                        tag = Tag.from_dict(tag_data)
                        self.tags[tag.id] = tag
                        self.name_index[tag.name.lower()] = tag.id
                        
                        # Add aliases to index
                        for alias in tag.aliases:
                            self.alias_index[alias.lower()] = tag.id
                            
                    except Exception as e:
                        logger.error(f"Failed to load tag: {e}")
                
                logger.info(f"Loaded {len(self.tags)} tags from {self.tags_file}")
                
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading tags: {e}")
                self.tags = {}
        else:
            self.tags = {}
            logger.info("No tags file found, starting with empty tag collection")
    
    def _save_tags(self):
        """Save tags to JSON file."""
        try:
            data = {
                'version': '2.0',
                'timestamp': datetime.now().isoformat(),
                'tags': [tag.to_dict() for tag in self.tags.values()]
            }
            
            with open(self.tags_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.debug(f"Saved {len(self.tags)} tags to {self.tags_file}")
        except IOError as e:
            logger.error(f"Error saving tags: {e}")
            raise