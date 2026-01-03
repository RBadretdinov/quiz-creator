"""
Menu System Module

This module handles the console menu display and navigation for the Quiz Application.
"""

import sys
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MenuSystem:
    """Handles console menu display and navigation."""
    
    def __init__(self):
        """Initialize the menu system."""
        self.current_menu = "main"
        self.menu_stack = []
        self.breadcrumbs = []
        logger.info("Menu system initialized")
    
    def display_main_menu(self) -> None:
        """Display the main application menu."""
        self.current_menu = "main"
        self.breadcrumbs = ["Main Menu"]
        
        print("\n" + "="*60)
        print("           QUIZ APPLICATION - MAIN MENU")
        print("="*60)
        print()
        print("1. Create Question")
        print("2. Take Quiz")
        print("3. Manage Tags")
        print("4. Enhanced Question Management")
        print("5. Question Types (Not Implemented)")
        print("6. Database Management")
        print("7. Analytics Dashboard")
        print("8. Import from Screenshot (Partially Implemented)")
        print("9. Settings (Not Implemented)")
        print("10. Help")
        print("0. Exit")
        print()
        print("-"*60)
    
    def display_question_creation_menu(self) -> None:
        """Display the question creation menu."""
        self.current_menu = "create_question"
        self.breadcrumbs = ["Main Menu", "Create Question"]
        
        print("\n" + "="*60)
        print("           CREATE NEW QUESTION")
        print("="*60)
        print()
        print("1. Multiple Choice Question")
        print("2. True/False Question")
        print("3. Select All That Apply Question")
        print("4. Back to Main Menu")
        print()
        print("-"*60)
    
    def display_quiz_menu(self) -> None:
        """Display the quiz taking menu."""
        self.current_menu = "take_quiz"
        self.breadcrumbs = ["Main Menu", "Take Quiz"]
        
        print("\n" + "="*60)
        print("           TAKE QUIZ")
        print("="*60)
        print()
        print("1. Quick Quiz (Random Questions)")
        print("2. Quiz by Tags")
        print("3. Custom Quiz")
        print("4. Back to Main Menu")
        print()
        print("-"*60)
    
    def display_tag_management_menu(self) -> None:
        """Display the enhanced tag management menu."""
        self.current_menu = "manage_tags"
        self.breadcrumbs = ["Main Menu", "Manage Tags"]
        
        print("\n" + "="*60)
        print("           ENHANCED TAG MANAGEMENT")
        print("="*60)
        print()
        print("1. View All Tags (Hierarchical)")
        print("2. Create New Tag")
        print("3. Edit Tag")
        print("4. Delete Tag")
        print("5. Search Tags")
        print("6. Tag Statistics (Not Implemented)")
        print("7. Bulk Operations (Not Implemented)")
        print("8. Import/Export Tags (Not Implemented)")
        print("9. Tag Hierarchy View (Not Implemented)")
        print("10. Advanced Tag Features (Not Implemented)")
        print("0. Back to Main Menu")
        print()
        print("-"*60)
    
    def display_question_bank_menu(self) -> None:
        """Display the question bank management menu."""
        self.current_menu = "question_bank"
        self.breadcrumbs = ["Main Menu", "Question Bank"]
        
        print("\n" + "="*60)
        print("           ENHANCED QUESTION MANAGEMENT")
        print("="*60)
        print("1. Browse Questions")
        print("2. Search Questions")
        print("3. Edit Question")
        print("4. Delete Question")
        print("5. Question Statistics")
        print("6. Bulk Operations (Not Implemented)")
        print("7. Import/Export Questions (Not Implemented)")
        print("0. Back to Main Menu")
        print("="*60)
    
    def display_settings_menu(self) -> None:
        """Display the settings menu."""
        self.current_menu = "settings"
        self.breadcrumbs = ["Main Menu", "Settings"]
        
        print("\n" + "="*60)
        print("           SETTINGS")
        print("="*60)
        print()
        print("1. Display Preferences")
        print("2. Quiz Preferences")
        print("3. Data Management")
        print("4. Reset to Defaults")
        print("5. Back to Main Menu")
        print()
        print("-"*60)
    
    def display_help_menu(self) -> None:
        """Display the help menu."""
        self.current_menu = "help"
        self.breadcrumbs = ["Main Menu", "Help"]
        
        print("\n" + "="*60)
        print("           HELP & DOCUMENTATION")
        print("="*60)
        print()
        print("1. Getting Started")
        print("2. Question Types")
        print("3. Tag System")
        print("4. OCR Import")
        print("5. Keyboard Shortcuts")
        print("6. Troubleshooting")
        print("7. Back to Main Menu")
        print()
        print("-"*60)
    
    def display_breadcrumb(self) -> None:
        """Display the current navigation breadcrumb."""
        if self.breadcrumbs:
            breadcrumb_str = " > ".join(self.breadcrumbs)
            print(f"\n📍 {breadcrumb_str}")
    
    def get_user_choice(self, min_choice: int = 1, max_choice: int = 8) -> int:
        """
        Get user menu choice with validation.
        
        Args:
            min_choice: Minimum valid choice number
            max_choice: Maximum valid choice number
            
        Returns:
            User's choice as integer
        """
        while True:
            try:
                choice = input(f"Enter your choice ({min_choice}-{max_choice}): ").strip()
                
                if not choice:
                    print("❌ Please enter a choice.")
                    continue
                
                choice_num = int(choice)
                
                if min_choice <= choice_num <= max_choice:
                    return choice_num
                else:
                    print(f"❌ Please enter a number between {min_choice} and {max_choice}.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)
    
    def display_confirmation(self, message: str) -> bool:
        """
        Display a confirmation prompt.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if user confirms, False otherwise
        """
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
    
    def display_success_message(self, message: str) -> None:
        """Display a success message."""
        print(f"✅ {message}")
    
    def display_error_message(self, message: str) -> None:
        """Display an error message."""
        print(f"❌ {message}")
    
    def display_warning_message(self, message: str) -> None:
        """Display a warning message."""
        print(f"⚠️  {message}")
    
    def display_info_message(self, message: str) -> None:
        """Display an info message."""
        print(f"ℹ️  {message}")
    
    def clear_screen(self) -> None:
        """Clear the console screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def pause_for_user(self, message: str = "Press Enter to continue...") -> None:
        """Pause and wait for user input."""
        input(f"\n{message}")
    
    def display_progress_bar(self, current: int, total: int, width: int = 50) -> None:
        """
        Display a progress bar.
        
        Args:
            current: Current progress value
            total: Total value
            width: Width of progress bar in characters
        """
        if total == 0:
            return
        
        progress = current / total
        filled_width = int(width * progress)
        bar = "█" * filled_width + "░" * (width - filled_width)
        percentage = int(progress * 100)
        
        print(f"\rProgress: [{bar}] {percentage}% ({current}/{total})", end="", flush=True)
        
        if current == total:
            print()  # New line when complete
