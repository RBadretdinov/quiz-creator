# Quiz Application Project Specification

## Project Overview

The Quiz Application is a comprehensive tool designed to create, manage, and administer quizzes from user-provided questions and answers. The application supports multiple input methods including text input and screenshot processing, with advanced features for question randomization and real-time feedback.

## Core Features

### 1. Question Input Methods
- **Text Input**: Direct text entry for questions and answers
- **Screenshot Processing**: OCR-based extraction of questions and answers from images
- **Batch Import**: Support for importing multiple questions at once

### 2. Question Management
- **Randomization**: Automatic shuffling of question order and answer options
- **Question Bank**: Storage and retrieval of previously created questions
- **Tag System**: User-defined tags for organizing questions into custom sections/categories
- **Question Types**: Support for multiple choice, true/false, and "select all that apply" questions

### 3. Quiz Administration
- **Real-time Feedback**: Immediate correct/incorrect answer validation
- **Progress Tracking**: Visual indicators of quiz completion status
- **Score Calculation**: Automatic scoring with detailed results

## Technical Requirements

### Functional Requirements

#### FR1: Question Input System
- **FR1.1**: Accept text input for questions and multiple choice answers
- **FR1.2**: Process screenshots/images to extract questions and answers using OCR
- **FR1.3**: Validate input format and completeness
- **FR1.4**: Support various question types (multiple choice, true/false, select all that apply)
- **FR1.5**: Allow users to create and assign custom tags to questions
- **FR1.6**: Enable users to specify which tag/section to save questions under

#### FR2: Question Randomization
- **FR2.1**: Randomize the order of questions in each quiz session
- **FR2.2**: Randomize the order of answer options for each question
- **FR2.3**: Ensure randomization is different for each quiz attempt
- **FR2.4**: Maintain question-answer pairing integrity during randomization

#### FR3: Answer Validation
- **FR3.1**: Compare user answers against correct answers
- **FR3.2**: Provide immediate feedback (correct/incorrect)
- **FR3.3**: Display correct answer when user selects wrong option
- **FR3.4**: Track and display overall quiz score
- **FR3.5**: Handle "select all that apply" questions with multiple correct answers
- **FR3.6**: Validate partial credit for multi-select questions

#### FR4: Console Interface
- **FR4.1**: Intuitive console-based question input with tag selection
- **FR4.2**: Clean console quiz-taking interface supporting different question types
- **FR4.3**: Clear results display with detailed feedback in console
- **FR4.4**: Progress indicators during quiz (text-based)
- **FR4.5**: Console-based tag management for creating and organizing question categories
- **FR4.6**: Menu-driven navigation system

### Non-Functional Requirements

#### NFR1: Performance
- **NFR1.1**: OCR processing should complete within 5 seconds for standard images
- **NFR1.2**: Quiz interface should respond within 100ms to user interactions
- **NFR1.3**: Support for quizzes with up to 100 questions

#### NFR2: Usability
- **NFR2.1**: Console application should be usable without prior training
- **NFR2.2**: Clear menu navigation and help text
- **NFR2.3**: Consistent command-line interface patterns

#### NFR3: Reliability
- **NFR3.1**: 99% uptime for core functionality
- **NFR3.2**: Graceful handling of OCR failures
- **NFR3.3**: Data persistence across sessions

## System Architecture

### Component Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Layer   │    │  Processing     │    │   Output Layer  │
│                 │    │     Layer       │    │                 │
│ • Text Input    │───▶│ • OCR Engine    │───▶│ • Quiz Display  │
│ • Image Upload  │    │ • Validation    │    │ • Results       │
│ • File Import   │    │ • Randomization │    │ • Feedback      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Layer    │    │  Business Logic │    │   UI Layer      │
│                 │    │                 │    │                 │
│ • Question Bank │    │ • Quiz Engine   │    │ • React/Vue     │
│ • User Data     │    │ • Score Logic   │    │ • Components    │
│ • Settings      │    │ • Randomization │    │ • Styling       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Data Structures

### Question Object
```javascript
{
  id: string,                    // Unique question identifier
  questionText: string,          // The question content
  questionType: string,          // 'multiple_choice', 'true_false', 'select_all'
  answers: [                     // Array of answer options
    {
      id: string,               // Unique answer identifier
      text: string,             // Answer text
      isCorrect: boolean        // Whether this answer is correct
    }
  ],
  tags: [string],               // Array of tag names
  createdAt: Date,              // Creation timestamp
  lastModified: Date            // Last modification timestamp
}
```

### Tag Object
```javascript
{
  id: string,                   // Unique tag identifier
  name: string,                 // Tag name (unique)
  description: string,          // Optional description
  questionCount: number,        // Number of questions with this tag
  createdAt: Date,              // Creation timestamp
  color: string                 // Optional color for UI display
}
```

### Quiz Session Object
```javascript
{
  id: string,                   // Unique session identifier
  questions: [QuestionObject],  // Array of questions in this quiz
  currentQuestionIndex: number, // Current question position
  answers: [                    // User's answers
    {
      questionId: string,       // Question being answered
      selectedAnswers: string|array, // User's selection(s)
      isCorrect: boolean,       // Whether answer is correct
      timestamp: Date           // When answer was submitted
    }
  ],
  score: number,                // Current score percentage
  startTime: Date,              // Quiz start timestamp
  endTime: Date                 // Quiz end timestamp (null if ongoing)
}
```

## Required Functions

### 1. Input Processing Functions

#### `processTextInput(questionText, answers, questionType, tags)`
- **Purpose**: Process and validate text-based question input
- **Parameters**: 
  - `questionText` (string): The question text
  - `answers` (array): Array of answer objects with text and correct flag
  - `questionType` (string): Type of question ('multiple_choice', 'true_false', 'select_all')
  - `tags` (array): Array of tag strings for categorization
- **Returns**: Question object with validated data
- **Validation**: Ensures question text is not empty and appropriate number of correct answers for question type

#### `processScreenshot(imageFile)`
- **Purpose**: Extract questions and answers from uploaded images using OCR
- **Parameters**: 
  - `imageFile` (File): Image file containing questions/answers
- **Returns**: Array of extracted question objects
- **Dependencies**: OCR service (Tesseract.js or cloud OCR API)

#### `validateQuestion(questionObject)`
- **Purpose**: Validate question structure and completeness
- **Parameters**: 
  - `questionObject` (object): Question data to validate
- **Returns**: Validation result with error messages if any
- **Validation Rules**: 
  - Question text must be non-empty
  - At least 2 answer options required
  - For multiple choice: exactly one correct answer
  - For true/false: exactly two options with one correct
  - For select all: at least one correct answer (can be multiple)
  - At least one tag must be specified

### 2. Randomization Functions

#### `randomizeQuestions(questionArray)`
- **Purpose**: Shuffle the order of questions in a quiz
- **Parameters**: 
  - `questionArray` (array): Array of question objects
- **Returns**: New array with randomized question order
- **Algorithm**: Fisher-Yates shuffle for uniform distribution

#### `randomizeAnswers(questionObject)`
- **Purpose**: Shuffle the order of answer options for a specific question
- **Parameters**: 
  - `questionObject` (object): Question with answer array
- **Returns**: Question object with randomized answer order
- **Preservation**: Maintains correct answer flag during shuffling

#### `createRandomizedQuiz(questionBank, questionCount)`
- **Purpose**: Create a new quiz with randomized questions and answers
- **Parameters**: 
  - `questionBank` (array): Source questions
  - `questionCount` (number): Number of questions to include
- **Returns**: Complete quiz object with randomized content

### 3. Quiz Management Functions

#### `startQuiz(quizObject)`
- **Purpose**: Initialize a new quiz session
- **Parameters**: 
  - `quizObject` (object): Quiz configuration and questions
- **Returns**: Quiz session object with initial state
- **State Management**: Tracks current question, score, and progress

#### `submitAnswer(sessionId, questionId, selectedAnswers)`
- **Purpose**: Process user's answer submission
- **Parameters**: 
  - `sessionId` (string): Unique session identifier
  - `questionId` (string): Question being answered
  - `selectedAnswers` (string|array): User's selected answer(s) - string for single choice, array for select all
- **Returns**: Answer result object with correctness and feedback
- **Validation**: Compares against correct answer(s) and updates session state
- **Multi-select Support**: Handles both single and multiple answer selections

#### `getNextQuestion(sessionId)`
- **Purpose**: Retrieve the next question in the quiz sequence
- **Parameters**: 
  - `sessionId` (string): Current quiz session
- **Returns**: Next question object or null if quiz complete
- **State Management**: Advances session to next question

### 4. Feedback and Scoring Functions

#### `calculateScore(sessionObject)`
- **Purpose**: Calculate final quiz score and statistics
- **Parameters**: 
  - `sessionObject` (object): Completed quiz session
- **Returns**: Score object with percentage, correct count, and details
- **Calculation**: (Correct answers / Total questions) * 100

#### `provideFeedback(answerResult)`
- **Purpose**: Generate immediate feedback for user answers
- **Parameters**: 
  - `answerResult` (object): Result from answer submission
- **Returns**: Feedback object with message and correct answer display
- **Content**: Congratulatory message for correct, shows correct answer for incorrect (no explanations)

#### `generateResultsReport(sessionObject)`
- **Purpose**: Create comprehensive quiz results report
- **Parameters**: 
  - `sessionObject` (object): Completed quiz session
- **Returns**: Detailed results object with statistics and question review
- **Content**: Score breakdown, time taken, question-by-question review

### 5. Data Management Functions

#### `saveQuestion(questionObject)`
- **Purpose**: Store question in the question bank
- **Parameters**: 
  - `questionObject` (object): Validated question data
- **Returns**: Success confirmation with question ID
- **Storage**: Local storage or database persistence

#### `loadQuestionBank(tags)`
- **Purpose**: Retrieve questions from storage
- **Parameters**: 
  - `tags` (array, optional): Filter by question tags
- **Returns**: Array of question objects
- **Filtering**: Support for tag-based retrieval with multiple tag support

#### `createTag(tagName, description)`
- **Purpose**: Create a new tag for organizing questions
- **Parameters**: 
  - `tagName` (string): Name of the tag
  - `description` (string, optional): Description of the tag
- **Returns**: Tag object with ID and metadata
- **Validation**: Ensures tag name is unique and non-empty

#### `getAllTags()`
- **Purpose**: Retrieve all available tags
- **Parameters**: None
- **Returns**: Array of tag objects
- **Usage**: For tag selection dropdowns and management interfaces

#### `deleteTag(tagId)`
- **Purpose**: Remove a tag and reassign its questions
- **Parameters**: 
  - `tagId` (string): ID of tag to delete
- **Returns**: Success confirmation
- **Behavior**: Prompts user to reassign questions to other tags

#### `exportQuiz(quizObject, format)`
- **Purpose**: Export quiz data in various formats
- **Parameters**: 
  - `quizObject` (object): Quiz to export
  - `format` (string): Export format ('json', 'csv', 'pdf')
- **Returns**: Exported data or file download
- **Formats**: JSON for data, CSV for spreadsheet, PDF for printing

### 6. Tag Management Functions

#### `createTag(tagName, description, color)`
- **Purpose**: Create a new tag for organizing questions
- **Parameters**: 
  - `tagName` (string): Name of the tag (must be unique)
  - `description` (string, optional): Description of the tag
  - `color` (string, optional): Hex color code for UI display
- **Returns**: Tag object with ID and metadata
- **Validation**: Ensures tag name is unique and non-empty

#### `getAllTags()`
- **Purpose**: Retrieve all available tags
- **Parameters**: None
- **Returns**: Array of tag objects sorted by name
- **Usage**: For tag selection dropdowns and management interfaces

#### `getQuestionsByTag(tagName)`
- **Purpose**: Retrieve all questions associated with a specific tag
- **Parameters**: 
  - `tagName` (string): Name of the tag to filter by
- **Returns**: Array of question objects
- **Usage**: For creating tag-specific quizzes

#### `updateQuestionTags(questionId, newTags)`
- **Purpose**: Update the tags associated with a question
- **Parameters**: 
  - `questionId` (string): ID of the question to update
  - `newTags` (array): New array of tag names
- **Returns**: Success confirmation
- **Validation**: Ensures all tags exist before updating

#### `deleteTag(tagId)`
- **Purpose**: Remove a tag and handle question reassignment
- **Parameters**: 
  - `tagId` (string): ID of tag to delete
- **Returns**: Success confirmation with reassignment options
- **Behavior**: Prompts user to reassign questions to other tags or delete questions

#### `getTagStatistics()`
- **Purpose**: Get statistics about tag usage
- **Parameters**: None
- **Returns**: Object with tag usage statistics
- **Content**: Question counts per tag, most/least used tags

### 7. Utility Functions

#### `generateSessionId()`
- **Purpose**: Create unique session identifiers
- **Parameters**: None
- **Returns**: Unique string identifier
- **Format**: UUID v4 or timestamp-based ID

#### `formatTimeElapsed(startTime, endTime)`
- **Purpose**: Calculate and format quiz duration
- **Parameters**: 
  - `startTime` (Date): Quiz start timestamp
  - `endTime` (Date): Quiz end timestamp
- **Returns**: Formatted time string (e.g., "2 minutes 30 seconds")

#### `sanitizeInput(text)`
- **Purpose**: Clean and validate user input text
- **Parameters**: 
  - `text` (string): Raw user input
- **Returns**: Sanitized text string
- **Security**: Remove potentially harmful content, trim whitespace

## Console Application Structure

### Main Application Flow
```
Quiz Application
├── Main Menu
│   ├── 1. Create Question
│   ├── 2. Take Quiz
│   ├── 3. Manage Tags
│   ├── 4. View Question Bank
│   ├── 5. Import from Screenshot
│   └── 6. Exit
│
├── Question Creation Flow
│   ├── Enter question text
│   ├── Select question type
│   ├── Add answer options
│   ├── Mark correct answers
│   ├── Assign tags
│   └── Save question
│
└── Quiz Taking Flow
    ├── Select tags/categories
    ├── Choose number of questions
    ├── Answer questions (one by one)
    ├── View immediate feedback
    └── Display final results
```

### Console Interface Design
- **Menu-driven navigation** with numbered options
- **Clear prompts** for all user inputs
- **Immediate feedback** for all actions
- **Progress indicators** (e.g., "Question 3 of 10")
- **Error handling** with helpful messages
- **Help text** available at any time

### File Structure
```
quiz/
├── docs/
│   └── PROJECT_SPECIFICATION.md
├── src/
│   ├── main.py              # Main application entry point
│   ├── quiz_engine.py       # Core quiz logic
│   ├── question_manager.py  # Question CRUD operations
│   ├── tag_manager.py       # Tag management
│   ├── ocr_processor.py     # Screenshot processing
│   ├── ui/
│   │   ├── menus.py         # Menu display functions
│   │   ├── prompts.py       # User input prompts
│   │   └── display.py       # Results and feedback display
│   └── models/
│       ├── question.py      # Question data model
│       ├── tag.py           # Tag data model
│       └── quiz_session.py  # Quiz session model
├── data/
│   ├── questions.json       # Question storage
│   ├── tags.json           # Tag storage
│   └── quiz_sessions.json  # Session history
├── tests/
│   └── test_*.py           # Unit tests
├── requirements.txt        # Python dependencies
└── README.md              # Setup and usage instructions
```

## Technology Stack

### Core Platform
- **Language**: Python 3.8+
- **Interface**: Console/Command-line only (no web UI)
- **Database**: SQLite (built into Python)
- **OCR Service**: Tesseract (via pytesseract) for screenshot processing
- **File Storage**: JSON files for question banks and quiz data

### Python Dependencies
- **Core**: Standard library only for basic functionality
- **OCR**: `pytesseract` for image processing
- **Image Processing**: `Pillow` for image handling
- **Data Handling**: `json` (built-in) for file storage
- **Testing**: `unittest` (built-in) or `pytest`

### Development Tools
- **Version Control**: Git
- **Testing**: unittest (built-in) or pytest
- **Code Formatting**: black, flake8
- **Package Management**: pip

## Implementation Phases

### Phase 1: Core Console Application (Week 1)
- Basic console interface for question input
- Question randomization algorithms
- Simple quiz taking interface with answer validation
- Basic scoring and feedback system
- JSON file storage for questions

### Phase 2: Enhanced Features (Week 2)
- Tag system implementation
- Question bank management via console
- "Select all that apply" question type
- Data persistence with SQLite

### Phase 3: Advanced Input (Week 3)
- Screenshot/OCR integration
- File import/export functionality
- Batch question processing
- Enhanced console UI with menus

### Phase 4: Polish and Testing (Week 4)
- Comprehensive testing
- Error handling and validation
- Documentation completion
- Performance optimization

## Success Criteria

### Functional Success
- ✅ Users can input questions via text and screenshots
- ✅ Questions and answers are properly randomized
- ✅ Real-time feedback is provided for all answers (without explanations)
- ✅ Quiz scores are accurately calculated and displayed
- ✅ Tag system allows users to organize questions into custom categories
- ✅ "Select all that apply" questions are properly handled
- ✅ Users can create and manage custom tags for question organization

### Technical Success
- ✅ Application loads and responds within acceptable time limits
- ✅ OCR processing achieves >90% accuracy on clear images
- ✅ All functions handle edge cases gracefully
- ✅ Code is maintainable and well-documented

### User Experience Success
- ✅ Console interface is intuitive for first-time users
- ✅ Quiz-taking experience is smooth and engaging
- ✅ Results are clearly presented and actionable
- ✅ Application works consistently across different terminal environments

## Future Enhancements

### Advanced Features
- **Multiplayer Mode**: Real-time quiz competitions
- **Analytics Dashboard**: Detailed performance tracking
- **Question Difficulty**: Adaptive difficulty based on performance
- **Voice Input**: Speech-to-text for question input
- **Mobile App**: Native mobile application
- **Cloud Sync**: Cross-device question bank synchronization

### Integration Possibilities
- **Learning Management Systems**: Integration with LMS platforms
- **Educational APIs**: Connection to educational content providers
- **Social Features**: Sharing quizzes and competing with friends
- **AI Enhancement**: Automatic question generation from content

---

*This specification serves as the foundation for developing a comprehensive quiz application that meets all stated requirements while providing a solid foundation for future enhancements.*
