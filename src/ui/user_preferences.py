"""
User Preferences and Configuration System

This module provides comprehensive user preference management with
validation, synchronization, and customization options.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import platform

logger = logging.getLogger(__name__)

class UserPreferences:
    """User preferences and configuration management system."""
    
    def __init__(self, config_dir: str = "data/config"):
        """
        Initialize user preferences system.
        
        Args:
            config_dir: Directory for storing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration files
        self.preferences_file = self.config_dir / "preferences.json"
        self.themes_file = self.config_dir / "themes.json"
        self.shortcuts_file = self.config_dir / "shortcuts.json"
        self.settings_file = self.config_dir / "settings.json"
        
        # Load preferences
        self.preferences = self._load_preferences()
        self.themes = self._load_themes()
        self.shortcuts = self._load_shortcuts()
        self.settings = self._load_settings()
        
        # Validation rules
        self.validation_rules = self._initialize_validation_rules()
        
        logger.info("User preferences system initialized")
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference value.
        
        Args:
            key: Preference key
            default: Default value if key not found
            
        Returns:
            Preference value
        """
        return self.preferences.get(key, default)
    
    def set_preference(self, key: str, value: Any) -> bool:
        """
        Set a user preference value.
        
        Args:
            key: Preference key
            value: Preference value
            
        Returns:
            True if set successfully
        """
        try:
            # Validate preference
            if not self._validate_preference(key, value):
                logger.error(f"Invalid preference value for {key}: {value}")
                return False
            
            # Set preference
            self.preferences[key] = value
            
            # Save preferences
            self._save_preferences()
            
            logger.debug(f"Preference set: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting preference {key}: {e}")
            return False
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences."""
        return self.preferences.copy()
    
    def reset_preferences(self) -> bool:
        """Reset all preferences to defaults."""
        try:
            self.preferences = self._get_default_preferences()
            self._save_preferences()
            logger.info("Preferences reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting preferences: {e}")
            return False
    
    def export_preferences(self, output_file: str = None) -> str:
        """
        Export preferences to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            Path to exported file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.config_dir / f"preferences_export_{timestamp}.json"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'preferences': self.preferences,
            'themes': self.themes,
            'shortcuts': self.shortcuts,
            'settings': self.settings
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Preferences exported to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Error exporting preferences: {e}")
            return ""
    
    def import_preferences(self, input_file: str) -> bool:
        """
        Import preferences from file.
        
        Args:
            input_file: Input file path
            
        Returns:
            True if import successful
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Import preferences
            if 'preferences' in data:
                self.preferences.update(data['preferences'])
                self._save_preferences()
            
            # Import themes
            if 'themes' in data:
                self.themes.update(data['themes'])
                self._save_themes()
            
            # Import shortcuts
            if 'shortcuts' in data:
                self.shortcuts.update(data['shortcuts'])
                self._save_shortcuts()
            
            # Import settings
            if 'settings' in data:
                self.settings.update(data['settings'])
                self._save_settings()
            
            logger.info(f"Preferences imported from {input_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing preferences: {e}")
            return False
    
    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """
        Get theme configuration.
        
        Args:
            theme_name: Theme name (uses current if None)
            
        Returns:
            Theme configuration
        """
        if not theme_name:
            theme_name = self.preferences.get('theme', 'default')
        
        return self.themes.get(theme_name, self.themes.get('default', {}))
    
    def set_theme(self, theme_name: str) -> bool:
        """
        Set current theme.
        
        Args:
            theme_name: Theme name
            
        Returns:
            True if theme set successfully
        """
        if theme_name not in self.themes:
            logger.error(f"Theme '{theme_name}' not found")
            return False
        
        return self.set_preference('theme', theme_name)
    
    def create_custom_theme(self, theme_name: str, theme_config: Dict[str, Any]) -> bool:
        """
        Create a custom theme.
        
        Args:
            theme_name: Theme name
            theme_config: Theme configuration
            
        Returns:
            True if theme created successfully
        """
        try:
            # Validate theme configuration
            if not self._validate_theme(theme_config):
                logger.error(f"Invalid theme configuration for {theme_name}")
                return False
            
            # Add theme
            self.themes[theme_name] = theme_config
            
            # Save themes
            self._save_themes()
            
            logger.info(f"Custom theme '{theme_name}' created")
            return True
            
        except Exception as e:
            logger.error(f"Error creating custom theme {theme_name}: {e}")
            return False
    
    def get_shortcut(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get keyboard shortcut configuration.
        
        Args:
            key: Shortcut key
            
        Returns:
            Shortcut configuration or None
        """
        return self.shortcuts.get(key)
    
    def set_shortcut(self, key: str, shortcut_config: Dict[str, Any]) -> bool:
        """
        Set keyboard shortcut configuration.
        
        Args:
            key: Shortcut key
            shortcut_config: Shortcut configuration
            
        Returns:
            True if shortcut set successfully
        """
        try:
            # Validate shortcut configuration
            if not self._validate_shortcut(shortcut_config):
                logger.error(f"Invalid shortcut configuration for {key}")
                return False
            
            # Set shortcut
            self.shortcuts[key] = shortcut_config
            
            # Save shortcuts
            self._save_shortcuts()
            
            logger.debug(f"Shortcut set: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting shortcut {key}: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get application setting.
        
        Args:
            key: Setting key
            default: Default value
            
        Returns:
            Setting value
        """
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set application setting.
        
        Args:
            key: Setting key
            value: Setting value
            
        Returns:
            True if setting set successfully
        """
        try:
            # Validate setting
            if not self._validate_setting(key, value):
                logger.error(f"Invalid setting value for {key}: {value}")
                return False
            
            # Set setting
            self.settings[key] = value
            
            # Save settings
            self._save_settings()
            
            logger.debug(f"Setting set: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting setting {key}: {e}")
            return False
    
    def validate_all_preferences(self) -> Dict[str, List[str]]:
        """
        Validate all preferences.
        
        Returns:
            Dictionary of validation errors
        """
        errors = {}
        
        # Validate preferences
        for key, value in self.preferences.items():
            if not self._validate_preference(key, value):
                errors.setdefault('preferences', []).append(f"Invalid value for {key}: {value}")
        
        # Validate themes
        for theme_name, theme_config in self.themes.items():
            if not self._validate_theme(theme_config):
                errors.setdefault('themes', []).append(f"Invalid theme configuration for {theme_name}")
        
        # Validate shortcuts
        for key, shortcut_config in self.shortcuts.items():
            if not self._validate_shortcut(shortcut_config):
                errors.setdefault('shortcuts', []).append(f"Invalid shortcut configuration for {key}")
        
        # Validate settings
        for key, value in self.settings.items():
            if not self._validate_setting(key, value):
                errors.setdefault('settings', []).append(f"Invalid setting value for {key}: {value}")
        
        return errors
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from file."""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_preferences()
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
            return self._get_default_preferences()
    
    def _save_preferences(self) -> None:
        """Save user preferences to file."""
        try:
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences."""
        return {
            'theme': 'default',
            'language': 'en',
            'accessibility': False,
            'auto_save': True,
            'confirm_actions': True,
            'show_breadcrumbs': True,
            'show_shortcuts': True,
            'history_size': 100,
            'onboarding_completed': False,
            'last_used': datetime.now().isoformat()
        }
    
    def _load_themes(self) -> Dict[str, Dict[str, Any]]:
        """Load themes from file."""
        try:
            if self.themes_file.exists():
                with open(self.themes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_themes()
        except Exception as e:
            logger.error(f"Error loading themes: {e}")
            return self._get_default_themes()
    
    def _save_themes(self) -> None:
        """Save themes to file."""
        try:
            with open(self.themes_file, 'w', encoding='utf-8') as f:
                json.dump(self.themes, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving themes: {e}")
    
    def _get_default_themes(self) -> Dict[str, Dict[str, Any]]:
        """Get default themes."""
        return {
            'default': {
                'name': 'Default Theme',
                'description': 'Default theme with standard colors',
                'colors': {
                    'primary': '#00BFFF',
                    'secondary': '#00FF00',
                    'warning': '#FFFF00',
                    'error': '#FF0000',
                    'info': '#0000FF',
                    'background': '#000000',
                    'foreground': '#FFFFFF'
                }
            },
            'dark': {
                'name': 'Dark Theme',
                'description': 'Dark theme for low-light environments',
                'colors': {
                    'primary': '#FFFFFF',
                    'secondary': '#00FF00',
                    'warning': '#FFFF00',
                    'error': '#FF0000',
                    'info': '#00BFFF',
                    'background': '#1A1A1A',
                    'foreground': '#FFFFFF'
                }
            },
            'high_contrast': {
                'name': 'High Contrast Theme',
                'description': 'High contrast theme for accessibility',
                'colors': {
                    'primary': '#FFFFFF',
                    'secondary': '#00FF00',
                    'warning': '#FFFF00',
                    'error': '#FF0000',
                    'info': '#00BFFF',
                    'background': '#000000',
                    'foreground': '#FFFFFF'
                }
            }
        }
    
    def _load_shortcuts(self) -> Dict[str, Dict[str, Any]]:
        """Load shortcuts from file."""
        try:
            if self.shortcuts_file.exists():
                with open(self.shortcuts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_shortcuts()
        except Exception as e:
            logger.error(f"Error loading shortcuts: {e}")
            return self._get_default_shortcuts()
    
    def _save_shortcuts(self) -> None:
        """Save shortcuts to file."""
        try:
            with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
                json.dump(self.shortcuts, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving shortcuts: {e}")
    
    def _get_default_shortcuts(self) -> Dict[str, Dict[str, Any]]:
        """Get default shortcuts."""
        return {
            'ctrl+h': {
                'description': 'Show help',
                'action': 'show_help',
                'enabled': True
            },
            'ctrl+q': {
                'description': 'Quit application',
                'action': 'quit',
                'enabled': True
            },
            'ctrl+n': {
                'description': 'Create new question',
                'action': 'create_question',
                'enabled': True
            },
            'ctrl+t': {
                'description': 'Take quiz',
                'action': 'take_quiz',
                'enabled': True
            },
            'f1': {
                'description': 'Context help',
                'action': 'context_help',
                'enabled': True
            }
        }
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load application settings from file."""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_settings()
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            return self._get_default_settings()
    
    def _save_settings(self) -> None:
        """Save application settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings."""
        return {
            'auto_save_interval': 300,  # seconds
            'max_history_size': 100,
            'log_level': 'INFO',
            'debug_mode': False,
            'performance_monitoring': False,
            'update_check': True,
            'backup_interval': 86400,  # seconds
            'compression_enabled': True
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize validation rules."""
        return {
            'preferences': {
                'theme': {'type': str, 'allowed_values': ['default', 'dark', 'high_contrast', 'monochrome']},
                'language': {'type': str, 'allowed_values': ['en', 'es', 'fr', 'de']},
                'accessibility': {'type': bool},
                'auto_save': {'type': bool},
                'confirm_actions': {'type': bool},
                'show_breadcrumbs': {'type': bool},
                'show_shortcuts': {'type': bool},
                'history_size': {'type': int, 'min': 10, 'max': 1000}
            },
            'themes': {
                'name': {'type': str, 'required': True},
                'description': {'type': str, 'required': True},
                'colors': {'type': dict, 'required': True}
            },
            'shortcuts': {
                'description': {'type': str, 'required': True},
                'action': {'type': str, 'required': True},
                'enabled': {'type': bool, 'default': True}
            },
            'settings': {
                'auto_save_interval': {'type': int, 'min': 60, 'max': 3600},
                'max_history_size': {'type': int, 'min': 10, 'max': 1000},
                'log_level': {'type': str, 'allowed_values': ['DEBUG', 'INFO', 'WARNING', 'ERROR']},
                'debug_mode': {'type': bool},
                'performance_monitoring': {'type': bool},
                'update_check': {'type': bool},
                'backup_interval': {'type': int, 'min': 3600, 'max': 604800},
                'compression_enabled': {'type': bool}
            }
        }
    
    def _validate_preference(self, key: str, value: Any) -> bool:
        """Validate a preference value."""
        if key not in self.validation_rules['preferences']:
            return True  # Unknown preference, allow it
        
        rule = self.validation_rules['preferences'][key]
        
        # Check type
        if 'type' in rule and not isinstance(value, rule['type']):
            return False
        
        # Check allowed values
        if 'allowed_values' in rule and value not in rule['allowed_values']:
            return False
        
        # Check range
        if 'min' in rule and value < rule['min']:
            return False
        if 'max' in rule and value > rule['max']:
            return False
        
        return True
    
    def _validate_theme(self, theme_config: Dict[str, Any]) -> bool:
        """Validate theme configuration."""
        if not isinstance(theme_config, dict):
            return False
        
        # Check required fields
        required_fields = ['name', 'description', 'colors']
        for field in required_fields:
            if field not in theme_config:
                return False
        
        # Check colors
        if not isinstance(theme_config['colors'], dict):
            return False
        
        return True
    
    def _validate_shortcut(self, shortcut_config: Dict[str, Any]) -> bool:
        """Validate shortcut configuration."""
        if not isinstance(shortcut_config, dict):
            return False
        
        # Check required fields
        required_fields = ['description', 'action']
        for field in required_fields:
            if field not in shortcut_config:
                return False
        
        return True
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """Validate a setting value."""
        if key not in self.validation_rules['settings']:
            return True  # Unknown setting, allow it
        
        rule = self.validation_rules['settings'][key]
        
        # Check type
        if 'type' in rule and not isinstance(value, rule['type']):
            return False
        
        # Check allowed values
        if 'allowed_values' in rule and value not in rule['allowed_values']:
            return False
        
        # Check range
        if 'min' in rule and value < rule['min']:
            return False
        if 'max' in rule and value > rule['max']:
            return False
        
        return True
