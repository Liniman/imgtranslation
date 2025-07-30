"""
Utility functions for image translation.
"""

from PIL import Image
import numpy as np
from typing import Tuple, List, Optional


def validate_image(image: Image.Image) -> Tuple[bool, str]:
    """
    Validate if image is suitable for text detection.
    
    Args:
        image: PIL Image object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if image is None:
        return False, "Image is None"
    
    # Check image dimensions
    width, height = image.size
    if width < 50 or height < 50:
        return False, "Image too small (minimum 50x50 pixels)"
    
    if width > 4096 or height > 4096:
        return False, "Image too large (maximum 4096x4096 pixels)"
    
    # Check if image has reasonable aspect ratio
    aspect_ratio = max(width, height) / min(width, height)
    if aspect_ratio > 10:
        return False, "Image aspect ratio too extreme"
    
    # Check if image has content (not just blank)
    img_array = np.array(image.convert('L'))  # Convert to grayscale
    if np.std(img_array) < 10:  # Very low variance = likely blank
        return False, "Image appears to be blank or has very low contrast"
    
    return True, "Valid image"


def get_supported_languages():
    """
    Get list of supported languages for OCR and translation.
    
    Returns:
        Dict with OCR and translation language mappings
    """
    ocr_languages = {
        'ch_sim': 'Chinese (Simplified)',
        'en': 'English',
        'es': 'Spanish', 
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'hi': 'Hindi'
    }
    
    translation_languages = {
        'es': 'Spanish',
        'fr': 'French', 
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'hi': 'Hindi',
        'en': 'English',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'pl': 'Polish',
        'cs': 'Czech',
        'hu': 'Hungarian',
        'tr': 'Turkish',
        'th': 'Thai',
        'vi': 'Vietnamese'
    }
    
    return {
        'ocr': ocr_languages,
        'translation': translation_languages
    }


def estimate_text_properties(text_region: np.ndarray) -> dict:
    """
    Estimate text properties from image region.
    
    Args:
        text_region: Numpy array of text region
        
    Returns:
        Dict with estimated properties (is_bold, is_italic, etc.)
    """
    import cv2
    
    if len(text_region.shape) == 3:
        gray = cv2.cvtColor(text_region, cv2.COLOR_BGR2GRAY)
    else:
        gray = text_region
    
    # Threshold to binary
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Estimate stroke width using morphological operations
    kernel = np.ones((2, 2), np.uint8)
    eroded = cv2.erode(binary, kernel, iterations=1)
    stroke_width = np.sum(binary) - np.sum(eroded)
    
    # Calculate relative stroke width
    total_pixels = binary.shape[0] * binary.shape[1]
    stroke_ratio = stroke_width / total_pixels if total_pixels > 0 else 0
    
    # Simple heuristics for text properties
    is_bold = stroke_ratio > 0.1
    
    # Estimate if text is italic (simple approach - check slant)
    # This is a simplified approach and may not be very accurate
    is_italic = False  # TODO: Implement slant detection
    
    return {
        'is_bold': is_bold,
        'is_italic': is_italic,
        'stroke_ratio': stroke_ratio
    }


def resize_image_if_needed(image: Image.Image, max_dimension: int = 2048) -> Image.Image:
    """
    Resize image if it's too large for processing.
    
    Args:
        image: PIL Image object
        max_dimension: Maximum width or height
        
    Returns:
        Resized image if needed, original otherwise
    """
    width, height = image.size
    
    if width <= max_dimension and height <= max_dimension:
        return image
    
    # Calculate new dimensions maintaining aspect ratio
    if width > height:
        new_width = max_dimension
        new_height = int(height * (max_dimension / width))
    else:
        new_height = max_dimension
        new_width = int(width * (max_dimension / height))
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def calculate_text_bbox(bbox_points: List[List[float]]) -> Tuple[int, int, int, int]:
    """
    Calculate bounding box from OCR points.
    
    Args:
        bbox_points: List of [x, y] coordinate pairs
        
    Returns:
        Tuple of (x, y, width, height)
    """
    points = np.array(bbox_points)
    x_min, y_min = points.min(axis=0)
    x_max, y_max = points.max(axis=0)
    
    return int(x_min), int(y_min), int(x_max - x_min), int(y_max - y_min)