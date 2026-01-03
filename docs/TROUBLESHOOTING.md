# Quiz Application - Troubleshooting Guide

## Table of Contents
1. [Common Issues](#common-issues)
2. [Installation Problems](#installation-problems)
3. [Runtime Errors](#runtime-errors)
4. [Performance Issues](#performance-issues)
5. [Database Problems](#database-problems)
6. [OCR Issues](#ocr-issues)
7. [File I/O Problems](#file-io-problems)
8. [Memory Issues](#memory-issues)
9. [Network Issues](#network-issues)
10. [Platform-Specific Issues](#platform-specific-issues)

## Common Issues

### Application Won't Start

#### Problem: Application fails to start with error message
```
Error: ModuleNotFoundError: No module named 'pytesseract'
```

**Solutions:**
1. **Install missing dependencies:**
   ```bash
   pip install pytesseract Pillow psutil
   ```

2. **Install Tesseract OCR:**
   ```bash
   # Windows: Download from GitHub releases
   # macOS: brew install tesseract
   # Linux: sudo apt install tesseract-ocr
   ```

3. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

4. **Verify virtual environment:**
   ```bash
   # Activate virtual environment
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

#### Problem: Permission denied errors
```
Error: PermissionError: [Errno 13] Permission denied: './data/quiz.db'
```

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la data/  # Linux/macOS
   dir data\     # Windows
   ```

2. **Fix permissions:**
   ```bash
   chmod 755 data/  # Linux/macOS
   chmod 644 data/quiz.db
   ```

3. **Run as administrator (Windows):**
   ```powershell
   # Right-click Command Prompt and select "Run as administrator"
   ```

### Import Errors

#### Problem: ImportError when running application
```
Error: ImportError: cannot import name 'Question' from 'models'
```

**Solutions:**
1. **Check Python path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

2. **Add src directory to path:**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:./src"  # Linux/macOS
   set PYTHONPATH=%PYTHONPATH%;./src        # Windows
   ```

3. **Use absolute imports:**
   ```python
   from src.models.question import Question
   ```

### Configuration Issues

#### Problem: Configuration file not found
```
Error: FileNotFoundError: [Errno 2] No such file or directory: 'config.json'
```

**Solutions:**
1. **Create default configuration:**
   ```python
   # Run setup script
   python setup.py
   ```

2. **Check configuration path:**
   ```python
   import os
   print(os.path.exists('config.json'))
   ```

3. **Use environment variables:**
   ```bash
   export QUIZ_CONFIG_PATH="./config.json"
   ```

## Installation Problems

### Python Version Issues

#### Problem: Python version too old
```
Error: This application requires Python 3.8 or higher
```

**Solutions:**
1. **Install Python 3.8+:**
   ```bash
   # Windows: Download from python.org
   # macOS: brew install python@3.9
   # Linux: sudo apt install python3.9
   ```

2. **Use pyenv (Linux/macOS):**
   ```bash
   pyenv install 3.9.0
   pyenv local 3.9.0
   ```

3. **Check multiple Python versions:**
   ```bash
   python3.9 --version
   python3.8 --version
   ```

### Virtual Environment Issues

#### Problem: Virtual environment not working
```
Error: The virtual environment was not created successfully
```

**Solutions:**
1. **Create virtual environment manually:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate    # Windows
   ```

2. **Use different Python version:**
   ```bash
   python3.9 -m venv venv
   ```

3. **Check virtual environment:**
   ```bash
   which python  # Should point to venv/bin/python
   ```

### Dependency Installation Issues

#### Problem: pip install fails
```
Error: Failed building wheel for psutil
```

**Solutions:**
1. **Install build tools:**
   ```bash
   # Linux
   sudo apt install build-essential python3-dev
   
   # macOS
   xcode-select --install
   
   # Windows
   # Install Visual Studio Build Tools
   ```

2. **Use pre-compiled wheels:**
   ```bash
   pip install --only-binary=all psutil
   ```

3. **Upgrade pip:**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

### Tesseract OCR Installation

#### Problem: Tesseract not found
```
Error: TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**Solutions:**
1. **Install Tesseract:**
   ```bash
   # Windows: Download from GitHub releases
   # macOS: brew install tesseract
   # Linux: sudo apt install tesseract-ocr
   ```

2. **Add to PATH:**
   ```bash
   # Windows: Add to system PATH
   # Linux/macOS: Add to ~/.bashrc or ~/.zshrc
   export PATH="/usr/local/bin:$PATH"
   ```

3. **Specify Tesseract path:**
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

## Runtime Errors

### Database Connection Errors

#### Problem: Database connection failed
```
Error: sqlite3.OperationalError: unable to open database file
```

**Solutions:**
1. **Check database file:**
   ```bash
   ls -la data/quiz.db
   ```

2. **Create database directory:**
   ```bash
   mkdir -p data
   ```

3. **Check file permissions:**
   ```bash
   chmod 644 data/quiz.db
   ```

4. **Reset database:**
   ```bash
   rm data/quiz.db
   python src/main.py  # Will recreate database
   ```

#### Problem: Database locked
```
Error: sqlite3.OperationalError: database is locked
```

**Solutions:**
1. **Check for running processes:**
   ```bash
   ps aux | grep python
   ```

2. **Kill hanging processes:**
   ```bash
   kill -9 <process_id>
   ```

3. **Wait for lock to release:**
   ```bash
   # Wait 30 seconds and try again
   ```

4. **Force unlock database:**
   ```bash
   sqlite3 data/quiz.db "PRAGMA busy_timeout = 30000;"
   ```

### Memory Errors

#### Problem: Out of memory
```
Error: MemoryError: Unable to allocate array
```

**Solutions:**
1. **Check memory usage:**
   ```bash
   # Linux/macOS
   top
   htop
   
   # Windows
   taskmgr
   ```

2. **Reduce cache size:**
   ```python
   # In config.json
   {
     "performance": {
       "cache_size": 100,
       "memory_threshold": 0.6
     }
   }
   ```

3. **Clear cache:**
   ```python
   from caching_system import cache_manager
   cache_manager.clear_all_caches()
   ```

4. **Restart application:**
   ```bash
   # Close and restart
   ```

### File Permission Errors

#### Problem: Permission denied
```
Error: PermissionError: [Errno 13] Permission denied: './data/logs/error.log'
```

**Solutions:**
1. **Check directory permissions:**
   ```bash
   ls -la data/logs/
   ```

2. **Fix permissions:**
   ```bash
   chmod 755 data/logs/
   chmod 644 data/logs/*.log
   ```

3. **Create directories:**
   ```bash
   mkdir -p data/logs
   mkdir -p data/backups
   mkdir -p data/cache
   ```

4. **Run as administrator (Windows):**
   ```powershell
   # Right-click and "Run as administrator"
   ```

## Performance Issues

### Slow Application

#### Problem: Application is slow to respond
```
Symptoms: Long response times, high CPU usage, memory usage
```

**Solutions:**
1. **Check system resources:**
   ```bash
   # Linux/macOS
   top
   htop
   iostat
   
   # Windows
   taskmgr
   ```

2. **Optimize database:**
   ```python
   from database_manager import DatabaseManager
   db_manager = DatabaseManager()
   db_manager.optimize_database()
   ```

3. **Clear cache:**
   ```python
   from caching_system import cache_manager
   cache_manager.clear_all_caches()
   ```

4. **Reduce cache size:**
   ```python
   # In config.json
   {
     "performance": {
       "cache_size": 500,
       "memory_threshold": 0.7
     }
   }
   ```

### High Memory Usage

#### Problem: Application uses too much memory
```
Symptoms: High memory usage, system slowdown, out of memory errors
```

**Solutions:**
1. **Monitor memory usage:**
   ```python
   import psutil
   print(f"Memory usage: {psutil.virtual_memory().percent:.2f}%")
   ```

2. **Enable garbage collection:**
   ```python
   import gc
   gc.collect()
   ```

3. **Reduce cache size:**
   ```python
   # In config.json
   {
     "performance": {
       "cache_size": 100,
       "memory_threshold": 0.5
     }
   }
   ```

4. **Restart application:**
   ```bash
   # Close and restart to free memory
   ```

### Database Performance

#### Problem: Slow database queries
```
Symptoms: Long query times, database locks, timeout errors
```

**Solutions:**
1. **Create indexes:**
   ```sql
   CREATE INDEX idx_questions_type ON questions(question_type);
   CREATE INDEX idx_questions_created ON questions(created_at);
   CREATE INDEX idx_tags_name ON tags(name);
   ```

2. **Optimize database:**
   ```python
   from database_manager import DatabaseManager
   db_manager = DatabaseManager()
   db_manager.optimize_database()
   ```

3. **Vacuum database:**
   ```sql
   VACUUM;
   ```

4. **Check database size:**
   ```bash
   ls -lh data/quiz.db
   ```

## Database Problems

### Database Corruption

#### Problem: Database is corrupted
```
Error: sqlite3.DatabaseError: database disk image is malformed
```

**Solutions:**
1. **Check database integrity:**
   ```sql
   PRAGMA integrity_check;
   ```

2. **Repair database:**
   ```sql
   VACUUM;
   ```

3. **Restore from backup:**
   ```bash
   cp data/backups/quiz_backup_latest.db data/quiz.db
   ```

4. **Reset database:**
   ```bash
   rm data/quiz.db
   python src/main.py  # Will recreate database
   ```

### Database Lock Issues

#### Problem: Database is locked
```
Error: sqlite3.OperationalError: database is locked
```

**Solutions:**
1. **Check for running processes:**
   ```bash
   ps aux | grep python
   ```

2. **Kill hanging processes:**
   ```bash
   kill -9 <process_id>
   ```

3. **Wait for lock to release:**
   ```bash
   # Wait 30 seconds and try again
   ```

4. **Force unlock:**
   ```sql
   PRAGMA busy_timeout = 30000;
   ```

### Database Migration Issues

#### Problem: Migration fails
```
Error: MigrationError: Failed to migrate database
```

**Solutions:**
1. **Check database version:**
   ```sql
   PRAGMA user_version;
   ```

2. **Backup before migration:**
   ```bash
   cp data/quiz.db data/quiz_backup.db
   ```

3. **Run migration manually:**
   ```python
   from database.migration import DatabaseMigration
   migration = DatabaseMigration()
   migration.migrate_database()
   ```

4. **Reset and recreate:**
   ```bash
   rm data/quiz.db
   python src/main.py
   ```

## OCR Issues

### Tesseract Not Found

#### Problem: Tesseract OCR not installed
```
Error: TesseractNotFoundError: tesseract is not installed
```

**Solutions:**
1. **Install Tesseract:**
   ```bash
   # Windows: Download from GitHub releases
   # macOS: brew install tesseract
   # Linux: sudo apt install tesseract-ocr
   ```

2. **Add to PATH:**
   ```bash
   # Windows: Add to system PATH
   # Linux/macOS: Add to ~/.bashrc
   export PATH="/usr/local/bin:$PATH"
   ```

3. **Specify Tesseract path:**
   ```python
   import pytesseract
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### OCR Accuracy Issues

#### Problem: Poor OCR accuracy
```
Symptoms: Incorrect text extraction, missing text, garbled output
```

**Solutions:**
1. **Improve image quality:**
   - Use high-resolution images (300+ DPI)
   - Ensure good contrast
   - Remove noise and artifacts
   - Correct skew and rotation

2. **Adjust OCR settings:**
   ```python
   # In config.json
   {
     "ocr": {
       "confidence_threshold": 0.7,
       "preprocessing": true,
       "language": "eng"
     }
   }
   ```

3. **Use different OCR configurations:**
   ```python
   # Try different Tesseract configurations
   config = '--psm 6 --oem 3'
   text = pytesseract.image_to_string(image, config=config)
   ```

### Image Format Issues

#### Problem: Unsupported image format
```
Error: UnsupportedImageError: cannot identify image file
```

**Solutions:**
1. **Check image format:**
   ```bash
   file image.png
   ```

2. **Convert image format:**
   ```bash
   # Convert to PNG
   convert image.jpg image.png
   ```

3. **Use supported formats:**
   - PNG (recommended)
   - JPEG
   - TIFF
   - BMP

## File I/O Problems

### File Permission Issues

#### Problem: Cannot read/write files
```
Error: PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la data/
   ```

2. **Fix permissions:**
   ```bash
   chmod 755 data/
   chmod 644 data/*.json
   chmod 644 data/*.db
   ```

3. **Run as administrator (Windows):**
   ```powershell
   # Right-click and "Run as administrator"
   ```

### File Not Found

#### Problem: File not found errors
```
Error: FileNotFoundError: [Errno 2] No such file or directory
```

**Solutions:**
1. **Check file existence:**
   ```bash
   ls -la data/
   ```

2. **Create missing directories:**
   ```bash
   mkdir -p data/logs
   mkdir -p data/backups
   mkdir -p data/cache
   ```

3. **Check file paths:**
   ```python
   import os
   print(os.path.exists('data/quiz.db'))
   ```

### Disk Space Issues

#### Problem: No space left on device
```
Error: OSError: [Errno 28] No space left on device
```

**Solutions:**
1. **Check disk space:**
   ```bash
   df -h  # Linux/macOS
   dir    # Windows
   ```

2. **Clean up old files:**
   ```bash
   rm -rf data/logs/*.log.old
   rm -rf data/backups/*.old
   ```

3. **Compress files:**
   ```bash
   gzip data/logs/*.log
   ```

## Memory Issues

### Out of Memory

#### Problem: Memory allocation failed
```
Error: MemoryError: Unable to allocate array
```

**Solutions:**
1. **Check memory usage:**
   ```bash
   # Linux/macOS
   top
   htop
   
   # Windows
   taskmgr
   ```

2. **Reduce cache size:**
   ```python
   # In config.json
   {
     "performance": {
       "cache_size": 100,
       "memory_threshold": 0.5
     }
   }
   ```

3. **Clear cache:**
   ```python
   from caching_system import cache_manager
   cache_manager.clear_all_caches()
   ```

4. **Restart application:**
   ```bash
   # Close and restart
   ```

### Memory Leaks

#### Problem: Memory usage keeps increasing
```
Symptoms: Memory usage grows over time, system slowdown
```

**Solutions:**
1. **Monitor memory usage:**
   ```python
   import psutil
   import time
   
   while True:
       print(f"Memory: {psutil.virtual_memory().percent:.2f}%")
       time.sleep(60)
   ```

2. **Force garbage collection:**
   ```python
   import gc
   gc.collect()
   ```

3. **Check for memory leaks:**
   ```python
   # Use memory profiler
   from memory_profiler import profile
   
   @profile
   def your_function():
       pass
   ```

4. **Restart application:**
   ```bash
   # Close and restart
   ```

## Network Issues

### Connection Issues

#### Problem: Cannot connect to database
```
Error: sqlite3.OperationalError: unable to open database file
```

**Solutions:**
1. **Check database file:**
   ```bash
   ls -la data/quiz.db
   ```

2. **Check file permissions:**
   ```bash
   chmod 644 data/quiz.db
   ```

3. **Check disk space:**
   ```bash
   df -h
   ```

### Firewall Issues

#### Problem: Application blocked by firewall
```
Error: Connection refused
```

**Solutions:**
1. **Check firewall settings:**
   ```bash
   # Linux
   sudo ufw status
   
   # Windows
   netsh advfirewall show allprofiles
   ```

2. **Allow application through firewall:**
   ```bash
   # Linux
   sudo ufw allow 8000/tcp
   
   # Windows
   netsh advfirewall firewall add rule name="Quiz App" dir=in action=allow protocol=TCP localport=8000
   ```

## Platform-Specific Issues

### Windows Issues

#### Problem: Path issues on Windows
```
Error: OSError: [Errno 22] Invalid argument
```

**Solutions:**
1. **Use raw strings:**
   ```python
   path = r"C:\path\to\file"
   ```

2. **Use pathlib:**
   ```python
   from pathlib import Path
   path = Path("C:/path/to/file")
   ```

3. **Check path separators:**
   ```python
   import os
   path = os.path.join("C:", "path", "to", "file")
   ```

#### Problem: Windows service issues
```
Error: The service did not start
```

**Solutions:**
1. **Check service configuration:**
   ```powershell
   sc query "QuizApp"
   ```

2. **Check service logs:**
   ```powershell
   Get-EventLog -LogName Application -Source "QuizApp"
   ```

3. **Reinstall service:**
   ```powershell
   sc delete "QuizApp"
   sc create "QuizApp" binPath="C:\path\to\quiz-app\venv\Scripts\python.exe C:\path\to\quiz-app\src\main.py"
   ```

### macOS Issues

#### Problem: Permission issues on macOS
```
Error: PermissionError: [Errno 13] Permission denied
```

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la data/
   ```

2. **Fix permissions:**
   ```bash
   chmod 755 data/
   chmod 644 data/*.db
   ```

3. **Check system integrity:**
   ```bash
   sudo diskutil verifyDisk disk0
   ```

#### Problem: Homebrew issues
```
Error: brew: command not found
```

**Solutions:**
1. **Install Homebrew:**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Add to PATH:**
   ```bash
   echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Linux Issues

#### Problem: Package manager issues
```
Error: E: Unable to locate package python3.9
```

**Solutions:**
1. **Update package lists:**
   ```bash
   sudo apt update
   ```

2. **Add Python repository:**
   ```bash
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update
   ```

3. **Install Python:**
   ```bash
   sudo apt install python3.9 python3.9-venv
   ```

#### Problem: Systemd service issues
```
Error: Failed to start quiz-app.service
```

**Solutions:**
1. **Check service status:**
   ```bash
   sudo systemctl status quiz-app
   ```

2. **Check service logs:**
   ```bash
   sudo journalctl -u quiz-app -f
   ```

3. **Reload systemd:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart quiz-app
   ```

## Getting Help

### Debug Mode

#### Enable debug logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Run with debug flags
```bash
python src/main.py --debug --verbose
```

### Log Files

#### Check log files
```bash
# Error log
tail -f data/logs/error.log

# Info log
tail -f data/logs/info.log

# Debug log
tail -f data/logs/debug.log
```

#### Clear log files
```bash
rm data/logs/*.log
```

### Performance Profiling

#### Profile application
```python
import cProfile
cProfile.run('python src/main.py', 'profile_output.prof')
```

#### Analyze profile
```python
import pstats
p = pstats.Stats('profile_output.prof')
p.sort_stats('cumulative').print_stats(10)
```

### System Information

#### Get system info
```python
import platform
import psutil

print(f"Platform: {platform.platform()}")
print(f"Python: {platform.python_version()}")
print(f"CPU: {psutil.cpu_count()} cores")
print(f"Memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")
```

### Contact Support

#### Report issues
- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and get help
- **Email Support**: Contact maintainers for urgent issues

#### Provide information
When reporting issues, include:
- Operating system and version
- Python version
- Error messages and logs
- Steps to reproduce the issue
- System configuration

---

**For additional help, see the [User Guide](USER_GUIDE.md) and [API Reference](API_REFERENCE.md).**
