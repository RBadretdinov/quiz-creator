"""
Application Controller Module

This module serves as the main controller that coordinates all application components
and manages the user interface flow for the Quiz Application.
"""

import sys
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.menus import MenuSystem
from ui.prompts import InputPrompts
from ui.display import DisplayManager
from ui.tag_interface import TagInterface
from ui.question_type_interface import QuestionTypeInterface
from ui.question_browser import QuestionBrowser
from ui.question_editor import QuestionEditor
from ui.bulk_operations import BulkOperations
from question_manager import QuestionManager
from tag_manager import TagManager
from quiz_engine import QuizEngine
from question_filter import QuestionFilter
from tag_quiz_generator import TagQuizGenerator
from question_versioning import QuestionVersioning
from question_quality_analyzer import QuestionQualityAnalyzer
from question_import_export import QuestionImportExport
try:
    from ocr_processor import OCRProcessor
    OCR_AVAILABLE = True
except ImportError:
    OCRProcessor = None
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)

class AppController:
    """Main application controller that coordinates all components."""
    
    def __init__(self):
        """Initialize the application controller."""
        self.menu_system = MenuSystem()
        self.prompts = InputPrompts()
        self.display = DisplayManager()
        self.question_manager = QuestionManager()
        self.tag_manager = TagManager()
        self.quiz_engine = QuizEngine()
        
        # Enhanced tag management components
        self.question_filter = QuestionFilter(self.tag_manager)
        self.tag_quiz_generator = TagQuizGenerator(self.tag_manager, self.question_filter)
        self.tag_interface = TagInterface(self.tag_manager)
        
        # Enhanced question type management
        self.question_type_interface = QuestionTypeInterface()
        
        # Enhanced question management
        self.question_browser = QuestionBrowser(self.question_manager, self.tag_manager)
        self.question_editor = QuestionEditor(self.question_manager, self.tag_manager, self.prompts, self.display)
        self.bulk_operations = BulkOperations(self.question_manager, self.tag_manager, self.display)
        self.question_versioning = QuestionVersioning()
        self.quality_analyzer = QuestionQualityAnalyzer()
        self.import_export = QuestionImportExport(self.question_manager, self.tag_manager)
        
        if OCR_AVAILABLE:
            self.ocr_processor = OCRProcessor()
        else:
            self.ocr_processor = None
        
        # Application state
        self.running = True
        self.current_session_id = None
        
        logger.info("Application controller initialized")
    
    def run(self):
        """Main application loop."""
        try:
            self.display.display_welcome_message()
            self.menu_system.pause_for_user()
            
            while self.running:
                self._show_main_menu()
                
        except KeyboardInterrupt:
            self._handle_exit()
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.display.display_error_message(f"An error occurred: {e}")
            self.menu_system.pause_for_user()
    
    def _show_main_menu(self):
        """Display and handle main menu."""
        self.menu_system.clear_screen()
        self.menu_system.display_main_menu()
        self.menu_system.display_breadcrumb()
        
        choice = self.menu_system.get_user_choice(1, 9)
        
        if choice == 1:
            self._handle_create_question()
        elif choice == 2:
            self._handle_take_quiz()
        elif choice == 3:
            self._handle_manage_tags()
        elif choice == 4:
            self._handle_enhanced_question_management()
        elif choice == 5:
            self._handle_question_types()
        elif choice == 6:
            self._handle_import_screenshot()
        elif choice == 7:
            self._handle_settings()
        elif choice == 8:
            self._handle_help()
        elif choice == 9:
            self._handle_exit()
    
    def _handle_create_question(self):
        """Handle question creation flow."""
        self.menu_system.clear_screen()
        self.menu_system.display_question_creation_menu()
        self.menu_system.display_breadcrumb()
        
        choice = self.menu_system.get_user_choice(1, 4)
        
        if choice == 1:
            self._create_multiple_choice_question()
        elif choice == 2:
            self._create_true_false_question()
        elif choice == 3:
            self._create_select_all_question()
        elif choice == 4:
            return  # Back to main menu
    
    def _create_multiple_choice_question(self):
        """Create a multiple choice question."""
        try:
            self.display.display_info_message("Creating Multiple Choice Question")
            
            # Get question text
            question_text = self.prompts.prompt_question_text()
            
            # Get answer options
            answers = self.prompts.prompt_answer_options("multiple_choice")
            
            # Get tags
            available_tags = [tag['name'] for tag in self.tag_manager.get_all_tags()]
            tags = self.prompts.prompt_tag_selection(available_tags)
            
            # Create question
            question = self.question_manager.create_question(
                question_text, "multiple_choice", answers, tags
            )
            
            self.display.display_success_message(f"Question created successfully! ID: {question['id'][:8]}...")
            self.menu_system.pause_for_user()
            
        except Exception as e:
            self.display.display_error_message(f"Error creating question: {e}")
            self.menu_system.pause_for_user()
    
    def _create_true_false_question(self):
        """Create a true/false question."""
        try:
            self.display.display_info_message("Creating True/False Question")
            
            # Get question text
            question_text = self.prompts.prompt_question_text()
            
            # Get answer options (pre-defined for true/false)
            answers = self.prompts.prompt_answer_options("true_false")
            
            # Get tags
            available_tags = [tag['name'] for tag in self.tag_manager.get_all_tags()]
            tags = self.prompts.prompt_tag_selection(available_tags)
            
            # Create question
            question = self.question_manager.create_question(
                question_text, "true_false", answers, tags
            )
            
            self.display.display_success_message(f"Question created successfully! ID: {question['id'][:8]}...")
            self.menu_system.pause_for_user()
            
        except Exception as e:
            self.display.display_error_message(f"Error creating question: {e}")
            self.menu_system.pause_for_user()
    
    def _create_select_all_question(self):
        """Create a select all that apply question."""
        try:
            self.display.display_info_message("Creating Select All That Apply Question")
            
            # Get question text
            question_text = self.prompts.prompt_question_text()
            
            # Get answer options
            answers = self.prompts.prompt_answer_options("select_all")
            
            # Get tags
            available_tags = [tag['name'] for tag in self.tag_manager.get_all_tags()]
            tags = self.prompts.prompt_tag_selection(available_tags)
            
            # Create question
            question = self.question_manager.create_question(
                question_text, "select_all", answers, tags
            )
            
            self.display.display_success_message(f"Question created successfully! ID: {question['id'][:8]}...")
            self.menu_system.pause_for_user()
            
        except Exception as e:
            self.display.display_error_message(f"Error creating question: {e}")
            self.menu_system.pause_for_user()
    
    def _handle_take_quiz(self):
        """Handle quiz taking flow."""
        self.menu_system.clear_screen()
        self.menu_system.display_quiz_menu()
        self.menu_system.display_breadcrumb()
        
        choice = self.menu_system.get_user_choice(1, 4)
        
        if choice == 1:
            self._take_quick_quiz()
        elif choice == 2:
            self._take_quiz_by_tags()
        elif choice == 3:
            self._take_custom_quiz()
        elif choice == 4:
            return  # Back to main menu
    
    def _take_quick_quiz(self):
        """Take a quick random quiz."""
        try:
            all_questions = self.question_manager.get_all_questions()
            if not all_questions:
                self.display.display_warning_message("No questions available. Create some questions first!")
                self.menu_system.pause_for_user()
                return
            
            # Get quiz settings
            settings = self.prompts.prompt_quiz_settings()
            num_questions = min(settings['num_questions'], len(all_questions))
            
            # Create randomized quiz
            quiz_questions = self.quiz_engine.create_randomized_quiz(all_questions, num_questions)
            
            # Start quiz session
            session_id = self.quiz_engine.start_quiz(quiz_questions)
            self.current_session_id = session_id
            
            # Take the quiz
            self._run_quiz_session(session_id)
            
        except Exception as e:
            self.display.display_error_message(f"Error starting quiz: {e}")
            self.menu_system.pause_for_user()
    
    def _take_quiz_by_tags(self):
        """Take a quiz filtered by tags."""
        try:
            # Show available tags
            tags = self.tag_manager.get_all_tags()
            if not tags:
                self.display.display_warning_message("No tags available. Create some tags first!")
                self.menu_system.pause_for_user()
                return
            
            self.display.display_tag_list([tag.to_dict() for tag in tags])
            
            # Get tag selection
            available_tags = [tag['name'] for tag in tags]
            selected_tags = self.prompts.prompt_tag_selection(available_tags)
            
            # Get questions by tags
            questions = []
            for tag in selected_tags:
                questions.extend(self.question_manager.get_questions_by_tag(tag))
            
            if not questions:
                self.display.display_warning_message("No questions found with selected tags!")
                self.menu_system.pause_for_user()
                return
            
            # Get quiz settings
            settings = self.prompts.prompt_quiz_settings()
            num_questions = min(settings['num_questions'], len(questions))
            
            # Create randomized quiz
            quiz_questions = self.quiz_engine.create_randomized_quiz(questions, num_questions)
            
            # Start quiz session
            session_id = self.quiz_engine.start_quiz(quiz_questions)
            self.current_session_id = session_id
            
            # Take the quiz
            self._run_quiz_session(session_id)
            
        except Exception as e:
            self.display.display_error_message(f"Error starting quiz: {e}")
            self.menu_system.pause_for_user()
    
    def _take_custom_quiz(self):
        """Take a custom quiz with specific settings."""
        # This would be similar to quick quiz but with more customization options
        self.display.display_info_message("Custom quiz feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _run_quiz_session(self, session_id: str):
        """Run a quiz session."""
        try:
            session = self.quiz_engine.active_sessions[session_id]
            questions = session['questions']
            
            for i, question in enumerate(questions):
                self.menu_system.clear_screen()
                
                # Display question
                self.display.display_question(question, i + 1, len(questions))
                
                # Display progress
                self.display.display_quiz_progress(i + 1, len(questions))
                
                # Get user answer
                user_answer = self._get_user_answer(question)
                
                # Submit answer
                result = self.quiz_engine.submit_answer(session_id, question['id'], user_answer)
                
                # Display feedback
                self.display.display_feedback(
                    result['is_correct'], 
                    result['correct_answers'], 
                    question
                )
                
                self.menu_system.pause_for_user()
            
            # Quiz complete - show results
            self.menu_system.clear_screen()
            self.display.display_results(session)
            self.menu_system.pause_for_user()
            
        except Exception as e:
            self.display.display_error_message(f"Error during quiz: {e}")
            self.menu_system.pause_for_user()
    
    def _get_user_answer(self, question: Dict) -> Any:
        """Get user's answer for a question."""
        question_type = question.get('question_type', 'multiple_choice')
        
        if question_type in ['multiple_choice', 'true_false']:
            # Single answer
            while True:
                try:
                    answer = input("Enter your answer (number): ").strip()
                    answer_num = int(answer)
                    if 1 <= answer_num <= len(question['answers']):
                        return answer_num
                    else:
                        self.display.display_error_message(f"Please enter a number between 1 and {len(question['answers'])}")
                except ValueError:
                    self.display.display_error_message("Please enter a valid number")
        
        elif question_type == 'select_all':
            # Multiple answers
            while True:
                answer = input("Enter your answers (numbers separated by commas): ").strip()
                try:
                    answer_nums = [int(x.strip()) for x in answer.split(',')]
                    # Validate all numbers are in range
                    if all(1 <= num <= len(question['answers']) for num in answer_nums):
                        return answer_nums
                    else:
                        self.display.display_error_message(f"Please enter numbers between 1 and {len(question['answers'])}")
                except ValueError:
                    self.display.display_error_message("Please enter valid numbers separated by commas")
    
    def _handle_manage_tags(self):
        """Handle enhanced tag management flow."""
        while True:
            self.menu_system.clear_screen()
            self.menu_system.display_tag_management_menu()
            self.menu_system.display_breadcrumb()
            
            choice = self.menu_system.get_user_choice(0, 10)
            
            if choice == 0:
                return  # Back to main menu
            elif choice == 1:
                self.tag_interface.view_all_tags(show_hierarchy=True)
                self.menu_system.pause_for_user()
            elif choice == 2:
                self.tag_interface.create_tag_interactive()
                self.menu_system.pause_for_user()
            elif choice == 3:
                self.tag_interface.edit_tag_interactive()
                self.menu_system.pause_for_user()
            elif choice == 4:
                self.tag_interface.delete_tag_interactive()
                self.menu_system.pause_for_user()
            elif choice == 5:
                self.tag_interface.search_tags_interactive()
                self.menu_system.pause_for_user()
            elif choice == 6:
                self.tag_interface.display_tag_statistics()
                self.menu_system.pause_for_user()
            elif choice == 7:
                self.tag_interface.bulk_operations_menu()
            elif choice == 8:
                self.tag_interface.import_export_menu()
            elif choice == 9:
                self._display_tag_hierarchy()
            elif choice == 10:
                self._display_advanced_tag_features()
    
    def _display_tag_hierarchy(self):
        """Display tag hierarchy in a tree structure."""
        self.menu_system.clear_screen()
        print("\n" + "="*60)
        print("🌳 TAG HIERARCHY VIEW")
        print("="*60)
        
        root_tags = self.tag_manager.get_root_tags()
        if not root_tags:
            print("No tags found. Create some tags first!")
            self.menu_system.pause_for_user()
            return
        
        for root_tag in root_tags:
            self._display_tag_tree_recursive(root_tag, 0)
        
        self.menu_system.pause_for_user()
    
    def _display_tag_tree_recursive(self, tag, depth):
        """Display a tag and its children recursively."""
        indent = "  " * depth
        prefix = "├─ " if depth > 0 else "🌳 "
        
        print(f"{indent}{prefix}{tag.name}")
        print(f"{indent}   📊 {tag.question_count} questions, {tag.usage_count} uses")
        
        if tag.description:
            print(f"{indent}   📝 {tag.description}")
        
        if tag.aliases:
            aliases_str = ", ".join(tag.aliases)
            print(f"{indent}   🔖 Aliases: {aliases_str}")
        
        print()
        
        # Display children
        children = self.tag_manager.get_children(tag.id)
        for child in children:
            self._display_tag_tree_recursive(child, depth + 1)
    
    def _display_advanced_tag_features(self):
        """Display advanced tag features and options."""
        self.menu_system.clear_screen()
        print("\n" + "="*60)
        print("⚡ ADVANCED TAG FEATURES")
        print("="*60)
        print()
        print("🔍 Available Features:")
        print("  • Hierarchical tag organization")
        print("  • Tag aliases and alternative names")
        print("  • Usage tracking and analytics")
        print("  • Bulk operations (merge, delete, update)")
        print("  • Import/Export in JSON and CSV formats")
        print("  • Advanced search with operators (AND, OR, NOT)")
        print("  • Tag-based quiz generation")
        print("  • Question filtering by multiple criteria")
        print("  • Tag hierarchy validation")
        print("  • Performance optimization suggestions")
        print()
        print("🎯 Quiz Generation Strategies:")
        print("  • Random selection")
        print("  • Balanced representation")
        print("  • Hierarchical balance")
        print("  • Weighted by usage statistics")
        print("  • Adaptive based on performance")
        print("  • Progressive chronological order")
        print()
        print("📊 Analytics Available:")
        print("  • Tag usage statistics")
        print("  • Hierarchy depth analysis")
        print("  • Recently used tags")
        print("  • Unused tag identification")
        print("  • Performance metrics")
        print()
        
        self.menu_system.pause_for_user()
    
    def _view_all_tags(self):
        """View all tags."""
        tags = self.tag_manager.get_all_tags()
        if tags:
            self.display.display_tag_list([tag.to_dict() for tag in tags])
        else:
            self.display.display_info_message("No tags found. Create some tags first!")
        self.menu_system.pause_for_user()
    
    def _create_new_tag(self):
        """Create a new tag."""
        try:
            tag_name = self.prompts.prompt_new_tag()
            description = input("Enter tag description (optional): ").strip()
            color = input("Enter tag color (hex code, optional): ").strip()
            
            tag = self.tag_manager.create_tag(tag_name, description, color)
            self.display.display_success_message(f"Tag '{tag_name}' created successfully!")
            
        except Exception as e:
            self.display.display_error_message(f"Error creating tag: {e}")
        
        self.menu_system.pause_for_user()
    
    def _edit_tag(self):
        """Edit an existing tag."""
        self.display.display_info_message("Edit tag feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _delete_tag(self):
        """Delete a tag."""
        self.display.display_info_message("Delete tag feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _show_tag_statistics(self):
        """Show tag statistics."""
        self.display.display_info_message("Tag statistics feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _handle_view_question_bank(self):
        """Handle question bank viewing."""
        self.menu_system.clear_screen()
        self.menu_system.display_question_bank_menu()
        self.menu_system.display_breadcrumb()
        
        choice = self.menu_system.get_user_choice(1, 7)
        
        if choice == 1:
            self._view_all_questions()
        elif choice == 2:
            self._search_questions()
        elif choice == 3:
            self._filter_questions_by_tags()
        elif choice == 4:
            self._edit_question()
        elif choice == 5:
            self._delete_question()
        elif choice == 6:
            self._export_questions()
        elif choice == 7:
            return  # Back to main menu
    
    def _view_all_questions(self):
        """View all questions."""
        questions = self.question_manager.get_all_questions()
        if questions:
            self.display.display_question_list(questions)
        else:
            self.display.display_info_message("No questions found. Create some questions first!")
        self.menu_system.pause_for_user()
    
    def _search_questions(self):
        """Search questions."""
        search_term = input("Enter search term: ").strip()
        if search_term:
            results = self.question_manager.search_questions(search_term)
            if results:
                self.display.display_question_list(results)
            else:
                self.display.display_info_message("No questions found matching your search.")
        else:
            self.display.display_error_message("Search term cannot be empty.")
        self.menu_system.pause_for_user()
    
    def _filter_questions_by_tags(self):
        """Filter questions by tags."""
        tags = self.tag_manager.get_all_tags()
        if not tags:
            self.display.display_warning_message("No tags available!")
            self.menu_system.pause_for_user()
            return
        
        self.display.display_tag_list([tag.to_dict() for tag in tags])
        available_tags = [tag['name'] for tag in tags]
        selected_tags = self.prompts.prompt_tag_selection(available_tags)
        
        questions = []
        for tag in selected_tags:
            questions.extend(self.question_manager.get_questions_by_tag(tag))
        
        if questions:
            self.display.display_question_list(questions)
        else:
            self.display.display_info_message("No questions found with selected tags.")
        self.menu_system.pause_for_user()
    
    def _edit_question(self):
        """Edit a question."""
        self.display.display_info_message("Edit question feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _delete_question(self):
        """Delete a question."""
        self.display.display_info_message("Delete question feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _export_questions(self):
        """Export questions."""
        self.display.display_info_message("Export questions feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _handle_enhanced_question_management(self):
        """Handle enhanced question management flow."""
        while True:
            self.menu_system.clear_screen()
            self.question_browser.display_question_browser_menu()
            self.menu_system.display_breadcrumb()
            
            choice = self.menu_system.get_user_choice(0, 6)
            
            if choice == 0:
                return  # Back to main menu
            elif choice == 1:
                self._handle_browse_questions()
            elif choice == 2:
                self._handle_search_questions()
            elif choice == 3:
                self._handle_filter_by_tags()
            elif choice == 4:
                self._handle_sort_options()
            elif choice == 5:
                self._handle_question_statistics()
            elif choice == 6:
                self._handle_bulk_operations()
    
    def _handle_browse_questions(self):
        """Handle question browsing."""
        questions = self.question_manager.get_all_questions()
        if not questions:
            self.display.display_info_message("No questions found.")
            self.menu_system.pause_for_user()
            return
        
        page = 1
        while True:
            self.menu_system.clear_screen()
            self.question_browser.browse_questions(questions, page)
            
            action = input("\nEnter action (n/p/g/f/l/v/e/d/c/s/f/q): ").strip().lower()
            
            if action == 'n':  # Next page
                total_pages = (len(questions) + self.question_browser.page_size - 1) // self.question_browser.page_size
                if page < total_pages:
                    page += 1
            elif action == 'p':  # Previous page
                if page > 1:
                    page -= 1
            elif action == 'g':  # Go to page
                try:
                    new_page = int(input("Enter page number: "))
                    total_pages = (len(questions) + self.question_browser.page_size - 1) // self.question_browser.page_size
                    if 1 <= new_page <= total_pages:
                        page = new_page
                except ValueError:
                    print("Invalid page number.")
            elif action == 'f':  # First page
                page = 1
            elif action == 'l':  # Last page
                total_pages = (len(questions) + self.question_browser.page_size - 1) // self.question_browser.page_size
                page = total_pages
            elif action == 'v':  # View question
                self._handle_view_question(questions, page)
            elif action == 'e':  # Edit question
                self._handle_edit_question(questions, page)
            elif action == 'd':  # Delete question
                self._handle_delete_question(questions, page)
            elif action == 'c':  # Copy question
                self._handle_copy_question(questions, page)
            elif action == 's':  # Search
                self._handle_search_questions()
            elif action == 'f':  # Filter
                self._handle_filter_by_tags()
            elif action == 'q':  # Quit
                break
            else:
                print("Invalid action.")
    
    def _handle_view_question(self, questions, page):
        """Handle viewing a specific question."""
        try:
            selection = input("Enter question number to view: ").strip()
            question = self.question_browser.get_question_by_selection(questions, selection)
            
            if question:
                self.menu_system.clear_screen()
                self.question_editor._display_question_details(question)
                self.menu_system.pause_for_user()
            else:
                print("Invalid question number.")
        except Exception as e:
            print(f"Error viewing question: {e}")
    
    def _handle_edit_question(self, questions, page):
        """Handle editing a specific question."""
        try:
            selection = input("Enter question number to edit: ").strip()
            question = self.question_browser.get_question_by_selection(questions, selection)
            
            if question:
                # Create version before editing
                self.question_versioning.create_version(question, "Before editing")
                
                # Edit the question
                if self.question_editor.edit_question_interactive(question):
                    # Create version after editing
                    self.question_versioning.create_version(question, "After editing")
                    print("Question updated successfully.")
                else:
                    print("Question editing cancelled.")
            else:
                print("Invalid question number.")
        except Exception as e:
            print(f"Error editing question: {e}")
    
    def _handle_delete_question(self, questions, page):
        """Handle deleting a specific question."""
        try:
            selection = input("Enter question number to delete: ").strip()
            question = self.question_browser.get_question_by_selection(questions, selection)
            
            if question:
                if self.question_editor.delete_question_interactive(question):
                    # Remove from current list
                    questions.remove(question)
                    print("Question deleted successfully.")
                else:
                    print("Question deletion cancelled.")
            else:
                print("Invalid question number.")
        except Exception as e:
            print(f"Error deleting question: {e}")
    
    def _handle_copy_question(self, questions, page):
        """Handle copying a specific question."""
        try:
            selection = input("Enter question number to copy: ").strip()
            question = self.question_browser.get_question_by_selection(questions, selection)
            
            if question:
                new_question = self.question_editor.duplicate_question_interactive(question)
                if new_question:
                    questions.append(new_question)
                    print("Question copied successfully.")
                else:
                    print("Question copying cancelled.")
            else:
                print("Invalid question number.")
        except Exception as e:
            print(f"Error copying question: {e}")
    
    def _handle_search_questions(self):
        """Handle question search."""
        results = self.question_browser.search_questions_interactive()
        if results:
            self.menu_system.pause_for_user()
    
    def _handle_filter_by_tags(self):
        """Handle filtering by tags."""
        results = self.question_browser.filter_by_tags_interactive()
        if results:
            self.menu_system.pause_for_user()
    
    def _handle_sort_options(self):
        """Handle sort options."""
        self.question_browser.display_sort_options()
        self.menu_system.pause_for_user()
    
    def _handle_question_statistics(self):
        """Handle question statistics."""
        self.question_browser.display_question_statistics()
        self.menu_system.pause_for_user()
    
    def _handle_bulk_operations(self):
        """Handle bulk operations."""
        while True:
            self.menu_system.clear_screen()
            self.bulk_operations.display_bulk_operations_menu()
            self.menu_system.display_breadcrumb()
            
            choice = self.menu_system.get_user_choice(0, 6)
            
            if choice == 0:
                return  # Back to question management
            elif choice == 1:
                self._handle_bulk_delete()
            elif choice == 2:
                self._handle_bulk_edit_tags()
            elif choice == 3:
                self._handle_bulk_change_type()
            elif choice == 4:
                self._handle_bulk_export()
            elif choice == 5:
                self._handle_bulk_import()
            elif choice == 6:
                self._handle_bulk_duplicate()
    
    def _handle_bulk_delete(self):
        """Handle bulk delete operations."""
        questions = self.question_manager.get_all_questions()
        if not questions:
            self.display.display_info_message("No questions found.")
            self.menu_system.pause_for_user()
            return
        
        # For simplicity, delete all questions (in real implementation, user would select)
        print(f"Selected {len(questions)} questions for bulk deletion.")
        confirm = input("Are you sure you want to delete ALL questions? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            deleted_count = self.bulk_operations.bulk_delete_questions(questions)
            print(f"Bulk deletion completed: {deleted_count} questions deleted.")
        else:
            print("Bulk deletion cancelled.")
        
        self.menu_system.pause_for_user()
    
    def _handle_bulk_edit_tags(self):
        """Handle bulk tag editing."""
        questions = self.question_manager.get_all_questions()
        if not questions:
            self.display.display_info_message("No questions found.")
            self.menu_system.pause_for_user()
            return
        
        updated_count = self.bulk_operations.bulk_edit_tags(questions)
        print(f"Bulk tag editing completed: {updated_count} questions updated.")
        self.menu_system.pause_for_user()
    
    def _handle_bulk_change_type(self):
        """Handle bulk question type changes."""
        questions = self.question_manager.get_all_questions()
        if not questions:
            self.display.display_info_message("No questions found.")
            self.menu_system.pause_for_user()
            return
        
        updated_count = self.bulk_operations.bulk_change_question_type(questions)
        print(f"Bulk type change completed: {updated_count} questions updated.")
        self.menu_system.pause_for_user()
    
    def _handle_bulk_export(self):
        """Handle bulk export operations."""
        questions = self.question_manager.get_all_questions()
        if not questions:
            self.display.display_info_message("No questions found.")
            self.menu_system.pause_for_user()
            return
        
        print("Export formats available:")
        formats = self.import_export.get_export_formats()
        for i, fmt in enumerate(formats, 1):
            print(f"{i}. {fmt['format'].upper()} - {fmt['description']}")
        
        try:
            choice = int(input("Select export format (1-3): "))
            if 1 <= choice <= 3:
                format_type = formats[choice - 1]['format']
                output_path = f"export_questions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                
                if format_type == 'json':
                    success = self.import_export.export_questions_json(questions, output_path)
                elif format_type == 'csv':
                    success = self.import_export.export_questions_csv(questions, output_path)
                elif format_type == 'html':
                    success = self.import_export.export_questions_html(questions, output_path)
                
                if success:
                    print(f"Questions exported successfully to {output_path}")
                else:
                    print("Export failed.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        self.menu_system.pause_for_user()
    
    def _handle_bulk_import(self):
        """Handle bulk import operations."""
        print("Import formats available:")
        formats = self.import_export.get_import_formats()
        for i, fmt in enumerate(formats, 1):
            print(f"{i}. {fmt['format'].upper()} - {fmt['description']}")
        
        try:
            choice = int(input("Select import format (1-2): "))
            if 1 <= choice <= 2:
                format_type = formats[choice - 1]['format']
                file_path = input("Enter file path: ").strip()
                
                if os.path.exists(file_path):
                    if format_type == 'json':
                        result = self.import_export.import_questions_json(file_path)
                    elif format_type == 'csv':
                        result = self.import_export.import_questions_csv(file_path)
                    
                    if result['success']:
                        print(f"Import completed: {result['imported_count']} questions imported.")
                        if result['errors']:
                            print(f"Errors: {len(result['errors'])}")
                    else:
                        print("Import failed.")
                        for error in result['errors']:
                            print(f"  - {error}")
                else:
                    print("File not found.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
        
        self.menu_system.pause_for_user()
    
    def _handle_bulk_duplicate(self):
        """Handle bulk duplication."""
        questions = self.question_manager.get_all_questions()
        if not questions:
            self.display.display_info_message("No questions found.")
            self.menu_system.pause_for_user()
            return
        
        duplicated_count = self.bulk_operations.bulk_duplicate_questions(questions)
        print(f"Bulk duplication completed: {duplicated_count} questions duplicated.")
        self.menu_system.pause_for_user()
    
    def _handle_question_types(self):
        """Handle question type management flow."""
        while True:
            self.menu_system.clear_screen()
            self.question_type_interface.display_question_type_menu()
            self.menu_system.display_breadcrumb()
            
            choice = self.menu_system.get_user_choice(0, 6)
            
            if choice == 0:
                return  # Back to main menu
            elif choice == 1:
                self.question_type_interface.view_question_types()
                self.menu_system.pause_for_user()
            elif choice == 2:
                self.question_type_interface.display_templates_menu()
            elif choice == 3:
                self.question_type_interface.convert_question_type_interactive()
                self.menu_system.pause_for_user()
            elif choice == 4:
                self.question_type_interface.validate_question_interactive()
                self.menu_system.pause_for_user()
            elif choice == 5:
                self._display_question_type_statistics()
            elif choice == 6:
                self.question_type_interface.display_scoring_information()
                self.menu_system.pause_for_user()
    
    def _display_question_type_statistics(self):
        """Display question type statistics."""
        self.menu_system.clear_screen()
        print("\n" + "="*60)
        print("📊 QUESTION TYPE STATISTICS")
        print("="*60)
        
        # Get all questions to analyze
        questions = self.question_manager.get_all_questions()
        
        if not questions:
            print("No questions found to analyze.")
            self.menu_system.pause_for_user()
            return
        
        # Count by question type
        type_counts = {}
        for question in questions:
            question_type = question.get('question_type', 'unknown')
            type_counts[question_type] = type_counts.get(question_type, 0) + 1
        
        print(f"Total Questions: {len(questions)}")
        print("\nQuestion Type Distribution:")
        print("-" * 40)
        
        for question_type, count in sorted(type_counts.items()):
            percentage = (count / len(questions)) * 100
            print(f"{question_type.replace('_', ' ').title():<20}: {count:>3} ({percentage:>5.1f}%)")
        
        # Show type-specific information
        print("\n📋 Question Type Details:")
        print("-" * 40)
        
        type_info = self.question_type_interface.validator.get_question_type_info()
        for question_type, info in type_info.items():
            count = type_counts.get(question_type, 0)
            print(f"\n🔹 {info['name']}:")
            print(f"   Count: {count}")
            print(f"   Description: {info['description']}")
            print(f"   Answer Range: {info['min_answers']}-{info['max_answers']}")
        
        self.menu_system.pause_for_user()
    
    def _handle_import_screenshot(self):
        """Handle screenshot import."""
        if not self.ocr_processor:
            self.display.display_error_message("OCR functionality not available. Please install pytesseract and Pillow.")
            self.menu_system.pause_for_user()
            return
        
        try:
            image_path = self.prompts.prompt_file_path("screenshot")
            
            if not self.ocr_processor.validate_image_format(image_path):
                self.display.display_error_message("Unsupported image format. Please use PNG, JPG, JPEG, TIFF, or BMP.")
                self.menu_system.pause_for_user()
                return
            
            self.display.display_info_message("Processing image with OCR...")
            result = self.ocr_processor.process_screenshot(image_path)
            
            if result['success']:
                questions = result['questions']
                if questions:
                    self.display.display_success_message(f"Extracted {len(questions)} questions from image!")
                    # TODO: Allow user to review and import questions
                else:
                    self.display.display_warning_message("No questions found in the image.")
            else:
                self.display.display_error_message(f"OCR processing failed: {result.get('error', 'Unknown error')}")
            
        except Exception as e:
            self.display.display_error_message(f"Error processing image: {e}")
        
        self.menu_system.pause_for_user()
    
    def _handle_settings(self):
        """Handle settings."""
        self.menu_system.clear_screen()
        self.menu_system.display_settings_menu()
        self.menu_system.display_breadcrumb()
        
        choice = self.menu_system.get_user_choice(1, 5)
        
        if choice == 1:
            self._display_preferences()
        elif choice == 2:
            self._quiz_preferences()
        elif choice == 3:
            self._data_management()
        elif choice == 4:
            self._reset_to_defaults()
        elif choice == 5:
            return  # Back to main menu
    
    def _display_preferences(self):
        """Display preferences."""
        self.display.display_info_message("Display preferences feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _quiz_preferences(self):
        """Quiz preferences."""
        self.display.display_info_message("Quiz preferences feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _data_management(self):
        """Data management."""
        self.display.display_info_message("Data management feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _reset_to_defaults(self):
        """Reset to defaults."""
        self.display.display_info_message("Reset to defaults feature coming soon!")
        self.menu_system.pause_for_user()
    
    def _handle_help(self):
        """Handle help system."""
        self.menu_system.clear_screen()
        self.menu_system.display_help_menu()
        self.menu_system.display_breadcrumb()
        
        choice = self.menu_system.get_user_choice(1, 7)
        
        if choice == 1:
            self.display.display_help_text("getting_started")
        elif choice == 2:
            self.display.display_help_text("question_types")
        elif choice == 3:
            self.display.display_help_text("tag_system")
        elif choice == 4:
            self.display.display_help_text("ocr_import")
        elif choice == 5:
            self.display.display_help_text("keyboard_shortcuts")
        elif choice == 6:
            self.display.display_help_text("troubleshooting")
        elif choice == 7:
            return  # Back to main menu
        
        self.menu_system.pause_for_user()
    
    def _handle_exit(self):
        """Handle application exit."""
        self.display.display_info_message("Thank you for using Quiz Application!")
        self.running = False
