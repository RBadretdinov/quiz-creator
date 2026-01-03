"""
OCR Testing and Validation Framework

This module provides comprehensive testing capabilities for OCR accuracy,
performance benchmarking, and validation of OCR results.
"""

import os
import logging
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import statistics
from datetime import datetime

logger = logging.getLogger(__name__)

class OCRTester:
    """Comprehensive OCR testing and validation framework."""
    
    def __init__(self, test_data_dir: str = "data/ocr_tests"):
        """
        Initialize the OCR tester.
        
        Args:
            test_data_dir: Directory containing test images and expected results
        """
        self.test_data_dir = Path(test_data_dir)
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Test results storage
        self.test_results = []
        self.benchmark_results = []
        
        logger.info("OCR tester initialized")
    
    def run_accuracy_test(self, test_images: List[str], 
                          expected_texts: List[str] = None,
                          test_name: str = "accuracy_test") -> Dict[str, Any]:
        """
        Run comprehensive accuracy testing on a set of images.
        
        Args:
            test_images: List of image file paths
            expected_texts: List of expected text results (optional)
            test_name: Name for this test run
            
        Returns:
            Dictionary containing test results and statistics
        """
        logger.info(f"Starting accuracy test: {test_name}")
        start_time = time.time()
        
        results = []
        total_accuracy = 0
        confidence_scores = []
        processing_times = []
        
        for i, image_path in enumerate(test_images):
            try:
                # Process image (this would use the AdvancedOCRProcessor)
                # For now, we'll simulate the results
                result = self._simulate_ocr_processing(image_path)
                
                # Calculate accuracy if expected text provided
                accuracy = 0
                if expected_texts and i < len(expected_texts):
                    accuracy = self._calculate_text_accuracy(
                        result['text'], expected_texts[i]
                    )
                    total_accuracy += accuracy
                
                results.append({
                    'image_path': image_path,
                    'extracted_text': result['text'],
                    'expected_text': expected_texts[i] if expected_texts and i < len(expected_texts) else None,
                    'accuracy': accuracy,
                    'confidence': result['confidence'],
                    'processing_time': result['processing_time'],
                    'success': result['success']
                })
                
                confidence_scores.append(result['confidence'])
                processing_times.append(result['processing_time'])
                
            except Exception as e:
                logger.error(f"Error processing test image {image_path}: {e}")
                results.append({
                    'image_path': image_path,
                    'extracted_text': '',
                    'expected_text': expected_texts[i] if expected_texts and i < len(expected_texts) else None,
                    'accuracy': 0,
                    'confidence': 0,
                    'processing_time': 0,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate statistics
        total_time = time.time() - start_time
        average_accuracy = total_accuracy / len(test_images) if test_images else 0
        average_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
        average_processing_time = statistics.mean(processing_times) if processing_times else 0
        
        # Categorize results
        high_accuracy = len([r for r in results if r['accuracy'] >= 90])
        medium_accuracy = len([r for r in results if 70 <= r['accuracy'] < 90])
        low_accuracy = len([r for r in results if r['accuracy'] < 70])
        
        test_result = {
            'test_name': test_name,
            'timestamp': datetime.now().isoformat(),
            'total_images': len(test_images),
            'successful_extractions': len([r for r in results if r['success']]),
            'failed_extractions': len([r for r in results if not r['success']]),
            'average_accuracy': average_accuracy,
            'average_confidence': average_confidence,
            'average_processing_time': average_processing_time,
            'total_test_time': total_time,
            'accuracy_distribution': {
                'high_accuracy': high_accuracy,
                'medium_accuracy': medium_accuracy,
                'low_accuracy': low_accuracy
            },
            'results': results
        }
        
        # Store test result
        self.test_results.append(test_result)
        
        logger.info(f"Accuracy test completed: {average_accuracy:.1f}% average accuracy")
        return test_result
    
    def run_performance_benchmark(self, test_images: List[str], 
                                 iterations: int = 3) -> Dict[str, Any]:
        """
        Run performance benchmarking on OCR processing.
        
        Args:
            test_images: List of image file paths
            iterations: Number of iterations to run
            
        Returns:
            Dictionary containing benchmark results
        """
        logger.info(f"Starting performance benchmark with {iterations} iterations")
        
        benchmark_results = []
        
        for iteration in range(iterations):
            logger.info(f"Running iteration {iteration + 1}/{iterations}")
            
            iteration_results = []
            start_time = time.time()
            
            for image_path in test_images:
                try:
                    # Simulate OCR processing
                    result = self._simulate_ocr_processing(image_path)
                    iteration_results.append({
                        'image_path': image_path,
                        'processing_time': result['processing_time'],
                        'success': result['success']
                    })
                    
                except Exception as e:
                    logger.error(f"Error in benchmark iteration {iteration + 1}: {e}")
                    iteration_results.append({
                        'image_path': image_path,
                        'processing_time': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            iteration_time = time.time() - start_time
            
            benchmark_results.append({
                'iteration': iteration + 1,
                'total_time': iteration_time,
                'average_processing_time': iteration_time / len(test_images),
                'results': iteration_results
            })
        
        # Calculate statistics
        total_times = [r['total_time'] for r in benchmark_results]
        avg_processing_times = [r['average_processing_time'] for r in benchmark_results]
        
        benchmark_result = {
            'test_name': 'performance_benchmark',
            'timestamp': datetime.now().isoformat(),
            'iterations': iterations,
            'total_images': len(test_images),
            'statistics': {
                'average_total_time': statistics.mean(total_times),
                'min_total_time': min(total_times),
                'max_total_time': max(total_times),
                'average_processing_time': statistics.mean(avg_processing_times),
                'min_processing_time': min(avg_processing_times),
                'max_processing_time': max(avg_processing_times),
                'standard_deviation': statistics.stdev(total_times) if len(total_times) > 1 else 0
            },
            'iterations': benchmark_results
        }
        
        # Store benchmark result
        self.benchmark_results.append(benchmark_result)
        
        logger.info(f"Performance benchmark completed: {benchmark_result['statistics']['average_processing_time']:.2f}s average processing time")
        return benchmark_result
    
    def run_quality_analysis(self, test_images: List[str]) -> Dict[str, Any]:
        """
        Run image quality analysis to determine OCR suitability.
        
        Args:
            test_images: List of image file paths
            
        Returns:
            Dictionary containing quality analysis results
        """
        logger.info("Starting image quality analysis")
        
        quality_results = []
        
        for image_path in test_images:
            try:
                # Simulate quality analysis
                quality_result = self._simulate_quality_analysis(image_path)
                
                quality_results.append({
                    'image_path': image_path,
                    'quality_score': quality_result['quality_score'],
                    'sharpness': quality_result['sharpness'],
                    'contrast': quality_result['contrast'],
                    'brightness': quality_result['brightness'],
                    'recommendations': quality_result['recommendations'],
                    'ocr_suitability': quality_result['ocr_suitability']
                })
                
            except Exception as e:
                logger.error(f"Error analyzing quality for {image_path}: {e}")
                quality_results.append({
                    'image_path': image_path,
                    'quality_score': 0,
                    'sharpness': 0,
                    'contrast': 0,
                    'brightness': 0,
                    'recommendations': ['Error analyzing image'],
                    'ocr_suitability': 'poor',
                    'error': str(e)
                })
        
        # Calculate overall statistics
        quality_scores = [r['quality_score'] for r in quality_results]
        suitability_counts = {}
        for result in quality_results:
            suitability = result.get('ocr_suitability', 'unknown')
            suitability_counts[suitability] = suitability_counts.get(suitability, 0) + 1
        
        analysis_result = {
            'test_name': 'quality_analysis',
            'timestamp': datetime.now().isoformat(),
            'total_images': len(test_images),
            'statistics': {
                'average_quality_score': statistics.mean(quality_scores) if quality_scores else 0,
                'min_quality_score': min(quality_scores) if quality_scores else 0,
                'max_quality_score': max(quality_scores) if quality_scores else 0,
                'suitability_distribution': suitability_counts
            },
            'results': quality_results
        }
        
        logger.info(f"Quality analysis completed: {analysis_result['statistics']['average_quality_score']:.1f} average quality score")
        return analysis_result
    
    def run_comprehensive_test_suite(self, test_images: List[str], 
                                   expected_texts: List[str] = None) -> Dict[str, Any]:
        """
        Run a comprehensive test suite including accuracy, performance, and quality tests.
        
        Args:
            test_images: List of image file paths
            expected_texts: List of expected text results (optional)
            
        Returns:
            Dictionary containing all test results
        """
        logger.info("Starting comprehensive OCR test suite")
        
        suite_start_time = time.time()
        
        # Run all tests
        accuracy_test = self.run_accuracy_test(test_images, expected_texts, "comprehensive_accuracy")
        performance_test = self.run_performance_benchmark(test_images)
        quality_test = self.run_quality_analysis(test_images)
        
        suite_time = time.time() - suite_start_time
        
        # Compile comprehensive results
        comprehensive_result = {
            'test_suite': 'comprehensive_ocr_test',
            'timestamp': datetime.now().isoformat(),
            'total_images': len(test_images),
            'total_suite_time': suite_time,
            'accuracy_test': accuracy_test,
            'performance_test': performance_test,
            'quality_test': quality_test,
            'overall_assessment': self._assess_overall_performance(
                accuracy_test, performance_test, quality_test
            )
        }
        
        logger.info("Comprehensive test suite completed")
        return comprehensive_result
    
    def _simulate_ocr_processing(self, image_path: str) -> Dict[str, Any]:
        """Simulate OCR processing for testing purposes."""
        # This would normally use the AdvancedOCRProcessor
        # For testing, we'll simulate results
        
        # Simulate processing time (0.5-3 seconds)
        processing_time = 0.5 + (hash(image_path) % 25) / 10
        
        # Simulate confidence (60-95%)
        confidence = 60 + (hash(image_path) % 35)
        
        # Simulate success rate (80% success)
        success = (hash(image_path) % 10) < 8
        
        # Simulate extracted text
        if success:
            text = f"Sample extracted text from {os.path.basename(image_path)}"
        else:
            text = ""
        
        return {
            'text': text,
            'confidence': confidence,
            'processing_time': processing_time,
            'success': success
        }
    
    def _simulate_quality_analysis(self, image_path: str) -> Dict[str, Any]:
        """Simulate image quality analysis for testing purposes."""
        # Simulate quality metrics
        quality_score = 50 + (hash(image_path) % 50)
        sharpness = 100 + (hash(image_path) % 200)
        contrast = 50 + (hash(image_path) % 100)
        brightness = 100 + (hash(image_path) % 100)
        
        # Determine OCR suitability
        if quality_score >= 80:
            suitability = 'excellent'
        elif quality_score >= 60:
            suitability = 'good'
        elif quality_score >= 40:
            suitability = 'fair'
        else:
            suitability = 'poor'
        
        # Generate recommendations
        recommendations = []
        if sharpness < 150:
            recommendations.append("Image is blurry - improve focus")
        if contrast < 70:
            recommendations.append("Low contrast - improve lighting")
        if brightness < 120 or brightness > 180:
            recommendations.append("Adjust lighting for better brightness")
        
        return {
            'quality_score': quality_score,
            'sharpness': sharpness,
            'contrast': contrast,
            'brightness': brightness,
            'recommendations': recommendations,
            'ocr_suitability': suitability
        }
    
    def _calculate_text_accuracy(self, extracted_text: str, expected_text: str) -> float:
        """Calculate accuracy between extracted and expected text."""
        if not extracted_text or not expected_text:
            return 0.0
        
        # Simple word-based accuracy calculation
        extracted_words = set(extracted_text.lower().split())
        expected_words = set(expected_text.lower().split())
        
        if not expected_words:
            return 0.0
        
        # Calculate intersection and union
        intersection = extracted_words & expected_words
        union = extracted_words | expected_words
        
        # Jaccard similarity
        if union:
            return (len(intersection) / len(union)) * 100
        else:
            return 0.0
    
    def _assess_overall_performance(self, accuracy_test: Dict[str, Any], 
                                  performance_test: Dict[str, Any], 
                                  quality_test: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall OCR performance based on all test results."""
        # Extract key metrics
        accuracy = accuracy_test.get('average_accuracy', 0)
        confidence = accuracy_test.get('average_confidence', 0)
        processing_time = performance_test.get('statistics', {}).get('average_processing_time', 0)
        quality_score = quality_test.get('statistics', {}).get('average_quality_score', 0)
        
        # Determine overall rating
        if accuracy >= 90 and confidence >= 80 and processing_time <= 2.0:
            rating = 'excellent'
        elif accuracy >= 80 and confidence >= 70 and processing_time <= 3.0:
            rating = 'good'
        elif accuracy >= 70 and confidence >= 60 and processing_time <= 5.0:
            rating = 'fair'
        else:
            rating = 'poor'
        
        # Generate recommendations
        recommendations = []
        if accuracy < 80:
            recommendations.append("Improve OCR accuracy through better image preprocessing")
        if confidence < 70:
            recommendations.append("Enhance image quality for better confidence scores")
        if processing_time > 3.0:
            recommendations.append("Optimize processing speed for better performance")
        if quality_score < 60:
            recommendations.append("Improve input image quality")
        
        return {
            'overall_rating': rating,
            'accuracy_score': accuracy,
            'confidence_score': confidence,
            'performance_score': 100 - (processing_time * 20),  # Convert to score
            'quality_score': quality_score,
            'recommendations': recommendations
        }
    
    def export_test_results(self, output_file: str = None) -> str:
        """Export all test results to a JSON file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"ocr_test_results_{timestamp}.json"
        
        results = {
            'test_results': self.test_results,
            'benchmark_results': self.benchmark_results,
            'export_timestamp': datetime.now().isoformat()
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Test results exported to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error exporting test results: {e}")
            return ""
    
    def clear_test_results(self) -> None:
        """Clear all stored test results."""
        self.test_results = []
        self.benchmark_results = []
        logger.info("Test results cleared")
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """Get overall test statistics."""
        if not self.test_results:
            return {'message': 'No test results available'}
        
        total_tests = len(self.test_results)
        total_images = sum(test.get('total_images', 0) for test in self.test_results)
        
        # Calculate average metrics
        avg_accuracy = statistics.mean([test.get('average_accuracy', 0) for test in self.test_results])
        avg_confidence = statistics.mean([test.get('average_confidence', 0) for test in self.test_results])
        avg_processing_time = statistics.mean([test.get('average_processing_time', 0) for test in self.test_results])
        
        return {
            'total_test_runs': total_tests,
            'total_images_tested': total_images,
            'average_accuracy': avg_accuracy,
            'average_confidence': avg_confidence,
            'average_processing_time': avg_processing_time,
            'test_history': [
                {
                    'test_name': test.get('test_name', 'unknown'),
                    'timestamp': test.get('timestamp', 'unknown'),
                    'images_tested': test.get('total_images', 0),
                    'accuracy': test.get('average_accuracy', 0)
                }
                for test in self.test_results
            ]
        }
