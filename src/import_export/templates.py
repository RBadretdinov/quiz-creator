"""
Import/Export Templates and Presets

This module provides predefined templates and presets for common
import/export scenarios and data migration patterns.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

class ImportExportTemplates:
    """Template system for import/export operations."""
    
    def __init__(self, templates_dir: str = "data/templates"):
        """
        Initialize the template system.
        
        Args:
            templates_dir: Directory for storing template files
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize default templates
        self._initialize_default_templates()
        
        logger.info("Import/export templates initialized")
    
    def get_export_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get export template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template dictionary or None if not found
        """
        return self._templates.get(template_name)
    
    def get_import_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get import template by name.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Template dictionary or None if not found
        """
        return self._import_templates.get(template_name)
    
    def create_custom_template(self, template_name: str, 
                              template_data: Dict[str, Any],
                              template_type: str = 'export') -> bool:
        """
        Create a custom template.
        
        Args:
            template_name: Name for the template
            template_data: Template configuration
            template_type: Type of template ('export' or 'import')
            
        Returns:
            True if template created successfully
        """
        try:
            template_data['created_at'] = datetime.now().isoformat()
            template_data['template_type'] = template_type
            
            if template_type == 'export':
                self._templates[template_name] = template_data
            else:
                self._import_templates[template_name] = template_data
            
            # Save template to file
            template_file = self.templates_dir / f"{template_name}_{template_type}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, default=str)
            
            logger.info(f"Custom template '{template_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom template '{template_name}': {e}")
            return False
    
    def get_available_templates(self) -> Dict[str, List[str]]:
        """Get list of available templates."""
        return {
            'export_templates': list(self._templates.keys()),
            'import_templates': list(self._import_templates.keys())
        }
    
    def _initialize_default_templates(self):
        """Initialize default templates."""
        self._templates = {
            'basic_export': {
                'name': 'Basic Export',
                'description': 'Basic export with questions and tags',
                'format': 'json',
                'options': {
                    'include_metadata': True,
                    'include_questions': True,
                    'include_tags': True,
                    'include_sessions': False,
                    'compress': False
                },
                'fields': {
                    'questions': ['id', 'question_text', 'question_type', 'answers', 'tags'],
                    'tags': ['id', 'name', 'description'],
                    'metadata': ['export_date', 'total_questions', 'total_tags']
                }
            },
            'csv_export': {
                'name': 'CSV Export',
                'description': 'Export to CSV format for spreadsheet compatibility',
                'format': 'csv',
                'options': {
                    'include_answers': True,
                    'include_tags': True,
                    'include_metadata': False,
                    'separator': ',',
                    'encoding': 'utf-8'
                },
                'fields': {
                    'questions': ['id', 'question_text', 'question_type', 'answer_1', 'correct_1', 'answer_2', 'correct_2', 'answer_3', 'correct_3', 'answer_4', 'correct_4', 'answer_5', 'correct_5', 'tags'],
                    'tags': ['id', 'name', 'description']
                }
            },
            'pdf_export': {
                'name': 'PDF Export',
                'description': 'Export to PDF format for printing',
                'format': 'pdf',
                'options': {
                    'include_answers': True,
                    'include_tags': True,
                    'include_metadata': True,
                    'page_size': 'A4',
                    'font_size': 12
                },
                'fields': {
                    'questions': ['question_text', 'answers', 'tags'],
                    'metadata': ['export_date', 'total_questions']
                }
            },
            'html_export': {
                'name': 'HTML Export',
                'description': 'Export to HTML format for web display',
                'format': 'html',
                'options': {
                    'include_answers': True,
                    'include_tags': True,
                    'include_metadata': True,
                    'include_styling': True,
                    'responsive': True
                },
                'fields': {
                    'questions': ['question_text', 'answers', 'tags'],
                    'metadata': ['export_date', 'total_questions', 'total_tags']
                }
            },
            'xml_export': {
                'name': 'XML Export',
                'description': 'Export to XML format for data exchange',
                'format': 'xml',
                'options': {
                    'include_answers': True,
                    'include_tags': True,
                    'include_metadata': True,
                    'pretty_print': True,
                    'encoding': 'utf-8'
                },
                'fields': {
                    'questions': ['id', 'question_text', 'question_type', 'answers', 'tags'],
                    'tags': ['id', 'name', 'description'],
                    'metadata': ['export_date', 'version']
                }
            },
            'compressed_export': {
                'name': 'Compressed Export',
                'description': 'Compressed export for large datasets',
                'format': 'json',
                'options': {
                    'include_metadata': True,
                    'include_questions': True,
                    'include_tags': True,
                    'include_sessions': True,
                    'compress': True,
                    'compression_level': 9
                },
                'fields': {
                    'questions': ['id', 'question_text', 'question_type', 'answers', 'tags', 'created_at'],
                    'tags': ['id', 'name', 'description', 'created_at'],
                    'sessions': ['id', 'user_id', 'start_time', 'end_time', 'score', 'total_questions']
                }
            }
        }
        
        self._import_templates = {
            'basic_import': {
                'name': 'Basic Import',
                'description': 'Basic import from JSON format',
                'format': 'json',
                'options': {
                    'validate_data': True,
                    'create_missing_tags': True,
                    'overwrite_existing': False,
                    'backup_before_import': True
                },
                'validation': {
                    'required_fields': ['questions'],
                    'optional_fields': ['tags', 'metadata'],
                    'question_required': ['question_text', 'answers'],
                    'tag_required': ['name']
                }
            },
            'csv_import': {
                'name': 'CSV Import',
                'description': 'Import from CSV format',
                'format': 'csv',
                'options': {
                    'validate_data': True,
                    'create_missing_tags': True,
                    'overwrite_existing': False,
                    'backup_before_import': True,
                    'encoding': 'utf-8',
                    'delimiter': ','
                },
                'validation': {
                    'required_fields': ['question_text'],
                    'optional_fields': ['answer_1', 'answer_2', 'answer_3', 'answer_4', 'answer_5', 'tags'],
                    'question_required': ['question_text'],
                    'tag_required': ['name']
                }
            },
            'xml_import': {
                'name': 'XML Import',
                'description': 'Import from XML format',
                'format': 'xml',
                'options': {
                    'validate_data': True,
                    'create_missing_tags': True,
                    'overwrite_existing': False,
                    'backup_before_import': True,
                    'encoding': 'utf-8'
                },
                'validation': {
                    'required_fields': ['questions'],
                    'optional_fields': ['tags', 'metadata'],
                    'question_required': ['text', 'answers'],
                    'tag_required': ['name']
                }
            },
            'text_import': {
                'name': 'Text Import',
                'description': 'Import from plain text format',
                'format': 'text',
                'options': {
                    'validate_data': True,
                    'create_missing_tags': True,
                    'overwrite_existing': False,
                    'backup_before_import': True,
                    'encoding': 'utf-8',
                    'auto_detect_questions': True
                },
                'validation': {
                    'required_fields': [],
                    'optional_fields': [],
                    'question_required': ['question_text'],
                    'tag_required': []
                }
            },
            'batch_import': {
                'name': 'Batch Import',
                'description': 'Import multiple files in batch',
                'format': 'mixed',
                'options': {
                    'validate_data': True,
                    'create_missing_tags': True,
                    'overwrite_existing': False,
                    'backup_before_import': True,
                    'progress_tracking': True,
                    'stop_on_error': False
                },
                'validation': {
                    'required_fields': [],
                    'optional_fields': [],
                    'question_required': ['question_text'],
                    'tag_required': ['name']
                }
            }
        }
    
    def get_export_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get export preset by name.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset dictionary or None if not found
        """
        return self._export_presets.get(preset_name)
    
    def get_import_preset(self, preset_name: str) -> Optional[Dict[str, Any]]:
        """
        Get import preset by name.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            Preset dictionary or None if not found
        """
        return self._import_presets.get(preset_name)
    
    def _initialize_export_presets(self):
        """Initialize export presets."""
        self._export_presets = {
            'quiz_export': {
                'name': 'Quiz Export',
                'description': 'Export quiz data for sharing',
                'template': 'basic_export',
                'options': {
                    'include_metadata': True,
                    'include_questions': True,
                    'include_tags': True,
                    'include_sessions': False,
                    'compress': False
                }
            },
            'backup_export': {
                'name': 'Backup Export',
                'description': 'Export for backup purposes',
                'template': 'compressed_export',
                'options': {
                    'include_metadata': True,
                    'include_questions': True,
                    'include_tags': True,
                    'include_sessions': True,
                    'compress': True
                }
            },
            'print_export': {
                'name': 'Print Export',
                'description': 'Export for printing',
                'template': 'pdf_export',
                'options': {
                    'include_answers': True,
                    'include_tags': True,
                    'include_metadata': True,
                    'page_size': 'A4'
                }
            },
            'spreadsheet_export': {
                'name': 'Spreadsheet Export',
                'description': 'Export for spreadsheet analysis',
                'template': 'csv_export',
                'options': {
                    'include_answers': True,
                    'include_tags': True,
                    'include_metadata': False,
                    'separator': ','
                }
            }
        }
    
    def _initialize_import_presets(self):
        """Initialize import presets."""
        self._import_presets = {
            'quiz_import': {
                'name': 'Quiz Import',
                'description': 'Import quiz data from another system',
                'template': 'basic_import',
                'options': {
                    'validate_data': True,
                    'create_missing_tags': True,
                    'overwrite_existing': False,
                    'backup_before_import': True
                }
            },
            'backup_import': {
                'name': 'Backup Import',
                'description': 'Import from backup file',
                'template': 'basic_import',
                'options': {
                    'validate_data': True,
                    'create_missing_tags': True,
                    'overwrite_existing': True,
                    'backup_before_import': False
                }
            },
            'bulk_import': {
                'name': 'Bulk Import',
                'description': 'Import multiple files at once',
                'template': 'batch_import',
                'options': {
                    'validate_data': True,
                    'create_missing_tags': True,
                    'overwrite_existing': False,
                    'backup_before_import': True,
                    'progress_tracking': True
                }
            }
        }
    
    def get_template_schema(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get template schema for validation.
        
        Args:
            template_name: Name of the template
            
        Returns:
            Schema dictionary or None if not found
        """
        template = self.get_export_template(template_name)
        if not template:
            template = self.get_import_template(template_name)
        
        if not template:
            return None
        
        return {
            'name': template['name'],
            'description': template['description'],
            'format': template['format'],
            'options': template['options'],
            'fields': template['fields'],
            'validation': template.get('validation', {}),
            'created_at': template.get('created_at', datetime.now().isoformat())
        }
    
    def validate_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate template data.
        
        Args:
            template_data: Template data to validate
            
        Returns:
            Validation result dictionary
        """
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['name', 'description', 'format', 'options']
        for field in required_fields:
            if field not in template_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate format
        if 'format' in template_data:
            valid_formats = ['json', 'csv', 'pdf', 'xml', 'html', 'text', 'mixed']
            if template_data['format'] not in valid_formats:
                errors.append(f"Invalid format: {template_data['format']}")
        
        # Validate options
        if 'options' in template_data:
            if not isinstance(template_data['options'], dict):
                errors.append("Options must be a dictionary")
        
        # Validate fields
        if 'fields' in template_data:
            if not isinstance(template_data['fields'], dict):
                errors.append("Fields must be a dictionary")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def export_templates(self, output_path: str = None) -> str:
        """
        Export all templates to a file.
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.templates_dir / f"templates_export_{timestamp}.json"
        
        export_data = {
            'export_templates': self._templates,
            'import_templates': self._import_templates,
            'export_presets': self._export_presets,
            'import_presets': self._import_presets,
            'export_timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Templates exported to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error exporting templates: {e}")
            return ""
    
    def import_templates(self, file_path: str) -> bool:
        """
        Import templates from a file.
        
        Args:
            file_path: Path to template file
            
        Returns:
            True if import successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Import templates
            if 'export_templates' in data:
                self._templates.update(data['export_templates'])
            
            if 'import_templates' in data:
                self._import_templates.update(data['import_templates'])
            
            if 'export_presets' in data:
                self._export_presets.update(data['export_presets'])
            
            if 'import_presets' in data:
                self._import_presets.update(data['import_presets'])
            
            logger.info(f"Templates imported from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing templates from {file_path}: {e}")
            return False
