"""
Command History and Auto-completion System

This module provides command history, auto-completion, and fuzzy matching
for enhanced user experience in the console interface.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import difflib

# Readline support
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

logger = logging.getLogger(__name__)

class CommandHistory:
    """Command history and auto-completion system."""
    
    def __init__(self, history_file: str = "data/config/command_history.json"):
        """
        Initialize command history system.
        
        Args:
            history_file: Path to history file
        """
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Command history
        self.history = self._load_history()
        self.current_index = -1
        self.max_history_size = 100
        
        # Auto-completion
        self.completions = self._initialize_completions()
        self.fuzzy_threshold = 0.6
        
        # Setup readline if available
        if READLINE_AVAILABLE:
            self._setup_readline()
        
        logger.info("Command history system initialized")
    
    def add_command(self, command: str, context: str = None) -> None:
        """
        Add command to history.
        
        Args:
            command: Command string
            context: Optional context information
        """
        if not command.strip():
            return
        
        # Create history entry
        entry = {
            'command': command.strip(),
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'success': True  # Will be updated later
        }
        
        # Add to history
        self.history.append(entry)
        
        # Limit history size
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
        
        # Reset index
        self.current_index = -1
        
        # Save history
        self._save_history()
        
        logger.debug(f"Added command to history: {command}")
    
    def get_previous_command(self) -> Optional[str]:
        """
        Get previous command from history.
        
        Returns:
            Previous command or None if at beginning
        """
        if not self.history or self.current_index >= len(self.history) - 1:
            return None
        
        self.current_index += 1
        return self.history[-(self.current_index + 1)]['command']
    
    def get_next_command(self) -> Optional[str]:
        """
        Get next command from history.
        
        Returns:
            Next command or None if at end
        """
        if self.current_index <= 0:
            self.current_index = -1
            return None
        
        self.current_index -= 1
        return self.history[-(self.current_index + 1)]['command']
    
    def search_history(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search command history.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching history entries
        """
        if not query.strip():
            return self.history[-limit:]
        
        query_lower = query.lower()
        matches = []
        
        for entry in reversed(self.history):
            if query_lower in entry['command'].lower():
                matches.append(entry)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_auto_completions(self, partial_command: str, context: str = None) -> List[str]:
        """
        Get auto-completion suggestions.
        
        Args:
            partial_command: Partial command string
            context: Optional context for filtering
            
        Returns:
            List of completion suggestions
        """
        if not partial_command.strip():
            return []
        
        partial_lower = partial_command.lower()
        suggestions = []
        
        # Get context-specific completions
        context_completions = self.completions.get(context, {})
        all_completions = {**self.completions.get('general', {}), **context_completions}
        
        # Find matching completions
        for command, info in all_completions.items():
            if partial_lower in command.lower():
                suggestions.append(command)
            elif info.get('aliases'):
                for alias in info['aliases']:
                    if partial_lower in alias.lower():
                        suggestions.append(command)
        
        # Add fuzzy matches from history
        history_matches = self._fuzzy_search_history(partial_command)
        suggestions.extend(history_matches)
        
        # Remove duplicates and sort
        suggestions = sorted(list(set(suggestions)))
        
        return suggestions[:10]  # Limit to 10 suggestions
    
    def get_command_suggestions(self, partial_command: str, context: str = None) -> List[Dict[str, Any]]:
        """
        Get detailed command suggestions with descriptions.
        
        Args:
            partial_command: Partial command string
            context: Optional context for filtering
            
        Returns:
            List of command suggestions with descriptions
        """
        if not partial_command.strip():
            return []
        
        partial_lower = partial_command.lower()
        suggestions = []
        
        # Get context-specific completions
        context_completions = self.completions.get(context, {})
        all_completions = {**self.completions.get('general', {}), **context_completions}
        
        # Find matching completions
        for command, info in all_completions.items():
            if partial_lower in command.lower():
                suggestions.append({
                    'command': command,
                    'description': info.get('description', ''),
                    'usage': info.get('usage', ''),
                    'aliases': info.get('aliases', [])
                })
            elif info.get('aliases'):
                for alias in info['aliases']:
                    if partial_lower in alias.lower():
                        suggestions.append({
                            'command': command,
                            'description': info.get('description', ''),
                            'usage': info.get('usage', ''),
                            'aliases': info.get('aliases', [])
                        })
                        break
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def get_command_help(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Get help information for a specific command.
        
        Args:
            command: Command name
            
        Returns:
            Help information or None if not found
        """
        # Search in all contexts
        for context, completions in self.completions.items():
            if command in completions:
                info = completions[command]
                return {
                    'command': command,
                    'description': info.get('description', ''),
                    'usage': info.get('usage', ''),
                    'examples': info.get('examples', []),
                    'aliases': info.get('aliases', []),
                    'context': context
                }
        
        return None
    
    def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent commands from history.
        
        Args:
            limit: Maximum number of commands
            
        Returns:
            List of recent commands
        """
        return self.history[-limit:] if self.history else []
    
    def clear_history(self) -> None:
        """Clear command history."""
        self.history = []
        self.current_index = -1
        self._save_history()
        logger.info("Command history cleared")
    
    def export_history(self, output_file: str = None) -> str:
        """
        Export command history to file.
        
        Args:
            output_file: Output file path
            
        Returns:
            Path to exported file
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"command_history_{timestamp}.json"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_commands': len(self.history),
            'history': self.history
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Command history exported to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error exporting command history: {e}")
            return ""
    
    def import_history(self, input_file: str) -> bool:
        """
        Import command history from file.
        
        Args:
            input_file: Input file path
            
        Returns:
            True if import successful
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'history' in data:
                self.history = data['history']
                self.current_index = -1
                self._save_history()
                logger.info(f"Command history imported from {input_file}")
                return True
            else:
                logger.error("Invalid history file format")
                return False
                
        except Exception as e:
            logger.error(f"Error importing command history: {e}")
            return False
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load command history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('history', [])
            else:
                return []
        except Exception as e:
            logger.error(f"Error loading command history: {e}")
            return []
    
    def _save_history(self) -> None:
        """Save command history to file."""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_commands': len(self.history),
                'history': self.history
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error saving command history: {e}")
    
    def _initialize_completions(self) -> Dict[str, Dict[str, Any]]:
        """Initialize command completions database."""
        return {
            'general': {
                'help': {
                    'description': 'Show help information',
                    'usage': 'help [topic]',
                    'examples': ['help', 'help navigation', 'help shortcuts'],
                    'aliases': ['h', '?']
                },
                'quit': {
                    'description': 'Exit the application',
                    'usage': 'quit',
                    'examples': ['quit', 'exit'],
                    'aliases': ['exit', 'q']
                },
                'clear': {
                    'description': 'Clear the screen',
                    'usage': 'clear',
                    'examples': ['clear', 'cls'],
                    'aliases': ['cls', 'c']
                },
                'history': {
                    'description': 'Show command history',
                    'usage': 'history [limit]',
                    'examples': ['history', 'history 20'],
                    'aliases': ['hist']
                }
            },
            'main': {
                'create': {
                    'description': 'Create a new question',
                    'usage': 'create',
                    'examples': ['create', 'new question'],
                    'aliases': ['new', 'add']
                },
                'quiz': {
                    'description': 'Take a quiz',
                    'usage': 'quiz [options]',
                    'examples': ['quiz', 'quiz --tags math'],
                    'aliases': ['take', 'start']
                },
                'tags': {
                    'description': 'Manage tags',
                    'usage': 'tags [action]',
                    'examples': ['tags', 'tags list', 'tags create'],
                    'aliases': ['tag']
                }
            },
            'question_creation': {
                'save': {
                    'description': 'Save current question',
                    'usage': 'save',
                    'examples': ['save'],
                    'aliases': ['store']
                },
                'cancel': {
                    'description': 'Cancel question creation',
                    'usage': 'cancel',
                    'examples': ['cancel', 'abort'],
                    'aliases': ['abort', 'quit']
                },
                'preview': {
                    'description': 'Preview question',
                    'usage': 'preview',
                    'examples': ['preview', 'show'],
                    'aliases': ['show', 'view']
                }
            }
        }
    
    def _setup_readline(self) -> None:
        """Setup readline for enhanced input."""
        try:
            # Set up tab completion
            readline.set_completer(self._readline_completer)
            readline.parse_and_bind("tab: complete")
            
            # Set up history navigation
            readline.parse_and_bind("\\C-p: history-search-backward")
            readline.parse_and_bind("\\C-n: history-search-forward")
            
            # Set up history file
            readline.set_history_length(self.max_history_size)
            
            logger.debug("Readline setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up readline: {e}")
    
    def _readline_completer(self, text: str, state: int) -> Optional[str]:
        """Readline completer function."""
        if state == 0:
            self._completion_matches = self.get_auto_completions(text)
        
        if state < len(self._completion_matches):
            return self._completion_matches[state]
        
        return None
    
    def _fuzzy_search_history(self, query: str) -> List[str]:
        """Perform fuzzy search on command history."""
        if not query.strip():
            return []
        
        matches = []
        query_lower = query.lower()
        
        for entry in self.history:
            command = entry['command']
            # Calculate similarity
            similarity = difflib.SequenceMatcher(None, query_lower, command.lower()).ratio()
            
            if similarity >= self.fuzzy_threshold:
                matches.append(command)
        
        # Sort by similarity (most similar first)
        matches.sort(key=lambda x: difflib.SequenceMatcher(None, query_lower, x.lower()).ratio(), reverse=True)
        
        return matches[:5]  # Return top 5 matches
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get command history statistics."""
        if not self.history:
            return {
                'total_commands': 0,
                'unique_commands': 0,
                'most_used_command': None,
                'average_commands_per_day': 0
            }
        
        # Calculate statistics
        total_commands = len(self.history)
        unique_commands = len(set(entry['command'] for entry in self.history))
        
        # Find most used command
        command_counts = {}
        for entry in self.history:
            command = entry['command']
            command_counts[command] = command_counts.get(command, 0) + 1
        
        most_used_command = max(command_counts.items(), key=lambda x: x[1]) if command_counts else None
        
        # Calculate average commands per day
        if self.history:
            first_date = datetime.fromisoformat(self.history[0]['timestamp'])
            last_date = datetime.fromisoformat(self.history[-1]['timestamp'])
            days = (last_date - first_date).days + 1
            average_commands_per_day = total_commands / days if days > 0 else 0
        else:
            average_commands_per_day = 0
        
        return {
            'total_commands': total_commands,
            'unique_commands': unique_commands,
            'most_used_command': most_used_command[0] if most_used_command else None,
            'most_used_count': most_used_command[1] if most_used_command else 0,
            'average_commands_per_day': average_commands_per_day
        }
