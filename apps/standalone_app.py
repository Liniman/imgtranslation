#!/usr/bin/env python3
"""
Standalone web app with built-in error handling.
"""

import sys
import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import io
import base64
from urllib.parse import parse_qs, urlparse
from PIL import Image

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules with error handling
try:
    from core import OCREngine, TranslationEngine, ImageProcessor, validate_image
    logger.info("Core modules imported successfully")
except Exception as e:
    logger.error(f"Failed to import core modules: {e}")
    sys.exit(1)

# Initialize engines
try:
    logger.info("Initializing engines...")
    ocr_engine = OCREngine(min_confidence=0.6)
    translation_engine = TranslationEngine() 
    image_processor = ImageProcessor()
    logger.info("All engines initialized")
except Exception as e:
    logger.error(f"Failed to initialize engines: {e}")
    sys.exit(1)

# HTML template
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Translation Tool</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
        .upload-box { border: 2px dashed #ccc; padding: 30px; text-align: center; margin: 20px 0; }
        button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #45a049; }
        .results { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        img { max-width: 100%; border: 1px solid #ddd; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🌍 Image Translation Tool</h1>
    <div class="container">
        <div class="upload-box">
            <p>Upload an image to translate text</p>
            <input type="file" id="imageFile" accept="image/*">
            <br><br>
            <select id="targetLang">
                <option value="uk" selected>🇺🇦 Ukrainian</option>
                <option value="es">🇪🇸 Spanish</option>
                <option value="fr">🇫🇷 French</option>
                <option value="de">🇩🇪 German</option>
            </select>
            <br><br>
            <button onclick="translateImage()">Translate</button>
        </div>
        <div id="status"></div>
        <div id="results"></div>
    </div>
    
    <script>
        function translateImage() {
            const fileInput = document.getElementById('imageFile');
            const targetLang = document.getElementById('targetLang').value;
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select an image');
                return;
            }
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64Image = e.target.result.split(',')[1];
                
                document.getElementById('status').innerHTML = '<div class="status">Processing...</div>';
                
                fetch('/translate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        image: base64Image,
                        target_lang: targetLang
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('status').innerHTML = '<div class="status success">✅ ' + data.message + '</div>';
                        document.getElementById('results').innerHTML = `
                            <div class="results">
                                <div>
                                    <h3>Original</h3>
                                    <img src="data:image/png;base64,${base64Image}" alt="Original">
                                </div>
                                <div>
                                    <h3>Translated</h3>
                                    <img src="data:image/png;base64,${data.result}" alt="Translated">
                                    <br><br>
                                    <a href="data:image/png;base64,${data.result}" download="translated.png">
                                        <button>Download</button>
                                    </a>
                                </div>
                            </div>
                            <h3>Translations:</h3>
                            <ul>${data.translations.map(t => '<li>' + t + '</li>').join('')}</ul>
                        `;
                    } else {
                        document.getElementById('status').innerHTML = '<div class="status error">❌ ' + data.message + '</div>';
                    }
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = '<div class="status error">❌ Error: ' + error + '</div>';
                });
            };
            reader.readAsDataURL(file);
        }
    </script>
</body>
</html>
"""

class TranslationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/translate':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                # Decode image
                image_data = base64.b64decode(data['image'])
                image = Image.open(io.BytesIO(image_data))
                target_lang = data.get('target_lang', 'uk')
                
                # Process image
                result = self.process_image(image, target_lang)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
                
            except Exception as e:
                logger.error(f"Error processing request: {e}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'message': str(e)
                }).encode())
        else:
            self.send_error(404)
    
    def process_image(self, image, target_lang):
        """Process the image through our translation pipeline."""
        try:
            # Validate
            is_valid, msg = validate_image(image)
            if not is_valid:
                return {'success': False, 'message': msg}
            
            # OCR
            text_regions = ocr_engine.get_text_regions(image)
            if not text_regions:
                return {'success': False, 'message': 'No text detected'}
            
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
            
            # Convert to base64
            buffer = io.BytesIO()
            final_image.save(buffer, format='PNG')
            result_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Prepare translations list
            trans_list = [f"{texts[i]} → {translations[i][0]}" for i in range(len(texts))]
            
            return {
                'success': True,
                'message': f'Translated {len(text_regions)} text regions',
                'result': result_base64,
                'translations': trans_list
            }
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            return {'success': False, 'message': str(e)}
    
    def log_message(self, format, *args):
        """Suppress request logs."""
        pass

def main():
    """Start the web server."""
    PORT = 9999
    
    print(f"\n🌍 Image Translation Tool")
    print(f"=" * 40)
    print(f"✅ Server starting on port {PORT}")
    print(f"🌐 Open your browser to: http://127.0.0.1:{PORT}")
    print(f"⏹️  Press Ctrl+C to stop\n")
    
    try:
        server = HTTPServer(('127.0.0.1', PORT), TranslationHandler)
        logger.info(f"Server started on http://127.0.0.1:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()