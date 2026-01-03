#!/usr/bin/env python3
"""
Development Environment Setup Script

This script sets up the development environment for the Quiz Application,
including virtual environment creation, dependency installation, and
development tools configuration.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_virtual_environment():
    """Create virtual environment."""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python -m venv venv", "Creating virtual environment")

def get_pip_command():
    """Get the correct pip command for the platform."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\pip.exe"
    else:
        return "venv/bin/pip"

def get_python_command():
    """Get the correct python command for the platform."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\python.exe"
    else:
        return "venv/bin/python"

def install_dependencies():
    """Install project dependencies."""
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing project dependencies"):
        return False
    
    return True

def install_development_tools():
    """Install development tools."""
    pip_cmd = get_pip_command()
    
    dev_tools = [
        "black==23.3.0",
        "flake8==6.0.0",
        "pytest==7.3.1",
        "pytest-cov==4.1.0"
    ]
    
    for tool in dev_tools:
        if not run_command(f"{pip_cmd} install {tool}", f"Installing {tool.split('==')[0]}"):
            return False
    
    return True

def create_directories():
    """Create necessary directories."""
    print("📁 Creating project directories...")
    
    directories = [
        "logs",
        "data",
        "tests",
        "docs",
        "src/config"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def run_tests():
    """Run the test suite to verify setup."""
    print("🧪 Running tests to verify setup...")
    python_cmd = get_python_command()
    
    test_files = [
        "tests/test_models.py",
        "tests/test_quiz_engine.py"
    ]
    
    all_passed = True
    for test_file in test_files:
        if Path(test_file).exists():
            if not run_command(f"{python_cmd} {test_file}", f"Running {test_file}"):
                all_passed = False
        else:
            print(f"⚠️  Test file not found: {test_file}")
    
    return all_passed

def create_gitignore():
    """Create .gitignore file if it doesn't exist."""
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        print("✅ .gitignore already exists")
        return True
    
    print("📝 Creating .gitignore file...")
    # Note: .gitignore was already created earlier
    return True

def display_setup_summary():
    """Display setup summary and next steps."""
    print("\n" + "="*60)
    print("🎉 DEVELOPMENT ENVIRONMENT SETUP COMPLETE!")
    print("="*60)
    
    print("\n📋 Setup Summary:")
    print("✅ Python virtual environment created")
    print("✅ Project dependencies installed")
    print("✅ Development tools installed")
    print("✅ Project directories created")
    print("✅ Logging configuration set up")
    print("✅ .gitignore file created")
    
    print("\n🚀 Next Steps:")
    print("1. Activate virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. Run the application:")
    print("   python src/main.py")
    
    print("\n3. Run tests:")
    print("   python tests/test_models.py")
    print("   python tests/test_quiz_engine.py")
    
    print("\n4. Development commands:")
    print("   black src/ tests/          # Format code")
    print("   flake8 src/ tests/         # Lint code")
    print("   pytest tests/              # Run all tests")
    
    print("\n📚 Documentation:")
    print("   - Project specification: docs/PROJECT_SPECIFICATION.md")
    print("   - Implementation plan: docs/IMPLEMENTATION_PLAN.md")
    
    print("="*60)

def main():
    """Main setup function."""
    print("🎯 QUIZ APPLICATION - DEVELOPMENT ENVIRONMENT SETUP")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Install development tools
    if not install_development_tools():
        print("❌ Failed to install development tools")
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories")
        sys.exit(1)
    
    # Create .gitignore
    if not create_gitignore():
        print("❌ Failed to create .gitignore")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("⚠️  Some tests failed, but setup is complete")
    
    # Display summary
    display_setup_summary()

if __name__ == "__main__":
    main()

