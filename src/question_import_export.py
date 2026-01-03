"""
Question Import/Export

This module provides functionality for importing and exporting questions
in various formats with validation and error handling.
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import csv
import os
from datetime import datetime
import logging

from question_type_validator import QuestionTypeValidator

logger = logging.getLogger(__name__)

class QuestionImportExport:
    """Handles importing and exporting questions in various formats."""
    
    def __init__(self, question_manager, tag_manager):
        """Initialize import/export functionality."""
        self.question_manager = question_manager
        self.tag_manager = tag_manager
        self.validator = QuestionTypeValidator()
    
    def export_questions_json(self, questions: List[Dict[str, Any]], output_path: str) -> bool:
        """
        Export questions to JSON format.
        
        Args:
            questions: List of questions to export
            output_path: Path to output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                'export_info': {
                    'timestamp': datetime.now().isoformat(),
                    'format_version': '1.0',
                    'question_count': len(questions),
                    'exported_by': 'Quiz Application'
                },
                'questions': questions
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(questions)} questions to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting questions to JSON: {e}")
            return False
    
    def export_questions_csv(self, questions: List[Dict[str, Any]], output_path: str) -> bool:
        """
        Export questions to CSV format.
        
        Args:
            questions: List of questions to export
            output_path: Path to output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'ID', 'Question Text', 'Question Type', 'Answers', 'Correct Answers',
                    'Tags', 'Created At', 'Last Modified', 'Usage Count'
                ])
                
                # Write questions
                for question in questions:
                    answers = question.get('answers', [])
                    answer_texts = [a.get('text', '') for a in answers]
                    correct_answers = [a.get('text', '') for a in answers if a.get('is_correct', False)]
                    
                    writer.writerow([
                        question.get('id', ''),
                        question.get('question_text', ''),
                        question.get('question_type', ''),
                        '|'.join(answer_texts),
                        '|'.join(correct_answers),
                        ','.join(question.get('tags', [])),
                        question.get('created_at', ''),
                        question.get('last_modified', ''),
                        question.get('usage_count', 0)
                    ])
            
            logger.info(f"Exported {len(questions)} questions to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting questions to CSV: {e}")
            return False
    
    def export_questions_html(self, questions: List[Dict[str, Any]], output_path: str) -> bool:
        """
        Export questions to HTML format.
        
        Args:
            questions: List of questions to export
            output_path: Path to output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            html_content = self._generate_html_export(questions)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Exported {len(questions)} questions to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting questions to HTML: {e}")
            return False
    
    def _generate_html_export(self, questions: List[Dict[str, Any]]) -> str:
        """Generate HTML content for question export."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Question Bank Export - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .question {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }}
        .question-header {{ background-color: #e9e9e9; padding: 10px; margin: -15px -15px 15px -15px; border-radius: 5px 5px 0 0; }}
        .question-text {{ font-weight: bold; margin-bottom: 10px; }}
        .answers {{ margin-left: 20px; }}
        .answer {{ margin: 5px 0; }}
        .correct {{ color: green; font-weight: bold; }}
        .incorrect {{ color: #666; }}
        .tags {{ margin-top: 10px; font-style: italic; color: #666; }}
        .metadata {{ font-size: 0.9em; color: #888; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Question Bank Export</h1>
        <p>Exported on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Questions: {len(questions)}</p>
    </div>
"""
        
        for i, question in enumerate(questions, 1):
            question_type = question.get('question_type', 'unknown')
            question_text = question.get('question_text', 'No text')
            answers = question.get('answers', [])
            tags = question.get('tags', [])
            
            html += f"""
    <div class="question">
        <div class="question-header">
            Question {i} - {question_type.replace('_', ' ').title()}
        </div>
        <div class="question-text">{question_text}</div>
        <div class="answers">
"""
            
            for j, answer in enumerate(answers, 1):
                answer_text = answer.get('text', 'No text')
                is_correct = answer.get('is_correct', False)
                answer_class = 'correct' if is_correct else 'incorrect'
                answer_marker = '✓' if is_correct else '○'
                
                html += f"""
            <div class="answer {answer_class}">
                {answer_marker} {j}. {answer_text}
            </div>
"""
            
            html += """
        </div>
"""
            
            if tags:
                html += f"""
        <div class="tags">
            Tags: {', '.join(tags)}
        </div>
"""
            
            html += f"""
        <div class="metadata">
            ID: {question.get('id', 'Unknown')} | 
            Created: {question.get('created_at', 'Unknown')} | 
            Usage: {question.get('usage_count', 0)} times
        </div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        
        return html
    
    def import_questions_json(self, input_path: str, validate: bool = True) -> Dict[str, Any]:
        """
        Import questions from JSON format.
        
        Args:
            input_path: Path to input file
            validate: Whether to validate imported questions
            
        Returns:
            Import result with success/failure information
        """
        result = {
            'success': False,
            'imported_count': 0,
            'failed_count': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON formats
            if 'questions' in data:
                questions = data['questions']
            elif isinstance(data, list):
                questions = data
            else:
                result['errors'].append("Invalid JSON format: expected 'questions' array or question list")
                return result
            
            # Import questions
            for i, question_data in enumerate(questions):
                try:
                    if validate:
                        # Validate question structure
                        validation_result = self._validate_imported_question(question_data)
                        if not validation_result['is_valid']:
                            result['errors'].append(f"Question {i+1}: {validation_result['errors']}")
                            result['failed_count'] += 1
                            continue
                    
                    # Create question
                    question = self.question_manager.create_question(
                        question_data.get('question_text', ''),
                        question_data.get('question_type', 'multiple_choice'),
                        question_data.get('answers', []),
                        question_data.get('tags', [])
                    )
                    
                    result['imported_count'] += 1
                    
                except Exception as e:
                    result['errors'].append(f"Question {i+1}: {str(e)}")
                    result['failed_count'] += 1
            
            result['success'] = result['imported_count'] > 0
            
            if result['imported_count'] > 0:
                logger.info(f"Imported {result['imported_count']} questions from {input_path}")
            
            return result
            
        except Exception as e:
            result['errors'].append(f"File error: {str(e)}")
            logger.error(f"Error importing questions from JSON: {e}")
            return result
    
    def import_questions_csv(self, input_path: str, validate: bool = True) -> Dict[str, Any]:
        """
        Import questions from CSV format.
        
        Args:
            input_path: Path to input file
            validate: Whether to validate imported questions
            
        Returns:
            Import result with success/failure information
        """
        result = {
            'success': False,
            'imported_count': 0,
            'failed_count': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(input_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader):
                    try:
                        # Parse CSV row
                        question_data = self._parse_csv_row(row)
                        
                        if validate:
                            # Validate question structure
                            validation_result = self._validate_imported_question(question_data)
                            if not validation_result['is_valid']:
                                result['errors'].append(f"Row {i+2}: {validation_result['errors']}")
                                result['failed_count'] += 1
                                continue
                        
                        # Create question
                        question = self.question_manager.create_question(
                            question_data.get('question_text', ''),
                            question_data.get('question_type', 'multiple_choice'),
                            question_data.get('answers', []),
                            question_data.get('tags', [])
                        )
                        
                        result['imported_count'] += 1
                        
                    except Exception as e:
                        result['errors'].append(f"Row {i+2}: {str(e)}")
                        result['failed_count'] += 1
            
            result['success'] = result['imported_count'] > 0
            
            if result['imported_count'] > 0:
                logger.info(f"Imported {result['imported_count']} questions from {input_path}")
            
            return result
            
        except Exception as e:
            result['errors'].append(f"File error: {str(e)}")
            logger.error(f"Error importing questions from CSV: {e}")
            return result
    
    def _parse_csv_row(self, row: Dict[str, str]) -> Dict[str, Any]:
        """Parse a CSV row into question data."""
        # Parse answers
        answer_texts = row.get('Answers', '').split('|') if row.get('Answers') else []
        correct_answers = row.get('Correct Answers', '').split('|') if row.get('Correct Answers') else []
        
        answers = []
        for answer_text in answer_texts:
            if answer_text.strip():
                answers.append({
                    'text': answer_text.strip(),
                    'is_correct': answer_text.strip() in correct_answers
                })
        
        # Parse tags
        tags = [tag.strip() for tag in row.get('Tags', '').split(',') if tag.strip()]
        
        return {
            'question_text': row.get('Question Text', '').strip(),
            'question_type': row.get('Question Type', 'multiple_choice').strip(),
            'answers': answers,
            'tags': tags
        }
    
    def _validate_imported_question(self, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate an imported question."""
        errors = []
        
        # Check required fields
        if not question_data.get('question_text'):
            errors.append("Missing question text")
        
        if not question_data.get('question_type'):
            errors.append("Missing question type")
        
        if not question_data.get('answers'):
            errors.append("Missing answers")
        
        # Validate question type
        if question_data.get('question_type'):
            type_validation = self.validator.validate_question_type(question_data['question_type'])
            if not type_validation['is_valid']:
                errors.append(f"Invalid question type: {type_validation['error']}")
        
        # Validate answers
        if question_data.get('answers') and question_data.get('question_type'):
            answer_validation = self.validator.validate_answers_for_type(
                question_data['question_type'],
                question_data['answers']
            )
            if not answer_validation['is_valid']:
                errors.extend(answer_validation['errors'])
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_export_formats(self) -> List[Dict[str, str]]:
        """Get available export formats."""
        return [
            {'format': 'json', 'description': 'JSON format with full metadata'},
            {'format': 'csv', 'description': 'CSV format for spreadsheet applications'},
            {'format': 'html', 'description': 'HTML format for web viewing'}
        ]
    
    def get_import_formats(self) -> List[Dict[str, str]]:
        """Get available import formats."""
        return [
            {'format': 'json', 'description': 'JSON format with full metadata'},
            {'format': 'csv', 'description': 'CSV format from spreadsheet applications'}
        ]
    
    def validate_import_file(self, file_path: str, format_type: str) -> Dict[str, Any]:
        """
        Validate an import file before importing.
        
        Args:
            file_path: Path to file to validate
            format_type: Format type ('json' or 'csv')
            
        Returns:
            Validation result
        """
        result = {
            'is_valid': False,
            'question_count': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            if format_type == 'json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if 'questions' in data:
                    questions = data['questions']
                elif isinstance(data, list):
                    questions = data
                else:
                    result['errors'].append("Invalid JSON format")
                    return result
                
                result['question_count'] = len(questions)
                
                # Validate each question
                for i, question in enumerate(questions):
                    validation = self._validate_imported_question(question)
                    if not validation['is_valid']:
                        result['errors'].append(f"Question {i+1}: {validation['errors']}")
                
                result['is_valid'] = len(result['errors']) == 0
                
            elif format_type == 'csv':
                with open(file_path, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    questions = list(reader)
                
                result['question_count'] = len(questions)
                
                # Check required columns
                required_columns = ['Question Text', 'Question Type', 'Answers']
                missing_columns = [col for col in required_columns if col not in reader.fieldnames]
                if missing_columns:
                    result['errors'].append(f"Missing required columns: {', '.join(missing_columns)}")
                    return result
                
                # Validate each question
                for i, row in enumerate(questions):
                    try:
                        question_data = self._parse_csv_row(row)
                        validation = self._validate_imported_question(question_data)
                        if not validation['is_valid']:
                            result['errors'].append(f"Row {i+2}: {validation['errors']}")
                    except Exception as e:
                        result['errors'].append(f"Row {i+2}: {str(e)}")
                
                result['is_valid'] = len(result['errors']) == 0
            
            else:
                result['errors'].append(f"Unsupported format: {format_type}")
            
        except Exception as e:
            result['errors'].append(f"File error: {str(e)}")
        
        return result
