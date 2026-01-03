# Quiz Application - Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Performance Tuning](#performance-tuning)
6. [Security Considerations](#security-considerations)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)
10. [Platform-Specific Instructions](#platform-specific-instructions)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10, macOS 10.14, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Memory**: 512MB RAM
- **Storage**: 100MB free space
- **CPU**: 1 GHz processor

### Recommended Requirements
- **Operating System**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Python**: 3.9 or higher
- **Memory**: 2GB RAM
- **Storage**: 500MB free space
- **CPU**: 2 GHz dual-core processor

### Optional Dependencies
- **Tesseract OCR**: For OCR functionality
- **ImageMagick**: For advanced image processing
- **Git**: For version control

## Installation Methods

### Method 1: Direct Installation

#### Windows
```powershell
# Download and install Python 3.8+ from python.org
# Open Command Prompt or PowerShell

# Clone repository
git clone https://github.com/your-username/quiz-app.git
cd quiz-app

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
# Install Python using Homebrew
brew install python

# Clone repository
git clone https://github.com/your-username/quiz-app.git
cd quiz-app

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
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Clone repository
git clone https://github.com/your-username/quiz-app.git
cd quiz-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

### Method 2: Docker Installation

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY data/ ./data/

# Create non-root user
RUN useradd -m -u 1000 quizuser && chown -R quizuser:quizuser /app
USER quizuser

# Expose port (if needed)
EXPOSE 8000

# Run application
CMD ["python", "src/main.py"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  quiz-app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - QUIZ_DB_PATH=/app/data/quiz.db
      - QUIZ_LOG_LEVEL=INFO
    restart: unless-stopped
```

#### Docker Commands
```bash
# Build image
docker build -t quiz-app .

# Run container
docker run -d --name quiz-app -p 8000:8000 -v $(pwd)/data:/app/data quiz-app

# Using Docker Compose
docker-compose up -d
```

### Method 3: Package Installation

#### Create Package
```bash
# Create setup.py
cat > setup.py << EOF
from setuptools import setup, find_packages

setup(
    name="quiz-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pytesseract==0.3.10",
        "Pillow==9.5.0",
        "psutil==5.9.5",
        "colorama==0.4.6",
        "click==8.1.7",
        "rich==13.7.0"
    ],
    entry_points={
        "console_scripts": [
            "quiz-app=src.main:main"
        ]
    }
)
EOF

# Build package
python setup.py sdist bdist_wheel

# Install package
pip install dist/quiz_app-1.0.0-py3-none-any.whl
```

#### Install from Package
```bash
# Install from wheel
pip install quiz_app-1.0.0-py3-none-any.whl

# Run application
quiz-app
```

## Configuration

### Environment Variables

#### Database Configuration
```bash
export QUIZ_DB_PATH="./data/quiz.db"
export QUIZ_BACKUP_DIR="./data/backups"
export QUIZ_DB_POOL_SIZE=10
export QUIZ_DB_TIMEOUT=30
```

#### Performance Configuration
```bash
export QUIZ_CACHE_SIZE=1000
export QUIZ_MEMORY_THRESHOLD=0.8
export QUIZ_OPTIMIZATION_LEVEL="medium"
export QUIZ_GC_THRESHOLD=1000
```

#### Logging Configuration
```bash
export QUIZ_LOG_LEVEL="INFO"
export QUIZ_LOG_DIR="./data/logs"
export QUIZ_LOG_MAX_SIZE=10485760
export QUIZ_LOG_BACKUP_COUNT=5
```

#### OCR Configuration
```bash
export QUIZ_OCR_ENABLED=true
export QUIZ_OCR_CONFIDENCE=0.7
export QUIZ_OCR_LANGUAGE="eng"
export QUIZ_OCR_PREPROCESSING=true
```

### Configuration File

#### config.json
```json
{
    "database": {
        "path": "./data/quiz.db",
        "backup_dir": "./data/backups",
        "connection_pool_size": 10,
        "timeout": 30,
        "optimization": {
            "auto_optimize": true,
            "optimization_frequency": "weekly",
            "index_optimization": true,
            "query_optimization": true
        }
    },
    "performance": {
        "cache_size": 1000,
        "memory_threshold": 0.8,
        "optimization_level": "medium",
        "gc_threshold": 1000,
        "monitoring": {
            "enabled": true,
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
        "compression": true
    },
    "ocr": {
        "enabled": true,
        "confidence_threshold": 0.7,
        "language": "eng",
        "preprocessing": true,
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
            "show_progress": true,
            "show_timers": true,
            "show_statistics": true,
            "color_scheme": "default"
        }
    }
}
```

### Application Settings

#### Settings Menu
```
Settings Menu:
1. Performance Settings
2. UI Settings
3. Database Settings
4. OCR Settings
5. Logging Settings
6. Security Settings
7. Backup Settings
8. Reset to Defaults
0. Back to Main Menu
```

#### Performance Settings
```
Performance Settings:
- Cache Size: 1000 entries
- Memory Threshold: 80%
- Optimization Level: Medium
- Garbage Collection: Automatic
- Monitoring: Enabled
```

#### UI Settings
```
UI Settings:
- Theme: Default
- Show Progress: Yes
- Show Timers: Yes
- Show Statistics: Yes
- Color Scheme: Default
- Keyboard Shortcuts: Enabled
```

## Database Setup

### SQLite Database

#### Initial Setup
```python
from database_manager import DatabaseManager

# Initialize database
db_manager = DatabaseManager("./data/quiz.db")
db_manager.initialize_database()

# Create tables
db_manager.create_schema()

# Verify setup
stats = db_manager.get_database_statistics()
print(f"Database initialized: {stats['initialized']}")
```

#### Database Schema
```sql
-- Questions table
CREATE TABLE questions (
    id TEXT PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type TEXT NOT NULL,
    answers TEXT NOT NULL,  -- JSON
    tags TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tags table
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    parent_id TEXT,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    aliases TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quiz sessions table
CREATE TABLE quiz_sessions (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    questions TEXT NOT NULL,  -- JSON
    answers TEXT,  -- JSON
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    score REAL,
    duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics table
CREATE TABLE analytics (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    question_id TEXT,
    user_id TEXT,
    answer TEXT,
    is_correct BOOLEAN,
    response_time REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Database Optimization
```python
# Optimize database
optimization_results = db_manager.optimize_database()

# Create indexes
db_manager.create_indexes()

# Update statistics
db_manager.update_statistics()

# Vacuum database
db_manager.vacuum_database()
```

### Database Backup

#### Automatic Backup
```python
# Configure automatic backup
backup_config = {
    "enabled": True,
    "frequency": "daily",
    "retention_days": 30,
    "compression": True,
    "location": "./data/backups"
}

# Schedule backup
db_manager.schedule_backup(backup_config)
```

#### Manual Backup
```python
# Create backup
backup_path = db_manager.backup_database()
print(f"Backup created: {backup_path}")

# Restore from backup
restore_success = db_manager.restore_database(backup_path)
print(f"Restore successful: {restore_success}")
```

## Performance Tuning

### Memory Optimization

#### Memory Settings
```python
# Configure memory optimization
memory_config = {
    "cache_size": 1000,
    "memory_threshold": 0.8,
    "gc_threshold": 1000,
    "monitoring": True
}

# Apply settings
optimizer = PerformanceOptimizer(**memory_config)
```

#### Garbage Collection
```python
# Optimize garbage collection
gc_optimizer = GarbageCollectionOptimizer()
gc_results = gc_optimizer.optimize()

# Monitor memory usage
memory_monitor = MemoryMonitor()
memory_monitor.start_monitoring(interval=30)
```

### Database Optimization

#### Query Optimization
```python
# Optimize database queries
db_optimizer = DatabaseOptimizer()
optimization_results = db_optimizer.optimize_database("./data/quiz.db")

# Create performance indexes
indexes = [
    "CREATE INDEX idx_questions_type ON questions(question_type)",
    "CREATE INDEX idx_questions_created ON questions(created_at)",
    "CREATE INDEX idx_tags_name ON tags(name)",
    "CREATE INDEX idx_sessions_user ON quiz_sessions(user_id)",
    "CREATE INDEX idx_sessions_date ON quiz_sessions(start_time)"
]

for index_sql in indexes:
    db_manager.execute_query(index_sql)
```

#### Connection Pooling
```python
# Configure connection pooling
pool_config = {
    "max_connections": 10,
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1
}

# Apply configuration
db_manager.configure_connection_pool(pool_config)
```

### Caching Optimization

#### Cache Configuration
```python
# Configure intelligent caching
cache_config = {
    "max_size": 1000,
    "default_ttl": 3600,
    "cleanup_interval": 300,
    "eviction_policy": "lru"
}

# Initialize cache
cache = IntelligentCache(**cache_config)
cache.start_cleanup_thread()
```

#### Cache Statistics
```python
# Monitor cache performance
stats = cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate']:.2f}%")
print(f"Cache size: {stats['size']}/{stats['max_size']}")
print(f"Memory usage: {stats['memory_usage']} bytes")
```

## Security Considerations

### Data Protection

#### Encryption
```python
# Enable data encryption
encryption_config = {
    "enabled": True,
    "algorithm": "AES-256",
    "key_rotation": True,
    "key_rotation_interval": 30
}

# Apply encryption
data_persistence = DataPersistence(encryption_config)
```

#### Access Control
```python
# Configure access control
access_control = {
    "user_authentication": True,
    "session_timeout": 3600,
    "max_login_attempts": 5,
    "password_policy": {
        "min_length": 8,
        "require_special_chars": True,
        "require_numbers": True
    }
}
```

### File Permissions

#### Linux/macOS
```bash
# Set appropriate permissions
chmod 755 quiz-app
chmod 644 data/quiz.db
chmod 600 data/logs/*.log
chmod 700 data/backups/
```

#### Windows
```powershell
# Set file permissions
icacls data\quiz.db /grant:r "%USERNAME%:(R,W)"
icacls data\logs\*.log /grant:r "%USERNAME%:(R,W)"
icacls data\backups\ /grant:r "%USERNAME%:(F)"
```

### Network Security

#### Firewall Configuration
```bash
# Linux firewall (ufw)
sudo ufw allow 8000/tcp
sudo ufw enable

# Windows firewall
netsh advfirewall firewall add rule name="Quiz App" dir=in action=allow protocol=TCP localport=8000
```

#### SSL/TLS Configuration
```python
# Configure SSL/TLS
ssl_config = {
    "enabled": True,
    "cert_file": "./certs/server.crt",
    "key_file": "./certs/server.key",
    "protocol": "TLSv1.2"
}
```

## Monitoring & Logging

### Logging Configuration

#### Log Levels
```python
# Configure logging levels
logging_config = {
    "error": "ERROR",
    "info": "INFO",
    "debug": "DEBUG",
    "audit": "INFO",
    "performance": "INFO"
}
```

#### Log Rotation
```python
# Configure log rotation
rotation_config = {
    "max_file_size": 10485760,  # 10MB
    "backup_count": 5,
    "rotation_frequency": "daily",
    "compression": True
}
```

### Performance Monitoring

#### System Metrics
```python
# Monitor system performance
monitor = PerformanceMonitor()
metrics = monitor.get_system_metrics()

print(f"CPU Usage: {metrics['cpu_usage']:.2f}%")
print(f"Memory Usage: {metrics['memory_usage']:.2f}%")
print(f"Disk Usage: {metrics['disk_usage']:.2f}%")
```

#### Application Metrics
```python
# Monitor application performance
app_metrics = monitor.get_application_metrics()

print(f"Response Time: {app_metrics['response_time']:.2f}ms")
print(f"Throughput: {app_metrics['throughput']:.2f} req/s")
print(f"Error Rate: {app_metrics['error_rate']:.2f}%")
```

### Health Checks

#### Database Health
```python
# Check database health
db_health = db_manager.check_health()
print(f"Database Status: {db_health['status']}")
print(f"Connection Count: {db_health['connections']}")
print(f"Query Performance: {db_health['query_performance']}")
```

#### Application Health
```python
# Check application health
app_health = monitor.check_application_health()
print(f"Application Status: {app_health['status']}")
print(f"Memory Usage: {app_health['memory_usage']:.2f}%")
print(f"Cache Performance: {app_health['cache_performance']}")
```

## Backup & Recovery

### Automated Backup

#### Backup Schedule
```python
# Configure automated backup
backup_schedule = {
    "enabled": True,
    "frequency": "daily",
    "time": "02:00",
    "retention_days": 30,
    "compression": True,
    "encryption": True
}

# Schedule backup
scheduler = BackupScheduler(backup_schedule)
scheduler.start()
```

#### Backup Verification
```python
# Verify backup integrity
backup_verifier = BackupVerifier()
verification_results = backup_verifier.verify_backup(backup_path)

print(f"Backup Valid: {verification_results['valid']}")
print(f"Data Integrity: {verification_results['integrity']}")
print(f"File Size: {verification_results['size']} bytes")
```

### Recovery Procedures

#### Database Recovery
```python
# Recover from backup
recovery_config = {
    "backup_path": "./data/backups/quiz_backup_2024-01-15.db",
    "verify_integrity": True,
    "restore_analytics": True,
    "restore_sessions": True
}

# Perform recovery
recovery_success = db_manager.recover_from_backup(recovery_config)
print(f"Recovery Successful: {recovery_success}")
```

#### Data Migration
```python
# Migrate data between systems
migration_config = {
    "source_path": "./old_data/quiz.db",
    "target_path": "./data/quiz.db",
    "preserve_analytics": True,
    "preserve_sessions": True
}

# Perform migration
migration_success = db_manager.migrate_data(migration_config)
print(f"Migration Successful: {migration_success}")
```

## Troubleshooting

### Common Issues

#### Database Issues
```bash
# Check database integrity
sqlite3 data/quiz.db "PRAGMA integrity_check;"

# Repair database
sqlite3 data/quiz.db "VACUUM;"

# Reset database
rm data/quiz.db
python src/main.py  # Will recreate database
```

#### Memory Issues
```bash
# Check memory usage
ps aux | grep python

# Monitor memory
python -c "import psutil; print(psutil.virtual_memory())"

# Clear cache
python -c "from caching_system import cache_manager; cache_manager.clear_all_caches()"
```

#### Performance Issues
```bash
# Check system resources
top
htop
iostat

# Monitor application
python -c "from performance_optimizer import performance_optimizer; print(performance_optimizer.get_performance_metrics())"
```

### Debug Mode

#### Enable Debug Logging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run application in debug mode
python src/main.py --debug
```

#### Performance Profiling
```python
# Enable performance profiling
import cProfile
cProfile.run('python src/main.py', 'profile_output.prof')

# Analyze profile
import pstats
p = pstats.Stats('profile_output.prof')
p.sort_stats('cumulative').print_stats(10)
```

### Error Recovery

#### Automatic Recovery
```python
# Configure automatic recovery
recovery_config = {
    "enabled": True,
    "max_retries": 3,
    "retry_delay": 5,
    "fallback_mode": True
}

# Apply recovery configuration
error_handler = ErrorHandler(recovery_config)
```

#### Manual Recovery
```bash
# Reset application state
rm -rf data/logs/*
rm -rf data/cache/*
python src/main.py --reset

# Restore from backup
cp data/backups/quiz_backup_latest.db data/quiz.db
python src/main.py
```

## Platform-Specific Instructions

### Windows Deployment

#### Windows Service
```powershell
# Install as Windows service
sc create "QuizApp" binPath="C:\path\to\quiz-app\venv\Scripts\python.exe C:\path\to\quiz-app\src\main.py" start=auto

# Start service
sc start "QuizApp"

# Stop service
sc stop "QuizApp"
```

#### Windows Task Scheduler
```powershell
# Create scheduled task for backup
schtasks /create /tn "QuizApp Backup" /tr "C:\path\to\quiz-app\backup.bat" /sc daily /st 02:00
```

### macOS Deployment

#### LaunchAgent
```xml
<!-- ~/Library/LaunchAgents/com.quizapp.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.quizapp</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/quiz-app/src/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

#### Homebrew Installation
```bash
# Create Homebrew formula
brew create https://github.com/your-username/quiz-app

# Install via Homebrew
brew install quiz-app
```

### Linux Deployment

#### Systemd Service
```ini
# /etc/systemd/system/quiz-app.service
[Unit]
Description=Quiz Application
After=network.target

[Service]
Type=simple
User=quizuser
WorkingDirectory=/opt/quiz-app
ExecStart=/opt/quiz-app/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Systemd Commands
```bash
# Enable and start service
sudo systemctl enable quiz-app
sudo systemctl start quiz-app

# Check status
sudo systemctl status quiz-app

# View logs
sudo journalctl -u quiz-app -f
```

#### Nginx Configuration
```nginx
# /etc/nginx/sites-available/quiz-app
server {
    listen 80;
    server_name quiz-app.local;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### Docker Deployment

#### Production Dockerfile
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY data/ ./data/

# Create non-root user
RUN useradd -m -u 1000 quizuser && chown -R quizuser:quizuser /app
USER quizuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "src/main.py"]
```

#### Docker Compose Production
```yaml
version: '3.8'

services:
  quiz-app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - QUIZ_DB_PATH=/app/data/quiz.db
      - QUIZ_LOG_LEVEL=INFO
      - QUIZ_CACHE_SIZE=1000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - quiz-app
    restart: unless-stopped
```

---

**For additional support and troubleshooting, see the [User Guide](USER_GUIDE.md) and [API Reference](API_REFERENCE.md).**
