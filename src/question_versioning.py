"""
Question Versioning

This module provides version control for questions, tracking changes,
history, and allowing rollback to previous versions.
"""

from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class QuestionVersioning:
    """Manages version control for questions."""
    
    def __init__(self, version_storage_path: str = "data/question_versions.json"):
        """Initialize question versioning."""
        self.version_storage_path = version_storage_path
        self.versions: Dict[str, List[Dict[str, Any]]] = {}
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(version_storage_path), exist_ok=True)
        
        # Load existing versions
        self._load_versions()
    
    def _load_versions(self) -> None:
        """Load question versions from storage."""
        try:
            if os.path.exists(self.version_storage_path):
                with open(self.version_storage_path, 'r', encoding='utf-8') as f:
                    self.versions = json.load(f)
                logger.info(f"Loaded question versions from {self.version_storage_path}")
            else:
                self.versions = {}
                logger.info("No existing question versions found")
        except Exception as e:
            logger.error(f"Error loading question versions: {e}")
            self.versions = {}
    
    def _save_versions(self) -> None:
        """Save question versions to storage."""
        try:
            with open(self.version_storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.versions, f, indent=2, ensure_ascii=False)
            logger.debug("Question versions saved successfully")
        except Exception as e:
            logger.error(f"Error saving question versions: {e}")
    
    def create_version(self, question: Dict[str, Any], change_description: str = "Question modified") -> str:
        """
        Create a new version of a question.
        
        Args:
            question: Question data to version
            change_description: Description of the change
            
        Returns:
            Version ID
        """
        question_id = question.get('id')
        if not question_id:
            raise ValueError("Question must have an ID to create version")
        
        # Generate version ID
        version_id = f"{question_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create version record
        version_record = {
            'version_id': version_id,
            'question_id': question_id,
            'timestamp': datetime.now().isoformat(),
            'change_description': change_description,
            'question_data': question.copy(),
            'version_number': self._get_next_version_number(question_id)
        }
        
        # Add to versions
        if question_id not in self.versions:
            self.versions[question_id] = []
        
        self.versions[question_id].append(version_record)
        
        # Keep only last 10 versions per question
        if len(self.versions[question_id]) > 10:
            self.versions[question_id] = self.versions[question_id][-10:]
        
        # Save versions
        self._save_versions()
        
        logger.info(f"Created version {version_id} for question {question_id}")
        return version_id
    
    def _get_next_version_number(self, question_id: str) -> int:
        """Get the next version number for a question."""
        if question_id not in self.versions:
            return 1
        
        return len(self.versions[question_id]) + 1
    
    def get_question_history(self, question_id: str) -> List[Dict[str, Any]]:
        """
        Get version history for a question.
        
        Args:
            question_id: ID of the question
            
        Returns:
            List of version records
        """
        return self.versions.get(question_id, [])
    
    def get_latest_version(self, question_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest version of a question.
        
        Args:
            question_id: ID of the question
            
        Returns:
            Latest version record or None
        """
        history = self.get_question_history(question_id)
        if history:
            return history[-1]
        return None
    
    def get_version_by_id(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific version by ID.
        
        Args:
            version_id: Version ID
            
        Returns:
            Version record or None
        """
        for question_id, versions in self.versions.items():
            for version in versions:
                if version['version_id'] == version_id:
                    return version
        return None
    
    def revert_to_version(self, version_id: str) -> Optional[Dict[str, Any]]:
        """
        Revert a question to a specific version.
        
        Args:
            version_id: Version ID to revert to
            
        Returns:
            Reverted question data or None
        """
        version = self.get_version_by_id(version_id)
        if not version:
            logger.error(f"Version {version_id} not found")
            return None
        
        # Get the question data from the version
        reverted_question = version['question_data'].copy()
        
        # Update timestamps
        reverted_question['last_modified'] = datetime.now().isoformat()
        
        # Create a new version for the revert
        self.create_version(reverted_question, f"Reverted to version {version_id}")
        
        logger.info(f"Reverted question {version['question_id']} to version {version_id}")
        return reverted_question
    
    def compare_versions(self, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """
        Compare two versions of a question.
        
        Args:
            version_id1: First version ID
            version_id2: Second version ID
            
        Returns:
            Comparison result
        """
        version1 = self.get_version_by_id(version_id1)
        version2 = self.get_version_by_id(version_id2)
        
        if not version1 or not version2:
            return {'error': 'One or both versions not found'}
        
        if version1['question_id'] != version2['question_id']:
            return {'error': 'Cannot compare versions of different questions'}
        
        # Compare question data
        question1 = version1['question_data']
        question2 = version2['question_data']
        
        changes = []
        
        # Compare question text
        if question1.get('question_text') != question2.get('question_text'):
            changes.append({
                'field': 'question_text',
                'old_value': question1.get('question_text'),
                'new_value': question2.get('question_text')
            })
        
        # Compare question type
        if question1.get('question_type') != question2.get('question_type'):
            changes.append({
                'field': 'question_type',
                'old_value': question1.get('question_type'),
                'new_value': question2.get('question_type')
            })
        
        # Compare answers
        if question1.get('answers') != question2.get('answers'):
            changes.append({
                'field': 'answers',
                'old_value': question1.get('answers'),
                'new_value': question2.get('answers')
            })
        
        # Compare tags
        if question1.get('tags') != question2.get('tags'):
            changes.append({
                'field': 'tags',
                'old_value': question1.get('tags'),
                'new_value': question2.get('tags')
            })
        
        return {
            'version1': version1,
            'version2': version2,
            'changes': changes,
            'has_changes': len(changes) > 0
        }
    
    def get_version_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about question versions.
        
        Returns:
            Version statistics
        """
        total_questions = len(self.versions)
        total_versions = sum(len(versions) for versions in self.versions.values())
        
        # Calculate average versions per question
        avg_versions = total_versions / total_questions if total_questions > 0 else 0
        
        # Find questions with most versions
        questions_by_version_count = [
            (question_id, len(versions))
            for question_id, versions in self.versions.items()
        ]
        questions_by_version_count.sort(key=lambda x: x[1], reverse=True)
        
        # Find recent activity
        recent_versions = []
        for question_id, versions in self.versions.items():
            for version in versions:
                recent_versions.append({
                    'question_id': question_id,
                    'version_id': version['version_id'],
                    'timestamp': version['timestamp'],
                    'change_description': version['change_description']
                })
        
        recent_versions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {
            'total_questions_with_versions': total_questions,
            'total_versions': total_versions,
            'average_versions_per_question': round(avg_versions, 2),
            'most_versions': questions_by_version_count[:5],
            'recent_activity': recent_versions[:10]
        }
    
    def cleanup_old_versions(self, keep_versions: int = 5) -> int:
        """
        Clean up old versions, keeping only the specified number.
        
        Args:
            keep_versions: Number of versions to keep per question
            
        Returns:
            Number of versions removed
        """
        removed_count = 0
        
        for question_id in list(self.versions.keys()):
            versions = self.versions[question_id]
            
            if len(versions) > keep_versions:
                # Keep the most recent versions
                versions_to_remove = versions[:-keep_versions]
                self.versions[question_id] = versions[-keep_versions:]
                removed_count += len(versions_to_remove)
                
                logger.info(f"Removed {len(versions_to_remove)} old versions for question {question_id}")
        
        if removed_count > 0:
            self._save_versions()
        
        return removed_count
    
    def export_question_history(self, question_id: str, output_path: str) -> bool:
        """
        Export version history for a question to a file.
        
        Args:
            question_id: ID of the question
            output_path: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            history = self.get_question_history(question_id)
            
            export_data = {
                'question_id': question_id,
                'export_timestamp': datetime.now().isoformat(),
                'version_count': len(history),
                'versions': history
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(history)} versions for question {question_id} to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting question history: {e}")
            return False
    
    def import_question_history(self, input_path: str) -> bool:
        """
        Import version history from a file.
        
        Args:
            input_path: Path to import file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(input_path):
                logger.error(f"Import file not found: {input_path}")
                return False
            
            with open(input_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            question_id = import_data.get('question_id')
            versions = import_data.get('versions', [])
            
            if not question_id or not versions:
                logger.error("Invalid import data: missing question_id or versions")
                return False
            
            # Add imported versions
            if question_id not in self.versions:
                self.versions[question_id] = []
            
            self.versions[question_id].extend(versions)
            
            # Sort by timestamp
            self.versions[question_id].sort(key=lambda x: x['timestamp'])
            
            # Save versions
            self._save_versions()
            
            logger.info(f"Imported {len(versions)} versions for question {question_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing question history: {e}")
            return False
