"""
Data Persistence Module

This module handles all data storage, validation, encryption, backup, and maintenance
for the quiz application. Implements Phase 1.5 requirements.
"""

import json
import os
import shutil
import hashlib
import gzip
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import logging

# Import encryption modules
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    Fernet = None
    logging.warning("Encryption not available - install cryptography package")

logger = logging.getLogger(__name__)

class DataPersistence:
    """Handles all data persistence operations with encryption, validation, and backup."""
    
    def __init__(self, data_dir: str = "data", encryption_key: Optional[str] = None):
        """
        Initialize data persistence system.
        
        Args:
            data_dir: Directory for data storage
            encryption_key: Optional encryption key (generated if not provided)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.questions_file = self.data_dir / "questions.json"
        self.tags_file = self.data_dir / "tags.json"
        self.sessions_file = self.data_dir / "sessions.json"
        self.analytics_file = self.data_dir / "analytics.json"
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Encryption setup
        self.encryption_key = encryption_key
        if ENCRYPTION_AVAILABLE and not self.encryption_key:
            self.encryption_key = self._generate_encryption_key()
        
        # Data versioning
        self.current_version = "1.0"
        self.version_file = self.data_dir / "version.json"
        
        logger.info(f"Data persistence initialized in {self.data_dir}")
    
    def _generate_encryption_key(self) -> str:
        """Generate a new encryption key."""
        if not ENCRYPTION_AVAILABLE:
            return None
        
        key = Fernet.generate_key()
        return base64.b64encode(key).decode('utf-8')
    
    def _get_fernet(self) -> Optional[Fernet]:
        """Get Fernet encryption object."""
        if not ENCRYPTION_AVAILABLE or not self.encryption_key:
            return None
        
        key = base64.b64decode(self.encryption_key.encode('utf-8'))
        return Fernet(key)
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not ENCRYPTION_AVAILABLE:
            return data
        
        fernet = self._get_fernet()
        if not fernet:
            return data
        
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not ENCRYPTION_AVAILABLE:
            return encrypted_data
        
        fernet = self._get_fernet()
        if not fernet:
            return encrypted_data
        
        try:
            decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return encrypted_data
    
    def _calculate_checksum(self, data: str) -> str:
        """Calculate SHA-256 checksum for data integrity."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def _atomic_write(self, file_path: Path, data) -> bool:
        """
        Write data atomically to prevent corruption.
        
        Args:
            file_path: Target file path
            data: Data to write (string or bytes)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Write to temporary file first
            temp_file = file_path.with_suffix('.tmp')
            
            # Determine if data is binary or text
            if isinstance(data, bytes):
                with open(temp_file, 'wb') as f:
                    f.write(data)
            else:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    f.write(data)
            
            # Atomic rename (works on most filesystems)
            temp_file.replace(file_path)
            
            logger.debug(f"Atomically wrote data to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Atomic write failed for {file_path}: {e}")
            # Clean up temp file if it exists
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def _atomic_read(self, file_path: Path) -> Optional[str]:
        """
        Read data with integrity checking.
        
        Args:
            file_path: File path to read
            
        Returns:
            File contents or None if failed
        """
        try:
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            logger.debug(f"Read data from {file_path}")
            return data
            
        except Exception as e:
            logger.error(f"Read failed for {file_path}: {e}")
            return None
    
    def save_questions(self, questions: List[Dict[str, Any]]) -> bool:
        """
        Save questions with atomic write and validation.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate all questions before saving
            for question in questions:
                validation_result = self._validate_question(question)
                if not validation_result['is_valid']:
                    logger.error(f"Invalid question {question.get('id', 'unknown')}: {validation_result['errors']}")
                    return False
            
            # Prepare data for saving
            data = {
                'version': self.current_version,
                'timestamp': datetime.now().isoformat(),
                'questions': questions
            }
            
            # Serialize to JSON
            json_data = json.dumps(data, indent=2, default=str)
            
            # Calculate checksum and add to data
            data['checksum'] = self._calculate_checksum(json_data)
            json_data = json.dumps(data, indent=2, default=str)
            
            # Atomic write
            success = self._atomic_write(self.questions_file, json_data)
            
            if success:
                logger.info(f"Saved {len(questions)} questions to {self.questions_file}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to save questions: {e}")
            return False
    
    def load_questions(self) -> List[Dict[str, Any]]:
        """
        Load questions with validation and error recovery.
        
        Returns:
            List of question dictionaries
        """
        try:
            # Try to read the file
            data = self._atomic_read(self.questions_file)
            if not data:
                logger.info("No questions file found, returning empty list")
                return []
            
            # Parse JSON
            parsed_data = json.loads(data)
            
            # Verify checksum
            stored_checksum = parsed_data.get('checksum')
            if stored_checksum:
                # Calculate checksum without the checksum field
                data_without_checksum = parsed_data.copy()
                data_without_checksum.pop('checksum', None)
                json_without_checksum = json.dumps(data_without_checksum, indent=2, default=str)
                calculated_checksum = self._calculate_checksum(json_without_checksum)
                if stored_checksum != calculated_checksum:
                    logger.warning("Checksum mismatch, attempting recovery")
                    return self._recover_questions()
            
            # Validate questions
            questions = parsed_data.get('questions', [])
            valid_questions = []
            
            for question in questions:
                validation_result = self._validate_question(question)
                if validation_result['is_valid']:
                    valid_questions.append(question)
                else:
                    logger.warning(f"Skipping invalid question {question.get('id', 'unknown')}: {validation_result['errors']}")
            
            logger.info(f"Loaded {len(valid_questions)} valid questions")
            return valid_questions
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._recover_questions()
        except Exception as e:
            logger.error(f"Failed to load questions: {e}")
            return self._recover_questions()
    
    def _recover_questions(self) -> List[Dict[str, Any]]:
        """Attempt to recover questions from backup."""
        try:
            # Try to load from backup
            backup_files = list(self.backup_dir.glob("questions_backup_*.json"))
            if backup_files:
                # Get most recent backup
                latest_backup = max(backup_files, key=os.path.getctime)
                logger.info(f"Attempting recovery from {latest_backup}")
                
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                
                questions = backup_data.get('questions', [])
                logger.info(f"Recovered {len(questions)} questions from backup")
                return questions
            
            logger.warning("No backup found, returning empty list")
            return []
            
        except Exception as e:
            logger.error(f"Recovery failed: {e}")
            return []
    
    def _validate_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate question data structure and content.
        
        Args:
            question: Question dictionary to validate
            
        Returns:
            Validation result with errors
        """
        errors = []
        
        # Required fields
        required_fields = ['id', 'question_text', 'question_type', 'answers', 'tags']
        for field in required_fields:
            if field not in question:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return {'is_valid': False, 'errors': errors}
        
        # Validate question text
        question_text = question.get('question_text', '')
        if not isinstance(question_text, str):
            errors.append("Question text must be a string")
        elif len(question_text.strip()) < 10:
            errors.append("Question text must be at least 10 characters")
        elif len(question_text.strip()) > 500:
            errors.append("Question text cannot exceed 500 characters")
        
        # Validate question type
        valid_types = ['multiple_choice', 'true_false', 'select_all']
        if question.get('question_type') not in valid_types:
            errors.append(f"Question type must be one of: {', '.join(valid_types)}")
        
        # Validate answers
        answers = question.get('answers', [])
        if not isinstance(answers, list):
            errors.append("Answers must be a list")
        elif len(answers) < 2:
            errors.append("At least 2 answer options are required")
        elif len(answers) > 6:
            errors.append("Maximum 6 answer options allowed")
        else:
            # Validate answer structure
            correct_count = 0
            for i, answer in enumerate(answers):
                if not isinstance(answer, dict):
                    errors.append(f"Answer {i+1} must be a dictionary")
                    continue
                
                if 'text' not in answer or not answer.get('text', '').strip():
                    errors.append(f"Answer {i+1} text cannot be empty")
                
                if 'is_correct' not in answer:
                    errors.append(f"Answer {i+1} must specify if it's correct")
                elif answer.get('is_correct'):
                    correct_count += 1
            
            # Validate correct answer count
            question_type = question.get('question_type')
            if question_type == 'multiple_choice' and correct_count != 1:
                errors.append("Multiple choice questions must have exactly one correct answer")
            elif question_type == 'true_false' and correct_count != 1:
                errors.append("True/false questions must have exactly one correct answer")
            elif question_type == 'select_all' and correct_count == 0:
                errors.append("Select all questions must have at least one correct answer")
        
        # Validate tags
        tags = question.get('tags', [])
        if not isinstance(tags, list):
            errors.append("Tags must be a list")
        elif len(tags) == 0:
            errors.append("At least one tag is required")
        elif len(tags) > 10:
            errors.append("Maximum 10 tags allowed")
        else:
            for tag in tags:
                if not isinstance(tag, str) or not tag.strip():
                    errors.append("Tag names cannot be empty")
                elif len(tag.strip()) > 20:
                    errors.append("Tag names cannot exceed 20 characters")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def save_sessions(self, sessions: Dict[str, Any]) -> bool:
        """
        Save quiz sessions with compression.
        
        Args:
            sessions: Dictionary of session data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare data
            data = {
                'version': self.current_version,
                'timestamp': datetime.now().isoformat(),
                'sessions': sessions
            }
            
            # Serialize to JSON
            json_data = json.dumps(data, indent=2, default=str)
            
            # Calculate checksum and add to data
            data['checksum'] = self._calculate_checksum(json_data)
            json_data = json.dumps(data, indent=2, default=str)
            
            # Compress the final JSON data
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            
            # Write compressed data
            success = self._atomic_write(self.sessions_file.with_suffix('.json.gz'), compressed_data)
            
            if success:
                logger.info(f"Saved {len(sessions)} sessions (compressed)")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
            return False
    
    def load_sessions(self) -> Dict[str, Any]:
        """
        Load quiz sessions with decompression.
        
        Returns:
            Dictionary of session data
        """
        try:
            compressed_file = self.sessions_file.with_suffix('.json.gz')
            
            if not compressed_file.exists():
                logger.info("No sessions file found, returning empty dict")
                return {}
            
            # Read and decompress
            with open(compressed_file, 'rb') as f:
                compressed_data = f.read()
            
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            parsed_data = json.loads(json_data)
            
            # Verify checksum
            stored_checksum = parsed_data.get('checksum')
            if stored_checksum:
                # Calculate checksum without the checksum field
                data_without_checksum = parsed_data.copy()
                data_without_checksum.pop('checksum', None)
                json_without_checksum = json.dumps(data_without_checksum, indent=2, default=str)
                calculated_checksum = self._calculate_checksum(json_without_checksum)
                if stored_checksum != calculated_checksum:
                    logger.warning("Session data checksum mismatch")
                    return {}
            
            sessions = parsed_data.get('sessions', {})
            logger.info(f"Loaded {len(sessions)} sessions")
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            return {}
    
    def backup_data(self) -> bool:
        """
        Create backup of all data with versioning.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(exist_ok=True)
            
            # Backup all data files
            files_to_backup = [
                self.questions_file,
                self.tags_file,
                self.analytics_file,
                self.sessions_file.with_suffix('.json.gz')
            ]
            
            for file_path in files_to_backup:
                if file_path.exists():
                    backup_file = backup_path / file_path.name
                    shutil.copy2(file_path, backup_file)
                    logger.debug(f"Backed up {file_path.name}")
            
            # Create backup manifest
            manifest = {
                'backup_name': backup_name,
                'timestamp': datetime.now().isoformat(),
                'version': self.current_version,
                'files': [f.name for f in files_to_backup if f.exists()]
            }
            
            manifest_file = backup_path / "manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Clean up old backups (keep last 30 days)
            self._cleanup_old_backups()
            
            logger.info(f"Created backup: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Remove backups older than 30 days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            
            for backup_dir in self.backup_dir.iterdir():
                if backup_dir.is_dir() and backup_dir.name.startswith('backup_'):
                    # Extract timestamp from directory name
                    try:
                        timestamp_str = backup_dir.name.replace('backup_', '')
                        backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        
                        if backup_date < cutoff_date:
                            shutil.rmtree(backup_dir)
                            logger.info(f"Removed old backup: {backup_dir.name}")
                    except ValueError:
                        # Skip directories with invalid names
                        continue
                        
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    def restore_data(self, backup_name: str) -> bool:
        """
        Restore data from backup.
        
        Args:
            backup_name: Name of backup to restore
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                logger.error(f"Backup {backup_name} not found")
                return False
            
            # Read manifest
            manifest_file = backup_path / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                logger.info(f"Restoring backup from {manifest['timestamp']}")
            
            # Restore files from backup
            files_to_restore = [
                self.questions_file,
                self.tags_file,
                self.analytics_file,
                self.sessions_file.with_suffix('.json.gz')
            ]
            
            for file_path in files_to_restore:
                backup_file = backup_path / file_path.name
                if backup_file.exists():
                    shutil.copy2(backup_file, file_path)
                    logger.info(f"Restored {file_path.name}")
            
            logger.info(f"Successfully restored backup: {backup_name}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def export_data(self, format: str = "json") -> Optional[str]:
        """
        Export all data in specified format.
        
        Args:
            format: Export format ("json", "csv")
            
        Returns:
            Exported data as string or None if failed
        """
        try:
            # Load all data
            questions = self.load_questions()
            sessions = self.load_sessions()
            
            # Load tags and analytics if they exist
            tags = []
            analytics = {}
            
            if self.tags_file.exists():
                tags_data = self._atomic_read(self.tags_file)
                if tags_data:
                    tags = json.loads(tags_data)
            
            if self.analytics_file.exists():
                analytics_data = self._atomic_read(self.analytics_file)
                if analytics_data:
                    analytics = json.loads(analytics_data)
            
            # Prepare export data
            export_data = {
                'version': self.current_version,
                'export_timestamp': datetime.now().isoformat(),
                'questions': questions,
                'tags': tags,
                'sessions': sessions,
                'analytics': analytics
            }
            
            if format == "json":
                return json.dumps(export_data, indent=2, default=str)
            elif format == "csv":
                return self._export_to_csv(export_data)
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return None
    
    def _export_to_csv(self, data: Dict[str, Any]) -> str:
        """Export data to CSV format."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write questions
        writer.writerow(['Type', 'ID', 'Text', 'Question Type', 'Tags'])
        for question in data.get('questions', []):
            writer.writerow([
                'Question',
                question.get('id', ''),
                question.get('question_text', ''),
                question.get('question_type', ''),
                ', '.join(question.get('tags', []))
            ])
        
        # Write tags
        writer.writerow(['Type', 'ID', 'Name', 'Description'])
        for tag in data.get('tags', []):
            writer.writerow([
                'Tag',
                tag.get('id', ''),
                tag.get('name', ''),
                tag.get('description', '')
            ])
        
        return output.getvalue()
    
    def import_data(self, data: str, format: str = "json") -> bool:
        """
        Import data from external source.
        
        Args:
            data: Data to import
            format: Data format ("json", "csv")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if format == "json":
                import_data = json.loads(data)
            else:
                logger.error(f"Import format {format} not supported yet")
                return False
            
            # Validate imported data
            questions = import_data.get('questions', [])
            for question in questions:
                validation_result = self._validate_question(question)
                if not validation_result['is_valid']:
                    logger.error(f"Invalid imported question: {validation_result['errors']}")
                    return False
            
            # Save imported data
            success = True
            if questions:
                success &= self.save_questions(questions)
            
            if import_data.get('tags'):
                tags_data = json.dumps(import_data['tags'], indent=2)
                success &= self._atomic_write(self.tags_file, tags_data)
            
            if import_data.get('sessions'):
                success &= self.save_sessions(import_data['sessions'])
            
            if success:
                logger.info("Successfully imported data")
            
            return success
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False
    
    def cleanup_old_sessions(self, days: int = 90) -> int:
        """
        Clean up old session data.
        
        Args:
            days: Number of days to keep sessions
            
        Returns:
            Number of sessions cleaned up
        """
        try:
            sessions = self.load_sessions()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cleaned_count = 0
            sessions_to_keep = {}
            
            for session_id, session_data in sessions.items():
                # Check if session is old
                if 'end_time' in session_data:
                    try:
                        end_time = datetime.fromisoformat(session_data['end_time'])
                        if end_time > cutoff_date:
                            sessions_to_keep[session_id] = session_data
                        else:
                            cleaned_count += 1
                    except (ValueError, TypeError):
                        # Keep sessions with invalid timestamps
                        sessions_to_keep[session_id] = session_data
                else:
                    # Keep incomplete sessions
                    sessions_to_keep[session_id] = session_data
            
            # Save cleaned sessions
            if cleaned_count > 0:
                self.save_sessions(sessions_to_keep)
                logger.info(f"Cleaned up {cleaned_count} old sessions")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")
            return 0
    
    def get_data_integrity_report(self) -> Dict[str, Any]:
        """
        Generate data integrity report.
        
        Returns:
            Report with integrity status
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'version': self.current_version,
            'files': {},
            'overall_status': 'healthy'
        }
        
        # Check each data file
        files_to_check = [
            ('questions', self.questions_file),
            ('tags', self.tags_file),
            ('analytics', self.analytics_file),
            ('sessions', self.sessions_file.with_suffix('.json.gz'))
        ]
        
        for name, file_path in files_to_check:
            file_status = {
                'exists': file_path.exists(),
                'size': 0,
                'checksum_valid': False,
                'data_valid': False
            }
            
            if file_path.exists():
                file_status['size'] = file_path.stat().st_size
                
                try:
                    if file_path.suffix == '.gz':
                        # Compressed file
                        with open(file_path, 'rb') as f:
                            data = gzip.decompress(f.read()).decode('utf-8')
                    else:
                        # Regular file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = f.read()
                    
                    parsed_data = json.loads(data)
                    stored_checksum = parsed_data.get('checksum')
                    
                    if stored_checksum:
                        # Calculate checksum without the checksum field
                        data_without_checksum = parsed_data.copy()
                        data_without_checksum.pop('checksum', None)
                        json_without_checksum = json.dumps(data_without_checksum, indent=2, default=str)
                        calculated_checksum = self._calculate_checksum(json_without_checksum)
                        file_status['checksum_valid'] = (stored_checksum == calculated_checksum)
                    
                    # Basic data validation
                    if name == 'questions':
                        questions = parsed_data.get('questions', [])
                        valid_count = 0
                        for question in questions:
                            if self._validate_question(question)['is_valid']:
                                valid_count += 1
                        file_status['data_valid'] = (valid_count == len(questions))
                        file_status['valid_questions'] = valid_count
                        file_status['total_questions'] = len(questions)
                    
                except Exception as e:
                    file_status['error'] = str(e)
                    report['overall_status'] = 'degraded'
            
            report['files'][name] = file_status
        
        return report
