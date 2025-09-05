#!/usr/bin/env python3
"""
Quiz Application - Main Entry Point

This is the main entry point for the Quiz Application, a console-based tool
for creating, managing, and administering quizzes with support for multiple
question types, tag-based organization, and OCR-based question input.
"""

import sys
import os
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Set up comprehensive logging configuration."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "quiz_app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """Main application entry point."""
    logger = setup_logging()
    logger.info("Starting Quiz Application")
    
    try:
        # TODO: Import and initialize main application components
        print("Welcome to the Quiz Application!")
        print("This is a placeholder for the main application logic.")
        print("Phase 1.1 setup completed successfully.")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    
    logger.info("Quiz Application shutdown")

if __name__ == "__main__":
    main()
