"""
File Export System

This module provides comprehensive file export functionality with multiple formats,
compression, and professional layouts.
"""

import os
import json
import csv
import logging
import gzip
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import hashlib
import tempfile

# PDF export dependencies
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

logger = logging.getLogger(__name__)

class FileExporter:
    """Comprehensive file export system with multiple formats and compression."""
    
    def __init__(self, export_dir: str = "data/exports"):
        """
        Initialize the file exporter.
        
        Args:
            export_dir: Directory for storing export files
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Export statistics
        self.export_stats = {
            'total_exports': 0,
            'successful_exports': 0,
            'failed_exports': 0,
            'total_questions_exported': 0,
            'total_tags_exported': 0,
            'total_sessions_exported': 0
        }
        
        # Supported formats
        self.supported_formats = {
            'json': self._export_json,
            'csv': self._export_csv,
            'pdf': self._export_pdf,
            'xml': self._export_xml,
            'html': self._export_html
        }
        
        logger.info("File exporter initialized")
    
    def export_data(self, data: Dict[str, Any], 
                   export_format: str,
                   output_path: str = None,
                   export_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export data to specified format.
        
        Args:
            data: Data to export
            export_format: Export format ('json', 'csv', 'pdf', 'xml', 'html')
            output_path: Output file path (optional)
            export_options: Custom export options
            
        Returns:
            Dictionary containing export results
        """
        if export_format not in self.supported_formats:
            return {
                'success': False,
                'error': f'Unsupported export format: {export_format}',
                'output_path': '',
                'file_size': 0,
                'processing_time': 0
            }
        
        start_time = datetime.now()
        
        try:
            # Generate output path if not provided
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.export_dir / f"export_{timestamp}.{export_format}"
            
            # Apply export options
            if not export_options:
                export_options = {}
            
            # Export data
            export_result = self.supported_formats[export_format](
                data, output_path, export_options
            )
            
            if not export_result['success']:
                return export_result
            
            # Apply compression if needed
            if export_options.get('compress', False) and os.path.getsize(output_path) > 1024 * 1024:  # > 1MB
                compressed_path = self._compress_file(output_path)
                if compressed_path:
                    os.remove(output_path)
                    output_path = compressed_path
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_export_statistics(True, data)
            
            result = {
                'success': True,
                'output_path': str(output_path),
                'file_size': os.path.getsize(output_path),
                'processing_time': processing_time,
                'export_format': export_format,
                'compressed': export_options.get('compress', False),
                'data_hash': self._calculate_data_hash(data)
            }
            
            logger.info(f"Successfully exported data to {output_path} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            self._update_export_statistics(False, data)
            
            return {
                'success': False,
                'error': str(e),
                'output_path': '',
                'file_size': 0,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    def batch_export_data(self, data_list: List[Dict[str, Any]], 
                         export_format: str,
                         output_dir: str = None,
                         export_options: Dict[str, Any] = None,
                         progress_callback: callable = None) -> Dict[str, Any]:
        """
        Export multiple datasets in batch.
        
        Args:
            data_list: List of data dictionaries to export
            export_format: Export format for all files
            output_dir: Output directory (optional)
            export_options: Custom export options
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary containing batch export results
        """
        if not output_dir:
            output_dir = self.export_dir / f"batch_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = datetime.now()
        results = []
        successful = 0
        failed = 0
        
        logger.info(f"Starting batch export of {len(data_list)} datasets")
        
        for i, data in enumerate(data_list):
            try:
                # Generate output path
                output_path = output_dir / f"export_{i+1:03d}.{export_format}"
                
                # Export data
                result = self.export_data(data, export_format, str(output_path), export_options)
                results.append({
                    'index': i,
                    'output_path': str(output_path),
                    'result': result
                })
                
                if result['success']:
                    successful += 1
                else:
                    failed += 1
                
                # Update progress
                if progress_callback:
                    progress = (i + 1) / len(data_list) * 100
                    progress_callback(progress, f"Exported {i + 1}/{len(data_list)} datasets")
                
                logger.info(f"Exported {i + 1}/{len(data_list)}: {output_path}")
                
            except Exception as e:
                logger.error(f"Error in batch export for dataset {i}: {e}")
                results.append({
                    'index': i,
                    'output_path': '',
                    'result': {
                        'success': False,
                        'error': str(e),
                        'file_size': 0
                    }
                })
                failed += 1
        
        # Calculate summary statistics
        total_time = (datetime.now() - start_time).total_seconds()
        
        summary = {
            'total_datasets': len(data_list),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(data_list)) * 100,
            'total_processing_time': total_time,
            'average_processing_time': total_time / len(data_list),
            'output_directory': str(output_dir)
        }
        
        logger.info(f"Batch export completed: {successful}/{len(data_list)} successful ({summary['success_rate']:.1f}%)")
        
        return {
            'success': failed == 0,
            'results': results,
            'summary': summary,
            'error': None if failed == 0 else f"{failed} datasets failed to export"
        }
    
    def _export_json(self, data: Dict[str, Any], output_path: str, 
                    export_options: Dict[str, Any]) -> Dict[str, Any]:
        """Export data to JSON format."""
        try:
            # Prepare export data
            export_data = self._prepare_export_data(data, export_options)
            
            # Write JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str, ensure_ascii=False)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}")
            return {'success': False, 'error': str(e)}
    
    def _export_csv(self, data: Dict[str, Any], output_path: str, 
                   export_options: Dict[str, Any]) -> Dict[str, Any]:
        """Export data to CSV format."""
        try:
            questions = data.get('questions', [])
            if not questions:
                return {'success': False, 'error': 'No questions to export'}
            
            # Determine CSV structure
            include_answers = export_options.get('include_answers', True)
            include_tags = export_options.get('include_tags', True)
            include_metadata = export_options.get('include_metadata', False)
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                headers = ['id', 'question_text', 'question_type']
                
                if include_answers:
                    max_answers = max(len(q.get('answers', [])) for q in questions) if questions else 0
                    for i in range(max_answers):
                        headers.extend([f'answer_{i+1}', f'correct_{i+1}'])
                
                if include_tags:
                    headers.append('tags')
                
                if include_metadata:
                    headers.extend(['created_at', 'source'])
                
                writer.writerow(headers)
                
                # Write data rows
                for question in questions:
                    row = [
                        question.get('id', ''),
                        question.get('question_text', ''),
                        question.get('question_type', 'multiple_choice')
                    ]
                    
                    if include_answers:
                        answers = question.get('answers', [])
                        for i in range(max_answers):
                            if i < len(answers):
                                row.extend([
                                    answers[i].get('text', ''),
                                    'true' if answers[i].get('is_correct', False) else 'false'
                                ])
                            else:
                                row.extend(['', 'false'])
                    
                    if include_tags:
                        tags = question.get('tags', [])
                        row.append(','.join(tags))
                    
                    if include_metadata:
                        row.extend([
                            question.get('created_at', ''),
                            question.get('source', '')
                        ])
                    
                    writer.writerow(row)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return {'success': False, 'error': str(e)}
    
    def _export_pdf(self, data: Dict[str, Any], output_path: str, 
                   export_options: Dict[str, Any]) -> Dict[str, Any]:
        """Export data to PDF format."""
        if not PDF_AVAILABLE:
            return {'success': False, 'error': 'PDF export not available. Install reportlab.'}
        
        try:
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph("Quiz Export", title_style))
            story.append(Spacer(1, 12))
            
            # Export metadata
            metadata = data.get('metadata', {})
            if metadata:
                story.append(Paragraph(f"<b>Export Date:</b> {metadata.get('export_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}", styles['Normal']))
                story.append(Paragraph(f"<b>Total Questions:</b> {len(data.get('questions', []))}", styles['Normal']))
                story.append(Spacer(1, 12))
            
            # Export questions
            questions = data.get('questions', [])
            for i, question in enumerate(questions, 1):
                # Question text
                story.append(Paragraph(f"<b>Question {i}:</b> {question.get('question_text', '')}", styles['Normal']))
                story.append(Spacer(1, 6))
                
                # Answers
                answers = question.get('answers', [])
                if answers:
                    answer_data = [['Answer', 'Correct']]
                    for answer in answers:
                        answer_data.append([
                            answer.get('text', ''),
                            '✓' if answer.get('is_correct', False) else '✗'
                        ])
                    
                    answer_table = Table(answer_data)
                    answer_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(answer_table)
                
                # Tags
                tags = question.get('tags', [])
                if tags:
                    story.append(Paragraph(f"<b>Tags:</b> {', '.join(tags)}", styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            # Build PDF
            doc.build(story)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            return {'success': False, 'error': str(e)}
    
    def _export_xml(self, data: Dict[str, Any], output_path: str, 
                   export_options: Dict[str, Any]) -> Dict[str, Any]:
        """Export data to XML format."""
        try:
            import xml.etree.ElementTree as ET
            
            # Create root element
            root = ET.Element('quiz_export')
            root.set('export_date', datetime.now().isoformat())
            root.set('version', '1.0')
            
            # Add metadata
            metadata = data.get('metadata', {})
            if metadata:
                meta_elem = ET.SubElement(root, 'metadata')
                for key, value in metadata.items():
                    meta_elem.set(key, str(value))
            
            # Add questions
            questions = data.get('questions', [])
            questions_elem = ET.SubElement(root, 'questions')
            for question in questions:
                q_elem = ET.SubElement(questions_elem, 'question')
                q_elem.set('id', question.get('id', ''))
                q_elem.set('type', question.get('question_type', 'multiple_choice'))
                
                # Question text
                text_elem = ET.SubElement(q_elem, 'text')
                text_elem.text = question.get('question_text', '')
                
                # Answers
                answers = question.get('answers', [])
                if answers:
                    answers_elem = ET.SubElement(q_elem, 'answers')
                    for answer in answers:
                        answer_elem = ET.SubElement(answers_elem, 'answer')
                        answer_elem.set('correct', 'true' if answer.get('is_correct', False) else 'false')
                        answer_elem.text = answer.get('text', '')
                
                # Tags
                tags = question.get('tags', [])
                if tags:
                    tags_elem = ET.SubElement(q_elem, 'tags')
                    for tag in tags:
                        tag_elem = ET.SubElement(tags_elem, 'tag')
                        tag_elem.text = tag
            
            # Add tags
            tags_data = data.get('tags', [])
            if tags_data:
                tags_elem = ET.SubElement(root, 'tags')
                for tag in tags_data:
                    tag_elem = ET.SubElement(tags_elem, 'tag')
                    tag_elem.set('id', tag.get('id', ''))
                    
                    name_elem = ET.SubElement(tag_elem, 'name')
                    name_elem.text = tag.get('name', '')
                    
                    desc_elem = ET.SubElement(tag_elem, 'description')
                    desc_elem.text = tag.get('description', '')
            
            # Write XML file
            tree = ET.ElementTree(root)
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error exporting XML: {e}")
            return {'success': False, 'error': str(e)}
    
    def _export_html(self, data: Dict[str, Any], output_path: str, 
                    export_options: Dict[str, Any]) -> Dict[str, Any]:
        """Export data to HTML format."""
        try:
            html_content = self._generate_html_content(data, export_options)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error exporting HTML: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_html_content(self, data: Dict[str, Any], export_options: Dict[str, Any]) -> str:
        """Generate HTML content for export."""
        metadata = data.get('metadata', {})
        questions = data.get('questions', [])
        tags = data.get('tags', [])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz Export - {metadata.get('export_date', datetime.now().strftime('%Y-%m-%d'))}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .question {{
            margin-bottom: 30px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }}
        .question-text {{
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .answers {{
            margin-left: 20px;
        }}
        .answer {{
            margin-bottom: 5px;
        }}
        .correct {{
            color: green;
            font-weight: bold;
        }}
        .incorrect {{
            color: red;
        }}
        .tags {{
            margin-top: 10px;
            font-style: italic;
            color: #666;
        }}
        .metadata {{
            background-color: #e9e9e9;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Quiz Export</h1>
        <p>Generated on {metadata.get('export_date', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}</p>
    </div>
    
    <div class="metadata">
        <h3>Export Information</h3>
        <p><strong>Total Questions:</strong> {len(questions)}</p>
        <p><strong>Total Tags:</strong> {len(tags)}</p>
        <p><strong>Export Format:</strong> HTML</p>
    </div>
"""
        
        # Add questions
        for i, question in enumerate(questions, 1):
            html += f"""
    <div class="question">
        <div class="question-text">Question {i}: {question.get('question_text', '')}</div>
        <div class="answers">
"""
            
            answers = question.get('answers', [])
            for answer in answers:
                correct_class = 'correct' if answer.get('is_correct', False) else 'incorrect'
                html += f'            <div class="answer {correct_class}">{answer.get("text", "")}</div>\n'
            
            html += "        </div>\n"
            
            # Add tags
            question_tags = question.get('tags', [])
            if question_tags:
                html += f'        <div class="tags">Tags: {", ".join(question_tags)}</div>\n'
            
            html += "    </div>\n"
        
        html += """
</body>
</html>
"""
        
        return html
    
    def _prepare_export_data(self, data: Dict[str, Any], export_options: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for export with options."""
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'export_format': 'json',
                'version': '1.0',
                **data.get('metadata', {})
            },
            'questions': data.get('questions', []),
            'tags': data.get('tags', []),
            'sessions': data.get('sessions', [])
        }
        
        # Apply export options
        if export_options.get('include_metadata', True):
            export_data['metadata'].update({
                'total_questions': len(export_data['questions']),
                'total_tags': len(export_data['tags']),
                'total_sessions': len(export_data['sessions'])
            })
        
        return export_data
    
    def _compress_file(self, file_path: str) -> Optional[str]:
        """Compress file using gzip."""
        try:
            compressed_path = f"{file_path}.gz"
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            logger.info(f"File compressed: {file_path} -> {compressed_path}")
            return compressed_path
            
        except Exception as e:
            logger.error(f"Error compressing file {file_path}: {e}")
            return None
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash for exported data."""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating data hash: {e}")
            return ""
    
    def _update_export_statistics(self, success: bool, data: Dict[str, Any]) -> None:
        """Update export statistics."""
        self.export_stats['total_exports'] += 1
        
        if success:
            self.export_stats['successful_exports'] += 1
            self.export_stats['total_questions_exported'] += len(data.get('questions', []))
            self.export_stats['total_tags_exported'] += len(data.get('tags', []))
            self.export_stats['total_sessions_exported'] += len(data.get('sessions', []))
        else:
            self.export_stats['failed_exports'] += 1
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """Get export statistics."""
        return self.export_stats.copy()
    
    def clear_export_statistics(self) -> None:
        """Clear export statistics."""
        self.export_stats = {
            'total_exports': 0,
            'successful_exports': 0,
            'failed_exports': 0,
            'total_questions_exported': 0,
            'total_tags_exported': 0,
            'total_sessions_exported': 0
        }
        logger.info("Export statistics cleared")
