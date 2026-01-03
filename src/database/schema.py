"""
Database Schema

This module defines the SQLite database schema for the quiz application
with proper indexes, constraints, and relationships.
"""

from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseSchema:
    """Manages database schema definitions and migrations."""
    
    CURRENT_VERSION = 1
    
    # Table creation SQL
    TABLES = {
        'questions': """
            CREATE TABLE IF NOT EXISTS questions (
                id TEXT PRIMARY KEY,
                question_text TEXT NOT NULL,
                question_type TEXT NOT NULL CHECK (question_type IN ('multiple_choice', 'true_false', 'select_all')),
                answers TEXT NOT NULL, -- JSON array
                tags TEXT NOT NULL,    -- JSON array
                usage_count INTEGER DEFAULT 0,
                quality_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                version INTEGER DEFAULT 1
            )
        """,
        
        'tags': """
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT,
                parent_id TEXT,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP,
                children TEXT, -- JSON array of child tag IDs
                aliases TEXT,  -- JSON array of aliases
                question_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                FOREIGN KEY (parent_id) REFERENCES tags(id)
            )
        """,
        
        'quiz_sessions': """
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id TEXT PRIMARY KEY,
                questions TEXT NOT NULL, -- JSON array
                answers TEXT NOT NULL,   -- JSON array
                score REAL,
                total_questions INTEGER,
                correct_answers INTEGER,
                partial_credit REAL DEFAULT 0.0,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                is_complete BOOLEAN DEFAULT FALSE,
                is_paused BOOLEAN DEFAULT FALSE,
                pause_count INTEGER DEFAULT 0,
                total_pause_time INTEGER DEFAULT 0,
                user_id TEXT,
                quiz_type TEXT DEFAULT 'practice'
            )
        """,
        
        'question_history': """
            CREATE TABLE IF NOT EXISTS question_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id TEXT NOT NULL,
                action TEXT NOT NULL, -- 'created', 'modified', 'deleted'
                old_data TEXT, -- JSON of previous state
                new_data TEXT, -- JSON of new state
                change_description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
        """,
        
        'analytics': """
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value TEXT NOT NULL, -- JSON data
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                question_id TEXT,
                user_id TEXT
            )
        """,
        
        'schema_version': """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """
    }
    
    # Indexes for performance optimization
    INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type)",
        "CREATE INDEX IF NOT EXISTS idx_questions_tags ON questions(tags)",
        "CREATE INDEX IF NOT EXISTS idx_questions_created ON questions(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_questions_usage ON questions(usage_count)",
        "CREATE INDEX IF NOT EXISTS idx_questions_quality ON questions(quality_score)",
        "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)",
        "CREATE INDEX IF NOT EXISTS idx_tags_parent ON tags(parent_id)",
        "CREATE INDEX IF NOT EXISTS idx_tags_usage ON tags(usage_count)",
        "CREATE INDEX IF NOT EXISTS idx_quiz_sessions_user ON quiz_sessions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_quiz_sessions_date ON quiz_sessions(start_time)",
        "CREATE INDEX IF NOT EXISTS idx_quiz_sessions_complete ON quiz_sessions(is_complete)",
        "CREATE INDEX IF NOT EXISTS idx_question_history_question ON question_history(question_id)",
        "CREATE INDEX IF NOT EXISTS idx_question_history_timestamp ON question_history(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric_name)",
        "CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)"
    ]
    
    # Triggers for automatic updates
    TRIGGERS = [
        """
        CREATE TRIGGER IF NOT EXISTS update_question_modified
        AFTER UPDATE ON questions
        BEGIN
            UPDATE questions SET last_modified = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
        """,
        
        """
        CREATE TRIGGER IF NOT EXISTS update_tag_usage
        AFTER UPDATE OF usage_count ON tags
        BEGIN
            UPDATE tags SET last_used = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
        """
    ]
    
    @classmethod
    def get_create_statements(cls) -> List[str]:
        """Get all table creation statements."""
        return list(cls.TABLES.values())
    
    @classmethod
    def get_index_statements(cls) -> List[str]:
        """Get all index creation statements."""
        return cls.INDEXES.copy()
    
    @classmethod
    def get_trigger_statements(cls) -> List[str]:
        """Get all trigger creation statements."""
        return cls.TRIGGERS.copy()
    
    @classmethod
    def get_all_statements(cls) -> List[str]:
        """Get all SQL statements for complete schema setup."""
        statements = []
        statements.extend(cls.get_create_statements())
        statements.extend(cls.get_index_statements())
        statements.extend(cls.get_trigger_statements())
        return statements
    
    @classmethod
    def get_schema_info(cls) -> Dict[str, Any]:
        """Get schema information and statistics."""
        return {
            'version': cls.CURRENT_VERSION,
            'tables': list(cls.TABLES.keys()),
            'indexes': len(cls.INDEXES),
            'triggers': len(cls.TRIGGERS),
            'total_statements': len(cls.get_all_statements())
        }
    
    @classmethod
    def validate_schema(cls, connection) -> Dict[str, Any]:
        """
        Validate that the current schema matches the expected schema.
        
        Args:
            connection: Database connection
            
        Returns:
            Validation result with details
        """
        result = {
            'is_valid': True,
            'missing_tables': [],
            'missing_indexes': [],
            'missing_triggers': [],
            'errors': []
        }
        
        try:
            cursor = connection.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            expected_tables = set(cls.TABLES.keys())
            
            missing_tables = expected_tables - existing_tables
            if missing_tables:
                result['missing_tables'] = list(missing_tables)
                result['is_valid'] = False
            
            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
            existing_indexes = {row[0] for row in cursor.fetchall()}
            expected_indexes = {
                'idx_questions_type', 'idx_questions_tags', 'idx_questions_created',
                'idx_questions_usage', 'idx_questions_quality', 'idx_tags_name',
                'idx_tags_parent', 'idx_tags_usage', 'idx_quiz_sessions_user',
                'idx_quiz_sessions_date', 'idx_quiz_sessions_complete',
                'idx_question_history_question', 'idx_question_history_timestamp',
                'idx_analytics_metric', 'idx_analytics_timestamp'
            }
            
            missing_indexes = expected_indexes - existing_indexes
            if missing_indexes:
                result['missing_indexes'] = list(missing_indexes)
                result['is_valid'] = False
            
            # Check triggers
            cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
            existing_triggers = {row[0] for row in cursor.fetchall()}
            expected_triggers = {'update_question_modified', 'update_tag_usage'}
            
            missing_triggers = expected_triggers - existing_triggers
            if missing_triggers:
                result['missing_triggers'] = list(missing_triggers)
                result['is_valid'] = False
            
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(str(e))
            logger.error(f"Schema validation error: {e}")
        
        return result
