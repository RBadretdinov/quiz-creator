"""
Question Editor

This module provides console-based interfaces for editing, deleting,
and managing individual questions with validation and confirmation.
"""

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from question_type_validator import QuestionTypeValidator

logger = logging.getLogger(__name__)

class QuestionEditor:
    """Console interface for editing and managing questions."""
    
    def __init__(self, question_manager, tag_manager, prompts, display):
        """Initialize the question editor."""
        self.question_manager = question_manager
        self.tag_manager = tag_manager
        self.prompts = prompts
        self.display = display
        self.validator = QuestionTypeValidator()
    
    def edit_question_interactive(self, question: Dict[str, Any]) -> bool:
        """
        Interactive question editing.
        
        Args:
            question: Question to edit
            
        Returns:
            True if question was successfully edited, False otherwise
        """
        print(f"\n{'='*60}")
        print("✏️  EDIT QUESTION")
        print(f"{'='*60}")
        
        # Display current question
        self._display_question_details(question)
        
        print("\nWhat would you like to edit?")
        print("1. Question Text")
        print("2. Question Type")
        print("3. Answers")
        print("4. Tags")
        print("5. Save Changes")
        print("0. Cancel")
        
        while True:
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self._edit_question_text(question)
            elif choice == '2':
                self._edit_question_type(question)
            elif choice == '3':
                self._edit_answers(question)
            elif choice == '4':
                self._edit_tags(question)
            elif choice == '5':
                return self._save_question_changes(question)
            elif choice == '0':
                return False
            else:
                print("Invalid option. Please try again.")
    
    def _display_question_details(self, question: Dict[str, Any]) -> None:
        """Display detailed question information."""
        print(f"\nQuestion ID: {question.get('id', 'Unknown')}")
        print(f"Type: {question.get('question_type', 'Unknown')}")
        print(f"Created: {question.get('created_at', 'Unknown')}")
        print(f"Last Modified: {question.get('last_modified', 'Unknown')}")
        print(f"Usage Count: {question.get('usage_count', 0)}")
        print(f"Tags: {', '.join(question.get('tags', []))}")
        
        print(f"\nQuestion Text:")
        print(f"  {question.get('question_text', 'No text')}")
        
        print(f"\nAnswers:")
        for i, answer in enumerate(question.get('answers', []), 1):
            status = "✅" if answer.get('is_correct', False) else "❌"
            print(f"  {i}. {answer.get('text', 'No text')} {status}")
    
    def _edit_question_text(self, question: Dict[str, Any]) -> None:
        """Edit question text."""
        current_text = question.get('question_text', '')
        print(f"\nCurrent question text:")
        print(f"  {current_text}")
        
        new_text = input("\nEnter new question text: ").strip()
        if new_text:
            question['question_text'] = new_text
            question['last_modified'] = datetime.now().isoformat()
            print("✅ Question text updated.")
        else:
            print("❌ No changes made.")
    
    def _edit_question_type(self, question: Dict[str, Any]) -> None:
        """Edit question type."""
        current_type = question.get('question_type', 'unknown')
        print(f"\nCurrent question type: {current_type}")
        
        # Show available types
        type_info = self.validator.get_question_type_info()
        print("\nAvailable question types:")
        for i, (qtype, info) in enumerate(type_info.items(), 1):
            current = " (current)" if qtype == current_type else ""
            print(f"{i}. {info['name']} - {info['description']}{current}")
        
        try:
            choice = int(input("\nSelect new question type (number): "))
            question_types = list(type_info.keys())
            
            if 1 <= choice <= len(question_types):
                new_type = question_types[choice - 1]
                
                # Validate if conversion is possible
                if new_type != current_type:
                    # Check if answers are compatible
                    validation = self.validator.validate_answers_for_type(new_type, question.get('answers', []))
                    if validation['is_valid']:
                        question['question_type'] = new_type
                        question['last_modified'] = datetime.now().isoformat()
                        print(f"✅ Question type changed to: {new_type}")
                    else:
                        print(f"❌ Cannot change to {new_type}: {validation['errors']}")
                        print("You may need to modify the answers first.")
                else:
                    print("❌ No changes made.")
            else:
                print("❌ Invalid selection.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def _edit_answers(self, question: Dict[str, Any]) -> None:
        """Edit question answers."""
        answers = question.get('answers', [])
        
        print(f"\nCurrent answers:")
        for i, answer in enumerate(answers, 1):
            status = "✅" if answer.get('is_correct', False) else "❌"
            print(f"  {i}. {answer.get('text', 'No text')} {status}")
        
        print("\nAnswer editing options:")
        print("1. Add Answer")
        print("2. Edit Answer")
        print("3. Delete Answer")
        print("4. Reorder Answers")
        print("0. Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self._add_answer(question)
        elif choice == '2':
            self._edit_answer(question)
        elif choice == '3':
            self._delete_answer(question)
        elif choice == '4':
            self._reorder_answers(question)
        elif choice == '0':
            return
        else:
            print("Invalid option.")
    
    def _add_answer(self, question: Dict[str, Any]) -> None:
        """Add a new answer to the question."""
        answers = question.get('answers', [])
        
        if len(answers) >= 8:  # Maximum answers
            print("❌ Maximum number of answers reached (8).")
            return
        
        text = input("Enter answer text: ").strip()
        if not text:
            print("❌ Answer text cannot be empty.")
            return
        
        is_correct = input("Is this answer correct? (y/n): ").strip().lower() == 'y'
        
        new_answer = {
            'text': text,
            'is_correct': is_correct
        }
        
        answers.append(new_answer)
        question['answers'] = answers
        question['last_modified'] = datetime.now().isoformat()
        
        print("✅ Answer added successfully.")
    
    def _edit_answer(self, question: Dict[str, Any]) -> None:
        """Edit an existing answer."""
        answers = question.get('answers', [])
        
        if not answers:
            print("❌ No answers to edit.")
            return
        
        try:
            index = int(input(f"Enter answer number to edit (1-{len(answers)}): ")) - 1
            
            if 0 <= index < len(answers):
                answer = answers[index]
                
                print(f"\nCurrent answer: {answer.get('text', 'No text')}")
                print(f"Currently correct: {'Yes' if answer.get('is_correct', False) else 'No'}")
                
                new_text = input("Enter new answer text (or press Enter to keep current): ").strip()
                if new_text:
                    answer['text'] = new_text
                
                correct_input = input("Is this answer correct? (y/n/Enter to keep current): ").strip().lower()
                if correct_input in ['y', 'n']:
                    answer['is_correct'] = correct_input == 'y'
                
                question['last_modified'] = datetime.now().isoformat()
                print("✅ Answer updated successfully.")
            else:
                print("❌ Invalid answer number.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def _delete_answer(self, question: Dict[str, Any]) -> None:
        """Delete an answer from the question."""
        answers = question.get('answers', [])
        
        if len(answers) <= 2:  # Minimum answers
            print("❌ Cannot delete answer. Questions must have at least 2 answers.")
            return
        
        try:
            index = int(input(f"Enter answer number to delete (1-{len(answers)}): ")) - 1
            
            if 0 <= index < len(answers):
                answer = answers[index]
                print(f"\nAnswer to delete: {answer.get('text', 'No text')}")
                
                confirm = input("Are you sure you want to delete this answer? (y/n): ").strip().lower()
                if confirm == 'y':
                    del answers[index]
                    question['answers'] = answers
                    question['last_modified'] = datetime.now().isoformat()
                    print("✅ Answer deleted successfully.")
                else:
                    print("❌ Deletion cancelled.")
            else:
                print("❌ Invalid answer number.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def _reorder_answers(self, question: Dict[str, Any]) -> None:
        """Reorder answers in the question."""
        answers = question.get('answers', [])
        
        if len(answers) < 2:
            print("❌ Need at least 2 answers to reorder.")
            return
        
        print("\nCurrent answer order:")
        for i, answer in enumerate(answers, 1):
            print(f"  {i}. {answer.get('text', 'No text')}")
        
        try:
            from_idx = int(input("Enter answer number to move: ")) - 1
            to_idx = int(input("Enter new position: ")) - 1
            
            if 0 <= from_idx < len(answers) and 0 <= to_idx < len(answers):
                # Move answer
                answer = answers.pop(from_idx)
                answers.insert(to_idx, answer)
                
                question['answers'] = answers
                question['last_modified'] = datetime.now().isoformat()
                
                print("✅ Answers reordered successfully.")
            else:
                print("❌ Invalid positions.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def _edit_tags(self, question: Dict[str, Any]) -> None:
        """Edit question tags."""
        current_tags = question.get('tags', [])
        print(f"\nCurrent tags: {', '.join(current_tags) if current_tags else 'None'}")
        
        # Show available tags
        all_tags = self.tag_manager.get_all_tags()
        if all_tags:
            print("\nAvailable tags:")
            for i, tag in enumerate(all_tags, 1):
                print(f"  {i}. {tag.name} ({tag.question_count} questions)")
        
        print("\nTag editing options:")
        print("1. Add Tag")
        print("2. Remove Tag")
        print("3. Replace All Tags")
        print("0. Back")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self._add_tag(question, all_tags)
        elif choice == '2':
            self._remove_tag(question)
        elif choice == '3':
            self._replace_tags(question, all_tags)
        elif choice == '0':
            return
        else:
            print("Invalid option.")
    
    def _add_tag(self, question: Dict[str, Any], all_tags: List) -> None:
        """Add a tag to the question."""
        current_tags = question.get('tags', [])
        
        if len(current_tags) >= 10:  # Maximum tags
            print("❌ Maximum number of tags reached (10).")
            return
        
        tag_input = input("Enter tag name or number: ").strip()
        
        if tag_input.isdigit():
            # Number provided
            try:
                tag_num = int(tag_input)
                if 1 <= tag_num <= len(all_tags):
                    tag_name = all_tags[tag_num - 1].name
                    if tag_name not in current_tags:
                        current_tags.append(tag_name)
                        question['tags'] = current_tags
                        question['last_modified'] = datetime.now().isoformat()
                        print(f"✅ Tag '{tag_name}' added.")
                    else:
                        print(f"❌ Tag '{tag_name}' already exists.")
                else:
                    print("❌ Invalid tag number.")
            except ValueError:
                print("❌ Invalid input.")
        else:
            # Tag name provided
            if tag_input and tag_input not in current_tags:
                current_tags.append(tag_input)
                question['tags'] = current_tags
                question['last_modified'] = datetime.now().isoformat()
                print(f"✅ Tag '{tag_input}' added.")
            else:
                print("❌ Tag name cannot be empty or already exists.")
    
    def _remove_tag(self, question: Dict[str, Any]) -> None:
        """Remove a tag from the question."""
        current_tags = question.get('tags', [])
        
        if not current_tags:
            print("❌ No tags to remove.")
            return
        
        print("\nCurrent tags:")
        for i, tag in enumerate(current_tags, 1):
            print(f"  {i}. {tag}")
        
        try:
            tag_num = int(input("Enter tag number to remove: ")) - 1
            
            if 0 <= tag_num < len(current_tags):
                removed_tag = current_tags.pop(tag_num)
                question['tags'] = current_tags
                question['last_modified'] = datetime.now().isoformat()
                print(f"✅ Tag '{removed_tag}' removed.")
            else:
                print("❌ Invalid tag number.")
                
        except ValueError:
            print("❌ Invalid input.")
    
    def _replace_tags(self, question: Dict[str, Any], all_tags: List) -> None:
        """Replace all tags for the question."""
        current_tags = question.get('tags', [])
        print(f"\nCurrent tags: {', '.join(current_tags) if current_tags else 'None'}")
        
        new_tags_input = input("Enter new tags (comma-separated): ").strip()
        if new_tags_input:
            new_tags = [tag.strip() for tag in new_tags_input.split(',') if tag.strip()]
            
            if len(new_tags) <= 10:  # Maximum tags
                question['tags'] = new_tags
                question['last_modified'] = datetime.now().isoformat()
                print(f"✅ Tags replaced: {', '.join(new_tags)}")
            else:
                print("❌ Too many tags. Maximum 10 allowed.")
        else:
            print("❌ No tags provided.")
    
    def _save_question_changes(self, question: Dict[str, Any]) -> bool:
        """Save changes to the question."""
        # Validate the updated question
        validation = self.validator.validate_answers_for_type(
            question.get('question_type', 'unknown'),
            question.get('answers', [])
        )
        
        if not validation['is_valid']:
            print(f"❌ Cannot save question: {validation['errors']}")
            return False
        
        try:
            # Update the question in the manager
            self.question_manager.update_question(question['id'], question)
            print("✅ Question saved successfully.")
            return True
        except Exception as e:
            print(f"❌ Error saving question: {e}")
            return False
    
    def delete_question_interactive(self, question: Dict[str, Any]) -> bool:
        """
        Interactive question deletion with confirmation.
        
        Args:
            question: Question to delete
            
        Returns:
            True if question was deleted, False otherwise
        """
        print(f"\n{'='*60}")
        print("🗑️  DELETE QUESTION")
        print(f"{'='*60}")
        
        # Display question details
        self._display_question_details(question)
        
        print(f"\n⚠️  WARNING: This action cannot be undone!")
        print(f"Question ID: {question.get('id', 'Unknown')}")
        print(f"Usage Count: {question.get('usage_count', 0)}")
        
        # Double confirmation
        confirm1 = input("\nAre you sure you want to delete this question? (yes/no): ").strip().lower()
        if confirm1 != 'yes':
            print("❌ Deletion cancelled.")
            return False
        
        confirm2 = input("Type 'DELETE' to confirm: ").strip()
        if confirm2 != 'DELETE':
            print("❌ Deletion cancelled.")
            return False
        
        try:
            # Delete the question
            self.question_manager.delete_question(question['id'])
            print("✅ Question deleted successfully.")
            return True
        except Exception as e:
            print(f"❌ Error deleting question: {e}")
            return False
    
    def duplicate_question_interactive(self, question: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Interactive question duplication.
        
        Args:
            question: Question to duplicate
            
        Returns:
            New question if successful, None otherwise
        """
        print(f"\n{'='*60}")
        print("📋 DUPLICATE QUESTION")
        print(f"{'='*60}")
        
        # Display original question
        self._display_question_details(question)
        
        print("\nDuplication options:")
        print("1. Exact Copy")
        print("2. Copy with New Text")
        print("3. Copy as Template")
        print("0. Cancel")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            return self._create_exact_copy(question)
        elif choice == '2':
            return self._create_copy_with_new_text(question)
        elif choice == '3':
            return self._create_template_copy(question)
        elif choice == '0':
            return None
        else:
            print("Invalid option.")
            return None
    
    def _create_exact_copy(self, question: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create an exact copy of the question."""
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
            created_question = self.question_manager.create_question(
                new_question['question_text'],
                new_question['question_type'],
                new_question['answers'],
                new_question['tags']
            )
            
            print("✅ Question duplicated successfully.")
            return created_question
            
        except Exception as e:
            print(f"❌ Error duplicating question: {e}")
            return None
    
    def _create_copy_with_new_text(self, question: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a copy with new question text."""
        new_text = input("Enter new question text: ").strip()
        if not new_text:
            print("❌ Question text cannot be empty.")
            return None
        
        try:
            # Create new question with new text
            created_question = self.question_manager.create_question(
                new_text,
                question['question_type'],
                question['answers'],
                question['tags']
            )
            
            print("✅ Question duplicated with new text.")
            return created_question
            
        except Exception as e:
            print(f"❌ Error duplicating question: {e}")
            return None
    
    def _create_template_copy(self, question: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a template copy (same structure, different content)."""
        new_text = input("Enter new question text: ").strip()
        if not new_text:
            print("❌ Question text cannot be empty.")
            return None
        
        # Keep the same answer structure but with placeholder text
        template_answers = []
        for i, answer in enumerate(question.get('answers', []), 1):
            new_answer_text = input(f"Enter text for answer {i} (or press Enter for placeholder): ").strip()
            if not new_answer_text:
                new_answer_text = f"Answer {i}"
            
            template_answers.append({
                'text': new_answer_text,
                'is_correct': answer.get('is_correct', False)
            })
        
        try:
            # Create new question
            created_question = self.question_manager.create_question(
                new_text,
                question['question_type'],
                template_answers,
                question['tags']
            )
            
            print("✅ Template created successfully.")
            return created_question
            
        except Exception as e:
            print(f"❌ Error creating template: {e}")
            return None
