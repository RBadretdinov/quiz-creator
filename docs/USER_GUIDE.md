# User Guide

This guide provides step-by-step instructions for using the Quiz Application.

## Table of Contents

- [Getting Started](#getting-started)
- [Creating Questions](#creating-questions)
- [Managing Tags](#managing-tags)
- [Taking Quizzes](#taking-quizzes)
- [OCR Import](#ocr-import)
- [Data Management](#data-management)
- [Troubleshooting](#troubleshooting)

## Getting Started

### First Launch

1. **Run the application**:
   ```bash
   python src/main.py
   ```

2. **You'll see the main menu**:
   ```
   ============================================================
              QUIZ APPLICATION - MAIN MENU
   ============================================================

   1. Create Question
   2. Take Quiz
   3. Manage Tags
   4. View Question Bank
   5. Import from Screenshot
   6. Settings
   7. Help
   8. Exit
   ```

3. **Navigate using numbers**: Enter the number corresponding to your choice.

## Creating Questions

### Step 1: Access Question Creation

1. From the main menu, select **1. Create Question**
2. Choose your question type:
   - **1. Multiple Choice Question** - One correct answer
   - **2. True/False Question** - Simple yes/no
   - **3. Select All That Apply Question** - Multiple correct answers

### Step 2: Enter Question Text

- Enter your question text (10-500 characters)
- Be clear and concise
- End with a question mark for clarity

**Example:**
```
📝 Enter the question text (10-500 characters): What is the capital of France?
```

### Step 3: Add Answer Options

#### For Multiple Choice Questions:
1. Enter 2-6 answer options
2. Press Enter on an empty line when done
3. Select which answer is correct

**Example:**
```
📝 Enter answer options (2-6 options):
(Enter empty line when done)
Answer 1: Paris
Answer 2: London
Answer 3: Berlin
Answer 4: [Press Enter to finish]

✅ Mark the correct answer:
1. Paris
2. London
3. Berlin
Enter the number of the correct answer: 1
```

#### For True/False Questions:
- The system automatically creates "True" and "False" options
- Simply select which is correct

#### For Select All That Apply:
1. Enter multiple answer options
2. Select all correct answers (comma-separated)

**Example:**
```
✅ Mark all correct answers (enter numbers separated by commas):
1. Paris
2. London
3. Berlin
4. Madrid
Enter numbers of correct answers (e.g., 1,3,4): 1,3
```

### Step 4: Assign Tags

1. **If you have existing tags**, select from the list:
   ```
   🏷️  Select tags for this question:
   (Enter numbers separated by commas, or 'new' to create a new tag)
   1. geography
   2. history
   3. science
   Enter tag numbers (e.g., 1,3,5) or 'new': 1
   ```

2. **To create a new tag**:
   ```
   Enter 'new' to create a new tag: new
   Enter new tag name (1-20 characters, alphanumeric and hyphens only): geography
   ```

### Step 5: Save Question

- The system validates your question
- If valid, the question is saved automatically
- You'll see a success message

## Managing Tags

### Viewing Tags

1. From main menu, select **3. Manage Tags**
2. Choose **1. View All Tags**
3. See all tags with question counts

### Creating Tags

1. From tag management menu, select **2. Create New Tag**
2. Enter tag name (1-20 characters, alphanumeric and hyphens only)
3. Optionally add description and color

**Example:**
```
Enter tag name: mathematics
Enter description (optional): Math and algebra questions
Enter color (optional): #FF0000
```

### Editing Tags

1. From tag management menu, select **3. Edit Tag**
2. Select the tag to edit
3. Update name, description, or color

### Deleting Tags

1. From tag management menu, select **4. Delete Tag**
2. Select the tag to delete
3. **Warning**: You'll be prompted to reassign questions if the tag is in use

### Tag Statistics

1. From tag management menu, select **5. Tag Statistics**
2. View usage statistics:
   - Total tags
   - Most used tags
   - Unused tags
   - Average usage

## Taking Quizzes

### Step 1: Start a Quiz

1. From main menu, select **2. Take Quiz**
2. Choose quiz type:
   - **1. Quick Quiz** - Random questions from all tags
   - **2. Quiz by Tags** - Questions from specific tags
   - **3. Custom Quiz** - Advanced options

### Step 2: Configure Quiz Settings

#### For Quick Quiz:
- Enter number of questions (1-50)
- Optionally set time limit

#### For Quiz by Tags:
1. Select tags to include
2. Enter number of questions
3. Set time limit (optional)

#### For Custom Quiz:
- Advanced filtering options
- Difficulty levels
- Question type preferences

### Step 3: Answer Questions

1. **Read the question carefully**
2. **Select your answer**:
   - For multiple choice: Enter number (1, 2, 3, etc.)
   - For true/false: Enter 1 (True) or 2 (False)
   - For select all: Enter numbers separated by commas (1,3,4)

3. **Get immediate feedback**:
   - ✅ Correct answers show "Correct! Well done!"
   - ❌ Incorrect answers show the correct answer

4. **Track progress**: See progress bar and question counter

### Step 4: View Results

After completing the quiz:
- **Final Score**: Percentage and correct/total count
- **Time Taken**: Duration of the quiz
- **Performance Message**: Encouragement based on score
- **Question Review**: Detailed breakdown of each answer

## OCR Import

### Preparing Images

1. **Take clear screenshots** of questions
2. **Ensure good quality**:
   - High contrast text
   - Good lighting
   - Clear, readable text
   - Minimal background noise

### Supported Formats

- PNG (recommended)
- JPEG
- TIFF
- BMP

### Import Process

1. From main menu, select **5. Import from Screenshot**
2. Enter the path to your image file
3. The system processes the image using OCR
4. **Review extracted text**:
   - Check accuracy
   - Edit if necessary
5. **Parse questions**:
   - System attempts to identify questions and answers
   - Manual correction may be needed
6. **Save questions**:
   - Assign tags
   - Validate and save

### Tips for Better OCR Results

- Use high-resolution images (300+ DPI)
- Ensure text is horizontal (not rotated)
- Avoid shadows and reflections
- Use clear, standard fonts
- Maintain good contrast

## Data Management

### Viewing Question Bank

1. From main menu, select **4. View Question Bank**
2. Choose viewing option:
   - **1. View All Questions** - Browse all questions
   - **2. Search Questions** - Find specific questions
   - **3. Filter by Tags** - View questions by tag

### Searching Questions

1. From question bank menu, select **2. Search Questions**
2. Enter search term
3. View matching questions

**Search Tips:**
- Search by question text
- Search by answer text
- Use keywords from your questions

### Editing Questions

1. From question bank menu, select **4. Edit Question**
2. Find and select the question to edit
3. Modify question text, answers, or tags
4. Save changes

### Deleting Questions

1. From question bank menu, select **5. Delete Question**
2. Find and select the question to delete
3. Confirm deletion

### Exporting Data

1. From question bank menu, select **6. Export Questions**
2. Choose export format:
   - JSON (for backup/transfer)
   - CSV (for spreadsheets)
   - PDF (for printing)

## Settings

### Display Preferences

1. From main menu, select **6. Settings**
2. Choose **1. Display Preferences**
3. Configure:
   - Color scheme
   - Progress bar style
   - Menu formatting

### Quiz Preferences

1. From settings menu, select **2. Quiz Preferences**
2. Set defaults:
   - Number of questions
   - Time limits
   - Question types

### Data Management

1. From settings menu, select **3. Data Management**
2. Options:
   - Backup data
   - Restore from backup
   - Clean up old data
   - Reset to defaults

## Troubleshooting

### Common Issues

#### "OCR not working"
- **Check**: Tesseract is installed
- **Solution**: Install Tesseract OCR and add to PATH

#### "Questions not saving"
- **Check**: Data directory permissions
- **Solution**: Ensure write access to data folder

#### "Menu not responding"
- **Check**: Terminal compatibility
- **Solution**: Try different terminal or restart application

#### "Invalid question data"
- **Check**: Question text length (10-500 characters)
- **Check**: Answer count (2-6 options)
- **Check**: At least one correct answer marked

### Getting Help

1. From main menu, select **7. Help**
2. Browse help topics:
   - Getting Started
   - Question Types
   - Tag System
   - OCR Import
   - Keyboard Shortcuts
   - Troubleshooting

### Debug Mode

Run with debug logging:
```bash
QUIZ_DEBUG=true python src/main.py
```

Check logs in the `logs/` directory for detailed error information.

### Keyboard Shortcuts

- **Ctrl+C**: Exit application
- **Enter**: Confirm selection
- **Numbers**: Select menu options
- **'q' or 'quit'**: Return to previous menu

## Best Practices

### Question Creation

1. **Write clear questions**: Avoid ambiguous language
2. **Use consistent formatting**: Follow the same style
3. **Test your questions**: Take quizzes to verify
4. **Use descriptive tags**: Make organization easy

### Tag Management

1. **Use consistent naming**: Follow a naming convention
2. **Keep tags simple**: Avoid overly complex hierarchies
3. **Regular cleanup**: Remove unused tags
4. **Descriptive names**: Make tags self-explanatory

### Quiz Taking

1. **Read carefully**: Don't rush through questions
2. **Use process of elimination**: For multiple choice
3. **Review answers**: Check your work before submitting
4. **Learn from mistakes**: Review incorrect answers

### Data Management

1. **Regular backups**: Export your question bank
2. **Organize questions**: Use tags effectively
3. **Clean up**: Remove outdated or incorrect questions
4. **Test regularly**: Verify your questions work correctly

---

For technical support or advanced usage, refer to the API Reference documentation.
