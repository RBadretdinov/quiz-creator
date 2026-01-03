"""
Database Package

This package provides SQLite database integration for the quiz application
including schema management, connection pooling, data access, migration,
backup/restore, and maintenance utilities.
"""

from .connection import DatabaseConnectionManager
from .schema import DatabaseSchema
from .migration import DatabaseMigration
from .data_access import QuestionDataAccess, TagDataAccess
from .backup import DatabaseBackup
from .maintenance import DatabaseMaintenance

__all__ = [
    'DatabaseConnectionManager',
    'DatabaseSchema', 
    'DatabaseMigration',
    'QuestionDataAccess',
    'TagDataAccess',
    'DatabaseBackup',
    'DatabaseMaintenance'
]
