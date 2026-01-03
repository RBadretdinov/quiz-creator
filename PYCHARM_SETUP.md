# PyCharm Setup Guide for Quiz Application

## ✅ Application Status
The Quiz Application has been tested and is **fully compatible** with PyCharm. All core functionality works correctly.

## 🚀 Quick Start in PyCharm

### 1. Open Project in PyCharm
1. Open PyCharm
2. Select "Open" and navigate to the project root directory (`C:\dev\quiz`)
3. Click "OK" to open the project

### 2. Configure Python Interpreter
1. Go to `File` → `Settings` → `Project` → `Python Interpreter`
2. Ensure Python 3.8+ is selected
3. Install required dependencies (see Dependencies section below)

### 3. Set Working Directory
1. Go to `Run` → `Edit Configurations`
2. Create a new configuration:
   - **Name**: Quiz Application
   - **Script path**: `src/main.py`
   - **Working directory**: `C:\dev\quiz` (project root)
   - **Python interpreter**: Your Python 3.8+ interpreter

### 4. Run the Application
1. Click the green "Run" button or press `Shift + F10`
2. The application will start and display the main menu

## 📦 Dependencies

### Required Dependencies
The following packages are required and should be installed via PyCharm's package manager:

```bash
# Core dependencies
pytesseract==0.3.10
Pillow==9.5.0

# Development tools
black==23.3.0
flake8==6.0.0
pytest==7.3.1
pytest-cov==4.1.0

# Additional dependencies
colorama==0.4.6
click==8.1.7
rich==13.7.0
psutil==5.9.5
```

### Installing Dependencies
1. Open PyCharm Terminal (`View` → `Tool Windows` → `Terminal`)
2. Run: `pip install -r requirements.txt`

## 🎯 Application Features

### Core Features (All Working)
- ✅ **Quiz Creation**: Create multiple choice, true/false, and select-all questions
- ✅ **Quiz Taking**: Take quizzes with randomization and scoring
- ✅ **Tag Management**: Hierarchical tag system for organizing questions
- ✅ **Database Integration**: SQLite database for persistent storage
- ✅ **Analytics Dashboard**: Basic analytics and statistics
- ✅ **Import/Export**: JSON and CSV import/export functionality
- ✅ **Question Management**: Browse, edit, and manage questions
- ✅ **OCR Support**: Basic OCR for importing questions from images

### Simplified Features (Removed Complexity)
- ❌ Advanced analytics with machine learning insights
- ❌ Complex OCR preprocessing with OpenCV
- ❌ PDF/XML/HTML export formats
- ❌ Advanced console UI with themes and accessibility

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: Module not found errors
**Solution**: Ensure working directory is set to project root (`C:\dev\quiz`)

#### 2. Database Errors
**Problem**: Database connection issues
**Solution**: The application will automatically create the database and migrate from JSON files

#### 3. OCR Warnings
**Problem**: OCR dependencies not available
**Solution**: OCR is optional. Install `pytesseract` and `Pillow` for OCR functionality

#### 4. Unicode Errors
**Problem**: Character encoding issues
**Solution**: The application uses ASCII-compatible characters for cross-platform compatibility

### Debug Configuration
For debugging, use this PyCharm configuration:
- **Script path**: `src/main.py`
- **Working directory**: `C:\dev\quiz`
- **Environment variables**: None required
- **Python options**: None required

## 📁 Project Structure
```
quiz/
├── src/                    # Source code
│   ├── main.py            # Main entry point
│   ├── app_controller_db.py  # Database-integrated controller
│   ├── ui/                # User interface modules
│   ├── database/          # Database modules
│   ├── analytics/         # Analytics modules
│   ├── models/            # Data models
│   └── ...
├── data/                  # Data storage
├── tests/                 # Test files
├── requirements.txt       # Dependencies
└── README.md             # Project documentation
```

## 🎮 Usage

### Running the Application
1. **Start**: Run `src/main.py` in PyCharm
2. **Main Menu**: Choose from 10 options including quiz creation, taking quizzes, and management
3. **Navigation**: Use number keys to navigate menus
4. **Exit**: Press 0 to exit the application

### Key Features
- **Create Questions**: Add multiple choice, true/false, and select-all questions
- **Take Quizzes**: Practice with randomized questions
- **Manage Tags**: Organize questions with hierarchical tags
- **View Analytics**: See basic statistics and performance metrics
- **Import/Export**: Share questions via JSON/CSV files

## ✅ Verification

The application has been tested and verified to work correctly in PyCharm with:
- ✅ All imports working correctly
- ✅ Database integration functional
- ✅ UI components operational
- ✅ Core quiz functionality working
- ✅ Analytics dashboard functional
- ✅ Cross-platform compatibility

## 🚀 Ready to Use!

The Quiz Application is fully ready for use in PyCharm. Simply follow the setup steps above and start creating and taking quizzes!
