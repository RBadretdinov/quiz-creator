"""
Intelligent Caching System

This module provides intelligent caching for frequently accessed data
with automatic cache management, expiration, and performance optimization.
"""

import time
import threading
import json
import hashlib
from typing import Dict, Any, Optional, Callable, Union, List
from datetime import datetime, timedelta
from pathlib import Path
import weakref
from collections import OrderedDict
from functools import wraps

class IntelligentCache:
    """Intelligent caching system with automatic management."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """Initialize intelligent cache."""
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.access_times = {}
        self.hit_counts = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expirations': 0
        }
        self.lock = threading.RLock()
        self.cleanup_thread = None
        self.cleanup_interval = 300  # 5 minutes
        self.running = False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                self.cache_stats['misses'] += 1
                return default
            
            # Check expiration
            if self._is_expired(key):
                self._remove_key(key)
                self.cache_stats['expirations'] += 1
                return default
            
            # Update access time and hit count
            self.access_times[key] = time.time()
            self.hit_counts[key] = self.hit_counts.get(key, 0) + 1
            
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            
            self.cache_stats['hits'] += 1
            return value['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        with self.lock:
            ttl = ttl or self.default_ttl
            expire_time = time.time() + ttl
            
            self.cache[key] = {
                'value': value,
                'expire_time': expire_time,
                'created_time': time.time()
            }
            
            self.access_times[key] = time.time()
            self.hit_counts[key] = 0
            
            # Check if we need to evict
            if len(self.cache) > self.max_size:
                self._evict_least_used()
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        with self.lock:
            if key in self.cache:
                self._remove_key(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.hit_counts.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': hit_rate,
                'stats': self.cache_stats.copy(),
                'memory_usage': self._estimate_memory_usage()
            }
    
    def start_cleanup_thread(self) -> None:
        """Start background cleanup thread."""
        if self.cleanup_thread is None or not self.cleanup_thread.is_alive():
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
            self.cleanup_thread.start()
    
    def stop_cleanup_thread(self) -> None:
        """Stop background cleanup thread."""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=1)
    
    def _is_expired(self, key: str) -> bool:
        """Check if key is expired."""
        if key not in self.cache:
            return True
        
        return time.time() > self.cache[key]['expire_time']
    
    def _remove_key(self, key: str) -> None:
        """Remove key from all tracking structures."""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_times:
            del self.access_times[key]
        if key in self.hit_counts:
            del self.hit_counts[key]
    
    def _evict_least_used(self) -> None:
        """Evict least recently used item."""
        if not self.cache:
            return
        
        # Find least recently used item
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove_key(lru_key)
        self.cache_stats['evictions'] += 1
    
    def _cleanup_worker(self) -> None:
        """Background cleanup worker."""
        while self.running:
            try:
                self._cleanup_expired()
                time.sleep(self.cleanup_interval)
            except Exception:
                pass
    
    def _cleanup_expired(self) -> None:
        """Clean up expired entries."""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, data in self.cache.items()
                if current_time > data['expire_time']
            ]
            
            for key in expired_keys:
                self._remove_key(key)
                self.cache_stats['expirations'] += 1
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage of cache."""
        total_size = 0
        for key, data in self.cache.items():
            total_size += len(str(key))
            total_size += len(str(data))
        return total_size


class QuestionCache:
    """Specialized cache for quiz questions."""
    
    def __init__(self, max_size: int = 500):
        """Initialize question cache."""
        self.cache = IntelligentCache(max_size, default_ttl=7200)  # 2 hours
        self.cache.start_cleanup_thread()
    
    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Get question from cache."""
        return self.cache.get(f"question_{question_id}")
    
    def set_question(self, question_id: str, question_data: Dict[str, Any]) -> None:
        """Set question in cache."""
        self.cache.set(f"question_{question_id}", question_data)
    
    def get_questions_by_tag(self, tag_id: str) -> Optional[List[str]]:
        """Get question IDs by tag from cache."""
        return self.cache.get(f"tag_questions_{tag_id}")
    
    def set_questions_by_tag(self, tag_id: str, question_ids: List[str]) -> None:
        """Set question IDs by tag in cache."""
        self.cache.set(f"tag_questions_{tag_id}", question_ids, ttl=1800)  # 30 minutes
    
    def invalidate_question(self, question_id: str) -> None:
        """Invalidate question cache."""
        self.cache.delete(f"question_{question_id}")
    
    def invalidate_tag_cache(self, tag_id: str) -> None:
        """Invalidate tag-related cache."""
        self.cache.delete(f"tag_questions_{tag_id}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()


class TagCache:
    """Specialized cache for tags."""
    
    def __init__(self, max_size: int = 200):
        """Initialize tag cache."""
        self.cache = IntelligentCache(max_size, default_ttl=3600)  # 1 hour
        self.cache.start_cleanup_thread()
    
    def get_tag(self, tag_id: str) -> Optional[Dict[str, Any]]:
        """Get tag from cache."""
        return self.cache.get(f"tag_{tag_id}")
    
    def set_tag(self, tag_id: str, tag_data: Dict[str, Any]) -> None:
        """Set tag in cache."""
        self.cache.set(f"tag_{tag_id}", tag_data)
    
    def get_tag_hierarchy(self) -> Optional[Dict[str, Any]]:
        """Get tag hierarchy from cache."""
        return self.cache.get("tag_hierarchy")
    
    def set_tag_hierarchy(self, hierarchy: Dict[str, Any]) -> None:
        """Set tag hierarchy in cache."""
        self.cache.set("tag_hierarchy", hierarchy, ttl=1800)  # 30 minutes
    
    def invalidate_tag(self, tag_id: str) -> None:
        """Invalidate tag cache."""
        self.cache.delete(f"tag_{tag_id}")
        # Also invalidate hierarchy cache
        self.cache.delete("tag_hierarchy")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()


class AnalyticsCache:
    """Specialized cache for analytics data."""
    
    def __init__(self, max_size: int = 100):
        """Initialize analytics cache."""
        self.cache = IntelligentCache(max_size, default_ttl=1800)  # 30 minutes
        self.cache.start_cleanup_thread()
    
    def get_analytics(self, analytics_type: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get analytics data from cache."""
        cache_key = self._create_analytics_key(analytics_type, params or {})
        return self.cache.get(cache_key)
    
    def set_analytics(self, analytics_type: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> None:
        """Set analytics data in cache."""
        cache_key = self._create_analytics_key(analytics_type, params or {})
        self.cache.set(cache_key, data)
    
    def invalidate_analytics(self, analytics_type: str = None) -> None:
        """Invalidate analytics cache."""
        if analytics_type:
            # Invalidate specific analytics type
            keys_to_remove = [key for key in self.cache.cache.keys() if key.startswith(f"analytics_{analytics_type}")]
            for key in keys_to_remove:
                self.cache.delete(key)
        else:
            # Invalidate all analytics
            keys_to_remove = [key for key in self.cache.cache.keys() if key.startswith("analytics_")]
            for key in keys_to_remove:
                self.cache.delete(key)
    
    def _create_analytics_key(self, analytics_type: str, params: Dict[str, Any]) -> str:
        """Create cache key for analytics."""
        param_str = json.dumps(params, sort_keys=True)
        return f"analytics_{analytics_type}_{hashlib.md5(param_str.encode()).hexdigest()}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()


class CacheManager:
    """Centralized cache management system."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.question_cache = QuestionCache()
        self.tag_cache = TagCache()
        self.analytics_cache = AnalyticsCache()
        self.global_cache = IntelligentCache(max_size=2000, default_ttl=3600)
        self.global_cache.start_cleanup_thread()
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches."""
        return {
            'question_cache': self.question_cache.get_stats(),
            'tag_cache': self.tag_cache.get_stats(),
            'analytics_cache': self.analytics_cache.get_stats(),
            'global_cache': self.global_cache.get_stats()
        }
    
    def clear_all_caches(self) -> None:
        """Clear all caches."""
        self.question_cache.cache.clear()
        self.tag_cache.cache.clear()
        self.analytics_cache.cache.clear()
        self.global_cache.clear()
    
    def optimize_caches(self) -> Dict[str, Any]:
        """Optimize all caches."""
        results = {
            'optimizations': [],
            'before_stats': self.get_global_stats(),
            'after_stats': None
        }
        
        # Clean up expired entries
        self.question_cache.cache._cleanup_expired()
        self.tag_cache.cache._cleanup_expired()
        self.analytics_cache.cache._cleanup_expired()
        self.global_cache._cleanup_expired()
        
        results['optimizations'].append("Cleaned up expired entries")
        
        # Optimize cache sizes if needed
        total_memory = sum(cache['memory_usage'] for cache in self.get_global_stats().values() if isinstance(cache, dict))
        if total_memory > 50 * 1024 * 1024:  # 50MB
            self._reduce_cache_sizes()
            results['optimizations'].append("Reduced cache sizes due to high memory usage")
        
        results['after_stats'] = self.get_global_stats()
        return results
    
    def _reduce_cache_sizes(self) -> None:
        """Reduce cache sizes to free memory."""
        # Reduce cache sizes by 25%
        self.question_cache.cache.max_size = int(self.question_cache.cache.max_size * 0.75)
        self.tag_cache.cache.max_size = int(self.tag_cache.cache.max_size * 0.75)
        self.analytics_cache.cache.max_size = int(self.analytics_cache.cache.max_size * 0.75)
        self.global_cache.max_size = int(self.global_cache.max_size * 0.75)


# Global cache manager instance
cache_manager = CacheManager()

def cached(ttl: int = 3600, cache_type: str = 'global'):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}_{hashlib.md5(str(args).encode() + str(kwargs).encode()).hexdigest()}"
            
            # Get appropriate cache
            if cache_type == 'question':
                cache = cache_manager.question_cache.cache
            elif cache_type == 'tag':
                cache = cache_manager.tag_cache.cache
            elif cache_type == 'analytics':
                cache = cache_manager.analytics_cache.cache
            else:
                cache = cache_manager.global_cache
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
