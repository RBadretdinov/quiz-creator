"""
Test Suite for Phase 4.1: OCR Processing System

This module contains comprehensive unit tests for the advanced OCR functionality
implemented in Phase 4.1.
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ocr import AdvancedOCRProcessor, OCRTester

class TestAdvancedOCRProcessor(unittest.TestCase):
    """Test cases for AdvancedOCRProcessor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, 'ocr_cache')
        
        # Mock OCR dependencies
        with patch.dict('sys.modules', {
            'pytesseract': Mock(),
            'PIL': Mock(),
            'cv2': Mock(),
            'numpy': Mock(),
            'skimage': Mock()
        }):
            self.ocr_processor = AdvancedOCRProcessor(self.cache_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ocr_processor_initialization(self):
        """Test OCR processor initialization."""
        self.assertIsNotNone(self.ocr_processor)
        self.assertEqual(self.ocr_processor.cache_dir, Path(self.cache_dir))
        self.assertEqual(self.ocr_processor.confidence_threshold, 60)
        self.assertEqual(self.ocr_processor.target_dpi, 300)
    
    def test_process_screenshot_without_dependencies(self):
        """Test processing screenshot when OCR dependencies are not available."""
        # Create a temporary image file
        test_image = os.path.join(self.temp_dir, 'test.png')
        with open(test_image, 'w') as f:
            f.write('fake image data')
        
        # Mock OCR_AVAILABLE = False
        with patch('ocr.advanced_ocr_processor.OCR_AVAILABLE', False):
            result = self.ocr_processor.process_screenshot(test_image)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'OCR dependencies not available')
        self.assertEqual(result['text'], '')
        self.assertEqual(result['confidence'], 0)
    
    def test_batch_process_images(self):
        """Test batch processing of multiple images."""
        # Create test images
        test_images = []
        for i in range(3):
            image_path = os.path.join(self.temp_dir, f'test_{i}.png')
            with open(image_path, 'w') as f:
                f.write(f'fake image data {i}')
            test_images.append(image_path)
        
        # Mock OCR_AVAILABLE = False
        with patch('ocr.advanced_ocr_processor.OCR_AVAILABLE', False):
            result = self.ocr_processor.batch_process_images(test_images)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'OCR dependencies not available')
        self.assertEqual(len(result['results']), 3)
        self.assertEqual(result['summary']['total_images'], 3)
    
    def test_generate_cache_key(self):
        """Test cache key generation."""
        image_path = "/path/to/image.png"
        options = {"resize_to_dpi": True, "contrast_enhancement": False}
        
        key1 = self.ocr_processor._generate_cache_key(image_path, options)
        key2 = self.ocr_processor._generate_cache_key(image_path, options)
        
        # Same inputs should generate same key
        self.assertEqual(key1, key2)
        
        # Different options should generate different key
        different_options = {"resize_to_dpi": False}
        key3 = self.ocr_processor._generate_cache_key(image_path, different_options)
        self.assertNotEqual(key1, key3)
    
    def test_get_processing_statistics(self):
        """Test getting processing statistics."""
        stats = self.ocr_processor.get_processing_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_images'], 0)
        self.assertEqual(stats['successful_extractions'], 0)
        self.assertEqual(stats['failed_extractions'], 0)
        self.assertEqual(stats['average_confidence'], 0.0)
        self.assertEqual(stats['average_processing_time'], 0.0)
    
    def test_clear_cache(self):
        """Test clearing OCR cache."""
        # Create a fake cache file
        cache_file = Path(self.cache_dir) / "test_cache.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text('{"test": "data"}')
        
        # Clear cache
        self.ocr_processor.clear_cache()
        
        # Cache file should be deleted
        self.assertFalse(cache_file.exists())
    
    def test_parse_questions_from_text(self):
        """Test parsing questions from extracted text."""
        # Test with sample text
        sample_text = """
        1. What is the capital of France?
        A. London
        B. Paris
        C. Berlin
        
        2. Which planet is closest to the Sun?
        A. Venus
        B. Mercury
        C. Earth
        """
        
        questions = self.ocr_processor._parse_questions_from_text(sample_text)
        
        self.assertIsInstance(questions, list)
        self.assertEqual(len(questions), 2)
        
        # Check first question
        self.assertIn("capital of France", questions[0]['question_text'])
        self.assertEqual(len(questions[0]['answers']), 3)
        self.assertEqual(questions[0]['question_type'], 'multiple_choice')
    
    def test_is_question_line(self):
        """Test question line detection."""
        # Test question patterns
        self.assertTrue(self.ocr_processor._is_question_line("1. What is the capital?"))
        self.assertTrue(self.ocr_processor._is_question_line("What is the capital?"))
        self.assertTrue(self.ocr_processor._is_question_line("Which city is largest?"))
        
        # Test non-question patterns
        self.assertFalse(self.ocr_processor._is_question_line("This is a statement."))
        self.assertFalse(self.ocr_processor._is_question_line("A. Answer option"))
    
    def test_is_answer_line(self):
        """Test answer line detection."""
        # Test answer patterns
        self.assertTrue(self.ocr_processor._is_answer_line("A. Paris"))
        self.assertTrue(self.ocr_processor._is_answer_line("1. London"))
        self.assertTrue(self.ocr_processor._is_answer_line("True"))
        self.assertTrue(self.ocr_processor._is_answer_line("False"))
        
        # Test non-answer patterns
        self.assertFalse(self.ocr_processor._is_answer_line("What is the capital?"))
        self.assertFalse(self.ocr_processor._is_answer_line("This is a question."))
    
    def test_is_correct_answer(self):
        """Test correct answer detection."""
        # Test correct answer indicators
        self.assertTrue(self.ocr_processor._is_correct_answer("A. Paris *"))
        self.assertTrue(self.ocr_processor._is_correct_answer("B. London ✓"))
        self.assertTrue(self.ocr_processor._is_correct_answer("C. Berlin (correct)"))
        self.assertTrue(self.ocr_processor._is_correct_answer("D. Madrid [x]"))
        
        # Test non-correct answers
        self.assertFalse(self.ocr_processor._is_correct_answer("A. Paris"))
        self.assertFalse(self.ocr_processor._is_correct_answer("B. London"))
    
    def test_determine_question_type(self):
        """Test question type determination."""
        # Test True/False
        tf_answers = [
            {"text": "True", "is_correct": True},
            {"text": "False", "is_correct": False}
        ]
        self.assertEqual(self.ocr_processor._determine_question_type(tf_answers), 'true_false')
        
        # Test multiple choice
        mc_answers = [
            {"text": "A. Option 1", "is_correct": False},
            {"text": "B. Option 2", "is_correct": True},
            {"text": "C. Option 3", "is_correct": False}
        ]
        self.assertEqual(self.ocr_processor._determine_question_type(mc_answers), 'multiple_choice')
        
        # Test empty answers
        self.assertEqual(self.ocr_processor._determine_question_type([]), 'multiple_choice')
    
    def test_assess_image_quality(self):
        """Test image quality assessment."""
        # Create a mock image
        mock_image = Mock()
        mock_image.size = (800, 600)
        
        # Mock numpy operations
        with patch('ocr.advanced_ocr_processor.np') as mock_np:
            mock_np.array.return_value = [[[100, 150, 200]]]
            mock_np.mean.return_value = 150
            mock_np.std.return_value = 50
            
            with patch('ocr.advanced_ocr_processor.cv2') as mock_cv2:
                mock_cv2.cvtColor.return_value = [[100]]
                mock_cv2.Laplacian.return_value.var.return_value = 200
                
                quality = self.ocr_processor._assess_image_quality(mock_image)
        
        self.assertIsInstance(quality, dict)
        self.assertIn('quality_score', quality)
        self.assertIn('sharpness', quality)
        self.assertIn('contrast', quality)
        self.assertIn('brightness', quality)
        self.assertIn('recommendations', quality)
    
    def test_get_quality_recommendations(self):
        """Test quality recommendations generation."""
        # Test various quality scenarios
        recommendations = self.ocr_processor._get_quality_recommendations(30, 50, 30, 80)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Test good quality
        recommendations = self.ocr_processor._get_quality_recommendations(90, 200, 80, 150)
        self.assertIsInstance(recommendations, list)


class TestOCRTester(unittest.TestCase):
    """Test cases for OCRTester."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data_dir = os.path.join(self.temp_dir, 'test_data')
        
        self.ocr_tester = OCRTester(self.test_data_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ocr_tester_initialization(self):
        """Test OCR tester initialization."""
        self.assertIsNotNone(self.ocr_tester)
        self.assertEqual(self.ocr_tester.test_data_dir, Path(self.test_data_dir))
        self.assertEqual(len(self.ocr_tester.test_results), 0)
        self.assertEqual(len(self.ocr_tester.benchmark_results), 0)
    
    def test_run_accuracy_test(self):
        """Test running accuracy test."""
        # Create test images
        test_images = []
        for i in range(3):
            image_path = os.path.join(self.temp_dir, f'test_{i}.png')
            with open(image_path, 'w') as f:
                f.write(f'fake image data {i}')
            test_images.append(image_path)
        
        expected_texts = [
            "Sample text 1",
            "Sample text 2", 
            "Sample text 3"
        ]
        
        result = self.ocr_tester.run_accuracy_test(test_images, expected_texts, "test_accuracy")
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['test_name'], 'test_accuracy')
        self.assertEqual(result['total_images'], 3)
        self.assertIn('average_accuracy', result)
        self.assertIn('average_confidence', result)
        self.assertIn('results', result)
        self.assertEqual(len(result['results']), 3)
    
    def test_run_performance_benchmark(self):
        """Test running performance benchmark."""
        # Create test images
        test_images = []
        for i in range(2):
            image_path = os.path.join(self.temp_dir, f'benchmark_{i}.png')
            with open(image_path, 'w') as f:
                f.write(f'benchmark data {i}')
            test_images.append(image_path)
        
        result = self.ocr_tester.run_performance_benchmark(test_images, iterations=2)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['test_name'], 'performance_benchmark')
        self.assertEqual(result['iterations'], 2)
        self.assertEqual(result['total_images'], 2)
        self.assertIn('statistics', result)
        self.assertIn('iterations', result)
        self.assertEqual(len(result['iterations']), 2)
    
    def test_run_quality_analysis(self):
        """Test running quality analysis."""
        # Create test images
        test_images = []
        for i in range(2):
            image_path = os.path.join(self.temp_dir, f'quality_{i}.png')
            with open(image_path, 'w') as f:
                f.write(f'quality data {i}')
            test_images.append(image_path)
        
        result = self.ocr_tester.run_quality_analysis(test_images)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['test_name'], 'quality_analysis')
        self.assertEqual(result['total_images'], 2)
        self.assertIn('statistics', result)
        self.assertIn('results', result)
        self.assertEqual(len(result['results']), 2)
    
    def test_run_comprehensive_test_suite(self):
        """Test running comprehensive test suite."""
        # Create test images
        test_images = []
        for i in range(2):
            image_path = os.path.join(self.temp_dir, f'comprehensive_{i}.png')
            with open(image_path, 'w') as f:
                f.write(f'comprehensive data {i}')
            test_images.append(image_path)
        
        expected_texts = ["Expected 1", "Expected 2"]
        
        result = self.ocr_tester.run_comprehensive_test_suite(test_images, expected_texts)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['test_suite'], 'comprehensive_ocr_test')
        self.assertEqual(result['total_images'], 2)
        self.assertIn('accuracy_test', result)
        self.assertIn('performance_test', result)
        self.assertIn('quality_test', result)
        self.assertIn('overall_assessment', result)
    
    def test_calculate_text_accuracy(self):
        """Test text accuracy calculation."""
        # Test identical texts
        accuracy = self.ocr_tester._calculate_text_accuracy("Hello world", "Hello world")
        self.assertEqual(accuracy, 100.0)
        
        # Test similar texts
        accuracy = self.ocr_tester._calculate_text_accuracy("Hello world", "Hello there world")
        self.assertGreater(accuracy, 0)
        self.assertLess(accuracy, 100)
        
        # Test completely different texts
        accuracy = self.ocr_tester._calculate_text_accuracy("Hello world", "Goodbye universe")
        self.assertEqual(accuracy, 0.0)
        
        # Test empty texts
        accuracy = self.ocr_tester._calculate_text_accuracy("", "Hello world")
        self.assertEqual(accuracy, 0.0)
    
    def test_export_test_results(self):
        """Test exporting test results."""
        # Add some test results
        self.ocr_tester.test_results.append({
            'test_name': 'test1',
            'total_images': 2,
            'average_accuracy': 85.0
        })
        
        # Export results
        output_file = self.ocr_tester.export_test_results()
        
        self.assertIsInstance(output_file, str)
        self.assertTrue(output_file.endswith('.json'))
        
        # Check if file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Clean up
        if os.path.exists(output_file):
            os.remove(output_file)
    
    def test_clear_test_results(self):
        """Test clearing test results."""
        # Add some test results
        self.ocr_tester.test_results.append({'test': 'data'})
        self.ocr_tester.benchmark_results.append({'benchmark': 'data'})
        
        # Clear results
        self.ocr_tester.clear_test_results()
        
        self.assertEqual(len(self.ocr_tester.test_results), 0)
        self.assertEqual(len(self.ocr_tester.benchmark_results), 0)
    
    def test_get_test_statistics(self):
        """Test getting test statistics."""
        # Test with no results
        stats = self.ocr_tester.get_test_statistics()
        self.assertIn('message', stats)
        
        # Add some test results
        self.ocr_tester.test_results.append({
            'test_name': 'test1',
            'timestamp': '2023-01-01T00:00:00',
            'total_images': 5,
            'average_accuracy': 80.0,
            'average_confidence': 75.0,
            'average_processing_time': 2.5
        })
        
        stats = self.ocr_tester.get_test_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total_test_runs'], 1)
        self.assertEqual(stats['total_images_tested'], 5)
        self.assertEqual(stats['average_accuracy'], 80.0)
        self.assertEqual(stats['average_confidence'], 75.0)
        self.assertEqual(stats['average_processing_time'], 2.5)


class TestOCRIntegration(unittest.TestCase):
    """Integration tests for OCR functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock OCR dependencies for integration tests
        with patch.dict('sys.modules', {
            'pytesseract': Mock(),
            'PIL': Mock(),
            'cv2': Mock(),
            'numpy': Mock(),
            'skimage': Mock()
        }):
            self.ocr_processor = AdvancedOCRProcessor()
            self.ocr_tester = OCRTester()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ocr_processor_with_tester(self):
        """Test OCR processor integration with tester."""
        # Create test images
        test_images = []
        for i in range(2):
            image_path = os.path.join(self.temp_dir, f'integration_{i}.png')
            with open(image_path, 'w') as f:
                f.write(f'integration data {i}')
            test_images.append(image_path)
        
        # Run accuracy test
        result = self.ocr_tester.run_accuracy_test(test_images)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_images'], 2)
        self.assertIn('results', result)
    
    def test_ocr_caching_integration(self):
        """Test OCR caching functionality."""
        # Test cache directory creation
        cache_dir = os.path.join(self.temp_dir, 'ocr_cache')
        processor = AdvancedOCRProcessor(cache_dir)
        
        self.assertEqual(processor.cache_dir, Path(cache_dir))
        self.assertTrue(Path(cache_dir).exists())
    
    def test_ocr_statistics_tracking(self):
        """Test OCR statistics tracking."""
        # Test initial statistics
        stats = self.ocr_processor.get_processing_statistics()
        
        self.assertEqual(stats['total_images'], 0)
        self.assertEqual(stats['successful_extractions'], 0)
        self.assertEqual(stats['failed_extractions'], 0)
        
        # Test statistics update (simulated)
        mock_result = {
            'success': True,
            'confidence': 85.0,
            'processing_time': 2.0
        }
        
        self.ocr_processor._update_statistics(mock_result)
        
        updated_stats = self.ocr_processor.get_processing_statistics()
        self.assertEqual(updated_stats['total_images'], 1)
        self.assertEqual(updated_stats['successful_extractions'], 1)


if __name__ == '__main__':
    # Set up logging
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Run tests
    unittest.main(verbosity=2)
