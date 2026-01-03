"""
Performance Optimization System

This module provides comprehensive performance optimization including
caching, memory management, database optimization, and performance monitoring.
"""

import time
import gc
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from pathlib import Path
import json
import sqlite3
from functools import wraps, lru_cache
import weakref

class PerformanceOptimizer:
    """Comprehensive performance optimization system."""
    
    def __init__(self, cache_size: int = 1000, memory_threshold: float = 0.8):
        """Initialize performance optimizer."""
        self.cache_size = cache_size
        self.memory_threshold = memory_threshold
        self.cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        self.performance_metrics = {
            'operations': {},
            'memory_usage': [],
            'response_times': []
        }
        self.optimization_enabled = True
        
        # Memory monitoring
        self.memory_monitor = MemoryMonitor()
        self.gc_optimizer = GarbageCollectionOptimizer()
        
        # Database optimizer
        self.db_optimizer = DatabaseOptimizer()
        
        # File I/O optimizer
        self.io_optimizer = FileIOOptimizer()
    
    def enable_caching(self, func: Callable) -> Callable:
        """Decorator to enable caching for a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.optimization_enabled:
                return func(*args, **kwargs)
            
            # Create cache key
            cache_key = self._create_cache_key(func.__name__, args, kwargs)
            
            # Check cache
            if cache_key in self.cache:
                self.cache_stats['hits'] += 1
                return self.cache[cache_key]['value']
            
            # Cache miss - execute function
            self.cache_stats['misses'] += 1
            result = func(*args, **kwargs)
            
            # Store in cache
            self._store_in_cache(cache_key, result)
            
            return result
        
        return wrapper
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """Optimize memory usage."""
        optimization_results = {
            'before': self._get_memory_usage(),
            'actions_taken': [],
            'after': None
        }
        
        # Force garbage collection
        collected = gc.collect()
        optimization_results['actions_taken'].append(f"Garbage collection: {collected} objects collected")
        
        # Clear cache if memory usage is high
        if self._get_memory_usage()['percentage'] > self.memory_threshold:
            cache_size_before = len(self.cache)
            self._clear_old_cache_entries()
            optimization_results['actions_taken'].append(f"Cache cleanup: {cache_size_before - len(self.cache)} entries removed")
        
        # Optimize garbage collection
        gc_optimization = self.gc_optimizer.optimize()
        optimization_results['actions_taken'].extend(gc_optimization['actions'])
        
        optimization_results['after'] = self._get_memory_usage()
        return optimization_results
    
    def optimize_database_queries(self, db_path: str) -> Dict[str, Any]:
        """Optimize database queries and indexing."""
        return self.db_optimizer.optimize_database(db_path)
    
    def optimize_file_operations(self, file_paths: List[str]) -> Dict[str, Any]:
        """Optimize file I/O operations."""
        return self.io_optimizer.optimize_files(file_paths)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            'cache_stats': self.cache_stats.copy(),
            'memory_usage': self._get_memory_usage(),
            'performance_metrics': self.performance_metrics.copy(),
            'optimization_status': {
                'caching_enabled': self.optimization_enabled,
                'cache_size': len(self.cache),
                'max_cache_size': self.cache_size
            }
        }
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
        self.cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def set_optimization_level(self, level: str) -> None:
        """Set optimization level (low, medium, high)."""
        if level == 'low':
            self.cache_size = 100
            self.memory_threshold = 0.9
        elif level == 'medium':
            self.cache_size = 500
            self.memory_threshold = 0.8
        elif level == 'high':
            self.cache_size = 1000
            self.memory_threshold = 0.7
        
        # Adjust cache size if needed
        if len(self.cache) > self.cache_size:
            self._clear_old_cache_entries()
    
    def _create_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Create a cache key for function arguments."""
        key_parts = [func_name]
        key_parts.extend(str(arg) for arg in args)
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return "|".join(key_parts)
    
    def _store_in_cache(self, key: str, value: Any) -> None:
        """Store value in cache with size management."""
        if len(self.cache) >= self.cache_size:
            self._evict_oldest_entry()
        
        self.cache[key] = {
            'value': value,
            'timestamp': time.time(),
            'access_count': 0
        }
    
    def _evict_oldest_entry(self) -> None:
        """Evict the oldest cache entry."""
        if not self.cache:
            return
        
        oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
        del self.cache[oldest_key]
        self.cache_stats['evictions'] += 1
    
    def _clear_old_cache_entries(self) -> None:
        """Clear old cache entries to free memory."""
        current_time = time.time()
        max_age = 3600  # 1 hour
        
        keys_to_remove = [
            key for key, data in self.cache.items()
            if current_time - data['timestamp'] > max_age
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        system_memory = psutil.virtual_memory()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percentage': process.memory_percent(),
            'system_available_mb': system_memory.available / 1024 / 1024,
            'system_percentage': system_memory.percent
        }


class MemoryMonitor:
    """Memory usage monitoring and optimization."""
    
    def __init__(self):
        """Initialize memory monitor."""
        self.memory_history = []
        self.peak_memory = 0
        self.monitoring_enabled = True
    
    def start_monitoring(self, interval: int = 30) -> None:
        """Start memory monitoring in background thread."""
        if not self.monitoring_enabled:
            return
        
        def monitor():
            while self.monitoring_enabled:
                self._record_memory_usage()
                time.sleep(interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop memory monitoring."""
        self.monitoring_enabled = False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        if not self.memory_history:
            return {'error': 'No memory data available'}
        
        recent_memory = [entry['rss_mb'] for entry in self.memory_history[-10:]]
        
        return {
            'current_mb': recent_memory[-1] if recent_memory else 0,
            'average_mb': sum(recent_memory) / len(recent_memory) if recent_memory else 0,
            'peak_mb': self.peak_memory,
            'trend': 'increasing' if len(recent_memory) > 1 and recent_memory[-1] > recent_memory[0] else 'stable'
        }
    
    def _record_memory_usage(self) -> None:
        """Record current memory usage."""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percentage': process.memory_percent()
        }
        
        self.memory_history.append(entry)
        self.peak_memory = max(self.peak_memory, entry['rss_mb'])
        
        # Keep only last 100 entries
        if len(self.memory_history) > 100:
            self.memory_history = self.memory_history[-100:]


class GarbageCollectionOptimizer:
    """Garbage collection optimization."""
    
    def __init__(self):
        """Initialize GC optimizer."""
        self.gc_stats = {
            'collections': 0,
            'objects_collected': 0,
            'time_spent': 0
        }
    
    def optimize(self) -> Dict[str, Any]:
        """Optimize garbage collection."""
        start_time = time.time()
        
        # Get current GC counts
        before_counts = gc.get_count()
        
        # Force collection
        collected = gc.collect()
        
        # Get new counts
        after_counts = gc.get_count()
        
        end_time = time.time()
        
        # Update stats
        self.gc_stats['collections'] += 1
        self.gc_stats['objects_collected'] += collected
        self.gc_stats['time_spent'] += (end_time - start_time)
        
        return {
            'objects_collected': collected,
            'time_spent': end_time - start_time,
            'before_counts': before_counts,
            'after_counts': after_counts,
            'actions': [
                f"Collected {collected} objects",
                f"Time spent: {(end_time - start_time):.3f}s"
            ]
        }
    
    def get_gc_stats(self) -> Dict[str, Any]:
        """Get garbage collection statistics."""
        return {
            'current_counts': gc.get_count(),
            'stats': self.gc_stats.copy(),
            'thresholds': gc.get_threshold()
        }


class DatabaseOptimizer:
    """Database performance optimization."""
    
    def __init__(self):
        """Initialize database optimizer."""
        self.optimization_results = {}
    
    def optimize_database(self, db_path: str) -> Dict[str, Any]:
        """Optimize database performance."""
        results = {
            'database': db_path,
            'optimizations': [],
            'performance_improvements': {}
        }
        
        try:
            with sqlite3.connect(db_path) as conn:
                # Analyze database
                analysis_results = self._analyze_database(conn)
                results['analysis'] = analysis_results
                
                # Create indexes if needed
                indexes_created = self._create_indexes(conn)
                results['optimizations'].extend(indexes_created)
                
                # Optimize queries
                query_optimizations = self._optimize_queries(conn)
                results['optimizations'].extend(query_optimizations)
                
                # Vacuum database
                self._vacuum_database(conn)
                results['optimizations'].append("Database vacuumed")
                
                # Update statistics
                self._update_statistics(conn)
                results['optimizations'].append("Statistics updated")
        
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def _analyze_database(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Analyze database structure and performance."""
        cursor = conn.cursor()
        
        # Get table information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get index information
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        # Get database size
        cursor.execute("PRAGMA page_count")
        page_count = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA page_size")
        page_size = cursor.fetchone()[0]
        
        return {
            'tables': tables,
            'indexes': indexes,
            'size_mb': (page_count * page_size) / (1024 * 1024),
            'page_count': page_count,
            'page_size': page_size
        }
    
    def _create_indexes(self, conn: sqlite3.Connection) -> List[str]:
        """Create performance indexes."""
        optimizations = []
        cursor = conn.cursor()
        
        # Common indexes for quiz application
        indexes_to_create = [
            ("idx_questions_type", "CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type)"),
            ("idx_questions_created", "CREATE INDEX IF NOT EXISTS idx_questions_created ON questions(created_at)"),
            ("idx_tags_name", "CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name)"),
            ("idx_sessions_user", "CREATE INDEX IF NOT EXISTS idx_sessions_user ON quiz_sessions(user_id)"),
            ("idx_sessions_date", "CREATE INDEX IF NOT EXISTS idx_sessions_date ON quiz_sessions(start_time)")
        ]
        
        for index_name, sql in indexes_to_create:
            try:
                cursor.execute(sql)
                optimizations.append(f"Created index: {index_name}")
            except sqlite3.Error as e:
                optimizations.append(f"Failed to create index {index_name}: {e}")
        
        conn.commit()
        return optimizations
    
    def _optimize_queries(self, conn: sqlite3.Connection) -> List[str]:
        """Optimize database queries."""
        optimizations = []
        cursor = conn.cursor()
        
        # Enable query optimization
        cursor.execute("PRAGMA optimize")
        optimizations.append("Query optimization enabled")
        
        # Set cache size
        cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache
        optimizations.append("Cache size increased to 64MB")
        
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode = WAL")
        optimizations.append("WAL mode enabled")
        
        # Set synchronous mode
        cursor.execute("PRAGMA synchronous = NORMAL")
        optimizations.append("Synchronous mode set to NORMAL")
        
        return optimizations
    
    def _vacuum_database(self, conn: sqlite3.Connection) -> None:
        """Vacuum database to reclaim space."""
        cursor = conn.cursor()
        cursor.execute("VACUUM")
    
    def _update_statistics(self, conn: sqlite3.Connection) -> None:
        """Update database statistics."""
        cursor = conn.cursor()
        cursor.execute("ANALYZE")


class FileIOOptimizer:
    """File I/O performance optimization."""
    
    def __init__(self):
        """Initialize file I/O optimizer."""
        self.optimization_results = {}
    
    def optimize_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Optimize file I/O operations."""
        results = {
            'files_processed': len(file_paths),
            'optimizations': [],
            'performance_improvements': {}
        }
        
        for file_path in file_paths:
            try:
                file_results = self._optimize_single_file(file_path)
                results['optimizations'].extend(file_results)
            except Exception as e:
                results['optimizations'].append(f"Error optimizing {file_path}: {e}")
        
        return results
    
    def _optimize_single_file(self, file_path: str) -> List[str]:
        """Optimize a single file."""
        optimizations = []
        path = Path(file_path)
        
        if not path.exists():
            return [f"File {file_path} does not exist"]
        
        # Check file size
        file_size = path.stat().st_size
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            optimizations.append(f"Large file detected: {file_size / (1024*1024):.1f}MB")
        
        # Check if file is frequently accessed
        access_time = path.stat().st_atime
        current_time = time.time()
        days_since_access = (current_time - access_time) / (24 * 3600)
        
        if days_since_access > 30:
            optimizations.append(f"File not accessed in {days_since_access:.0f} days")
        
        return optimizations


class PerformanceProfiler:
    """Performance profiling and analysis."""
    
    def __init__(self):
        """Initialize performance profiler."""
        self.profiles = {}
        self.active_profiles = {}
    
    def start_profile(self, name: str) -> None:
        """Start profiling an operation."""
        self.active_profiles[name] = {
            'start_time': time.time(),
            'start_memory': self._get_memory_usage()
        }
    
    def end_profile(self, name: str) -> Dict[str, Any]:
        """End profiling and return results."""
        if name not in self.active_profiles:
            return {'error': f'Profile {name} not found'}
        
        profile_data = self.active_profiles[name]
        end_time = time.time()
        end_memory = self._get_memory_usage()
        
        result = {
            'name': name,
            'duration': end_time - profile_data['start_time'],
            'memory_delta': end_memory - profile_data['start_memory'],
            'start_time': profile_data['start_time'],
            'end_time': end_time
        }
        
        # Store profile
        self.profiles[name] = result
        
        # Clean up
        del self.active_profiles[name]
        
        return result
    
    def get_profile_summary(self) -> Dict[str, Any]:
        """Get summary of all profiles."""
        if not self.profiles:
            return {'message': 'No profiles available'}
        
        durations = [profile['duration'] for profile in self.profiles.values()]
        memory_deltas = [profile['memory_delta'] for profile in self.profiles.values()]
        
        return {
            'total_profiles': len(self.profiles),
            'average_duration': sum(durations) / len(durations),
            'max_duration': max(durations),
            'min_duration': min(durations),
            'average_memory_delta': sum(memory_deltas) / len(memory_deltas),
            'profiles': self.profiles
        }
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

def optimize_performance(func: Callable) -> Callable:
    """Decorator to optimize function performance."""
    return performance_optimizer.enable_caching(func)

def profile_operation(name: str):
    """Context manager for profiling operations."""
    class ProfileContext:
        def __init__(self, profiler_name: str):
            self.name = profiler_name
            self.profiler = PerformanceProfiler()
        
        def __enter__(self):
            self.profiler.start_profile(self.name)
            return self.profiler
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            return self.profiler.end_profile(self.name)
    
    return ProfileContext(name)
