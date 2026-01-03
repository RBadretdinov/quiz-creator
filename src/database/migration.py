"""
Database Migration System

This module handles migration from JSON files to SQLite database
with rollback capability and data integrity validation.
"""

import json
import os
import shutil
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from .connection import DatabaseConnectionManager
from .schema import DatabaseSchema

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Handles migration from JSON to SQLite with rollback support."""
    
    def __init__(self, db_manager: DatabaseConnectionManager, 
                 json_data_path: str = "data"):
        """
        Initialize the migration system.
        
        Args:
            db_manager: Database connection manager
            json_data_path: Path to JSON data files
        """
        self.db_manager = db_manager
        self.json_data_path = json_data_path
        self.backup_path = os.path.join(json_data_path, "backup")
        self.migration_log = []
        
        # Ensure backup directory exists
        os.makedirs(self.backup_path, exist_ok=True)
        
        logger.info("Database migration system initialized")
    
    def validate_json_data(self) -> Dict[str, Any]:
        """
        Validate JSON data integrity before migration.
        
        Returns:
            Validation result with details
        """
        result = {
            'is_valid': True,
            'files_found': [],
            'files_missing': [],
            'data_errors': [],
            'statistics': {}
        }
        
        try:
            # Check for required JSON files
            required_files = ['questions.json', 'tags.json']
            optional_files = ['analytics.json', 'quiz_sessions.json']
            
            for file_name in required_files + optional_files:
                file_path = os.path.join(self.json_data_path, file_name)
                if os.path.exists(file_path):
                    result['files_found'].append(file_name)
                    
                    # Validate JSON structure
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if file_name == 'questions.json':
                            if isinstance(data, list):
                                result['statistics']['questions'] = len(data)
                                # Validate question structure
                                for i, question in enumerate(data):
                                    if not self._validate_question_structure(question):
                                        result['data_errors'].append(f"Invalid question structure at index {i}")
                                        result['is_valid'] = False
                            else:
                                result['data_errors'].append("Questions file should contain a list")
                                result['is_valid'] = False
                        
                        elif file_name == 'tags.json':
                            if isinstance(data, list):
                                result['statistics']['tags'] = len(data)
                                # Validate tag structure
                                for i, tag in enumerate(data):
                                    if not self._validate_tag_structure(tag):
                                        result['data_errors'].append(f"Invalid tag structure at index {i}")
                                        result['is_valid'] = False
                            else:
                                result['data_errors'].append("Tags file should contain a list")
                                result['is_valid'] = False
                        
                        elif file_name == 'analytics.json':
                            if isinstance(data, dict):
                                result['statistics']['analytics'] = len(data)
                            else:
                                result['data_errors'].append("Analytics file should contain a dictionary")
                                result['is_valid'] = False
                        
                        elif file_name == 'quiz_sessions.json':
                            if isinstance(data, list):
                                result['statistics']['sessions'] = len(data)
                            else:
                                result['data_errors'].append("Sessions file should contain a list")
                                result['is_valid'] = False
                    
                    except json.JSONDecodeError as e:
                        result['data_errors'].append(f"Invalid JSON in {file_name}: {e}")
                        result['is_valid'] = False
                    except Exception as e:
                        result['data_errors'].append(f"Error reading {file_name}: {e}")
                        result['is_valid'] = False
                
                elif file_name in required_files:
                    result['files_missing'].append(file_name)
                    result['is_valid'] = False
            
            # Check for missing required files
            if result['files_missing']:
                result['is_valid'] = False
            
            logger.info(f"JSON data validation completed: {result['is_valid']}")
            return result
            
        except Exception as e:
            result['is_valid'] = False
            result['data_errors'].append(f"Validation error: {e}")
            logger.error(f"JSON data validation failed: {e}")
            return result
    
    def _validate_question_structure(self, question: Dict[str, Any]) -> bool:
        """Validate question data structure."""
        required_fields = ['id', 'question_text', 'question_type', 'answers', 'tags']
        return all(field in question for field in required_fields)
    
    def _validate_tag_structure(self, tag: Dict[str, Any]) -> bool:
        """Validate tag data structure."""
        required_fields = ['id', 'name']
        return all(field in tag for field in required_fields)
    
    def create_backup(self) -> bool:
        """
        Create backup of JSON files before migration.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.backup_path, f"backup_{timestamp}")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy JSON files to backup
            json_files = ['questions.json', 'tags.json', 'analytics.json', 'quiz_sessions.json']
            for file_name in json_files:
                source_path = os.path.join(self.json_data_path, file_name)
                if os.path.exists(source_path):
                    dest_path = os.path.join(backup_dir, file_name)
                    shutil.copy2(source_path, dest_path)
                    logger.info(f"Backed up {file_name} to {dest_path}")
            
            self.migration_log.append(f"Backup created at {backup_dir}")
            logger.info(f"Backup created successfully at {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return False
    
    def migrate_questions(self, questions_data: List[Dict[str, Any]]) -> bool:
        """
        Migrate questions from JSON to SQLite.
        
        Args:
            questions_data: List of question dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not questions_data:
                logger.info("No questions to migrate")
                return True
            
            # Prepare batch insert
            insert_query = """
                INSERT OR REPLACE INTO questions 
                (id, question_text, question_type, answers, tags, usage_count, 
                 quality_score, created_at, last_modified, created_by, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            batch_data = []
            for question in questions_data:
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
            
            # Execute batch insert
            success = self.db_manager.execute_many_with_retry(insert_query, batch_data)
            
            if success:
                self.migration_log.append(f"Migrated {len(questions_data)} questions")
                logger.info(f"Successfully migrated {len(questions_data)} questions")
            else:
                logger.error("Failed to migrate questions")
            
            return success
            
        except Exception as e:
            logger.error(f"Error migrating questions: {e}")
            return False
    
    def migrate_tags(self, tags_data: List[Dict[str, Any]]) -> bool:
        """
        Migrate tags from JSON to SQLite.
        
        Args:
            tags_data: List of tag dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not tags_data:
                logger.info("No tags to migrate")
                return True
            
            # Prepare batch insert
            insert_query = """
                INSERT OR REPLACE INTO tags 
                (id, name, description, color, parent_id, usage_count, last_used,
                 children, aliases, question_count, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            batch_data = []
            for tag in tags_data:
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
            
            # Execute batch insert
            success = self.db_manager.execute_many_with_retry(insert_query, batch_data)
            
            if success:
                self.migration_log.append(f"Migrated {len(tags_data)} tags")
                logger.info(f"Successfully migrated {len(tags_data)} tags")
            else:
                logger.error("Failed to migrate tags")
            
            return success
            
        except Exception as e:
            logger.error(f"Error migrating tags: {e}")
            return False
    
    def migrate_analytics(self, analytics_data: Dict[str, Any]) -> bool:
        """
        Migrate analytics data from JSON to SQLite.
        
        Args:
            analytics_data: Analytics dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not analytics_data:
                logger.info("No analytics to migrate")
                return True
            
            # Prepare batch insert
            insert_query = """
                INSERT OR REPLACE INTO analytics 
                (metric_name, metric_value, timestamp, session_id, question_id, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            batch_data = []
            for metric_name, metric_value in analytics_data.items():
                row_data = (
                    metric_name,
                    json.dumps(metric_value),
                    datetime.now().isoformat(),
                    None,  # session_id
                    None,  # question_id
                    None   # user_id
                )
                batch_data.append(row_data)
            
            # Execute batch insert
            success = self.db_manager.execute_many_with_retry(insert_query, batch_data)
            
            if success:
                self.migration_log.append(f"Migrated {len(analytics_data)} analytics metrics")
                logger.info(f"Successfully migrated {len(analytics_data)} analytics metrics")
            else:
                logger.error("Failed to migrate analytics")
            
            return success
            
        except Exception as e:
            logger.error(f"Error migrating analytics: {e}")
            return False
    
    def migrate_quiz_sessions(self, sessions_data: List[Dict[str, Any]]) -> bool:
        """
        Migrate quiz sessions from JSON to SQLite.
        
        Args:
            sessions_data: List of session dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not sessions_data:
                logger.info("No quiz sessions to migrate")
                return True
            
            # Prepare batch insert
            insert_query = """
                INSERT OR REPLACE INTO quiz_sessions 
                (id, questions, answers, score, total_questions, correct_answers,
                 partial_credit, start_time, end_time, duration_seconds, is_complete,
                 is_paused, pause_count, total_pause_time, user_id, quiz_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            batch_data = []
            for session in sessions_data:
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
            
            # Execute batch insert
            success = self.db_manager.execute_many_with_retry(insert_query, batch_data)
            
            if success:
                self.migration_log.append(f"Migrated {len(sessions_data)} quiz sessions")
                logger.info(f"Successfully migrated {len(sessions_data)} quiz sessions")
            else:
                logger.error("Failed to migrate quiz sessions")
            
            return success
            
        except Exception as e:
            logger.error(f"Error migrating quiz sessions: {e}")
            return False
    
    def perform_migration(self) -> Dict[str, Any]:
        """
        Perform complete migration from JSON to SQLite.
        
        Returns:
            Migration result with details
        """
        result = {
            'success': False,
            'steps_completed': [],
            'steps_failed': [],
            'migration_log': [],
            'statistics': {}
        }
        
        try:
            # Step 1: Validate JSON data
            logger.info("Step 1: Validating JSON data...")
            validation = self.validate_json_data()
            if not validation['is_valid']:
                result['steps_failed'].append("JSON data validation failed")
                result['migration_log'].extend(validation['data_errors'])
                return result
            
            result['steps_completed'].append("JSON data validation")
            result['statistics'] = validation['statistics']
            
            # Step 2: Create backup
            logger.info("Step 2: Creating backup...")
            if not self.create_backup():
                result['steps_failed'].append("Backup creation failed")
                return result
            
            result['steps_completed'].append("Backup creation")
            
            # Step 3: Initialize database schema
            logger.info("Step 3: Initializing database schema...")
            if not self._initialize_schema():
                result['steps_failed'].append("Schema initialization failed")
                return result
            
            result['steps_completed'].append("Schema initialization")
            
            # Step 4: Migrate questions
            logger.info("Step 4: Migrating questions...")
            questions_data = self._load_json_file('questions.json')
            if questions_data is not None:
                if self.migrate_questions(questions_data):
                    result['steps_completed'].append("Questions migration")
                else:
                    result['steps_failed'].append("Questions migration failed")
            else:
                result['steps_completed'].append("Questions migration (no data)")
            
            # Step 5: Migrate tags
            logger.info("Step 5: Migrating tags...")
            tags_data = self._load_json_file('tags.json')
            if tags_data is not None:
                if self.migrate_tags(tags_data):
                    result['steps_completed'].append("Tags migration")
                else:
                    result['steps_failed'].append("Tags migration failed")
            else:
                result['steps_completed'].append("Tags migration (no data)")
            
            # Step 6: Migrate analytics
            logger.info("Step 6: Migrating analytics...")
            analytics_data = self._load_json_file('analytics.json')
            if analytics_data is not None:
                if self.migrate_analytics(analytics_data):
                    result['steps_completed'].append("Analytics migration")
                else:
                    result['steps_failed'].append("Analytics migration failed")
            else:
                result['steps_completed'].append("Analytics migration (no data)")
            
            # Step 7: Migrate quiz sessions
            logger.info("Step 7: Migrating quiz sessions...")
            sessions_data = self._load_json_file('quiz_sessions.json')
            if sessions_data is not None:
                if self.migrate_quiz_sessions(sessions_data):
                    result['steps_completed'].append("Quiz sessions migration")
                else:
                    result['steps_failed'].append("Quiz sessions migration failed")
            else:
                result['steps_completed'].append("Quiz sessions migration (no data)")
            
            # Step 8: Update schema version
            logger.info("Step 8: Updating schema version...")
            if self._update_schema_version():
                result['steps_completed'].append("Schema version update")
            else:
                result['steps_failed'].append("Schema version update failed")
            
            # Determine overall success
            result['success'] = len(result['steps_failed']) == 0
            result['migration_log'] = self.migration_log.copy()
            
            if result['success']:
                logger.info("Migration completed successfully")
            else:
                logger.error(f"Migration failed with {len(result['steps_failed'])} failed steps")
            
            return result
            
        except Exception as e:
            result['steps_failed'].append(f"Migration error: {e}")
            logger.error(f"Migration failed with error: {e}")
            return result
    
    def _load_json_file(self, filename: str) -> Optional[Any]:
        """Load JSON file data."""
        try:
            file_path = os.path.join(self.json_data_path, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            return None
    
    def _initialize_schema(self) -> bool:
        """Initialize database schema."""
        try:
            with self.db_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                
                # Execute all schema statements
                for statement in DatabaseSchema.get_all_statements():
                    cursor.execute(statement)
                
                conn.commit()
                logger.info("Database schema initialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            return False
    
    def _update_schema_version(self) -> bool:
        """Update schema version in database."""
        try:
            query = "INSERT OR REPLACE INTO schema_version (version, description) VALUES (?, ?)"
            params = (DatabaseSchema.CURRENT_VERSION, f"Migration completed at {datetime.now().isoformat()}")
            
            success = self.db_manager.execute_with_retry(query, params)
            if success:
                logger.info(f"Schema version updated to {DatabaseSchema.CURRENT_VERSION}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update schema version: {e}")
            return False
    
    def rollback_migration(self, backup_timestamp: str = None) -> bool:
        """
        Rollback migration by restoring from backup.
        
        Args:
            backup_timestamp: Specific backup timestamp to restore from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if backup_timestamp:
                backup_dir = os.path.join(self.backup_path, f"backup_{backup_timestamp}")
            else:
                # Find latest backup
                backup_dirs = [d for d in os.listdir(self.backup_path) if d.startswith('backup_')]
                if not backup_dirs:
                    logger.error("No backup directories found")
                    return False
                backup_dir = os.path.join(self.backup_path, max(backup_dirs))
            
            if not os.path.exists(backup_dir):
                logger.error(f"Backup directory not found: {backup_dir}")
                return False
            
            # Restore JSON files
            json_files = ['questions.json', 'tags.json', 'analytics.json', 'quiz_sessions.json']
            for file_name in json_files:
                backup_file = os.path.join(backup_dir, file_name)
                if os.path.exists(backup_file):
                    dest_file = os.path.join(self.json_data_path, file_name)
                    shutil.copy2(backup_file, dest_file)
                    logger.info(f"Restored {file_name} from backup")
            
            logger.info(f"Migration rollback completed from {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration: {e}")
            return False
