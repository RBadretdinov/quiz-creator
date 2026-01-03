"""
Comprehensive Test Suite for Phase 5.3: Performance Optimization

This module tests the performance optimization, caching, and monitoring systems
implemented in Phase 5.3.
"""

import unittest
import sys
import os
import tempfile
import shutil
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from performance_optimizer import (
    PerformanceOptimizer, MemoryMonitor, GarbageCollectionOptimizer,
    DatabaseOptimizer, FileIOOptimizer, PerformanceProfiler,
    performance_optimizer, optimize_performance, profile_operation
)
from caching_system import (
    IntelligentCache, QuestionCache, TagCache, AnalyticsCache,
    CacheManager, cache_manager, cached
)

class TestPerformanceOptimizer(unittest.TestCase):
    """Test performance optimization system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.optimizer = PerformanceOptimizer(cache_size=100, memory_threshold=0.8)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.cache_size, 100)
        self.assertEqual(self.optimizer.memory_threshold, 0.8)
        self.assertTrue(self.optimizer.optimization_enabled)
    
    def test_caching_decorator(self):
        """Test caching decorator."""
        call_count = 0
        
        @self.optimizer.enable_caching
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = test_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = test_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increment
        
        # Different arguments should execute function
        result3 = test_function(3)
        self.assertEqual(result3, 6)
        self.assertEqual(call_count, 2)
    
    def test_memory_optimization(self):
        """Test memory optimization."""
        # Create some objects to use memory
        large_list = [i for i in range(10000)]
        
        # Run memory optimization
        results = self.optimizer.optimize_memory_usage()
        
        self.assertIn('before', results)
        self.assertIn('after', results)
        self.assertIn('actions_taken', results)
        self.assertIsInstance(results['actions_taken'], list)
    
    def test_database_optimization(self):
        """Test database optimization."""
        # Create test database
        db_path = os.path.join(self.temp_dir, 'test.db')
        
        # Create simple database
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (name) VALUES ('test1'), ('test2')")
            conn.commit()
        
        # Test optimization
        results = self.optimizer.optimize_database_queries(db_path)
        
        self.assertIn('database', results)
        self.assertIn('optimizations', results)
        self.assertIsInstance(results['optimizations'], list)
    
    def test_file_optimization(self):
        """Test file I/O optimization."""
        # Create test files
        test_files = []
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f'test_{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f'Test content {i}')
            test_files.append(file_path)
        
        # Test optimization
        results = self.optimizer.optimize_file_operations(test_files)
        
        self.assertIn('files_processed', results)
        self.assertIn('optimizations', results)
        self.assertEqual(results['files_processed'], 3)
    
    def test_performance_metrics(self):
        """Test performance metrics collection."""
        metrics = self.optimizer.get_performance_metrics()
        
        self.assertIn('cache_stats', metrics)
        self.assertIn('memory_usage', metrics)
        self.assertIn('performance_metrics', metrics)
        self.assertIn('optimization_status', metrics)
    
    def test_cache_management(self):
        """Test cache management."""
        # Clear cache
        self.optimizer.clear_cache()
        
        # Check cache is empty
        self.assertEqual(len(self.optimizer.cache), 0)
        
        # Set optimization level
        self.optimizer.set_optimization_level('high')
        self.assertEqual(self.optimizer.cache_size, 1000)
        self.assertEqual(self.optimizer.memory_threshold, 0.7)


class TestMemoryMonitor(unittest.TestCase):
    """Test memory monitoring system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.monitor = MemoryMonitor()
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        self.assertIsNotNone(self.monitor)
        self.assertTrue(self.monitor.monitoring_enabled)
        self.assertEqual(self.monitor.peak_memory, 0)
    
    def test_memory_recording(self):
        """Test memory recording."""
        # Record memory usage
        self.monitor._record_memory_usage()
        
        self.assertEqual(len(self.monitor.memory_history), 1)
        self.assertIn('timestamp', self.monitor.memory_history[0])
        self.assertIn('rss_mb', self.monitor.memory_history[0])
        self.assertIn('vms_mb', self.monitor.memory_history[0])
        self.assertIn('percentage', self.monitor.memory_history[0])
    
    def test_memory_stats(self):
        """Test memory statistics."""
        # Record some memory usage
        for _ in range(5):
            self.monitor._record_memory_usage()
            time.sleep(0.01)
        
        stats = self.monitor.get_memory_stats()
        
        self.assertIn('current_mb', stats)
        self.assertIn('average_mb', stats)
        self.assertIn('peak_mb', stats)
        self.assertIn('trend', stats)
    
    def test_monitoring_control(self):
        """Test monitoring start/stop."""
        # Start monitoring
        self.monitor.start_monitoring(interval=1)
        self.assertTrue(self.monitor.monitoring_enabled)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_enabled)


class TestGarbageCollectionOptimizer(unittest.TestCase):
    """Test garbage collection optimization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.gc_optimizer = GarbageCollectionOptimizer()
    
    def test_gc_optimization(self):
        """Test garbage collection optimization."""
        # Create some objects
        large_list = [i for i in range(10000)]
        
        # Run optimization
        results = self.gc_optimizer.optimize()
        
        self.assertIn('objects_collected', results)
        self.assertIn('time_spent', results)
        self.assertIn('before_counts', results)
        self.assertIn('after_counts', results)
        self.assertIn('actions', results)
    
    def test_gc_stats(self):
        """Test garbage collection statistics."""
        # Run optimization to generate stats
        self.gc_optimizer.optimize()
        
        stats = self.gc_optimizer.get_gc_stats()
        
        self.assertIn('current_counts', stats)
        self.assertIn('stats', stats)
        self.assertIn('thresholds', stats)


class TestDatabaseOptimizer(unittest.TestCase):
    """Test database optimization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_optimizer = DatabaseOptimizer()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_optimization(self):
        """Test database optimization."""
        # Create test database
        db_path = os.path.join(self.temp_dir, 'test.db')
        
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)")
            conn.execute("INSERT INTO test (name, value) VALUES ('test1', 100), ('test2', 200)")
            conn.commit()
        
        # Test optimization
        results = self.db_optimizer.optimize_database(db_path)
        
        self.assertIn('database', results)
        self.assertIn('optimizations', results)
        self.assertIsInstance(results['optimizations'], list)
    
    def test_database_analysis(self):
        """Test database analysis."""
        # Create test database
        db_path = os.path.join(self.temp_dir, 'test.db')
        
        import sqlite3
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.commit()
        
        # Test analysis
        with sqlite3.connect(db_path) as conn:
            analysis = self.db_optimizer._analyze_database(conn)
            
            self.assertIn('tables', analysis)
            self.assertIn('indexes', analysis)
            self.assertIn('size_mb', analysis)
            self.assertIn('page_count', analysis)
            self.assertIn('page_size', analysis)


class TestFileIOOptimizer(unittest.TestCase):
    """Test file I/O optimization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.io_optimizer = FileIOOptimizer()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_optimization(self):
        """Test file optimization."""
        # Create test files
        test_files = []
        for i in range(3):
            file_path = os.path.join(self.temp_dir, f'test_{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f'Test content {i}')
            test_files.append(file_path)
        
        # Test optimization
        results = self.io_optimizer.optimize_files(test_files)
        
        self.assertIn('files_processed', results)
        self.assertIn('optimizations', results)
        self.assertEqual(results['files_processed'], 3)
    
    def test_single_file_optimization(self):
        """Test single file optimization."""
        # Create test file
        file_path = os.path.join(self.temp_dir, 'test.txt')
        with open(file_path, 'w') as f:
            f.write('Test content')
        
        # Test optimization
        results = self.io_optimizer._optimize_single_file(file_path)
        
        self.assertIsInstance(results, list)


class TestPerformanceProfiler(unittest.TestCase):
    """Test performance profiler."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.profiler = PerformanceProfiler()
    
    def test_profiler_initialization(self):
        """Test profiler initialization."""
        self.assertIsNotNone(self.profiler)
        self.assertEqual(len(self.profiler.profiles), 0)
        self.assertEqual(len(self.profiler.active_profiles), 0)
    
    def test_profile_operations(self):
        """Test profiling operations."""
        # Start profile
        self.profiler.start_profile('test_operation')
        
        # Simulate some work
        time.sleep(0.01)
        
        # End profile
        results = self.profiler.end_profile('test_operation')
        
        self.assertIn('name', results)
        self.assertIn('duration', results)
        self.assertIn('memory_delta', results)
        self.assertIn('start_time', results)
        self.assertIn('end_time', results)
        self.assertEqual(results['name'], 'test_operation')
        self.assertGreater(results['duration'], 0)
    
    def test_profile_summary(self):
        """Test profile summary."""
        # Create some profiles
        self.profiler.start_profile('op1')
        time.sleep(0.01)
        self.profiler.end_profile('op1')
        
        self.profiler.start_profile('op2')
        time.sleep(0.01)
        self.profiler.end_profile('op2')
        
        summary = self.profiler.get_profile_summary()
        
        self.assertIn('total_profiles', summary)
        self.assertIn('average_duration', summary)
        self.assertIn('max_duration', summary)
        self.assertIn('min_duration', summary)
        self.assertEqual(summary['total_profiles'], 2)


class TestIntelligentCache(unittest.TestCase):
    """Test intelligent cache system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache = IntelligentCache(max_size=10, default_ttl=1)
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        self.assertEqual(self.cache.max_size, 10)
        self.assertEqual(self.cache.default_ttl, 1)
        self.assertEqual(len(self.cache.cache), 0)
    
    def test_cache_set_get(self):
        """Test cache set and get operations."""
        # Set value
        self.cache.set('key1', 'value1')
        
        # Get value
        result = self.cache.get('key1')
        self.assertEqual(result, 'value1')
        
        # Get non-existent key
        result = self.cache.get('key2', 'default')
        self.assertEqual(result, 'default')
    
    def test_cache_expiration(self):
        """Test cache expiration."""
        # Set value with short TTL
        self.cache.set('key1', 'value1', ttl=0.1)
        
        # Should be available immediately
        result = self.cache.get('key1')
        self.assertEqual(result, 'value1')
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Should be expired
        result = self.cache.get('key1')
        self.assertIsNone(result)
    
    def test_cache_eviction(self):
        """Test cache eviction."""
        # Fill cache beyond max size
        for i in range(15):
            self.cache.set(f'key{i}', f'value{i}')
        
        # Cache should not exceed max size
        self.assertLessEqual(len(self.cache.cache), self.cache.max_size)
    
    def test_cache_stats(self):
        """Test cache statistics."""
        # Generate some cache activity
        self.cache.set('key1', 'value1')
        self.cache.get('key1')  # Hit
        self.cache.get('key2')  # Miss
        
        stats = self.cache.get_stats()
        
        self.assertIn('size', stats)
        self.assertIn('max_size', stats)
        self.assertIn('hit_rate', stats)
        self.assertIn('stats', stats)
        self.assertIn('memory_usage', stats)
    
    def test_cache_cleanup(self):
        """Test cache cleanup."""
        # Set value with short TTL
        self.cache.set('key1', 'value1', ttl=0.1)
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Clean up expired entries
        self.cache._cleanup_expired()
        
        # Should be removed
        result = self.cache.get('key1')
        self.assertIsNone(result)


class TestQuestionCache(unittest.TestCase):
    """Test question cache system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.question_cache = QuestionCache(max_size=10)
    
    def test_question_cache_operations(self):
        """Test question cache operations."""
        # Set question
        question_data = {'id': 'q1', 'text': 'Test question', 'type': 'multiple_choice'}
        self.question_cache.set_question('q1', question_data)
        
        # Get question
        result = self.question_cache.get_question('q1')
        self.assertEqual(result, question_data)
        
        # Invalidate question
        self.question_cache.invalidate_question('q1')
        result = self.question_cache.get_question('q1')
        self.assertIsNone(result)
    
    def test_tag_questions_cache(self):
        """Test tag questions cache."""
        # Set questions by tag
        question_ids = ['q1', 'q2', 'q3']
        self.question_cache.set_questions_by_tag('tag1', question_ids)
        
        # Get questions by tag
        result = self.question_cache.get_questions_by_tag('tag1')
        self.assertEqual(result, question_ids)
        
        # Invalidate tag cache
        self.question_cache.invalidate_tag_cache('tag1')
        result = self.question_cache.get_questions_by_tag('tag1')
        self.assertIsNone(result)


class TestTagCache(unittest.TestCase):
    """Test tag cache system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tag_cache = TagCache(max_size=10)
    
    def test_tag_cache_operations(self):
        """Test tag cache operations."""
        # Set tag
        tag_data = {'id': 't1', 'name': 'math', 'description': 'Mathematics'}
        self.tag_cache.set_tag('t1', tag_data)
        
        # Get tag
        result = self.tag_cache.get_tag('t1')
        self.assertEqual(result, tag_data)
        
        # Invalidate tag
        self.tag_cache.invalidate_tag('t1')
        result = self.tag_cache.get_tag('t1')
        self.assertIsNone(result)
    
    def test_tag_hierarchy_cache(self):
        """Test tag hierarchy cache."""
        # Set hierarchy
        hierarchy = {'parent': {'child1': {}, 'child2': {}}}
        self.tag_cache.set_tag_hierarchy(hierarchy)
        
        # Get hierarchy
        result = self.tag_cache.get_tag_hierarchy()
        self.assertEqual(result, hierarchy)
        
        # Invalidate tag (should also invalidate hierarchy)
        self.tag_cache.invalidate_tag('t1')
        result = self.tag_cache.get_tag_hierarchy()
        self.assertIsNone(result)


class TestAnalyticsCache(unittest.TestCase):
    """Test analytics cache system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analytics_cache = AnalyticsCache(max_size=10)
    
    def test_analytics_cache_operations(self):
        """Test analytics cache operations."""
        # Set analytics
        analytics_data = {'total_questions': 100, 'average_score': 85.5}
        self.analytics_cache.set_analytics('performance', analytics_data)
        
        # Get analytics
        result = self.analytics_cache.get_analytics('performance')
        self.assertEqual(result, analytics_data)
        
        # Invalidate analytics
        self.analytics_cache.invalidate_analytics('performance')
        result = self.analytics_cache.get_analytics('performance')
        self.assertIsNone(result)


class TestCacheManager(unittest.TestCase):
    """Test cache manager system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cache_manager = CacheManager()
    
    def test_cache_manager_initialization(self):
        """Test cache manager initialization."""
        self.assertIsNotNone(self.cache_manager.question_cache)
        self.assertIsNotNone(self.cache_manager.tag_cache)
        self.assertIsNotNone(self.cache_manager.analytics_cache)
        self.assertIsNotNone(self.cache_manager.global_cache)
    
    def test_global_stats(self):
        """Test global statistics."""
        stats = self.cache_manager.get_global_stats()
        
        self.assertIn('question_cache', stats)
        self.assertIn('tag_cache', stats)
        self.assertIn('analytics_cache', stats)
        self.assertIn('global_cache', stats)
    
    def test_cache_optimization(self):
        """Test cache optimization."""
        results = self.cache_manager.optimize_caches()
        
        self.assertIn('optimizations', results)
        self.assertIn('before_stats', results)
        self.assertIn('after_stats', results)
    
    def test_clear_all_caches(self):
        """Test clearing all caches."""
        # Add some data to caches
        self.cache_manager.question_cache.set_question('q1', {'id': 'q1'})
        self.cache_manager.tag_cache.set_tag('t1', {'id': 't1'})
        self.cache_manager.global_cache.set('key1', 'value1')
        
        # Clear all caches
        self.cache_manager.clear_all_caches()
        
        # Check caches are empty
        self.assertEqual(len(self.cache_manager.question_cache.cache.cache), 0)
        self.assertEqual(len(self.cache_manager.tag_cache.cache.cache), 0)
        self.assertEqual(len(self.cache_manager.global_cache.cache), 0)


class TestCachingDecorator(unittest.TestCase):
    """Test caching decorator."""
    
    def setUp(self):
        """Set up test fixtures."""
        from caching_system import cache_manager
        cache_manager.clear_all_caches()
    
    def test_cached_decorator(self):
        """Test cached decorator."""
        call_count = 0
        
        @cached(ttl=60, cache_type='global')
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = test_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Second call should use cache
        result2 = test_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Should not increment


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run tests
    unittest.main(verbosity=2)
