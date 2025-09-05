#!/usr/bin/env python3
"""
Code Formatting Script

This script formats the codebase using black and checks code quality with flake8.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def format_with_black():
    """Format code using black."""
    return run_command("black src/ tests/", "Formatting code with black")

def check_with_flake8():
    """Check code quality with flake8."""
    return run_command("flake8 src/ tests/", "Checking code quality with flake8")

def main():
    """Main formatting function."""
    print("🎨 CODE FORMATTING AND QUALITY CHECK")
    print("="*50)
    
    # Check if we're in the right directory
    if not Path("src").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Format with black
    if not format_with_black():
        print("❌ Code formatting failed")
        sys.exit(1)
    
    # Check with flake8
    if not check_with_flake8():
        print("⚠️  Code quality issues found (see output above)")
        print("   Fix the issues and run the script again")
        sys.exit(1)
    
    print("\n🎉 Code formatting and quality check completed successfully!")

if __name__ == "__main__":
    main()
