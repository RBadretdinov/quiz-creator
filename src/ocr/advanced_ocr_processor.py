"""
Advanced OCR Processor Module

This module provides comprehensive OCR processing capabilities with advanced
image preprocessing, intelligent text parsing, and batch processing features.
"""

import os
import logging
import json
import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple, Union
from pathlib import Path
import re
from datetime import datetime
import statistics

# Advanced image processing imports
try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw
    import cv2
    import numpy as np
    from skimage import filters, transform, exposure
    from skimage.morphology import disk
    from skimage.filters import rank
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    Image = None
    cv2 = None
    np = None

logger = logging.getLogger(__name__)

class AdvancedOCRProcessor:
    """Advanced OCR processor with comprehensive image preprocessing and intelligent parsing."""
    
    def __init__(self, cache_dir: str = "data/ocr_cache"):
        """
        Initialize the advanced OCR processor.
        
        Args:
            cache_dir: Directory for caching OCR results
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if not OCR_AVAILABLE:
            logger.warning("Advanced OCR dependencies not available. Install pytesseract, Pillow, opencv-python, and scikit-image.")
        
        # OCR configuration
        self.ocr_configs = {
            'default': '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?()[]{}:;"\' ',
            'single_line': '--psm 7',
            'single_word': '--psm 8',
            'single_char': '--psm 10',
            'sparse_text': '--psm 11',
            'osd': '--psm 0'
        }
        
        self.confidence_threshold = 60
        self.min_image_size = (100, 100)
        self.max_image_size = (4000, 4000)
        self.target_dpi = 300
        
        # Performance tracking
        self.processing_stats = {
            'total_images': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'average_confidence': 0.0,
            'average_processing_time': 0.0
        }
        
        logger.info("Advanced OCR processor initialized")
    
    def process_screenshot(self, image_path: str, 
                          preprocessing_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a screenshot with advanced preprocessing and OCR extraction.
        
        Args:
            image_path: Path to the image file
            preprocessing_options: Custom preprocessing options
            
        Returns:
            Dictionary containing extracted text and processing results
        """
        if not OCR_AVAILABLE:
            return {
                'success': False,
                'error': 'OCR dependencies not available',
                'text': '',
                'confidence': 0,
                'processing_time': 0
            }
        
        start_time = time.time()
        
        try:
            # Load and validate image
            image = self._load_image(image_path)
            if not image:
                return {
                    'success': False,
                    'error': 'Failed to load image',
                    'text': '',
                    'confidence': 0,
                    'processing_time': time.time() - start_time
                }
            
            # Check cache first
            cache_key = self._generate_cache_key(image_path, preprocessing_options)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.info(f"Using cached OCR result for {image_path}")
                return cached_result
            
            # Preprocess image
            preprocessed_image = self._preprocess_image(image, preprocessing_options)
            
            # Extract text with multiple OCR configurations
            ocr_results = self._extract_text_multiple_configs(preprocessed_image)
            
            # Select best result
            best_result = self._select_best_ocr_result(ocr_results)
            
            # Parse questions from text
            parsed_questions = self._parse_questions_from_text(best_result['text'])
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Prepare result
            result = {
                'success': best_result['confidence'] >= self.confidence_threshold,
                'text': best_result['text'],
                'confidence': best_result['confidence'],
                'processing_time': processing_time,
                'parsed_questions': parsed_questions,
                'image_quality': self._assess_image_quality(image),
                'preprocessing_applied': preprocessing_options or {},
                'ocr_config_used': best_result['config'],
                'error': None if best_result['confidence'] >= self.confidence_threshold else 'Low confidence OCR result'
            }
            
            # Cache result
            self._cache_result(cache_key, result)
            
            # Update statistics
            self._update_statistics(result)
            
            logger.info(f"OCR processing completed for {image_path} in {processing_time:.2f}s with confidence {best_result['confidence']:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0,
                'processing_time': time.time() - start_time
            }
    
    def batch_process_images(self, image_paths: List[str], 
                             preprocessing_options: Dict[str, Any] = None,
                             progress_callback: callable = None) -> Dict[str, Any]:
        """
        Process multiple images in batch with progress tracking.
        
        Args:
            image_paths: List of image file paths
            preprocessing_options: Custom preprocessing options
            progress_callback: Callback function for progress updates
            
        Returns:
            Dictionary containing batch processing results
        """
        if not OCR_AVAILABLE:
            return {
                'success': False,
                'error': 'OCR dependencies not available',
                'results': [],
                'summary': {}
            }
        
        start_time = time.time()
        results = []
        successful = 0
        failed = 0
        total_confidence = 0
        
        logger.info(f"Starting batch processing of {len(image_paths)} images")
        
        for i, image_path in enumerate(image_paths):
            try:
                # Process individual image
                result = self.process_screenshot(image_path, preprocessing_options)
                results.append({
                    'image_path': image_path,
                    'result': result
                })
                
                if result['success']:
                    successful += 1
                    total_confidence += result['confidence']
                else:
                    failed += 1
                
                # Update progress
                if progress_callback:
                    progress = (i + 1) / len(image_paths) * 100
                    progress_callback(progress, f"Processed {i + 1}/{len(image_paths)} images")
                
                logger.info(f"Processed {i + 1}/{len(image_paths)}: {image_path}")
                
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                results.append({
                    'image_path': image_path,
                    'result': {
                        'success': False,
                        'error': str(e),
                        'text': '',
                        'confidence': 0
                    }
                })
                failed += 1
        
        # Calculate summary statistics
        total_time = time.time() - start_time
        average_confidence = total_confidence / max(successful, 1)
        
        summary = {
            'total_images': len(image_paths),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(image_paths)) * 100,
            'average_confidence': average_confidence,
            'total_processing_time': total_time,
            'average_processing_time': total_time / len(image_paths)
        }
        
        logger.info(f"Batch processing completed: {successful}/{len(image_paths)} successful ({summary['success_rate']:.1f}%)")
        
        return {
            'success': failed == 0,
            'results': results,
            'summary': summary,
            'error': None if failed == 0 else f"{failed} images failed to process"
        }
    
    def _load_image(self, image_path: str) -> Optional[Any]:
        """Load and validate image file."""
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            image = Image.open(image_path)
            
            # Validate image size
            if image.size[0] < self.min_image_size[0] or image.size[1] < self.min_image_size[1]:
                logger.warning(f"Image too small: {image.size}")
                return None
            
            if image.size[0] > self.max_image_size[0] or image.size[1] > self.max_image_size[1]:
                logger.warning(f"Image too large: {image.size}")
                return None
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            logger.debug(f"Loaded image: {image.size}, mode: {image.mode}")
            return image
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            return None
    
    def _preprocess_image(self, image: Any, 
                         options: Dict[str, Any] = None) -> Any:
        """
        Apply comprehensive image preprocessing for better OCR accuracy.
        
        Args:
            image: PIL Image object
            options: Preprocessing options
            
        Returns:
            Preprocessed PIL Image object
        """
        if not options:
            options = {}
        
        try:
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # 1. Resize to optimal DPI (300 DPI)
            if options.get('resize_to_dpi', True):
                img_array = self._resize_to_dpi(img_array)
            
            # 2. Noise reduction
            if options.get('noise_reduction', True):
                img_array = self._reduce_noise(img_array)
            
            # 3. Contrast enhancement
            if options.get('contrast_enhancement', True):
                img_array = self._enhance_contrast(img_array)
            
            # 4. Skew correction
            if options.get('skew_correction', True):
                img_array = self._correct_skew(img_array)
            
            # 5. Text enhancement
            if options.get('text_enhancement', True):
                img_array = self._enhance_text(img_array)
            
            # 6. Adaptive thresholding
            if options.get('adaptive_threshold', True):
                img_array = self._apply_adaptive_threshold(img_array)
            
            # Convert back to PIL Image
            preprocessed_image = Image.fromarray(img_array)
            
            logger.debug("Image preprocessing completed")
            return preprocessed_image
            
        except Exception as e:
            logger.error(f"Error in image preprocessing: {e}")
            return image
    
    def _resize_to_dpi(self, img_array: Any) -> Any:
        """Resize image to target DPI (300 DPI)."""
        try:
            height, width = img_array.shape[:2]
            # Calculate new dimensions for 300 DPI
            # Assuming original image is at 72 DPI
            scale_factor = 300 / 72
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            resized = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            return resized
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return img_array
    
    def _reduce_noise(self, img_array: Any) -> Any:
        """Apply noise reduction using Gaussian blur and median filtering."""
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # Apply median filter
            denoised = cv2.medianBlur(blurred, 3)
            
            return denoised
        except Exception as e:
            logger.error(f"Error reducing noise: {e}")
            return img_array
    
    def _enhance_contrast(self, img_array: Any) -> Any:
        """Enhance contrast using histogram equalization."""
        try:
            if len(img_array.shape) == 3:
                # Convert to LAB color space
                lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
                l, a, b = cv2.split(lab)
                
                # Apply CLAHE to L channel
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                l = clahe.apply(l)
                
                # Merge channels and convert back
                enhanced = cv2.merge([l, a, b])
                enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
                return enhanced
            else:
                # Apply CLAHE to grayscale
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(img_array)
                return enhanced
        except Exception as e:
            logger.error(f"Error enhancing contrast: {e}")
            return img_array
    
    def _correct_skew(self, img_array: Any) -> Any:
        """Correct image skew using Hough line detection."""
        try:
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Detect lines
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # Calculate average angle
                angles = []
                for line in lines:
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi
                    if 45 < angle < 135:  # Horizontal lines
                        angles.append(angle - 90)
                
                if angles:
                    # Calculate median angle
                    median_angle = statistics.median(angles)
                    
                    # Rotate image to correct skew
                    if abs(median_angle) > 0.5:  # Only correct if skew is significant
                        height, width = img_array.shape[:2]
                        center = (width // 2, height // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                        corrected = cv2.warpAffine(img_array, rotation_matrix, (width, height))
                        return corrected
            
            return img_array
        except Exception as e:
            logger.error(f"Error correcting skew: {e}")
            return img_array
    
    def _enhance_text(self, img_array: Any) -> Any:
        """Enhance text using morphological operations."""
        try:
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply morphological operations to enhance text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            
            # Closing operation to connect text
            closed = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            
            # Opening operation to remove noise
            opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)
            
            return opened
        except Exception as e:
            logger.error(f"Error enhancing text: {e}")
            return img_array
    
    def _apply_adaptive_threshold(self, img_array: Any) -> Any:
        """Apply adaptive thresholding for better text extraction."""
        try:
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply adaptive threshold
            thresholded = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return thresholded
        except Exception as e:
            logger.error(f"Error applying adaptive threshold: {e}")
            return img_array
    
    def _extract_text_multiple_configs(self, image: Any) -> List[Dict[str, Any]]:
        """Extract text using multiple OCR configurations and return all results."""
        results = []
        
        for config_name, config in self.ocr_configs.items():
            try:
                # Extract text with confidence
                data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                
                # Calculate average confidence
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = statistics.mean(confidences) if confidences else 0
                
                # Extract text
                text = pytesseract.image_to_string(image, config=config).strip()
                
                results.append({
                    'config': config_name,
                    'text': text,
                    'confidence': avg_confidence,
                    'word_count': len(text.split()),
                    'data': data
                })
                
            except Exception as e:
                logger.error(f"Error with OCR config {config_name}: {e}")
                results.append({
                    'config': config_name,
                    'text': '',
                    'confidence': 0,
                    'word_count': 0,
                    'data': {}
                })
        
        return results
    
    def _select_best_ocr_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Select the best OCR result based on confidence and text quality."""
        if not results:
            return {'config': 'none', 'text': '', 'confidence': 0}
        
        # Filter results with minimum confidence
        valid_results = [r for r in results if r['confidence'] >= 30]
        
        if not valid_results:
            # Return the result with highest confidence even if below threshold
            return max(results, key=lambda x: x['confidence'])
        
        # Score results based on confidence and text quality
        scored_results = []
        for result in valid_results:
            score = result['confidence']
            
            # Bonus for longer text (but not too long)
            word_count = result['word_count']
            if 5 <= word_count <= 100:
                score += 10
            
            # Bonus for common question patterns
            text = result['text'].lower()
            if any(pattern in text for pattern in ['what', 'which', 'how', 'when', 'where', 'why']):
                score += 5
            
            scored_results.append((score, result))
        
        # Return the highest scoring result
        best_score, best_result = max(scored_results, key=lambda x: x[0])
        return best_result
    
    def _parse_questions_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse questions and answers from extracted text."""
        if not text.strip():
            return []
        
        questions = []
        lines = text.split('\n')
        current_question = None
        current_answers = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line looks like a question
            if self._is_question_line(line):
                # Save previous question if exists
                if current_question:
                    questions.append({
                        'question_text': current_question,
                        'answers': current_answers,
                        'question_type': self._determine_question_type(current_answers)
                    })
                
                # Start new question
                current_question = line
                current_answers = []
            
            # Check if line looks like an answer
            elif self._is_answer_line(line):
                current_answers.append({
                    'text': line,
                    'is_correct': self._is_correct_answer(line)
                })
        
        # Add last question
        if current_question:
            questions.append({
                'question_text': current_question,
                'answers': current_answers,
                'question_type': self._determine_question_type(current_answers)
            })
        
        return questions
    
    def _is_question_line(self, line: str) -> bool:
        """Determine if a line is likely a question."""
        # Check for question patterns
        question_patterns = [
            r'^\d+[\.\)]\s+',  # Numbered questions
            r'^[A-Z][^?]*\?',  # Questions ending with ?
            r'^(What|Which|How|When|Where|Why|Who)',  # Question words
            r'^[A-Z][^.]*\.$'  # Statements that might be questions
        ]
        
        for pattern in question_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _is_answer_line(self, line: str) -> bool:
        """Determine if a line is likely an answer."""
        # Check for answer patterns
        answer_patterns = [
            r'^[A-Z][a-z]',  # Starts with capital letter
            r'^\d+[\.\)]\s+',  # Numbered answers
            r'^[A-D][\.\)]\s+',  # Lettered answers
            r'^(True|False|Yes|No)$',  # Boolean answers
        ]
        
        for pattern in answer_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _is_correct_answer(self, line: str) -> bool:
        """Determine if an answer is likely correct."""
        # Look for indicators of correct answers
        correct_indicators = [
            r'\*',  # Asterisk
            r'✓',  # Checkmark
            r'\(correct\)',  # (correct)
            r'\[x\]',  # Checked box
        ]
        
        for pattern in correct_indicators:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _determine_question_type(self, answers: List[Dict[str, Any]]) -> str:
        """Determine the question type based on answers."""
        if not answers:
            return 'multiple_choice'
        
        # Check for True/False
        if len(answers) == 2:
            answer_texts = [ans['text'].lower() for ans in answers]
            if any(text in ['true', 'false', 'yes', 'no', 't', 'f'] for text in answer_texts):
                return 'true_false'
        
        # Check for multiple choice
        if len(answers) >= 2:
            return 'multiple_choice'
        
        return 'multiple_choice'
    
    def _assess_image_quality(self, image: Any) -> Dict[str, Any]:
        """Assess the quality of an image for OCR processing."""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Calculate quality metrics
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Calculate sharpness (Laplacian variance)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate contrast (standard deviation)
            contrast = np.std(gray)
            
            # Calculate brightness (mean)
            brightness = np.mean(gray)
            
            # Assess overall quality
            quality_score = 0
            if sharpness > 100:
                quality_score += 25
            if contrast > 50:
                quality_score += 25
            if 100 < brightness < 200:
                quality_score += 25
            if image.size[0] > 500 and image.size[1] > 500:
                quality_score += 25
            
            return {
                'sharpness': float(sharpness),
                'contrast': float(contrast),
                'brightness': float(brightness),
                'quality_score': quality_score,
                'size': image.size,
                'recommendations': self._get_quality_recommendations(quality_score, sharpness, contrast, brightness)
            }
            
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return {
                'sharpness': 0,
                'contrast': 0,
                'brightness': 0,
                'quality_score': 0,
                'size': image.size,
                'recommendations': ['Unable to assess image quality']
            }
    
    def _get_quality_recommendations(self, quality_score: int, sharpness: float, 
                                   contrast: float, brightness: float) -> List[str]:
        """Get recommendations for improving image quality."""
        recommendations = []
        
        if quality_score < 50:
            recommendations.append("Image quality is poor - consider retaking the screenshot")
        
        if sharpness < 100:
            recommendations.append("Image is blurry - ensure camera is focused")
        
        if contrast < 50:
            recommendations.append("Image has low contrast - improve lighting")
        
        if brightness < 100:
            recommendations.append("Image is too dark - increase lighting")
        elif brightness > 200:
            recommendations.append("Image is too bright - reduce lighting")
        
        return recommendations
    
    def _generate_cache_key(self, image_path: str, options: Dict[str, Any] = None) -> str:
        """Generate cache key for image and options."""
        # Create hash of image path and options
        content = f"{image_path}_{json.dumps(options or {}, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached OCR result."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading cached result: {e}")
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """Cache OCR result."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error caching result: {e}")
    
    def _update_statistics(self, result: Dict[str, Any]) -> None:
        """Update processing statistics."""
        self.processing_stats['total_images'] += 1
        
        if result['success']:
            self.processing_stats['successful_extractions'] += 1
        else:
            self.processing_stats['failed_extractions'] += 1
        
        # Update average confidence
        total_conf = (self.processing_stats['average_confidence'] * 
                     (self.processing_stats['total_images'] - 1) + result['confidence'])
        self.processing_stats['average_confidence'] = total_conf / self.processing_stats['total_images']
        
        # Update average processing time
        total_time = (self.processing_stats['average_processing_time'] * 
                     (self.processing_stats['total_images'] - 1) + result['processing_time'])
        self.processing_stats['average_processing_time'] = total_time / self.processing_stats['total_images']
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return self.processing_stats.copy()
    
    def clear_cache(self) -> None:
        """Clear OCR result cache."""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("OCR cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def test_ocr_accuracy(self, test_images: List[str], 
                          expected_results: List[str] = None) -> Dict[str, Any]:
        """Test OCR accuracy with test images."""
        if not test_images:
            return {'error': 'No test images provided'}
        
        results = []
        total_accuracy = 0
        
        for i, image_path in enumerate(test_images):
            result = self.process_screenshot(image_path)
            
            if expected_results and i < len(expected_results):
                # Calculate accuracy against expected result
                expected = expected_results[i].lower().strip()
                actual = result['text'].lower().strip()
                
                # Simple accuracy calculation (can be improved with more sophisticated methods)
                if expected == actual:
                    accuracy = 100
                else:
                    # Calculate similarity
                    common_words = set(expected.split()) & set(actual.split())
                    total_words = set(expected.split()) | set(actual.split())
                    accuracy = (len(common_words) / len(total_words)) * 100 if total_words else 0
                
                results.append({
                    'image_path': image_path,
                    'expected': expected,
                    'actual': actual,
                    'accuracy': accuracy,
                    'confidence': result['confidence']
                })
                
                total_accuracy += accuracy
        
        average_accuracy = total_accuracy / len(test_images) if test_images else 0
        
        return {
            'test_images': len(test_images),
            'average_accuracy': average_accuracy,
            'results': results,
            'summary': {
                'high_accuracy': len([r for r in results if r['accuracy'] >= 90]),
                'medium_accuracy': len([r for r in results if 70 <= r['accuracy'] < 90]),
                'low_accuracy': len([r for r in results if r['accuracy'] < 70])
            }
        }
