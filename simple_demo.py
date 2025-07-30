#!/usr/bin/env python3
"""
Simple demo to show the working image translation system.
"""

import os
import time
from PIL import Image

# Import our enhanced modules
from core import OCREngine, TranslationEngine, ImageProcessor, validate_image

def main():
    print("🌍 Image Translation Demo")
    print("=" * 40)
    
    # Check if supplement image exists
    image_path = "/Users/andriy.ivakhov/imgtranslation/assets/Sports-Research-Omega-3-Fish-Oil-Triple-Strength-180-Softgels-07-29-2025_05_32_PM.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        print("Please make sure the supplement image is in the assets/ folder")
        return
    
    print(f"📷 Loading: {os.path.basename(image_path)}")
    
    try:
        # Load image
        image = Image.open(image_path)
        print(f"✅ Image loaded: {image.size[0]}x{image.size[1]} pixels")
        
        # Validate image
        is_valid, msg = validate_image(image)
        if not is_valid:
            print(f"❌ Validation failed: {msg}")
            return
        print("✅ Image validation passed")
        
        # Initialize engines
        print("\n🔧 Initializing engines...")
        ocr_engine = OCREngine(min_confidence=0.5)
        translation_engine = TranslationEngine()
        image_processor = ImageProcessor()
        print("✅ All engines ready")
        
        # Detect text
        print("\n🔍 Detecting text...")
        start_time = time.time()
        text_regions = ocr_engine.get_text_regions(image)
        ocr_time = time.time() - start_time
        
        if not text_regions:
            print("❌ No text detected")
            return
        
        print(f"✅ Found {len(text_regions)} text regions in {ocr_time:.2f}s:")
        for i, region in enumerate(text_regions):
            print(f"   {i+1}. '{region['text']}' (confidence: {region['confidence']:.2f})")
        
        # Translate to Ukrainian
        print("\n🌐 Translating to Ukrainian...")
        start_time = time.time()
        texts_to_translate = [region['text'] for region in text_regions]
        translations = translation_engine.translate_batch(texts_to_translate, 'uk')
        translation_time = time.time() - start_time
        
        print(f"✅ Translation completed in {translation_time:.2f}s:")
        for i, (original, (translated, quality)) in enumerate(zip(texts_to_translate, translations)):
            print(f"   {i+1}. '{original}' → '{translated}' (quality: {quality:.2f})")
            # Add translation to regions
            if i < len(text_regions):
                text_regions[i]['translated_text'] = translated
                text_regions[i]['translation_quality'] = quality
                text_regions[i]['target_language'] = 'uk'
        
        # Process image
        print("\n🎨 Processing image...")
        start_time = time.time()
        
        # Create mask
        mask = image_processor.create_enhanced_mask(image, text_regions)
        
        # Inpaint
        inpainted = image_processor.enhanced_inpainting(image, mask)
        
        # Add translated text
        final_image = image_processor.add_translated_text(inpainted, text_regions)
        
        processing_time = time.time() - start_time
        print(f"✅ Image processing completed in {processing_time:.2f}s")
        
        # Save result
        output_path = "/Users/andriy.ivakhov/imgtranslation/demo_result_ukrainian.png"
        final_image.save(output_path)
        print(f"\n💾 Result saved to: demo_result_ukrainian.png")
        
        # Summary
        total_time = ocr_time + translation_time + processing_time
        print(f"\n📊 Performance Summary:")
        print(f"   Total processing time: {total_time:.2f}s")
        print(f"   Text regions processed: {len(text_regions)}")
        print(f"   Average translation quality: {sum(r.get('translation_quality', 0) for r in text_regions) / len(text_regions):.2f}")
        
        print(f"\n🎉 SUCCESS! Ukrainian translation complete!")
        print(f"   Original: {os.path.basename(image_path)}")
        print(f"   Result: demo_result_ukrainian.png")
        print(f"   Open both files to compare!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()