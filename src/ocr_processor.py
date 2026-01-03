"""
OCR Processor Module

This module handles screenshot processing and OCR-based text extraction
for converting images containing questions and answers into structured data.
Enhanced with Phase 4.1 advanced OCR capabilities.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

# OCR imports (will be available after installing dependencies)
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None

# Import advanced OCR processor if available
try:
    from ocr import AdvancedOCRProcessor, OCRTester
    ADVANCED_OCR_AVAILABLE = True
except ImportError:
    ADVANCED_OCR_AVAILABLE = False
    AdvancedOCRProcessor = None
    OCRTester = None

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR processing and image preprocessing for question extraction."""
    
    def __init__(self, use_advanced_ocr: bool = True):
        """
        Initialize the OCR processor.
        
        Args:
            use_advanced_ocr: Whether to use advanced OCR features (Phase 4.1)
        """
        if not OCR_AVAILABLE:
            logger.warning("OCR dependencies not available. Install pytesseract and Pillow.")
        
        # OCR configuration
        self.ocr_config = '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?()[]{}:;"\' '
        self.confidence_threshold = 60
        self.use_advanced_ocr = use_advanced_ocr and ADVANCED_OCR_AVAILABLE
        
        # Initialize advanced OCR processor if available
        if self.use_advanced_ocr:
            try:
                self.advanced_processor = AdvancedOCRProcessor()
                self.ocr_tester = OCRTester()
                logger.info("Advanced OCR processor initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize advanced OCR: {e}")
                self.use_advanced_ocr = False
                self.advanced_processor = None
                self.ocr_tester = None
        else:
            self.advanced_processor = None
            self.ocr_tester = None
        
        logger.info("OCR processor initialized")
    
    def process_screenshot(self, image_path: str, 
                          preprocessing_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a screenshot to extract questions and answers.
        
        Args:
            image_path: Path to the image file
            preprocessing_options: Custom preprocessing options for advanced OCR
            
        Returns:
            Dictionary containing extracted text and processing results
        """
        if not OCR_AVAILABLE:
            raise RuntimeError("OCR dependencies not available")
        
        # Use advanced OCR if available
        if self.use_advanced_ocr and self.advanced_processor:
            try:
                result = self.advanced_processor.process_screenshot(image_path, preprocessing_options)
                
                # Convert advanced result to legacy format
                return {
                    'success': result['success'],
                    'error': result.get('error'),
                    'text': result['text'],
                    'confidence': result['confidence'],
                    'questions': result.get('parsed_questions', []),
                    'processing_time': result.get('processing_time', 0),
                    'image_quality': result.get('image_quality', {}),
                    'advanced_features': True
                }
            except Exception as e:
                logger.error(f"Advanced OCR failed, falling back to basic OCR: {e}")
                # Fall through to basic OCR
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            processed_image = self._preprocess_image(image)
            
            # Extract text using OCR
            extracted_text = self._extract_text_from_image(processed_image)
            
            # Parse questions from extracted text
            questions = self._parse_questions_from_text(extracted_text)
            
            result = {
                'success': True,
                'extracted_text': extracted_text,
                'questions': questions,
                'confidence': self._get_ocr_confidence(processed_image),
                'image_quality': self._assess_image_quality(image)
            }
            
            logger.info(f"Successfully processed image: {image_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'extracted_text': '',
                'questions': []
            }
    
    def _preprocess_image(self, image) -> Any:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Original PIL Image
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply noise reduction
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        # Resize if too small (minimum 300 DPI equivalent)
        width, height = image.size
        if width < 1200 or height < 800:  # Rough 300 DPI equivalent
            scale_factor = max(1200 / width, 800 / height)
            new_size = (int(width * scale_factor), int(height * scale_factor))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def _extract_text_from_image(self, image) -> str:
        """
        Extract text from preprocessed image using OCR.
        
        Args:
            image: Preprocessed PIL Image
            
        Returns:
            Extracted text string
        """
        try:
            # Extract text with confidence data
            data = pytesseract.image_to_data(image, config=self.ocr_config, output_type=pytesseract.Output.DICT)
            
            # Filter text by confidence
            extracted_text = ""
            for i, conf in enumerate(data['conf']):
                if int(conf) >= self.confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        extracted_text += text + " "
            
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            return ""
    
    def _parse_questions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse questions and answers from extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            List of parsed question dictionaries
        """
        questions = []
        
        # Simple parsing patterns (can be enhanced)
        question_patterns = [
            r'(\d+\.\s*[^?]+\?)',  # Numbered questions ending with ?
            r'([A-Z][^?]+\?)',     # Questions starting with capital letter
        ]
        
        for pattern in question_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                question_text = match.group(1).strip()
                
                # Look for answer options after the question
                answer_section = self._extract_answer_section(text, match.end())
                if answer_section:
                    answers = self._parse_answer_options(answer_section)
                    if answers:
                        question = {
                            'question_text': question_text,
                            'question_type': 'multiple_choice',
                            'answers': answers,
                            'tags': ['ocr-imported'],
                            'source': 'ocr'
                        }
                        questions.append(question)
        
        logger.info(f"Parsed {len(questions)} questions from OCR text")
        return questions
    
    def _extract_answer_section(self, text: str, start_pos: int) -> str:
        """Extract the answer section following a question."""
        # Look for common answer patterns
        answer_patterns = [
            r'([A-E]\.\s*[^\n]+(?:\n[A-E]\.\s*[^\n]+)*)',  # A. B. C. format
            r'([1-5]\.\s*[^\n]+(?:\n[1-5]\.\s*[^\n]+)*)',  # 1. 2. 3. format
        ]
        
        remaining_text = text[start_pos:start_pos + 500]  # Look ahead 500 chars
        
        for pattern in answer_patterns:
            match = re.search(pattern, remaining_text, re.MULTILINE)
            if match:
                return match.group(1)
        
        return ""
    
    def _parse_answer_options(self, answer_section: str) -> List[Dict[str, Any]]:
        """Parse individual answer options from answer section."""
        answers = []
        
        # Split by answer markers
        answer_lines = re.split(r'[A-E]\.\s*|[1-5]\.\s*', answer_section)
        answer_lines = [line.strip() for line in answer_lines if line.strip()]
        
        for i, answer_text in enumerate(answer_lines[:6]):  # Max 6 options
            if answer_text:
                answer = {
                    'id': f'answer_{i+1}',
                    'text': answer_text,
                    'is_correct': False  # Will need manual correction
                }
                answers.append(answer)
        
        return answers
    
    def _get_ocr_confidence(self, image) -> float:
        """Get average OCR confidence for the image."""
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            return sum(confidences) / len(confidences) if confidences else 0.0
        except:
            return 0.0
    
    def _assess_image_quality(self, image) -> str:
        """Assess the quality of the input image."""
        width, height = image.size
        
        # Check resolution
        if width < 800 or height < 600:
            return "low"
        elif width < 1200 or height < 800:
            return "medium"
        else:
            return "high"
    
    def validate_image_format(self, image_path: str) -> bool:
        """Validate that the image is in a supported format."""
        supported_formats = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        file_ext = Path(image_path).suffix.lower()
        return file_ext in supported_formats
    
    def batch_process_images(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple images in batch.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of processing results for each image
        """
        results = []
        
        for i, image_path in enumerate(image_paths):
            logger.info(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
            result = self.process_screenshot(image_path)
            result['image_path'] = image_path
            results.append(result)
        
        return results
    
    def batch_process_images_advanced(self, image_paths: List[str], 
                                    preprocessing_options: Dict[str, Any] = None,
                                    progress_callback: callable = None) -> Dict[str, Any]:
        """
        Process multiple images using advanced OCR with progress tracking.
        
        Args:
            image_paths: List of image file paths
            preprocessing_options: Custom preprocessing options
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary containing batch processing results
        """
        if self.use_advanced_ocr and self.advanced_processor:
            return self.advanced_processor.batch_process_images(
                image_paths, preprocessing_options, progress_callback
            )
        else:
            # Fall back to basic batch processing
            results = []
            for i, image_path in enumerate(image_paths):
                try:
                    result = self.process_screenshot(image_path)
                    results.append({
                        'image_path': image_path,
                        'result': result
                    })
                    
                    if progress_callback:
                        progress = (i + 1) / len(image_paths) * 100
                        progress_callback(progress, f"Processed {i + 1}/{len(image_paths)} images")
                        
                except Exception as e:
                    results.append({
                        'image_path': image_path,
                        'result': {
                            'success': False,
                            'error': str(e),
                            'text': '',
                            'confidence': 0
                        }
                    })
            
            return {
                'success': True,
                'results': results,
                'summary': {
                    'total_images': len(image_paths),
                    'successful': len([r for r in results if r['result']['success']]),
                    'failed': len([r for r in results if not r['result']['success']])
                }
            }
    
    def test_ocr_accuracy(self, test_images: List[str], 
                         expected_results: List[str] = None) -> Dict[str, Any]:
        """
        Test OCR accuracy with test images.
        
        Args:
            test_images: List of test image paths
            expected_results: List of expected text results
            
        Returns:
            Dictionary containing accuracy test results
        """
        if self.use_advanced_ocr and self.ocr_tester:
            return self.ocr_tester.run_accuracy_test(test_images, expected_results)
        else:
            # Basic accuracy test
            results = []
            total_accuracy = 0
            
            for i, image_path in enumerate(test_images):
                try:
                    result = self.process_screenshot(image_path)
                    accuracy = 0
                    
                    if expected_results and i < len(expected_results):
                        # Simple accuracy calculation
                        expected = expected_results[i].lower().strip()
                        actual = result['text'].lower().strip()
                        if expected == actual:
                            accuracy = 100
                        else:
                            # Word-based similarity
                            expected_words = set(expected.split())
                            actual_words = set(actual.split())
                            if expected_words:
                                common = expected_words & actual_words
                                accuracy = (len(common) / len(expected_words)) * 100
                    
                    results.append({
                        'image_path': image_path,
                        'accuracy': accuracy,
                        'confidence': result['confidence'],
                        'success': result['success']
                    })
                    
                    total_accuracy += accuracy
                    
                except Exception as e:
                    results.append({
                        'image_path': image_path,
                        'accuracy': 0,
                        'confidence': 0,
                        'success': False,
                        'error': str(e)
                    })
            
            average_accuracy = total_accuracy / len(test_images) if test_images else 0
            
            return {
                'test_images': len(test_images),
                'average_accuracy': average_accuracy,
                'results': results
            }
    
    def run_performance_benchmark(self, test_images: List[str], 
                                 iterations: int = 3) -> Dict[str, Any]:
        """
        Run performance benchmark on OCR processing.
        
        Args:
            test_images: List of test image paths
            iterations: Number of iterations to run
            
        Returns:
            Dictionary containing benchmark results
        """
        if self.use_advanced_ocr and self.ocr_tester:
            return self.ocr_tester.run_performance_benchmark(test_images, iterations)
        else:
            # Basic performance test
            import time
            
            benchmark_results = []
            
            for iteration in range(iterations):
                start_time = time.time()
                
                for image_path in test_images:
                    try:
                        self.process_screenshot(image_path)
                    except Exception as e:
                        logger.error(f"Error in benchmark iteration {iteration + 1}: {e}")
                
                iteration_time = time.time() - start_time
                benchmark_results.append({
                    'iteration': iteration + 1,
                    'total_time': iteration_time,
                    'average_processing_time': iteration_time / len(test_images)
                })
            
            return {
                'iterations': iterations,
                'total_images': len(test_images),
                'results': benchmark_results
            }
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get OCR processing statistics."""
        if self.use_advanced_ocr and self.advanced_processor:
            return self.advanced_processor.get_processing_statistics()
        else:
            return {
                'total_images': 0,
                'successful_extractions': 0,
                'failed_extractions': 0,
                'average_confidence': 0.0,
                'average_processing_time': 0.0
            }
    
    def clear_ocr_cache(self) -> None:
        """Clear OCR result cache."""
        if self.use_advanced_ocr and self.advanced_processor:
            self.advanced_processor.clear_cache()
        else:
            logger.info("No cache to clear for basic OCR")
    
    def export_test_results(self, output_file: str = None) -> str:
        """Export OCR test results."""
        if self.use_advanced_ocr and self.ocr_tester:
            return self.ocr_tester.export_test_results(output_file)
        else:
            logger.warning("Test result export not available for basic OCR")
            return ""
