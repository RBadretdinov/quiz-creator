"""
File Import System

This module provides comprehensive file import functionality with validation,
error handling, and batch processing capabilities.
"""

import os
import json
import csv
import logging
import gzip
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import hashlib
import shutil

logger = logging.getLogger(__name__)

class FileImporter:
    """Comprehensive file import system with validation and error handling."""
    
    def __init__(self, import_dir: str = "data/imports"):
        """
        Initialize the file importer.
        
        Args:
            import_dir: Directory for storing import files and logs
        """
        self.import_dir = Path(import_dir)
        self.import_dir.mkdir(parents=True, exist_ok=True)
        
        # Import statistics
        self.import_stats = {
            'total_imports': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'total_files_processed': 0,
            'total_questions_imported': 0,
            'total_tags_imported': 0
        }
        
        # Supported formats
        self.supported_formats = {
            '.json': self._import_json,
            '.csv': self._import_csv,
            '.xml': self._import_xml,
            '.txt': self._import_text
        }
        
        logger.info("File importer initialized")
    
    def import_file(self, file_path: str, 
                   import_type: str = 'auto',
                   validation_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Import a single file with comprehensive validation.
        
        Args:
            file_path: Path to the file to import
            import_type: Type of import ('auto', 'questions', 'tags', 'sessions')
            validation_options: Custom validation options
            
        Returns:
            Dictionary containing import results
        """
        if not os.path.exists(file_path):
            return {
                'success': False,
                'error': f'File not found: {file_path}',
                'imported_data': {},
                'validation_errors': [],
                'processing_time': 0
            }
        
        start_time = datetime.now()
        
        try:
            # Validate file format
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                return {
                    'success': False,
                    'error': f'Unsupported file format: {file_ext}',
                    'imported_data': {},
                    'validation_errors': [f'Unsupported format: {file_ext}'],
                    'processing_time': 0
                }
            
            # Auto-detect import type if needed
            if import_type == 'auto':
                import_type = self._detect_import_type(file_path)
            
            # Load and validate file
            raw_data = self._load_file(file_path)
            if not raw_data:
                return {
                    'success': False,
                    'error': 'Failed to load file data',
                    'imported_data': {},
                    'validation_errors': ['Failed to load file'],
                    'processing_time': 0
                }
            
            # Validate data structure
            validation_result = self._validate_import_data(raw_data, import_type, validation_options)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': 'Data validation failed',
                    'imported_data': {},
                    'validation_errors': validation_result['errors'],
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }
            
            # Process import
            processed_data = self._process_import_data(raw_data, import_type)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_import_statistics(True, 1, len(processed_data.get('questions', [])))
            
            result = {
                'success': True,
                'imported_data': processed_data,
                'validation_errors': [],
                'processing_time': processing_time,
                'import_type': import_type,
                'file_size': os.path.getsize(file_path),
                'data_hash': self._calculate_data_hash(processed_data)
            }
            
            logger.info(f"Successfully imported {file_path} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error importing file {file_path}: {e}")
            self._update_import_statistics(False, 1, 0)
            
            return {
                'success': False,
                'error': str(e),
                'imported_data': {},
                'validation_errors': [str(e)],
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def batch_import_files(self, file_paths: List[str], 
                          import_type: str = 'auto',
                          validation_options: Dict[str, Any] = None,
                          progress_callback: callable = None) -> Dict[str, Any]:
        """
        Import multiple files in batch with progress tracking.
        
        Args:
            file_paths: List of file paths to import
            import_type: Type of import for all files
            validation_options: Custom validation options
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary containing batch import results
        """
        start_time = datetime.now()
        results = []
        successful = 0
        failed = 0
        total_questions = 0
        total_tags = 0
        
        logger.info(f"Starting batch import of {len(file_paths)} files")
        
        for i, file_path in enumerate(file_paths):
            try:
                # Import individual file
                result = self.import_file(file_path, import_type, validation_options)
                results.append({
                    'file_path': file_path,
                    'result': result
                })
                
                if result['success']:
                    successful += 1
                    total_questions += len(result['imported_data'].get('questions', []))
                    total_tags += len(result['imported_data'].get('tags', []))
                else:
                    failed += 1
                
                # Update progress
                if progress_callback:
                    progress = (i + 1) / len(file_paths) * 100
                    progress_callback(progress, f"Processed {i + 1}/{len(file_paths)} files")
                
                logger.info(f"Processed {i + 1}/{len(file_paths)}: {file_path}")
                
            except Exception as e:
                logger.error(f"Error in batch import for {file_path}: {e}")
                results.append({
                    'file_path': file_path,
                    'result': {
                        'success': False,
                        'error': str(e),
                        'imported_data': {},
                        'validation_errors': [str(e)]
                    }
                })
                failed += 1
        
        # Calculate summary statistics
        total_time = (datetime.now() - start_time).total_seconds()
        
        summary = {
            'total_files': len(file_paths),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(file_paths)) * 100,
            'total_questions': total_questions,
            'total_tags': total_tags,
            'total_processing_time': total_time,
            'average_processing_time': total_time / len(file_paths)
        }
        
        logger.info(f"Batch import completed: {successful}/{len(file_paths)} successful ({summary['success_rate']:.1f}%)")
        
        return {
            'success': failed == 0,
            'results': results,
            'summary': summary,
            'error': None if failed == 0 else f"{failed} files failed to import"
        }
    
    def _load_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load file data based on file extension."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in self.supported_formats:
            return self.supported_formats[file_ext](file_path)
        else:
            logger.error(f"Unsupported file format: {file_ext}")
            return None
    
    def _import_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Successfully loaded JSON file: {file_path}")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading JSON file {file_path}: {e}")
            return None
    
    def _import_csv(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import CSV file and convert to structured format."""
        try:
            questions = []
            tags = []
            
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Convert CSV row to question format
                    question = self._csv_row_to_question(row)
                    if question:
                        questions.append(question)
                    
                    # Extract tags from CSV
                    if 'tags' in row and row['tags']:
                        for tag_name in row['tags'].split(','):
                            tag_name = tag_name.strip()
                            if tag_name and not any(t['name'] == tag_name for t in tags):
                                tags.append({
                                    'id': f"imported_{len(tags)}",
                                    'name': tag_name,
                                    'description': f"Imported from {Path(file_path).name}",
                                    'created_at': datetime.now().isoformat()
                                })
            
            result = {
                'questions': questions,
                'tags': tags,
                'metadata': {
                    'source_file': file_path,
                    'import_date': datetime.now().isoformat(),
                    'total_questions': len(questions),
                    'total_tags': len(tags)
                }
            }
            
            logger.debug(f"Successfully loaded CSV file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            return None
    
    def _import_xml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import XML file and convert to structured format."""
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            questions = []
            tags = []
            
            # Parse XML structure (assuming standard quiz format)
            for question_elem in root.findall('.//question'):
                question = self._xml_element_to_question(question_elem)
                if question:
                    questions.append(question)
            
            for tag_elem in root.findall('.//tag'):
                tag = self._xml_element_to_tag(tag_elem)
                if tag:
                    tags.append(tag)
            
            result = {
                'questions': questions,
                'tags': tags,
                'metadata': {
                    'source_file': file_path,
                    'import_date': datetime.now().isoformat(),
                    'total_questions': len(questions),
                    'total_tags': len(tags)
                }
            }
            
            logger.debug(f"Successfully loaded XML file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error loading XML file {file_path}: {e}")
            return None
    
    def _import_text(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Import plain text file and convert to structured format."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple text parsing (can be enhanced)
            questions = self._parse_text_content(content)
            
            result = {
                'questions': questions,
                'tags': [],
                'metadata': {
                    'source_file': file_path,
                    'import_date': datetime.now().isoformat(),
                    'total_questions': len(questions),
                    'total_tags': 0
                }
            }
            
            logger.debug(f"Successfully loaded text file: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            return None
    
    def _csv_row_to_question(self, row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Convert CSV row to question format."""
        try:
            question_text = row.get('question', '').strip()
            if not question_text:
                return None
            
            # Parse answers
            answers = []
            for i in range(1, 6):  # Support up to 5 answers
                answer_text = row.get(f'answer_{i}', '').strip()
                if answer_text:
                    is_correct = row.get(f'correct_{i}', '').lower() in ['true', '1', 'yes']
                    answers.append({
                        'id': f"answer_{i}",
                        'text': answer_text,
                        'is_correct': is_correct
                    })
            
            # Determine question type
            question_type = row.get('type', 'multiple_choice').lower()
            if question_type not in ['multiple_choice', 'true_false', 'select_all']:
                question_type = 'multiple_choice'
            
            return {
                'id': f"imported_{hash(question_text)}",
                'question_text': question_text,
                'question_type': question_type,
                'answers': answers,
                'tags': [tag.strip() for tag in row.get('tags', '').split(',') if tag.strip()],
                'created_at': datetime.now().isoformat(),
                'source': 'csv_import'
            }
            
        except Exception as e:
            logger.error(f"Error converting CSV row to question: {e}")
            return None
    
    def _xml_element_to_question(self, element) -> Optional[Dict[str, Any]]:
        """Convert XML element to question format."""
        try:
            question_text = element.find('text')
            if question_text is None or not question_text.text:
                return None
            
            answers = []
            for answer_elem in element.findall('answer'):
                answer_text = answer_elem.text
                is_correct = answer_elem.get('correct', 'false').lower() == 'true'
                if answer_text:
                    answers.append({
                        'id': f"answer_{len(answers)}",
                        'text': answer_text,
                        'is_correct': is_correct
                    })
            
            question_type = element.get('type', 'multiple_choice')
            
            return {
                'id': f"imported_{hash(question_text.text)}",
                'question_text': question_text.text,
                'question_type': question_type,
                'answers': answers,
                'tags': [tag.text for tag in element.findall('tag') if tag.text],
                'created_at': datetime.now().isoformat(),
                'source': 'xml_import'
            }
            
        except Exception as e:
            logger.error(f"Error converting XML element to question: {e}")
            return None
    
    def _xml_element_to_tag(self, element) -> Optional[Dict[str, Any]]:
        """Convert XML element to tag format."""
        try:
            name = element.find('name')
            description = element.find('description')
            
            if name is None or not name.text:
                return None
            
            return {
                'id': f"imported_{hash(name.text)}",
                'name': name.text,
                'description': description.text if description is not None else '',
                'created_at': datetime.now().isoformat(),
                'source': 'xml_import'
            }
            
        except Exception as e:
            logger.error(f"Error converting XML element to tag: {e}")
            return None
    
    def _parse_text_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse plain text content into questions."""
        questions = []
        lines = content.split('\n')
        current_question = None
        current_answers = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Simple question detection
            if line.endswith('?') or line.startswith(('What', 'Which', 'How', 'When', 'Where', 'Why', 'Who')):
                # Save previous question
                if current_question:
                    questions.append({
                        'id': f"imported_{hash(current_question)}",
                        'question_text': current_question,
                        'question_type': 'multiple_choice',
                        'answers': current_answers,
                        'tags': [],
                        'created_at': datetime.now().isoformat(),
                        'source': 'text_import'
                    })
                
                # Start new question
                current_question = line
                current_answers = []
            
            # Answer detection
            elif line.startswith(('-', '*', '•')) or line.startswith(('A.', 'B.', 'C.', 'D.')):
                answer_text = line.lstrip('-*•').strip()
                if answer_text.startswith(('A.', 'B.', 'C.', 'D.')):
                    answer_text = answer_text[2:].strip()
                
                if answer_text:
                    current_answers.append({
                        'id': f"answer_{len(current_answers)}",
                        'text': answer_text,
                        'is_correct': False  # Default to false, needs manual correction
                    })
        
        # Add last question
        if current_question:
            questions.append({
                'id': f"imported_{hash(current_question)}",
                'question_text': current_question,
                'question_type': 'multiple_choice',
                'answers': current_answers,
                'tags': [],
                'created_at': datetime.now().isoformat(),
                'source': 'text_import'
            })
        
        return questions
    
    def _detect_import_type(self, file_path: str) -> str:
        """Auto-detect import type based on file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Read first 1000 characters
            
            # Check for JSON structure
            if content.strip().startswith('{') or content.strip().startswith('['):
                return 'json'
            
            # Check for CSV structure
            if ',' in content and '\n' in content:
                return 'csv'
            
            # Check for XML structure
            if content.strip().startswith('<'):
                return 'xml'
            
            # Default to text
            return 'text'
            
        except Exception as e:
            logger.error(f"Error detecting import type for {file_path}: {e}")
            return 'text'
    
    def _validate_import_data(self, data: Dict[str, Any], 
                            import_type: str, 
                            validation_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Validate imported data structure."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append("Data must be a dictionary")
            return {'valid': False, 'errors': errors}
        
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
    
    def _process_import_data(self, data: Dict[str, Any], import_type: str) -> Dict[str, Any]:
        """Process and clean imported data."""
        processed_data = {
            'questions': [],
            'tags': [],
            'metadata': data.get('metadata', {})
        }
        
        # Process questions
        if 'questions' in data:
            for question in data['questions']:
                processed_question = self._clean_question_data(question)
                if processed_question:
                    processed_data['questions'].append(processed_question)
        
        # Process tags
        if 'tags' in data:
            for tag in data['tags']:
                processed_tag = self._clean_tag_data(tag)
                if processed_tag:
                    processed_data['tags'].append(processed_tag)
        
        return processed_data
    
    def _clean_question_data(self, question: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and validate question data."""
        try:
            # Ensure required fields
            if 'question_text' not in question or not question['question_text']:
                return None
            
            # Clean question text
            question_text = str(question['question_text']).strip()
            if not question_text:
                return None
            
            # Clean answers
            answers = []
            if 'answers' in question and isinstance(question['answers'], list):
                for answer in question['answers']:
                    if isinstance(answer, dict) and 'text' in answer:
                        answer_text = str(answer['text']).strip()
                        if answer_text:
                            answers.append({
                                'id': answer.get('id', f"answer_{len(answers)}"),
                                'text': answer_text,
                                'is_correct': bool(answer.get('is_correct', False))
                            })
            
            # Clean tags
            tags = []
            if 'tags' in question and isinstance(question['tags'], list):
                for tag in question['tags']:
                    if isinstance(tag, str) and tag.strip():
                        tags.append(tag.strip())
            
            return {
                'id': question.get('id', f"imported_{hash(question_text)}"),
                'question_text': question_text,
                'question_type': question.get('question_type', 'multiple_choice'),
                'answers': answers,
                'tags': tags,
                'created_at': question.get('created_at', datetime.now().isoformat()),
                'source': question.get('source', 'import')
            }
            
        except Exception as e:
            logger.error(f"Error cleaning question data: {e}")
            return None
    
    def _clean_tag_data(self, tag: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Clean and validate tag data."""
        try:
            if 'name' not in tag or not tag['name']:
                return None
            
            name = str(tag['name']).strip()
            if not name:
                return None
            
            return {
                'id': tag.get('id', f"imported_{hash(name)}"),
                'name': name,
                'description': str(tag.get('description', '')).strip(),
                'created_at': tag.get('created_at', datetime.now().isoformat()),
                'source': tag.get('source', 'import')
            }
            
        except Exception as e:
            logger.error(f"Error cleaning tag data: {e}")
            return None
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for imported data."""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating data hash: {e}")
            return ""
    
    def _update_import_statistics(self, success: bool, files_processed: int, questions_imported: int) -> None:
        """Update import statistics."""
        self.import_stats['total_imports'] += 1
        self.import_stats['total_files_processed'] += files_processed
        self.import_stats['total_questions_imported'] += questions_imported
        
        if success:
            self.import_stats['successful_imports'] += 1
        else:
            self.import_stats['failed_imports'] += 1
    
    def get_import_statistics(self) -> Dict[str, Any]:
        """Get import statistics."""
        return self.import_stats.copy()
    
    def clear_import_statistics(self) -> None:
        """Clear import statistics."""
        self.import_stats = {
            'total_imports': 0,
            'successful_imports': 0,
            'failed_imports': 0,
            'total_files_processed': 0,
            'total_questions_imported': 0,
            'total_tags_imported': 0
        }
        logger.info("Import statistics cleared")
