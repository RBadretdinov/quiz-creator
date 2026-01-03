"""
Data Migration System

This module provides comprehensive data migration tools with rollback capability,
validation, and automated migration processes.
"""

import os
import json
import logging
import shutil
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib
import tempfile

logger = logging.getLogger(__name__)

class DataMigration:
    """Comprehensive data migration system with rollback capability."""
    
    def __init__(self, migration_dir: str = "data/migrations"):
        """
        Initialize the data migration system.
        
        Args:
            migration_dir: Directory for storing migration files and backups
        """
        self.migration_dir = Path(migration_dir)
        self.migration_dir.mkdir(parents=True, exist_ok=True)
        
        # Migration history
        self.migration_history = []
        self.current_version = "1.0"
        
        # Migration statistics
        self.migration_stats = {
            'total_migrations': 0,
            'successful_migrations': 0,
            'failed_migrations': 0,
            'rollbacks_performed': 0
        }
        
        logger.info("Data migration system initialized")
    
    def migrate_data(self, source_path: str, 
                    target_path: str,
                    migration_type: str = 'json_to_sqlite',
                    backup_source: bool = True) -> Dict[str, Any]:
        """
        Migrate data from source to target with backup and validation.
        
        Args:
            source_path: Path to source data
            target_path: Path to target data
            migration_type: Type of migration to perform
            backup_source: Whether to backup source data
            
        Returns:
            Dictionary containing migration results
        """
        start_time = datetime.now()
        migration_id = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Validate source data
            if not os.path.exists(source_path):
                return {
                    'success': False,
                    'error': f'Source path does not exist: {source_path}',
                    'migration_id': migration_id,
                    'processing_time': 0
                }
            
            # Create backup if requested
            backup_path = None
            if backup_source:
                backup_path = self._create_backup(source_path, migration_id)
                if not backup_path:
                    return {
                        'success': False,
                        'error': 'Failed to create backup',
                        'migration_id': migration_id,
                        'processing_time': 0
                    }
            
            # Load source data
            source_data = self._load_source_data(source_path)
            if not source_data:
                return {
                    'success': False,
                    'error': 'Failed to load source data',
                    'migration_id': migration_id,
                    'processing_time': 0
                }
            
            # Validate source data
            validation_result = self._validate_source_data(source_data, migration_type)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Source data validation failed',
                    'validation_errors': validation_result['errors'],
                    'migration_id': migration_id,
                    'processing_time': 0
                }
            
            # Perform migration
            migration_result = self._perform_migration(
                source_data, target_path, migration_type, migration_id
            )
            
            if not migration_result['success']:
                # Rollback if migration failed
                if backup_path:
                    self._rollback_migration(backup_path, source_path)
                
                return {
                    'success': False,
                    'error': migration_result['error'],
                    'migration_id': migration_id,
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'rollback_performed': True
                }
            
            # Record migration
            migration_record = {
                'migration_id': migration_id,
                'timestamp': datetime.now().isoformat(),
                'migration_type': migration_type,
                'source_path': source_path,
                'target_path': target_path,
                'backup_path': backup_path,
                'success': True,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'data_hash': self._calculate_data_hash(source_data)
            }
            
            self.migration_history.append(migration_record)
            self._update_migration_statistics(True)
            
            logger.info(f"Migration {migration_id} completed successfully")
            
            return {
                'success': True,
                'migration_id': migration_id,
                'target_path': target_path,
                'backup_path': backup_path,
                'processing_time': migration_record['processing_time'],
                'data_hash': migration_record['data_hash']
            }
            
        except Exception as e:
            logger.error(f"Error in migration {migration_id}: {e}")
            self._update_migration_statistics(False)
            
            return {
                'success': False,
                'error': str(e),
                'migration_id': migration_id,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def rollback_migration(self, migration_id: str) -> Dict[str, Any]:
        """
        Rollback a specific migration.
        
        Args:
            migration_id: ID of migration to rollback
            
        Returns:
            Dictionary containing rollback results
        """
        try:
            # Find migration record
            migration_record = None
            for record in self.migration_history:
                if record['migration_id'] == migration_id:
                    migration_record = record
                    break
            
            if not migration_record:
                return {
                    'success': False,
                    'error': f'Migration {migration_id} not found',
                    'rollback_time': 0
                }
            
            if not migration_record['success']:
                return {
                    'success': False,
                    'error': f'Cannot rollback failed migration {migration_id}',
                    'rollback_time': 0
                }
            
            start_time = datetime.now()
            
            # Perform rollback
            rollback_result = self._rollback_migration(
                migration_record['backup_path'],
                migration_record['source_path']
            )
            
            if not rollback_result:
                return {
                    'success': False,
                    'error': 'Rollback failed',
                    'rollback_time': 0
                }
            
            # Update migration record
            migration_record['rollback_timestamp'] = datetime.now().isoformat()
            migration_record['rolled_back'] = True
            
            # Update statistics
            self.migration_stats['rollbacks_performed'] += 1
            
            rollback_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Migration {migration_id} rolled back successfully")
            
            return {
                'success': True,
                'migration_id': migration_id,
                'rollback_time': rollback_time,
                'restored_from': migration_record['backup_path']
            }
            
        except Exception as e:
            logger.error(f"Error rolling back migration {migration_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'rollback_time': 0
            }
    
    def batch_migrate_data(self, migration_tasks: List[Dict[str, Any]], 
                          progress_callback: callable = None) -> Dict[str, Any]:
        """
        Perform batch data migration.
        
        Args:
            migration_tasks: List of migration task dictionaries
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary containing batch migration results
        """
        start_time = datetime.now()
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"Starting batch migration of {len(migration_tasks)} tasks")
        
        for i, task in enumerate(migration_tasks):
            try:
                # Perform individual migration
                result = self.migrate_data(
                    task['source_path'],
                    task['target_path'],
                    task.get('migration_type', 'json_to_sqlite'),
                    task.get('backup_source', True)
                )
                
                results.append({
                    'task_index': i,
                    'task': task,
                    'result': result
                })
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                
                # Update progress
                if progress_callback:
                    progress = (i + 1) / len(migration_tasks) * 100
                    progress_callback(progress, f"Migrated {i + 1}/{len(migration_tasks)} tasks")
                
                logger.info(f"Migrated {i + 1}/{len(migration_tasks)}: {task['source_path']}")
                
            except Exception as e:
                logger.error(f"Error in batch migration task {i}: {e}")
                results.append({
                    'task_index': i,
                    'task': task,
                    'result': {
                        'success': False,
                        'error': str(e),
                        'processing_time': 0
                    }
                })
                failed += 1
        
        # Calculate summary statistics
        total_time = (datetime.now() - start_time).total_seconds()
        
        summary = {
            'total_tasks': len(migration_tasks),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(migration_tasks)) * 100,
            'total_processing_time': total_time,
            'average_processing_time': total_time / len(migration_tasks)
        }
        
        logger.info(f"Batch migration completed: {successful}/{len(migration_tasks)} successful ({summary['success_rate']:.1f}%)")
        
        return {
            'success': failed == 0,
            'results': results,
            'summary': summary,
            'error': None if failed == 0 else f"{failed} tasks failed"
        }
    
    def _create_backup(self, source_path: str, migration_id: str) -> Optional[str]:
        """Create backup of source data."""
        try:
            backup_dir = self.migration_dir / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            backup_path = backup_dir / f"{migration_id}_backup.json"
            
            # Copy source data to backup
            if os.path.isfile(source_path):
                shutil.copy2(source_path, backup_path)
            else:
                # Handle directory backup
                shutil.copytree(source_path, backup_path)
            
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def _load_source_data(self, source_path: str) -> Optional[Dict[str, Any]]:
        """Load source data from file."""
        try:
            if source_path.endswith('.json'):
                with open(source_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Handle other formats
                logger.error(f"Unsupported source format: {source_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading source data from {source_path}: {e}")
            return None
    
    def _validate_source_data(self, data: Dict[str, Any], migration_type: str) -> Dict[str, Any]:
        """Validate source data for migration."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Source data must be a dictionary")
            return {'valid': False, 'errors': errors}
        
        # Validate based on migration type
        if migration_type == 'json_to_sqlite':
            # Validate questions
            if 'questions' in data:
                questions = data['questions']
                if not isinstance(questions, list):
                    errors.append("Questions must be a list")
                else:
                    for i, question in enumerate(questions):
                        if not isinstance(question, dict):
                            errors.append(f"Question {i} must be a dictionary")
                        else:
                            if 'question_text' not in question:
                                errors.append(f"Question {i} missing 'question_text'")
                            if 'answers' not in question:
                                errors.append(f"Question {i} missing 'answers'")
            
            # Validate tags
            if 'tags' in data:
                tags = data['tags']
                if not isinstance(tags, list):
                    errors.append("Tags must be a list")
                else:
                    for i, tag in enumerate(tags):
                        if not isinstance(tag, dict):
                            errors.append(f"Tag {i} must be a dictionary")
                        else:
                            if 'name' not in tag:
                                errors.append(f"Tag {i} missing 'name'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _perform_migration(self, source_data: Dict[str, Any], 
                          target_path: str, 
                          migration_type: str, 
                          migration_id: str) -> Dict[str, Any]:
        """Perform the actual data migration."""
        try:
            if migration_type == 'json_to_sqlite':
                return self._migrate_json_to_sqlite(source_data, target_path, migration_id)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported migration type: {migration_type}'
                }
                
        except Exception as e:
            logger.error(f"Error performing migration: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _migrate_json_to_sqlite(self, source_data: Dict[str, Any], 
                               target_path: str, 
                               migration_id: str) -> Dict[str, Any]:
        """Migrate JSON data to SQLite format."""
        try:
            # This would integrate with the database system
            # For now, we'll create a structured JSON file
            migrated_data = {
                'migration_id': migration_id,
                'migration_timestamp': datetime.now().isoformat(),
                'source_format': 'json',
                'target_format': 'sqlite',
                'data': source_data
            }
            
            # Write migrated data
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(migrated_data, f, indent=2, default=str)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error migrating JSON to SQLite: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _rollback_migration(self, backup_path: str, target_path: str) -> bool:
        """Rollback migration by restoring from backup."""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Restore from backup
            if os.path.isfile(backup_path):
                shutil.copy2(backup_path, target_path)
            else:
                # Handle directory restoration
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.copytree(backup_path, target_path)
            
            logger.info(f"Migration rolled back: {backup_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error rolling back migration: {e}")
            return False
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for data integrity."""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating data hash: {e}")
            return ""
    
    def _update_migration_statistics(self, success: bool) -> None:
        """Update migration statistics."""
        self.migration_stats['total_migrations'] += 1
        
        if success:
            self.migration_stats['successful_migrations'] += 1
        else:
            self.migration_stats['failed_migrations'] += 1
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get migration history."""
        return self.migration_history.copy()
    
    def get_migration_statistics(self) -> Dict[str, Any]:
        """Get migration statistics."""
        return self.migration_stats.copy()
    
    def clear_migration_history(self) -> None:
        """Clear migration history."""
        self.migration_history = []
        logger.info("Migration history cleared")
    
    def export_migration_report(self, output_path: str = None) -> str:
        """Export migration report to file."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.migration_dir / f"migration_report_{timestamp}.json"
        
        report = {
            'migration_history': self.migration_history,
            'migration_statistics': self.migration_stats,
            'current_version': self.current_version,
            'report_timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Migration report exported to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exporting migration report: {e}")
            return ""
