# Quiz Application

A comprehensive console-based quiz application for creating, managing, and administering quizzes with support for multiple question types, tag-based organization, and OCR-based question input from screenshots.

## Features

- **Multiple Question Types**: Multiple choice, true/false, and select all that apply
- **Tag System**: Organize questions with custom tags and categories
- **Question Randomization**: Automatic shuffling of questions and answer options
- **OCR Import**: Extract questions from screenshots using OCR technology
- **Real-time Feedback**: Immediate correct/incorrect answer validation
- **Progress Tracking**: Visual indicators of quiz completion status
- **Data Persistence**: JSON and SQLite storage options
- **Console Interface**: Intuitive command-line interface

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for screenshot processing)

### Installation

1. **Clone the repository** (when Git is available):
   ```bash
   git clone <repository-url>
   cd quiz
   ```

2. **Set up development environment**:
   ```bash
   python setup_dev.py
   ```

3. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Run the application**:
   ```bash
   python src/main.py
   ```

### Manual Setup

If the setup script doesn't work, you can set up manually:

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python src/main.py
   ```

## Usage

### Basic Workflow

1. **Create Questions**: Use the "Create Question" menu to add new questions
2. **Organize with Tags**: Assign tags to categorize your questions
3. **Take Quizzes**: Select questions by tags or take random quizzes
4. **Review Results**: See detailed feedback and performance statistics

### Question Types

- **Multiple Choice**: Choose one correct answer from several options
- **True/False**: Simple yes/no questions
- **Select All That Apply**: Choose all correct answers from the options

### Tag System

- Create custom tags to organize questions into categories
- Filter quizzes by specific tags
- Use descriptive tag names (e.g., "Math", "Science", "History")
- Each question can have multiple tags

## Development

### Project Structure

```
quiz/
├── src/                    # Source code
│   ├── main.py            # Main application entry point
│   ├── quiz_engine.py     # Core quiz logic
│   ├── question_manager.py # Question CRUD operations
│   ├── tag_manager.py     # Tag management
│   ├── ocr_processor.py   # Screenshot processing
│   ├── ui/                # User interface components
│   ├── models/            # Data models
│   └── config/            # Configuration
├── tests/                 # Test suite
├── data/                  # Data storage
├── logs/                  # Log files
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

### Running Tests

```bash
# Run all tests
python tests/test_models.py
python tests/test_quiz_engine.py

# Run with pytest (if installed)
pytest tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check code quality
flake8 src/ tests/

# Run formatting script
python scripts/format_code.py
```

### Development Tools

- **Black**: Code formatting
- **Flake8**: Code linting
- **Pytest**: Testing framework
- **Coverage**: Test coverage reporting

## Configuration

### Logging

Logs are stored in the `logs/` directory:
- `quiz_app.log`: General application logs
- `quiz_app_errors.log`: Error logs only
- `quiz_app_debug.log`: Debug logs (development mode)

### Data Storage

- **JSON Files**: Initial data storage in `data/` directory
- **SQLite**: Production database (Phase 2)
- **Backup**: Automatic data backup and recovery

## Troubleshooting

### Common Issues

1. **OCR not working**: Ensure Tesseract is installed and in PATH
2. **Questions not saving**: Check data directory permissions
3. **Menu not responding**: Try restarting the application

### Debug Mode

Run with debug logging:
```bash
QUIZ_DEBUG=true python src/main.py
```

### Logs

Check the `logs/` directory for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and code quality checks
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

### Phase 1: Foundation (Current)
- ✅ Core console application
- ✅ Question management
- ✅ Tag system
- ✅ Basic quiz functionality

### Phase 2: Enhanced Features
- 🔄 Advanced question types
- 🔄 SQLite integration
- 🔄 Enhanced UI

### Phase 3: Advanced Input
- 📋 OCR integration
- 📋 File import/export
- 📋 Batch processing

### Phase 4: Polish & Testing
- 📋 Comprehensive testing
- 📋 Performance optimization
- 📋 Documentation

## Support

For questions, issues, or contributions, please refer to the project documentation in the `docs/` directory.

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Python**: 3.8+
