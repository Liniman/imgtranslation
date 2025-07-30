"""
OCR Engine with confidence filtering and text validation.
"""

import easyocr
import numpy as np
from PIL import Image
from typing import List, Tuple, Optional
import re
import logging

logger = logging.getLogger(__name__)


class OCREngine:
    """Enhanced OCR engine with confidence filtering and validation."""
    
    def __init__(self, languages: List[str] = None, min_confidence: float = 0.6):
        """
        Initialize OCR engine.
        
        Args:
            languages: List of language codes for OCR
            min_confidence: Minimum confidence threshold for text detection
        """
        if languages is None:
            languages = ['en']  # Start with English only, can be expanded
        
        self.languages = languages
        self.min_confidence = min_confidence
        self.reader = None
        self._initialize_reader()
    
    def _initialize_reader(self):
        """Initialize EasyOCR reader with error handling."""
        try:
            logger.info(f"Initializing OCR reader with languages: {self.languages}")
            self.reader = easyocr.Reader(self.languages)
            logger.info("OCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OCR reader: {e}")
            raise
    
    def detect_text(self, image: Image.Image) -> List[Tuple]:
        """
        Detect text in image with confidence filtering.
        
        Args:
            image: PIL Image object
            
        Returns:
            List of (bbox, text, confidence) tuples for valid detections
        """
        if self.reader is None:
            raise RuntimeError("OCR reader not initialized")
        
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        try:
            # Run OCR detection
            logger.info("Starting text detection...")
            raw_results = self.reader.readtext(img_array)
            logger.info(f"Raw OCR detected {len(raw_results)} text regions")
            
            # Filter and validate results
            filtered_results = self._filter_ocr_results(raw_results)
            logger.info(f"After filtering: {len(filtered_results)} valid text regions")
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"OCR detection failed: {e}")
            raise
    
    def _filter_ocr_results(self, ocr_results: List[Tuple]) -> List[Tuple]:
        """
        Filter OCR results based on confidence and text validation.
        
        Args:
            ocr_results: Raw OCR results from EasyOCR
            
        Returns:
            Filtered list of valid text detections
        """
        filtered = []
        
        for bbox, text, confidence in ocr_results:
            # Skip low confidence detections
            if confidence < self.min_confidence:
                logger.debug(f"Skipping low confidence text: '{text}' (conf: {confidence:.2f})")
                continue
            
            # Validate text content
            if not self._is_valid_text(text):
                logger.debug(f"Skipping invalid text: '{text}'")
                continue
            
            # Validate bounding box
            if not self._is_valid_bbox(bbox):
                logger.debug(f"Skipping invalid bbox for text: '{text}'")
                continue
            
            filtered.append((bbox, text.strip(), confidence))
        
        return filtered
    
    def _is_valid_text(self, text: str) -> bool:
        """
        Validate if detected text is meaningful.
        
        Args:
            text: Detected text string
            
        Returns:
            True if text appears valid, False otherwise
        """
        # Remove whitespace
        text = text.strip()
        
        # Check minimum length
        if len(text) < 2:
            return False
        
        # Check if text is too long (likely OCR error)
        if len(text) > 200:
            return False
        
        # Calculate ratio of special characters
        special_chars = sum(1 for c in text if not (c.isalnum() or c.isspace() or c in '.,!?;:()[]{}"\'-'))
        special_ratio = special_chars / len(text) if len(text) > 0 else 0
        
        # Reject if too many special characters (likely OCR noise)
        if special_ratio > 0.5:
            return False
        
        # Check for common OCR error patterns
        error_patterns = [
            r'^[^a-zA-Z0-9\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]+$',  # Only special chars
            r'^[|\\\/\-_=+~`]+$',  # Common OCR line errors
            r'^\.+$',  # Only dots
            r'^,+$',  # Only commas
        ]
        
        for pattern in error_patterns:
            if re.match(pattern, text):
                return False
        
        return True
    
    def _is_valid_bbox(self, bbox: List[List[float]]) -> bool:
        """
        Validate bounding box dimensions.
        
        Args:
            bbox: List of [x, y] coordinate pairs
            
        Returns:
            True if bbox is valid, False otherwise
        """
        try:
            points = np.array(bbox)
            
            # Check if we have 4 points
            if points.shape != (4, 2):
                return False
            
            # Calculate dimensions
            x_min, y_min = points.min(axis=0)
            x_max, y_max = points.max(axis=0)
            
            width = x_max - x_min
            height = y_max - y_min
            
            # Check minimum dimensions (text should be at least 10x10 pixels)
            if width < 10 or height < 10:
                return False
            
            # Check maximum dimensions (reject extremely large regions)
            if width > 2000 or height > 500:
                return False
            
            # Check aspect ratio (reject extremely wide or tall regions)
            aspect_ratio = max(width, height) / min(width, height)
            if aspect_ratio > 20:
                return False
            
            return True
            
        except Exception:
            return False
    
    def set_confidence_threshold(self, min_confidence: float):
        """
        Update minimum confidence threshold.
        
        Args:
            min_confidence: New minimum confidence (0.0 to 1.0)
        """
        if 0.0 <= min_confidence <= 1.0:
            self.min_confidence = min_confidence
            logger.info(f"Updated confidence threshold to {min_confidence}")
        else:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
    
    def get_text_regions(self, image: Image.Image, padding: int = 5) -> List[dict]:
        """
        Get detailed information about detected text regions.
        
        Args:
            image: PIL Image object
            padding: Padding to add around text regions
            
        Returns:
            List of text region dictionaries with bbox, text, confidence, etc.
        """
        detections = self.detect_text(image)
        regions = []
        
        for bbox, text, confidence in detections:
            points = np.array(bbox)
            x_min, y_min = points.min(axis=0)
            x_max, y_max = points.max(axis=0)
            
            # Add padding
            x_min = max(0, int(x_min - padding))
            y_min = max(0, int(y_min - padding))
            x_max = min(image.width, int(x_max + padding))
            y_max = min(image.height, int(y_max + padding))
            
            region = {
                'bbox_points': bbox,
                'bbox_rect': (x_min, y_min, x_max - x_min, y_max - y_min),
                'text': text,
                'confidence': confidence,
                'center': ((x_min + x_max) // 2, (y_min + y_max) // 2),
                'area': (x_max - x_min) * (y_max - y_min)
            }
            
            regions.append(region)
        
        # Sort by area (largest first) for processing priority
        regions.sort(key=lambda r: r['area'], reverse=True)
        
        return regions