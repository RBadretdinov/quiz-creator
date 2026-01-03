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
    
    def get_menu_choice(self, max_choice: int) -> int:
        """
        Get user menu choice with validation.
        
        Args:
            max_choice: Maximum valid choice number
            
        Returns:
            Valid menu choice
        """
        while True:
            try:
                choice = input(f"\nEnter your choice (0-{max_choice}): ").strip()
                choice_num = int(choice)
                
                if 0 <= choice_num <= max_choice:
                    return choice_num
                else:
                    print(f"[ERROR] Please enter a number between 0 and {max_choice}")
                    
            except ValueError:
                print("[ERROR] Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                return 0
    
    def get_yes_no_input(self, prompt: str) -> Optional[bool]:
        """
        Get yes/no input from user with cancel support.
        
        Args:
            prompt: Prompt message to display
            
        Returns:
            True for yes, False for no, None if cancelled
        """
        while True:
            try:
                response = input(f"{prompt} (y/n, or 'cancel'): ").strip().lower()
                
                # Check for cancel
                if self._is_cancel_command(response):
                    return None
                
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("[ERROR] Please enter 'y' for yes, 'n' for no, or 'cancel'")
            except KeyboardInterrupt:
                print("\n[CANCELLED] Operation cancelled.")
                return None
            except EOFError:
                return None
    
    def _is_cancel_command(self, text: str) -> bool:
        """
        Check if user input is a cancel command.
        
        Args:
            text: User input text
            
        Returns:
            True if user wants to cancel
        """
        cancel_commands = ['cancel', 'c', 'q', 'quit', 'exit', 'back']
        return text.lower().strip() in cancel_commands
    
    def get_text_input(self, prompt: str, allow_cancel: bool = True) -> Optional[str]:
        """
        Get text input from user with optional cancel support.
        
        Args:
            prompt: Prompt message to display
            allow_cancel: Whether to allow cancel commands
            
        Returns:
            User input text, or None if cancelled
        """
        try:
            user_input = input(f"{prompt} ").strip()
            
            if allow_cancel and self._is_cancel_command(user_input):
                return None
            
            return user_input
        except KeyboardInterrupt:
            if allow_cancel:
                print("\n[CANCELLED] Operation cancelled.")
                return None
            print("\n\nGoodbye!")
            return ""
        except EOFError:
            return None if allow_cancel else ""
    
    def prompt_question_text(self) -> Optional[str]:
        """
        Prompt user for question text with validation.
        
        Returns:
            Validated question text, or None if cancelled
        """
        while True:
            question_text = input("\nEnter the question text (10-500 characters, or 'cancel' to cancel): ").strip()
            
            # Check for cancel
            if self._is_cancel_command(question_text):
                print("[CANCELLED] Question creation cancelled.")
                return None
            
            if not question_text:
                print("[ERROR] Question text cannot be empty. (Type 'cancel' to cancel)")
                continue
            
            if len(question_text) < 10:
                print("[ERROR] Question text must be at least 10 characters long. (Type 'cancel' to cancel)")
                continue
            
            if len(question_text) > 500:
                print("[ERROR] Question text cannot exceed 500 characters. (Type 'cancel' to cancel)")
                continue
            
            return question_text
    
    def prompt_question_type(self) -> Optional[str]:
        """
        Prompt user for question type.
        
        Returns:
            Selected question type, or None if cancelled
        """
        print("\n📋 Select question type:")
        print("1. Multiple Choice (one correct answer)")
        print("2. True/False")
        print("3. Select All That Apply (multiple correct answers)")
        print("(Type 'cancel' to cancel)")
        
        while True:
            choice = input("Enter choice (1-3 or 'cancel'): ").strip()
            
            # Check for cancel
            if self._is_cancel_command(choice):
                print("[CANCELLED] Question creation cancelled.")
                return None
            
            if choice == "1":
                return "multiple_choice"
            elif choice == "2":
                return "true_false"
            elif choice == "3":
                return "select_all"
            else:
                print("❌ Please enter 1, 2, 3, or 'cancel'.")
    
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
    
    def get_answers_for_type(self, question_type: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get answers for a specific question type.
        
        Args:
            question_type: Type of question ('multiple_choice', 'true_false', 'select_all')
            
        Returns:
            List of answer dictionaries, or None if cancelled
        """
        answers = []
        
        if question_type == "multiple_choice":
            print("\nEnter multiple choice answers (at least 2, maximum 6, or 'cancel' to cancel):")
            answer_count = 0
            
            while answer_count < 6:
                answer_text = input(f"Answer {answer_count + 1} (or press Enter to finish, 'cancel' to cancel): ").strip()
                
                # Check for cancel
                if self._is_cancel_command(answer_text):
                    print("[CANCELLED] Question creation cancelled.")
                    return None
                
                if not answer_text:
                    if answer_count >= 2:
                        break
                    else:
                        print("You need at least 2 answers for multiple choice. (Type 'cancel' to cancel)")
                        continue
                
                is_correct = self.get_yes_no_input(f"Is '{answer_text}' the correct answer?")
                if is_correct is None:  # User cancelled
                    print("[CANCELLED] Question creation cancelled.")
                    return None
                
                answers.append({"text": answer_text, "is_correct": is_correct})
                answer_count += 1
        
        elif question_type == "true_false":
            print("\nTrue/False question - answers will be automatically set.")
            answers = [
                {"text": "True", "is_correct": True},
                {"text": "False", "is_correct": False}
            ]
        
        elif question_type == "select_all":
            print("\nEnter select-all answers (at least 2, maximum 8, or 'cancel' to cancel):")
            answer_count = 0
            
            while answer_count < 8:
                answer_text = input(f"Answer {answer_count + 1} (or press Enter to finish, 'cancel' to cancel): ").strip()
                
                # Check for cancel
                if self._is_cancel_command(answer_text):
                    print("[CANCELLED] Question creation cancelled.")
                    return None
                
                if not answer_text:
                    if answer_count >= 2:
                        break
                    else:
                        print("You need at least 2 answers for select-all. (Type 'cancel' to cancel)")
                        continue
                
                is_correct = self.get_yes_no_input(f"Is '{answer_text}' a correct answer?")
                if is_correct is None:  # User cancelled
                    print("[CANCELLED] Question creation cancelled.")
                    return None
                
                answers.append({"text": answer_text, "is_correct": is_correct})
                answer_count += 1
        
        return answers
    
    def get_number_input(self, prompt: str, min_val: int = 1, max_val: int = 100, default: int = None) -> Optional[int]:
        """
        Get number input from user with validation.
        
        Args:
            prompt: Prompt message to display
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            default: Default value to return if user presses Enter without input
            
        Returns:
            Valid number input, or None if cancelled
        """
        while True:
            try:
                user_input = input(f"{prompt} ({min_val}-{max_val}): ").strip()
                
                # If empty input and default is provided, return default
                if not user_input and default is not None:
                    if min_val <= default <= max_val:
                        return default
                    else:
                        print(f"[ERROR] Default value {default} is not within range {min_val}-{max_val}")
                        continue
                
                # If empty and no default, treat as cancellation
                if not user_input:
                    return None
                
                # Check for cancel commands
                if self._is_cancel_command(user_input):
                    return None
                
                value = int(user_input)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"[ERROR] Please enter a number between {min_val} and {max_val}")
            except ValueError:
                print("[ERROR] Please enter a valid number")
            except KeyboardInterrupt:
                print("\n[CANCELLED] Operation cancelled.")
                return None
            except EOFError:
                return None
    
    def get_answer_input(self, question: Dict[str, Any]) -> Optional[str]:
        """
        Get answer input for a question.
        
        Args:
            question: Question dictionary
            
        Returns:
            User's answer(s) - for select_all, returns comma-separated indices;
            for other types, returns single answer text or comma-separated indices
        """
        question_type = question.get('question_type', 'multiple_choice')
        
        if question_type == 'select_all':
            # For select-all questions, allow multiple selections
            print("\n[Select All That Apply] Enter numbers separated by commas (e.g., 1,3,4)")
            while True:
                try:
                    choice = input(f"Enter your answer(s) (1-{len(question['answers'])}): ").strip()
                    
                    # Check for cancel
                    if self._is_cancel_command(choice):
                        return None
                    
                    # Parse comma-separated numbers
                    choices = [c.strip() for c in choice.split(',')]
                    choice_nums = [int(c) for c in choices if c]
                    
                    # Validate all choices
                    if not choice_nums:
                        print("[ERROR] Please enter at least one number")
                        continue
                    
                    invalid = [c for c in choice_nums if not (1 <= c <= len(question['answers']))]
                    if invalid:
                        print(f"[ERROR] Invalid numbers: {invalid}. Please enter numbers between 1 and {len(question['answers'])}")
                        continue
                    
                    # Return comma-separated indices (0-based) for the quiz engine
                    indices = [c - 1 for c in choice_nums]
                    return ','.join(map(str, indices))
                    
                except ValueError:
                    print("[ERROR] Please enter valid numbers separated by commas (e.g., 1,3,4)")
                except KeyboardInterrupt:
                    print("\n[CANCELLED] Quiz cancelled.")
                    return None
                except EOFError:
                    return None
        else:
            # For single-choice questions (multiple choice or true/false)
            while True:
                try:
                    choice = input(f"Enter your answer (1-{len(question['answers'])}): ").strip()
                    
                    # Check for cancel
                    if self._is_cancel_command(choice):
                        return None
                    
                    choice_num = int(choice)
                    
                    if 1 <= choice_num <= len(question['answers']):
                        # Return the index (0-based) for consistency
                        return str(choice_num - 1)
                    else:
                        print(f"[ERROR] Please enter a number between 1 and {len(question['answers'])}")
                    
                except ValueError:
                    print("[ERROR] Please enter a valid number")
                except KeyboardInterrupt:
                    print("\n[CANCELLED] Quiz cancelled.")
                    return None
                except EOFError:
                    return None
    
    def get_question_type(self) -> str:
        """
        Get question type from user.
        
        Returns:
            Selected question type
        """
        print("\nSelect question type:")
        print("1. Multiple Choice")
        print("2. True/False")
        print("3. Select All That Apply")
        
        while True:
            try:
                choice = input("Enter your choice (1-3): ").strip()
                choice_num = int(choice)
                
                if choice_num == 1:
                    return "multiple_choice"
                elif choice_num == 2:
                    return "true_false"
                elif choice_num == 3:
                    return "select_all"
                else:
                    print("[ERROR] Please enter 1, 2, or 3")
                    
            except ValueError:
                print("[ERROR] Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                return ""
            except EOFError:
                return ""
    
    def get_tag_selection(self) -> Optional[List[str]]:
        """
        Get tag selection from user.
        
        Returns:
            List of selected tag names, or None if cancelled
        """
        print("\nTag selection (press Enter when done, or 'cancel' to cancel):")
        tags = []
        
        while True:
            tag_name = input(f"Enter tag name (or press Enter to finish, 'cancel' to cancel): ").strip()
            
            # Check for cancel
            if self._is_cancel_command(tag_name):
                print("[CANCELLED] Question creation cancelled.")
                return None
            
            if not tag_name:
                break
            
            if tag_name not in tags:
                tags.append(tag_name)
            else:
                print("Tag already added.")
        
        return tags
    
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
