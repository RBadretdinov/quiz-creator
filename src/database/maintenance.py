"""
Database Maintenance Utilities

This module provides database maintenance and cleanup utilities
for performance optimization and data integrity.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .connection import DatabaseConnectionManager
from .schema import DatabaseSchema

logger = logging.getLogger(__name__)

class DatabaseMaintenance:
    """Handles database maintenance and optimization tasks."""
    
    def __init__(self, db_manager: DatabaseConnectionManager):
        """
        Initialize database maintenance system.
        
        Args:
            db_manager: Database connection manager
        """
        self.db_manager = db_manager
        logger.info("Database maintenance system initialized")
    
    def perform_maintenance(self) -> Dict[str, Any]:
        """
        Perform comprehensive database maintenance.
        
        Returns:
            Maintenance result with details
        """
        result = {
            'success': True,
            'operations_completed': [],
            'operations_failed': [],
            'statistics': {},
            'recommendations': []
        }
        
        try:
            # 1. Analyze database
            logger.info("Performing database analysis...")
            if self.analyze_database():
                result['operations_completed'].append("Database analysis")
            else:
                result['operations_failed'].append("Database analysis")
            
            # 2. Vacuum database
            logger.info("Performing database vacuum...")
            if self.vacuum_database():
                result['operations_completed'].append("Database vacuum")
            else:
                result['operations_failed'].append("Database vacuum")
            
            # 3. Clean up old data
            logger.info("Cleaning up old data...")
            cleanup_result = self.cleanup_old_data()
            result['operations_completed'].append("Data cleanup")
            result['statistics']['cleanup'] = cleanup_result
            
            # 4. Optimize indexes
            logger.info("Optimizing indexes...")
            if self.optimize_indexes():
                result['operations_completed'].append("Index optimization")
            else:
                result['operations_failed'].append("Index optimization")
            
            # 5. Check data integrity
            logger.info("Checking data integrity...")
            integrity_result = self.check_data_integrity()
            result['statistics']['integrity'] = integrity_result
            if integrity_result['is_valid']:
                result['operations_completed'].append("Integrity check")
            else:
                result['operations_failed'].append("Integrity check")
            
            # 6. Generate recommendations
            result['recommendations'] = self.generate_recommendations(result['statistics'])
            
            # Determine overall success
            result['success'] = len(result['operations_failed']) == 0
            
            logger.info(f"Database maintenance completed: {len(result['operations_completed'])} operations successful")
            return result
            
        except Exception as e:
            result['success'] = False
            result['operations_failed'].append(f"Maintenance error: {e}")
            logger.error(f"Database maintenance failed: {e}")
            return result
    
    def analyze_database(self) -> bool:
        """
        Analyze database to update query optimizer statistics.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db_manager.get_connection_context() as conn:
                conn.execute("ANALYZE")
                logger.info("Database analysis completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to analyze database: {e}")
            return False
    
    def vacuum_database(self) -> bool:
        """
        Vacuum database to reclaim space and optimize performance.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db_manager.get_connection_context() as conn:
                conn.execute("VACUUM")
                logger.info("Database vacuum completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to vacuum database: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """
        Clean up old data from the database.
        
        Args:
            days_to_keep: Number of days of data to keep
            
        Returns:
            Cleanup statistics
        """
        result = {
            'old_sessions_removed': 0,
            'old_analytics_removed': 0,
            'old_history_removed': 0,
            'total_records_removed': 0
        }
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            cutoff_str = cutoff_date.isoformat()
            
            with self.db_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                
                # Clean up old quiz sessions
                cursor.execute("DELETE FROM quiz_sessions WHERE start_time < ?", (cutoff_str,))
                result['old_sessions_removed'] = cursor.rowcount
                
                # Clean up old analytics
                cursor.execute("DELETE FROM analytics WHERE timestamp < ?", (cutoff_str,))
                result['old_analytics_removed'] = cursor.rowcount
                
                # Clean up old question history
                cursor.execute("DELETE FROM question_history WHERE timestamp < ?", (cutoff_str,))
                result['old_history_removed'] = cursor.rowcount
                
                conn.commit()
                
                result['total_records_removed'] = (
                    result['old_sessions_removed'] + 
                    result['old_analytics_removed'] + 
                    result['old_history_removed']
                )
                
                logger.info(f"Data cleanup completed: {result['total_records_removed']} records removed")
                return result
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return result
    
    def optimize_indexes(self) -> bool:
        """
        Optimize database indexes.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.db_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                
                # Rebuild indexes
                cursor.execute("REINDEX")
                
                logger.info("Index optimization completed successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to optimize indexes: {e}")
            return False
    
    def check_data_integrity(self) -> Dict[str, Any]:
        """
        Check database data integrity.
        
        Returns:
            Integrity check results
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        try:
            with self.db_manager.get_connection_context() as conn:
                cursor = conn.cursor()
                
                # Check for orphaned records
                orphaned_checks = [
                    ("Orphaned question history", 
                     "SELECT COUNT(*) FROM question_history h LEFT JOIN questions q ON h.question_id = q.id WHERE q.id IS NULL"),
                    ("Orphaned tag references", 
                     "SELECT COUNT(*) FROM questions WHERE tags LIKE '%\"invalid_tag_id\"%'"),
                    ("Invalid question types", 
                     "SELECT COUNT(*) FROM questions WHERE question_type NOT IN ('multiple_choice', 'true_false', 'select_all')"),
                    ("Invalid JSON in answers", 
                     "SELECT COUNT(*) FROM questions WHERE json_valid(answers) = 0"),
                    ("Invalid JSON in tags", 
                     "SELECT COUNT(*) FROM questions WHERE json_valid(tags) = 0")
                ]
                
                for check_name, query in orphaned_checks:
                    try:
                        cursor.execute(query)
                        count = cursor.fetchone()[0]
                        if count > 0:
                            result['warnings'].append(f"{check_name}: {count} issues found")
                            result['statistics'][check_name.lower().replace(' ', '_')] = count
                    except Exception as e:
                        result['errors'].append(f"Failed to check {check_name}: {e}")
                
                # Check table row counts
                tables = ['questions', 'tags', 'quiz_sessions', 'question_history', 'analytics']
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        result['statistics'][f'{table}_count'] = count
                    except Exception as e:
                        result['errors'].append(f"Failed to count {table}: {e}")
                
                # Check for data consistency
                consistency_checks = [
                    ("Tag usage count mismatch", 
                     "SELECT COUNT(*) FROM tags t WHERE t.usage_count != (SELECT COUNT(*) FROM questions q WHERE json_extract(q.tags, '$') LIKE '%' || t.name || '%')"),
                    ("Question count mismatch", 
                     "SELECT COUNT(*) FROM tags t WHERE t.question_count != (SELECT COUNT(*) FROM questions q WHERE json_extract(q.tags, '$') LIKE '%' || t.name || '%')")
                ]
                
                for check_name, query in consistency_checks:
                    try:
                        cursor.execute(query)
                        count = cursor.fetchone()[0]
                        if count > 0:
                            result['warnings'].append(f"{check_name}: {count} inconsistencies found")
                            result['statistics'][check_name.lower().replace(' ', '_')] = count
                    except Exception as e:
                        result['errors'].append(f"Failed to check {check_name}: {e}")
                
                # Determine overall validity
                result['is_valid'] = len(result['errors']) == 0
                
                logger.info(f"Data integrity check completed: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
                return result
                
        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f"Integrity check failed: {e}")
            logger.error(f"Data integrity check failed: {e}")
            return result
    
    def generate_recommendations(self, statistics: Dict[str, Any]) -> List[str]:
        """
        Generate maintenance recommendations based on statistics.
        
        Args:
            statistics: Database statistics
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            # Check database size
            db_info = self.db_manager.get_database_info()
            db_size_mb = db_info.get('database_size_mb', 0)
            
            if db_size_mb > 100:
                recommendations.append("Database size is large (>100MB). Consider archiving old data.")
            
            # Check table sizes
            table_counts = db_info.get('table_counts', {})
            
            if table_counts.get('quiz_sessions', 0) > 1000:
                recommendations.append("Large number of quiz sessions. Consider cleaning up old sessions.")
            
            if table_counts.get('analytics', 0) > 5000:
                recommendations.append("Large number of analytics records. Consider archiving old analytics.")
            
            if table_counts.get('question_history', 0) > 2000:
                recommendations.append("Large number of question history records. Consider cleaning up old history.")
            
            # Check for unused data
            if statistics.get('unused_tags', 0) > 10:
                recommendations.append("Many unused tags found. Consider removing unused tags.")
            
            if statistics.get('low_quality_questions', 0) > 20:
                recommendations.append("Many low-quality questions found. Consider reviewing and improving questions.")
            
            # Check for performance issues
            if statistics.get('missing_indexes', 0) > 0:
                recommendations.append("Missing indexes detected. Consider adding indexes for better performance.")
            
            if statistics.get('fragmented_data', 0) > 0:
                recommendations.append("Data fragmentation detected. Consider running VACUUM more frequently.")
            
            # General recommendations
            if not recommendations:
                recommendations.append("Database is in good condition. Continue regular maintenance.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return ["Unable to generate recommendations due to error"]
    
    def get_maintenance_schedule(self) -> Dict[str, Any]:
        """
        Get recommended maintenance schedule.
        
        Returns:
            Maintenance schedule recommendations
        """
        return {
            'daily': [
                "Check database connectivity",
                "Monitor database size",
                "Check for error logs"
            ],
            'weekly': [
                "Run ANALYZE to update statistics",
                "Check data integrity",
                "Review performance metrics"
            ],
            'monthly': [
                "Run VACUUM to optimize database",
                "Clean up old data",
                "Review and optimize indexes",
                "Create database backup"
            ],
            'quarterly': [
                "Comprehensive data integrity check",
                "Review and update maintenance procedures",
                "Archive old data",
                "Performance optimization review"
            ]
        }
    
    def get_database_health_score(self) -> Dict[str, Any]:
        """
        Calculate database health score.
        
        Returns:
            Health score and details
        """
        try:
            score = 100
            issues = []
            
            # Check database connectivity
            if not self.db_manager.initialize():
                score -= 50
                issues.append("Database connectivity issues")
            
            # Check data integrity
            integrity_result = self.check_data_integrity()
            if not integrity_result['is_valid']:
                score -= 20
                issues.append("Data integrity issues")
            
            if integrity_result['warnings']:
                score -= len(integrity_result['warnings']) * 5
                issues.extend(integrity_result['warnings'])
            
            # Check database size
            db_info = self.db_manager.get_database_info()
            db_size_mb = db_info.get('database_size_mb', 0)
            
            if db_size_mb > 500:
                score -= 10
                issues.append("Large database size")
            elif db_size_mb > 100:
                score -= 5
                issues.append("Moderate database size")
            
            # Check table counts
            table_counts = db_info.get('table_counts', {})
            
            if table_counts.get('questions', 0) == 0:
                score -= 15
                issues.append("No questions in database")
            
            if table_counts.get('tags', 0) == 0:
                score -= 10
                issues.append("No tags in database")
            
            # Ensure score doesn't go below 0
            score = max(0, score)
            
            # Determine health level
            if score >= 90:
                health_level = "Excellent"
            elif score >= 75:
                health_level = "Good"
            elif score >= 60:
                health_level = "Fair"
            elif score >= 40:
                health_level = "Poor"
            else:
                health_level = "Critical"
            
            return {
                'score': score,
                'health_level': health_level,
                'issues': issues,
                'database_info': db_info,
                'recommendations': self.generate_recommendations({})
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return {
                'score': 0,
                'health_level': 'Unknown',
                'issues': [f"Health check failed: {e}"],
                'database_info': {},
                'recommendations': ["Unable to assess database health"]
            }
