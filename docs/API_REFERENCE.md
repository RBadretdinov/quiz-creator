# Quiz Application - API Reference

## Table of Contents
1. [Core Models](#core-models)
2. [Data Managers](#data-managers)
3. [Quiz Engine](#quiz-engine)
4. [Analytics System](#analytics-system)
5. [OCR Processing](#ocr-processing)
6. [Performance Optimization](#performance-optimization)
7. [Error Handling](#error-handling)
8. [UI Components](#ui-components)

## Core Models

### Question Model

```python
class Question:
    def __init__(self, question_text: str, question_type: str, answers: List[Dict], 
                 tags: List[str] = None, created_at: datetime = None, 
                 updated_at: datetime = None, question_id: str = None)
```

**Parameters:**
- `question_text` (str): The question text
- `question_type` (str): Type of question ('multiple_choice', 'true_false', 'select_all', 'fill_in_blank')
- `answers` (List[Dict]): List of answer dictionaries
- `tags` (List[str], optional): List of tag names
- `created_at` (datetime, optional): Creation timestamp
- `updated_at` (datetime, optional): Last update timestamp
- `question_id` (str, optional): Unique identifier

**Answer Dictionary Structure:**
```python
{
    "text": "Answer text",
    "is_correct": True/False,
    "explanation": "Optional explanation"
}
```

**Methods:**
- `validate()`: Validate question data
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary
- `get_correct_answers()`: Get correct answers
- `get_incorrect_answers()`: Get incorrect answers

**Example:**
```python
question = Question(
    question_text="What is the capital of France?",
    question_type="multiple_choice",
    answers=[
        {"text": "Paris", "is_correct": True},
        {"text": "London", "is_correct": False},
        {"text": "Berlin", "is_correct": False},
        {"text": "Madrid", "is_correct": False}
    ],
    tags=["geography", "europe", "capitals"]
)
```

### Tag Model

```python
class Tag:
    def __init__(self, name: str, description: str = "", parent_id: str = None,
                 usage_count: int = 0, last_used: datetime = None,
                 children: List[str] = None, aliases: List[str] = None,
                 tag_id: str = None)
```

**Parameters:**
- `name` (str): Tag name
- `description` (str, optional): Tag description
- `parent_id` (str, optional): Parent tag ID for hierarchy
- `usage_count` (int, optional): Usage count
- `last_used` (datetime, optional): Last usage timestamp
- `children` (List[str], optional): Child tag IDs
- `aliases` (List[str], optional): Alternative names
- `tag_id` (str, optional): Unique identifier

**Methods:**
- `validate()`: Validate tag data
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary
- `add_child(child_id)`: Add child tag
- `remove_child(child_id)`: Remove child tag
- `add_alias(alias)`: Add alias
- `remove_alias(alias)`: Remove alias
- `increment_usage()`: Increment usage count
- `get_full_path()`: Get hierarchical path
- `get_depth()`: Get hierarchy depth

**Example:**
```python
tag = Tag(
    name="geography",
    description="Questions about geography",
    parent_id=None,
    aliases=["geo", "world"]
)
```

### QuizSession Model

```python
class QuizSession:
    def __init__(self, questions: List[Question], user_id: str = None,
                 start_time: datetime = None, end_time: datetime = None,
                 score: float = None, session_id: str = None)
```

**Parameters:**
- `questions` (List[Question]): List of questions in session
- `user_id` (str, optional): User identifier
- `start_time` (datetime, optional): Session start time
- `end_time` (datetime, optional): Session end time
- `score` (float, optional): Session score
- `session_id` (str, optional): Unique identifier

**Methods:**
- `validate()`: Validate session data
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary
- `calculate_score()`: Calculate session score
- `get_duration()`: Get session duration
- `is_complete()`: Check if session is complete

## Data Managers

### QuestionManager

```python
class QuestionManager:
    def __init__(self, db_manager: DatabaseManager = None)
```

**Methods:**
- `add_question(question: Question) -> str`: Add question and return ID
- `get_question(question_id: str) -> Question`: Get question by ID
- `get_all_questions() -> List[Question]`: Get all questions
- `update_question(question_id: str, question: Question) -> bool`: Update question
- `delete_question(question_id: str) -> bool`: Delete question
- `search_questions(query: str) -> List[Question]`: Search questions
- `get_questions_by_tag(tag_name: str) -> List[Question]`: Get questions by tag
- `get_questions_by_type(question_type: str) -> List[Question]`: Get questions by type
- `get_question_statistics() -> Dict`: Get question statistics

**Example:**
```python
question_manager = QuestionManager(db_manager)
question_id = question_manager.add_question(question)
question = question_manager.get_question(question_id)
```

### TagManager

```python
class TagManager:
    def __init__(self, db_manager: DatabaseManager = None)
```

**Methods:**
- `create_tag(name: str, description: str = "", parent_id: str = None) -> str`: Create tag
- `get_tag(tag_id: str) -> Tag`: Get tag by ID
- `get_tag_by_name(name: str) -> Tag`: Get tag by name
- `get_all_tags() -> List[Tag]`: Get all tags
- `update_tag(tag_id: str, tag: Tag) -> bool`: Update tag
- `delete_tag(tag_id: str) -> bool`: Delete tag
- `search_tags(query: str) -> List[Tag]`: Search tags
- `get_root_tags() -> List[Tag]`: Get root tags
- `get_children(tag_id: str) -> List[Tag]`: Get child tags
- `get_descendants(tag_id: str) -> List[Tag]`: Get all descendants
- `get_ancestors(tag_id: str) -> List[Tag]`: Get all ancestors
- `merge_tags(source_id: str, target_id: str) -> bool`: Merge tags
- `get_tag_statistics() -> Dict`: Get tag statistics

**Example:**
```python
tag_manager = TagManager(db_manager)
tag_id = tag_manager.create_tag("geography", "Geography questions")
tag = tag_manager.get_tag(tag_id)
```

## Quiz Engine

### QuizEngine

```python
class QuizEngine:
    def __init__(self, question_manager: QuestionManager, tag_manager: TagManager)
```

**Methods:**
- `create_quiz(num_questions: int, question_types: List[str] = None, 
               tags: List[str] = None, randomize: bool = True) -> QuizSession`: Create quiz
- `start_quiz(session: QuizSession) -> bool`: Start quiz session
- `submit_answer(session_id: str, question_id: str, answer: Any) -> Dict`: Submit answer
- `pause_quiz(session_id: str) -> bool`: Pause quiz session
- `resume_quiz(session_id: str) -> bool`: Resume quiz session
- `end_quiz(session_id: str) -> Dict`: End quiz session
- `get_quiz_progress(session_id: str) -> Dict`: Get quiz progress
- `calculate_score(session_id: str) -> Dict`: Calculate session score
- `export_quiz_session(session_id: str, format: str = "json") -> str`: Export session

**Example:**
```python
quiz_engine = QuizEngine(question_manager, tag_manager)
session = quiz_engine.create_quiz(10, ["multiple_choice"], ["geography"])
quiz_engine.start_quiz(session)
result = quiz_engine.submit_answer(session.session_id, question_id, "A")
```

## Analytics System

### AnalyticsEngine

```python
class AnalyticsEngine:
    def __init__(self, db_manager: DatabaseManager)
```

**Methods:**
- `get_performance_analytics(user_id: str = None) -> Dict`: Get performance analytics
- `get_learning_analytics(user_id: str = None) -> Dict`: Get learning analytics
- `get_question_analytics(question_id: str = None) -> Dict`: Get question analytics
- `get_tag_analytics(tag_id: str = None) -> Dict`: Get tag analytics
- `get_system_analytics() -> Dict`: Get system analytics
- `export_analytics(format: str = "json") -> str`: Export analytics data
- `get_analytics_summary() -> Dict`: Get analytics summary

**Example:**
```python
analytics_engine = AnalyticsEngine(db_manager)
performance = analytics_engine.get_performance_analytics()
learning = analytics_engine.get_learning_analytics()
```

### AnalyticsDashboard

```python
class AnalyticsDashboard:
    def __init__(self, analytics_engine: AnalyticsEngine, 
                 display_manager: DisplayManager, prompts: InputPrompts)
```

**Methods:**
- `show_main_dashboard() -> None`: Show main analytics dashboard
- `show_performance_analytics() -> None`: Show performance analytics
- `show_learning_analytics() -> None`: Show learning analytics
- `show_question_analytics() -> None`: Show question analytics
- `show_tag_analytics() -> None`: Show tag analytics
- `show_system_analytics() -> None`: Show system analytics
- `export_analytics() -> None`: Export analytics data

## OCR Processing

### OCRProcessor

```python
class OCRProcessor:
    def __init__(self, use_advanced_ocr: bool = True)
```

**Methods:**
- `process_screenshot(image_path: str) -> Dict`: Process image for OCR
- `batch_process_images(image_paths: List[str]) -> List[Dict]`: Process multiple images
- `test_ocr_accuracy(test_images: List[str]) -> Dict`: Test OCR accuracy
- `get_processing_statistics() -> Dict`: Get processing statistics
- `clear_ocr_cache() -> None`: Clear OCR cache

**Example:**
```python
ocr_processor = OCRProcessor(use_advanced_ocr=True)
result = ocr_processor.process_screenshot("image.png")
questions = result.get("questions", [])
```

### AdvancedOCRProcessor

```python
class AdvancedOCRProcessor:
    def __init__(self, cache_dir: str = "./data/ocr_cache")
```

**Methods:**
- `process_screenshot(image_path: str) -> Dict`: Process image with advanced OCR
- `batch_process_images(image_paths: List[str]) -> List[Dict]`: Batch process images
- `get_processing_statistics() -> Dict`: Get processing statistics
- `clear_cache() -> None`: Clear OCR cache
- `assess_image_quality(image_path: str) -> Dict`: Assess image quality

## Performance Optimization

### PerformanceOptimizer

```python
class PerformanceOptimizer:
    def __init__(self, cache_size: int = 1000, memory_threshold: float = 0.8)
```

**Methods:**
- `enable_caching(func: Callable) -> Callable`: Decorator for caching functions
- `optimize_memory_usage() -> Dict`: Optimize memory usage
- `optimize_database_queries(db_path: str) -> Dict`: Optimize database queries
- `optimize_file_operations(file_paths: List[str]) -> Dict`: Optimize file operations
- `get_performance_metrics() -> Dict`: Get performance metrics
- `clear_cache() -> None`: Clear all caches
- `set_optimization_level(level: str) -> None`: Set optimization level

**Example:**
```python
optimizer = PerformanceOptimizer(cache_size=1000, memory_threshold=0.8)

@optimizer.enable_caching
def expensive_function(x):
    return x * 2

metrics = optimizer.get_performance_metrics()
```

### IntelligentCache

```python
class IntelligentCache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600)
```

**Methods:**
- `get(key: str, default: Any = None) -> Any`: Get value from cache
- `set(key: str, value: Any, ttl: int = None) -> None`: Set value in cache
- `delete(key: str) -> bool`: Delete key from cache
- `clear() -> None`: Clear all cache entries
- `get_stats() -> Dict`: Get cache statistics
- `start_cleanup_thread() -> None`: Start background cleanup
- `stop_cleanup_thread() -> None`: Stop background cleanup

**Example:**
```python
cache = IntelligentCache(max_size=1000, default_ttl=3600)
cache.set("key1", "value1", ttl=1800)
value = cache.get("key1")
stats = cache.get_stats()
```

## Error Handling

### ErrorHandler

```python
class ErrorHandler:
    def __init__(self, log_errors: bool = True)
```

**Methods:**
- `handle_error(error: Exception, context: str = None) -> Dict`: Handle error
- `log_error(error: Exception, context: str = None) -> None`: Log error
- `get_error_statistics() -> Dict`: Get error statistics
- `clear_error_log() -> bool`: Clear error log
- `export_error_log() -> str`: Export error log

### InputValidator

```python
class InputValidator:
    def __init__(self)
```

**Methods:**
- `validate_question(question_data: Dict) -> Tuple[bool, List[str]]`: Validate question
- `validate_tag(tag_data: Dict) -> Tuple[bool, List[str]]`: Validate tag
- `validate_file_path(file_path: str) -> bool`: Validate file path
- `validate_email(email: str) -> bool`: Validate email
- `validate_number(value: Any, min_val: float = None, max_val: float = None) -> bool`: Validate number

### DataIntegrityChecker

```python
class DataIntegrityChecker:
    def __init__(self, db_manager: DatabaseManager)
```

**Methods:**
- `check_question_integrity() -> Dict`: Check question data integrity
- `check_tag_integrity() -> Dict`: Check tag data integrity
- `check_session_integrity() -> Dict`: Check session data integrity
- `check_referential_integrity() -> Dict`: Check referential integrity
- `repair_data_integrity() -> Dict`: Repair data integrity issues

## UI Components

### DisplayManager

```python
class DisplayManager:
    def __init__(self)
```

**Methods:**
- `show_welcome() -> None`: Show welcome message
- `show_main_menu() -> None`: Show main menu
- `show_question(question: Question, question_num: int, total: int) -> None`: Show question
- `show_quiz_results(results: Dict) -> None`: Show quiz results
- `show_analytics(analytics: Dict) -> None`: Show analytics
- `show_error(message: str) -> None`: Show error message
- `show_success(message: str) -> None`: Show success message
- `show_info(message: str) -> None`: Show info message
- `show_loading(message: str) -> None`: Show loading message
- `clear_screen() -> None`: Clear screen

### InputPrompts

```python
class InputPrompts:
    def __init__(self)
```

**Methods:**
- `get_text_input(prompt: str, required: bool = True) -> str`: Get text input
- `get_number_input(prompt: str, min_val: int = None, max_val: int = None) -> int`: Get number input
- `get_choice_input(prompt: str, choices: List[str]) -> str`: Get choice input
- `get_yes_no_input(prompt: str) -> bool`: Get yes/no input
- `get_menu_choice(max_choice: int) -> int`: Get menu choice
- `get_multiple_choice_input(prompt: str, choices: List[str]) -> List[str]`: Get multiple choice input
- `get_file_input(prompt: str, file_types: List[str] = None) -> str`: Get file input

### MenuSystem

```python
class MenuSystem:
    def __init__(self)
```

**Methods:**
- `display_main_menu() -> None`: Display main menu
- `display_question_creation_menu() -> None`: Display question creation menu
- `display_quiz_menu() -> None`: Display quiz menu
- `display_tag_management_menu() -> None`: Display tag management menu
- `display_analytics_menu() -> None`: Display analytics menu
- `display_settings_menu() -> None`: Display settings menu
- `display_help_menu() -> None`: Display help menu

## Database Components

### DatabaseManager

```python
class DatabaseManager:
    def __init__(self, db_path: str = "./data/quiz.db")
```

**Methods:**
- `initialize_database() -> bool`: Initialize database
- `backup_database() -> str`: Backup database
- `restore_database(backup_path: str) -> bool`: Restore database
- `optimize_database() -> Dict`: Optimize database
- `get_database_statistics() -> Dict`: Get database statistics
- `close_connection() -> None`: Close database connection

### DatabaseConnection

```python
class DatabaseConnection:
    def __init__(self, db_path: str)
```

**Methods:**
- `get_connection() -> sqlite3.Connection`: Get database connection
- `execute_query(query: str, params: tuple = None) -> List[Dict]`: Execute query
- `execute_update(query: str, params: tuple = None) -> int`: Execute update
- `begin_transaction() -> None`: Begin transaction
- `commit_transaction() -> None`: Commit transaction
- `rollback_transaction() -> None`: Rollback transaction

## File I/O Components

### FileImporter

```python
class FileImporter:
    def __init__(self)
```

**Methods:**
- `import_json(file_path: str) -> Dict`: Import JSON file
- `import_csv(file_path: str) -> Dict`: Import CSV file
- `import_html(file_path: str) -> Dict`: Import HTML file
- `validate_import_data(data: Dict) -> Tuple[bool, List[str]]`: Validate import data
- `get_import_statistics() -> Dict`: Get import statistics

### FileExporter

```python
class FileExporter:
    def __init__(self)
```

**Methods:**
- `export_json(data: Dict, file_path: str) -> bool`: Export to JSON
- `export_csv(data: Dict, file_path: str) -> bool`: Export to CSV
- `export_html(data: Dict, file_path: str) -> bool`: Export to HTML
- `get_export_statistics() -> Dict`: Get export statistics
- `compress_export(file_path: str) -> str`: Compress export file

## Utility Functions

### Performance Decorators

```python
@optimize_performance
def expensive_function(x):
    return x * 2

@cached(ttl=3600, cache_type='global')
def cached_function(x):
    return x * 2

@profile_operation("operation_name")
def profiled_function():
    pass
```

### Validation Functions

```python
def validate_question_data(data: Dict) -> Tuple[bool, List[str]]:
    """Validate question data structure"""
    pass

def validate_tag_data(data: Dict) -> Tuple[bool, List[str]]:
    """Validate tag data structure"""
    pass

def validate_session_data(data: Dict) -> Tuple[bool, List[str]]:
    """Validate session data structure"""
    pass
```

### Helper Functions

```python
def generate_id() -> str:
    """Generate unique identifier"""
    pass

def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    pass

def calculate_score(correct: int, total: int) -> float:
    """Calculate percentage score"""
    pass

def format_duration(seconds: int) -> str:
    """Format duration for display"""
    pass
```

## Error Codes

### Application Errors
- **E001**: Database connection error
- **E002**: File permission error
- **E003**: Memory allocation error
- **E004**: OCR processing error
- **E005**: Cache operation error
- **E006**: Validation error
- **E007**: Import/export error
- **E008**: Performance error

### Validation Errors
- **V001**: Invalid question format
- **V002**: Invalid tag format
- **V003**: Invalid session format
- **V004**: Invalid file format
- **V005**: Invalid input data

### System Errors
- **S001**: System resource error
- **S002**: Network connection error
- **S003**: File system error
- **S004**: Process error
- **S005**: Configuration error

## Configuration Options

### Application Configuration
```python
{
    "database": {
        "path": "./data/quiz.db",
        "backup_dir": "./data/backups",
        "connection_pool_size": 10
    },
    "performance": {
        "cache_size": 1000,
        "memory_threshold": 0.8,
        "optimization_level": "medium"
    },
    "ocr": {
        "enabled": True,
        "confidence_threshold": 0.7,
        "preprocessing": True
    },
    "logging": {
        "level": "INFO",
        "max_file_size": 10485760,
        "backup_count": 5
    }
}
```

### Environment Variables
```bash
QUIZ_DB_PATH=./data/quiz.db
QUIZ_BACKUP_DIR=./data/backups
QUIZ_CACHE_SIZE=1000
QUIZ_MEMORY_THRESHOLD=0.8
QUIZ_LOG_LEVEL=INFO
QUIZ_LOG_DIR=./data/logs
```

---

**For more detailed examples and usage patterns, see the [User Guide](USER_GUIDE.md) and [README](README.md).**
