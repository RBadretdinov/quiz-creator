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
    
    def show_welcome(self) -> None:
        """Display welcome message."""
        print("\n" + "="*60)
        print("           WELCOME TO QUIZ APPLICATION")
        print("="*60)
        print("Create, manage, and take quizzes with ease!")
        print("="*60)
    
    def show_error(self, message: str) -> None:
        """
        Display error message.
        
        Args:
            message: Error message to display
        """
        print(f"\n[ERROR] {message}")
    
    def show_success(self, message: str) -> None:
        """
        Display success message.
        
        Args:
            message: Success message to display
        """
        print(f"\n[SUCCESS] {message}")
    
    def show_section_header(self, title: str) -> None:
        """
        Display section header.
        
        Args:
            title: Section title to display
        """
        print("\n" + "="*60)
        print(f"           {title.upper()}")
        print("="*60)
    
    def show_message(self, message: str) -> None:
        """
        Display general message.
        
        Args:
            message: Message to display
        """
        print(f"\n{message}")
    
    def show_tags_list(self, tags: List[Dict[str, Any]]) -> None:
        """
        Display list of tags.
        
        Args:
            tags: List of tag dictionaries
        """
        if not tags:
            print("\nNo tags found.")
            return
        
        print("\n" + "="*60)
        print("TAGS")
        print("="*60)
        
        for i, tag in enumerate(tags, 1):
            name = tag.get('name', 'N/A')
            description = tag.get('description', '')
            question_count = tag.get('question_count', 0)
            
            print(f"\n{i}. {name}")
            if description:
                print(f"   Description: {description}")
            print(f"   Questions: {question_count}")
        
        print("="*60)
    
    def show_question_summary(self, question: Dict[str, Any]) -> None:
        """
        Display question summary.
        
        Args:
            question: Question dictionary
        """
        print(f"\nQuestion Summary:")
        print(f"Text: {question.get('question_text', 'N/A')}")
        print(f"Type: {question.get('question_type', 'N/A')}")
        print(f"Tags: {', '.join(question.get('tags', []))}")
        print(f"Answers: {len(question.get('answers', []))}")
    
    def show_quiz_start(self, session: Dict[str, Any]) -> None:
        """
        Display quiz start message.
        
        Args:
            session: Quiz session dictionary
        """
        print(f"\nQuiz Started!")
        print(f"Total Questions: {len(session.get('questions', []))}")
        print("="*60)
    
    def show_question(self, question: Dict[str, Any], current: int, total: int) -> None:
        """
        Display a quiz question.
        
        Args:
            question: Question dictionary
            current: Current question number
            total: Total number of questions
        """
        print(f"\nQuestion {current}/{total}")
        print(f"Question: {question.get('question_text', 'N/A')}")
        print("Options:")
        
        for i, answer in enumerate(question.get('answers', []), 1):
            print(f"  {i}. {answer.get('text', 'N/A')}")
    
    def show_immediate_feedback(self, result: Dict[str, Any]) -> None:
        """
        Display immediate feedback for an answer.
        
        Args:
            result: Result dictionary
        """
        if result.get('is_correct', False):
            print("CORRECT!")
        else:
            print("INCORRECT!")
            if result.get('correct_answers'):
                print(f"Correct answer: {result['correct_answers']}")
    
    def show_final_results(self, score: Dict[str, Any]) -> None:
        """
        Display final quiz results.
        
        Args:
            score: Score dictionary
        """
        print("\n" + "="*60)
        print("QUIZ COMPLETE!")
        print("="*60)
        print(f"Score: {score.get('correct', 0)}/{score.get('total', 0)}")
        print(f"Percentage: {score.get('percentage', 0):.1f}%")
        print("="*60)
    
    def show_info(self, message: str) -> None:
        """
        Display info message.
        
        Args:
            message: Info message to display
        """
        print(f"\n[INFO] {message}")
    
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
    
    def show_performance_analytics(self, analytics: Dict[str, Any]) -> None:
        """Display performance analytics."""
        print("\n" + "="*60)
        print("📊 PERFORMANCE ANALYTICS")
        print("="*60)
        print()
        
        print(f"📈 Total Sessions: {analytics.get('total_sessions', 0)}")
        print(f"📈 Total Questions: {analytics.get('total_questions', 0)}")
        print(f"📈 Total Correct: {analytics.get('total_correct', 0)}")
        print(f"📈 Average Score: {analytics.get('average_score', 0):.1f}%")
        print(f"📈 Average Accuracy: {analytics.get('average_accuracy', 0):.1f}%")
        print(f"📈 Total Time Spent: {analytics.get('total_time_spent', 0)} seconds")
        print(f"📈 Average Session Duration: {analytics.get('average_session_duration', 0):.1f} seconds")
        print(f"📈 Questions per Minute: {analytics.get('questions_per_minute', 0):.1f}")
        print()
        
        # Show best performance
        best = analytics.get('best_performance', {})
        if best:
            print("🏆 Best Performance:")
            print(f"   Score: {best.get('score', 0):.1f}%")
            print(f"   Accuracy: {best.get('accuracy', 0):.1f}%")
            print(f"   Date: {best.get('date', 'Unknown')}")
            print()
        
        # Show performance distribution
        distribution = analytics.get('performance_distribution', {})
        if distribution:
            print("📊 Performance Distribution:")
            for level, count in distribution.items():
                print(f"   {level.title()}: {count}")
            print()
    
    def show_learning_analytics(self, analytics: Dict[str, Any]) -> None:
        """Display learning analytics."""
        print("\n" + "="*60)
        print("🎓 LEARNING ANALYTICS")
        print("="*60)
        print()
        
        print(f"📚 Total Questions Attempted: {analytics.get('total_questions_attempted', 0)}")
        print(f"📚 Unique Questions: {analytics.get('unique_questions', 0)}")
        print(f"📚 Overall Accuracy: {analytics.get('overall_accuracy', 0):.1f}%")
        print(f"📚 Learning Velocity: {analytics.get('learning_velocity', 0):.2f}")
        print(f"📚 Retention Rate: {analytics.get('retention_rate', 0):.1f}%")
        print()
        
        # Show difficult questions
        difficult = analytics.get('difficult_questions', [])
        if difficult:
            print("🔴 Difficult Questions:")
            for question in difficult[:5]:  # Show top 5
                print(f"   - {question.get('question_text', 'Unknown')[:50]}...")
            print()
        
        # Show mastered questions
        mastered = analytics.get('mastered_questions', [])
        if mastered:
            print("✅ Mastered Questions:")
            for question in mastered[:5]:  # Show top 5
                print(f"   - {question.get('question_text', 'Unknown')[:50]}...")
            print()
        
        # Show knowledge gaps
        gaps = analytics.get('knowledge_gaps', [])
        if gaps:
            print("⚠️ Knowledge Gaps:")
            for gap in gaps:
                print(f"   - {gap}")
            print()
    
    def show_question_analytics(self, analytics: Dict[str, Any]) -> None:
        """Display question analytics."""
        print("\n" + "="*60)
        print("❓ QUESTION ANALYTICS")
        print("="*60)
        print()
        
        print(f"📊 Total Attempts: {analytics.get('total_attempts', 0)}")
        print(f"📊 Unique Users: {analytics.get('unique_users', 0)}")
        print(f"📊 Success Rate: {analytics.get('success_rate', 0):.1f}%")
        print(f"📊 Average Response Time: {analytics.get('average_response_time', 0):.1f} seconds")
        print(f"📊 Difficulty Score: {analytics.get('difficulty_score', 0):.2f}")
        print(f"📊 Popularity Score: {analytics.get('popularity_score', 0)}")
        print(f"📊 Effectiveness Score: {analytics.get('effectiveness_score', 0):.2f}")
        print()
        
        # Show response time distribution
        distribution = analytics.get('response_time_distribution', {})
        if distribution:
            print("⏱️ Response Time Distribution:")
            for category, count in distribution.items():
                print(f"   {category.replace('_', ' ').title()}: {count}")
            print()
    
    def show_tag_analytics(self, analytics: Dict[str, Any]) -> None:
        """Display tag analytics."""
        print("\n" + "="*60)
        print("🏷️ TAG ANALYTICS")
        print("="*60)
        print()
        
        print(f"📊 Total Tags: {analytics.get('total_tags', 0)}")
        print()
        
        # Show most used tags
        most_used = analytics.get('most_used_tags', [])
        if most_used:
            print("🔥 Most Used Tags:")
            for tag in most_used[:10]:  # Show top 10
                print(f"   - {tag.get('name', 'Unknown')}: {tag.get('usage_count', 0)} uses")
            print()
        
        # Show least used tags
        least_used = analytics.get('least_used_tags', [])
        if least_used:
            print("❄️ Least Used Tags:")
            for tag in least_used[:10]:  # Show top 10
                print(f"   - {tag.get('name', 'Unknown')}: {tag.get('usage_count', 0)} uses")
            print()
    
    def show_system_analytics(self, analytics: Dict[str, Any]) -> None:
        """Display system analytics."""
        print("\n" + "="*60)
        print("🖥️ SYSTEM ANALYTICS")
        print("="*60)
        print()
        
        print(f"📊 Total Questions: {analytics.get('total_questions', 0)}")
        print(f"📊 Total Tags: {analytics.get('total_tags', 0)}")
        print(f"📊 Total Sessions: {analytics.get('total_sessions', 0)}")
        print(f"📊 Total Users: {analytics.get('total_users', 0)}")
        print(f"📊 Database Size: {analytics.get('database_size', 0)} MB")
        print(f"📊 System Health: {analytics.get('system_health', 0):.1f}%")
        print()
        
        # Show usage statistics
        usage = analytics.get('usage_statistics', {})
        if usage:
            print("📈 Usage Statistics:")
            for key, value in usage.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
            print()
        
        # Show performance metrics
        performance = analytics.get('performance_metrics', {})
        if performance:
            print("⚡ Performance Metrics:")
            for key, value in performance.items():
                print(f"   {key.replace('_', ' ').title()}: {value}")
            print()
    
    def show_questions_list(self, questions: List[Dict[str, Any]]) -> None:
        """
        Display list of questions.
        
        Args:
            questions: List of question dictionaries
        """
        if not questions:
            print("\nNo questions found.")
            return
        
        print("\n" + "="*60)
        print("QUESTIONS")
        print("="*60)
        
        for i, question in enumerate(questions, 1):
            text = question.get('question_text', 'N/A')
            q_type = question.get('question_type', 'N/A')
            tags = ', '.join(question.get('tags', []))
            
            print(f"\n{i}. {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"   Type: {q_type} | Tags: {tags or 'None'}")
        
        print("="*60)
    
    def show_question_statistics(self, stats: Dict[str, Any]) -> None:
        """
        Display question statistics.
        
        Args:
            stats: Statistics dictionary
        """
        print("\n" + "="*60)
        print("QUESTION STATISTICS")
        print("="*60)
        
        print(f"\nTotal Questions: {stats.get('total_questions', 0)}")
        print(f"By Type:")
        for q_type, count in stats.get('by_type', {}).items():
            print(f"  - {q_type}: {count}")
        
        print(f"\nBy Tag:")
        for tag, count in stats.get('by_tag', {}).items():
            print(f"  - {tag}: {count}")
        
        print("="*60)
    
    def show_database_info(self, db_info: Dict[str, Any]) -> None:
        """
        Display database information.
        
        Args:
            db_info: Database information dictionary
        """
        print("\n" + "="*60)
        print("DATABASE INFORMATION")
        print("="*60)
        
        print(f"\nDatabase Path: {db_info.get('database_path', 'N/A')}")
        print(f"Total Questions: {db_info.get('total_questions', 0)}")
        print(f"Total Tags: {db_info.get('total_tags', 0)}")
        print(f"Total Sessions: {db_info.get('total_sessions', 0)}")
        print(f"Database Size: {db_info.get('database_size', 0):.2f} MB")
        
        print("="*60)
    
    def show_backups_list(self, backups: List[Dict[str, Any]]) -> None:
        """
        Display list of backups.
        
        Args:
            backups: List of backup dictionaries
        """
        if not backups:
            print("\nNo backups found.")
            return
        
        print("\n" + "="*60)
        print("BACKUPS")
        print("="*60)
        
        for i, backup in enumerate(backups, 1):
            name = backup.get('name', 'N/A')
            date = backup.get('date', 'N/A')
            size = backup.get('size', 0)
            
            print(f"\n{i}. {name}")
            print(f"   Date: {date}")
            print(f"   Size: {size:.2f} MB")
        
        print("="*60)
    
    def show_maintenance_results(self, results: Dict[str, Any]) -> None:
        """
        Display database maintenance results.
        
        Args:
            results: Maintenance results dictionary
        """
        print("\n" + "="*60)
        print("MAINTENANCE RESULTS")
        print("="*60)
        
        if results.get('success'):
            print("\n[SUCCESS] Maintenance completed successfully!")
            print(f"Actions performed: {results.get('actions', [])}")
        else:
            print("\n[ERROR] Maintenance failed:")
            print(f"Error: {results.get('error', 'Unknown error')}")
        
        print("="*60)
    
    def show_health_score(self, score: Dict[str, Any]) -> None:
        """
        Display database health score.
        
        Args:
            score: Health score dictionary
        """
        print("\n" + "="*60)
        print("DATABASE HEALTH")
        print("="*60)
        
        health_value = score.get('score', 0)
        health_status = score.get('status', 'Unknown')
        
        print(f"\nHealth Score: {health_value:.1f}%")
        print(f"Status: {health_status}")
        
        issues = score.get('issues', [])
        if issues:
            print("\nIssues found:")
            for issue in issues:
                print(f"  - {issue}")
        
        print("="*60)
