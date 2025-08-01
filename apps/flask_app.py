#!/usr/bin/env python3
"""
Simple Flask web interface for image translation.
"""

from flask import Flask, render_template_string, request, send_file
from werkzeug.utils import secure_filename
import os
import io
from PIL import Image
import base64

# Import our core modules
from core import OCREngine, TranslationEngine, ImageProcessor, validate_image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize engines
print("Initializing engines...")
ocr_engine = OCREngine(min_confidence=0.6)
translation_engine = TranslationEngine()
image_processor = ImageProcessor()
print("Engines ready!")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🌍 Image Translation Tool</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .upload-area {
            border: 2px dashed #ccc;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
        }
        .button {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        .button:hover {
            background: #45a049;
        }
        .results {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        .result-box {
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
        }
        img {
            max-width: 100%;
            height: auto;
        }
        .status {
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .info { background: #d1ecf1; color: #0c5460; }
        select {
            padding: 8px;
            font-size: 16px;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 Image Translation Tool</h1>
        
        <form method="POST" enctype="multipart/form-data">
            <div class="upload-area">
                <p>📤 Upload an image containing text</p>
                <input type="file" name="image" accept="image/*" required>
                <br><br>
                <label>Target Language:</label>
                <select name="target_lang">
                    <option value="uk" selected>🇺🇦 Ukrainian</option>
                    <option value="es">🇪🇸 Spanish</option>
                    <option value="fr">🇫🇷 French</option>
                    <option value="de">🇩🇪 German</option>
                    <option value="it">🇮🇹 Italian</option>
                    <option value="pt">🇵🇹 Portuguese</option>
                    <option value="ja">🇯🇵 Japanese</option>
                    <option value="ko">🇰🇷 Korean</option>
                    <option value="zh">🇨🇳 Chinese</option>
                </select>
                <br><br>
                <button type="submit" class="button">🚀 Translate Image</button>
            </div>
        </form>
        
        {% if status %}
            <div class="status {{ status_type }}">{{ status }}</div>
        {% endif %}
        
        {% if result %}
            <h2>📊 Results</h2>
            <div class="results">
                <div class="result-box">
                    <h3>Original</h3>
                    <img src="data:image/png;base64,{{ original_img }}" alt="Original">
                </div>
                <div class="result-box">
                    <h3>Translated</h3>
                    <img src="data:image/png;base64,{{ result_img }}" alt="Translated">
                    <br><br>
                    <a href="/download" class="button">📥 Download</a>
                </div>
            </div>
            
            <h3>📝 Translation Details</h3>
            <ul>
                {% for orig, trans in translations %}
                    <li><code>{{ orig }}</code> → <code>{{ trans }}</code></li>
                {% endfor %}
            </ul>
        {% endif %}
    </div>
</body>
</html>
"""

# Store last result for download
last_result = None

@app.route('/', methods=['GET', 'POST'])
def index():
    global last_result
    
    if request.method == 'POST':
        try:
            # Get uploaded file
            file = request.files['image']
            target_lang = request.form.get('target_lang', 'uk')
            
            # Load image
            image = Image.open(file.stream)
            
            # Validate
            is_valid, msg = validate_image(image)
            if not is_valid:
                return render_template_string(HTML_TEMPLATE, 
                                            status=f"❌ {msg}", 
                                            status_type="error")
            
            # Process image
            text_regions = ocr_engine.get_text_regions(image)
            
            if not text_regions:
                return render_template_string(HTML_TEMPLATE, 
                                            status="❌ No text detected", 
                                            status_type="error")
            
            # Translate
            texts = [r['text'] for r in text_regions]
            translations = translation_engine.translate_batch(texts, target_lang)
            
            # Update regions
            for i, (trans, quality) in enumerate(translations):
                if i < len(text_regions):
                    text_regions[i]['translated_text'] = trans
                    text_regions[i]['target_language'] = target_lang
            
            # Process image
            mask = image_processor.create_enhanced_mask(image, text_regions)
            inpainted = image_processor.enhanced_inpainting(image, mask)
            final_image = image_processor.add_translated_text(inpainted, text_regions)
            
            # Convert images to base64
            def img_to_base64(img):
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                return base64.b64encode(buffer.getvalue()).decode()
            
            original_b64 = img_to_base64(image)
            result_b64 = img_to_base64(final_image)
            
            # Store result for download
            last_result = final_image
            
            # Prepare translation pairs
            trans_pairs = [(texts[i], translations[i][0]) 
                          for i in range(len(texts))]
            
            return render_template_string(HTML_TEMPLATE,
                                        status=f"✅ Translated {len(text_regions)} text regions",
                                        status_type="success",
                                        result=True,
                                        original_img=original_b64,
                                        result_img=result_b64,
                                        translations=trans_pairs)
            
        except Exception as e:
            return render_template_string(HTML_TEMPLATE,
                                        status=f"❌ Error: {str(e)}",
                                        status_type="error")
    
    return render_template_string(HTML_TEMPLATE)

@app.route('/download')
def download():
    global last_result
    if last_result:
        buffer = io.BytesIO()
        last_result.save(buffer, format='PNG')
        buffer.seek(0)
        return send_file(buffer, 
                        mimetype='image/png',
                        as_attachment=True,
                        download_name='translated_image.png')
    return "No image to download", 404

if __name__ == '__main__':
    print("\n🌍 Starting Image Translation Web Interface...")
    print("🌐 Open your browser to: http://127.0.0.1:5000")
    print("⏹️  Press Ctrl+C to stop\n")
    app.run(host='127.0.0.1', port=5000, debug=False)