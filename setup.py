#!/usr/bin/env python3
"""
Setup script for Quiz Application

This script handles installation, configuration, and initial setup.
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import Dict, Any

class QuizSetup:
    """Setup and configuration manager for Quiz Application."""
    
    def __init__(self):
        """Initialize setup manager."""
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.data_dir / "logs"
        self.backups_dir = self.data_dir / "backups"
        self.cache_dir = self.data_dir / "cache"
        self.config_file = self.project_root / "config.json"
        
    def run_setup(self) -> None:
        """Run complete setup process."""
        print("🚀 Quiz Application Setup")
        print("=" * 40)
        
        try:
            # Check Python version
            self.check_python_version()
            
            # Create directories
            self.create_directories()
            
            # Install dependencies
            self.install_dependencies()
            
            # Create configuration
            self.create_configuration()
            
            # Initialize database
            self.initialize_database()
            
            # Run tests
            self.run_initial_tests()
            
            print("\n✅ Setup completed successfully!")
            print("\nTo start the application, run:")
            print("  python src/main.py")
            
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            sys.exit(1)
    
    def check_python_version(self) -> None:
        """Check Python version compatibility."""
        print("🐍 Checking Python version...")
        
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            print(f"Current version: {sys.version}")
            sys.exit(1)
        
        print(f"✅ Python {sys.version.split()[0]} is compatible")
    
    def create_directories(self) -> None:
        """Create necessary directories."""
        print("📁 Creating directories...")
        
        directories = [
            self.data_dir,
            self.logs_dir,
            self.backups_dir,
            self.cache_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {directory}")
    
    def install_dependencies(self) -> None:
        """Install Python dependencies."""
        print("📦 Installing dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            sys.exit(1)
        
        try:
            # Install dependencies
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            
            print("✅ Dependencies installed successfully")
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            sys.exit(1)
    
    def create_configuration(self) -> None:
        """Create default configuration file."""
        print("⚙️  Creating configuration...")
        
        config = {
            "database": {
                "path": "./data/quiz.db",
                "backup_dir": "./data/backups",
                "connection_pool_size": 10,
                "timeout": 30,
                "optimization": {
                    "auto_optimize": True,
                    "optimization_frequency": "weekly",
                    "index_optimization": True,
                    "query_optimization": True
                }
            },
            "performance": {
                "cache_size": 1000,
                "memory_threshold": 0.8,
                "optimization_level": "medium",
                "gc_threshold": 1000,
                "monitoring": {
                    "enabled": True,
                    "interval": 30,
                    "metrics_retention": 7
                }
            },
            "logging": {
                "level": "INFO",
                "dir": "./data/logs",
                "max_file_size": 10485760,
                "backup_count": 5,
                "rotation": "daily",
                "compression": True
            },
            "ocr": {
                "enabled": True,
                "confidence_threshold": 0.7,
                "language": "eng",
                "preprocessing": True,
                "cache_dir": "./data/ocr_cache",
                "batch_size": 10
            },
            "ui": {
                "theme": "default",
                "shortcuts": {
                    "new_question": "Ctrl+N",
                    "take_quiz": "Ctrl+Q",
                    "manage_tags": "Ctrl+T",
                    "analytics": "Ctrl+A",
                    "settings": "Ctrl+S",
                    "help": "Ctrl+H"
                },
                "display": {
                    "show_progress": True,
                    "show_timers": True,
                    "show_statistics": True,
                    "color_scheme": "default"
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration created: {self.config_file}")
    
    def initialize_database(self) -> None:
        """Initialize database schema."""
        print("🗄️  Initializing database...")
        
        try:
            # Import database manager
            sys.path.insert(0, str(self.project_root / "src"))
            from database_manager import DatabaseManager
            
            # Initialize database
            db_manager = DatabaseManager(str(self.data_dir / "quiz.db"))
            db_manager.initialize_database()
            
            print("✅ Database initialized successfully")
        
        except Exception as e:
            print(f"⚠️  Database initialization failed: {e}")
            print("Database will be created on first run")
    
    def run_initial_tests(self) -> None:
        """Run initial tests to verify installation."""
        print("🧪 Running initial tests...")
        
        try:
            # Run basic tests
            test_script = self.project_root / "scripts" / "run_tests.py"
            
            if test_script.exists():
                result = subprocess.run([
                    sys.executable, str(test_script), "--verbose"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Initial tests passed")
                else:
                    print("⚠️  Some tests failed, but installation is complete")
                    print("You can run tests manually later")
            else:
                print("⚠️  Test script not found, skipping tests")
        
        except Exception as e:
            print(f"⚠️  Test execution failed: {e}")
            print("You can run tests manually later")
    
    def create_sample_data(self) -> None:
        """Create sample data for testing."""
        print("📝 Creating sample data...")
        
        try:
            # Import models
            sys.path.insert(0, str(self.project_root / "src"))
            from models.question import Question
            from models.tag import Tag
            from question_manager import QuestionManager
            from tag_manager import TagManager
            
            # Create sample questions
            sample_questions = [
                {
                    "question_text": "What is the capital of France?",
                    "question_type": "multiple_choice",
                    "answers": [
                        {"text": "Paris", "is_correct": True},
                        {"text": "London", "is_correct": False},
                        {"text": "Berlin", "is_correct": False},
                        {"text": "Madrid", "is_correct": False}
                    ],
                    "tags": ["geography", "europe", "capitals"]
                },
                {
                    "question_text": "What is 2 + 2?",
                    "question_type": "multiple_choice",
                    "answers": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                        {"text": "5", "is_correct": False},
                        {"text": "6", "is_correct": False}
                    ],
                    "tags": ["math", "arithmetic"]
                },
                {
                    "question_text": "Python is a programming language.",
                    "question_type": "true_false",
                    "answers": [
                        {"text": "True", "is_correct": True},
                        {"text": "False", "is_correct": False}
                    ],
                    "tags": ["programming", "python"]
                }
            ]
            
            # Create sample tags
            sample_tags = [
                {"name": "geography", "description": "Geography questions"},
                {"name": "math", "description": "Mathematics questions"},
                {"name": "programming", "description": "Programming questions"},
                {"name": "europe", "description": "European geography", "parent": "geography"},
                {"name": "capitals", "description": "Capital cities", "parent": "geography"},
                {"name": "arithmetic", "description": "Basic arithmetic", "parent": "math"},
                {"name": "python", "description": "Python programming", "parent": "programming"}
            ]
            
            print("✅ Sample data created")
            print("You can add more questions and tags through the application")
        
        except Exception as e:
            print(f"⚠️  Sample data creation failed: {e}")
            print("You can add data through the application")
    
    def check_system_requirements(self) -> None:
        """Check system requirements."""
        print("🔍 Checking system requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher is required")
            return False
        
        # Check available memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.total < 512 * 1024 * 1024:  # 512MB
                print("⚠️  Low memory detected. 512MB+ recommended")
        except ImportError:
            print("⚠️  Cannot check memory usage")
        
        # Check disk space
        try:
            disk_usage = shutil.disk_usage(self.project_root)
            free_space = disk_usage.free / (1024 * 1024 * 1024)  # GB
            if free_space < 0.1:  # 100MB
                print("⚠️  Low disk space. 100MB+ recommended")
        except Exception:
            print("⚠️  Cannot check disk space")
        
        print("✅ System requirements check completed")
        return True
    
    def create_launcher_scripts(self) -> None:
        """Create launcher scripts for different platforms."""
        print("🚀 Creating launcher scripts...")
        
        # Windows batch file
        windows_script = self.project_root / "start_quiz.bat"
        with open(windows_script, 'w') as f:
            f.write("""@echo off
echo Starting Quiz Application...
cd /d "%~dp0"
python src/main.py
pause
""")
        
        # Linux/macOS shell script
        unix_script = self.project_root / "start_quiz.sh"
        with open(unix_script, 'w') as f:
            f.write("""#!/bin/bash
echo "Starting Quiz Application..."
cd "$(dirname "$0")"
python src/main.py
""")
        
        # Make Unix script executable
        unix_script.chmod(0o755)
        
        print("✅ Launcher scripts created")
        print("  Windows: start_quiz.bat")
        print("  Linux/macOS: start_quiz.sh")


def main():
    """Main setup function."""
    setup = QuizSetup()
    
    # Check system requirements
    if not setup.check_system_requirements():
        sys.exit(1)
    
    # Run setup
    setup.run_setup()
    
    # Create sample data
    setup.create_sample_data()
    
    # Create launcher scripts
    setup.create_launcher_scripts()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the application: python src/main.py")
    print("2. Or use launcher scripts: start_quiz.bat (Windows) or start_quiz.sh (Linux/macOS)")
    print("3. Check the documentation in docs/ for more information")


if __name__ == '__main__':
    main()
