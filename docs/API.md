# API Documentation

## Core Modules

### ImageProcessor (`core.image_processor`)

Enhanced image processing with smart font matching and better inpainting.

#### Class: `ImageProcessor`

**Methods:**

- `__init__()`: Initialize image processor with font discovery
- `_discover_system_fonts() -> Dict[str, str]`: Discover available system fonts
- `process_image(image, text_regions, translations) -> Image`: Process image with translations
- `remove_text(image, text_boxes) -> Image`: Remove text from image using inpainting
- `add_translated_text(image, text_data) -> Image`: Add translated text with proper fonts

**Font Support:**
- Windows: `C:/Windows/Fonts/`
- macOS: `/System/Library/Fonts/`, `/Library/Fonts/`, `~/Library/Fonts/`
- Linux: `/usr/share/fonts/`, `/usr/local/share/fonts/`, `~/.fonts/`

### TranslationEngine (`core.translator`)

DeepL-powered translation engine for superior context-aware translation quality.

#### Class: `TranslationEngine`

**Constructor:**
```python
TranslationEngine(primary_provider: str = 'deepl')
```

**Methods:**

- `translate_text(text: str, target_lang: str, source_lang: str = 'auto') -> str`
- `translate_batch(texts: List[str], target_lang: str) -> List[str]`
- `get_supported_languages() -> Dict[str, str]`
- `assess_quality(original: str, translated: str) -> float`

**Environment Variables:**
- `DEEPL_API_KEY`: Your DeepL API key (required)

### OCREngine (`core.ocr_engine`)

Text detection and recognition with confidence filtering.

#### Class: `OCREngine`

**Methods:**

- `detect_text(image, confidence_threshold=0.5) -> List[Dict]`
- `extract_text_regions(image) -> List[TextRegion]`
- `filter_by_confidence(detections, threshold) -> List[Dict]`

## Usage Examples

### Basic Image Translation

```python
from core.image_processor import ImageProcessor
from core.translator import TranslationEngine
from core.ocr_engine import OCREngine

# Initialize components
processor = ImageProcessor()
translator = TranslationEngine()
ocr = OCREngine()

# Process image
image = Image.open('input.jpg')
text_regions = ocr.detect_text(image)
translations = translator.translate_batch(
    [region['text'] for region in text_regions], 
    target_lang='uk'
)

# Apply translations
result = processor.process_image(image, text_regions, translations)
result.save('output.jpg')
```

### Batch Processing

```python
import os
from pathlib import Path

input_dir = Path('input_images')
output_dir = Path('output_images')

for image_path in input_dir.glob('*.jpg'):
    # Process each image...
    pass
```

## Error Handling

All modules include comprehensive error handling:

- Network timeouts for translation APIs
- Invalid image format detection
- Font loading failures
- OCR processing errors

## Configuration

### Environment Setup

Create a `.env` file:
```
DEEPL_API_KEY=your_deepl_api_key_here
```

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```