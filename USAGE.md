# Usage Guide - Image Translation Tool

## Quick Start

### 1. Basic Setup
```bash
# Clone or navigate to project directory
cd imgtranslation

# Install dependencies
pip3 install -r requirements.txt

# Run the enhanced version
python3 run_app.py --version enhanced

# Or run original version
python3 run_app.py --version original
```

### 2. Access the Interface
- Open browser to `http://localhost:8501`
- Upload images containing text
- Select target language (Ukrainian recommended for testing)
- Click "Translate Image" and download results

## Feature Comparison

| Feature | Original App | Enhanced App |
|---------|-------------|-------------|
| Image Upload | Single file | Multiple files + batch |
| OCR Quality | Basic EasyOCR | Confidence filtering |
| Font Matching | System default | Language-aware fonts |
| Inpainting | Basic OpenCV | Content-aware enhancement |
| Progress Tracking | Simple spinner | Real-time callbacks |
| Error Handling | Basic try/catch | Comprehensive validation |
| Download | Single PNG | Individual + ZIP batch |
| Languages | 12 languages | 20+ with quality scoring |

## Interface Guide

### Enhanced App Features

#### 1. Configuration Sidebar
- **Target Language**: Choose from 20+ supported languages
- **OCR Confidence**: Adjust threshold (0.3-0.9) to filter uncertain text
- **Processing Mode**: Single image or batch processing

#### 2. Single Image Mode
- Drag-drop or click to upload image
- View original image with metadata (size, format, mode)
- Real-time processing with step-by-step progress
- Before/after comparison with quality metrics
- Translation details showing confidence scores

#### 3. Batch Processing Mode
- Upload multiple images simultaneously
- Progress tracking across all images
- Success/failure summary with detailed metrics
- ZIP download of all translated images
- Individual result preview for each image

#### 4. Quality Metrics
- **Processing Time**: End-to-end translation time
- **Text Regions**: Number of text areas detected
- **Average Quality**: Translation confidence score
- **Success Rate**: Percentage of successfully processed images

## Advanced Usage

### 1. Testing with Specific Images
```bash
# Test Ukrainian translation on supplement image
python3 test_ukrainian.py

# Run performance benchmarks
python3 performance_test.py
```

### 2. Confidence Threshold Tuning
- **0.3-0.5**: Detect more text (may include noise)
- **0.6-0.7**: Balanced accuracy (recommended)
- **0.8-0.9**: High precision (may miss some text)

### 3. Language-Specific Optimization

#### Ukrainian (Cyrillic Script)
- Uses Cyrillic-optimized fonts (DejaVu Sans, Liberation Sans)
- Enhanced translation quality scoring
- Special character validation

#### Asian Languages (CJK)
- Attempts to use CJK fonts (Noto Sans CJK, Hiragino)
- Different text layout considerations
- Improved character recognition

#### Right-to-Left Languages
- Arabic script support via python-bidi
- Proper text direction handling

## Troubleshooting

### Common Issues

#### 1. "No text detected in image"
**Causes:**
- Image quality too low
- Text too small or blurry
- Language not supported by OCR

**Solutions:**
- Lower confidence threshold to 0.3-0.4
- Use higher resolution images
- Ensure good contrast between text and background

#### 2. "Translation quality is low"
**Causes:**
- OCR misread the original text
- Unsupported language pair
- API rate limiting

**Solutions:**
- Check OCR confidence scores in translation details
- Verify original text detection accuracy
- Try different target languages

#### 3. "Font doesn't match original"
**Causes:**
- System fonts not available
- Language script not detected properly

**Solutions:**
- Install additional fonts for your target language
- Check font availability in system
- Use enhanced app for better font matching

#### 4. "Inpainting leaves artifacts"
**Causes:**
- Complex background patterns
- Large text regions
- High contrast edges

**Solutions:**
- Use enhanced app for content-aware inpainting
- Try images with simpler backgrounds
- Adjust padding in mask creation (future feature)

### Performance Tips

#### 1. Image Optimization
- Use images between 500-2000px in largest dimension
- Ensure good contrast (text vs background)
- Avoid extremely complex backgrounds

#### 2. Batch Processing
- Process 5-10 images at a time for optimal performance
- Use consistent image sizes in batch
- Allow sufficient processing time for large batches

#### 3. System Resources
- EasyOCR requires ~1GB RAM for model loading
- GPU acceleration available if PyTorch with CUDA installed
- Processing time: 5-15 seconds per image depending on size

## API Integration (Future)

The modular architecture supports easy API integration:

```python
from core import OCREngine, TranslationEngine, ImageProcessor

# Initialize engines
ocr = OCREngine(min_confidence=0.6)
translator = TranslationEngine()
processor = ImageProcessor()

# Process image
regions = ocr.get_text_regions(image)
# ... translation and processing logic
```

## Development Commands

```bash
# Run tests
python3 test_ukrainian.py

# Performance benchmarking
python3 performance_test.py

# Launch with specific port
python3 run_app.py --port 8502

# Check git status
git status

# Create new feature branch
git checkout -b feature/new-feature
```

## Support

### File Structure
```
imgtranslation/
├── core/                 # Core processing modules
├── assets/              # Test images and resources
├── .streamlit/          # Streamlit configuration
├── app_enhanced.py      # Enhanced Streamlit interface
├── streamlit_app.py     # Original interface
├── run_app.py          # Application launcher
├── test_ukrainian.py    # Ukrainian translation tests
├── performance_test.py  # Benchmarking suite
└── requirements.txt     # Python dependencies
```

### Logs and Debugging
- Application logs available in Streamlit interface
- Enable debug logging by setting `logging.basicConfig(level=logging.DEBUG)`
- Check browser console for JavaScript errors
- Use performance benchmarks to identify bottlenecks

### Contributing
1. Create feature branch: `git checkout -b feature/name`
2. Make changes and test thoroughly
3. Update DEVELOPMENT.md with progress
4. Commit with detailed messages
5. Test with Ukrainian translation on supplement image