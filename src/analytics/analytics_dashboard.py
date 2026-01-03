"""
Analytics Dashboard

This module provides an interactive console-based analytics dashboard
for viewing and analyzing quiz application data.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .analytics_engine import AnalyticsEngine
from ui.display import DisplayManager
from ui.prompts import InputPrompts

logger = logging.getLogger(__name__)

class AnalyticsDashboard:
    """Interactive analytics dashboard for the quiz application."""
    
    def __init__(self, analytics_engine: AnalyticsEngine, 
                 display_manager: DisplayManager, 
                 prompts: InputPrompts):
        """
        Initialize the analytics dashboard.
        
        Args:
            analytics_engine: Analytics engine instance
            display_manager: Display manager for output
            prompts: Input prompts for user interaction
        """
        self.analytics_engine = analytics_engine
        self.display = display_manager
        self.prompts = prompts
        
        logger.info("Analytics dashboard initialized")
    
    def show_main_dashboard(self) -> None:
        """Display the main analytics dashboard menu."""
        while True:
            try:
                self.display.show_section_header("Analytics Dashboard")
                self.display.show_message("1. Performance Analytics")
                self.display.show_message("2. Export Analytics")
                self.display.show_message("0. Back to Main Menu")
                
                choice = self.prompts.get_menu_choice(2)
                
                if choice == 1:
                    self.show_performance_analytics()
                elif choice == 2:
                    self.show_export_analytics()
                elif choice == 0:
                    break
                else:
                    self.display.show_error("Invalid choice. Please try again.")
                    
            except Exception as e:
                logger.error(f"Error in analytics dashboard: {e}")
                self.display.show_error(f"An error occurred: {e}")
    
    def show_performance_analytics(self) -> None:
        """Display performance analytics."""
        try:
            self.display.show_section_header("Performance Analytics")
            
            # Get time period
            days = self.prompts.get_number_input("Enter number of days to analyze (default: 30)", 
                                               min_val=1, max_val=365, default=30)
            if days is None:
                return
            
            # Get user filter
            user_id = self.prompts.get_text_input("Enter user ID (optional, press Enter to skip):")
            if not user_id:
                user_id = None
            
            # Get analytics data
            self.display.show_message("Generating performance analytics...")
            analytics = self.analytics_engine.get_performance_analytics(user_id, days)
            
            # Display results
            self.display.show_performance_analytics(analytics)
            
            # Ask if user wants to export
            if self.prompts.get_yes_no_input("Export these analytics?"):
                self.export_analytics('performance', analytics)
                
        except Exception as e:
            logger.error(f"Error showing performance analytics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def show_learning_analytics(self) -> None:
        """Display learning analytics."""
        try:
            self.display.show_section_header("Learning Analytics")
            
            # Get time period
            days = self.prompts.get_number_input("Enter number of days to analyze (default: 30)", 
                                               min_val=1, max_val=365, default=30)
            if days is None:
                return
            
            # Get user filter
            user_id = self.prompts.get_text_input("Enter user ID (optional, press Enter to skip):")
            if not user_id:
                user_id = None
            
            # Get analytics data
            self.display.show_message("Generating learning analytics...")
            analytics = self.analytics_engine.get_learning_analytics(user_id, days)
            
            # Display results
            self.display.show_learning_analytics(analytics)
            
            # Ask if user wants to export
            if self.prompts.get_yes_no_input("Export these analytics?"):
                self.export_analytics('learning', analytics)
                
        except Exception as e:
            logger.error(f"Error showing learning analytics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def show_question_analytics(self) -> None:
        """Display question analytics."""
        try:
            self.display.show_section_header("Question Analytics")
            
            # Get question filter
            question_id = self.prompts.get_text_input("Enter question ID (optional, press Enter for all questions):")
            if not question_id:
                question_id = None
            
            # Get analytics data
            self.display.show_message("Generating question analytics...")
            analytics = self.analytics_engine.get_question_analytics(question_id)
            
            # Display results
            self.display.show_question_analytics(analytics)
            
            # Ask if user wants to export
            if self.prompts.get_yes_no_input("Export these analytics?"):
                self.export_analytics('questions', analytics)
                
        except Exception as e:
            logger.error(f"Error showing question analytics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def show_tag_analytics(self) -> None:
        """Display tag analytics."""
        try:
            self.display.show_section_header("Tag Analytics")
            
            # Get tag filter
            tag_id = self.prompts.get_text_input("Enter tag ID (optional, press Enter for all tags):")
            if not tag_id:
                tag_id = None
            
            # Get analytics data
            self.display.show_message("Generating tag analytics...")
            analytics = self.analytics_engine.get_tag_analytics(tag_id)
            
            # Display results
            self.display.show_tag_analytics(analytics)
            
            # Ask if user wants to export
            if self.prompts.get_yes_no_input("Export these analytics?"):
                self.export_analytics('tags', analytics)
                
        except Exception as e:
            logger.error(f"Error showing tag analytics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def show_system_analytics(self) -> None:
        """Display system analytics."""
        try:
            self.display.show_section_header("System Analytics")
            
            # Get analytics data
            self.display.show_message("Generating system analytics...")
            analytics = self.analytics_engine.get_system_analytics()
            
            # Display results
            self.display.show_system_analytics(analytics)
            
            # Ask if user wants to export
            if self.prompts.get_yes_no_input("Export these analytics?"):
                self.export_analytics('system', analytics)
                
        except Exception as e:
            logger.error(f"Error showing system analytics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def show_export_analytics(self) -> None:
        """Display analytics export options."""
        try:
            self.display.show_section_header("Export Analytics")
            
            # Get time period for performance analytics
            days = self.prompts.get_number_input("Enter number of days to analyze (default: 30)", 
                                               min_val=1, max_val=365, default=30)
            if days is None:
                self.display.show_message("Export cancelled.")
                return
            
            # Get user filter
            user_id = self.prompts.get_text_input("Enter user ID (optional, press Enter to skip, or 'cancel' to cancel):")
            if user_id is None:
                self.display.show_message("Export cancelled.")
                return
            if not user_id:
                user_id = None
            
            # Generate performance analytics with specified parameters
            self.display.show_message("Generating performance analytics...")
            analytics = self.analytics_engine.get_performance_analytics(user_id, days)
            
            # Use the helper method to export
            self.export_analytics('performance', analytics)
                
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def show_custom_analytics(self) -> None:
        """Display custom analytics options."""
        try:
            self.display.show_section_header("Custom Analytics")
            self.display.show_message("Custom analytics features coming soon!")
            self.display.show_message("This will include:")
            self.display.show_message("- Custom date ranges")
            self.display.show_message("- Advanced filtering")
            self.display.show_message("- Comparative analysis")
            self.display.show_message("- Trend analysis")
            self.display.show_message("- Predictive analytics")
            
            self.prompts.get_text_input("Press Enter to continue...")
            
        except Exception as e:
            logger.error(f"Error showing custom analytics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def export_analytics(self, analytics_type: str, data: Dict[str, Any]) -> None:
        """Export analytics data."""
        try:
            # Get export format
            self.display.show_message("Select export format:")
            self.display.show_message("1. JSON")
            self.display.show_message("2. CSV")
            self.display.show_message("3. HTML")
            self.display.show_message("0. Cancel")
            
            format_choice = self.prompts.get_menu_choice(3)
            if format_choice == 0:
                self.display.show_message("Export cancelled.")
                return
            
            formats = ['json', 'csv', 'html']
            export_format = formats[format_choice - 1]
            
            # Get file path
            file_path = self.prompts.get_text_input("Enter file path (optional, press Enter for auto-generated, or 'cancel' to cancel):")
            if file_path is None:
                self.display.show_message("Export cancelled.")
                return
            if not file_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"analytics_{analytics_type}_{timestamp}.{export_format}"
            
            # Export analytics directly using provided data
            self.display.show_message(f"Exporting {analytics_type} analytics as {export_format}...")
            
            import json
            
            if export_format == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=str)
                success = True
            elif export_format == 'csv':
                import csv
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for key, value in data.items():
                        if isinstance(value, (dict, list)):
                            writer.writerow([key, json.dumps(value)])
                        else:
                            writer.writerow([key, value])
                success = True
            elif export_format == 'html':
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{analytics_type.title()} Analytics</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
        .metric h3 {{ margin: 0 0 10px 0; color: #333; }}
        .metric-value {{ font-size: 18px; font-weight: bold; color: #007bff; }}
    </style>
</head>
<body>
    <h1>{analytics_type.title()} Analytics Report</h1>
    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
                for key, value in data.items():
                    html_content += f"    <div class='metric'>\n"
                    html_content += f"        <h3>{key.replace('_', ' ').title()}</h3>\n"
                    if isinstance(value, (dict, list)):
                        html_content += f"        <pre>{json.dumps(value, indent=2, default=str)}</pre>\n"
                    else:
                        html_content += f"        <div class='metric-value'>{value}</div>\n"
                    html_content += f"    </div>\n"
                html_content += """
</body>
</html>
"""
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                success = True
            else:
                success = False
            
            if success:
                self.display.show_success(f"Analytics exported successfully to: {file_path}")
            else:
                self.display.show_error(f"Export failed: Unsupported format")
                
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def show_quick_stats(self) -> None:
        """Display quick statistics overview."""
        try:
            self.display.show_section_header("Quick Statistics")
            
            # Get system analytics for quick overview
            analytics = self.analytics_engine.get_system_analytics()
            
            # Display key metrics
            self.display.show_message(f"Total Questions: {analytics.get('total_questions', 0)}")
            self.display.show_message(f"Total Tags: {analytics.get('total_tags', 0)}")
            self.display.show_message(f"Total Sessions: {analytics.get('total_sessions', 0)}")
            self.display.show_message(f"Total Users: {analytics.get('total_users', 0)}")
            self.display.show_message(f"Database Size: {analytics.get('database_size', 0)} MB")
            self.display.show_message(f"System Health: {analytics.get('system_health', 0):.1f}%")
            
            # Show recent performance if available
            performance = self.analytics_engine.get_performance_analytics(days=7)
            if performance.get('total_sessions', 0) > 0:
                self.display.show_message(f"Recent Sessions (7 days): {performance.get('total_sessions', 0)}")
                self.display.show_message(f"Average Score: {performance.get('average_score', 0):.1f}%")
                self.display.show_message(f"Average Accuracy: {performance.get('average_accuracy', 0):.1f}%")
            
        except Exception as e:
            logger.error(f"Error showing quick stats: {e}")
            self.display.show_error(f"An error occurred: {e}")
    
    def show_analytics_help(self) -> None:
        """Display analytics help information."""
        try:
            self.display.show_section_header("Analytics Help")
            
            self.display.show_message("Analytics Dashboard Features:")
            self.display.show_message("")
            self.display.show_message("📊 Performance Analytics:")
            self.display.show_message("  - Session performance metrics")
            self.display.show_message("  - Accuracy and score trends")
            self.display.show_message("  - Time-based analysis")
            self.display.show_message("  - Efficiency measurements")
            self.display.show_message("")
            self.display.show_message("🎓 Learning Analytics:")
            self.display.show_message("  - Learning progress tracking")
            self.display.show_message("  - Knowledge gap identification")
            self.display.show_message("  - Mastery level assessment")
            self.display.show_message("  - Retention rate analysis")
            self.display.show_message("")
            self.display.show_message("❓ Question Analytics:")
            self.display.show_message("  - Question difficulty analysis")
            self.display.show_message("  - Response time patterns")
            self.display.show_message("  - Question effectiveness scores")
            self.display.show_message("  - Usage statistics")
            self.display.show_message("")
            self.display.show_message("🏷️ Tag Analytics:")
            self.display.show_message("  - Tag usage patterns")
            self.display.show_message("  - Tag performance metrics")
            self.display.show_message("  - Tag correlation analysis")
            self.display.show_message("  - Tag effectiveness scores")
            self.display.show_message("")
            self.display.show_message("🖥️ System Analytics:")
            self.display.show_message("  - System health monitoring")
            self.display.show_message("  - Usage statistics")
            self.display.show_message("  - Performance metrics")
            self.display.show_message("  - Growth tracking")
            self.display.show_message("")
            self.display.show_message("📤 Export Options:")
            self.display.show_message("  - JSON format for data processing")
            self.display.show_message("  - CSV format for spreadsheet analysis")
            self.display.show_message("  - HTML format for reports")
            
            self.prompts.get_text_input("Press Enter to continue...")
            
        except Exception as e:
            logger.error(f"Error showing analytics help: {e}")
            self.display.show_error(f"An error occurred: {e}")
