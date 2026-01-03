"""
User Feedback System for Errors and Validation

This module provides user-friendly error messages and feedback
for the quiz application.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorFeedback:
    """User-friendly error feedback system."""
    
    def __init__(self):
        """Initialize error feedback system."""
        self.feedback_messages = self._initialize_feedback_messages()
        self.user_preferences = {
            'show_detailed_errors': False,
            'show_error_codes': False,
            'suggest_solutions': True
        }
    
    def get_error_feedback(self, error_type: str, error_details: Dict[str, Any] = None) -> str:
        """
        Get user-friendly error feedback.
        
        Args:
            error_type: Type of error
            error_details: Additional error details
            
        Returns:
            User-friendly error message
        """
        try:
            # Get base message
            base_message = self.feedback_messages.get(error_type, "An unexpected error occurred.")
            
            # Add context if available
            if error_details and 'context' in error_details:
                context = error_details['context']
                if context == 'question_creation':
                    base_message += " Please check your question details and try again."
                elif context == 'quiz_taking':
                    base_message += " Please check your answer and try again."
                elif context == 'file_operation':
                    base_message += " Please check the file path and permissions."
                elif context == 'database_operation':
                    base_message += " Please try again in a moment."
            
            # Add solution suggestions if enabled
            if self.user_preferences['suggest_solutions']:
                solution = self._get_solution_suggestion(error_type)
                if solution:
                    base_message += f" {solution}"
            
            return base_message
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            return "An error occurred while processing your request."
    
    def get_validation_feedback(self, field_name: str, validation_error: str) -> str:
        """
        Get validation feedback for specific field.
        
        Args:
            field_name: Name of field with validation error
            validation_error: Validation error message
            
        Returns:
            User-friendly validation message
        """
        field_messages = {
            'question_text': "Please enter a question (1-1000 characters).",
            'answers': "Please provide at least 2 answer options.",
            'correct_answers': "Please select the correct answer(s).",
            'tag_name': "Please enter a tag name (1-50 characters).",
            'description': "Please enter a description (1-200 characters).",
            'file_path': "Please enter a valid file path.",
            'user_input': "Please enter a valid response."
        }
        
        base_message = field_messages.get(field_name, "Please check your input.")
        
        # Add specific guidance based on error
        if "required" in validation_error.lower():
            base_message += " This field is required."
        elif "length" in validation_error.lower():
            if "minimum" in validation_error.lower():
                base_message += " The text is too short."
            else:
                base_message += " The text is too long."
        elif "type" in validation_error.lower():
            base_message += " Please enter the correct type of data."
        
        return base_message
    
    def get_success_feedback(self, action: str, details: Dict[str, Any] = None) -> str:
        """
        Get success feedback for completed actions.
        
        Args:
            action: Action that was completed
            details: Additional details about the action
            
        Returns:
            Success message
        """
        success_messages = {
            'question_created': "Question created successfully!",
            'question_updated': "Question updated successfully!",
            'question_deleted': "Question deleted successfully!",
            'tag_created': "Tag created successfully!",
            'tag_updated': "Tag updated successfully!",
            'tag_deleted': "Tag deleted successfully!",
            'quiz_completed': "Quiz completed! Great job!",
            'data_saved': "Data saved successfully!",
            'data_loaded': "Data loaded successfully!",
            'file_imported': "File imported successfully!",
            'file_exported': "File exported successfully!",
            'settings_saved': "Settings saved successfully!"
        }
        
        base_message = success_messages.get(action, "Operation completed successfully!")
        
        # Add details if available
        if details:
            if 'count' in details:
                base_message += f" ({details['count']} items processed)"
            if 'file_path' in details:
                base_message += f" Saved to: {details['file_path']}"
        
        return base_message
    
    def get_help_feedback(self, topic: str) -> str:
        """
        Get help feedback for specific topics.
        
        Args:
            topic: Help topic
            
        Returns:
            Help message
        """
        help_messages = {
            'question_creation': "To create a question: 1) Enter the question text, 2) Choose question type, 3) Add answer options, 4) Mark correct answers.",
            'quiz_taking': "To take a quiz: 1) Select questions or tags, 2) Answer each question, 3) Submit your answers, 4) View your results.",
            'tag_management': "To manage tags: 1) Create tags to organize questions, 2) Use hierarchical tags for better organization, 3) Search and filter by tags.",
            'file_operations': "To import/export: 1) Choose file format (JSON/CSV), 2) Select questions/tags to export, 3) Choose destination, 4) Confirm operation.",
            'error_handling': "If you encounter errors: 1) Check your input, 2) Try again, 3) Contact support if problems persist.",
            'keyboard_shortcuts': "Use Ctrl+H for help, Ctrl+N for new question, Ctrl+T for quiz, F1 for context help."
        }
        
        return help_messages.get(topic, "Help is available. Use Ctrl+H for more information.")
    
    def get_progress_feedback(self, current: int, total: int, operation: str) -> str:
        """
        Get progress feedback for operations.
        
        Args:
            current: Current progress
            total: Total items
            operation: Operation being performed
            
        Returns:
            Progress message
        """
        percentage = (current / total * 100) if total > 0 else 0
        
        progress_messages = {
            'importing': f"Importing... {current}/{total} ({percentage:.1f}%)",
            'exporting': f"Exporting... {current}/{total} ({percentage:.1f}%)",
            'processing': f"Processing... {current}/{total} ({percentage:.1f}%)",
            'loading': f"Loading... {current}/{total} ({percentage:.1f}%)",
            'saving': f"Saving... {current}/{total} ({percentage:.1f}%)"
        }
        
        return progress_messages.get(operation, f"Progress: {current}/{total} ({percentage:.1f}%)")
    
    def set_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """Set user preferences for feedback."""
        self.user_preferences.update(preferences)
    
    def _initialize_feedback_messages(self) -> Dict[str, str]:
        """Initialize feedback messages."""
        return {
            'validation': "Please check your input and try again.",
            'file_operation': "There was a problem with the file operation. Please check the file path and try again.",
            'database_operation': "There was a problem with the database. Please try again.",
            'network_error': "There was a network problem. Please check your connection and try again.",
            'permission_error': "You don't have permission to perform this operation. Please check your access rights.",
            'not_found': "The requested item was not found. Please check your input and try again.",
            'already_exists': "This item already exists. Please use a different name or update the existing item.",
            'invalid_format': "The file format is not supported. Please use a supported format (JSON, CSV).",
            'corrupted_data': "The data appears to be corrupted. Please check the file and try again.",
            'system_error': "A system error occurred. Please try again or contact support if the problem persists.",
            'timeout': "The operation timed out. Please try again.",
            'memory_error': "Not enough memory available. Please try with fewer items or restart the application.",
            'disk_full': "Not enough disk space available. Please free up space and try again."
        }
    
    def _get_solution_suggestion(self, error_type: str) -> str:
        """Get solution suggestion for error type."""
        solutions = {
            'validation': "Make sure all required fields are filled and data is in the correct format.",
            'file_operation': "Check that the file path is correct and you have permission to access it.",
            'database_operation': "The database may be busy. Please wait a moment and try again.",
            'network_error': "Check your internet connection and try again.",
            'permission_error': "Contact your administrator to get the necessary permissions.",
            'not_found': "Double-check the name or ID of the item you're looking for.",
            'already_exists': "Try using a different name or update the existing item instead.",
            'invalid_format': "Convert your file to a supported format (JSON or CSV) and try again.",
            'corrupted_data': "Try using a backup file or recreate the data if possible.",
            'system_error': "Restart the application and try again. If the problem persists, contact support.",
            'timeout': "Try again with a smaller dataset or check your internet connection.",
            'memory_error': "Close other applications to free up memory, or try with fewer items.",
            'disk_full': "Delete unnecessary files to free up disk space and try again."
        }
        
        return solutions.get(error_type, "Please try again or contact support if the problem persists.")

class ValidationFeedback:
    """Validation feedback utilities."""
    
    @staticmethod
    def get_field_validation_message(field_name: str, error_type: str) -> str:
        """Get validation message for specific field."""
        field_messages = {
            'question_text': {
                'required': "Question text is required.",
                'too_short': "Question text must be at least 1 character.",
                'too_long': "Question text must be no more than 1000 characters.",
                'invalid_type': "Question text must be text."
            },
            'answers': {
                'required': "At least 2 answer options are required.",
                'too_few': "At least 2 answer options are required.",
                'empty_option': "Answer options cannot be empty.",
                'invalid_type': "Answer options must be a list."
            },
            'correct_answers': {
                'required': "Please select at least one correct answer.",
                'invalid_index': "Correct answer index is out of range.",
                'invalid_type': "Correct answers must be a list of numbers."
            },
            'tag_name': {
                'required': "Tag name is required.",
                'too_short': "Tag name must be at least 1 character.",
                'too_long': "Tag name must be no more than 50 characters.",
                'invalid_type': "Tag name must be text."
            }
        }
        
        field_specific = field_messages.get(field_name, {})
        return field_specific.get(error_type, "Please check your input.")

class ProgressIndicator:
    """Progress indication utilities."""
    
    @staticmethod
    def create_progress_bar(current: int, total: int, width: int = 20) -> str:
        """Create a text-based progress bar."""
        if total == 0:
            return "[" + " " * width + "] 0%"
        
        percentage = current / total
        filled = int(percentage * width)
        bar = "█" * filled + "░" * (width - filled)
        
        return f"[{bar}] {percentage:.1%}"
    
    @staticmethod
    def create_spinner(current: int, total: int) -> str:
        """Create a spinner for indeterminate progress."""
        spinner_chars = "|/-\\"
        return spinner_chars[current % len(spinner_chars)]

# Global feedback instances
error_feedback = ErrorFeedback()
validation_feedback = ValidationFeedback()
progress_indicator = ProgressIndicator()
