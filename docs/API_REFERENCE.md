# API Reference

This document provides detailed API reference for the Quiz Application modules.

## Table of Contents

- [Data Models](#data-models)
- [Quiz Engine](#quiz-engine)
- [Question Manager](#question-manager)
- [Tag Manager](#tag-manager)
- [OCR Processor](#ocr-processor)
- [UI Components](#ui-components)

## Data Models

### Question Class

Represents a quiz question with validation and serialization.

#### Constructor
```python
Question(question_text: str, question_type: str, answers: List[Dict], tags: List[str], question_id: Optional[str] = None)
```

#### Methods

##### `validate() -> Dict[str, Any]`
Validates the question data structure and content.

**Returns:**
- `Dict` with `is_valid` (bool) and `errors` (List[str])

##### `to_dict() -> Dict[str, Any]`
Converts question to dictionary for serialization.

**Returns:**
- Dictionary representation of the question

##### `from_dict(data: Dict[str, Any]) -> Question`
Creates Question object from dictionary.

**Parameters:**
- `data`: Dictionary containing question data

**Returns:**
- Question object

##### `get_correct_answers() -> List[str]`
Gets list of correct answer IDs.

**Returns:**
- List of correct answer IDs

##### `update(**updates) -> None`
Updates question fields.

**Parameters:**
- `**updates`: Fields to update

### Tag Class

Represents a tag for organizing questions.

#### Constructor
```python
Tag(name: str, description: str = "", color: str = "", tag_id: Optional[str] = None)
```

#### Methods

##### `validate() -> Dict[str, Any]`
Validates the tag data.

**Returns:**
- Dictionary with validation result and errors

##### `to_dict() -> Dict[str, Any]`
Converts tag to dictionary for serialization.

**Returns:**
- Dictionary representation of the tag

##### `increment_question_count() -> None`
Increments the question count for this tag.

##### `decrement_question_count() -> None`
Decrements the question count for this tag.

## Quiz Engine

### QuizEngine Class

Core quiz engine for managing quiz sessions and logic.

#### Methods

##### `randomize_questions(questions: List[Dict]) -> List[Dict]`
Randomizes the order of questions using Fisher-Yates shuffle.

**Parameters:**
- `questions`: List of question dictionaries

**Returns:**
- List of questions in randomized order

##### `randomize_answers(question: Dict) -> Dict`
Randomizes the order of answer options for a question.

**Parameters:**
- `question`: Question dictionary with answers array

**Returns:**
- Question with randomized answer order

##### `start_quiz(questions: List[Dict]) -> str`
Initializes a new quiz session.

**Parameters:**
- `questions`: List of questions for the quiz

**Returns:**
- Session ID for the new quiz session

##### `submit_answer(session_id: str, question_id: str, selected_answers: Any) -> Dict`
Processes user's answer submission.

**Parameters:**
- `session_id`: Unique session identifier
- `question_id`: Question being answered
- `selected_answers`: User's selected answer(s)

**Returns:**
- Answer result with correctness and feedback

##### `calculate_score(session: Dict) -> float`
Calculates final quiz score and statistics.

**Parameters:**
- `session`: Completed quiz session

**Returns:**
- Score percentage

## Question Manager

### QuestionManager Class

Manages question bank operations and validation.

#### Constructor
```python
QuestionManager(data_dir: str = "data")
```

#### Methods

##### `create_question(question_text: str, question_type: str, answers: List[Dict], tags: List[str]) -> Dict`
Creates a new question with validation.

**Parameters:**
- `question_text`: The question content
- `question_type`: Type of question
- `answers`: List of answer dictionaries
- `tags`: List of tag names

**Returns:**
- Created question dictionary

##### `get_question(question_id: str) -> Optional[Dict]`
Gets a question by its ID.

**Parameters:**
- `question_id`: Question ID

**Returns:**
- Question dictionary or None

##### `get_all_questions() -> List[Dict]`
Gets all questions in the question bank.

**Returns:**
- List of all question dictionaries

##### `search_questions(search_term: str) -> List[Dict]`
Searches questions by text content.

**Parameters:**
- `search_term`: Search term

**Returns:**
- List of matching questions

##### `update_question(question_id: str, **updates) -> bool`
Updates an existing question.

**Parameters:**
- `question_id`: ID of question to update
- `**updates`: Fields to update

**Returns:**
- True if update successful

##### `delete_question(question_id: str) -> bool`
Deletes a question from the question bank.

**Parameters:**
- `question_id`: Question ID to delete

**Returns:**
- True if deletion successful

## Tag Manager

### TagManager Class

Manages tag operations and question organization.

#### Constructor
```python
TagManager(data_dir: str = "data")
```

#### Methods

##### `create_tag(name: str, description: str = "", color: str = "") -> Dict`
Creates a new tag.

**Parameters:**
- `name`: Tag name (must be unique)
- `description`: Optional description
- `color`: Optional hex color code

**Returns:**
- Created tag dictionary

##### `get_all_tags() -> List[Dict]`
Gets all tags sorted by name.

**Returns:**
- List of all tag dictionaries

##### `get_tag_by_name(name: str) -> Optional[Dict]`
Gets a tag by its name.

**Parameters:**
- `name`: Tag name

**Returns:**
- Tag dictionary or None

##### `search_tags(search_term: str) -> List[Dict]`
Searches tags by name or description.

**Parameters:**
- `search_term`: Search term

**Returns:**
- List of matching tags

##### `get_tag_statistics() -> Dict[str, Any]`
Gets statistics about tag usage.

**Returns:**
- Dictionary with tag usage statistics

## OCR Processor

### OCRProcessor Class

Handles OCR processing and image preprocessing for question extraction.

#### Methods

##### `process_screenshot(image_path: str) -> Dict[str, Any]`
Processes a screenshot to extract questions and answers.

**Parameters:**
- `image_path`: Path to the image file

**Returns:**
- Dictionary containing extracted text and processing results

##### `validate_image_format(image_path: str) -> bool`
Validates that the image is in a supported format.

**Parameters:**
- `image_path`: Path to image file

**Returns:**
- True if format is supported

##### `batch_process_images(image_paths: List[str]) -> List[Dict[str, Any]]`
Processes multiple images in batch.

**Parameters:**
- `image_paths`: List of image file paths

**Returns:**
- List of processing results for each image

## UI Components

### MenuSystem Class

Handles console menu display and navigation.

#### Methods

##### `display_main_menu() -> None`
Displays the main application menu.

##### `display_question_creation_menu() -> None`
Displays the question creation menu.

##### `get_user_choice(min_choice: int = 1, max_choice: int = 8) -> int`
Gets user menu choice with validation.

**Parameters:**
- `min_choice`: Minimum valid choice number
- `max_choice`: Maximum valid choice number

**Returns:**
- User's choice as integer

##### `display_confirmation(message: str) -> bool`
Displays a confirmation prompt.

**Parameters:**
- `message`: Confirmation message

**Returns:**
- True if user confirms

### InputPrompts Class

Handles user input prompts and validation.

#### Methods

##### `prompt_question_text() -> str`
Prompts user for question text with validation.

**Returns:**
- Validated question text

##### `prompt_question_type() -> str`
Prompts user for question type.

**Returns:**
- Selected question type

##### `prompt_answer_options(question_type: str) -> List[Dict[str, Any]]`
Prompts user for answer options based on question type.

**Parameters:**
- `question_type`: Type of question being created

**Returns:**
- List of answer dictionaries

##### `sanitize_input(text: str) -> str`
Sanitizes user input text.

**Parameters:**
- `text`: Raw input text

**Returns:**
- Sanitized text

### DisplayManager Class

Handles display of quiz content and results.

#### Methods

##### `display_question(question: Dict[str, Any], question_num: int, total_questions: int) -> None`
Displays a question with its answer options.

**Parameters:**
- `question`: Question dictionary
- `question_num`: Current question number
- `total_questions`: Total number of questions

##### `display_quiz_progress(current: int, total: int) -> None`
Displays quiz progress.

**Parameters:**
- `current`: Current question number
- `total`: Total number of questions

##### `display_feedback(is_correct: bool, correct_answers: List[str], question: Dict[str, Any]) -> None`
Displays immediate feedback for an answer.

**Parameters:**
- `is_correct`: Whether the answer was correct
- `correct_answers`: List of correct answer IDs
- `question`: Question dictionary

##### `display_results(session: Dict[str, Any]) -> None`
Displays final quiz results.

**Parameters:**
- `session`: Quiz session dictionary

## Error Handling

All classes include comprehensive error handling with custom exception types:

- `ValueError`: For validation errors
- `FileNotFoundError`: For missing files
- `RuntimeError`: For system errors

## Logging

All modules use structured logging with the following levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## Data Formats

### Question Format
```json
{
  "id": "string",
  "question_text": "string",
  "question_type": "multiple_choice|true_false|select_all",
  "answers": [
    {
      "id": "string",
      "text": "string",
      "is_correct": boolean
    }
  ],
  "tags": ["string"],
  "created_at": "ISO datetime",
  "last_modified": "ISO datetime",
  "usage_count": number
}
```

### Tag Format
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "color": "string",
  "question_count": number,
  "created_at": "ISO datetime",
  "created_by": "string"
}
```

### Quiz Session Format
```json
{
  "id": "string",
  "questions": [Question],
  "current_question_index": number,
  "answers": [
    {
      "question_id": "string",
      "selected_answers": "string|array",
      "is_correct": boolean,
      "timestamp": "ISO datetime"
    }
  ],
  "score": number,
  "start_time": "ISO datetime",
  "end_time": "ISO datetime",
  "is_complete": boolean
}
```
