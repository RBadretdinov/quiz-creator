"""
Database Manager

This module provides a unified interface for all database operations,
integrating connection management, data access, migration, backup, and maintenance.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from database import (
    DatabaseConnectionManager,
    DatabaseSchema,
    DatabaseMigration,
    QuestionDataAccess,
    TagDataAccess,
    DatabaseBackup,
    DatabaseMaintenance
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Unified database manager for all SQLite operations."""
    
    def __init__(self, database_path: str = "data/quiz.db", 
                 json_data_path: str = "data"):
        """
        Initialize the database manager.
        
        Args:
            database_path: Path to SQLite database file
            json_data_path: Path to JSON data files
        """
        self.database_path = database_path
        self.json_data_path = json_data_path
        
        # Initialize components
        self.connection_manager = DatabaseConnectionManager(database_path)
        self.schema = DatabaseSchema()
        self.migration = DatabaseMigration(self.connection_manager, json_data_path)
        self.backup = DatabaseBackup(self.connection_manager)
        self.maintenance = DatabaseMaintenance(self.connection_manager)
        
        # Initialize data access layers
        self.question_access = QuestionDataAccess(self.connection_manager)
        self.tag_access = TagDataAccess(self.connection_manager)
        
        # State tracking
        self._initialized = False
        self._migrated = False
        
        logger.info("Database manager initialized")
    
    def initialize(self) -> bool:
        """
        Initialize the database system.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Initialize connection pool
            if not self.connection_manager.initialize():
                logger.error("Failed to initialize connection pool")
                return False
            
            # Check if database exists and has data
            if self._database_exists_and_has_data():
                logger.info("Database exists with data, skipping migration")
                self._migrated = True
            else:
                # Check if JSON data exists for migration
                if self._json_data_exists():
                    logger.info("JSON data found, performing migration...")
                    migration_result = self.migration.perform_migration()
                    if migration_result['success']:
                        self._migrated = True
                        logger.info("Migration completed successfully")
                    else:
                        logger.error(f"Migration failed: {migration_result.get('steps_failed', [])}")
                        return False
                else:
                    # Create empty database with schema
                    logger.info("Creating new database with schema...")
                    if not self._create_empty_database():
                        logger.error("Failed to create empty database")
                        return False
                    self._migrated = True
            
            self._initialized = True
            logger.info("Database manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            return False
    
    def _database_exists_and_has_data(self) -> bool:
        """Check if database exists and contains data."""
        try:
            if not Path(self.database_path).exists():
                return False
            
            # Check if database has tables and data
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                
                # Check if tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                
                if not tables:
                    return False
                
                # Check if questions table has data
                cursor.execute("SELECT COUNT(*) FROM questions")
                question_count = cursor.fetchone()[0]
                
                return question_count > 0
                
        except Exception as e:
            logger.error(f"Failed to check database existence: {e}")
            return False
    
    def _json_data_exists(self) -> bool:
        """Check if JSON data files exist."""
        try:
            json_files = ['questions.json', 'tags.json']
            for file_name in json_files:
                file_path = Path(self.json_data_path) / file_name
                if not file_path.exists():
                    return False
            return True
        except Exception as e:
            logger.error(f"Failed to check JSON data existence: {e}")
            return False
    
    def _create_empty_database(self) -> bool:
        """Create empty database with schema."""
        try:
            with self.connection_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                
                # Execute all schema statements
                for statement in self.schema.get_all_statements():
                    cursor.execute(statement)
                
                # Insert initial schema version
                cursor.execute(
                    "INSERT OR REPLACE INTO schema_version (version, description) VALUES (?, ?)",
                    (self.schema.CURRENT_VERSION, "Initial database creation")
                )
                
                conn.commit()
                logger.info("Empty database created with schema")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create empty database: {e}")
            return False
    
    # Question operations
    def create_question(self, question_data: Dict[str, Any]) -> Optional[str]:
        """Create a new question."""
        return self.question_access.create_question(question_data)
    
    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get a question by ID."""
        return self.question_access.get_question_by_id(question_id)
    
    def get_all_questions(self, limit: int = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all questions with optional pagination."""
        return self.question_access.get_all_questions(limit, offset)
    
    def update_question(self, question_id: str, question_data: Dict[str, Any]) -> bool:
        """Update a question."""
        return self.question_access.update_question(question_id, question_data)
    
    def delete_question(self, question_id: str) -> bool:
        """Delete a question."""
        return self.question_access.delete_question(question_id)
    
    def search_questions(self, search_term: str, question_type: str = None, 
                        tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search questions with filters."""
        return self.question_access.search_questions(search_term, question_type, tags)
    
    def get_questions_by_type(self, question_type: str) -> List[Dict[str, Any]]:
        """Get questions by type."""
        return self.question_access.get_questions_by_type(question_type)
    
    def increment_question_usage(self, question_id: str) -> bool:
        """Increment usage count for a question."""
        return self.question_access.increment_usage_count(question_id)
    
    def get_question_statistics(self) -> Dict[str, Any]:
        """Get question statistics."""
        return self.question_access.get_question_statistics()
    
    # Tag operations
    def create_tag(self, tag_data: Dict[str, Any]) -> Optional[str]:
        """Create a new tag."""
        return self.tag_access.create_tag(tag_data)
    
    def get_tag(self, tag_id: str) -> Optional[Dict[str, Any]]:
        """Get a tag by ID."""
        return self.tag_access.get_tag_by_id(tag_id)
    
    def get_tag_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a tag by name."""
        return self.tag_access.get_tag_by_name(name)
    
    def get_all_tags(self) -> List[Dict[str, Any]]:
        """Get all tags."""
        return self.tag_access.get_all_tags()
    
    def update_tag(self, tag_id: str, tag_data: Dict[str, Any]) -> bool:
        """Update a tag."""
        return self.tag_access.update_tag(tag_id, tag_data)
    
    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag."""
        return self.tag_access.delete_tag(tag_id)
    
    def search_tags(self, search_term: str) -> List[Dict[str, Any]]:
        """Search tags by name or description."""
        return self.tag_access.search_tags(search_term)
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """Get tag statistics."""
        return self.tag_access.get_tag_statistics()
    
    # Database management operations
    def create_backup(self, backup_name: str = None, compress: bool = True) -> Dict[str, Any]:
        """Create a database backup."""
        return self.backup.create_backup(backup_name, compress)
    
    def restore_backup(self, backup_path: str) -> Dict[str, Any]:
        """Restore database from backup."""
        return self.backup.restore_backup(backup_path)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups."""
        return self.backup.list_backups()
    
    def delete_backup(self, backup_path: str) -> bool:
        """Delete a backup."""
        return self.backup.delete_backup(backup_path)
    
    def perform_maintenance(self) -> Dict[str, Any]:
        """Perform database maintenance."""
        return self.maintenance.perform_maintenance()
    
    def get_database_health_score(self) -> Dict[str, Any]:
        """Get database health score."""
        return self.maintenance.get_database_health_score()
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        return self.connection_manager.get_database_info()
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate database schema."""
        try:
            with self.connection_manager.get_connection_context() as conn:
                return self.schema.validate_schema(conn)
        except Exception as e:
            logger.error(f"Failed to validate schema: {e}")
            return {'is_valid': False, 'errors': [str(e)]}
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return self.connection_manager.get_connection_stats()
    
    def close(self) -> None:
        """Close all database connections."""
        self.connection_manager.close_all_connections()
        self._initialized = False
        logger.info("Database manager closed")
    
    def is_initialized(self) -> bool:
        """Check if database manager is initialized."""
        return self._initialized
    
    def is_migrated(self) -> bool:
        """Check if database has been migrated from JSON."""
        return self._migrated
    
    def get_status(self) -> Dict[str, Any]:
        """Get database manager status."""
        return {
            'initialized': self._initialized,
            'migrated': self._migrated,
            'database_path': self.database_path,
            'json_data_path': self.json_data_path,
            'connection_stats': self.get_connection_stats(),
            'database_info': self.get_database_info() if self._initialized else {}
        }
