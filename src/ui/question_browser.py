"""
Question Browser

This module provides a console-based interface for browsing, searching,
and managing questions with pagination and advanced filtering.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class QuestionBrowser:
    """Console interface for browsing and managing questions."""
    
    def __init__(self, question_manager, tag_manager):
        """Initialize the question browser."""
        self.question_manager = question_manager
        self.tag_manager = tag_manager
        self.page_size = 20
        self.current_page = 1
        self.current_filter = None
        self.current_sort = 'created_at'
        self.sort_ascending = False
    
    def display_question_browser_menu(self) -> None:
        """Display the question browser menu."""
        print("\n" + "="*60)
        print("📚 QUESTION BROWSER")
        print("="*60)
        print("1. Browse All Questions")
        print("2. Search Questions")
        print("3. Filter by Tags")
        print("4. Sort Options")
        print("5. Question Statistics")
        print("6. Bulk Operations")
        print("0. Back to Main Menu")
        print("-"*60)
    
    def browse_questions(self, questions: List[Dict] = None, page: int = 1) -> None:
        """
        Display questions with pagination.
        
        Args:
            questions: List of questions to display (if None, uses all questions)
            page: Page number to display
        """
        if questions is None:
            questions = self.question_manager.get_all_questions()
        
        if not questions:
            print("\n❌ No questions found.")
            return
        
        # Apply current filter if set
        if self.current_filter:
            questions = self._apply_filter(questions, self.current_filter)
        
        # Apply current sort
        questions = self._apply_sort(questions, self.current_sort, self.sort_ascending)
        
        # Calculate pagination
        total_questions = len(questions)
        total_pages = (total_questions + self.page_size - 1) // self.page_size
        
        if page < 1 or page > total_pages:
            page = 1
        
        start_idx = (page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_questions)
        page_questions = questions[start_idx:end_idx]
        
        # Display header
        print(f"\n📚 QUESTION BROWSER - Page {page} of {total_pages}")
        print(f"Showing {start_idx + 1}-{end_idx} of {total_questions} questions")
        if self.current_filter:
            print(f"Filter: {self.current_filter}")
        print(f"Sort: {self.current_sort} ({'ascending' if self.sort_ascending else 'descending'})")
        print("="*80)
        
        # Display questions
        for i, question in enumerate(page_questions, start_idx + 1):
            self._display_question_summary(question, i)
        
        # Display pagination controls
        self._display_pagination_controls(page, total_pages)
        
        # Display action menu
        self._display_browser_actions()
    
    def _display_question_summary(self, question: Dict[str, Any], index: int) -> None:
        """Display a summary of a question."""
        question_id = question.get('id', 'Unknown')
        question_text = question.get('question_text', 'No text')
        question_type = question.get('question_type', 'unknown')
        tags = question.get('tags', [])
        usage_count = question.get('usage_count', 0)
        created_at = question.get('created_at', 'Unknown')
        
        # Truncate long question text
        if len(question_text) > 60:
            question_text = question_text[:57] + "..."
        
        print(f"\n{index:>3}. [{question_type.upper()}] {question_text}")
        print(f"     ID: {question_id[:8]}... | Tags: {', '.join(tags[:3])}{'...' if len(tags) > 3 else ''}")
        print(f"     Used: {usage_count} times | Created: {created_at[:10]}")
    
    def _display_pagination_controls(self, current_page: int, total_pages: int) -> None:
        """Display pagination controls."""
        print(f"\n{'='*80}")
        print("Navigation: [N]ext | [P]revious | [G]o to page | [F]irst | [L]ast | [Q]uit")
        
        if total_pages > 1:
            # Show page numbers
            start_page = max(1, current_page - 2)
            end_page = min(total_pages, current_page + 2)
            
            page_numbers = []
            if start_page > 1:
                page_numbers.append("1")
                if start_page > 2:
                    page_numbers.append("...")
            
            for page in range(start_page, end_page + 1):
                if page == current_page:
                    page_numbers.append(f"[{page}]")
                else:
                    page_numbers.append(str(page))
            
            if end_page < total_pages:
                if end_page < total_pages - 1:
                    page_numbers.append("...")
                page_numbers.append(str(total_pages))
            
            print(f"Pages: {' '.join(page_numbers)}")
    
    def _display_browser_actions(self) -> None:
        """Display available actions for questions."""
        print("\nActions: [V]iew | [E]dit | [D]elete | [C]opy | [S]earch | [F]ilter | [Q]uit")
    
    def _apply_filter(self, questions: List[Dict], filter_criteria: Dict[str, Any]) -> List[Dict]:
        """Apply filter criteria to questions."""
        filtered = questions.copy()
        
        # Filter by question type
        if 'question_type' in filter_criteria:
            filtered = [q for q in filtered if q.get('question_type') == filter_criteria['question_type']]
        
        # Filter by tags
        if 'tags' in filter_criteria:
            required_tags = filter_criteria['tags']
            filtered = [q for q in filtered if any(tag in q.get('tags', []) for tag in required_tags)]
        
        # Filter by text search
        if 'text_search' in filter_criteria:
            search_term = filter_criteria['text_search'].lower()
            filtered = [q for q in filtered if search_term in q.get('question_text', '').lower()]
        
        # Filter by usage count
        if 'min_usage' in filter_criteria:
            filtered = [q for q in filtered if q.get('usage_count', 0) >= filter_criteria['min_usage']]
        
        if 'max_usage' in filter_criteria:
            filtered = [q for q in filtered if q.get('usage_count', 0) <= filter_criteria['max_usage']]
        
        return filtered
    
    def _apply_sort(self, questions: List[Dict], sort_field: str, ascending: bool = False) -> List[Dict]:
        """Apply sorting to questions."""
        def sort_key(question):
            value = question.get(sort_field, '')
            if sort_field == 'created_at':
                return value
            elif sort_field == 'usage_count':
                return int(value) if value else 0
            else:
                return str(value).lower()
        
        return sorted(questions, key=sort_key, reverse=not ascending)
    
    def search_questions_interactive(self) -> List[Dict]:
        """Interactive question search."""
        print("\n" + "="*60)
        print("🔍 SEARCH QUESTIONS")
        print("="*60)
        
        search_term = input("Enter search term (question text): ").strip()
        if not search_term:
            return []
        
        questions = self.question_manager.get_all_questions()
        results = []
        
        for question in questions:
            if search_term.lower() in question.get('question_text', '').lower():
                results.append(question)
        
        print(f"\nFound {len(results)} questions matching '{search_term}'")
        
        if results:
            self.browse_questions(results, 1)
        
        return results
    
    def filter_by_tags_interactive(self) -> List[Dict]:
        """Interactive tag filtering."""
        print("\n" + "="*60)
        print("🏷️  FILTER BY TAGS")
        print("="*60)
        
        # Show available tags
        all_tags = self.tag_manager.get_all_tags()
        if not all_tags:
            print("No tags available.")
            return []
        
        print("Available tags:")
        for i, tag in enumerate(all_tags, 1):
            print(f"{i}. {tag.name} ({tag.question_count} questions)")
        
        try:
            choice = input("\nEnter tag numbers (comma-separated) or tag names: ").strip()
            if not choice:
                return []
            
            # Parse selection
            selected_tags = []
            if choice.replace(',', '').replace(' ', '').isdigit():
                # Numbers provided
                numbers = [int(x.strip()) for x in choice.split(',')]
                for num in numbers:
                    if 1 <= num <= len(all_tags):
                        selected_tags.append(all_tags[num - 1].name)
            else:
                # Tag names provided
                tag_names = [x.strip() for x in choice.split(',')]
                for tag_name in tag_names:
                    if any(tag.name == tag_name for tag in all_tags):
                        selected_tags.append(tag_name)
            
            if not selected_tags:
                print("No valid tags selected.")
                return []
            
            # Filter questions
            questions = self.question_manager.get_all_questions()
            filtered = []
            
            for question in questions:
                question_tags = question.get('tags', [])
                if any(tag in question_tags for tag in selected_tags):
                    filtered.append(question)
            
            print(f"\nFound {len(filtered)} questions with tags: {', '.join(selected_tags)}")
            
            if filtered:
                self.browse_questions(filtered, 1)
            
            return filtered
            
        except ValueError:
            print("Invalid input.")
            return []
    
    def display_sort_options(self) -> None:
        """Display and handle sort options."""
        print("\n" + "="*60)
        print("📊 SORT OPTIONS")
        print("="*60)
        
        sort_options = {
            '1': ('created_at', 'Creation Date'),
            '2': ('question_type', 'Question Type'),
            '3': ('usage_count', 'Usage Count'),
            '4': ('question_text', 'Question Text')
        }
        
        print("Sort by:")
        for key, (field, description) in sort_options.items():
            current = " (current)" if field == self.current_sort else ""
            print(f"{key}. {description}{current}")
        
        print(f"\nOrder: {'Ascending' if self.sort_ascending else 'Descending'}")
        print("Options: [1-4] Sort field | [A]scending | [D]escending | [Q]uit")
        
        choice = input("Select option: ").strip().upper()
        
        if choice in sort_options:
            self.current_sort = sort_options[choice][0]
            print(f"Sort field set to: {sort_options[choice][1]}")
        elif choice == 'A':
            self.sort_ascending = True
            print("Sort order set to: Ascending")
        elif choice == 'D':
            self.sort_ascending = False
            print("Sort order set to: Descending")
        elif choice == 'Q':
            return
        else:
            print("Invalid option.")
    
    def display_question_statistics(self) -> None:
        """Display comprehensive question statistics."""
        questions = self.question_manager.get_all_questions()
        
        if not questions:
            print("\n❌ No questions found.")
            return
        
        print("\n" + "="*60)
        print("📊 QUESTION STATISTICS")
        print("="*60)
        
        # Basic statistics
        total_questions = len(questions)
        print(f"Total Questions: {total_questions}")
        
        # Question type distribution
        type_counts = {}
        for question in questions:
            question_type = question.get('question_type', 'unknown')
            type_counts[question_type] = type_counts.get(question_type, 0) + 1
        
        print(f"\nQuestion Type Distribution:")
        for question_type, count in sorted(type_counts.items()):
            percentage = (count / total_questions) * 100
            print(f"  {question_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        # Tag statistics
        tag_counts = {}
        for question in questions:
            for tag in question.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        print(f"\nMost Used Tags:")
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_tags[:10]:
            print(f"  {tag}: {count} questions")
        
        # Usage statistics
        usage_counts = [q.get('usage_count', 0) for q in questions]
        total_usage = sum(usage_counts)
        avg_usage = total_usage / total_questions if total_questions > 0 else 0
        
        print(f"\nUsage Statistics:")
        print(f"  Total Usage: {total_usage}")
        print(f"  Average Usage: {avg_usage:.1f}")
        print(f"  Most Used: {max(usage_counts)}")
        print(f"  Least Used: {min(usage_counts)}")
        
        # Recent activity
        recent_questions = sorted(questions, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        print(f"\nRecent Questions:")
        for i, question in enumerate(recent_questions, 1):
            text = question.get('question_text', 'No text')[:50]
            if len(question.get('question_text', '')) > 50:
                text += "..."
            print(f"  {i}. {text}")
    
    def get_question_by_selection(self, questions: List[Dict], selection: str) -> Optional[Dict]:
        """Get a question by user selection."""
        try:
            if selection.isdigit():
                index = int(selection) - 1
                if 0 <= index < len(questions):
                    return questions[index]
            return None
        except ValueError:
            return None
