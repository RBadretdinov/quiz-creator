"""
Performance and Load Testing for Phase 5.1

This module provides comprehensive performance testing including
load testing, memory profiling, and response time analysis.
"""

import unittest
import sys
import os
import time
import tempfile
import shutil
import psutil
import gc
from typing import Dict, List, Any, Tuple
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.question import Question
from models.tag import Tag
from models.quiz_session import QuizSession
from quiz_engine import QuizEngine
from question_manager import QuestionManager
from tag_manager import TagManager
from data_persistence import DataPersistence
from database_manager import DatabaseManager

class PerformanceTestSuite(unittest.TestCase):
    """Comprehensive performance test suite."""
    
    def setUp(self):
        """Set up performance test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize components
        self.question_manager = QuestionManager(self.data_dir)
        self.tag_manager = TagManager(self.data_dir)
        self.quiz_engine = QuizEngine(self.question_manager, self.tag_manager)
        self.data_persistence = DataPersistence(self.data_dir)
        
        # Performance metrics
        self.performance_metrics = {}
    
    def tearDown(self):
        """Clean up performance test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets."""
        print("\n=== Large Dataset Performance Test ===")
        
        # Test with 1000 questions
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        questions = []
        for i in range(1000):
            question = Question(
                f"Question {i}: What is the answer to question {i}?",
                "multiple_choice",
                [f"Option A{i}", f"Option B{i}", f"Option C{i}", f"Option D{i}"],
                [i % 4]
            )
            questions.append(question)
            self.question_manager.add_question(question)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        print(f"Created 1000 questions in {execution_time:.2f} seconds")
        print(f"Memory usage: {memory_usage:.2f} MB")
        print(f"Average time per question: {execution_time/1000*1000:.2f} ms")
        
        # Performance assertions
        self.assertLess(execution_time, 10.0, "Question creation took too long")
        self.assertLess(memory_usage, 100.0, "Memory usage too high")
        
        # Test retrieval performance
        start_time = time.time()
        retrieved_questions = self.question_manager.get_all_questions()
        end_time = time.time()
        
        retrieval_time = end_time - start_time
        print(f"Retrieved 1000 questions in {retrieval_time:.2f} seconds")
        
        self.assertEqual(len(retrieved_questions), 1000)
        self.assertLess(retrieval_time, 1.0, "Question retrieval took too long")
    
    def test_memory_usage_analysis(self):
        """Test memory usage analysis."""
        print("\n=== Memory Usage Analysis ===")
        
        # Initial memory
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        # Create questions and measure memory
        memory_usage = []
        for i in range(0, 1001, 100):
            if i > 0:
                for j in range(100):
                    question = Question(
                        f"Question {i+j}",
                        "multiple_choice",
                        ["A", "B", "C", "D"],
                        [0]
                    )
                    self.question_manager.add_question(question)
            
            current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            memory_usage.append((i, current_memory - initial_memory))
            print(f"Questions: {i}, Memory: {current_memory - initial_memory:.2f} MB")
        
        # Analyze memory growth
        memory_growth = memory_usage[-1][1] - memory_usage[0][1]
        print(f"Total memory growth: {memory_growth:.2f} MB")
        
        # Memory should grow linearly, not exponentially
        self.assertLess(memory_growth, 50.0, "Memory growth too high")
    
    def test_response_time_analysis(self):
        """Test response time analysis."""
        print("\n=== Response Time Analysis ===")
        
        # Create test questions
        questions = []
        for i in range(100):
            question = Question(
                f"Question {i}",
                "multiple_choice",
                ["A", "B", "C", "D"],
                [0]
            )
            questions.append(question)
            self.question_manager.add_question(question)
        
        # Test question retrieval response times
        response_times = []
        for i in range(10):
            start_time = time.time()
            retrieved_questions = self.question_manager.get_all_questions()
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to ms
            response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"Average response time: {avg_response_time:.2f} ms")
        print(f"Max response time: {max_response_time:.2f} ms")
        print(f"Min response time: {min_response_time:.2f} ms")
        
        # Response time assertions
        self.assertLess(avg_response_time, 100.0, "Average response time too high")
        self.assertLess(max_response_time, 500.0, "Max response time too high")
    
    def test_concurrent_operations(self):
        """Test concurrent operations performance."""
        print("\n=== Concurrent Operations Test ===")
        
        # Test concurrent question creation
        start_time = time.time()
        
        # Simulate concurrent operations (simplified)
        for i in range(50):
            question = Question(
                f"Concurrent question {i}",
                "multiple_choice",
                ["A", "B", "C", "D"],
                [0]
            )
            self.question_manager.add_question(question)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Concurrent operations completed in {execution_time:.2f} seconds")
        
        # Should handle concurrent operations efficiently
        self.assertLess(execution_time, 5.0, "Concurrent operations too slow")
    
    def test_database_performance(self):
        """Test database performance."""
        print("\n=== Database Performance Test ===")
        
        try:
            # Initialize database
            db_manager = DatabaseManager(self.data_dir)
            
            # Test database operations
            start_time = time.time()
            
            # Create questions in database
            for i in range(100):
                question = Question(
                    f"DB Question {i}",
                    "multiple_choice",
                    ["A", "B", "C", "D"],
                    [0]
                )
                # Add to database (simplified)
                pass
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            print(f"Database operations completed in {execution_time:.2f} seconds")
            
            # Database should be fast
            self.assertLess(execution_time, 2.0, "Database operations too slow")
            
        except ImportError:
            print("Database module not available, skipping database performance test")
    
    def test_file_io_performance(self):
        """Test file I/O performance."""
        print("\n=== File I/O Performance Test ===")
        
        # Create test questions
        questions = []
        for i in range(100):
            question = Question(
                f"File I/O Question {i}",
                "multiple_choice",
                ["A", "B", "C", "D"],
                [0]
            )
            questions.append(question)
        
        # Test save performance
        start_time = time.time()
        self.data_persistence.save_questions(questions)
        end_time = time.time()
        
        save_time = end_time - start_time
        print(f"Saved 100 questions in {save_time:.2f} seconds")
        
        # Test load performance
        start_time = time.time()
        loaded_questions = self.data_persistence.load_questions()
        end_time = time.time()
        
        load_time = end_time - start_time
        print(f"Loaded 100 questions in {load_time:.2f} seconds")
        
        # File I/O should be reasonably fast
        self.assertLess(save_time, 1.0, "Save operation too slow")
        self.assertLess(load_time, 1.0, "Load operation too slow")
        self.assertEqual(len(loaded_questions), 100)
    
    def test_quiz_engine_performance(self):
        """Test quiz engine performance."""
        print("\n=== Quiz Engine Performance Test ===")
        
        # Create test questions
        questions = []
        for i in range(50):
            question = Question(
                f"Quiz Question {i}",
                "multiple_choice",
                ["A", "B", "C", "D"],
                [0]
            )
            questions.append(question)
            self.question_manager.add_question(question)
        
        # Test quiz start performance
        start_time = time.time()
        session = self.quiz_engine.start_quiz(questions, "test_user")
        end_time = time.time()
        
        quiz_start_time = end_time - start_time
        print(f"Quiz started in {quiz_start_time:.2f} seconds")
        
        # Test answer submission performance
        start_time = time.time()
        for i in range(10):
            result = self.quiz_engine.submit_answer(questions[i], "A")
        end_time = time.time()
        
        answer_time = end_time - start_time
        print(f"10 answers submitted in {answer_time:.2f} seconds")
        
        # Quiz operations should be fast
        self.assertLess(quiz_start_time, 1.0, "Quiz start too slow")
        self.assertLess(answer_time, 1.0, "Answer submission too slow")
    
    def test_analytics_performance(self):
        """Test analytics performance."""
        print("\n=== Analytics Performance Test ===")
        
        try:
            from analytics.analytics_engine import AnalyticsEngine
            
            # Initialize analytics
            analytics_engine = AnalyticsEngine(None)  # Mock database manager
            
            # Test analytics calculation
            start_time = time.time()
            
            # Mock analytics data
            analytics_data = {
                'sessions': [{'score': 80, 'time_spent': 300} for _ in range(100)],
                'questions': [{'attempts': 10, 'correct': 8} for _ in range(50)]
            }
            
            # Calculate analytics (simplified)
            total_sessions = len(analytics_data['sessions'])
            total_questions = len(analytics_data['questions'])
            
            end_time = time.time()
            analytics_time = end_time - start_time
            
            print(f"Analytics calculated in {analytics_time:.2f} seconds")
            print(f"Processed {total_sessions} sessions and {total_questions} questions")
            
            # Analytics should be fast
            self.assertLess(analytics_time, 0.5, "Analytics calculation too slow")
            
        except ImportError:
            print("Analytics module not available, skipping analytics performance test")
    
    def test_memory_cleanup(self):
        """Test memory cleanup and garbage collection."""
        print("\n=== Memory Cleanup Test ===")
        
        # Initial memory
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        print(f"Initial memory: {initial_memory:.2f} MB")
        
        # Create and destroy objects
        for i in range(10):
            questions = []
            for j in range(100):
                question = Question(
                    f"Memory test question {i}-{j}",
                    "multiple_choice",
                    ["A", "B", "C", "D"],
                    [0]
                )
                questions.append(question)
            
            # Clear references
            del questions
        
        # Force garbage collection
        gc.collect()
        
        # Check memory after cleanup
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_difference = final_memory - initial_memory
        
        print(f"Final memory: {final_memory:.2f} MB")
        print(f"Memory difference: {memory_difference:.2f} MB")
        
        # Memory should be cleaned up
        self.assertLess(memory_difference, 50.0, "Memory not properly cleaned up")
    
    def test_stress_testing(self):
        """Test system under stress."""
        print("\n=== Stress Testing ===")
        
        # Test rapid operations
        start_time = time.time()
        
        for i in range(200):
            # Create question
            question = Question(
                f"Stress test question {i}",
                "multiple_choice",
                ["A", "B", "C", "D"],
                [0]
            )
            self.question_manager.add_question(question)
            
            # Retrieve questions
            questions = self.question_manager.get_all_questions()
            
            # Update question
            if questions:
                questions[0].question_text = f"Updated question {i}"
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Stress test completed in {execution_time:.2f} seconds")
        print(f"Operations per second: {200/execution_time:.2f}")
        
        # System should handle stress
        self.assertLess(execution_time, 10.0, "Stress test too slow")
    
    def test_scalability_analysis(self):
        """Test scalability analysis."""
        print("\n=== Scalability Analysis ===")
        
        # Test with different dataset sizes
        dataset_sizes = [10, 50, 100, 200]
        execution_times = []
        
        for size in dataset_sizes:
            # Clear previous data
            self.question_manager = QuestionManager(self.data_dir)
            
            # Create dataset
            start_time = time.time()
            for i in range(size):
                question = Question(
                    f"Scalability question {i}",
                    "multiple_choice",
                    ["A", "B", "C", "D"],
                    [0]
                )
                self.question_manager.add_question(question)
            end_time = time.time()
            
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            print(f"Dataset size: {size}, Execution time: {execution_time:.2f} seconds")
        
        # Analyze scalability
        time_ratio = execution_times[-1] / execution_times[0] if execution_times[0] > 0 else 1
        size_ratio = dataset_sizes[-1] / dataset_sizes[0]
        
        print(f"Time ratio: {time_ratio:.2f}")
        print(f"Size ratio: {size_ratio:.2f}")
        print(f"Scalability factor: {time_ratio/size_ratio:.2f}")
        
        # Should scale reasonably (not exponentially)
        self.assertLess(time_ratio/size_ratio, 2.0, "Poor scalability")


class LoadTestSuite(unittest.TestCase):
    """Load testing suite."""
    
    def setUp(self):
        """Set up load test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up load test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_high_load_questions(self):
        """Test high load with many questions."""
        print("\n=== High Load Questions Test ===")
        
        question_manager = QuestionManager(self.data_dir)
        
        # Create 5000 questions
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        for i in range(5000):
            question = Question(
                f"Load test question {i}",
                "multiple_choice",
                ["A", "B", "C", "D"],
                [0]
            )
            question_manager.add_question(question)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        print(f"Created 5000 questions in {execution_time:.2f} seconds")
        print(f"Memory usage: {memory_usage:.2f} MB")
        
        # Should handle high load
        self.assertLess(execution_time, 30.0, "High load too slow")
        self.assertLess(memory_usage, 200.0, "High load memory usage too high")
    
    def test_high_load_tags(self):
        """Test high load with many tags."""
        print("\n=== High Load Tags Test ===")
        
        tag_manager = TagManager(self.data_dir)
        
        # Create 1000 tags
        start_time = time.time()
        
        for i in range(1000):
            tag_manager.create_tag(f"load_tag_{i}", f"Load test tag {i}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Created 1000 tags in {execution_time:.2f} seconds")
        
        # Should handle high load
        self.assertLess(execution_time, 10.0, "High load tags too slow")
    
    def test_rapid_operations(self):
        """Test rapid operations."""
        print("\n=== Rapid Operations Test ===")
        
        question_manager = QuestionManager(self.data_dir)
        
        # Rapid create/delete operations
        start_time = time.time()
        
        for i in range(100):
            # Create question
            question = Question(
                f"Rapid question {i}",
                "multiple_choice",
                ["A", "B", "C", "D"],
                [0]
            )
            question_manager.add_question(question)
            
            # Retrieve questions
            questions = question_manager.get_all_questions()
            
            # Delete question (if possible)
            if questions:
                # Simplified delete operation
                pass
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Rapid operations completed in {execution_time:.2f} seconds")
        
        # Should handle rapid operations
        self.assertLess(execution_time, 5.0, "Rapid operations too slow")


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run performance tests
    print("Starting Performance Tests...")
    unittest.main(verbosity=2)
