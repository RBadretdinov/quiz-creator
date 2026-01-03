"""
Database Connection Manager

This module provides database connection management with connection pooling,
error handling, and retry logic for SQLite operations.
"""

import sqlite3
import threading
import time
import logging
from typing import Optional, Dict, Any, List, Callable
from contextlib import contextmanager
from pathlib import Path
import os

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """Manages SQLite database connections with pooling and error handling."""
    
    def __init__(self, database_path: str = "data/quiz.db", 
                 max_connections: int = 10, 
                 connection_timeout: int = 30):
        """
        Initialize the database connection manager.
        
        Args:
            database_path: Path to SQLite database file
            max_connections: Maximum number of concurrent connections
            connection_timeout: Connection timeout in seconds
        """
        self.database_path = database_path
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self._connections: List[sqlite3.Connection] = []
        self._lock = threading.Lock()
        self._initialized = False
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(database_path), exist_ok=True)
        
        logger.info(f"Database connection manager initialized for {database_path}")
    
    def initialize(self) -> bool:
        """
        Initialize the database connection pool.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self._lock:
                if self._initialized:
                    return True
                
                # Create initial connections
                for _ in range(min(3, self.max_connections)):
                    conn = self._create_connection()
                    if conn:
                        self._connections.append(conn)
                
                self._initialized = True
                logger.info(f"Database connection pool initialized with {len(self._connections)} connections")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            return False
    
    def _create_connection(self) -> Optional[sqlite3.Connection]:
        """Create a new database connection."""
        try:
            conn = sqlite3.connect(
                self.database_path,
                timeout=self.connection_timeout,
                check_same_thread=False
            )
            
            # Configure connection
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = 10000")
            conn.execute("PRAGMA temp_store = MEMORY")
            
            return conn
            
        except Exception as e:
            logger.error(f"Failed to create database connection: {e}")
            return None
    
    def get_connection(self) -> Optional[sqlite3.Connection]:
        """
        Get a database connection from the pool.
        
        Returns:
            Database connection or None if failed
        """
        try:
            with self._lock:
                # Try to get existing connection
                if self._connections:
                    return self._connections.pop()
                
                # Create new connection if under limit
                if len(self._connections) < self.max_connections:
                    conn = self._create_connection()
                    if conn:
                        return conn
                
                # Wait for connection to become available
                start_time = time.time()
                while time.time() - start_time < self.connection_timeout:
                    if self._connections:
                        return self._connections.pop()
                    time.sleep(0.1)
                
                logger.warning("Connection timeout - no connections available")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get database connection: {e}")
            return None
    
    def return_connection(self, conn: sqlite3.Connection) -> None:
        """
        Return a connection to the pool.
        
        Args:
            conn: Database connection to return
        """
        try:
            if conn is None:
                return
            
            # Check if connection is still valid
            try:
                conn.execute("SELECT 1")
            except sqlite3.Error:
                # Connection is invalid, don't return it
                conn.close()
                return
            
            with self._lock:
                if len(self._connections) < self.max_connections:
                    self._connections.append(conn)
                else:
                    conn.close()
                    
        except Exception as e:
            logger.error(f"Failed to return database connection: {e}")
            if conn:
                conn.close()
    
    @contextmanager
    def get_connection_context(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = self.get_connection()
            if conn is None:
                raise sqlite3.Error("Failed to get database connection")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                self.return_connection(conn)
    
    def execute_with_retry(self, query: str, params: tuple = (), 
                          max_retries: int = 3) -> Optional[sqlite3.Cursor]:
        """
        Execute a query with retry logic.
        
        Args:
            query: SQL query to execute
            params: Query parameters
            max_retries: Maximum number of retry attempts
            
        Returns:
            Query cursor or None if failed
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                with self.get_connection_context() as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor
                    
            except sqlite3.Error as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Database query failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Database query failed after {max_retries + 1} attempts: {e}")
        
        return None
    
    def execute_many_with_retry(self, query: str, params_list: List[tuple], 
                               max_retries: int = 3) -> bool:
        """
        Execute a query multiple times with retry logic.
        
        Args:
            query: SQL query to execute
            params_list: List of parameter tuples
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if successful, False otherwise
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                with self.get_connection_context() as conn:
                    cursor = conn.cursor()
                    cursor.executemany(query, params_list)
                    conn.commit()
                    return True
                    
            except sqlite3.Error as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = 2 ** attempt
                    logger.warning(f"Database batch query failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Database batch query failed after {max_retries + 1} attempts: {e}")
        
        return False
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Fetch one row from the database.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Row as dictionary or None if not found
        """
        try:
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                row = cursor.fetchone()
                return dict(row) if row else None
                
        except Exception as e:
            logger.error(f"Failed to fetch one row: {e}")
            return None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Fetch all rows from the database.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of rows as dictionaries
        """
        try:
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to fetch all rows: {e}")
            return []
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        with self._lock:
            return {
                'total_connections': len(self._connections),
                'max_connections': self.max_connections,
                'available_connections': len(self._connections),
                'database_path': self.database_path,
                'initialized': self._initialized
            }
    
    def close_all_connections(self) -> None:
        """Close all database connections."""
        with self._lock:
            for conn in self._connections:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            self._connections.clear()
            self._initialized = False
            logger.info("All database connections closed")
    
    def vacuum_database(self) -> bool:
        """
        Vacuum the database to reclaim space and optimize performance.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection_context() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuum completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            return False
    
    def analyze_database(self) -> bool:
        """
        Analyze the database to update query optimizer statistics.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection_context() as conn:
                conn.execute("ANALYZE")
                logger.info("Database analysis completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to analyze database: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        try:
            with self.get_connection_context() as conn:
                cursor = conn.cursor()
                
                # Get database size
                cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
                size_result = cursor.fetchone()
                db_size = size_result[0] if size_result else 0
                
                # Get table counts
                table_counts = {}
                for table in ['questions', 'tags', 'quiz_sessions', 'question_history', 'analytics']:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    table_counts[table] = count
                
                return {
                    'database_path': self.database_path,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'table_counts': table_counts,
                    'connection_stats': self.get_connection_stats()
                }
                
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {'error': str(e)}
