"""
Enhanced Console UI System

This module provides advanced console interface features including
breadcrumb navigation, keyboard shortcuts, command history, and accessibility.
"""

import os
import sys
import json
import logging
import shutil
from typing import Dict, Any, List, Optional, Tuple, Callable
from pathlib import Path
from datetime import datetime
import platform

# Terminal capabilities detection
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

try:
    import colorama
    from colorama import Fore, Back, Style, init
    COLORAMA_AVAILABLE = True
    init(autoreset=True)
except ImportError:
    COLORAMA_AVAILABLE = False
    # Fallback color constants
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Back:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ""
    class Style:
        DIM = NORMAL = BRIGHT = RESET_ALL = ""

logger = logging.getLogger(__name__)

class EnhancedConsole:
    """Enhanced console interface with advanced features."""
    
    def __init__(self, config_dir: str = "data/config"):
        """
        Initialize the enhanced console.
        
        Args:
            config_dir: Directory for storing configuration files
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Terminal capabilities
        self.terminal_info = self._detect_terminal_capabilities()
        
        # Navigation state
        self.breadcrumbs = []
        self.current_context = "main"
        self.navigation_history = []
        
        # User preferences
        self.preferences = self._load_preferences()
        
        # Command history
        self.command_history = []
        self.history_index = -1
        
        # Keyboard shortcuts
        self.shortcuts = self._initialize_shortcuts()
        
        # Help system
        self.help_database = self._initialize_help_database()
        
        # Themes
        self.themes = self._initialize_themes()
        self.current_theme = self.preferences.get('theme', 'default')
        
        # Accessibility features
        self.accessibility_enabled = self.preferences.get('accessibility', False)
        
        logger.info("Enhanced console initialized")
    
    def display_breadcrumb(self) -> None:
        """Display current navigation breadcrumb."""
        if not self.breadcrumbs:
            return
        
        breadcrumb_str = " > ".join(self.breadcrumbs)
        self._print_colored(f"📍 {breadcrumb_str}", Fore.CYAN)
    
    def navigate_to(self, location: str, context: str = None) -> None:
        """
        Navigate to a specific location with context.
        
        Args:
            location: Location name
            context: Optional context information
        """
        # Add to history
        self.navigation_history.append({
            'location': location,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update breadcrumbs
        if location not in self.breadcrumbs:
            self.breadcrumbs.append(location)
        
        # Update context
        if context:
            self.current_context = context
        
        logger.debug(f"Navigated to: {location} (context: {context})")
    
    def navigate_back(self) -> Optional[str]:
        """
        Navigate back to previous location.
        
        Returns:
            Previous location name or None if at root
        """
        if len(self.breadcrumbs) <= 1:
            return None
        
        # Remove current location
        current = self.breadcrumbs.pop()
        
        # Get previous location
        previous = self.breadcrumbs[-1] if self.breadcrumbs else None
        
        # Update history
        if self.navigation_history:
            self.navigation_history.pop()
        
        logger.debug(f"Navigated back from {current} to {previous}")
        return previous
    
    def handle_keyboard_shortcuts(self, key: str) -> bool:
        """
        Handle keyboard shortcuts.
        
        Args:
            key: Key pressed by user
            
        Returns:
            True if shortcut was handled, False otherwise
        """
        if key in self.shortcuts:
            shortcut = self.shortcuts[key]
            if callable(shortcut['action']):
                shortcut['action']()
            else:
                self._execute_shortcut_action(shortcut['action'])
            
            logger.debug(f"Executed shortcut: {key} -> {shortcut['description']}")
            return True
        
        return False
    
    def get_context_help(self, context: str = None) -> Dict[str, Any]:
        """
        Get context-sensitive help.
        
        Args:
            context: Specific context for help
            
        Returns:
            Help information dictionary
        """
        context = context or self.current_context
        
        if context in self.help_database:
            return self.help_database[context]
        
        # Return general help if context not found
        return self.help_database.get('general', {})
    
    def show_help(self, topic: str = None) -> None:
        """
        Display help information.
        
        Args:
            topic: Specific help topic
        """
        if topic:
            help_info = self.help_database.get(topic, {})
        else:
            help_info = self.get_context_help()
        
        if not help_info:
            self._print_colored("❌ No help available for this topic", Fore.RED)
            return
        
        # Display help
        self._print_colored(f"\n📚 Help: {help_info.get('title', 'General Help')}", Fore.YELLOW)
        self._print_colored("=" * 50, Fore.YELLOW)
        
        if 'description' in help_info:
            self._print_colored(f"\n{help_info['description']}", Fore.WHITE)
        
        if 'shortcuts' in help_info:
            self._print_colored("\n⌨️  Keyboard Shortcuts:", Fore.CYAN)
            for shortcut, info in help_info['shortcuts'].items():
                self._print_colored(f"  {shortcut}: {info['description']}", Fore.GREEN)
        
        if 'commands' in help_info:
            self._print_colored("\n💻 Commands:", Fore.CYAN)
            for command, info in help_info['commands'].items():
                self._print_colored(f"  {command}: {info['description']}", Fore.GREEN)
        
        if 'examples' in help_info:
            self._print_colored("\n📝 Examples:", Fore.CYAN)
            for example in help_info['examples']:
                self._print_colored(f"  {example}", Fore.WHITE)
    
    def save_user_preferences(self, preferences: Dict[str, Any] = None) -> bool:
        """
        Save user preferences.
        
        Args:
            preferences: Preferences to save (optional)
            
        Returns:
            True if saved successfully
        """
        try:
            if preferences:
                self.preferences.update(preferences)
            
            preferences_file = self.config_dir / "preferences.json"
            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=2, default=str)
            
            logger.info("User preferences saved")
            return True
            
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
            return False
    
    def load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences."""
        return self._load_preferences()
    
    def reset_preferences(self) -> bool:
        """Reset preferences to defaults."""
        try:
            self.preferences = self._get_default_preferences()
            return self.save_user_preferences()
        except Exception as e:
            logger.error(f"Error resetting preferences: {e}")
            return False
    
    def setup_user_onboarding(self) -> None:
        """Setup user onboarding process."""
        self._print_colored("\n🎉 Welcome to the Quiz Application!", Fore.GREEN)
        self._print_colored("=" * 50, Fore.GREEN)
        
        # Check if first time user
        if not self.preferences.get('onboarding_completed', False):
            self._run_onboarding_tutorial()
        else:
            self._print_colored("Welcome back! Use 'help' for assistance.", Fore.CYAN)
    
    def run_tutorial(self, tutorial_name: str = "basic") -> None:
        """
        Run a specific tutorial.
        
        Args:
            tutorial_name: Name of tutorial to run
        """
        tutorials = {
            'basic': self._run_basic_tutorial,
            'navigation': self._run_navigation_tutorial,
            'shortcuts': self._run_shortcuts_tutorial,
            'themes': self._run_themes_tutorial
        }
        
        if tutorial_name in tutorials:
            tutorials[tutorial_name]()
        else:
            self._print_colored(f"❌ Tutorial '{tutorial_name}' not found", Fore.RED)
    
    def customize_theme(self, theme_name: str = None) -> bool:
        """
        Customize console theme.
        
        Args:
            theme_name: Name of theme to apply
            
        Returns:
            True if theme applied successfully
        """
        if theme_name:
            if theme_name in self.themes:
                self.current_theme = theme_name
                self.preferences['theme'] = theme_name
                self.save_user_preferences()
                self._print_colored(f"🎨 Theme changed to: {theme_name}", Fore.GREEN)
                return True
            else:
                self._print_colored(f"❌ Theme '{theme_name}' not found", Fore.RED)
                return False
        else:
            # Show available themes
            self._print_colored("\n🎨 Available Themes:", Fore.CYAN)
            for theme_name, theme_info in self.themes.items():
                status = " (current)" if theme_name == self.current_theme else ""
                self._print_colored(f"  {theme_name}: {theme_info['description']}{status}", Fore.WHITE)
            return True
    
    def validate_terminal_capabilities(self) -> Dict[str, Any]:
        """Validate terminal capabilities."""
        return self.terminal_info
    
    def adapt_ui_to_terminal(self) -> None:
        """Adapt UI to terminal capabilities."""
        if not self.terminal_info['colors']:
            self._print_colored("⚠️  Color support not available, using monochrome mode", Fore.YELLOW)
        
        if not self.terminal_info['unicode']:
            self._print_colored("⚠️  Unicode support limited, using ASCII characters", Fore.YELLOW)
        
        if self.terminal_info['width'] < 80:
            self._print_colored("⚠️  Terminal width is narrow, some features may be limited", Fore.YELLOW)
    
    def enable_accessibility_features(self, enable: bool = True) -> None:
        """
        Enable or disable accessibility features.
        
        Args:
            enable: Whether to enable accessibility features
        """
        self.accessibility_enabled = enable
        self.preferences['accessibility'] = enable
        self.save_user_preferences()
        
        if enable:
            self._print_colored("♿ Accessibility features enabled", Fore.GREEN)
        else:
            self._print_colored("♿ Accessibility features disabled", Fore.YELLOW)
    
    def _detect_terminal_capabilities(self) -> Dict[str, Any]:
        """Detect terminal capabilities."""
        terminal_info = {
            'platform': platform.system(),
            'width': shutil.get_terminal_size().columns,
            'height': shutil.get_terminal_size().lines,
            'colors': COLORAMA_AVAILABLE,
            'unicode': True,  # Assume Unicode support
            'readline': READLINE_AVAILABLE,
            'terminal': os.environ.get('TERM', 'unknown')
        }
        
        # Detect specific terminal types
        if terminal_info['platform'] == 'Windows':
            terminal_info['type'] = 'windows'
        elif terminal_info['platform'] == 'Darwin':
            terminal_info['type'] = 'macos'
        else:
            terminal_info['type'] = 'linux'
        
        return terminal_info
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load user preferences from file."""
        try:
            preferences_file = self.config_dir / "preferences.json"
            if preferences_file.exists():
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_preferences()
        except Exception as e:
            logger.error(f"Error loading preferences: {e}")
            return self._get_default_preferences()
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences."""
        return {
            'theme': 'default',
            'accessibility': False,
            'onboarding_completed': False,
            'auto_save': True,
            'confirm_actions': True,
            'show_breadcrumbs': True,
            'show_shortcuts': True,
            'history_size': 100,
            'language': 'en'
        }
    
    def _initialize_shortcuts(self) -> Dict[str, Dict[str, Any]]:
        """Initialize keyboard shortcuts."""
        return {
            'ctrl+h': {
                'description': 'Show help',
                'action': lambda: self.show_help()
            },
            'ctrl+q': {
                'description': 'Quit application',
                'action': 'quit'
            },
            'ctrl+n': {
                'description': 'Create new question',
                'action': 'create_question'
            },
            'ctrl+t': {
                'description': 'Take quiz',
                'action': 'take_quiz'
            },
            'ctrl+b': {
                'description': 'Go back',
                'action': lambda: self.navigate_back()
            },
            'ctrl+s': {
                'description': 'Save data',
                'action': 'save_data'
            },
            'ctrl+r': {
                'description': 'Refresh display',
                'action': 'refresh'
            },
            'f1': {
                'description': 'Context help',
                'action': lambda: self.show_help(self.current_context)
            },
            'f2': {
                'description': 'Toggle theme',
                'action': 'toggle_theme'
            },
            'f3': {
                'description': 'Toggle accessibility',
                'action': 'toggle_accessibility'
            }
        }
    
    def _initialize_help_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize help database."""
        return {
            'general': {
                'title': 'General Help',
                'description': 'Welcome to the Quiz Application! This is a comprehensive quiz management system.',
                'shortcuts': {
                    'Ctrl+H': {'description': 'Show this help'},
                    'Ctrl+Q': {'description': 'Quit application'},
                    'Ctrl+N': {'description': 'Create new question'},
                    'Ctrl+T': {'description': 'Take quiz'},
                    'F1': {'description': 'Context-sensitive help'}
                },
                'commands': {
                    'help': {'description': 'Show help information'},
                    'quit': {'description': 'Exit application'},
                    'tutorial': {'description': 'Run tutorials'}
                }
            },
            'main': {
                'title': 'Main Menu Help',
                'description': 'You are in the main menu. Choose an option to continue.',
                'shortcuts': {
                    '1': {'description': 'Create Question'},
                    '2': {'description': 'Take Quiz'},
                    '3': {'description': 'Manage Tags'},
                    '0': {'description': 'Exit'}
                }
            },
            'question_creation': {
                'title': 'Question Creation Help',
                'description': 'Create new quiz questions with multiple types and options.',
                'examples': [
                    'Enter question text',
                    'Add multiple answer options',
                    'Mark correct answers',
                    'Add tags for organization'
                ]
            }
        }
    
    def _initialize_themes(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available themes."""
        return {
            'default': {
                'description': 'Default theme with standard colors',
                'colors': {
                    'primary': Fore.CYAN,
                    'secondary': Fore.GREEN,
                    'warning': Fore.YELLOW,
                    'error': Fore.RED,
                    'info': Fore.BLUE
                }
            },
            'dark': {
                'description': 'Dark theme for low-light environments',
                'colors': {
                    'primary': Fore.WHITE,
                    'secondary': Fore.GREEN,
                    'warning': Fore.YELLOW,
                    'error': Fore.RED,
                    'info': Fore.CYAN
                }
            },
            'high_contrast': {
                'description': 'High contrast theme for accessibility',
                'colors': {
                    'primary': Fore.WHITE,
                    'secondary': Fore.GREEN,
                    'warning': Fore.YELLOW,
                    'error': Fore.RED,
                    'info': Fore.CYAN
                }
            },
            'monochrome': {
                'description': 'Monochrome theme for basic terminals',
                'colors': {
                    'primary': '',
                    'secondary': '',
                    'warning': '',
                    'error': '',
                    'info': ''
                }
            }
        }
    
    def _print_colored(self, text: str, color: str = '') -> None:
        """Print colored text if color support is available."""
        try:
            if self.terminal_info['colors'] and color:
                print(f"{color}{text}{Style.RESET_ALL}")
            else:
                print(text)
        except UnicodeEncodeError:
            # Fallback for terminals that don't support Unicode
            safe_text = text.encode('ascii', 'replace').decode('ascii')
            if self.terminal_info['colors'] and color:
                print(f"{color}{safe_text}{Style.RESET_ALL}")
            else:
                print(safe_text)
    
    def _execute_shortcut_action(self, action: str) -> None:
        """Execute shortcut action by name."""
        actions = {
            'quit': lambda: sys.exit(0),
            'create_question': lambda: self._print_colored("📝 Create Question", Fore.GREEN),
            'take_quiz': lambda: self._print_colored("📚 Take Quiz", Fore.GREEN),
            'save_data': lambda: self._print_colored("💾 Save Data", Fore.GREEN),
            'refresh': lambda: self._print_colored("🔄 Refresh", Fore.GREEN),
            'toggle_theme': lambda: self.customize_theme(),
            'toggle_accessibility': lambda: self.enable_accessibility_features(not self.accessibility_enabled)
        }
        
        if action in actions:
            actions[action]()
    
    def _run_onboarding_tutorial(self) -> None:
        """Run onboarding tutorial for new users."""
        self._print_colored("\n🎓 Welcome! Let's take a quick tour:", Fore.GREEN)
        
        # Basic tutorial
        self._run_basic_tutorial()
        
        # Mark onboarding as completed
        self.preferences['onboarding_completed'] = True
        self.save_user_preferences()
    
    def _run_basic_tutorial(self) -> None:
        """Run basic tutorial."""
        self._print_colored("\n📚 Basic Tutorial:", Fore.CYAN)
        self._print_colored("1. Use number keys to navigate menus", Fore.WHITE)
        self._print_colored("2. Press Ctrl+H for help anytime", Fore.WHITE)
        self._print_colored("3. Use Ctrl+Q to quit", Fore.WHITE)
        self._print_colored("4. Try the keyboard shortcuts!", Fore.WHITE)
    
    def _run_navigation_tutorial(self) -> None:
        """Run navigation tutorial."""
        self._print_colored("\n🧭 Navigation Tutorial:", Fore.CYAN)
        self._print_colored("1. Use breadcrumbs to see where you are", Fore.WHITE)
        self._print_colored("2. Press Ctrl+B to go back", Fore.WHITE)
        self._print_colored("3. Use F1 for context help", Fore.WHITE)
    
    def _run_shortcuts_tutorial(self) -> None:
        """Run shortcuts tutorial."""
        self._print_colored("\n⌨️  Shortcuts Tutorial:", Fore.CYAN)
        for key, shortcut in self.shortcuts.items():
            self._print_colored(f"{key}: {shortcut['description']}", Fore.WHITE)
    
    def _run_themes_tutorial(self) -> None:
        """Run themes tutorial."""
        self._print_colored("\n🎨 Themes Tutorial:", Fore.CYAN)
        self._print_colored("1. Use 'customize_theme()' to change themes", Fore.WHITE)
        self._print_colored("2. Available themes:", Fore.WHITE)
        for theme_name, theme_info in self.themes.items():
            self._print_colored(f"   - {theme_name}: {theme_info['description']}", Fore.WHITE)
