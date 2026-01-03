# Quiz Application

A comprehensive, console-based quiz application built with Python that supports multiple question types, advanced analytics, OCR processing, and intelligent performance optimization.

## 🚀 Features

### Core Functionality
- **Multiple Question Types**: Multiple choice, true/false, select all, and fill-in-the-blank questions
- **Advanced Quiz Engine**: Intelligent randomization, partial credit scoring, and session management
- **Comprehensive Analytics**: Performance tracking, learning analytics, and detailed reporting
- **Tag Management**: Hierarchical tag system with advanced search and filtering
- **Database Integration**: SQLite database with optimized queries and indexing

### Advanced Features
- **OCR Processing**: Import questions from screenshots using advanced OCR technology
- **File Import/Export**: Support for JSON, CSV, and HTML formats
- **Performance Optimization**: Intelligent caching, memory management, and database optimization
- **Enhanced Console UI**: Breadcrumb navigation, keyboard shortcuts, and user preferences
- **Error Handling**: Comprehensive error handling with user-friendly feedback

### Analytics & Reporting
- **Performance Analytics**: Track quiz performance, accuracy, and response times
- **Learning Analytics**: Monitor progress, identify knowledge gaps, and track mastery
- **Question Analytics**: Analyze question effectiveness and difficulty
- **Tag Analytics**: Track tag usage and performance correlation
- **System Analytics**: Monitor system health and usage statistics

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 100MB for application and data

### Python Dependencies
- **Core**: `pytesseract`, `Pillow`, `psutil`
- **Development**: `black`, `flake8`, `pytest`, `pytest-cov`
- **UI Enhancement**: `colorama`, `click`, `rich`

## 🛠️ Installation

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd quiz
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
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

### Detailed Installation

#### Windows
```bash
# Install Python 3.8+ from python.org
# Open Command Prompt or PowerShell

# Clone repository
git clone <repository-url>
cd quiz

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

#### macOS
```bash
# Install Python 3.8+ using Homebrew
brew install python

# Clone repository
git clone <repository-url>
cd quiz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

#### Linux (Ubuntu/Debian)
```bash
# Install Python 3.8+
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Clone repository
git clone <repository-url>
cd quiz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

## 🎯 Quick Start Guide

### First Run
1. **Start the application**: `python src/main.py`
2. **Create your first question**: Choose option 1 from the main menu
3. **Add tags**: Use the tag management system to organize questions
4. **Take a quiz**: Choose option 2 to start a quiz session
5. **View analytics**: Check your performance in the analytics dashboard

### Basic Usage

#### Creating Questions
```
Main Menu > 1. Create Question
- Enter question text
- Select question type
- Add answer options
- Assign tags
- Save question
```

#### Taking Quizzes
```
Main Menu > 2. Take Quiz
- Select quiz parameters
- Answer questions
- View results
- Export session data
```

#### Managing Tags
```
Main Menu > 3. Manage Tags
- Create hierarchical tags
- Search and filter tags
- Bulk operations
- Import/export tags
```

## 📚 User Guide

### Main Menu Options

1. **Create Question** - Add new questions to your question bank
2. **Take Quiz** - Start a quiz session with customizable parameters
3. **Manage Tags** - Organize questions with hierarchical tags
4. **Enhanced Question Management** - Browse, edit, and manage questions
5. **Question Types** - View and manage different question types
6. **Database Management** - Manage database operations and backups
7. **Analytics Dashboard** - View performance and learning analytics
8. **Import from Screenshot** - Use OCR to import questions from images
9. **Settings** - Configure application preferences
10. **Help** - Access help and documentation

### Question Types

#### Multiple Choice
- Single correct answer
- Multiple answer options
- Partial credit for select-all questions

#### True/False
- Binary choice questions
- Simple scoring system

#### Select All
- Multiple correct answers
- Partial credit scoring
- Comprehensive feedback

#### Fill in the Blank
- Text-based answers
- Flexible matching
- Case-insensitive options

### Tag Management

#### Creating Tags
- **Simple Tags**: Basic categorization
- **Hierarchical Tags**: Parent-child relationships
- **Tag Aliases**: Alternative names for tags
- **Usage Tracking**: Monitor tag usage and performance

#### Tag Operations
- **Search**: Find tags by name, description, or aliases
- **Filter**: Advanced filtering with logical operators
- **Bulk Operations**: Mass operations on multiple tags
- **Import/Export**: Transfer tag data between systems

### Analytics Dashboard

#### Performance Analytics
- **Session Statistics**: Total sessions, questions, and scores
- **Accuracy Metrics**: Success rates and performance trends
- **Time Analysis**: Response times and session duration
- **Performance Distribution**: Score distribution analysis

#### Learning Analytics
- **Progress Tracking**: Monitor learning progress over time
- **Knowledge Gaps**: Identify areas needing improvement
- **Mastery Assessment**: Track question mastery levels
- **Retention Analysis**: Monitor knowledge retention

#### Question Analytics
- **Effectiveness Analysis**: Question performance metrics
- **Usage Patterns**: Question usage and popularity
- **Difficulty Assessment**: Question difficulty analysis
- **Quality Metrics**: Question quality and clarity

### OCR Processing

#### Supported Formats
- **Image Types**: PNG, JPEG, TIFF, BMP
- **Text Extraction**: Advanced OCR with multiple configurations
- **Question Parsing**: Intelligent parsing of extracted text
- **Quality Assessment**: Image quality analysis and recommendations

#### OCR Workflow
1. **Select Image**: Choose image file for processing
2. **Preprocessing**: Automatic image enhancement and optimization
3. **Text Extraction**: OCR processing with confidence scoring
4. **Question Parsing**: Intelligent parsing into question format
5. **Review & Edit**: Review extracted questions and make corrections
6. **Save Questions**: Add parsed questions to question bank

### File Import/Export

#### Supported Formats
- **JSON**: Complete data export with metadata
- **CSV**: Spreadsheet-compatible format
- **HTML**: Web-friendly format for sharing

#### Import Process
1. **Select Format**: Choose import format
2. **Select File**: Choose file to import
3. **Validate Data**: Automatic data validation
4. **Review Import**: Review imported data
5. **Confirm Import**: Complete import process

#### Export Process
1. **Select Data**: Choose data to export
2. **Select Format**: Choose export format
3. **Configure Options**: Set export parameters
4. **Generate Export**: Create export file
5. **Download/Save**: Save export file

## 🔧 Configuration

### Application Settings

#### Performance Settings
- **Cache Size**: Configure cache size for optimal performance
- **Memory Threshold**: Set memory usage limits
- **Optimization Level**: Choose performance optimization level

#### UI Settings
- **Theme**: Select application theme
- **Shortcuts**: Configure keyboard shortcuts
- **Display**: Set display preferences
- **Accessibility**: Configure accessibility options

#### Database Settings
- **Connection Pool**: Configure database connection settings
- **Backup Frequency**: Set automatic backup schedule
- **Optimization**: Configure database optimization settings

### Environment Variables

```bash
# Database configuration
QUIZ_DB_PATH=./data/quiz.db
QUIZ_BACKUP_DIR=./data/backups

# Performance settings
QUIZ_CACHE_SIZE=1000
QUIZ_MEMORY_THRESHOLD=0.8

# Logging configuration
QUIZ_LOG_LEVEL=INFO
QUIZ_LOG_DIR=./data/logs
```

## 🧪 Testing

### Running Tests

#### All Tests
```bash
python -m pytest tests/ -v
```

#### Specific Test Suites
```bash
# Core functionality tests
python tests/test_models.py
python tests/test_quiz_engine.py

# Phase-specific tests
python tests/test_performance_optimization_phase_5_3.py
python tests/test_error_handling_validation_phase_5_2.py
```

#### Test Coverage
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Performance and load testing
- **Error Handling Tests**: Error scenario testing
- **Accessibility Tests**: UI accessibility testing

## 📊 Performance

### Optimization Features

#### Caching System
- **Intelligent Caching**: Multi-level caching with automatic expiration
- **Cache Statistics**: Performance metrics and optimization
- **Memory Management**: Efficient memory usage and garbage collection

#### Database Optimization
- **Query Optimization**: Optimized SQL queries and indexing
- **Connection Pooling**: Efficient database connection management
- **Performance Monitoring**: Real-time performance tracking

#### File I/O Optimization
- **Batch Processing**: Efficient file operations
- **Compression**: Data compression for storage optimization
- **Caching**: File operation caching for improved performance

### Performance Metrics

- **Response Time**: < 100ms for most operations
- **Memory Usage**: < 100MB for typical usage
- **Database Performance**: Optimized queries with indexing
- **Cache Hit Rate**: > 80% for frequently accessed data

## 🐛 Troubleshooting

### Common Issues

#### Installation Issues
```bash
# Python version check
python --version

# Virtual environment issues
python -m venv --clear venv

# Dependency issues
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### Runtime Issues
```bash
# Database issues
rm data/quiz.db  # Reset database
python src/main.py  # Restart application

# Memory issues
# Check system memory usage
# Restart application
```

#### OCR Issues
```bash
# Tesseract installation
# Windows: Download from GitHub releases
# macOS: brew install tesseract
# Linux: sudo apt install tesseract-ocr

# Image format issues
# Ensure images are in supported formats (PNG, JPEG, TIFF, BMP)
```

### Error Codes

- **E001**: Database connection error
- **E002**: File permission error
- **E003**: Memory allocation error
- **E004**: OCR processing error
- **E005**: Cache operation error

### Log Files

- **Error Log**: `data/logs/error.log`
- **Info Log**: `data/logs/info.log`
- **Debug Log**: `data/logs/debug.log`
- **Audit Log**: `data/logs/audit.log`
- **Performance Log**: `data/logs/performance.log`

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature-name`
3. **Install development dependencies**: `pip install -r requirements.txt`
4. **Run tests**: `python -m pytest tests/`
5. **Make changes**: Follow coding standards
6. **Test changes**: Ensure all tests pass
7. **Submit pull request**: Include description and tests

### Coding Standards

- **Python Style**: Follow PEP 8 guidelines
- **Documentation**: Add docstrings to all functions
- **Testing**: Write tests for new features
- **Type Hints**: Use type hints for function parameters
- **Error Handling**: Implement proper error handling

### Pull Request Process

1. **Fork repository**
2. **Create feature branch**
3. **Make changes**
4. **Add tests**
5. **Update documentation**
6. **Submit pull request**
7. **Address feedback**
8. **Merge when approved**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Python Community**: For excellent documentation and libraries
- **Tesseract OCR**: For powerful OCR capabilities
- **SQLite**: For reliable database functionality
- **Contributors**: For valuable feedback and contributions

## 📞 Support

### Getting Help

- **Documentation**: Check this README and user guide
- **Issues**: Report issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for urgent issues

### Resources

- **User Guide**: Comprehensive usage documentation
- **API Reference**: Detailed API documentation
- **Examples**: Sample code and configurations
- **Tutorials**: Step-by-step tutorials
- **FAQ**: Frequently asked questions

---

**Happy Quizzing!** 🎯
