"""
Bulk Operations

This module provides console-based interfaces for performing bulk operations
on multiple questions with progress tracking and confirmation.
"""

from typing import List, Dict, Any, Optional, Callable
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BulkOperations:
    """Console interface for bulk question operations."""
    
    def __init__(self, question_manager, tag_manager, display):
        """Initialize bulk operations."""
        self.question_manager = question_manager
        self.tag_manager = tag_manager
        self.display = display
    
    def display_bulk_operations_menu(self) -> None:
        """Display the bulk operations menu."""
        print("\n" + "="*60)
        print("⚡ BULK OPERATIONS")
        print("="*60)
        print("1. Bulk Delete Questions")
        print("2. Bulk Edit Tags")
        print("3. Bulk Change Question Type")
        print("4. Bulk Export Questions")
        print("5. Bulk Import Questions")
        print("6. Bulk Duplicate Questions")
        print("0. Back")
        print("-"*60)
    
    def bulk_delete_questions(self, questions: List[Dict[str, Any]]) -> int:
        """
        Bulk delete questions with confirmation and progress tracking.
        
        Args:
            questions: List of questions to delete
            
        Returns:
            Number of questions successfully deleted
        """
        if not questions:
            print("❌ No questions selected for deletion.")
            return 0
        
        print(f"\n{'='*60}")
        print("🗑️  BULK DELETE QUESTIONS")
        print(f"{'='*60}")
        
        # Show summary
        print(f"Selected {len(questions)} questions for deletion:")
        for i, question in enumerate(questions[:5], 1):  # Show first 5
            text = question.get('question_text', 'No text')[:50]
            if len(question.get('question_text', '')) > 50:
                text += "..."
            print(f"  {i}. {text}")
        
        if len(questions) > 5:
            print(f"  ... and {len(questions) - 5} more")
        
        # Show usage statistics
        total_usage = sum(q.get('usage_count', 0) for q in questions)
        print(f"\nTotal usage count: {total_usage}")
        
        # Confirmation
        print(f"\n⚠️  WARNING: This action cannot be undone!")
        confirm = input(f"Are you sure you want to delete {len(questions)} questions? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Bulk deletion cancelled.")
            return 0
        
        # Perform deletion with progress tracking
        deleted_count = 0
        failed_count = 0
        
        print(f"\nDeleting questions...")
        for i, question in enumerate(questions, 1):
            try:
                self.question_manager.delete_question(question['id'])
                deleted_count += 1
                print(f"  ✅ {i}/{len(questions)}: Deleted question {question['id'][:8]}...")
            except Exception as e:
                failed_count += 1
                print(f"  ❌ {i}/{len(questions)}: Failed to delete {question['id'][:8]}... - {e}")
        
        print(f"\n📊 Bulk deletion completed:")
        print(f"  Successfully deleted: {deleted_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total processed: {len(questions)}")
        
        return deleted_count
    
    def bulk_edit_tags(self, questions: List[Dict[str, Any]]) -> int:
        """
        Bulk edit tags for multiple questions.
        
        Args:
            questions: List of questions to edit
            
        Returns:
            Number of questions successfully updated
        """
        if not questions:
            print("❌ No questions selected for tag editing.")
            return 0
        
        print(f"\n{'='*60}")
        print("🏷️  BULK EDIT TAGS")
        print(f"{'='*60}")
        
        print(f"Selected {len(questions)} questions for tag editing.")
        
        # Show tag editing options
        print("\nTag editing options:")
        print("1. Add tags to all questions")
        print("2. Remove tags from all questions")
        print("3. Replace all tags")
        print("4. Merge tags")
        print("0. Cancel")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            return self._bulk_add_tags(questions)
        elif choice == '2':
            return self._bulk_remove_tags(questions)
        elif choice == '3':
            return self._bulk_replace_tags(questions)
        elif choice == '4':
            return self._bulk_merge_tags(questions)
        elif choice == '0':
            return 0
        else:
            print("❌ Invalid option.")
            return 0
    
    def _bulk_add_tags(self, questions: List[Dict[str, Any]]) -> int:
        """Add tags to all selected questions."""
        # Show available tags
        all_tags = self.tag_manager.get_all_tags()
        if all_tags:
            print("\nAvailable tags:")
            for i, tag in enumerate(all_tags, 1):
                print(f"  {i}. {tag.name} ({tag.question_count} questions)")
        
        tags_input = input("\nEnter tags to add (comma-separated): ").strip()
        if not tags_input:
            print("❌ No tags provided.")
            return 0
        
        tags_to_add = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        updated_count = 0
        print(f"\nAdding tags to questions...")
        
        for i, question in enumerate(questions, 1):
            try:
                current_tags = question.get('tags', [])
                new_tags = list(set(current_tags + tags_to_add))  # Remove duplicates
                
                if len(new_tags) <= 10:  # Maximum tags
                    question['tags'] = new_tags
                    question['last_modified'] = datetime.now().isoformat()
                    self.question_manager.update_question(question['id'], question)
                    updated_count += 1
                    print(f"  ✅ {i}/{len(questions)}: Added tags to question {question['id'][:8]}...")
                else:
                    print(f"  ❌ {i}/{len(questions)}: Too many tags for question {question['id'][:8]}...")
            except Exception as e:
                print(f"  ❌ {i}/{len(questions)}: Failed to update question {question['id'][:8]}... - {e}")
        
        print(f"\n📊 Bulk tag addition completed:")
        print(f"  Successfully updated: {updated_count}")
        print(f"  Total processed: {len(questions)}")
        
        return updated_count
    
    def _bulk_remove_tags(self, questions: List[Dict[str, Any]]) -> int:
        """Remove tags from all selected questions."""
        tags_input = input("\nEnter tags to remove (comma-separated): ").strip()
        if not tags_input:
            print("❌ No tags provided.")
            return 0
        
        tags_to_remove = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        updated_count = 0
        print(f"\nRemoving tags from questions...")
        
        for i, question in enumerate(questions, 1):
            try:
                current_tags = question.get('tags', [])
                new_tags = [tag for tag in current_tags if tag not in tags_to_remove]
                
                question['tags'] = new_tags
                question['last_modified'] = datetime.now().isoformat()
                self.question_manager.update_question(question['id'], question)
                updated_count += 1
                print(f"  ✅ {i}/{len(questions)}: Removed tags from question {question['id'][:8]}...")
            except Exception as e:
                print(f"  ❌ {i}/{len(questions)}: Failed to update question {question['id'][:8]}... - {e}")
        
        print(f"\n📊 Bulk tag removal completed:")
        print(f"  Successfully updated: {updated_count}")
        print(f"  Total processed: {len(questions)}")
        
        return updated_count
    
    def _bulk_replace_tags(self, questions: List[Dict[str, Any]]) -> int:
        """Replace all tags for selected questions."""
        tags_input = input("\nEnter new tags (comma-separated): ").strip()
        if not tags_input:
            print("❌ No tags provided.")
            return 0
        
        new_tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
        
        if len(new_tags) > 10:
            print("❌ Too many tags. Maximum 10 allowed.")
            return 0
        
        updated_count = 0
        print(f"\nReplacing tags for questions...")
        
        for i, question in enumerate(questions, 1):
            try:
                question['tags'] = new_tags
                question['last_modified'] = datetime.now().isoformat()
                self.question_manager.update_question(question['id'], question)
                updated_count += 1
                print(f"  ✅ {i}/{len(questions)}: Replaced tags for question {question['id'][:8]}...")
            except Exception as e:
                print(f"  ❌ {i}/{len(questions)}: Failed to update question {question['id'][:8]}... - {e}")
        
        print(f"\n📊 Bulk tag replacement completed:")
        print(f"  Successfully updated: {updated_count}")
        print(f"  Total processed: {len(questions)}")
        
        return updated_count
    
    def _bulk_merge_tags(self, questions: List[Dict[str, Any]]) -> int:
        """Merge tags for selected questions."""
        print("\nTag merging combines all tags from selected questions.")
        
        # Collect all unique tags
        all_tags = set()
        for question in questions:
            all_tags.update(question.get('tags', []))
        
        print(f"Found {len(all_tags)} unique tags across all questions:")
        for tag in sorted(all_tags):
            print(f"  - {tag}")
        
        confirm = input(f"\nApply all {len(all_tags)} tags to all {len(questions)} questions? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Tag merging cancelled.")
            return 0
        
        updated_count = 0
        print(f"\nMerging tags for questions...")
        
        for i, question in enumerate(questions, 1):
            try:
                question['tags'] = list(all_tags)
                question['last_modified'] = datetime.now().isoformat()
                self.question_manager.update_question(question['id'], question)
                updated_count += 1
                print(f"  ✅ {i}/{len(questions)}: Merged tags for question {question['id'][:8]}...")
            except Exception as e:
                print(f"  ❌ {i}/{len(questions)}: Failed to update question {question['id'][:8]}... - {e}")
        
        print(f"\n📊 Bulk tag merging completed:")
        print(f"  Successfully updated: {updated_count}")
        print(f"  Total processed: {len(questions)}")
        
        return updated_count
    
    def bulk_change_question_type(self, questions: List[Dict[str, Any]]) -> int:
        """
        Bulk change question type for multiple questions.
        
        Args:
            questions: List of questions to update
            
        Returns:
            Number of questions successfully updated
        """
        if not questions:
            print("❌ No questions selected for type change.")
            return 0
        
        print(f"\n{'='*60}")
        print("🔄 BULK CHANGE QUESTION TYPE")
        print(f"{'='*60}")
        
        # Show current type distribution
        type_counts = {}
        for question in questions:
            qtype = question.get('question_type', 'unknown')
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        print("Current question type distribution:")
        for qtype, count in sorted(type_counts.items()):
            print(f"  {qtype}: {count} questions")
        
        # Show available types
        print("\nAvailable question types:")
        print("1. multiple_choice")
        print("2. true_false")
        print("3. select_all")
        
        try:
            choice = int(input("\nSelect new question type (1-3): "))
            type_mapping = {1: 'multiple_choice', 2: 'true_false', 3: 'select_all'}
            
            if choice not in type_mapping:
                print("❌ Invalid selection.")
                return 0
            
            new_type = type_mapping[choice]
            
            # Confirmation
            confirm = input(f"\nChange {len(questions)} questions to '{new_type}'? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Type change cancelled.")
                return 0
            
            # Perform type change with progress tracking
            updated_count = 0
            failed_count = 0
            
            print(f"\nChanging question types...")
            for i, question in enumerate(questions, 1):
                try:
                    # Check if conversion is possible
                    from question_type_validator import QuestionTypeValidator
                    validator = QuestionTypeValidator()
                    validation = validator.validate_answers_for_type(new_type, question.get('answers', []))
                    
                    if validation['is_valid']:
                        question['question_type'] = new_type
                        question['last_modified'] = datetime.now().isoformat()
                        self.question_manager.update_question(question['id'], question)
                        updated_count += 1
                        print(f"  ✅ {i}/{len(questions)}: Changed type for question {question['id'][:8]}...")
                    else:
                        failed_count += 1
                        print(f"  ❌ {i}/{len(questions)}: Cannot convert question {question['id'][:8]}... - {validation['errors']}")
                except Exception as e:
                    failed_count += 1
                    print(f"  ❌ {i}/{len(questions)}: Failed to update question {question['id'][:8]}... - {e}")
            
            print(f"\n📊 Bulk type change completed:")
            print(f"  Successfully updated: {updated_count}")
            print(f"  Failed: {failed_count}")
            print(f"  Total processed: {len(questions)}")
            
            return updated_count
            
        except ValueError:
            print("❌ Invalid input.")
            return 0
    
    def bulk_duplicate_questions(self, questions: List[Dict[str, Any]]) -> int:
        """
        Bulk duplicate questions.
        
        Args:
            questions: List of questions to duplicate
            
        Returns:
            Number of questions successfully duplicated
        """
        if not questions:
            print("❌ No questions selected for duplication.")
            return 0
        
        print(f"\n{'='*60}")
        print("📋 BULK DUPLICATE QUESTIONS")
        print(f"{'='*60}")
        
        print(f"Selected {len(questions)} questions for duplication.")
        
        # Show duplication options
        print("\nDuplication options:")
        print("1. Exact copies")
        print("2. Copies with prefix")
        print("3. Template copies")
        print("0. Cancel")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            return self._bulk_exact_duplicate(questions)
        elif choice == '2':
            return self._bulk_duplicate_with_prefix(questions)
        elif choice == '3':
            return self._bulk_template_duplicate(questions)
        elif choice == '0':
            return 0
        else:
            print("❌ Invalid option.")
            return 0
    
    def _bulk_exact_duplicate(self, questions: List[Dict[str, Any]]) -> int:
        """Create exact copies of all questions."""
        confirm = input(f"\nCreate exact copies of {len(questions)} questions? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Duplication cancelled.")
            return 0
        
        duplicated_count = 0
        print(f"\nDuplicating questions...")
        
        for i, question in enumerate(questions, 1):
            try:
                # Create new question with same data
                new_question = question.copy()
                new_question['id'] = None  # Let the manager generate new ID
                new_question['created_at'] = datetime.now().isoformat()
                new_question['last_modified'] = datetime.now().isoformat()
                new_question['usage_count'] = 0
                
                # Add "(Copy)" to the question text
                new_question['question_text'] = f"{question.get('question_text', '')} (Copy)"
                
                # Create the question
                self.question_manager.create_question(
                    new_question['question_text'],
                    new_question['question_type'],
                    new_question['answers'],
                    new_question['tags']
                )
                
                duplicated_count += 1
                print(f"  ✅ {i}/{len(questions)}: Duplicated question {question['id'][:8]}...")
            except Exception as e:
                print(f"  ❌ {i}/{len(questions)}: Failed to duplicate question {question['id'][:8]}... - {e}")
        
        print(f"\n📊 Bulk duplication completed:")
        print(f"  Successfully duplicated: {duplicated_count}")
        print(f"  Total processed: {len(questions)}")
        
        return duplicated_count
    
    def _bulk_duplicate_with_prefix(self, questions: List[Dict[str, Any]]) -> int:
        """Create copies with a custom prefix."""
        prefix = input("Enter prefix for duplicated questions: ").strip()
        if not prefix:
            print("❌ Prefix cannot be empty.")
            return 0
        
        confirm = input(f"\nCreate copies with prefix '{prefix}' for {len(questions)} questions? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Duplication cancelled.")
            return 0
        
        duplicated_count = 0
        print(f"\nDuplicating questions with prefix...")
        
        for i, question in enumerate(questions, 1):
            try:
                # Create new question with prefix
                new_text = f"{prefix}: {question.get('question_text', '')}"
                
                self.question_manager.create_question(
                    new_text,
                    question['question_type'],
                    question['answers'],
                    question['tags']
                )
                
                duplicated_count += 1
                print(f"  ✅ {i}/{len(questions)}: Duplicated question {question['id'][:8]}...")
            except Exception as e:
                print(f"  ❌ {i}/{len(questions)}: Failed to duplicate question {question['id'][:8]}... - {e}")
        
        print(f"\n📊 Bulk duplication completed:")
        print(f"  Successfully duplicated: {duplicated_count}")
        print(f"  Total processed: {len(questions)}")
        
        return duplicated_count
    
    def _bulk_template_duplicate(self, questions: List[Dict[str, Any]]) -> int:
        """Create template copies (same structure, placeholder content)."""
        print("\nTemplate duplication creates questions with the same structure but placeholder content.")
        confirm = input(f"Create template copies for {len(questions)} questions? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Duplication cancelled.")
            return 0
        
        duplicated_count = 0
        print(f"\nCreating template copies...")
        
        for i, question in enumerate(questions, 1):
            try:
                # Create template with placeholder content
                template_text = f"Template: {question.get('question_text', '')}"
                
                # Create template answers with placeholders
                template_answers = []
                for j, answer in enumerate(question.get('answers', []), 1):
                    template_answers.append({
                        'text': f"Answer {j}",
                        'is_correct': answer.get('is_correct', False)
                    })
                
                self.question_manager.create_question(
                    template_text,
                    question['question_type'],
                    template_answers,
                    question['tags']
                )
                
                duplicated_count += 1
                print(f"  ✅ {i}/{len(questions)}: Created template for question {question['id'][:8]}...")
            except Exception as e:
                print(f"  ❌ {i}/{len(questions)}: Failed to create template for question {question['id'][:8]}... - {e}")
        
        print(f"\n📊 Bulk template creation completed:")
        print(f"  Successfully created: {duplicated_count}")
        print(f"  Total processed: {len(questions)}")
        
        return duplicated_count
