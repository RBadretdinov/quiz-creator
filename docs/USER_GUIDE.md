# Quiz Application - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Main Menu Navigation](#main-menu-navigation)
3. [Creating Questions](#creating-questions)
4. [Taking Quizzes](#taking-quizzes)
5. [Tag Management](#tag-management)
6. [Analytics Dashboard](#analytics-dashboard)
7. [OCR Processing](#ocr-processing)
8. [File Import/Export](#file-importexport)
9. [Settings & Configuration](#settings--configuration)
10. [Troubleshooting](#troubleshooting)

## Getting Started

### First Launch
When you first run the application, you'll see the main menu:

```
============================================================
           QUIZ APPLICATION - MAIN MENU
============================================================

1. Create Question
2. Take Quiz
3. Manage Tags
4. Enhanced Question Management
5. Question Types
6. Database Management
7. Analytics Dashboard
8. Import from Screenshot
9. Settings
10. Help
0. Exit

------------------------------------------------------------
```

### Navigation Tips
- **Use numbers** to select menu options
- **Press Enter** to confirm selections
- **Use '0' or 'q'** to go back or exit
- **Use 'h'** for help in any menu

## Main Menu Navigation

### 1. Create Question
Create new questions for your question bank.

**Workflow:**
1. Enter question text
2. Select question type
3. Add answer options
4. Assign tags
5. Save question

**Question Types:**
- **Multiple Choice**: Single correct answer
- **True/False**: Binary choice
- **Select All**: Multiple correct answers
- **Fill in the Blank**: Text-based answers

### 2. Take Quiz
Start a quiz session with customizable parameters.

**Quiz Options:**
- **Number of Questions**: 1-100 questions
- **Question Types**: Filter by specific types
- **Tags**: Include/exclude specific tags
- **Time Limit**: Optional time constraints
- **Randomization**: Question and answer order

**Quiz Session:**
- Answer questions one by one
- View progress and time remaining
- Pause and resume sessions
- Get immediate feedback
- View detailed results

### 3. Manage Tags
Organize questions with hierarchical tags.

**Tag Operations:**
- **Create Tags**: Simple and hierarchical tags
- **Search Tags**: Find tags by name or description
- **Edit Tags**: Modify tag properties
- **Delete Tags**: Remove unused tags
- **Bulk Operations**: Mass tag operations

**Hierarchical Tags:**
- **Parent Tags**: Main categories
- **Child Tags**: Subcategories
- **Tag Aliases**: Alternative names
- **Usage Tracking**: Monitor tag usage

### 4. Enhanced Question Management
Advanced question management and editing.

**Features:**
- **Browse Questions**: Paginated question listing
- **Search Questions**: Find questions by text or tags
- **Edit Questions**: Modify existing questions
- **Delete Questions**: Remove questions
- **Bulk Operations**: Mass question operations
- **Question Statistics**: View question analytics

### 5. Question Types
Manage different question types and templates.

**Question Type Management:**
- **View Types**: See available question types
- **Templates**: Pre-built question templates
- **Validation**: Question type validation
- **Conversion**: Convert between question types
- **Statistics**: Question type distribution

### 6. Database Management
Manage database operations and backups.

**Database Operations:**
- **Backup Database**: Create database backups
- **Restore Database**: Restore from backups
- **Optimize Database**: Improve performance
- **View Statistics**: Database usage statistics
- **Maintenance**: Database cleanup and repair

### 7. Analytics Dashboard
View performance and learning analytics.

**Analytics Categories:**
- **Performance Analytics**: Quiz performance metrics
- **Learning Analytics**: Learning progress tracking
- **Question Analytics**: Question effectiveness analysis
- **Tag Analytics**: Tag usage and performance
- **System Analytics**: System health and usage

### 8. Import from Screenshot
Use OCR to import questions from images.

**OCR Workflow:**
1. **Select Image**: Choose image file
2. **Preprocessing**: Automatic image enhancement
3. **Text Extraction**: OCR processing
4. **Question Parsing**: Parse extracted text
5. **Review & Edit**: Review and correct
6. **Save Questions**: Add to question bank

**Supported Formats:**
- PNG, JPEG, TIFF, BMP images
- High-resolution images recommended
- Clear text for better accuracy

### 9. Settings
Configure application preferences.

**Settings Categories:**
- **Performance**: Cache and optimization settings
- **UI**: Display and theme preferences
- **Database**: Database configuration
- **OCR**: OCR processing settings
- **Logging**: Logging configuration

### 10. Help
Access help and documentation.

**Help Options:**
- **Quick Start**: Basic usage guide
- **Tutorials**: Step-by-step tutorials
- **FAQ**: Frequently asked questions
- **Keyboard Shortcuts**: Available shortcuts
- **Troubleshooting**: Common issues and solutions

## Creating Questions

### Question Creation Process

#### Step 1: Question Text
```
Enter question text: What is the capital of France?
```

#### Step 2: Question Type
```
Select question type:
1. Multiple Choice
2. True/False
3. Select All
4. Fill in the Blank
```

#### Step 3: Answer Options
**Multiple Choice:**
```
Enter answer options:
A) Paris
B) London
C) Berlin
D) Madrid

Enter correct answer (A, B, C, or D): A
```

**True/False:**
```
Enter correct answer (True/False): True
```

**Select All:**
```
Enter answer options:
A) Paris
B) London
C) Berlin
D) Madrid

Enter correct answers (comma-separated): A, B
```

**Fill in the Blank:**
```
Enter correct answer: Paris
Enter alternative answers (comma-separated): paris, PARIS
```

#### Step 4: Tags
```
Enter tags (comma-separated): geography, europe, capitals
```

#### Step 5: Save Question
```
Question saved successfully!
Question ID: q_12345678-1234-1234-1234-123456789abc
```

### Question Templates

#### Geography Template
```
Question: What is the capital of [Country]?
Type: Multiple Choice
Answers: [Capital], [City1], [City2], [City3]
Tags: geography, capitals, [Country]
```

#### Math Template
```
Question: What is [Number1] + [Number2]?
Type: Fill in the Blank
Answer: [Sum]
Tags: math, arithmetic, addition
```

#### Science Template
```
Question: What is the chemical symbol for [Element]?
Type: Multiple Choice
Answers: [Symbol], [Symbol1], [Symbol2], [Symbol3]
Tags: science, chemistry, elements
```

### Question Validation

The system automatically validates questions for:
- **Text Quality**: Clear and unambiguous questions
- **Answer Validity**: Correct answer format and options
- **Tag Relevance**: Appropriate tag assignment
- **Type Consistency**: Question type matches content

## Taking Quizzes

### Quiz Configuration

#### Basic Quiz
```
Number of questions: 10
Question types: All
Tags: All
Time limit: None
Randomization: Yes
```

#### Advanced Quiz
```
Number of questions: 25
Question types: Multiple Choice, True/False
Tags: geography, history
Time limit: 30 minutes
Randomization: Yes
Difficulty: Mixed
```

### Quiz Session

#### Question Display
```
Question 1 of 10
Time remaining: 25:30

What is the capital of France?

A) Paris
B) London
C) Berlin
D) Madrid

Enter your answer (A, B, C, or D): 
```

#### Answer Submission
```
Your answer: A
Correct! ✓
Score: 1/1
Time taken: 5.2 seconds
```

#### Session Progress
```
Progress: 3/10 (30%)
Score: 2/3 (66.7%)
Time elapsed: 2:15
Average time per question: 45 seconds
```

### Quiz Results

#### Summary
```
Quiz Completed!
Total questions: 10
Correct answers: 8
Score: 80%
Time taken: 12:30
Average time per question: 1:15
```

#### Detailed Results
```
Question 1: ✓ Correct (5.2s)
Question 2: ✗ Incorrect (8.1s)
Question 3: ✓ Correct (3.4s)
...
```

#### Performance Analysis
```
Best performance: Questions 1, 3, 5, 7, 8, 9, 10
Needs improvement: Questions 2, 4, 6
Average response time: 1:15
Fastest question: Question 3 (3.4s)
Slowest question: Question 2 (8.1s)
```

## Tag Management

### Creating Tags

#### Simple Tags
```
Tag name: geography
Description: Questions about geography
Parent tag: None
Aliases: geo, world
```

#### Hierarchical Tags
```
Tag name: europe
Description: Questions about Europe
Parent tag: geography
Aliases: eu, european
```

#### Tag Aliases
```
Tag name: mathematics
Aliases: math, maths, arithmetic
Description: Mathematical questions
```

### Tag Operations

#### Search Tags
```
Search tags by:
1. Name: geography
2. Description: Contains "world"
3. Aliases: math
4. Parent tag: geography
5. Usage count: > 5
```

#### Bulk Operations
```
Select tags for bulk operation:
1. geography
2. europe
3. capitals

Bulk operations:
1. Change parent tag
2. Add aliases
3. Delete tags
4. Export tags
```

### Tag Statistics

#### Usage Statistics
```
Tag: geography
Usage count: 45
Last used: 2024-01-15
Child tags: 3
Questions: 45
```

#### Performance Statistics
```
Tag: geography
Average score: 78.5%
Total attempts: 45
Success rate: 78.5%
```

## Analytics Dashboard

### Performance Analytics

#### Session Statistics
```
Total Sessions: 25
Total Questions: 250
Total Correct: 200
Average Score: 80.0%
Average Accuracy: 80.0%
Total Time Spent: 1,250 seconds
Average Session Duration: 50.0 seconds
Questions per Minute: 12.0
```

#### Performance Trends
```
Week 1: 75% average score
Week 2: 80% average score
Week 3: 85% average score
Week 4: 82% average score
```

#### Best Performance
```
Best Score: 95%
Date: 2024-01-15
Session Duration: 45 minutes
Questions: 50
```

### Learning Analytics

#### Progress Tracking
```
Total Questions Attempted: 250
Unique Questions: 200
Overall Accuracy: 80.0%
Learning Velocity: 0.85
Retention Rate: 78.5%
```

#### Knowledge Gaps
```
Areas needing improvement:
- Geography: 65% accuracy
- History: 70% accuracy
- Science: 75% accuracy
```

#### Mastered Questions
```
Mastered Questions (90%+ accuracy):
- Capital cities: 95% accuracy
- Basic math: 92% accuracy
- Science facts: 90% accuracy
```

### Question Analytics

#### Question Effectiveness
```
Total Attempts: 250
Unique Users: 1
Success Rate: 80.0%
Average Response Time: 1.2 seconds
Difficulty Score: 0.65
Popularity Score: 8.5
Effectiveness Score: 0.78
```

#### Response Time Distribution
```
Fast (< 30s): 150 questions
Medium (30-60s): 80 questions
Slow (> 60s): 20 questions
```

### Tag Analytics

#### Most Used Tags
```
1. geography: 45 uses
2. history: 30 uses
3. science: 25 uses
4. math: 20 uses
5. literature: 15 uses
```

#### Least Used Tags
```
1. philosophy: 2 uses
2. art: 3 uses
3. music: 4 uses
4. sports: 5 uses
5. technology: 6 uses
```

### System Analytics

#### System Health
```
Total Questions: 500
Total Tags: 50
Total Sessions: 25
Total Users: 1
Database Size: 2.5 MB
System Health: 95.0%
```

#### Usage Statistics
```
Daily Active Users: 1
Weekly Active Users: 1
Monthly Active Users: 1
Average Session Duration: 50 minutes
```

## OCR Processing

### Supported Image Formats

#### Image Types
- **PNG**: Best for text with transparency
- **JPEG**: Good for photographs and screenshots
- **TIFF**: High-quality images with multiple pages
- **BMP**: Uncompressed bitmap images

#### Image Requirements
- **Resolution**: Minimum 300 DPI recommended
- **Text Size**: Clear, readable text
- **Contrast**: High contrast between text and background
- **Orientation**: Text should be horizontal

### OCR Workflow

#### Step 1: Select Image
```
Select image file:
1. Browse for file
2. Recent files
3. Clipboard image
```

#### Step 2: Preprocessing
```
Image preprocessing:
- Resizing to optimal DPI
- Noise reduction
- Contrast enhancement
- Skew correction
- Text enhancement
```

#### Step 3: Text Extraction
```
OCR Processing:
- Multiple OCR configurations
- Confidence scoring
- Best result selection
- Text validation
```

#### Step 4: Question Parsing
```
Parsing extracted text:
- Question identification
- Answer option detection
- Question type determination
- Answer validation
```

#### Step 5: Review & Edit
```
Review extracted questions:
1. Question: What is the capital of France?
   Type: Multiple Choice
   Answers: A) Paris, B) London, C) Berlin, D) Madrid
   Correct: A
   
2. Question: What is 2 + 2?
   Type: Fill in the Blank
   Answer: 4
```

#### Step 6: Save Questions
```
Save questions to question bank:
- Validate question format
- Assign tags
- Save to database
- Update statistics
```

### OCR Quality Assessment

#### Image Quality Metrics
```
Sharpness: 85%
Contrast: 90%
Brightness: 80%
OCR Suitability: 88%
```

#### Recommendations
```
For better OCR results:
- Increase image resolution
- Improve contrast
- Reduce noise
- Correct skew angle
```

### OCR Performance

#### Processing Statistics
```
Images processed: 25
Successful extractions: 23
Failed extractions: 2
Average processing time: 3.2 seconds
Average confidence: 85%
```

#### Accuracy Testing
```
OCR Accuracy Test:
- Test images: 50
- Correct extractions: 45
- Accuracy: 90%
- Average confidence: 87%
```

## File Import/Export

### Supported Formats

#### JSON Format
```json
{
  "questions": [
    {
      "id": "q_12345678-1234-1234-1234-123456789abc",
      "question_text": "What is the capital of France?",
      "question_type": "multiple_choice",
      "answers": [
        {"text": "Paris", "is_correct": true},
        {"text": "London", "is_correct": false},
        {"text": "Berlin", "is_correct": false},
        {"text": "Madrid", "is_correct": false}
      ],
      "tags": ["geography", "europe", "capitals"],
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "tags": [
    {
      "id": "t_12345678-1234-1234-1234-123456789abc",
      "name": "geography",
      "description": "Questions about geography",
      "parent_id": null,
      "aliases": ["geo", "world"]
    }
  ]
}
```

#### CSV Format
```csv
Question ID,Question Text,Question Type,Answer 1,Answer 2,Answer 3,Answer 4,Correct Answer,Tags
q_12345678-1234-1234-1234-123456789abc,"What is the capital of France?",multiple_choice,Paris,London,Berlin,Madrid,A,"geography, europe, capitals"
```

#### HTML Format
```html
<!DOCTYPE html>
<html>
<head>
    <title>Quiz Questions Export</title>
</head>
<body>
    <h1>Quiz Questions</h1>
    <div class="question">
        <h2>Question 1</h2>
        <p>What is the capital of France?</p>
        <ul>
            <li>A) Paris</li>
            <li>B) London</li>
            <li>C) Berlin</li>
            <li>D) Madrid</li>
        </ul>
        <p><strong>Correct Answer:</strong> A</p>
        <p><strong>Tags:</strong> geography, europe, capitals</p>
    </div>
</body>
</html>
```

### Import Process

#### Step 1: Select Format
```
Select import format:
1. JSON
2. CSV
3. HTML
4. Auto-detect
```

#### Step 2: Select File
```
Select file to import:
1. Browse for file
2. Recent files
3. URL import
```

#### Step 3: Validate Data
```
Data validation:
- Format validation: ✓
- Data integrity: ✓
- Question validation: ✓
- Tag validation: ✓
```

#### Step 4: Review Import
```
Import preview:
- Questions: 25
- Tags: 10
- Valid questions: 23
- Invalid questions: 2
- New tags: 5
- Existing tags: 5
```

#### Step 5: Confirm Import
```
Import confirmed:
- 23 questions imported
- 5 new tags created
- 5 existing tags updated
- 2 invalid questions skipped
```

### Export Process

#### Step 1: Select Data
```
Select data to export:
1. All questions
2. Questions by tags
3. Questions by type
4. Custom selection
```

#### Step 2: Select Format
```
Select export format:
1. JSON (complete data)
2. CSV (spreadsheet format)
3. HTML (web format)
```

#### Step 3: Configure Options
```
Export options:
- Include metadata: Yes
- Include tags: Yes
- Include statistics: Yes
- Compress file: No
```

#### Step 4: Generate Export
```
Generating export:
- Processing questions: 100%
- Processing tags: 100%
- Generating file: 100%
- Export complete
```

#### Step 5: Download/Save
```
Export saved to: exports/quiz_export_2024-01-15.json
File size: 2.5 MB
Questions exported: 500
Tags exported: 50
```

## Settings & Configuration

### Performance Settings

#### Cache Configuration
```
Cache settings:
- Cache size: 1000 entries
- Memory threshold: 80%
- TTL (Time To Live): 3600 seconds
- Cleanup interval: 300 seconds
```

#### Optimization Level
```
Optimization level:
1. Low (minimal optimization)
2. Medium (balanced optimization)
3. High (maximum optimization)
```

#### Memory Management
```
Memory management:
- Garbage collection: Automatic
- Memory monitoring: Enabled
- Leak detection: Enabled
- Optimization: Enabled
```

### UI Settings

#### Theme Selection
```
Available themes:
1. Default (system theme)
2. Light theme
3. Dark theme
4. High contrast
5. Custom theme
```

#### Display Preferences
```
Display settings:
- Show progress bars: Yes
- Show timers: Yes
- Show statistics: Yes
- Show hints: Yes
- Color scheme: Default
```

#### Keyboard Shortcuts
```
Available shortcuts:
- Ctrl+N: New question
- Ctrl+Q: Take quiz
- Ctrl+T: Manage tags
- Ctrl+A: Analytics
- Ctrl+S: Settings
- Ctrl+H: Help
- Ctrl+Q: Quit
```

### Database Settings

#### Connection Settings
```
Database configuration:
- Connection pool size: 10
- Connection timeout: 30 seconds
- Query timeout: 60 seconds
- Transaction timeout: 120 seconds
```

#### Backup Settings
```
Backup configuration:
- Automatic backups: Yes
- Backup frequency: Daily
- Backup retention: 30 days
- Backup location: ./data/backups
```

#### Optimization Settings
```
Database optimization:
- Auto-optimize: Yes
- Optimization frequency: Weekly
- Index optimization: Yes
- Query optimization: Yes
```

### OCR Settings

#### OCR Configuration
```
OCR settings:
- OCR engine: Tesseract
- Language: English
- Confidence threshold: 70%
- Preprocessing: Enabled
- Batch processing: Enabled
```

#### Image Processing
```
Image processing:
- Resize to DPI: 300
- Noise reduction: Yes
- Contrast enhancement: Yes
- Skew correction: Yes
- Text enhancement: Yes
```

### Logging Settings

#### Log Levels
```
Log configuration:
- Error log: ERROR
- Info log: INFO
- Debug log: DEBUG
- Audit log: INFO
- Performance log: INFO
```

#### Log Rotation
```
Log rotation:
- Max file size: 10 MB
- Backup count: 5
- Rotation frequency: Daily
- Compression: Yes
```

## Troubleshooting

### Common Issues

#### Application Won't Start
```
Problem: Application fails to start
Solutions:
1. Check Python version (3.8+ required)
2. Verify virtual environment activation
3. Check dependencies installation
4. Review error logs
```

#### Database Issues
```
Problem: Database connection errors
Solutions:
1. Check database file permissions
2. Verify database file integrity
3. Reset database if corrupted
4. Check disk space
```

#### OCR Not Working
```
Problem: OCR processing fails
Solutions:
1. Install Tesseract OCR
2. Check image format support
3. Verify image quality
4. Check OCR dependencies
```

#### Performance Issues
```
Problem: Slow application performance
Solutions:
1. Check system memory usage
2. Optimize database
3. Clear cache
4. Check system resources
```

### Error Messages

#### E001: Database Connection Error
```
Error: Cannot connect to database
Solution: Check database file and permissions
```

#### E002: File Permission Error
```
Error: Cannot access file
Solution: Check file permissions and location
```

#### E003: Memory Allocation Error
```
Error: Insufficient memory
Solution: Close other applications or increase memory
```

#### E004: OCR Processing Error
```
Error: OCR processing failed
Solution: Check image format and OCR installation
```

#### E005: Cache Operation Error
```
Error: Cache operation failed
Solution: Clear cache and restart application
```

### Log Files

#### Error Log (`data/logs/error.log`)
```
2024-01-15 10:30:00 ERROR: Database connection failed
2024-01-15 10:31:00 ERROR: File permission denied
2024-01-15 10:32:00 ERROR: Memory allocation failed
```

#### Info Log (`data/logs/info.log`)
```
2024-01-15 10:30:00 INFO: Application started
2024-01-15 10:31:00 INFO: Database connected
2024-01-15 10:32:00 INFO: User logged in
```

#### Debug Log (`data/logs/debug.log`)
```
2024-01-15 10:30:00 DEBUG: Initializing components
2024-01-15 10:31:00 DEBUG: Loading configuration
2024-01-15 10:32:00 DEBUG: Starting services
```

#### Audit Log (`data/logs/audit.log`)
```
2024-01-15 10:30:00 AUDIT: User action: Create question
2024-01-15 10:31:00 AUDIT: User action: Take quiz
2024-01-15 10:32:00 AUDIT: User action: View analytics
```

#### Performance Log (`data/logs/performance.log`)
```
2024-01-15 10:30:00 PERFORMANCE: Operation: Create question, Duration: 0.5s
2024-01-15 10:31:00 PERFORMANCE: Operation: Take quiz, Duration: 2.3s
2024-01-15 10:32:00 PERFORMANCE: Operation: View analytics, Duration: 1.1s
```

### Getting Help

#### Documentation
- **README.md**: Quick start guide
- **USER_GUIDE.md**: Detailed user manual
- **API_REFERENCE.md**: API documentation
- **TROUBLESHOOTING.md**: Common issues and solutions

#### Support Channels
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and get help
- **Email Support**: Contact maintainers for urgent issues
- **Community Forum**: User community support

#### Resources
- **Tutorials**: Step-by-step tutorials
- **Examples**: Sample code and configurations
- **FAQ**: Frequently asked questions
- **Video Guides**: Video tutorials and demonstrations

---

**Need more help?** Check the [FAQ](FAQ.md) or [contact support](mailto:support@quizapp.com).
