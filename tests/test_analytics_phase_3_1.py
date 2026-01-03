"""
Test Suite for Phase 3.1: Advanced Analytics Dashboard

This module contains comprehensive unit tests for the analytics functionality
implemented in Phase 3.1.
"""

import unittest
import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analytics import AnalyticsEngine, AnalyticsDashboard, AnalyticsVisualizer
from database_manager import DatabaseManager
from ui.display import DisplayManager
from ui.prompts import InputPrompts

class TestAnalyticsEngine(unittest.TestCase):
    """Test cases for AnalyticsEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_analytics.db')
        
        # Mock database manager
        self.mock_db_manager = Mock(spec=DatabaseManager)
        self.analytics_engine = AnalyticsEngine(self.mock_db_manager)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analytics_engine_initialization(self):
        """Test analytics engine initialization."""
        self.assertIsNotNone(self.analytics_engine)
        self.assertEqual(self.analytics_engine.db_manager, self.mock_db_manager)
        self.assertEqual(self.analytics_engine.cache_duration, 300)
    
    def test_collect_quiz_session_metrics(self):
        """Test collecting quiz session metrics."""
        session_data = {
            'id': 'test-session-1',
            'total_questions': 10,
            'correct_answers': 8,
            'score': 80.0,
            'duration_seconds': 300,
            'quiz_type': 'practice',
            'user_id': 'user-1',
            'is_complete': True,
            'pause_count': 2,
            'total_pause_time': 30
        }
        
        # Mock the _store_metrics method
        with patch.object(self.analytics_engine, '_store_metrics', return_value=True):
            metrics = self.analytics_engine.collect_quiz_session_metrics(session_data)
        
        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics['session_id'], 'test-session-1')
        self.assertEqual(metrics['total_questions'], 10)
        self.assertEqual(metrics['correct_answers'], 8)
        self.assertEqual(metrics['score'], 80.0)
        self.assertEqual(metrics['accuracy'], 0.8)
        self.assertEqual(metrics['questions_per_minute'], 2.0)
    
    def test_collect_question_metrics(self):
        """Test collecting question metrics."""
        # Mock the _store_metrics and _update_question_statistics methods
        with patch.object(self.analytics_engine, '_store_metrics', return_value=True), \
             patch.object(self.analytics_engine, '_update_question_statistics'):
            
            metrics = self.analytics_engine.collect_question_metrics(
                'question-1', 'answer-a', True, 15.5
            )
        
        self.assertIsInstance(metrics, dict)
        self.assertEqual(metrics['question_id'], 'question-1')
        self.assertEqual(metrics['user_answer'], 'answer-a')
        self.assertTrue(metrics['is_correct'])
        self.assertEqual(metrics['response_time'], 15.5)
        self.assertEqual(metrics['response_time_category'], 'fast')
    
    def test_categorize_response_time(self):
        """Test response time categorization."""
        # Test different response time categories
        self.assertEqual(self.analytics_engine._categorize_response_time(5), 'very_fast')
        self.assertEqual(self.analytics_engine._categorize_response_time(20), 'fast')
        self.assertEqual(self.analytics_engine._categorize_response_time(45), 'moderate')
        self.assertEqual(self.analytics_engine._categorize_response_time(90), 'slow')
        self.assertEqual(self.analytics_engine._categorize_response_time(150), 'very_slow')
    
    def test_get_performance_analytics(self):
        """Test getting performance analytics."""
        # Mock the _get_sessions_for_period method
        mock_sessions = [
            {'id': 'session-1', 'score': 80, 'total_questions': 10, 'correct_answers': 8, 'duration_seconds': 300},
            {'id': 'session-2', 'score': 90, 'total_questions': 10, 'correct_answers': 9, 'duration_seconds': 250}
        ]
        
        with patch.object(self.analytics_engine, '_get_sessions_for_period', return_value=mock_sessions):
            analytics = self.analytics_engine.get_performance_analytics()
        
        self.assertIsInstance(analytics, dict)
        self.assertEqual(analytics['total_sessions'], 2)
        self.assertEqual(analytics['total_questions'], 20)
        self.assertEqual(analytics['total_correct'], 17)
        self.assertEqual(analytics['average_score'], 85.0)
        self.assertEqual(analytics['average_accuracy'], 0.85)
    
    def test_get_learning_analytics(self):
        """Test getting learning analytics."""
        # Mock the _get_question_metrics_for_period method
        mock_question_metrics = [
            {'question_id': 'q1', 'is_correct': True, 'response_time': 10},
            {'question_id': 'q2', 'is_correct': False, 'response_time': 30},
            {'question_id': 'q1', 'is_correct': True, 'response_time': 8}
        ]
        
        with patch.object(self.analytics_engine, '_get_question_metrics_for_period', return_value=mock_question_metrics):
            analytics = self.analytics_engine.get_learning_analytics()
        
        self.assertIsInstance(analytics, dict)
        self.assertEqual(analytics['total_questions_attempted'], 3)
        self.assertEqual(analytics['unique_questions'], 2)
        self.assertEqual(analytics['overall_accuracy'], 2/3)
    
    def test_get_question_analytics(self):
        """Test getting question analytics."""
        # Mock the _get_question_metrics method
        mock_question_metrics = [
            {'question_id': 'q1', 'is_correct': True, 'response_time': 10, 'user_id': 'user1'},
            {'question_id': 'q1', 'is_correct': False, 'response_time': 30, 'user_id': 'user2'},
            {'question_id': 'q1', 'is_correct': True, 'response_time': 8, 'user_id': 'user1'}
        ]
        
        with patch.object(self.analytics_engine, '_get_question_metrics', return_value=mock_question_metrics):
            analytics = self.analytics_engine.get_question_analytics('q1')
        
        self.assertIsInstance(analytics, dict)
        self.assertEqual(analytics['total_attempts'], 3)
        self.assertEqual(analytics['unique_users'], 2)
        self.assertEqual(analytics['success_rate'], 2/3)
        self.assertEqual(analytics['average_response_time'], 16.0)
    
    def test_get_tag_analytics(self):
        """Test getting tag analytics."""
        # Mock the _get_tag_usage_data method
        mock_tag_usage = [
            {'id': 'tag1', 'name': 'Math', 'usage_count': 10},
            {'id': 'tag2', 'name': 'Science', 'usage_count': 5},
            {'id': 'tag3', 'name': 'History', 'usage_count': 15}
        ]
        
        with patch.object(self.analytics_engine, '_get_tag_usage_data', return_value=mock_tag_usage):
            analytics = self.analytics_engine.get_tag_analytics()
        
        self.assertIsInstance(analytics, dict)
        self.assertEqual(analytics['total_tags'], 3)
    
    def test_get_system_analytics(self):
        """Test getting system analytics."""
        # Mock the _get_system_data method
        mock_system_data = {
            'total_questions': 100,
            'total_tags': 20,
            'total_sessions': 50,
            'total_users': 5,
            'database_size': 1024
        }
        
        with patch.object(self.analytics_engine, '_get_system_data', return_value=mock_system_data):
            analytics = self.analytics_engine.get_system_analytics()
        
        self.assertIsInstance(analytics, dict)
        self.assertEqual(analytics['total_questions'], 100)
        self.assertEqual(analytics['total_tags'], 20)
        self.assertEqual(analytics['total_sessions'], 50)
        self.assertEqual(analytics['total_users'], 5)
        self.assertEqual(analytics['database_size'], 1024)
    
    def test_export_analytics(self):
        """Test exporting analytics."""
        # Mock the analytics methods
        mock_analytics = {'test': 'data', 'value': 123}
        
        with patch.object(self.analytics_engine, 'get_performance_analytics', return_value=mock_analytics), \
             patch.object(self.analytics_engine, '_export_json', return_value=True):
            
            result = self.analytics_engine.export_analytics('performance', 'json', 'test.json')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['file_path'], 'test.json')
        self.assertEqual(result['format'], 'json')
    
    def test_cache_functionality(self):
        """Test analytics caching functionality."""
        # Test cache validity
        self.assertFalse(self.analytics_engine._is_cache_valid('nonexistent_key'))
        
        # Test caching results
        test_data = {'test': 'data'}
        self.analytics_engine._cache_results('test_key', test_data)
        
        self.assertTrue(self.analytics_engine._is_cache_valid('test_key'))
        self.assertEqual(self.analytics_engine.metrics_cache['test_key'], test_data)
    
    def test_empty_analytics_structures(self):
        """Test empty analytics structures."""
        # Test all empty analytics methods
        empty_performance = self.analytics_engine._get_empty_analytics()
        self.assertIsInstance(empty_performance, dict)
        self.assertEqual(empty_performance['total_sessions'], 0)
        
        empty_learning = self.analytics_engine._get_empty_learning_analytics()
        self.assertIsInstance(empty_learning, dict)
        self.assertEqual(empty_learning['total_questions_attempted'], 0)
        
        empty_question = self.analytics_engine._get_empty_question_analytics()
        self.assertIsInstance(empty_question, dict)
        self.assertEqual(empty_question['total_attempts'], 0)
        
        empty_tag = self.analytics_engine._get_empty_tag_analytics()
        self.assertIsInstance(empty_tag, dict)
        self.assertEqual(empty_tag['total_tags'], 0)
        
        empty_system = self.analytics_engine._get_empty_system_analytics()
        self.assertIsInstance(empty_system, dict)
        self.assertEqual(empty_system['total_questions'], 0)


class TestAnalyticsDashboard(unittest.TestCase):
    """Test cases for AnalyticsDashboard."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_analytics_engine = Mock(spec=AnalyticsEngine)
        self.mock_display = Mock(spec=DisplayManager)
        self.mock_prompts = MagicMock(spec=InputPrompts)
        
        self.dashboard = AnalyticsDashboard(
            self.mock_analytics_engine,
            self.mock_display,
            self.mock_prompts
        )
    
    def test_analytics_dashboard_initialization(self):
        """Test analytics dashboard initialization."""
        self.assertIsNotNone(self.dashboard)
        self.assertEqual(self.dashboard.analytics_engine, self.mock_analytics_engine)
        self.assertEqual(self.dashboard.display, self.mock_display)
        self.assertEqual(self.dashboard.prompts, self.mock_prompts)
    
    def test_show_performance_analytics(self):
        """Test showing performance analytics."""
        # Mock the prompts and analytics engine
        self.mock_prompts.get_number_input.return_value = 30
        self.mock_prompts.get_text_input.return_value = None
        self.mock_prompts.get_yes_no_input.return_value = False
        
        mock_analytics = {
            'total_sessions': 10,
            'total_questions': 100,
            'average_score': 85.0
        }
        self.mock_analytics_engine.get_performance_analytics.return_value = mock_analytics
        
        # Test the method
        self.dashboard.show_performance_analytics()
        
        # Verify calls
        self.mock_prompts.get_number_input.assert_called_once()
        self.mock_prompts.get_text_input.assert_called_once()
        self.mock_analytics_engine.get_performance_analytics.assert_called_once_with(None, 30)
        self.mock_display.show_performance_analytics.assert_called_once_with(mock_analytics)
    
    def test_show_learning_analytics(self):
        """Test showing learning analytics."""
        # Mock the prompts and analytics engine
        self.mock_prompts.get_number_input.return_value = 30
        self.mock_prompts.get_text_input.return_value = None
        self.mock_prompts.get_yes_no_input.return_value = False
        
        mock_analytics = {
            'total_questions_attempted': 50,
            'overall_accuracy': 0.8
        }
        self.mock_analytics_engine.get_learning_analytics.return_value = mock_analytics
        
        # Test the method
        self.dashboard.show_learning_analytics()
        
        # Verify calls
        self.mock_analytics_engine.get_learning_analytics.assert_called_once_with(None, 30)
        self.mock_display.show_learning_analytics.assert_called_once_with(mock_analytics)
    
    def test_show_question_analytics(self):
        """Test showing question analytics."""
        # Mock the prompts and analytics engine
        self.mock_prompts.get_text_input.return_value = None
        self.mock_prompts.get_yes_no_input.return_value = False
        
        mock_analytics = {
            'total_attempts': 25,
            'success_rate': 0.75
        }
        self.mock_analytics_engine.get_question_analytics.return_value = mock_analytics
        
        # Test the method
        self.dashboard.show_question_analytics()
        
        # Verify calls
        self.mock_analytics_engine.get_question_analytics.assert_called_once_with(None)
        self.mock_display.show_question_analytics.assert_called_once_with(mock_analytics)
    
    def test_show_tag_analytics(self):
        """Test showing tag analytics."""
        # Mock the prompts and analytics engine
        self.mock_prompts.get_text_input.return_value = None
        self.mock_prompts.get_yes_no_input.return_value = False
        
        mock_analytics = {
            'total_tags': 15,
            'most_used_tags': []
        }
        self.mock_analytics_engine.get_tag_analytics.return_value = mock_analytics
        
        # Test the method
        self.dashboard.show_tag_analytics()
        
        # Verify calls
        self.mock_analytics_engine.get_tag_analytics.assert_called_once_with(None)
        self.mock_display.show_tag_analytics.assert_called_once_with(mock_analytics)
    
    def test_show_system_analytics(self):
        """Test showing system analytics."""
        # Mock the prompts and analytics engine
        self.mock_prompts.get_yes_no_input.return_value = False
        
        mock_analytics = {
            'total_questions': 100,
            'total_tags': 20,
            'system_health': 95.0
        }
        self.mock_analytics_engine.get_system_analytics.return_value = mock_analytics
        
        # Test the method
        self.dashboard.show_system_analytics()
        
        # Verify calls
        self.mock_analytics_engine.get_system_analytics.assert_called_once()
        self.mock_display.show_system_analytics.assert_called_once_with(mock_analytics)
    
    def test_export_analytics(self):
        """Test exporting analytics."""
        # Mock the prompts and analytics engine
        self.mock_prompts.get_menu_choice.side_effect = [1, 1]  # performance, json
        self.mock_prompts.get_text_input.return_value = None
        
        mock_export_result = {'success': True, 'file_path': 'test.json', 'format': 'json'}
        self.mock_analytics_engine.export_analytics.return_value = mock_export_result
        
        # Test the method
        self.dashboard.show_export_analytics()
        
        # Verify calls
        self.mock_analytics_engine.export_analytics.assert_called_once()
        self.mock_display.show_success.assert_called_once()
    
    def test_export_analytics_failure(self):
        """Test exporting analytics with failure."""
        # Mock the prompts and analytics engine
        self.mock_prompts.get_menu_choice.side_effect = [1, 1]  # performance, json
        self.mock_prompts.get_text_input.return_value = None
        
        mock_export_result = {'success': False, 'error': 'Export failed'}
        self.mock_analytics_engine.export_analytics.return_value = mock_export_result
        
        # Test the method
        self.dashboard.show_export_analytics()
        
        # Verify calls
        self.mock_display.show_error.assert_called_once_with("Export failed: Export failed")


class TestAnalyticsVisualizer(unittest.TestCase):
    """Test cases for AnalyticsVisualizer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.visualizer = AnalyticsVisualizer()
    
    def test_analytics_visualizer_initialization(self):
        """Test analytics visualizer initialization."""
        self.assertIsNotNone(self.visualizer)
        self.assertEqual(self.visualizer.chart_width, 60)
        self.assertEqual(self.visualizer.chart_height, 20)
    
    def test_create_bar_chart(self):
        """Test creating bar chart."""
        data = {'A': 10, 'B': 20, 'C': 15}
        chart = self.visualizer.create_bar_chart(data, "Test Chart")
        
        self.assertIsInstance(chart, str)
        self.assertIn("Test Chart", chart)
        self.assertIn("A", chart)
        self.assertIn("B", chart)
        self.assertIn("C", chart)
    
    def test_create_bar_chart_empty_data(self):
        """Test creating bar chart with empty data."""
        chart = self.visualizer.create_bar_chart({}, "Empty Chart")
        
        self.assertIsInstance(chart, str)
        self.assertIn("Empty Chart", chart)
        self.assertIn("No data available", chart)
    
    def test_create_line_chart(self):
        """Test creating line chart."""
        data = [
            {'date': '2023-01-01', 'value': 10},
            {'date': '2023-01-02', 'value': 15},
            {'date': '2023-01-03', 'value': 12}
        ]
        chart = self.visualizer.create_line_chart(data, "Trend Chart")
        
        self.assertIsInstance(chart, str)
        self.assertIn("Trend Chart", chart)
    
    def test_create_line_chart_empty_data(self):
        """Test creating line chart with empty data."""
        chart = self.visualizer.create_line_chart([], "Empty Trend")
        
        self.assertIsInstance(chart, str)
        self.assertIn("Empty Trend", chart)
        self.assertIn("No data available", chart)
    
    def test_create_pie_chart(self):
        """Test creating pie chart."""
        data = {'Red': 30, 'Blue': 20, 'Green': 50}
        chart = self.visualizer.create_pie_chart(data, "Color Distribution")
        
        self.assertIsInstance(chart, str)
        self.assertIn("Color Distribution", chart)
        self.assertIn("Red", chart)
        self.assertIn("Blue", chart)
        self.assertIn("Green", chart)
    
    def test_create_histogram(self):
        """Test creating histogram."""
        data = [1, 2, 2, 3, 3, 3, 4, 4, 5]
        chart = self.visualizer.create_histogram(data, "Value Distribution")
        
        self.assertIsInstance(chart, str)
        self.assertIn("Value Distribution", chart)
        self.assertIn("Total values: 9", chart)
    
    def test_create_heatmap(self):
        """Test creating heatmap."""
        data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        chart = self.visualizer.create_heatmap(data, "Data Heatmap")
        
        self.assertIsInstance(chart, str)
        self.assertIn("Data Heatmap", chart)
    
    def test_create_gauge(self):
        """Test creating gauge."""
        gauge = self.visualizer.create_gauge(75, 100, "Progress Gauge", "Completion")
        
        self.assertIsInstance(gauge, str)
        self.assertIn("Progress Gauge", gauge)
        self.assertIn("Completion: 75.0 / 100.0", gauge)
    
    def test_create_progress_bar(self):
        """Test creating progress bar."""
        progress = self.visualizer.create_progress_bar(75, 100, "Task Progress")
        
        self.assertIsInstance(progress, str)
        self.assertIn("Task Progress", progress)
        self.assertIn("Progress: 75 / 100", progress)
        self.assertIn("75.0%", progress)
    
    def test_create_summary_table(self):
        """Test creating summary table."""
        data = {'Total': 100, 'Average': 25.5, 'Count': 4}
        table = self.visualizer.create_summary_table(data, "Summary")
        
        self.assertIsInstance(table, str)
        self.assertIn("Summary", table)
        self.assertIn("Total", table)
        self.assertIn("Average", table)
        self.assertIn("Count", table)
    
    def test_create_trend_analysis(self):
        """Test creating trend analysis."""
        data = [
            {'timestamp': '2023-01-01', 'value': 10},
            {'timestamp': '2023-01-02', 'value': 15},
            {'timestamp': '2023-01-03', 'value': 12}
        ]
        analysis = self.visualizer.create_trend_analysis(data, "Trend Analysis")
        
        self.assertIsInstance(analysis, str)
        self.assertIn("Trend Analysis", analysis)
        self.assertIn("Trend Direction", analysis)
        self.assertIn("Average Value", analysis)


class TestAnalyticsIntegration(unittest.TestCase):
    """Integration tests for analytics functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_integration.db')
        
        # Create a real database manager for integration tests
        self.db_manager = DatabaseManager(self.db_path)
        self.analytics_engine = AnalyticsEngine(self.db_manager)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self.db_manager, 'close'):
            self.db_manager.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analytics_engine_with_real_database(self):
        """Test analytics engine with real database."""
        # Initialize database
        self.assertTrue(self.db_manager.initialize())
        
        # Test that analytics engine can be created
        self.assertIsNotNone(self.analytics_engine)
        
        # Test getting system analytics (should work even with empty database)
        system_analytics = self.analytics_engine.get_system_analytics()
        self.assertIsInstance(system_analytics, dict)
    
    def test_analytics_dashboard_integration(self):
        """Test analytics dashboard integration."""
        # Create mock components
        mock_display = Mock(spec=DisplayManager)
        mock_prompts = Mock(spec=InputPrompts)
        
        # Create dashboard
        dashboard = AnalyticsDashboard(self.analytics_engine, mock_display, mock_prompts)
        
        # Test dashboard creation
        self.assertIsNotNone(dashboard)
        self.assertEqual(dashboard.analytics_engine, self.analytics_engine)
    
    def test_analytics_visualizer_integration(self):
        """Test analytics visualizer integration."""
        # Test visualizer creation
        visualizer = AnalyticsVisualizer()
        self.assertIsNotNone(visualizer)
        
        # Test creating various visualizations
        test_data = {'A': 10, 'B': 20, 'C': 30}
        
        bar_chart = visualizer.create_bar_chart(test_data, "Test Chart")
        self.assertIsInstance(bar_chart, str)
        self.assertIn("Test Chart", bar_chart)
        
        pie_chart = visualizer.create_pie_chart(test_data, "Test Pie")
        self.assertIsInstance(pie_chart, str)
        self.assertIn("Test Pie", pie_chart)


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run tests
    unittest.main(verbosity=2)
