"""
User Input Prompts Module

This module handles user input prompts and validation for the Quiz Application.
"""

import re
from typing import List, Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)

class InputPrompts:
    """Handles user input prompts and validation."""
    
    def __init__(self):
        """Initialize the input prompts system."""
        logger.info("Input prompts system initialized")
    
    def prompt_question_text(self) -> str:
        """
        Prompt user for question text with validation.
        
        Returns:
            Validated question text
        """
        while True:
            question_text = input("\n📝 Enter the question text (10-500 characters): ").strip()
            
            if not question_text:
                print("❌ Question text cannot be empty.")
                continue
            
            if len(question_text) < 10:
                print("❌ Question text must be at least 10 characters long.")
                continue
            
            if len(question_text) > 500:
                print("❌ Question text cannot exceed 500 characters.")
                continue
            
            return question_text
    
    def prompt_question_type(self) -> str:
        """
        Prompt user for question type.
        
        Returns:
            Selected question type
        """
        print("\n📋 Select question type:")
        print("1. Multiple Choice (one correct answer)")
        print("2. True/False")
        print("3. Select All That Apply (multiple correct answers)")
        
        while True:
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                return "multiple_choice"
            elif choice == "2":
                return "true_false"
            elif choice == "3":
                return "select_all"
            else:
                print("❌ Please enter 1, 2, or 3.")
    
    def prompt_answer_options(self, question_type: str) -> List[Dict[str, Any]]:
        """
        Prompt user for answer options based on question type.
        
        Args:
            question_type: Type of question being created
            
        Returns:
            List of answer dictionaries
        """
        answers = []
        
        if question_type == "true_false":
            # Pre-defined true/false options
            answers = [
                {"id": "answer_1", "text": "True", "is_correct": False},
                {"id": "answer_2", "text": "False", "is_correct": False}
            ]
            print("\n📝 True/False question - marking correct answer:")
            print("1. True")
            print("2. False")
            
            while True:
                choice = input("Which is correct? (1-2): ").strip()
                if choice == "1":
                    answers[0]["is_correct"] = True
                    break
                elif choice == "2":
                    answers[1]["is_correct"] = True
                    break
                else:
                    print("❌ Please enter 1 or 2.")
        
        else:
            # Multiple choice or select all
            min_answers = 2
            max_answers = 6
            
            print(f"\n📝 Enter answer options ({min_answers}-{max_answers} options):")
            print("(Enter empty line when done)")
            
            for i in range(max_answers):
                answer_text = input(f"Answer {i+1}: ").strip()
                
                if not answer_text:
                    if len(answers) < min_answers:
                        print(f"❌ You need at least {min_answers} answer options.")
                        continue
                    else:
                        break
                
                answer = {
                    "id": f"answer_{i+1}",
                    "text": answer_text,
                    "is_correct": False
                }
                answers.append(answer)
            
            # Mark correct answers
            self._mark_correct_answers(answers, question_type)
        
        return answers
    
    def _mark_correct_answers(self, answers: List[Dict], question_type: str) -> None:
        """
        Mark correct answers based on question type.
        
        Args:
            answers: List of answer dictionaries
            question_type: Type of question
        """
        if question_type == "multiple_choice":
            print("\n✅ Mark the correct answer:")
            for i, answer in enumerate(answers):
                print(f"{i+1}. {answer['text']}")
            
            while True:
                choice = input("Enter the number of the correct answer: ").strip()
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(answers):
                        answers[choice_num - 1]["is_correct"] = True
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(answers)}.")
                except ValueError:
                    print("❌ Please enter a valid number.")
        
        elif question_type == "select_all":
            print("\n✅ Mark all correct answers (enter numbers separated by commas):")
            for i, answer in enumerate(answers):
                print(f"{i+1}. {answer['text']}")
            
            while True:
                choices = input("Enter numbers of correct answers (e.g., 1,3,4): ").strip()
                
                if not choices:
                    print("❌ Please select at least one correct answer.")
                    continue
                
                try:
                    choice_nums = [int(x.strip()) for x in choices.split(',')]
                    
                    # Validate all choices
                    valid_choices = all(1 <= num <= len(answers) for num in choice_nums)
                    if not valid_choices:
                        print(f"❌ Please enter numbers between 1 and {len(answers)}.")
                        continue
                    
                    # Mark selected answers as correct
                    for num in choice_nums:
                        answers[num - 1]["is_correct"] = True
                    
                    break
                    
                except ValueError:
                    print("❌ Please enter valid numbers separated by commas.")
    
    def prompt_tag_selection(self, available_tags: List[str]) -> List[str]:
        """
        Prompt user for tag selection.
        
        Args:
            available_tags: List of available tag names
            
        Returns:
            List of selected tag names
        """
        if not available_tags:
            print("\n🏷️  No tags available. Creating new tag...")
            return [self.prompt_new_tag()]
        
        print("\n🏷️  Select tags for this question:")
        print("(Enter numbers separated by commas, or 'new' to create a new tag)")
        
        for i, tag in enumerate(available_tags):
            print(f"{i+1}. {tag}")
        
        while True:
            choice = input("Enter tag numbers (e.g., 1,3,5) or 'new': ").strip()
            
            if choice.lower() == "new":
                new_tag = self.prompt_new_tag()
                return [new_tag]
            
            if not choice:
                print("❌ Please select at least one tag.")
                continue
            
            try:
                choice_nums = [int(x.strip()) for x in choice.split(',')]
                
                # Validate all choices
                valid_choices = all(1 <= num <= len(available_tags) for num in choice_nums)
                if not valid_choices:
                    print(f"❌ Please enter numbers between 1 and {len(available_tags)}.")
                    continue
                
                selected_tags = [available_tags[num - 1] for num in choice_nums]
                return selected_tags
                
            except ValueError:
                print("❌ Please enter valid numbers separated by commas.")
    
    def prompt_new_tag(self) -> str:
        """
        Prompt user to create a new tag.
        
        Returns:
            New tag name
        """
        while True:
            tag_name = input("Enter new tag name (1-20 characters, alphanumeric and hyphens only): ").strip()
            
            if not tag_name:
                print("❌ Tag name cannot be empty.")
                continue
            
            if len(tag_name) > 20:
                print("❌ Tag name cannot exceed 20 characters.")
                continue
            
            if not re.match(r'^[a-zA-Z0-9_-]+$', tag_name):
                print("❌ Tag name can only contain alphanumeric characters, hyphens, and underscores.")
                continue
            
            return tag_name
    
    def prompt_quiz_settings(self) -> Dict[str, Any]:
        """
        Prompt user for quiz settings.
        
        Returns:
            Dictionary with quiz settings
        """
        settings = {}
        
        # Number of questions
        while True:
            try:
                num_questions = input("Number of questions (1-50): ").strip()
                num_questions = int(num_questions)
                if 1 <= num_questions <= 50:
                    settings['num_questions'] = num_questions
                    break
                else:
                    print("❌ Please enter a number between 1 and 50.")
            except ValueError:
                print("❌ Please enter a valid number.")
        
        # Time limit (optional)
        time_limit = input("Time limit in minutes (press Enter for no limit): ").strip()
        if time_limit:
            try:
                settings['time_limit'] = int(time_limit)
            except ValueError:
                print("❌ Invalid time limit, proceeding without time limit.")
                settings['time_limit'] = None
        else:
            settings['time_limit'] = None
        
        return settings
    
    def prompt_file_path(self, file_type: str = "file") -> str:
        """
        Prompt user for file path.
        
        Args:
            file_type: Type of file (for validation)
            
        Returns:
            File path
        """
        while True:
            file_path = input(f"Enter path to {file_type}: ").strip()
            
            if not file_path:
                print("❌ File path cannot be empty.")
                continue
            
            # Basic validation
            if not file_path.replace('\\', '/').replace(':', '').replace('.', ''):
                print("❌ Please enter a valid file path.")
                continue
            
            return file_path
    
    def prompt_yes_no(self, message: str) -> bool:
        """
        Prompt user for yes/no response.
        
        Args:
            message: Prompt message
            
        Returns:
            True for yes, False for no
        """
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no.")
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input text.
        
        Args:
            text: Raw input text
            
        Returns:
            Sanitized text
        """
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        # Limit length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
        
        return sanitized
