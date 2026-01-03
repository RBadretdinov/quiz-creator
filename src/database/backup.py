"""
Database Backup and Restore

This module provides database backup and restore functionality with compression
and integrity verification.
"""

import os
import shutil
import gzip
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from .connection import DatabaseConnectionManager

logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Handles database backup and restore operations."""
    
    def __init__(self, db_manager: DatabaseConnectionManager, 
                 backup_path: str = "data/backups"):
        """
        Initialize database backup system.
        
        Args:
            db_manager: Database connection manager
            backup_path: Path to store backups
        """
        self.db_manager = db_manager
        self.backup_path = backup_path
        
        # Ensure backup directory exists
        os.makedirs(backup_path, exist_ok=True)
        
        logger.info(f"Database backup system initialized at {backup_path}")
    
    def create_backup(self, backup_name: str = None, compress: bool = True) -> Dict[str, Any]:
        """
        Create a database backup.
        
        Args:
            backup_name: Custom backup name (optional)
            compress: Whether to compress the backup
            
        Returns:
            Backup result with details
        """
        result = {
            'success': False,
            'backup_path': None,
            'backup_size': 0,
            'backup_name': None,
            'error': None
        }
        
        try:
            # Generate backup name if not provided
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"quiz_backup_{timestamp}"
            
            # Create backup directory
            backup_dir = os.path.join(self.backup_path, backup_name)
            os.makedirs(backup_dir, exist_ok=True)
            
            # Export database to SQL
            sql_file = os.path.join(backup_dir, "database.sql")
            if not self._export_database_to_sql(sql_file):
                result['error'] = "Failed to export database to SQL"
                return result
            
            # Export data to JSON files
            json_files = self._export_data_to_json(backup_dir)
            if not json_files:
                result['error'] = "Failed to export data to JSON"
                return result
            
            # Create backup metadata
            metadata = {
                'backup_name': backup_name,
                'created_at': datetime.now().isoformat(),
                'database_path': self.db_manager.database_path,
                'files': json_files,
                'compressed': compress
            }
            
            metadata_file = os.path.join(backup_dir, "backup_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Compress backup if requested
            if compress:
                compressed_path = f"{backup_dir}.tar.gz"
                if self._compress_backup(backup_dir, compressed_path):
                    # Remove uncompressed directory
                    shutil.rmtree(backup_dir)
                    backup_dir = compressed_path
                else:
                    result['error'] = "Failed to compress backup"
                    return result
            
            # Calculate backup size
            backup_size = self._get_directory_size(backup_dir)
            
            result.update({
                'success': True,
                'backup_path': backup_dir,
                'backup_size': backup_size,
                'backup_name': backup_name
            })
            
            logger.info(f"Backup created successfully: {backup_name} ({backup_size} bytes)")
            return result
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Failed to create backup: {e}")
            return result
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup directory or compressed file
            
        Returns:
            Restore result with details
        """
        result = {
            'success': False,
            'restored_files': [],
            'error': None
        }
        
        try:
            # Check if backup exists
            if not os.path.exists(backup_path):
                result['error'] = f"Backup not found: {backup_path}"
                return result
            
            # Handle compressed backup
            if backup_path.endswith('.tar.gz'):
                temp_dir = self._decompress_backup(backup_path)
                if not temp_dir:
                    result['error'] = "Failed to decompress backup"
                    return result
                backup_path = temp_dir
            
            # Load backup metadata
            metadata_file = os.path.join(backup_path, "backup_metadata.json")
            if not os.path.exists(metadata_file):
                result['error'] = "Backup metadata not found"
                return result
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Restore database from SQL
            sql_file = os.path.join(backup_path, "database.sql")
            if os.path.exists(sql_file):
                if self._restore_database_from_sql(sql_file):
                    result['restored_files'].append("database.sql")
                else:
                    result['error'] = "Failed to restore database from SQL"
                    return result
            
            # Restore JSON data files
            json_files = metadata.get('files', [])
            for json_file in json_files:
                source_path = os.path.join(backup_path, json_file)
                if os.path.exists(source_path):
                    if self._restore_json_file(json_file, source_path):
                        result['restored_files'].append(json_file)
                    else:
                        logger.warning(f"Failed to restore {json_file}")
            
            result['success'] = True
            logger.info(f"Backup restored successfully: {len(result['restored_files'])} files")
            return result
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Failed to restore backup: {e}")
            return result
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Returns:
            List of backup information
        """
        backups = []
        
        try:
            if not os.path.exists(self.backup_path):
                return backups
            
            for item in os.listdir(self.backup_path):
                item_path = os.path.join(self.backup_path, item)
                
                if os.path.isdir(item_path):
                    # Uncompressed backup
                    metadata_file = os.path.join(item_path, "backup_metadata.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            backups.append({
                                'name': metadata.get('backup_name', item),
                                'path': item_path,
                                'created_at': metadata.get('created_at'),
                                'size': self._get_directory_size(item_path),
                                'compressed': False,
                                'files': metadata.get('files', [])
                            })
                        except Exception as e:
                            logger.warning(f"Failed to read metadata for {item}: {e}")
                
                elif item.endswith('.tar.gz'):
                    # Compressed backup
                    try:
                        # Try to extract metadata from compressed file
                        temp_dir = self._decompress_backup(item_path)
                        if temp_dir:
                            metadata_file = os.path.join(temp_dir, "backup_metadata.json")
                            if os.path.exists(metadata_file):
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                                
                                backups.append({
                                    'name': metadata.get('backup_name', item.replace('.tar.gz', '')),
                                    'path': item_path,
                                    'created_at': metadata.get('created_at'),
                                    'size': os.path.getsize(item_path),
                                    'compressed': True,
                                    'files': metadata.get('files', [])
                                })
                            
                            # Clean up temp directory
                            shutil.rmtree(temp_dir)
                    except Exception as e:
                        logger.warning(f"Failed to read metadata for {item}: {e}")
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        Delete a backup.
        
        Args:
            backup_path: Path to backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            elif os.path.isfile(backup_path):
                os.remove(backup_path)
            else:
                logger.error(f"Backup not found: {backup_path}")
                return False
            
            logger.info(f"Backup deleted: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return False
    
    def _export_database_to_sql(self, sql_file: str) -> bool:
        """Export database to SQL file."""
        try:
            with self.db_manager.get_connection_context() as conn:
                with open(sql_file, 'w', encoding='utf-8') as f:
                    for line in conn.iterdump():
                        f.write(f"{line}\n")
            
            logger.info(f"Database exported to SQL: {sql_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export database to SQL: {e}")
            return False
    
    def _export_data_to_json(self, backup_dir: str) -> List[str]:
        """Export data to JSON files."""
        exported_files = []
        
        try:
            # Export questions
            questions = self._export_table_to_json('questions', backup_dir, 'questions.json')
            if questions:
                exported_files.append('questions.json')
            
            # Export tags
            tags = self._export_table_to_json('tags', backup_dir, 'tags.json')
            if tags:
                exported_files.append('tags.json')
            
            # Export quiz sessions
            sessions = self._export_table_to_json('quiz_sessions', backup_dir, 'quiz_sessions.json')
            if sessions:
                exported_files.append('quiz_sessions.json')
            
            # Export analytics
            analytics = self._export_analytics_to_json(backup_dir, 'analytics.json')
            if analytics:
                exported_files.append('analytics.json')
            
            return exported_files
            
        except Exception as e:
            logger.error(f"Failed to export data to JSON: {e}")
            return []
    
    def _export_table_to_json(self, table_name: str, backup_dir: str, filename: str) -> bool:
        """Export a table to JSON file."""
        try:
            query = f"SELECT * FROM {table_name}"
            rows = self.db_manager.fetch_all(query)
            
            if rows:
                file_path = os.path.join(backup_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(rows, f, indent=2, default=str)
                
                logger.info(f"Exported {len(rows)} rows from {table_name} to {filename}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to export {table_name}: {e}")
            return False
    
    def _export_analytics_to_json(self, backup_dir: str, filename: str) -> bool:
        """Export analytics data to JSON file."""
        try:
            query = "SELECT metric_name, metric_value FROM analytics"
            rows = self.db_manager.fetch_all(query)
            
            if rows:
                # Convert to dictionary format
                analytics_data = {row['metric_name']: json.loads(row['metric_value']) for row in rows}
                
                file_path = os.path.join(backup_dir, filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(analytics_data, f, indent=2)
                
                logger.info(f"Exported {len(analytics_data)} analytics metrics to {filename}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to export analytics: {e}")
            return False
    
    def _restore_database_from_sql(self, sql_file: str) -> bool:
        """Restore database from SQL file."""
        try:
            with self.db_manager.get_connection_context() as conn:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_script = f.read()
                
                conn.executescript(sql_script)
                conn.commit()
            
            logger.info(f"Database restored from SQL: {sql_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore database from SQL: {e}")
            return False
    
    def _restore_json_file(self, filename: str, source_path: str) -> bool:
        """Restore a JSON file to the database."""
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if filename == 'questions.json' and isinstance(data, list):
                return self._restore_questions(data)
            elif filename == 'tags.json' and isinstance(data, list):
                return self._restore_tags(data)
            elif filename == 'quiz_sessions.json' and isinstance(data, list):
                return self._restore_quiz_sessions(data)
            elif filename == 'analytics.json' and isinstance(data, dict):
                return self._restore_analytics(data)
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to restore {filename}: {e}")
            return False
    
    def _restore_questions(self, questions: List[Dict[str, Any]]) -> bool:
        """Restore questions to database."""
        try:
            query = """
                INSERT OR REPLACE INTO questions 
                (id, question_text, question_type, answers, tags, usage_count, 
                 quality_score, created_at, last_modified, created_by, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            batch_data = []
            for question in questions:
                row_data = (
                    question.get('id'),
                    question.get('question_text'),
                    question.get('question_type'),
                    json.dumps(question.get('answers', [])),
                    json.dumps(question.get('tags', [])),
                    question.get('usage_count', 0),
                    question.get('quality_score', 0.0),
                    question.get('created_at'),
                    question.get('last_modified'),
                    question.get('created_by'),
                    question.get('version', 1)
                )
                batch_data.append(row_data)
            
            success = self.db_manager.execute_many_with_retry(query, batch_data)
            if success:
                logger.info(f"Restored {len(questions)} questions")
            return success
            
        except Exception as e:
            logger.error(f"Failed to restore questions: {e}")
            return False
    
    def _restore_tags(self, tags: List[Dict[str, Any]]) -> bool:
        """Restore tags to database."""
        try:
            query = """
                INSERT OR REPLACE INTO tags 
                (id, name, description, color, parent_id, usage_count, last_used,
                 children, aliases, question_count, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            batch_data = []
            for tag in tags:
                row_data = (
                    tag.get('id'),
                    tag.get('name'),
                    tag.get('description'),
                    tag.get('color'),
                    tag.get('parent_id'),
                    tag.get('usage_count', 0),
                    tag.get('last_used'),
                    json.dumps(tag.get('children', [])),
                    json.dumps(tag.get('aliases', [])),
                    tag.get('question_count', 0),
                    tag.get('created_at'),
                    tag.get('created_by')
                )
                batch_data.append(row_data)
            
            success = self.db_manager.execute_many_with_retry(query, batch_data)
            if success:
                logger.info(f"Restored {len(tags)} tags")
            return success
            
        except Exception as e:
            logger.error(f"Failed to restore tags: {e}")
            return False
    
    def _restore_quiz_sessions(self, sessions: List[Dict[str, Any]]) -> bool:
        """Restore quiz sessions to database."""
        try:
            query = """
                INSERT OR REPLACE INTO quiz_sessions 
                (id, questions, answers, score, total_questions, correct_answers,
                 partial_credit, start_time, end_time, duration_seconds, is_complete,
                 is_paused, pause_count, total_pause_time, user_id, quiz_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            batch_data = []
            for session in sessions:
                row_data = (
                    session.get('id'),
                    json.dumps(session.get('questions', [])),
                    json.dumps(session.get('answers', [])),
                    session.get('score'),
                    session.get('total_questions'),
                    session.get('correct_answers'),
                    session.get('partial_credit', 0.0),
                    session.get('start_time'),
                    session.get('end_time'),
                    session.get('duration_seconds'),
                    session.get('is_complete', False),
                    session.get('is_paused', False),
                    session.get('pause_count', 0),
                    session.get('total_pause_time', 0),
                    session.get('user_id'),
                    session.get('quiz_type', 'practice')
                )
                batch_data.append(row_data)
            
            success = self.db_manager.execute_many_with_retry(query, batch_data)
            if success:
                logger.info(f"Restored {len(sessions)} quiz sessions")
            return success
            
        except Exception as e:
            logger.error(f"Failed to restore quiz sessions: {e}")
            return False
    
    def _restore_analytics(self, analytics: Dict[str, Any]) -> bool:
        """Restore analytics to database."""
        try:
            query = """
                INSERT OR REPLACE INTO analytics 
                (metric_name, metric_value, timestamp, session_id, question_id, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            batch_data = []
            for metric_name, metric_value in analytics.items():
                row_data = (
                    metric_name,
                    json.dumps(metric_value),
                    datetime.now().isoformat(),
                    None,  # session_id
                    None,  # question_id
                    None   # user_id
                )
                batch_data.append(row_data)
            
            success = self.db_manager.execute_many_with_retry(query, batch_data)
            if success:
                logger.info(f"Restored {len(analytics)} analytics metrics")
            return success
            
        except Exception as e:
            logger.error(f"Failed to restore analytics: {e}")
            return False
    
    def _compress_backup(self, source_dir: str, dest_file: str) -> bool:
        """Compress backup directory to tar.gz file."""
        try:
            import tarfile
            
            with tarfile.open(dest_file, 'w:gz') as tar:
                tar.add(source_dir, arcname=os.path.basename(source_dir))
            
            logger.info(f"Backup compressed: {dest_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to compress backup: {e}")
            return False
    
    def _decompress_backup(self, compressed_file: str) -> Optional[str]:
        """Decompress backup file to temporary directory."""
        try:
            import tarfile
            
            temp_dir = os.path.join(self.backup_path, f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(temp_dir, exist_ok=True)
            
            with tarfile.open(compressed_file, 'r:gz') as tar:
                tar.extractall(temp_dir)
            
            # Find the extracted directory
            extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            if extracted_dirs:
                return os.path.join(temp_dir, extracted_dirs[0])
            
            return temp_dir
            
        except Exception as e:
            logger.error(f"Failed to decompress backup: {e}")
            return None
    
    def _get_directory_size(self, path: str) -> int:
        """Get total size of directory or file."""
        try:
            if os.path.isfile(path):
                return os.path.getsize(path)
            
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            return total_size
            
        except Exception as e:
            logger.error(f"Failed to get directory size: {e}")
            return 0
