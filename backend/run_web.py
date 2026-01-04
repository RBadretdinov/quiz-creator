#!/usr/bin/env python3
"""
Run the Quiz Application Web Server

This script starts the FastAPI web server for the Quiz Application.
"""

import sys
import os
from pathlib import Path

# Add src and backend directories to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import uvicorn
    
    # Run the web application
    uvicorn.run(
        "web_app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )

