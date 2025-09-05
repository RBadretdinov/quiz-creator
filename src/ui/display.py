"""
Display Module

This module handles the display of questions, results, and feedback in the console.
"""

from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DisplayManager:
    """Handles display of quiz content and results."""
    
    def __init__(self):
        """Initialize the display manager."""
        logger.info("Display manager initialized")
    
    def display_question(self, question: Dict[str, Any], question_num: int, total_questions: int) -> None:
        """
        Display a question with its answer options.
        
        Args:
            question: Question dictionary
            question_num: Current question number
            total_questions: Total number of questions
        """
        print("\n" + "="*60)
        print(f"Question {question_num} of {total_questions}")
        print("="*60)
        print()
        print(f"📝 {question['question_text']}")
        print()
        
        # Display answer options
        for i, answer in enumerate(question.get('answers', [])):
            print(f"{i+1}. {answer['text']}")
        
        print()
        print("-"*60)
    
    def display_quiz_progress(self, current: int, total: int) -> None:
        """
        Display quiz progress.
        
        Args:
            current: Current question number
            total: Total number of questions
        """
        progress = (current / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"\nProgress: [{bar}] {progress:.1f}% ({current}/{total})")
    
    def display_feedback(self, is_correct: bool, correct_answers: List[str], 
                        question: Dict[str, Any]) -> None:
        """
        Display immediate feedback for an answer.
        
        Args:
            is_correct: Whether the answer was correct
            correct_answers: List of correct answer IDs
            question: Question dictionary
        """
        print("\n" + "="*60)
        
        if is_correct:
            print("✅ CORRECT! Well done!")
        else:
            print("❌ INCORRECT")
            print("\nThe correct answer(s):")
            
            # Display correct answers
            for answer in question.get('answers', []):
                if answer['id'] in correct_answers:
                    print(f"  ✓ {answer['text']}")
        
        print("="*60)
    
    def display_results(self, session: Dict[str, Any]) -> None:
        """
        Display final quiz results.
        
        Args:
            session: Quiz session dictionary
        """
        print("\n" + "="*60)
        print("           QUIZ RESULTS")
        print("="*60)
        
        # Calculate statistics
        total_questions = len(session.get('questions', []))
        correct_answers = sum(1 for answer in session.get('answers', []) if answer.get('is_correct'))
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Display score
        print(f"\n📊 Final Score: {score_percentage:.1f}%")
        print(f"📝 Correct Answers: {correct_answers}/{total_questions}")
        
        # Display time taken
        if session.get('start_time') and session.get('end_time'):
            duration = session['end_time'] - session['start_time']
            minutes = int(duration.total_seconds() // 60)
            seconds = int(duration.total_seconds() % 60)
            print(f"⏱️  Time Taken: {minutes}m {seconds}s")
        
        # Display performance message
        if score_percentage >= 90:
            print("\n🎉 Excellent work! Outstanding performance!")
        elif score_percentage >= 80:
            print("\n👏 Great job! Well done!")
        elif score_percentage >= 70:
            print("\n👍 Good work! Keep it up!")
        elif score_percentage >= 60:
            print("\n📚 Not bad! Review the material and try again.")
        else:
            print("\n📖 Keep studying! Practice makes perfect.")
        
        print("="*60)
    
    def display_question_review(self, session: Dict[str, Any]) -> None:
        """
        Display detailed question-by-question review.
        
        Args:
            session: Quiz session dictionary
        """
        print("\n" + "="*60)
        print("           QUESTION REVIEW")
        print("="*60)
        
        questions = session.get('questions', [])
        answers = session.get('answers', [])
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            print(f"\nQuestion {i+1}:")
            print(f"📝 {question['question_text']}")
            
            # Show user's answer
            user_answer = answer.get('selected_answers', '')
            print(f"Your answer: {user_answer}")
            
            # Show correct answer
            correct_answers = [a['text'] for a in question.get('answers', []) if a.get('is_correct')]
            print(f"Correct answer: {', '.join(correct_answers)}")
            
            # Show result
            if answer.get('is_correct'):
                print("✅ Correct")
            else:
                print("❌ Incorrect")
            
            print("-" * 40)
    
    def display_question_list(self, questions: List[Dict[str, Any]], 
                            page: int = 1, per_page: int = 10) -> None:
        """
        Display a paginated list of questions.
        
        Args:
            questions: List of question dictionaries
            page: Current page number
            per_page: Number of questions per page
        """
        total_questions = len(questions)
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_questions)
        
        print(f"\n📚 Question Bank (Page {page})")
        print(f"Showing {start_idx + 1}-{end_idx} of {total_questions} questions")
        print("-" * 60)
        
        for i in range(start_idx, end_idx):
            question = questions[i]
            print(f"\n{i+1}. {question['question_text'][:80]}{'...' if len(question['question_text']) > 80 else ''}")
            print(f"   Type: {question.get('question_type', 'unknown')}")
            print(f"   Tags: {', '.join(question.get('tags', []))}")
            print(f"   ID: {question.get('id', 'unknown')[:8]}...")
        
        # Display pagination info
        total_pages = (total_questions + per_page - 1) // per_page
        if total_pages > 1:
            print(f"\nPage {page} of {total_pages}")
            if page > 1:
                print("(p) Previous page")
            if page < total_pages:
                print("(n) Next page")
    
    def display_tag_list(self, tags: List[Dict[str, Any]]) -> None:
        """
        Display a list of tags with statistics.
        
        Args:
            tags: List of tag dictionaries
        """
        print("\n🏷️  Available Tags:")
        print("-" * 60)
        
        for tag in tags:
            name = tag.get('name', 'Unknown')
            count = tag.get('question_count', 0)
            description = tag.get('description', '')
            
            print(f"• {name} ({count} questions)")
            if description:
                print(f"  {description}")
        
        print(f"\nTotal: {len(tags)} tags")
    
    def display_tag_statistics(self, stats: Dict[str, Any]) -> None:
        """
        Display tag usage statistics.
        
        Args:
            stats: Tag statistics dictionary
        """
        print("\n📊 Tag Statistics:")
        print("-" * 60)
        
        print(f"Total Tags: {stats.get('total_tags', 0)}")
        print(f"Average Usage: {stats.get('average_usage', 0):.1f} questions per tag")
        
        # Most used tags
        most_used = stats.get('most_used_tags', [])
        if most_used:
            print(f"\nMost Used Tags:")
            for tag in most_used[:5]:
                print(f"  • {tag.get('name', 'Unknown')}: {tag.get('question_count', 0)} questions")
        
        # Unused tags
        unused = stats.get('unused_tags', [])
        if unused:
            print(f"\nUnused Tags ({len(unused)}):")
            for tag in unused[:10]:  # Show first 10
                print(f"  • {tag.get('name', 'Unknown')}")
            if len(unused) > 10:
                print(f"  ... and {len(unused) - 10} more")
    
    def display_help_text(self, topic: str) -> None:
        """
        Display help text for a specific topic.
        
        Args:
            topic: Help topic to display
        """
        help_texts = {
            "getting_started": """
🎯 Getting Started with Quiz Application

1. Create Questions: Use the "Create Question" menu to add new questions
2. Organize with Tags: Assign tags to categorize your questions
3. Take Quizzes: Select questions by tags or take random quizzes
4. Review Results: See detailed feedback and performance statistics

💡 Tip: Start by creating a few questions and organizing them with tags!
            """,
            "question_types": """
📋 Question Types

1. Multiple Choice: Choose one correct answer from several options
2. True/False: Simple yes/no questions
3. Select All That Apply: Choose all correct answers from the options

💡 Tip: Use clear, concise language for better quiz experience!
            """,
            "tag_system": """
🏷️  Tag System

• Tags help organize questions into categories
• You can filter quizzes by specific tags
• Create descriptive tag names (e.g., "Math", "Science", "History")
• Each question can have multiple tags

💡 Tip: Use consistent naming conventions for your tags!
            """,
            "ocr_import": """
📷 OCR Import

• Take screenshots of questions from books, websites, or documents
• The app will extract text using OCR technology
• Review and edit the extracted questions before saving
• Works best with clear, high-contrast images

💡 Tip: Ensure good lighting and clear text for better OCR accuracy!
            """,
            "keyboard_shortcuts": """
⌨️  Keyboard Shortcuts

• Ctrl+C: Exit the application
• Enter: Confirm selection
• Numbers: Select menu options
• 'q' or 'quit': Return to previous menu

💡 Tip: Use number keys for quick menu navigation!
            """,
            "troubleshooting": """
🔧 Troubleshooting

Common Issues:
• OCR not working: Check if Tesseract is installed
• Questions not saving: Verify data directory permissions
• Menu not responding: Try restarting the application

💡 Tip: Check the logs in the 'logs' directory for detailed error information!
            """
        }
        
        text = help_texts.get(topic, "Help topic not found.")
        print(f"\n{text}")
    
    def display_welcome_message(self) -> None:
        """Display welcome message and application info."""
        print("\n" + "="*60)
        print("           WELCOME TO QUIZ APPLICATION")
        print("="*60)
        print()
        print("🎯 Create, manage, and take quizzes with ease!")
        print("📚 Support for multiple question types and OCR import")
        print("🏷️  Organize questions with custom tags")
        print("📊 Track your progress with detailed analytics")
        print()
        print("Version 1.0.0 - Console Edition")
        print("="*60)
