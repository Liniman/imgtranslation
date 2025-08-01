#!/usr/bin/env python3
"""
Generate an offline HTML file with the translation results.
"""

import os
import base64
from PIL import Image
from core import OCREngine, TranslationEngine, ImageProcessor, validate_image

def create_offline_demo():
    """Create an offline HTML demo with the supplement image."""
    
    print("🌍 Creating Offline Translation Demo")
    print("=" * 40)
    
    # Initialize engines
    print("Initializing engines...")
    ocr_engine = OCREngine(min_confidence=0.6)
    translation_engine = TranslationEngine()
    image_processor = ImageProcessor()
    
    # Load test image
    image_path = "/Users/andriy.ivakhov/imgtranslation/assets/Sports-Research-Omega-3-Fish-Oil-Triple-Strength-180-Softgels-07-29-2025_05_32_PM.png"
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return
    
    print("Loading image...")
    image = Image.open(image_path)
    
    # Process image
    print("Processing image...")
    text_regions = ocr_engine.get_text_regions(image)
    
    if not text_regions:
        print("❌ No text detected")
        return
    
    # Translate to Ukrainian
    print("Translating to Ukrainian...")
    texts = [r['text'] for r in text_regions]
    translations = translation_engine.translate_batch(texts, 'uk')
    
    # Update regions
    for i, (trans, quality) in enumerate(translations):
        if i < len(text_regions):
            text_regions[i]['translated_text'] = trans
            text_regions[i]['target_language'] = 'uk'
    
    # Process image
    print("Creating translated image...")
    mask = image_processor.create_enhanced_mask(image, text_regions)
    inpainted = image_processor.enhanced_inpainting(image, mask)
    final_image = image_processor.add_translated_text(inpainted, text_regions)
    
    # Convert images to base64
    def img_to_base64(img):
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    original_b64 = img_to_base64(image)
    result_b64 = img_to_base64(final_image)
    
    # Create HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Image Translation Demo - Offline</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .results {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 20px 0;
            }}
            .result-box {{
                text-align: center;
            }}
            img {{
                max-width: 100%;
                border: 2px solid #ddd;
                border-radius: 5px;
            }}
            .translations {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .success {{
                color: green;
                font-weight: bold;
            }}
            code {{
                background: #eee;
                padding: 2px 5px;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>
        <h1>🌍 Image Translation Demo - Ukrainian</h1>
        <div class="container">
            <p class="success">✅ Successfully translated {len(text_regions)} text regions!</p>
            
            <div class="results">
                <div class="result-box">
                    <h2>Original</h2>
                    <img src="data:image/png;base64,{original_b64}" alt="Original">
                </div>
                <div class="result-box">
                    <h2>Translated to Ukrainian</h2>
                    <img src="data:image/png;base64,{result_b64}" alt="Translated">
                </div>
            </div>
            
            <div class="translations">
                <h3>📝 Translation Details:</h3>
                <ul>
    """
    
    # Add translations
    for i, (orig, (trans, quality)) in enumerate(zip(texts, translations)):
        html_content += f'<li><code>{orig}</code> → <code>{trans}</code> (quality: {quality:.2f})</li>\n'
    
    html_content += """
                </ul>
            </div>
            
            <p style="text-align: center; margin-top: 30px;">
                <a href="#" onclick="downloadImage()" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    📥 Download Translated Image
                </a>
            </p>
        </div>
        
        <script>
            function downloadImage() {
                const link = document.createElement('a');
                link.href = 'data:image/png;base64,""" + result_b64 + """';
                link.download = 'translated_ukrainian.png';
                link.click();
            }
        </script>
    </body>
    </html>
    """
    
    # Save HTML file
    output_path = "/Users/andriy.ivakhov/imgtranslation/offline_demo.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ Offline demo created successfully!")
    print(f"📁 File saved to: {output_path}")
    print(f"\n🌐 To view the results:")
    print(f"   1. Open Finder")
    print(f"   2. Navigate to: /Users/andriy.ivakhov/imgtranslation/")
    print(f"   3. Double-click: offline_demo.html")
    print(f"\n   Or run: open offline_demo.html")

if __name__ == "__main__":
    create_offline_demo()