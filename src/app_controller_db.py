"""
Database-Integrated Application Controller

This module provides a database-integrated application controller that uses SQLite
for persistent storage while maintaining compatibility with the existing interface.
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
from database_manager import DatabaseManager
from question_manager_db import QuestionManagerDB
from tag_manager_db import TagManagerDB
from quiz_engine import QuizEngine
from question_filter import QuestionFilter
from tag_quiz_generator import TagQuizGenerator
from question_versioning import QuestionVersioning
from question_quality_analyzer import QuestionQualityAnalyzer
from question_import_export import QuestionImportExport
from analytics import AnalyticsEngine, AnalyticsDashboard

try:
    from ocr_processor import OCRProcessor
    OCR_AVAILABLE = True
except ImportError:
    OCRProcessor = None
    OCR_AVAILABLE = False

logger = logging.getLogger(__name__)

class AppControllerDB:
    """Database-integrated application controller."""
    
    def __init__(self, database_path: str = "data/quiz.db", json_data_path: str = "data"):
        """
        Initialize the database-integrated application controller.
        
        Args:
            database_path: Path to SQLite database file
            json_data_path: Path to JSON data files for migration
        """
        # Initialize database manager
        self.db_manager = DatabaseManager(database_path, json_data_path)
        
        # Initialize UI components
        self.menu_system = MenuSystem()
        self.prompts = InputPrompts()
        self.display = DisplayManager()
        
        # Initialize database-integrated managers
        self.question_manager = QuestionManagerDB(self.db_manager)
        self.tag_manager = TagManagerDB(self.db_manager)
        
        # Initialize other components
        self.quiz_engine = QuizEngine()
        self.question_filter = QuestionFilter(self.tag_manager)
        self.tag_quiz_generator = TagQuizGenerator(self.tag_manager, self.question_filter)
        self.question_versioning = QuestionVersioning()
        self.quality_analyzer = QuestionQualityAnalyzer()
        self.import_export = QuestionImportExport(self.question_manager, self.tag_manager)
        
        # Initialize UI interfaces
        self.tag_interface = TagInterface(self.tag_manager)
        self.question_type_interface = QuestionTypeInterface()
        self.question_browser = QuestionBrowser(self.question_manager, self.tag_manager)
        self.question_editor = QuestionEditor(self.question_manager, self.tag_manager, self.prompts, self.display)
        self.bulk_operations = BulkOperations(self.question_manager, self.tag_manager, self.display)
        
        # Initialize analytics components
        self.analytics_engine = AnalyticsEngine(self.db_manager)
        self.analytics_dashboard = AnalyticsDashboard(self.analytics_engine, self.display, self.prompts)
        
        # Initialize OCR processor if available
        if OCR_AVAILABLE:
            self.ocr_processor = OCRProcessor()
        else:
            self.ocr_processor = None
        
        # Application state
        self.running = False
        self.current_user = None
        
        logger.info("Database-integrated application controller initialized")
    
    def initialize(self) -> bool:
        """
        Initialize the application and database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize database
            if not self.db_manager.initialize():
                logger.error("Failed to initialize database")
                return False
            
            # Initialize quiz engine with database managers
            self.quiz_engine.question_manager = self.question_manager
            self.quiz_engine.tag_manager = self.tag_manager
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            return False
    
    def run(self):
        """Run the main application loop."""
        try:
            # Initialize application
            if not self.initialize():
                self.display.show_error("Failed to initialize application. Please check the logs.")
                return
            
            self.running = True
            logger.info("Starting application main loop")
            
            # Show welcome message
            self.display.show_welcome()
            
            # Main application loop
            while self.running:
                try:
                    self._show_main_menu()
                except KeyboardInterrupt:
                    self.display.show_message("\n\nApplication interrupted by user.")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    self.display.show_error(f"An error occurred: {e}")
                    if not self.prompts.get_yes_no_input("Continue running?"):
                        break
            
            logger.info("Application main loop ended")
            
        except Exception as e:
            logger.error(f"Fatal error in application: {e}")
            self.display.show_error(f"Fatal error: {e}")
        finally:
            self.shutdown()
    
    def _show_main_menu(self):
        """Display and handle the main menu."""
        self.menu_system.display_main_menu()
        choice = self.prompts.get_menu_choice(10)
        
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
            self._handle_database_management()
        elif choice == 7:
            self._handle_analytics()
        elif choice == 8:
            self._handle_import_screenshot()
        elif choice == 9:
            self._handle_settings()
        elif choice == 10:
            self._handle_help()
        elif choice == 0:
            self._handle_exit()
        else:
            self.display.show_error("Invalid choice. Please try again.")
    
    def _handle_create_question(self):
        """Handle question creation."""
        try:
            self.display.show_section_header("Create New Question")
            print("\n[Tip: Type 'cancel' at any step to cancel question creation]")
            
            # Get question details
            question_text = self.prompts.prompt_question_text()
            if question_text is None:
                self.display.show_message("Question creation cancelled.")
                return
            if not question_text:
                self.display.show_error("Question text cannot be empty.")
                return
            
            question_type = self.prompts.prompt_question_type()
            if question_type is None:
                self.display.show_message("Question creation cancelled.")
                return
            
            # Get answers based on question type
            answers = self.prompts.get_answers_for_type(question_type)
            if answers is None:
                self.display.show_message("Question creation cancelled.")
                return
            if not answers:
                self.display.show_message("Question creation cancelled.")
                return
            
            # Get tags
            tags = self.prompts.get_tag_selection()
            if tags is None:
                self.display.show_message("Question creation cancelled.")
                return
            
            # Create question
            try:
                question = self.question_manager.create_question(
                    question_text, question_type, answers, tags
                )
                
                self.display.show_success(f"Question created successfully!")
                self.display.show_question_summary(question)
                
                # Create tags if they don't exist and update usage counts
                for tag_name in tags:
                    tag = self.tag_manager.get_tag_by_name(tag_name)
                    if not tag:
                        # Create the tag if it doesn't exist
                        try:
                            tag_id = self.tag_manager.create_tag(tag_name)
                            if tag_id:
                                # Get the newly created tag
                                tag = self.tag_manager.get_tag(tag_id)
                                logger.info(f"Auto-created tag: {tag_name}")
                            else:
                                # Tag creation failed - likely validation error
                                self.display.show_error(f"Could not create tag '{tag_name}'. It may be a reserved word or too short. Please use a different tag name.")
                                logger.warning(f"Failed to create tag '{tag_name}' - validation failed")
                                continue
                        except Exception as e:
                            self.display.show_error(f"Could not create tag '{tag_name}': {e}")
                            logger.warning(f"Failed to auto-create tag '{tag_name}': {e}")
                            continue
                    
                    # Update tag usage count and question count
                    if tag:
                        self.tag_manager.increment_usage_count(tag['id'])
                        # Recalculate question count from actual questions to ensure accuracy
                        self.tag_manager.recalculate_question_count(tag['id'])
                
            except Exception as e:
                self.display.show_error(f"Failed to create question: {e}")
                
        except Exception as e:
            logger.error(f"Error in create question: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _filter_valid_questions(self, questions: List[Dict]) -> List[Dict]:
        """
        Filter out invalid questions that shouldn't appear in quizzes.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            List of valid questions
        """
        valid_questions = []
        
        for question in questions:
            # Check if question has required fields
            question_text = question.get('question_text', '').strip()
            answers = question.get('answers', [])
            
            # Skip if no question text
            if not question_text:
                logger.warning(f"Skipping question {question.get('id', 'unknown')}: missing question_text")
                continue
            
            # Skip if no answers or invalid answers
            if not answers or not isinstance(answers, list):
                logger.warning(f"Skipping question {question.get('id', 'unknown')}: missing or invalid answers")
                continue
            
            # Check that all answers have text
            valid_answers = True
            for answer in answers:
                if not isinstance(answer, dict) or not answer.get('text', '').strip():
                    valid_answers = False
                    break
            
            if not valid_answers:
                logger.warning(f"Skipping question {question.get('id', 'unknown')}: answers missing text")
                continue
            
            valid_questions.append(question)
        
        return valid_questions
    
    def _handle_take_quiz(self):
        """Handle quiz taking."""
        try:
            self.display.show_section_header("Take Quiz")
            
            # Get all questions and filter to only valid ones
            all_questions = self.question_manager.get_all_questions()
            if not all_questions:
                self.display.show_error("No questions available. Please create some questions first.")
                return
            
            # Filter to only valid questions
            questions = self._filter_valid_questions(all_questions)
            
            if not questions:
                self.display.show_error("No valid questions available. Please create some complete questions first.")
                return
            
            # Warn if there are invalid questions
            invalid_count = len(all_questions) - len(questions)
            if invalid_count > 0:
                self.display.show_info(f"Note: {invalid_count} invalid question(s) were excluded from the quiz.")
            
            # Get quiz configuration
            max_available = len(questions)
            num_questions = self.prompts.get_number_input(
                f"How many questions? (1-{max_available})", 
                min_val=1, max_val=max_available
            )
            if num_questions is None:
                return
            
            # Warn if user requests more than available
            if num_questions > max_available:
                self.display.show_error(f"Only {max_available} valid question(s) available. Quiz will include all available questions.")
                num_questions = max_available
            
            # Generate randomized quiz (questions and answers randomized per implementation plan)
            quiz_questions = self.quiz_engine.create_randomized_quiz(questions, num_questions)
            
            if not quiz_questions:
                self.display.show_error("Failed to generate quiz.")
                return
            
            # Start quiz session
            session_id = self.quiz_engine.start_quiz(quiz_questions)
            if not session_id:
                self.display.show_error("Failed to start quiz session.")
                return
            
            # Run quiz
            self._run_quiz_session(session_id)
            
        except Exception as e:
            logger.error(f"Error in take quiz: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _run_quiz_session(self, session_id: str):
        """Run a quiz session."""
        try:
            session = self.quiz_engine.get_session(session_id)
            if not session:
                self.display.show_error("Quiz session not found.")
                return
            
            self.display.show_quiz_start(session)
            
            # Answer questions
            for i, question in enumerate(session['questions'], 1):
                self.display.show_question(question, i, len(session['questions']))
                
                # Get user answer (returns comma-separated indices)
                user_answer = self.prompts.get_answer_input(question)
                if user_answer is None:
                    self.display.show_message("Quiz cancelled.")
                    return
                
                # Parse comma-separated indices
                try:
                    answer_indices = [int(idx) for idx in user_answer.split(',') if idx.strip()]
                except ValueError:
                    self.display.show_error("Invalid answer format.")
                    continue
                
                if not answer_indices:
                    self.display.show_error("Please select at least one answer.")
                    continue
                
                # Submit answer with indices
                result = self.quiz_engine.submit_answer(session_id, question['id'], answer_indices)
                if result:
                    self.display.show_immediate_feedback(result)
                    
                    # Update question usage count
                    self.question_manager.increment_usage_count(question['id'])
            
            # Show final results
            final_score = self.quiz_engine.calculate_score(session)
            self.display.show_final_results(final_score)
            
        except Exception as e:
            logger.error(f"Error in quiz session: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_manage_tags(self):
        """Handle tag management."""
        try:
            while True:
                self.menu_system.display_tag_management_menu()
                choice = self.prompts.get_menu_choice(10)
                
                if choice == 1:
                    self._handle_view_all_tags()
                elif choice == 2:
                    self._handle_create_tag()
                elif choice == 3:
                    self._handle_edit_tag()
                elif choice == 4:
                    self._handle_delete_tag()
                elif choice == 5:
                    self._handle_search_tags()
                elif choice == 6:
                    self._handle_tag_statistics()
                elif choice == 7:
                    self._handle_bulk_tag_operations()
                elif choice == 8:
                    self._handle_import_export_tags()
                elif choice == 9:
                    self._handle_tag_hierarchy_view()
                elif choice == 10:
                    self._handle_advanced_tag_features()
                elif choice == 0:
                    break
                else:
                    self.display.show_error("Invalid choice. Please try again.")
                    
        except Exception as e:
            logger.error(f"Error in tag management: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_view_all_tags(self):
        """Handle viewing all tags."""
        try:
            tags = self.tag_manager.get_all_tags()
            if not tags:
                self.display.show_message("No tags found.")
                return
            
            self.display.show_tags_list(tags)
            
        except Exception as e:
            logger.error(f"Error viewing tags: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_create_tag(self):
        """Handle tag creation."""
        try:
            name = self.prompts.get_text_input("Enter tag name:")
            if not name:
                return
            
            description = self.prompts.get_text_input("Enter tag description (optional):")
            color = self.prompts.get_text_input("Enter tag color (hex, optional):")
            
            tag_id = self.tag_manager.create_tag(name, description, color)
            if tag_id:
                self.display.show_success(f"Tag '{name}' created successfully!")
            else:
                self.display.show_error("Failed to create tag.")
                
        except Exception as e:
            logger.error(f"Error creating tag: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_edit_tag(self):
        """Handle tag editing."""
        try:
            tags = self.tag_manager.get_all_tags()
            if not tags:
                self.display.show_message("No tags found.")
                return
            
            self.display.show_tags_list(tags)
            tag_name = self.prompts.get_text_input("Enter tag name to edit:")
            
            tag = self.tag_manager.get_tag_by_name(tag_name)
            if not tag:
                self.display.show_error("Tag not found.")
                return
            
            # Get updated information
            new_name = self.prompts.get_text_input(f"Enter new name (current: {tag['name']}):")
            new_description = self.prompts.get_text_input(f"Enter new description (current: {tag.get('description', '')}):")
            new_color = self.prompts.get_text_input(f"Enter new color (current: {tag.get('color', '')}):")
            
            # Update tag
            success = self.tag_manager.update_tag(
                tag['id'],
                name=new_name if new_name else None,
                description=new_description if new_description else None,
                color=new_color if new_color else None
            )
            
            if success:
                self.display.show_success(f"Tag updated successfully!")
            else:
                self.display.show_error("Failed to update tag.")
                
        except Exception as e:
            logger.error(f"Error editing tag: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_delete_tag(self):
        """Handle tag deletion."""
        try:
            tags = self.tag_manager.get_all_tags()
            if not tags:
                self.display.show_message("No tags found.")
                return
            
            self.display.show_tags_list(tags)
            tag_name = self.prompts.get_text_input("Enter tag name to delete:")
            
            tag = self.tag_manager.get_tag_by_name(tag_name)
            if not tag:
                self.display.show_error("Tag not found.")
                return
            
            # Confirm deletion
            if self.prompts.get_yes_no_input(f"Are you sure you want to delete tag '{tag_name}'?"):
                success = self.tag_manager.delete_tag(tag['id'])
                if success:
                    self.display.show_success(f"Tag '{tag_name}' deleted successfully!")
                else:
                    self.display.show_error("Failed to delete tag.")
            else:
                self.display.show_message("Tag deletion cancelled.")
                
        except Exception as e:
            logger.error(f"Error deleting tag: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_search_tags(self):
        """Handle tag searching."""
        try:
            search_term = self.prompts.get_text_input("Enter search term:")
            if not search_term:
                return
            
            results = self.tag_manager.search_tags(search_term)
            if results:
                self.display.show_tags_list(results)
            else:
                self.display.show_message("No tags found matching your search.")
                
        except Exception as e:
            logger.error(f"Error searching tags: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_bulk_tag_operations(self):
        """Handle bulk tag operations."""
        try:
            self.display.show_message("Bulk tag operations not yet implemented.")
            self.display.show_message("This feature will allow bulk editing, deleting, merging,")
            self.display.show_message("or updating multiple tags at once.")
        except Exception as e:
            logger.error(f"Error in bulk tag operations: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_tag_statistics(self):
        """Handle tag statistics display."""
        try:
            self.display.show_message("Tag statistics not yet implemented.")
            self.display.show_message("This feature will show detailed statistics about tag usage,")
            self.display.show_message("question counts per tag, and tag performance metrics.")
        except Exception as e:
            logger.error(f"Error in tag statistics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_import_export_tags(self):
        """Handle tag import/export."""
        try:
            self.display.show_message("Tag import/export not yet implemented.")
            self.display.show_message("This feature will allow importing and exporting tags")
            self.display.show_message("in JSON, CSV, or other formats.")
        except Exception as e:
            logger.error(f"Error in tag import/export: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_tag_hierarchy_view(self):
        """Handle tag hierarchy view display."""
        try:
            self.display.show_message("Tag hierarchy view not yet implemented.")
            self.display.show_message("This feature will display tags in a hierarchical structure,")
            self.display.show_message("showing parent-child relationships between tags.")
        except Exception as e:
            logger.error(f"Error in tag hierarchy view: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_advanced_tag_features(self):
        """Handle advanced tag features."""
        try:
            self.display.show_message("Advanced tag features not yet implemented.")
            self.display.show_message("This feature will include tag aliases, tag merging,")
            self.display.show_message("tag suggestions, and other advanced tag management tools.")
        except Exception as e:
            logger.error(f"Error in advanced tag features: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_enhanced_question_management(self):
        """Handle enhanced question management."""
        try:
            while True:
                self.menu_system.display_question_bank_menu()
                choice = self.prompts.get_menu_choice(7)
                
                if choice == 0:
                    break  # Back to Main Menu
                elif choice == 1:
                    self._handle_browse_questions()
                elif choice == 2:
                    self._handle_search_questions()
                elif choice == 3:
                    self._handle_edit_question()
                elif choice == 4:
                    self._handle_delete_question()
                elif choice == 5:
                    self._handle_question_statistics()
                elif choice == 6:
                    self._handle_bulk_operations()
                elif choice == 7:
                    self._handle_import_export_questions()
                else:
                    self.display.show_error("Invalid choice. Please try again.")
                    
        except Exception as e:
            logger.error(f"Error in enhanced question management: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_browse_questions(self):
        """Handle question browsing with pagination."""
        try:
            # Use QuestionBrowser for better browsing experience with pagination
            self.question_browser.browse_questions()
            
        except Exception as e:
            logger.error(f"Error browsing questions: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_search_questions(self):
        """Handle question searching."""
        try:
            search_term = self.prompts.get_text_input("Enter search term:")
            if not search_term:
                return
            
            results = self.question_manager.search_questions(search_term)
            if results:
                self.display.show_questions_list(results)
            else:
                self.display.show_message("No questions found matching your search.")
                
        except Exception as e:
            logger.error(f"Error searching questions: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_edit_question(self):
        """Handle question editing."""
        try:
            # Get all questions for selection
            questions = self.question_manager.get_all_questions()
            if not questions:
                self.display.show_message("No questions available to edit.")
                return
            
            # Display questions for selection
            self.display.show_questions_list(questions)
            
            # Get question selection
            question_num = self.prompts.get_number_input(
                f"Select question to edit (1-{len(questions)}):",
                min_val=1,
                max_val=len(questions)
            )
            if question_num is None:
                return
            
            # Get selected question (convert to 0-based index)
            selected_question = questions[question_num - 1]
            
            # Use question editor to edit
            success = self.question_editor.edit_question_interactive(selected_question)
            if success:
                self.display.show_success("Question updated successfully!")
            else:
                self.display.show_message("Question edit cancelled or failed.")
                
        except Exception as e:
            logger.error(f"Error editing question: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_delete_question(self):
        """Handle question deletion."""
        try:
            # Get all questions for selection
            questions = self.question_manager.get_all_questions()
            if not questions:
                self.display.show_message("No questions available to delete.")
                return
            
            # Display questions for selection
            self.display.show_questions_list(questions)
            
            # Get question selection
            question_num = self.prompts.get_number_input(
                f"Select question to delete (1-{len(questions)}):",
                min_val=1,
                max_val=len(questions)
            )
            if question_num is None:
                return
            
            # Get selected question (convert to 0-based index)
            selected_question = questions[question_num - 1]
            
            # Use question editor to delete (has built-in confirmation)
            success = self.question_editor.delete_question_interactive(selected_question)
            if success:
                self.display.show_success("Question deleted successfully!")
                # Recalculate tag counts for tags that were associated with this question
                tags = selected_question.get('tags', [])
                for tag_name in tags:
                    tag = self.tag_manager.get_tag_by_name(tag_name)
                    if tag:
                        self.tag_manager.recalculate_question_count(tag['id'])
            else:
                self.display.show_message("Question deletion cancelled.")
                
        except Exception as e:
            logger.error(f"Error deleting question: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_question_statistics(self):
        """Handle question statistics."""
        try:
            stats = self.question_manager.get_question_statistics()
            self.display.show_question_statistics(stats)
            
        except Exception as e:
            logger.error(f"Error showing question statistics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_bulk_operations(self):
        """Handle bulk question operations."""
        try:
            self.display.show_message("Bulk question operations not yet implemented.")
            self.display.show_message("This feature will allow bulk editing, deleting, tagging,")
            self.display.show_message("duplicating, or updating multiple questions at once.")
        except Exception as e:
            logger.error(f"Error in bulk question operations: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_import_export_questions(self):
        """Handle question import/export."""
        try:
            self.display.show_message("Question import/export not yet implemented.")
            self.display.show_message("This feature will allow importing and exporting questions")
            self.display.show_message("in JSON, CSV, or other formats for backup and sharing.")
        except Exception as e:
            logger.error(f"Error in question import/export: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_question_versioning(self):
        """Handle question versioning."""
        try:
            self.display.show_message("Question versioning not yet implemented.")
        except Exception as e:
            logger.error(f"Error in question versioning: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_quality_analysis(self):
        """Handle quality analysis."""
        try:
            self.display.show_message("Quality analysis not yet implemented.")
        except Exception as e:
            logger.error(f"Error in quality analysis: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_question_types(self):
        """Handle question type management."""
        try:
            self.display.show_message("Question type management not yet implemented.")
        except Exception as e:
            logger.error(f"Error in question type management: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_database_management(self):
        """Handle database management operations."""
        try:
            while True:
                self.display.show_section_header("Database Management")
                self.display.show_message("1. Database Information")
                self.display.show_message("2. Create Backup")
                self.display.show_message("3. Restore Backup")
                self.display.show_message("4. List Backups")
                self.display.show_message("5. Database Maintenance")
                self.display.show_message("6. Health Check")
                self.display.show_message("0. Back to Main Menu")
                
                choice = self.prompts.get_menu_choice(6)
                
                if choice == 1:
                    self._handle_database_info()
                elif choice == 2:
                    self._handle_create_backup()
                elif choice == 3:
                    self._handle_restore_backup()
                elif choice == 4:
                    self._handle_list_backups()
                elif choice == 5:
                    self._handle_database_maintenance()
                elif choice == 6:
                    self._handle_health_check()
                elif choice == 0:
                    break
                else:
                    self.display.show_error("Invalid choice. Please try again.")
                    
        except Exception as e:
            logger.error(f"Error in database management: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_database_info(self):
        """Handle database information display."""
        try:
            db_info = self.db_manager.get_database_info()
            self.display.show_database_info(db_info)
            
        except Exception as e:
            logger.error(f"Error showing database info: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_create_backup(self):
        """Handle database backup creation."""
        try:
            backup_name = self.prompts.get_text_input("Enter backup name (optional):")
            compress = self.prompts.get_yes_no_input("Compress backup?")
            
            result = self.db_manager.create_backup(backup_name, compress)
            if result['success']:
                self.display.show_success(f"Backup created successfully: {result['backup_name']}")
            else:
                self.display.show_error(f"Failed to create backup: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_restore_backup(self):
        """Handle database backup restoration."""
        try:
            backups = self.db_manager.list_backups()
            if not backups:
                self.display.show_message("No backups available.")
                return
            
            self.display.show_backups_list(backups)
            backup_path = self.prompts.get_text_input("Enter backup path:")
            
            if self.prompts.get_yes_no_input("Are you sure you want to restore this backup?"):
                result = self.db_manager.restore_backup(backup_path)
                if result['success']:
                    self.display.show_success("Backup restored successfully!")
                else:
                    self.display.show_error(f"Failed to restore backup: {result.get('error', 'Unknown error')}")
            else:
                self.display.show_message("Backup restoration cancelled.")
                
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_list_backups(self):
        """Handle listing available backups."""
        try:
            backups = self.db_manager.list_backups()
            if backups:
                self.display.show_backups_list(backups)
            else:
                self.display.show_message("No backups available.")
                
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_database_maintenance(self):
        """Handle database maintenance."""
        try:
            if self.prompts.get_yes_no_input("Run database maintenance? This may take a few minutes."):
                result = self.db_manager.perform_maintenance()
                if result['success']:
                    self.display.show_success("Database maintenance completed successfully!")
                    self.display.show_maintenance_results(result)
                else:
                    self.display.show_error("Database maintenance failed.")
            else:
                self.display.show_message("Database maintenance cancelled.")
                
        except Exception as e:
            logger.error(f"Error in database maintenance: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_health_check(self):
        """Handle database health check."""
        try:
            health_score = self.db_manager.get_database_health_score()
            self.display.show_health_score(health_score)
            
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_analytics(self):
        """Handle analytics dashboard."""
        try:
            self.analytics_dashboard.show_main_dashboard()
        except Exception as e:
            logger.error(f"Error in analytics dashboard: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_import_screenshot(self):
        """Handle screenshot import (OCR functionality)."""
        try:
            self.display.show_section_header("Import from Screenshot")
            
            if not OCR_AVAILABLE:
                self.display.show_error("OCR functionality is not available. Please install pytesseract and Pillow.")
                return
            
            # Get image file path
            image_path = self.prompts.get_text_input("Enter the path to the image file:")
            if not image_path:
                self.display.show_error("Image path cannot be empty.")
                return
            
            # Process image with OCR
            self.display.show_message("Processing image with OCR...")
            result = self.ocr_processor.process_image(image_path)
            
            if result['success']:
                self.display.show_success("OCR processing completed successfully!")
                self.display.show_message(f"Extracted text: {result['text']}")
                
                # Ask if user wants to create questions from extracted text
                if self.prompts.get_yes_no_input("Would you like to create questions from the extracted text?"):
                    # This would need additional implementation for parsing questions from text
                    self.display.show_message("Question creation from OCR text is not yet implemented.")
            else:
                self.display.show_error(f"OCR processing failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in screenshot import: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_settings(self):
        """Handle application settings."""
        try:
            self.display.show_section_header("Settings")
            self.display.show_message("Settings functionality is not yet implemented.")
            self.display.show_message("This feature will allow you to configure:")
            self.display.show_message("- Theme preferences")
            self.display.show_message("- Display options")
            self.display.show_message("- Default quiz settings")
            self.display.show_message("- User preferences")
            
        except Exception as e:
            logger.error(f"Error in settings: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_help(self):
        """Handle help and documentation."""
        try:
            self.display.show_section_header("Help & Documentation")
            self.display.show_message("Welcome to the Quiz Application!")
            self.display.show_message("\nAvailable features:")
            self.display.show_message("1. Create Questions - Add new quiz questions")
            self.display.show_message("2. Take Quiz - Practice with questions")
            self.display.show_message("3. Manage Tags - Organize questions with tags")
            self.display.show_message("4. Enhanced Question Management - Advanced question operations")
            self.display.show_message("5. Question Types - Learn about different question formats")
            self.display.show_message("6. Database Management - Backup and maintain your data")
            self.display.show_message("7. Analytics Dashboard - View your progress and statistics")
            self.display.show_message("8. Import from Screenshot - Extract questions from images")
            self.display.show_message("9. Settings - Configure application preferences")
            self.display.show_message("10. Help - This help screen")
            
            self.display.show_message("\nFor detailed documentation, see the docs/ folder in your installation.")
            
        except Exception as e:
            logger.error(f"Error in help: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def _handle_exit(self):
        """Handle application exit."""
        try:
            if self.prompts.get_yes_no_input("Are you sure you want to exit?"):
                self.running = False
                self.display.show_message("Thank you for using the Quiz Application!")
            else:
                self.display.show_message("Exit cancelled.")
                
        except Exception as e:
            logger.error(f"Error in exit: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def shutdown(self):
        """Shutdown the application."""
        try:
            if hasattr(self, 'db_manager'):
                self.db_manager.close()
            logger.info("Application shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

