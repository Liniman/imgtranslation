"""
Enhanced image processor with improved inpainting and font matching.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import List, Tuple, Dict, Optional
import logging
import os
import platform

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Enhanced image processing with smart font matching and better inpainting."""
    
    def __init__(self):
        """Initialize image processor."""
        self.font_cache = {}
        self.system_fonts = self._discover_system_fonts()
        logger.info(f"Found {len(self.system_fonts)} system fonts")
    
    def _discover_system_fonts(self) -> Dict[str, str]:
        """
        Discover available system fonts.
        
        Returns:
            Dictionary mapping font names to file paths
        """
        fonts = {}
        
        # Common font directories by platform
        if platform.system() == "Windows":
            font_dirs = ["C:/Windows/Fonts/"]
        elif platform.system() == "Darwin":  # macOS
            font_dirs = [
                "/System/Library/Fonts/",
                "/Library/Fonts/",
                "~/Library/Fonts/"
            ]
        else:  # Linux
            font_dirs = [
                "/usr/share/fonts/",
                "/usr/local/share/fonts/",
                "~/.fonts/"
            ]
        
        # Font preferences for different languages and styles
        preferred_fonts = {
            'latin': {
                'normal': ['Arial.ttf', 'Helvetica.ttc', 'DejaVuSans.ttf', 'Liberation Sans Regular.ttf'],
                'bold': ['Arial Bold.ttf', 'Helvetica Bold.ttc', 'DejaVuSans-Bold.ttf', 'Liberation Sans Bold.ttf']
            },
            'cyrillic': {  # For Ukrainian and Russian
                'normal': ['Arial.ttf', 'DejaVuSans.ttf', 'Liberation Sans Regular.ttf', 'Roboto-Regular.ttf'],
                'bold': ['Arial Bold.ttf', 'DejaVuSans-Bold.ttf', 'Liberation Sans Bold.ttf', 'Roboto-Bold.ttf']
            },
            'cjk': {  # Chinese, Japanese, Korean
                'normal': ['NotoSansCJK-Regular.ttc', 'Hiragino Sans GB.otf', 'Yu Gothic.ttf'],
                'bold': ['NotoSansCJK-Bold.ttc', 'Hiragino Sans GB Bold.otf', 'Yu Gothic Bold.ttf']
            }
        }
        
        # Search for fonts in directories
        for font_dir in font_dirs:
            expanded_dir = os.path.expanduser(font_dir)
            if os.path.exists(expanded_dir):
                for root, dirs, files in os.walk(expanded_dir):
                    for file in files:
                        if file.lower().endswith(('.ttf', '.ttc', '.otf')):
                            font_path = os.path.join(root, file)
                            fonts[file] = font_path
        
        # Add default fallbacks
        fonts['default'] = None  # Will use PIL default
        
        return fonts
    
    def get_best_font(self, text: str, text_height: int, language: str = 'en', is_bold: bool = False) -> ImageFont.FreeTypeFont:
        """
        Get the best available font for text rendering.
        
        Args:
            text: Text to be rendered
            text_height: Target text height in pixels
            language: Language code for font selection
            is_bold: Whether text should be bold
            
        Returns:
            PIL ImageFont object
        """
        # Determine script type from language
        script_type = self._get_script_type(language)
        weight = 'bold' if is_bold else 'normal'
        
        cache_key = f"{script_type}_{weight}_{text_height}"
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Font preferences based on script type
        font_preferences = {
            'latin': {
                'normal': ['Arial.ttf', 'Helvetica.ttc', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf'],
                'bold': ['Arial Bold.ttf', 'Helvetica-Bold.ttc', 'DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf']
            },
            'cyrillic': {
                'normal': ['Arial.ttf', 'DejaVuSans.ttf', 'LiberationSans-Regular.ttf'],
                'bold': ['Arial Bold.ttf', 'DejaVuSans-Bold.ttf', 'LiberationSans-Bold.ttf']
            },
            'cjk': {
                'normal': ['NotoSansCJK-Regular.ttc', 'HiraginoSansGB-W3.otf'],
                'bold': ['NotoSansCJK-Bold.ttc', 'HiraginoSansGB-W6.otf']
            }
        }
        
        # Try preferred fonts in order
        preferred = font_preferences.get(script_type, font_preferences['latin'])
        for font_name in preferred[weight]:
            if font_name in self.system_fonts:
                try:
                    font = ImageFont.truetype(self.system_fonts[font_name], text_height)
                    self.font_cache[cache_key] = font
                    logger.debug(f"Using font {font_name} for {script_type} {weight}")
                    return font
                except Exception as e:
                    logger.debug(f"Failed to load font {font_name}: {e}")
                    continue
        
        # Fallback to default font with size adjustment
        try:
            font = ImageFont.load_default()
            self.font_cache[cache_key] = font
            logger.debug(f"Using default font for {script_type} {weight}")
            return font
        except Exception:
            # Ultimate fallback
            font = ImageFont.load_default()
            self.font_cache[cache_key] = font
            return font
    
    def _get_script_type(self, language: str) -> str:
        """
        Determine script type from language code.
        
        Args:
            language: Language code
            
        Returns:
            Script type ('latin', 'cyrillic', 'cjk', 'arabic', etc.)
        """
        cyrillic_langs = ['ru', 'uk', 'bg', 'sr', 'mk', 'be']
        cjk_langs = ['zh', 'ja', 'ko']
        arabic_langs = ['ar', 'fa', 'ur', 'he']
        
        if language in cyrillic_langs:
            return 'cyrillic'
        elif language in cjk_langs:
            return 'cjk'
        elif language in arabic_langs:
            return 'arabic'
        else:
            return 'latin'
    
    def create_enhanced_mask(self, image: Image.Image, text_regions: List[Dict], padding: int = 3) -> Image.Image:
        """
        Create enhanced mask for text inpainting.
        
        Args:
            image: Source image
            text_regions: List of text region dictionaries
            padding: Padding around text regions
            
        Returns:
            Binary mask image
        """
        mask = Image.new('L', image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        
        for region in text_regions:
            bbox_rect = region['bbox_rect']
            x, y, w, h = bbox_rect
            
            # Add padding
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.width - x, w + 2 * padding)
            h = min(image.height - y, h + 2 * padding)
            
            # Create mask with slight feathering for better inpainting
            mask_draw.rectangle([x, y, x + w, y + h], fill=255)
        
        return mask
    
    def enhanced_inpainting(self, image: Image.Image, mask: Image.Image) -> Image.Image:
        """
        Perform enhanced inpainting with multiple techniques.
        
        Args:
            image: Source image
            mask: Binary mask of regions to inpaint
            
        Returns:
            Inpainted image
        """
        # Convert to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        mask_cv = np.array(mask)
        
        # Choose inpainting method based on mask characteristics
        mask_area = np.sum(mask_cv > 0)
        total_area = mask_cv.shape[0] * mask_cv.shape[1]
        mask_ratio = mask_area / total_area
        
        if mask_ratio > 0.1:  # Large text regions
            # Use TELEA for large regions (better structure preservation)
            inpainted = cv2.inpaint(img_cv, mask_cv, 5, cv2.INPAINT_TELEA)
        else:
            # Use NS (Navier-Stokes) for small regions (smoother results)
            inpainted = cv2.inpaint(img_cv, mask_cv, 3, cv2.INPAINT_NS)
        
        # Apply additional content-aware improvements
        inpainted = self._content_aware_enhancement(img_cv, inpainted, mask_cv)
        
        # Convert back to PIL
        return Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
    
    def _content_aware_enhancement(self, original: np.ndarray, inpainted: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Apply content-aware enhancements to inpainted result.
        
        Args:
            original: Original image
            inpainted: Inpainted image
            mask: Inpainting mask
            
        Returns:
            Enhanced inpainted image
        """
        # For small masks, try to match surrounding colors better
        result = inpainted.copy()
        
        # Find mask contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Expand search region for color sampling
            margin = max(w, h) // 3
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(original.shape[1], x + w + margin)
            y2 = min(original.shape[0], y + h + margin)
            
            # Sample background colors from border region
            border_region = original[y1:y2, x1:x2]
            border_mask = mask[y1:y2, x1:x2] == 0
            
            if np.any(border_mask):
                # Calculate median color of background
                bg_pixels = border_region[border_mask]
                if len(bg_pixels) > 0:
                    median_color = np.median(bg_pixels, axis=0)
                    
                    # Blend with inpainted result for more natural look
                    text_mask = mask[y:y+h, x:x+w] > 0
                    if np.any(text_mask):
                        current_region = result[y:y+h, x:x+w]
                        # Subtle blending towards background color
                        blend_factor = 0.3
                        current_region[text_mask] = (
                            current_region[text_mask] * (1 - blend_factor) +
                            median_color * blend_factor
                        ).astype(np.uint8)
        
        return result
    
    def add_translated_text(self, image: Image.Image, text_regions: List[Dict]) -> Image.Image:
        """
        Add translated text to image with smart positioning and font matching.
        
        Args:
            image: Base image (after inpainting)
            text_regions: List of text regions with translations
            
        Returns:
            Image with translated text added
        """
        result_image = image.copy()
        draw = ImageDraw.Draw(result_image)
        
        for region in text_regions:
            if 'translated_text' not in region:
                continue
            
            text = region['translated_text']
            bbox_rect = region['bbox_rect']
            x, y, w, h = bbox_rect
            
            # Detect text properties
            is_bold = region.get('is_bold', False)
            language = region.get('target_language', 'uk')
            
            # Smart font size calculation with text fitting
            font_size, fitted_text = self._calculate_optimal_font_size(
                text, w, h, language, is_bold, draw
            )
            
            # Get appropriate font
            font = self.get_best_font(fitted_text, font_size, language, is_bold)
            
            # Calculate text position for centering within bounds
            bbox_text = draw.textbbox((0, 0), fitted_text, font=font)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]
            
            # Ensure text fits within bounding box
            if text_width > w or text_height > h:
                # Try smaller font size
                font_size = int(font_size * 0.8)
                font = self.get_best_font(fitted_text, font_size, language, is_bold)
                bbox_text = draw.textbbox((0, 0), fitted_text, font=font)
                text_width = bbox_text[2] - bbox_text[0]
                text_height = bbox_text[3] - bbox_text[1]
            
            # Center text in bounding box with constraints
            center_x = x + w // 2
            center_y = y + h // 2
            text_x = max(x, center_x - text_width // 2)
            text_y = max(y, center_y - text_height // 2)
            
            # Ensure text doesn't exceed right/bottom bounds
            if text_x + text_width > x + w:
                text_x = x + w - text_width
            if text_y + text_height > y + h:
                text_y = y + h - text_height
            
            # Determine text color based on background
            text_color, outline_color = self._get_optimal_colors(image, x, y, w, h)
            
            # Draw text with outline for better visibility
            outline_width = max(1, font_size // 25)  # Thinner outline for better fit
            
            # Draw outline
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((text_x + dx, text_y + dy), fitted_text, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((text_x, text_y), fitted_text, font=font, fill=text_color)
            
            logger.debug(f"Added text '{fitted_text}' at ({text_x}, {text_y}) with font size {font_size}")
        
        return result_image
    
    def _calculate_optimal_font_size(self, text: str, max_width: int, max_height: int, 
                                   language: str, is_bold: bool, draw: ImageDraw.Draw) -> tuple:
        """
        Calculate optimal font size and handle text wrapping if needed.
        
        Args:
            text: Text to fit
            max_width: Maximum width available
            max_height: Maximum height available  
            language: Language code
            is_bold: Whether text is bold
            draw: ImageDraw object for text measurement
            
        Returns:
            Tuple of (font_size, fitted_text)
        """
        # Start with height-based font size
        initial_font_size = int(max_height * 0.6)  # More conservative than 0.7
        initial_font_size = max(8, min(initial_font_size, 100))  # Reasonable bounds
        
        # Try to fit text at this size
        for font_size in range(initial_font_size, 7, -2):  # Decrease in steps of 2
            font = self.get_best_font(text, font_size, language, is_bold)
            
            # Measure text dimensions
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # If text fits, we're done
            if text_width <= max_width and text_height <= max_height:
                return font_size, text
        
        # If text still doesn't fit, try word wrapping for multi-word text
        words = text.split()
        if len(words) > 1:
            return self._fit_text_with_wrapping(words, max_width, max_height, language, is_bold, draw)
        
        # Last resort: truncate text
        font_size = max(8, int(max_height * 0.4))
        font = self.get_best_font(text, font_size, language, is_bold)
        
        # Find maximum characters that fit
        for i in range(len(text), 0, -1):
            truncated = text[:i] + ('...' if i < len(text) else '')
            bbox = draw.textbbox((0, 0), truncated, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                return font_size, truncated
        
        # Ultimate fallback
        return 8, text[:3] + '...'
    
    def _fit_text_with_wrapping(self, words: List[str], max_width: int, max_height: int,
                               language: str, is_bold: bool, draw: ImageDraw.Draw) -> tuple:
        """
        Try to fit text with line wrapping.
        
        Args:
            words: List of words to fit
            max_width: Maximum width available
            max_height: Maximum height available
            language: Language code  
            is_bold: Whether text is bold
            draw: ImageDraw object
            
        Returns:
            Tuple of (font_size, fitted_text)
        """
        # Try different font sizes for wrapped text
        for font_size in range(int(max_height * 0.3), 7, -1):
            font = self.get_best_font(' '.join(words), font_size, language, is_bold)
            
            # Try to fit words on multiple lines
            lines = []
            current_line = []
            
            for word in words:
                test_line = current_line + [word]
                test_text = ' '.join(test_line)
                
                bbox = draw.textbbox((0, 0), test_text, font=font)
                line_width = bbox[2] - bbox[0]
                
                if line_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:  # Save current line and start new one
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:  # Single word is too long
                        lines.append(word[:max(1, max_width // (font_size // 2))] + '...')
                        current_line = []
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Check if all lines fit vertically
            total_height = len(lines) * font_size * 1.2  # Line spacing
            if total_height <= max_height:
                return font_size, '\n'.join(lines)
        
        # Fallback to single line with truncation
        return self._calculate_optimal_font_size(' '.join(words[:2]) + '...', max_width, max_height, language, is_bold, draw)
    
    def _get_optimal_colors(self, image: Image.Image, x: int, y: int, w: int, h: int) -> Tuple[str, str]:
        """
        Determine optimal text and outline colors based on background.
        
        Args:
            image: Background image
            x, y, w, h: Text region coordinates
            
        Returns:
            Tuple of (text_color, outline_color)
        """
        # Sample background color from center of region
        sample_x = min(max(x + w // 2, 0), image.width - 1)
        sample_y = min(max(y + h // 2, 0), image.height - 1)
        
        try:
            # Get pixel color
            pixel = image.getpixel((sample_x, sample_y))
            if isinstance(pixel, tuple) and len(pixel) >= 3:
                brightness = sum(pixel[:3]) / 3
            else:
                brightness = pixel if isinstance(pixel, (int, float)) else 128
            
            # Choose contrasting colors
            if brightness > 127:  # Light background
                return 'black', 'white'
            else:  # Dark background  
                return 'white', 'black'
                
        except Exception as e:
            logger.debug(f"Color detection failed: {e}")
            return 'black', 'white'  # Safe default
    
    def resize_for_processing(self, image: Image.Image, max_dimension: int = 2048) -> Tuple[Image.Image, float]:
        """
        Resize image for optimal processing if needed.
        
        Args:
            image: Input image
            max_dimension: Maximum width or height
            
        Returns:
            Tuple of (resized_image, scale_factor)
        """
        width, height = image.size
        
        if width <= max_dimension and height <= max_dimension:
            return image, 1.0
        
        # Calculate scale factor
        scale = max_dimension / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height} (scale: {scale:.2f})")
        
        return resized, scale