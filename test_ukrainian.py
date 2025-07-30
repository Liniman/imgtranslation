"""
Test script for Ukrainian translation on supplement image.
"""

import logging
from PIL import Image
import time
import os

# Import our core modules
from core import OCREngine, TranslationEngine, ImageProcessor, validate_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_ukrainian_translation():
    """Test Ukrainian translation on the supplement image."""
    
    print("🧪 Testing Ukrainian Translation System")
    print("=" * 50)
    
    # Initialize engines
    print("🔧 Initializing engines...")
    try:
        ocr_engine = OCREngine(min_confidence=0.5)  # Lower confidence for testing
        translation_engine = TranslationEngine()
        image_processor = ImageProcessor()
        print("✅ All engines initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize engines: {e}")
        return False
    
    # Load test image
    image_path = "/Users/andriy.ivakhov/imgtranslation/assets/Sports-Research-Omega-3-Fish-Oil-Triple-Strength-180-Softgels-07-29-2025_05_32_PM.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        print("   Please ensure the image exists in the assets/ directory")
        return False
    
    print(f"📷 Loading test image: {os.path.basename(image_path)}")
    try:
        image = Image.open(image_path)
        print(f"✅ Image loaded: {image.size[0]}x{image.size[1]} pixels, mode: {image.mode}")
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
        return False
    
    # Validate image
    print("🔍 Validating image...")
    is_valid, error_msg = validate_image(image)
    if not is_valid:
        print(f"❌ Image validation failed: {error_msg}")
        return False
    print("✅ Image validation passed")
    
    # Start processing
    start_time = time.time()
    target_lang = 'uk'  # Ukrainian
    
    try:
        # Step 1: Resize if needed
        print("📏 Preparing image for processing...")
        processed_image, scale_factor = image_processor.resize_for_processing(image)
        if scale_factor != 1.0:
            print(f"   Image resized by factor {scale_factor:.2f}")
        else:
            print("   Image size is optimal, no resizing needed")
        
        # Step 2: OCR text detection
        print("🔍 Detecting text regions...")
        text_regions = ocr_engine.get_text_regions(processed_image)
        
        if not text_regions:
            print("❌ No text detected in image")
            return False
        
        print(f"✅ Detected {len(text_regions)} text regions:")
        for i, region in enumerate(text_regions):
            print(f"   {i+1}. '{region['text']}' (confidence: {region['confidence']:.2f})")
        
        # Step 3: Translate to Ukrainian
        print(f"🌐 Translating to Ukrainian...")
        texts_to_translate = [region['text'] for region in text_regions]
        translations = translation_engine.translate_batch(texts_to_translate, target_lang)
        
        print("📝 Translation results:")
        for i, (original_text, (translated_text, quality)) in enumerate(zip(texts_to_translate, translations)):
            print(f"   {i+1}. '{original_text}' → '{translated_text}' (quality: {quality:.2f})")
            # Add to region data
            if i < len(text_regions):
                text_regions[i]['translated_text'] = translated_text
                text_regions[i]['translation_quality'] = quality
                text_regions[i]['target_language'] = target_lang
        
        # Step 4: Create inpainting mask
        print("🎨 Creating inpainting mask...")
        mask = image_processor.create_enhanced_mask(processed_image, text_regions)
        mask_pixels = sum(1 for pixel in mask.getdata() if pixel > 0)
        total_pixels = mask.size[0] * mask.size[1]
        mask_coverage = (mask_pixels / total_pixels) * 100
        print(f"   Mask covers {mask_coverage:.1f}% of image")
        
        # Step 5: Inpaint original text
        print("🖌️ Removing original text...")
        inpainted_image = image_processor.enhanced_inpainting(processed_image, mask)
        print("✅ Original text removed")
        
        # Step 6: Add Ukrainian text
        print("✍️ Adding Ukrainian text...")
        final_image = image_processor.add_translated_text(inpainted_image, text_regions)
        print("✅ Ukrainian text added")
        
        # Scale back to original size if needed
        if scale_factor != 1.0:
            final_size = (
                int(final_image.width / scale_factor),
                int(final_image.height / scale_factor)
            )
            final_image = final_image.resize(final_size, Image.Resampling.LANCZOS)
            print(f"   Final image scaled back to {final_size[0]}x{final_size[1]}")
        
        # Save result
        output_path = "/Users/andriy.ivakhov/imgtranslation/test_output_ukrainian.png"
        final_image.save(output_path)
        print(f"💾 Result saved to: {output_path}")
        
        # Processing summary
        processing_time = time.time() - start_time
        print(f"\n🎉 Translation completed successfully!")
        print(f"   Processing time: {processing_time:.2f} seconds")
        print(f"   Text regions processed: {len(text_regions)}")
        print(f"   Average translation quality: {sum(r.get('translation_quality', 0) for r in text_regions) / len(text_regions):.2f}")
        
        # Quality assessment
        print(f"\n📊 Quality Assessment:")
        high_quality = sum(1 for r in text_regions if r.get('translation_quality', 0) > 0.7)
        medium_quality = sum(1 for r in text_regions if 0.4 <= r.get('translation_quality', 0) <= 0.7)
        low_quality = sum(1 for r in text_regions if r.get('translation_quality', 0) < 0.4)
        
        print(f"   High quality translations (>0.7): {high_quality}")
        print(f"   Medium quality translations (0.4-0.7): {medium_quality}")
        print(f"   Low quality translations (<0.4): {low_quality}")
        
        return True
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def benchmark_performance():
    """Benchmark system performance."""
    print("\n⚡ Performance Benchmark")
    print("=" * 30)
    
    # Test with different confidence thresholds
    confidence_levels = [0.3, 0.5, 0.7, 0.9]
    
    for confidence in confidence_levels:
        print(f"\n🔧 Testing with confidence threshold: {confidence}")
        
        try:
            ocr_engine = OCREngine(min_confidence=confidence)
            image_path = "/Users/andriy.ivakhov/imgtranslation/assets/Sports-Research-Omega-3-Fish-Oil-Triple-Strength-180-Softgels-07-29-2025_05_32_PM.png"
            
            if os.path.exists(image_path):
                image = Image.open(image_path)
                
                start_time = time.time()
                text_regions = ocr_engine.get_text_regions(image)
                ocr_time = time.time() - start_time
                
                print(f"   OCR time: {ocr_time:.2f}s")
                print(f"   Text regions detected: {len(text_regions)}")
                
                if text_regions:
                    avg_confidence = sum(r['confidence'] for r in text_regions) / len(text_regions)
                    print(f"   Average confidence: {avg_confidence:.2f}")
        
        except Exception as e:
            print(f"   ❌ Failed: {e}")

if __name__ == "__main__":
    # Run main test
    success = test_ukrainian_translation()
    
    if success:
        # Run performance benchmark
        benchmark_performance()
        
        print(f"\n🎯 Test Summary:")
        print(f"   ✅ Core functionality: PASSED")
        print(f"   ✅ Ukrainian translation: PASSED") 
        print(f"   ✅ Performance benchmark: COMPLETED")
    else:
        print(f"\n❌ Test failed - check logs above for details")