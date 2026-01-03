"""
Tag Management Interface

This module provides console-based interfaces for tag management operations
including hierarchical tag creation, bulk operations, and advanced search.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime

from models.tag import Tag
from tag_manager import TagManager

logger = logging.getLogger(__name__)

class TagInterface:
    """Console interface for tag management operations."""
    
    def __init__(self, tag_manager: TagManager):
        """Initialize the tag interface."""
        self.tag_manager = tag_manager
        self.logger = logging.getLogger(__name__)
    
    def display_tag_menu(self) -> None:
        """Display the main tag management menu."""
        print("\n" + "="*60)
        print("🏷️  TAG MANAGEMENT")
        print("="*60)
        print("1. View All Tags")
        print("2. Create New Tag")
        print("3. Edit Tag")
        print("4. Delete Tag")
        print("5. Search Tags")
        print("6. Tag Statistics")
        print("7. Bulk Operations")
        print("8. Import/Export Tags")
        print("9. Tag Hierarchy View")
        print("0. Back to Main Menu")
        print("-"*60)
    
    def view_all_tags(self, show_hierarchy: bool = True) -> None:
        """
        Display all tags with optional hierarchy view.
        
        Args:
            show_hierarchy: Whether to show hierarchical structure
        """
        print("\n" + "="*60)
        print("📋 ALL TAGS")
        print("="*60)
        
        if show_hierarchy:
            self._display_hierarchical_tags()
        else:
            self._display_flat_tags()
    
    def _display_hierarchical_tags(self) -> None:
        """Display tags in hierarchical structure."""
        root_tags = self.tag_manager.get_root_tags()
        
        if not root_tags:
            print("No tags found.")
            return
        
        for root_tag in root_tags:
            self._display_tag_tree(root_tag, 0)
    
    def _display_tag_tree(self, tag: Tag, depth: int) -> None:
        """Display a tag and its children recursively."""
        indent = "  " * depth
        prefix = "├─ " if depth > 0 else ""
        
        # Tag info with color coding
        color_indicator = f"🎨 {tag.color}" if tag.color else ""
        usage_info = f"📊 {tag.usage_count} uses, {tag.question_count} questions"
        
        print(f"{indent}{prefix}🏷️  {tag.name}")
        print(f"{indent}   {color_indicator}")
        print(f"{indent}   {usage_info}")
        
        if tag.description:
            print(f"{indent}   📝 {tag.description}")
        
        if tag.aliases:
            aliases_str = ", ".join(tag.aliases)
            print(f"{indent}   🔖 Aliases: {aliases_str}")
        
        print(f"{indent}   🆔 ID: {tag.id}")
        print()
        
        # Display children
        children = self.tag_manager.get_children(tag.id)
        for child in children:
            self._display_tag_tree(child, depth + 1)
    
    def _display_flat_tags(self) -> None:
        """Display tags in a flat list."""
        tags = self.tag_manager.get_all_tags()
        
        if not tags:
            print("No tags found.")
            return
        
        print(f"{'Name':<20} {'Questions':<10} {'Usage':<8} {'Parent':<15} {'Description'}")
        print("-" * 80)
        
        for tag in tags:
            parent_name = ""
            if tag.parent_id:
                parent = self.tag_manager.get_tag_by_id(tag.parent_id)
                if parent:
                    parent_name = parent.name
            
            description = tag.description[:30] + "..." if len(tag.description) > 30 else tag.description
            
            print(f"{tag.name:<20} {tag.question_count:<10} {tag.usage_count:<8} {parent_name:<15} {description}")
    
    def create_tag_interactive(self) -> Optional[Tag]:
        """
        Interactive tag creation with hierarchy support.
        
        Returns:
            Created Tag object or None if cancelled
        """
        print("\n" + "="*60)
        print("➕ CREATE NEW TAG")
        print("="*60)
        
        # Get tag name
        while True:
            name = input("Tag name: ").strip()
            if not name:
                print("❌ Tag name cannot be empty.")
                continue
            
            if self.tag_manager.get_tag_by_name(name):
                print(f"❌ Tag '{name}' already exists.")
                continue
            
            break
        
        # Get description
        description = input("Description (optional): ").strip()
        
        # Get color
        color = input("Color (hex code, optional): ").strip()
        if color and not color.startswith('#'):
            color = '#' + color
        
        # Get parent tag
        parent_id = None
        if input("Set parent tag? (y/N): ").lower() == 'y':
            parent_id = self._select_parent_tag()
        
        # Get aliases
        aliases = []
        if input("Add aliases? (y/N): ").lower() == 'y':
            aliases = self._get_aliases()
        
        try:
            tag = self.tag_manager.create_tag(
                name=name,
                description=description,
                color=color,
                parent_id=parent_id,
                aliases=aliases
            )
            
            print(f"✅ Successfully created tag: {tag.name}")
            return tag
            
        except Exception as e:
            print(f"❌ Error creating tag: {e}")
            return None
    
    def _select_parent_tag(self) -> Optional[str]:
        """Interactive parent tag selection."""
        print("\nSelect parent tag:")
        root_tags = self.tag_manager.get_root_tags()
        
        if not root_tags:
            print("No root tags available.")
            return None
        
        # Display root tags
        for i, tag in enumerate(root_tags, 1):
            print(f"{i}. {tag.name}")
        
        try:
            choice = int(input("Enter parent tag number (0 to cancel): "))
            if choice == 0:
                return None
            
            if 1 <= choice <= len(root_tags):
                return root_tags[choice - 1].id
            else:
                print("❌ Invalid selection.")
                return None
                
        except ValueError:
            print("❌ Invalid input.")
            return None
    
    def _get_aliases(self) -> List[str]:
        """Interactive alias collection."""
        aliases = []
        
        while True:
            alias = input("Enter alias (or press Enter to finish): ").strip()
            if not alias:
                break
            
            if alias in aliases:
                print("❌ Alias already added.")
                continue
            
            aliases.append(alias)
            print(f"✅ Added alias: {alias}")
        
        return aliases
    
    def edit_tag_interactive(self) -> bool:
        """
        Interactive tag editing.
        
        Returns:
            True if tag was edited successfully
        """
        print("\n" + "="*60)
        print("✏️  EDIT TAG")
        print("="*60)
        
        # Select tag to edit
        tag = self._select_tag("Select tag to edit:")
        if not tag:
            return False
        
        print(f"\nEditing tag: {tag.name}")
        print(f"Current description: {tag.description}")
        print(f"Current color: {tag.color}")
        
        # Get updates
        updates = {}
        
        # Name update
        if input("Update name? (y/N): ").lower() == 'y':
            new_name = input(f"New name (current: {tag.name}): ").strip()
            if new_name and new_name != tag.name:
                updates['name'] = new_name
        
        # Description update
        if input("Update description? (y/N): ").lower() == 'y':
            new_description = input(f"New description (current: {tag.description}): ").strip()
            updates['description'] = new_description
        
        # Color update
        if input("Update color? (y/N): ").lower() == 'y':
            new_color = input(f"New color (current: {tag.color}): ").strip()
            if new_color and not new_color.startswith('#'):
                new_color = '#' + new_color
            updates['color'] = new_color
        
        # Parent update
        if input("Update parent? (y/N): ").lower() == 'y':
            new_parent_id = self._select_parent_tag()
            updates['parent_id'] = new_parent_id
        
        # Aliases update
        if input("Update aliases? (y/N): ").lower() == 'y':
            print(f"Current aliases: {', '.join(tag.aliases) if tag.aliases else 'None'}")
            new_aliases = self._get_aliases()
            updates['aliases'] = new_aliases
        
        if not updates:
            print("No changes made.")
            return False
        
        try:
            success = self.tag_manager.update_tag(tag.id, **updates)
            if success:
                print("✅ Tag updated successfully.")
                return True
            else:
                print("❌ Failed to update tag.")
                return False
                
        except Exception as e:
            print(f"❌ Error updating tag: {e}")
            return False
    
    def delete_tag_interactive(self) -> bool:
        """
        Interactive tag deletion with reassignment options.
        
        Returns:
            True if tag was deleted successfully
        """
        print("\n" + "="*60)
        print("🗑️  DELETE TAG")
        print("="*60)
        
        # Select tag to delete
        tag = self._select_tag("Select tag to delete:")
        if not tag:
            return False
        
        print(f"\nTag to delete: {tag.name}")
        print(f"Questions using this tag: {tag.question_count}")
        print(f"Children: {len(tag.children)}")
        
        if tag.has_children():
            print("❌ Cannot delete tag with children.")
            return False
        
        if tag.question_count > 0:
            print(f"⚠️  This tag is used by {tag.question_count} questions.")
            if input("Continue with deletion? (y/N): ").lower() != 'y':
                return False
            
            # Ask for reassignment
            reassign_to = None
            if input("Reassign questions to another tag? (y/N): ").lower() == 'y':
                reassign_tag = self._select_tag("Select tag to reassign questions to:")
                if reassign_tag:
                    reassign_to = reassign_tag.id
        
        # Confirm deletion
        if input(f"Are you sure you want to delete '{tag.name}'? (y/N): ").lower() != 'y':
            return False
        
        try:
            success = self.tag_manager.delete_tag(tag.id, reassign_to)
            if success:
                print("✅ Tag deleted successfully.")
                return True
            else:
                print("❌ Failed to delete tag.")
                return False
                
        except Exception as e:
            print(f"❌ Error deleting tag: {e}")
            return False
    
    def search_tags_interactive(self) -> None:
        """Interactive tag search."""
        print("\n" + "="*60)
        print("🔍 SEARCH TAGS")
        print("="*60)
        
        search_term = input("Enter search term: ").strip()
        if not search_term:
            print("❌ Search term cannot be empty.")
            return
        
        include_aliases = input("Include aliases in search? (Y/n): ").lower() != 'n'
        
        results = self.tag_manager.search_tags(search_term, include_aliases)
        
        if not results:
            print("No tags found matching your search.")
            return
        
        print(f"\nFound {len(results)} tag(s):")
        print("-" * 60)
        
        for tag in results:
            print(f"🏷️  {tag.name}")
            if tag.description:
                print(f"   📝 {tag.description}")
            if tag.aliases:
                print(f"   🔖 Aliases: {', '.join(tag.aliases)}")
            print(f"   📊 {tag.question_count} questions, {tag.usage_count} uses")
            print()
    
    def display_tag_statistics(self) -> None:
        """Display comprehensive tag statistics."""
        print("\n" + "="*60)
        print("📊 TAG STATISTICS")
        print("="*60)
        
        stats = self.tag_manager.get_tag_statistics()
        
        print(f"Total Tags: {stats['total_tags']}")
        print(f"Root Tags: {stats['root_tags']}")
        print(f"Leaf Tags: {stats['leaf_tags']}")
        print(f"Max Hierarchy Depth: {stats['max_depth']}")
        print(f"Average Usage: {stats['average_usage']:.1f}")
        print(f"Average Questions per Tag: {stats['average_questions']:.1f}")
        
        # Most used tags
        if stats['most_used_tags']:
            print("\n🔥 Most Used Tags:")
            for tag in stats['most_used_tags']:
                print(f"  • {tag.name}: {tag.usage_count} uses")
        
        # Recently used tags
        if stats['recently_used']:
            print("\n⏰ Recently Used (Last 7 Days):")
            for tag in stats['recently_used']:
                print(f"  • {tag.name}: {tag.last_used}")
        
        # Unused tags
        if stats['unused_tags']:
            print(f"\n💤 Unused Tags ({len(stats['unused_tags'])}):")
            for tag in stats['unused_tags'][:10]:  # Show first 10
                print(f"  • {tag.name}")
            if len(stats['unused_tags']) > 10:
                print(f"  ... and {len(stats['unused_tags']) - 10} more")
        
        # Hierarchy statistics
        hierarchy_stats = stats['tag_hierarchy_stats']
        if hierarchy_stats['depth_distribution']:
            print("\n📊 Hierarchy Distribution:")
            for depth, count in sorted(hierarchy_stats['depth_distribution'].items()):
                print(f"  Depth {depth}: {count} tags")
    
    def bulk_operations_menu(self) -> None:
        """Display bulk operations menu."""
        print("\n" + "="*60)
        print("⚡ BULK OPERATIONS")
        print("="*60)
        print("1. Merge Tags")
        print("2. Delete Multiple Tags")
        print("3. Update Multiple Tags")
        print("4. Validate Tag Hierarchy")
        print("0. Back")
        print("-"*60)
        
        choice = input("Select operation: ").strip()
        
        if choice == '1':
            self._bulk_merge_tags()
        elif choice == '2':
            self._bulk_delete_tags()
        elif choice == '3':
            self._bulk_update_tags()
        elif choice == '4':
            self._validate_hierarchy()
        elif choice == '0':
            return
        else:
            print("❌ Invalid selection.")
    
    def _bulk_merge_tags(self) -> None:
        """Bulk merge tags operation."""
        print("\n🔄 MERGE TAGS")
        print("Select source tag to merge from:")
        source_tag = self._select_tag("Source tag:")
        if not source_tag:
            return
        
        print("Select target tag to merge into:")
        target_tag = self._select_tag("Target tag:")
        if not target_tag:
            return
        
        if source_tag.id == target_tag.id:
            print("❌ Cannot merge tag with itself.")
            return
        
        print(f"\nThis will merge '{source_tag.name}' into '{target_tag.name}'")
        print(f"• Children of '{source_tag.name}' will become children of '{target_tag.name}'")
        print(f"• Aliases of '{source_tag.name}' will be added to '{target_tag.name}'")
        print(f"• '{source_tag.name}' will be deleted")
        
        if input("Continue? (y/N): ").lower() != 'y':
            return
        
        try:
            success = self.tag_manager.merge_tags(source_tag.id, target_tag.id)
            if success:
                print("✅ Tags merged successfully.")
            else:
                print("❌ Failed to merge tags.")
        except Exception as e:
            print(f"❌ Error merging tags: {e}")
    
    def _bulk_delete_tags(self) -> None:
        """Bulk delete tags operation."""
        print("\n🗑️  BULK DELETE TAGS")
        print("Select tags to delete (press Enter when done):")
        
        tags_to_delete = []
        while True:
            tag = self._select_tag("Select tag to delete (or press Enter to finish):")
            if not tag:
                break
            
            if tag not in tags_to_delete:
                tags_to_delete.append(tag)
                print(f"✅ Added '{tag.name}' to deletion list")
            else:
                print("❌ Tag already in deletion list")
        
        if not tags_to_delete:
            print("No tags selected for deletion.")
            return
        
        print(f"\nTags to delete ({len(tags_to_delete)}):")
        for tag in tags_to_delete:
            print(f"  • {tag.name} ({tag.question_count} questions)")
        
        if input("Confirm bulk deletion? (y/N): ").lower() != 'y':
            return
        
        deleted_count = 0
        for tag in tags_to_delete:
            try:
                success = self.tag_manager.delete_tag(tag.id)
                if success:
                    deleted_count += 1
                    print(f"✅ Deleted '{tag.name}'")
                else:
                    print(f"❌ Failed to delete '{tag.name}'")
            except Exception as e:
                print(f"❌ Error deleting '{tag.name}': {e}")
        
        print(f"\nDeleted {deleted_count} out of {len(tags_to_delete)} tags.")
    
    def _bulk_update_tags(self) -> None:
        """Bulk update tags operation."""
        print("\n✏️  BULK UPDATE TAGS")
        print("This feature will be implemented in future versions.")
    
    def _validate_hierarchy(self) -> None:
        """Validate tag hierarchy."""
        print("\n🔍 VALIDATING TAG HIERARCHY")
        
        validation_result = self.tag_manager.validate_tag_hierarchy()
        
        if validation_result['is_valid']:
            print("✅ Tag hierarchy is valid.")
        else:
            print("❌ Tag hierarchy has issues:")
            for issue in validation_result['issues']:
                print(f"  • {issue}")
    
    def import_export_menu(self) -> None:
        """Display import/export menu."""
        print("\n" + "="*60)
        print("📤📥 IMPORT/EXPORT TAGS")
        print("="*60)
        print("1. Export Tags (JSON)")
        print("2. Export Tags (CSV)")
        print("3. Import Tags (JSON)")
        print("4. Import Tags (CSV)")
        print("0. Back")
        print("-"*60)
        
        choice = input("Select operation: ").strip()
        
        if choice == '1':
            self._export_tags('json')
        elif choice == '2':
            self._export_tags('csv')
        elif choice == '3':
            self._import_tags('json')
        elif choice == '4':
            self._import_tags('csv')
        elif choice == '0':
            return
        else:
            print("❌ Invalid selection.")
    
    def _export_tags(self, format: str) -> None:
        """Export tags to file."""
        try:
            data = self.tag_manager.export_tags(format)
            
            filename = f"tags_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
            filepath = self.tag_manager.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data)
            
            print(f"✅ Tags exported to: {filepath}")
            
        except Exception as e:
            print(f"❌ Error exporting tags: {e}")
    
    def _import_tags(self, format: str) -> None:
        """Import tags from file."""
        filename = input(f"Enter {format.upper()} filename: ").strip()
        if not filename:
            print("❌ Filename cannot be empty.")
            return
        
        filepath = self.tag_manager.data_dir / filename
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = f.read()
            
            imported_count = self.tag_manager.import_tags(data, format)
            print(f"✅ Imported {imported_count} tags.")
            
        except Exception as e:
            print(f"❌ Error importing tags: {e}")
    
    def _select_tag(self, prompt: str) -> Optional[Tag]:
        """Interactive tag selection."""
        tags = self.tag_manager.get_all_tags()
        
        if not tags:
            print("No tags available.")
            return None
        
        print(f"\n{prompt}")
        for i, tag in enumerate(tags, 1):
            parent_info = ""
            if tag.parent_id:
                parent = self.tag_manager.get_tag_by_id(tag.parent_id)
                if parent:
                    parent_info = f" (child of {parent.name})"
            
            print(f"{i}. {tag.name}{parent_info}")
        
        try:
            choice = int(input("Enter tag number (0 to cancel): "))
            if choice == 0:
                return None
            
            if 1 <= choice <= len(tags):
                return tags[choice - 1]
            else:
                print("❌ Invalid selection.")
                return None
                
        except ValueError:
            print("❌ Invalid input.")
            return None
