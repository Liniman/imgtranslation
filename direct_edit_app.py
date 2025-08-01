"""
Direct-manipulation text editing interface for image translation.
Provides Google Slides-like editing experience where users can click directly on text.
"""

import streamlit as st
import logging
from PIL import Image, ImageDraw
import io
import json
import base64
from typing import List, Dict, Optional, Tuple
import time
import numpy as np

# Import our enhanced core modules
from core import OCREngine, TranslationEngine, ImageProcessor, validate_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Direct Text Editor",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for direct manipulation interface
st.markdown("""
<style>
    /* Hide Streamlit default elements for cleaner look */
    .stDeployButton {display: none;}
    .stDecoration {display: none;}
    
    /* Main container styling */
    .main-container {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
    }
    
    /* Image container with relative positioning for overlays */
    .image-container {
        position: relative;
        display: inline-block;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        background: white;
    }
    
    /* Text region overlays - invisible by default */
    .text-region {
        position: absolute;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
        border-radius: 4px;
        background: transparent;
    }
    
    .text-region:hover {
        border: 2px solid #3b82f6;
        background: rgba(59, 130, 246, 0.15);
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
    }
    
    .text-region.selected {
        border-color: #ef4444;
        background: rgba(239, 68, 68, 0.15);
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.3);
        z-index: 10;
    }
    
    /* Floating control panel */
    .control-panel {
        position: fixed;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        padding: 1.5rem;
        z-index: 1000;
        border: 1px solid #e5e7eb;
        min-width: 320px;
        max-width: 400px;
        display: none;
    }
    
    .control-panel.visible {
        display: block;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Control panel header */
    .control-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .control-title {
        font-weight: 600;
        color: #374151;
        font-size: 0.9rem;
    }
    
    .close-btn {
        background: none;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
        color: #6b7280;
        padding: 0.25rem;
        border-radius: 4px;
    }
    
    .close-btn:hover {
        background: #f3f4f6;
        color: #374151;
    }
    
    /* Control groups */
    .control-group {
        margin-bottom: 1rem;
    }
    
    .control-label {
        display: block;
        font-size: 0.85rem;
        font-weight: 500;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    /* Size adjustment buttons */
    .size-controls {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .size-btn {
        background: #f3f4f6;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        font-size: 0.8rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    
    .size-btn:hover {
        background: #e5e7eb;
        border-color: #9ca3af;
    }
    
    .size-btn.active {
        background: #3b82f6;
        color: white;
        border-color: #3b82f6;
    }
    
    /* Font selector */
    .font-selector {
        width: 100%;
        padding: 0.5rem 0.75rem;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 0.85rem;
        background: white;
    }
    
    .font-selector:focus {
        outline: none;
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* Size slider */
    .size-slider {
        width: 100%;
        height: 6px;
        border-radius: 3px;
        background: #e5e7eb;
        outline: none;
        margin: 0.5rem 0;
    }
    
    .size-slider::-webkit-slider-thumb {
        appearance: none;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: #3b82f6;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .size-slider::-moz-range-thumb {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: #3b82f6;
        cursor: pointer;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Text content display */
    .text-content {
        background: #f8fafc;
        border-radius: 6px;
        padding: 0.75rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    .original-text {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 0.25rem;
    }
    
    .translated-text {
        font-size: 0.9rem;
        color: #1e293b;
        font-weight: 500;
    }
    
    /* Action buttons */
    .action-buttons {
        display: flex;
        gap: 0.5rem;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #e5e7eb;
    }
    
    .action-btn {
        flex: 1;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
    }
    
    .btn-primary {
        background: #3b82f6;
        color: white;
        border: 1px solid #3b82f6;
    }
    
    .btn-primary:hover {
        background: #2563eb;
        border-color: #2563eb;
    }
    
    .btn-secondary {
        background: white;
        color: #374151;
        border: 1px solid #d1d5db;
    }
    
    .btn-secondary:hover {
        background: #f9fafb;
        border-color: #9ca3af;
    }
    
    /* Loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 2000;
    }
    
    .loading-content {
        background: white;
        padding: 2rem 3rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    .spinner {
        border: 3px solid #f3f4f6;
        border-top: 3px solid #3b82f6;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Processing steps layout */
    .processing-steps {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .processing-step {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 2px solid #e5e7eb;
        transition: all 0.3s ease;
    }
    
    .processing-step.pending {
        opacity: 0.5;
        border-color: #d1d5db;
    }
    
    .processing-step.processing {
        border-color: #3b82f6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    .processing-step.completed {
        border-color: #10b981;
        background: linear-gradient(135deg, #f0fdf4, white);
    }
    
    .processing-step.error {
        border-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2, white);
    }
    
    .step-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }
    
    .step-title {
        font-weight: 600;
        color: #374151;
        font-size: 0.9rem;
    }
    
    .step-status {
        font-size: 1.2rem;
    }
    
    .step-content {
        text-align: center;
    }
    
    .step-image {
        width: 100%;
        max-height: 200px;
        object-fit: contain;
        border-radius: 4px;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.5rem;
    }
    
    .step-stats {
        font-size: 0.8rem;
        color: #6b7280;
        display: flex;
        justify-content: space-between;
        margin-top: 0.5rem;
    }
    
    .progress-bar {
        width: 100%;
        height: 4px;
        background: #e5e7eb;
        border-radius: 2px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #3b82f6, #10b981);
        border-radius: 2px;
        transition: width 0.3s ease;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .control-panel {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            border-radius: 12px 12px 0 0;
            max-width: none;
            min-width: auto;
        }
        
        .main-container {
            padding: 1rem;
        }
        
        .processing-steps {
            grid-template-columns: 1fr;
        }
    }
    
    /* Success/error indicators */
    .status-indicator {
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status-error {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_engines():
    """Load and cache the core engines."""
    logger.info("Initializing engines...")
    try:
        ocr_engine = OCREngine(min_confidence=0.6)
        translation_engine = TranslationEngine()
        image_processor = ImageProcessor()
        
        logger.info("All engines initialized successfully") 
        return ocr_engine, translation_engine, image_processor
    except Exception as e:
        logger.error(f"Failed to initialize engines: {e}")
        st.error(f"Failed to initialize processing engines: {e}")
        st.stop()

def create_ocr_visualization_html_3state(image: Image.Image, text_regions: List[Dict], 
                                        region_actions: List[str] = None) -> str:
    """
    Create HTML for OCR visualization with 3-state action control.
    
    Args:
        image: PIL Image to display
        text_regions: List of text regions with bounding boxes
        region_actions: List of actions for each region ('translate', 'keep', 'remove')
        
    Returns:
        HTML string with 3-state OCR region controls
    """
    if region_actions is None:
        region_actions = ['translate'] * len(text_regions)
    
    # Convert image to base64 for embedding
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Calculate image display dimensions - use container width or max 1000px
    max_width = min(1000, image.width)
    max_height = 600  # Max height to prevent very tall images
    
    # Calculate scaling to fit within bounds while maintaining aspect ratio
    width_scale = max_width / image.width
    height_scale = max_height / image.height
    scale = min(width_scale, height_scale, 1.0)  # Don't upscale
    
    display_width = int(image.width * scale)
    display_height = int(image.height * scale)
    
    # Scale factors for positioning overlays
    scale_x = display_width / image.width
    scale_y = display_height / image.height
    
    html_parts = []
    
    # Container div with image
    html_parts.append(f'''
    <div class="ocr-container" style="position: relative; display: inline-block; width: {display_width}px; height: {display_height}px;">
        <img src="data:image/png;base64,{img_str}"
             style="width: {display_width}px; height: {display_height}px; display: block;"
             alt="Image with OCR detection regions">
    ''')
    
    # Add selectable regions for each text area
    for i, region in enumerate(text_regions):
        if 'bbox_rect' not in region or 'text' not in region:
            continue
            
        x, y, w, h = region['bbox_rect']
        
        # Scale coordinates to display size
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        scaled_w = int(w * scale_x) 
        scaled_h = int(h * scale_y)
        
        confidence = region.get('confidence', 0.0)
        action = region_actions[i] if i < len(region_actions) else 'translate'
        
        # Color and icon based on action
        if action == 'translate':
            border_color = "#22c55e"  # Green for translate
            bg_color = "rgba(34, 197, 94, 0.15)"
            icon = "🌍"
            icon_bg = "#22c55e"
        elif action == 'keep':
            border_color = "#3b82f6"  # Blue for keep
            bg_color = "rgba(59, 130, 246, 0.15)"
            icon = "📝"
            icon_bg = "#3b82f6"
        else:  # remove
            border_color = "#ef4444"  # Red for remove
            bg_color = "rgba(239, 68, 68, 0.15)"
            icon = "🗑️"
            icon_bg = "#ef4444"
        
        # Truncate long text for display
        display_text = region['text'][:30] + "..." if len(region['text']) > 30 else region['text']
        
        html_parts.append(f'''
        <div class="ocr-region ocr-{action}" 
             id="ocr-region-{i}"
             data-region-index="{i}"
             data-action="{action}"
             style="position: absolute; left: {scaled_x}px; top: {scaled_y}px; 
                    width: {scaled_w}px; height: {scaled_h}px;
                    border: 2px solid {border_color};
                    background: {bg_color};
                    cursor: pointer;
                    z-index: 10;
                    transition: all 0.2s ease;"
             onclick="toggleRegionAction({i})"
             title="Action: {action.upper()} | Text: {region['text']} | Confidence: {confidence:.2f} | Click to cycle actions">
            
            <!-- Action indicator -->
            <div style="position: absolute; top: -10px; left: -10px; 
                        width: 20px; height: 20px; 
                        background: {icon_bg}; 
                        border: 2px solid white; 
                        border-radius: 50%;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 10px; color: white; font-weight: bold;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                {icon}
            </div>
            
            <!-- Region number -->
            <div style="position: absolute; top: 2px; right: 2px; 
                        background: rgba(0,0,0,0.8); color: white; 
                        padding: 2px 6px; font-size: 11px; 
                        border-radius: 3px; font-weight: bold;">
                #{i+1}
            </div>
            
            <!-- Confidence indicator -->
            <div style="position: absolute; bottom: 2px; left: 2px; 
                        background: rgba(0,0,0,0.7); color: white; 
                        padding: 1px 4px; font-size: 9px; 
                        border-radius: 2px;">
                {confidence:.0%}
            </div>
        </div>
        ''')
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def create_clickable_image_html(image: Image.Image, text_regions: List[Dict], 
                               image_id: str = "main-image") -> str:
    """
    Create HTML for clickable image with text region overlays.
    
    Args:
        image: PIL Image to display
        text_regions: List of text regions with bounding boxes
        image_id: Unique ID for the image element
        
    Returns:
        HTML string with clickable regions
    """
    # Convert image to base64 for embedding
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Calculate image display dimensions (maintain aspect ratio)
    display_width = min(800, image.width)
    display_height = int(image.height * (display_width / image.width))
    
    # Scale factors for positioning overlays
    scale_x = display_width / image.width
    scale_y = display_height / image.height
    
    # Create HTML structure
    html_parts = []
    
    # Container div with image
    html_parts.append(f'''
    <div class="image-container" id="{image_id}-container" 
         style="width: {display_width}px; height: {display_height}px;">
        <img id="{image_id}" 
             src="data:image/png;base64,{img_str}"
             style="width: {display_width}px; height: {display_height}px; display: block;"
             alt="Translated image with clickable text regions">
    ''')
    
    # Add clickable regions for each text area
    for i, region in enumerate(text_regions):
        if 'bbox_rect' not in region or 'translated_text' not in region:
            continue
            
        x, y, w, h = region['bbox_rect']
        
        # Scale coordinates to display size
        scaled_x = int(x * scale_x)
        scaled_y = int(y * scale_y)
        scaled_w = int(w * scale_x) 
        scaled_h = int(h * scale_y)
        
        # Create region data for JavaScript
        region_data = {
            'index': i,
            'original': region.get('text', ''),
            'translated': region['translated_text'],
            'language': region.get('target_language', 'uk'),
            'confidence': region.get('confidence', 0.0),
            'bbox': [x, y, w, h]
        }
        
        html_parts.append(f'''
        <div class="text-region" 
             id="region-{i}"
             data-region='{json.dumps(region_data)}'
             style="position: absolute; left: {scaled_x}px; top: {scaled_y}px; 
                    width: {scaled_w}px; height: {scaled_h}px; z-index: 100;
                    border: none;
                    background: transparent;
                    cursor: pointer;"
             onmouseover="this.style.border='2px solid rgba(59, 130, 246, 0.8)'; this.style.background='rgba(59, 130, 246, 0.15)'"
             onmouseout="this.style.border='none'; this.style.background='transparent'"
             title="Click to edit • Ctrl+drag to move: {region['translated_text'][:50] if len(region['translated_text']) > 50 else region['translated_text']}">
        </div>
        ''')
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)

def create_control_panel_html() -> str:
    """Create HTML for the floating control panel."""
    return '''
    <div class="control-panel" id="control-panel">
        <div class="control-header">
            <span class="control-title" id="control-title">Edit Text</span>
            <button class="close-btn" onclick="closeControlPanel()">×</button>
        </div>
        
        <div class="text-content" id="text-content">
            <div class="original-text" id="original-text">Original text will appear here</div>
            <div class="translated-text" id="translated-text">Translated text will appear here</div>
        </div>
        
        <div class="control-group">
            <label class="control-label">Font Size</label>
            <div class="size-controls">
                <button class="size-btn" onclick="adjustSize(-0.2)">−</button>
                <span id="size-display">1.0x</span>
                <button class="size-btn" onclick="adjustSize(0.2)">+</button>
            </div>
            <input type="range" class="size-slider" id="size-slider" 
                   min="0.5" max="2.0" step="0.1" value="1.0"
                   oninput="updateSizeFromSlider(this.value)">
        </div>
        
        <div class="control-group">
            <label class="control-label">Edit Text Content</label>
            <textarea class="text-edit-area" id="text-edit-area" 
                     placeholder="Enter text content here..."
                     oninput="updateTextContent(this.value)"></textarea>
        </div>
        
        <div class="control-group">
            <label class="control-label">Font Family</label>
            <select class="font-selector" id="font-selector" onchange="updateFont(this.value)">
                <option value="Default">Default</option>
                <option value="Arial">Arial</option>
                <option value="DejaVu Sans">DejaVu Sans</option>
                <option value="Liberation Sans">Liberation Sans</option>
                <optgroup label="CJK Fonts">
                    <option value="Noto Sans CJK">Noto Sans CJK</option>
                    <option value="Hiragino Sans">Hiragino Sans</option>
                    <option value="Yu Gothic">Yu Gothic</option>
                    <option value="Microsoft YaHei">Microsoft YaHei</option>
                    <option value="SimHei">SimHei</option>
                </optgroup>
                <optgroup label="Cyrillic Fonts">
                    <option value="DejaVu Sans">DejaVu Sans</option>
                    <option value="Liberation Sans">Liberation Sans</option>
                    <option value="Roboto">Roboto</option>
                </optgroup>
            </select>
        </div>
        
        <div class="control-group">
            <label class="control-label">Text Alignment</label>
            <div class="size-controls">
                <button class="size-btn" id="align-left" onclick="updateAlignment('left')">←</button>
                <button class="size-btn" id="align-center" onclick="updateAlignment('center')">■</button>
                <button class="size-btn" id="align-right" onclick="updateAlignment('right')">→</button>
            </div>
        </div>
        
        <div class="control-group">
            <label class="control-label">Text Style</label>
            <div class="size-controls">
                <button class="size-btn" id="style-normal" onclick="updateStyle('normal')">Normal</button>
                <button class="size-btn" id="style-bold" onclick="updateStyle('bold')">Bold</button>
                <button class="size-btn" id="style-italic" onclick="updateStyle('italic')">Italic</button>
            </div>
        </div>
        
        <div class="control-group">
            <label class="control-label">Line Spacing</label>
            <div class="size-controls">
                <button class="size-btn" onclick="adjustLineSpacing(-0.1)">−</button>
                <span id="spacing-display">1.0x</span>
                <button class="size-btn" onclick="adjustLineSpacing(0.1)">+</button>
            </div>
            <input type="range" class="size-slider" id="spacing-slider" 
                   min="0.8" max="2.0" step="0.1" value="1.0"
                   oninput="updateLineSpacingFromSlider(this.value)">
        </div>
        
        <div class="action-buttons">
            <button class="action-btn btn-secondary" onclick="resetRegion()">Reset</button>
            <button class="action-btn btn-primary" onclick="applyChanges()">Apply</button>
        </div>
        
        <div id="status-message"></div>
    </div>
    '''

def create_javascript_handler(current_adjustments: Dict = None) -> str:
    """Create JavaScript for handling interactions."""
    if current_adjustments is None:
        current_adjustments = {}
    
    # Convert adjustments to JavaScript object
    adjustments_js = json.dumps(current_adjustments)
    
    return f'''
    <script>
    let selectedRegion = null;
    let currentAdjustments = {adjustments_js};
    let textRegions = [];
    let updateTimer = null;
    let isDragging = false;
    let dragStartPos = {{ x: 0, y: 0 }};
    let regionStartPos = {{ x: 0, y: 0 }};
    let editMode = false;
    
    function selectTextRegion(regionIndex) {{
        // Remove previous selection
        document.querySelectorAll('.text-region').forEach(el => {{
            el.classList.remove('selected');
        }});
        
        // Select new region
        const regionEl = document.getElementById(`region-${{regionIndex}}`);
        if (!regionEl) return;
        
        regionEl.classList.add('selected');
        selectedRegion = regionIndex;
        
        // Get region data
        const regionData = JSON.parse(regionEl.dataset.region);
        
        // Update control panel
        updateControlPanel(regionData);
        showControlPanel(regionEl);
    }}
    
    function updateControlPanel(regionData) {{
        document.getElementById('original-text').textContent = 
            `Original: ${{regionData.original}}`;
        document.getElementById('translated-text').textContent = 
            `Translation: ${{regionData.translated}}`;
        
        // Reset controls to current values
        const currentAdj = currentAdjustments[selectedRegion] || {{}};
        const sizeMultiplier = currentAdj.font_size_multiplier || 1.0;
        const fontFamily = currentAdj.font_family || 'Default';
        const textContent = currentAdj.text_content || regionData.translated;
        const alignment = currentAdj.text_alignment || 'center';
        
        // Update text edit area
        document.getElementById('text-edit-area').value = textContent;
        
        // Update other controls
        document.getElementById('size-slider').value = sizeMultiplier;
        document.getElementById('size-display').textContent = `${{sizeMultiplier.toFixed(1)}}x`;
        document.getElementById('font-selector').value = fontFamily;
        
        // Update alignment buttons
        document.querySelectorAll('[id^="align-"]').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`align-${{alignment}}`).classList.add('active');
        
        // Update style buttons
        const textStyle = currentAdj.text_style || 'normal';
        document.querySelectorAll('[id^="style-"]').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`style-${{textStyle}}`).classList.add('active');
        
        // Update line spacing
        const lineSpacing = currentAdj.line_spacing || 1.0;
        document.getElementById('spacing-slider').value = lineSpacing;
        document.getElementById('spacing-display').textContent = `${{lineSpacing.toFixed(1)}}x`;
    }}
    
    function showControlPanel(regionEl) {{
        const panel = document.getElementById('control-panel');
        const rect = regionEl.getBoundingClientRect();
        
        // Position panel near the selected region
        let left = rect.right + 20;
        let top = rect.top;
        
        // Adjust if panel would go off screen
        if (left + 320 > window.innerWidth) {{
            left = rect.left - 340;
        }}
        if (top + 400 > window.innerHeight) {{
            top = Math.max(20, window.innerHeight - 420);
        }}
        
        panel.style.left = `${{left}}px`;
        panel.style.top = `${{top}}px`;
        panel.classList.add('visible');
    }}
    
    function closeControlPanel() {{
        document.getElementById('control-panel').classList.remove('visible');
        document.querySelectorAll('.text-region').forEach(el => {{
            el.classList.remove('selected');
        }});
        selectedRegion = null;
    }}
    
    function adjustSize(delta) {{
        const slider = document.getElementById('size-slider');
        const newValue = Math.max(0.5, Math.min(2.0, 
            parseFloat(slider.value) + delta));
        slider.value = newValue;
        updateSizeFromSlider(newValue);
    }}
    
    function updateSizeFromSlider(value) {{
        const size = parseFloat(value);
        document.getElementById('size-display').textContent = `${{size.toFixed(1)}}x`;
        
        if (selectedRegion !== null) {{
            if (!currentAdjustments[selectedRegion]) {{
                currentAdjustments[selectedRegion] = {{}};
            }}
            currentAdjustments[selectedRegion].font_size_multiplier = size;
            scheduleUpdate();
        }}
    }}
    
    function updateFont(fontFamily) {{
        if (selectedRegion !== null) {{
            if (!currentAdjustments[selectedRegion]) {{
                currentAdjustments[selectedRegion] = {{}};
            }}
            currentAdjustments[selectedRegion].font_family = fontFamily;
            scheduleUpdate();
        }}
    }}
    
    function updateTextContent(textContent) {{
        if (selectedRegion !== null) {{
            if (!currentAdjustments[selectedRegion]) {{
                currentAdjustments[selectedRegion] = {{}};
            }}
            currentAdjustments[selectedRegion].text_content = textContent;
            scheduleUpdate();
        }}
    }}
    
    function updateAlignment(alignment) {{
        if (selectedRegion !== null) {{
            if (!currentAdjustments[selectedRegion]) {{
                currentAdjustments[selectedRegion] = {{}};
            }}
            currentAdjustments[selectedRegion].text_alignment = alignment;
            
            // Update button states
            document.querySelectorAll('[id^="align-"]').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`align-${{alignment}}`).classList.add('active');
            
            scheduleUpdate();
        }}
    }}
    
    function updateStyle(style) {{
        if (selectedRegion !== null) {{
            if (!currentAdjustments[selectedRegion]) {{
                currentAdjustments[selectedRegion] = {{}};
            }}
            currentAdjustments[selectedRegion].text_style = style;
            
            // Update button states
            document.querySelectorAll('[id^="style-"]').forEach(btn => btn.classList.remove('active'));
            document.getElementById(`style-${{style}}`).classList.add('active');
            
            scheduleUpdate();
        }}
    }}
    
    function adjustLineSpacing(delta) {{
        const slider = document.getElementById('spacing-slider');
        const newValue = Math.max(0.8, Math.min(2.0, 
            parseFloat(slider.value) + delta));
        slider.value = newValue;
        updateLineSpacingFromSlider(newValue);
    }}
    
    function updateLineSpacingFromSlider(value) {{
        const spacing = parseFloat(value);
        document.getElementById('spacing-display').textContent = `${{spacing.toFixed(1)}}x`;
        
        if (selectedRegion !== null) {{
            if (!currentAdjustments[selectedRegion]) {{
                currentAdjustments[selectedRegion] = {{}};
            }}
            currentAdjustments[selectedRegion].line_spacing = spacing;
            scheduleUpdate();
        }}
    }}
    
    function scheduleUpdate() {{
        // Debounce updates to avoid too many requests
        if (updateTimer) {{
            clearTimeout(updateTimer);
        }}
        updateTimer = setTimeout(() => {{
            triggerStreamlitUpdate();
        }}, 500); // Wait 500ms after user stops adjusting
    }}
    
    function triggerStreamlitUpdate() {{
        // Store adjustments in a hidden input for Streamlit to read
        const hiddenInput = document.getElementById('adjustments-input');
        if (hiddenInput) {{
            hiddenInput.value = JSON.stringify(currentAdjustments);
            hiddenInput.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}
    }}
    
    // Drag and drop functionality
    function initializeDragAndDrop() {{
        document.querySelectorAll('.text-region').forEach(region => {{
            region.onmousedown = startDrag;
            region.ondragstart = function() {{ return false; }}; // Prevent default drag
        }});
    }}
    
    function startDrag(e) {{
        if (e.ctrlKey || e.metaKey) {{ // Only drag when Ctrl/Cmd is held
            e.preventDefault();
            isDragging = true;
            const regionIndex = parseInt(e.target.id.split('-')[1]);
            selectedRegion = regionIndex;
            
            dragStartPos.x = e.clientX;
            dragStartPos.y = e.clientY;
            
            const rect = e.target.getBoundingClientRect();
            regionStartPos.x = rect.left;
            regionStartPos.y = rect.top;
            
            e.target.classList.add('dragging');
            document.onmousemove = drag;
            document.onmouseup = stopDrag;
            
            showStatusMessage('Drag to reposition text (Ctrl+drag)', 'success');
        }} else {{
            // Normal click to select
            const regionIndex = parseInt(e.target.id.split('-')[1]);
            selectTextRegion(regionIndex);
        }}
    }}
    
    function drag(e) {{
        if (!isDragging) return;
        
        const deltaX = e.clientX - dragStartPos.x;
        const deltaY = e.clientY - dragStartPos.y;
        
        const regionEl = document.getElementById(`region-${{selectedRegion}}`);
        if (regionEl) {{
            const newX = regionStartPos.x + deltaX;
            const newY = regionStartPos.y + deltaY;
            
            // Update position immediately for visual feedback
            regionEl.style.left = `${{newX}}px`;
            regionEl.style.top = `${{newY}}px`;
        }}
    }}
    
    function stopDrag(e) {{
        if (!isDragging) return;
        
        isDragging = false;
        document.onmousemove = null;
        document.onmouseup = null;
        
        const regionEl = document.getElementById(`region-${{selectedRegion}}`);
        if (regionEl) {{
            regionEl.classList.remove('dragging');
            
            // Calculate new position relative to image
            const imageContainer = document.querySelector('.image-container');
            const containerRect = imageContainer.getBoundingClientRect();
            const regionRect = regionEl.getBoundingClientRect();
            
            const relativeX = regionRect.left - containerRect.left;
            const relativeY = regionRect.top - containerRect.top;
            
            // Store position adjustment
            if (!currentAdjustments[selectedRegion]) {{
                currentAdjustments[selectedRegion] = {{}};
            }}
            currentAdjustments[selectedRegion].position_x = relativeX;
            currentAdjustments[selectedRegion].position_y = relativeY;
            
            scheduleUpdate();
            showStatusMessage('Position updated!', 'success');
        }}
    }}
    
    function resetRegion() {{
        if (selectedRegion !== null) {{
            delete currentAdjustments[selectedRegion];
            
            // Reset UI controls
            document.getElementById('size-slider').value = 1.0;
            document.getElementById('size-display').textContent = '1.0x';
            document.getElementById('font-selector').value = 'Default';
            document.getElementById('text-edit-area').value = '';
            
            // Reset alignment
            document.querySelectorAll('[id^="align-"]').forEach(btn => btn.classList.remove('active'));
            document.getElementById('align-center').classList.add('active');
            
            // Reset style
            document.querySelectorAll('[id^="style-"]').forEach(btn => btn.classList.remove('active'));
            document.getElementById('style-normal').classList.add('active');
            
            // Reset line spacing
            document.getElementById('spacing-slider').value = 1.0;
            document.getElementById('spacing-display').textContent = '1.0x';
            
            showStatusMessage('Region reset to defaults', 'success');
            triggerStreamlitUpdate();
        }}
    }}
    
    function applyChanges() {{
        if (selectedRegion !== null) {{
            showStatusMessage('Changes applied!', 'success');
            triggerStreamlitUpdate();
            
            setTimeout(() => {{
                closeControlPanel();
            }}, 1000);
        }}
    }}
    
    function showStatusMessage(message, type) {{
        const statusEl = document.getElementById('status-message');
        statusEl.textContent = message;
        statusEl.className = `status-indicator status-${{type}}`;
        
        setTimeout(() => {{
            statusEl.textContent = '';
            statusEl.className = '';
        }}, 3000);
    }}
    
    // Close panel when clicking outside
    document.addEventListener('click', function(e) {{
        if (!e.target.closest('.control-panel') && 
            !e.target.closest('.text-region')) {{
            closeControlPanel();
        }}
    }});
    
    // Initialize drag and drop when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {{
        initializeDragAndDrop();
    }});
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {{
        if (selectedRegion !== null) {{
            if (e.key === 'Escape') {{
                closeControlPanel();
            }} else if (e.key === '+' || e.key === '=') {{
                e.preventDefault();
                adjustSize(0.1);
            }} else if (e.key === '-') {{
                e.preventDefault();
                adjustSize(-0.1);
            }} else if (e.key === 'Enter' && e.ctrlKey) {{
                e.preventDefault();
                applyChanges();
            }}
        }}
    }});
    
    // Re-initialize drag handlers after content updates
    window.reinitializeDragHandlers = function() {{
        setTimeout(initializeDragAndDrop, 100);
    }};
    
    // Global variable to track current actions
    window.currentRegionActions = [];
    
    // Update Streamlit input with current actions
    window.updateRegionActions = function(actions) {{
        console.log('updateRegionActions called with:', actions);
        window.currentRegionActions = actions;
        
        // Find and update the Streamlit input
        const streamlitInputs = document.querySelectorAll('input[type="text"]');
        for (let input of streamlitInputs) {{
            if (input.value && (input.value.includes('translate') || input.value.includes('keep') || input.value.includes('remove'))) {{
                input.value = JSON.stringify(actions);
                input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                break;
            }}
        }}
    }};
    
    // Simplified updateStreamlitActions - just reads DOM and updates state
    window.updateStreamlitActions = function() {{
        const allRegions = document.querySelectorAll('.ocr-region');
        const actions = [];
        
        allRegions.forEach((region, index) => {{
            const action = region.getAttribute('data-action') || 'translate';
            actions.push(action);
        }});
        
        window.updateRegionActions(actions);
    }};
    </script>
    '''

def create_ocr_visualization(image: Image.Image, text_regions: List[Dict]) -> Image.Image:
    """Create visualization of OCR detection with bounding boxes."""
    vis_image = image.copy()
    draw = ImageDraw.Draw(vis_image)
    
    for i, region in enumerate(text_regions):
        if 'bbox_rect' in region:
            x, y, w, h = region['bbox_rect']
            # Draw bounding box
            draw.rectangle([x, y, x + w, y + h], outline='red', width=3)
            # Add region number
            draw.text((x, y - 20), f"{i+1}", fill='red')
            # Add confidence score
            confidence = region.get('confidence', 0.0)
            draw.text((x, y + h + 5), f"{confidence:.2f}", fill='blue')
    
    return vis_image

def create_step_visualization(step_name: str, status: str, image: Image.Image = None, 
                            stats: Dict = None, progress: int = 0) -> str:
    """Create HTML for a processing step visualization."""
    status_icons = {
        'pending': '⏳',
        'processing': '🔄',
        'completed': '✅',
        'error': '❌'
    }
    
    icon = status_icons.get(status, '⏳')
    
    image_html = ""
    if image:
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        image_html = f'<img class="step-image" src="data:image/png;base64,{img_str}" alt="{step_name} result">'
    
    stats_html = ""
    if stats:
        stats_items = [f"<span>{k}: {v}</span>" for k, v in stats.items()]
        stats_html = f'<div class="step-stats">{"".join(stats_items)}</div>'
    
    progress_html = ""
    if progress > 0:
        progress_html = f'''
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
        </div>
        '''
    
    return f'''
    <div class="processing-step {status}">
        <div class="step-header">
            <span class="step-title">{step_name}</span>
            <span class="step-status">{icon}</span>
        </div>
        <div class="step-content">
            {image_html}
            {stats_html}
            {progress_html}
        </div>
    </div>
    '''

def process_image_with_translation(image: Image.Image, target_lang: str, engines: tuple, 
                                 progress_callback=None) -> Dict:
    """Process image through complete translation pipeline with step-by-step tracking."""
    ocr_engine, translation_engine, image_processor = engines
    
    result = {
        'success': False,
        'original_image': image,
        'ocr_visualization': None,
        'inpainted_image': None,
        'final_image': None,
        'inpainted_base': None,
        'text_regions': [],
        'processing_steps': {},
        'total_processing_time': 0,
        'error': None
    }
    
    start_time = time.time()
    
    try:
        # Step 1: Validate and resize image
        step_start = time.time()
        if progress_callback:
            progress_callback("Validating image...", 0)
        
        is_valid, error_msg = validate_image(image)
        if not is_valid:
            result['error'] = error_msg
            return result
        
        processed_image, scale_factor = image_processor.resize_for_processing(image)
        result['processing_steps']['validation'] = {
            'time': time.time() - step_start,
            'scale_factor': scale_factor
        }
        
        # Step 2: OCR text detection
        step_start = time.time()
        if progress_callback:
            progress_callback("Detecting text regions...", 25)
        
        text_regions = ocr_engine.get_text_regions(processed_image)
        if not text_regions:
            result['error'] = "No text detected in image"
            return result
        
        # Create OCR visualization
        ocr_vis = create_ocr_visualization(processed_image, text_regions)
        result['processing_steps']['ocr'] = {
            'time': time.time() - step_start,
            'regions_detected': len(text_regions)
        }
        
        # Step 3: Translate text based on region actions
        step_start = time.time()
        if progress_callback:
            progress_callback("Processing text regions...", 50)
        
        # Process regions based on their actions (translate, keep, remove)
        texts_to_translate = []
        translate_indices = []
        
        for i, region in enumerate(text_regions):
            action = region.get('action', 'translate')  # Default to translate for backwards compatibility
            
            if action == 'translate':
                texts_to_translate.append(region['text'])
                translate_indices.append(i)
            elif action == 'keep':
                # Keep original text, mark as processed
                region['translated_text'] = region['text']
                region['translation_quality'] = 1.0  # Original text has perfect "quality"
                region['target_language'] = target_lang
                region['action_taken'] = 'kept_original'
            elif action == 'remove':
                # Mark for removal - no text will be rendered
                region['translated_text'] = ''
                region['translation_quality'] = 0.0
                region['target_language'] = target_lang
                region['should_remove'] = True
                region['action_taken'] = 'removed'
        
        # Only translate regions marked for translation
        if texts_to_translate:
            translations = translation_engine.translate_batch(texts_to_translate, target_lang)
            
            # Apply translations back to the correct regions
            for idx, (translated_text, quality) in enumerate(translations):
                if idx < len(translate_indices):
                    region_idx = translate_indices[idx]
                    text_regions[region_idx]['translated_text'] = translated_text
                    text_regions[region_idx]['translation_quality'] = quality
                    text_regions[region_idx]['target_language'] = target_lang
                    text_regions[region_idx]['action_taken'] = 'translated'
        
        # Count regions by action for statistics
        action_counts = {
            'translated': len(translate_indices),
            'kept': len([r for r in text_regions if r.get('action') == 'keep']),
            'removed': len([r for r in text_regions if r.get('action') == 'remove'])
        }
        
        result['processing_steps']['translation'] = {
            'time': time.time() - step_start,
            'texts_translated': action_counts['translated'],
            'texts_kept': action_counts['kept'],
            'texts_removed': action_counts['removed'],
            'total_regions': len(text_regions)
        }
        
        # Step 4: Create inpainting mask and inpaint
        step_start = time.time()
        if progress_callback:
            progress_callback("Processing image regions...", 75)
        
        # Create mask only for regions that need inpainting (translate + remove)
        regions_to_inpaint = [
            region for region in text_regions 
            if region.get('action', 'translate') in ['translate', 'remove']
        ]
        
        if regions_to_inpaint:
            mask = image_processor.create_enhanced_mask(processed_image, regions_to_inpaint)
            inpainted_image = image_processor.enhanced_inpainting(processed_image, mask)
        else:
            # No regions need inpainting, use original image
            inpainted_image = processed_image.copy()
        
        result['processing_steps']['inpainting'] = {
            'time': time.time() - step_start,
            'regions_inpainted': len(regions_to_inpaint),
            'mask_coverage': np.sum(np.array(mask) > 0) / (mask.width * mask.height) if regions_to_inpaint else 0.0
        }
        
        # Step 5: Add text to get final result (only for translate and keep actions)
        step_start = time.time()
        if progress_callback:
            progress_callback("Rendering final text...", 95)
        
        # Only render text for regions that should have text (not removed regions)
        regions_to_render = [
            region for region in text_regions 
            if region.get('action', 'translate') != 'remove' and region.get('translated_text', '')
        ]
        
        final_image = image_processor.add_translated_text(inpainted_image, regions_to_render)
        
        result['processing_steps']['text_rendering'] = {
            'time': time.time() - step_start,
            'texts_rendered': len(regions_to_render)
        }
        
        # Scale back to original size if needed
        if scale_factor != 1.0:
            final_size = (
                int(final_image.width / scale_factor),
                int(final_image.height / scale_factor)
            )
            final_image = final_image.resize(final_size, Image.Resampling.LANCZOS)
            inpainted_image = inpainted_image.resize(final_size, Image.Resampling.LANCZOS)
            ocr_vis = ocr_vis.resize(final_size, Image.Resampling.LANCZOS)
            
            # Scale text regions back to original coordinates
            for region in text_regions:
                x, y, w, h = region['bbox_rect']
                region['bbox_rect'] = (
                    int(x / scale_factor),
                    int(y / scale_factor), 
                    int(w / scale_factor),
                    int(h / scale_factor)
                )
        
        if progress_callback:
            progress_callback("Complete!", 100)
        
        result.update({
            'success': True,
            'ocr_visualization': ocr_vis,
            'inpainted_image': inpainted_image,
            'final_image': final_image,
            'inpainted_base': inpainted_image,  # Base for editing
            'text_regions': text_regions,
            'total_processing_time': time.time() - start_time
        })
        
        logger.info(f"Image processed successfully in {result['total_processing_time']:.2f}s")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        result['error'] = str(e)
        result['total_processing_time'] = time.time() - start_time
    
    return result

def main():
    """Main application."""
    
    # Load engines
    engines = load_engines()
    
    # Header
    st.title("✏️ Direct Text Editor")
    st.markdown("**Click directly on text in the image to edit it!** Just like Google Slides or other visual editors.")
    
    # Initialize session state
    if 'text_adjustments' not in st.session_state:
        st.session_state['text_adjustments'] = {}
    if 'processing_result' not in st.session_state:
        st.session_state['processing_result'] = None
    
    # Main interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🌍 Upload & Translate")
        st.write("")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload an image containing text to translate"
        )
        
        st.write("")
        st.write("")
        
        # Language selection
        languages = {
            'uk': '🇺🇦 Українська (Ukrainian)',
            'en': '🇺🇸 English',
            'es': '🇪🇸 Español (Spanish)', 
            'fr': '🇫🇷 Français (French)',
            'de': '🇩🇪 Deutsch (German)',
            'it': '🇮🇹 Italiano (Italian)',
            'pt': '🇵🇹 Português (Portuguese)',
            'ru': '🇷🇺 Русский (Russian)',
            'ja': '🇯🇵 日本語 (Japanese)',
            'ko': '🇰🇷 한국어 (Korean)',
            'zh': '🇨🇳 中文 (Chinese)'
        }
        
        target_lang = st.selectbox(
            "Target Language",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=0
        )
        
        st.write("")
        st.write("")
        
        # Process button
        if st.button("🚀 Translate Image", type="primary", use_container_width=True):
            if uploaded_file:
                with st.spinner("Processing image..."):
                    image = Image.open(uploaded_file)
                    
                    # Apply region actions if they exist
                    def apply_region_actions(result):
                        if 'region_actions' in st.session_state and result['success']:
                            for i, region in enumerate(result['text_regions']):
                                if i < len(st.session_state['region_actions']):
                                    region['action'] = st.session_state['region_actions'][i]
                        return result
                    
                    result = process_image_with_translation(image, target_lang, engines)
                    result = apply_region_actions(result)
                    
                    st.session_state['processing_result'] = result
                    st.session_state['target_lang'] = target_lang
                    st.session_state['text_adjustments'] = {}  # Reset adjustments
                    st.rerun()
            else:
                st.warning("Please upload an image first.")
        
        st.write("")
        st.divider()
        st.write("")
        
        # Show processing stats if available
        if st.session_state['processing_result']:
            result = st.session_state['processing_result']
            if result['success']:
                st.success("✅ Translation complete!")
                st.metric("Text Regions", len(result['text_regions']))
                st.metric("Total Processing Time", f"{result['total_processing_time']:.1f}s")
                
                st.write("")
                
                # Show step-by-step timing breakdown
                if 'processing_steps' in result:
                    with st.expander("⏱️ Processing Breakdown", expanded=False):
                        if 'ocr' in result['processing_steps']:
                            st.write(f"🔍 OCR Detection: {result['processing_steps']['ocr']['time']:.1f}s")
                        if 'translation' in result['processing_steps']:
                            st.write(f"🌍 Translation: {result['processing_steps']['translation']['time']:.1f}s")
                        if 'inpainting' in result['processing_steps']:
                            st.write(f"🎨 Text Removal: {result['processing_steps']['inpainting']['time']:.1f}s")
                        if 'text_rendering' in result['processing_steps']:
                            st.write(f"✏️ Text Rendering: {result['processing_steps']['text_rendering']['time']:.1f}s")
            else:
                st.error(f"❌ Processing failed: {result['error']}")
    
    with col2:
        if st.session_state['processing_result']:
            result = st.session_state['processing_result']
            
            if result['success']:
                # Create interactive step tabs
                step_tabs = st.tabs(["Original", "OCR Detection", "Text Removal", "Final Result"])
                
                with step_tabs[0]:
                    st.markdown("**Original uploaded image**")
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.image(result['original_image'], caption="Original Image", use_container_width=True)
                    with col2:
                        st.metric("Width", f"{result['original_image'].width} px")
                        st.metric("Height", f"{result['original_image'].height} px")
                        if 'processing_steps' in result and 'validation' in result['processing_steps']:
                            st.metric("Scale Factor", f"{result['processing_steps']['validation']['scale_factor']:.2f}")
                
                with step_tabs[1]:
                    st.markdown("**Interactive OCR Region Control** - Choose action for each text region")
                    
                    # Initialize region actions state (3-state system)
                    if 'region_actions' not in st.session_state:
                        st.session_state['region_actions'] = ['translate'] * len(result['text_regions'])
                    
                    # Ensure region_actions matches the number of text regions
                    while len(st.session_state['region_actions']) < len(result['text_regions']):
                        st.session_state['region_actions'].append('translate')
                    if len(st.session_state['region_actions']) > len(result['text_regions']):
                        st.session_state['region_actions'] = st.session_state['region_actions'][:len(result['text_regions'])]
                    
                    # Control buttons for 3-state system
                    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                    
                    with col_btn1:
                        if st.button("🌍 Translate All", key="translate_all_regions"):
                            st.session_state['region_actions'] = ['translate'] * len(result['text_regions'])
                            st.success(f"Set all {len(result['text_regions'])} regions to TRANSLATE")
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("📝 Keep All", key="keep_all_regions"):
                            st.session_state['region_actions'] = ['keep'] * len(result['text_regions'])
                            st.success(f"Set all {len(result['text_regions'])} regions to KEEP")
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("🗑️ Remove All", key="remove_all_regions"):
                            st.session_state['region_actions'] = ['remove'] * len(result['text_regions'])
                            st.success(f"Set all {len(result['text_regions'])} regions to REMOVE")
                            st.rerun()
                    
                    with col_btn4:
                        # Count actions
                        translate_count = st.session_state['region_actions'].count('translate')
                        keep_count = st.session_state['region_actions'].count('keep')
                        remove_count = st.session_state['region_actions'].count('remove')
                        st.metric("Actions", f"🌍{translate_count} 📝{keep_count} 🗑️{remove_count}")
                    
                    # Interactive OCR visualization with 3-state system
                    ocr_html = create_ocr_visualization_html_3state(
                        result['original_image'], 
                        result['text_regions'],
                        st.session_state['region_actions']
                    )
                    
                    # JavaScript for 3-state region toggling
                    ocr_js = '''
                    <script>
                    function toggleRegionAction(regionIndex) {
                        console.log('=== toggleRegionAction START ===', regionIndex);
                        
                        const regionEl = document.getElementById('ocr-region-' + regionIndex);
                        if (!regionEl) {
                            console.error('Region element not found:', regionIndex);
                            return;
                        }
                        
                        // Get current action from data attribute
                        const currentAction = regionEl.getAttribute('data-action');
                        console.log('Current action:', currentAction);
                        
                        // Cycle through actions: translate -> keep -> remove -> translate
                        let newAction;
                        if (currentAction === 'translate') {
                            newAction = 'keep';
                        } else if (currentAction === 'keep') {
                            newAction = 'remove';
                        } else {
                            newAction = 'translate';
                        }
                        console.log('New action:', newAction);
                        
                        // STEP 1: Update data-action attribute FIRST
                        regionEl.setAttribute('data-action', newAction);
                        console.log('Updated data-action attribute to:', newAction);
                        
                        // STEP 2: Update visual appearance
                        updateRegionVisuals(regionEl, newAction, regionIndex);
                        
                        // STEP 3: Update global state with proper timing
                        setTimeout(() => {
                            updateGlobalState(regionIndex, newAction);
                        }, 10);
                        
                        console.log('=== toggleRegionAction END ===');
                    }
                    
                    function updateRegionVisuals(regionEl, newAction, regionIndex) {
                        console.log('Updating visuals for region', regionIndex, 'to', newAction);
                        
                        // Update CSS class
                        regionEl.className = 'ocr-region ocr-' + newAction;
                        
                        // Update colors and icon based on new action
                        let borderColor, bgColor, icon, iconBg;
                        if (newAction === 'translate') {
                            borderColor = '#22c55e';
                            bgColor = 'rgba(34, 197, 94, 0.15)';
                            icon = '🌍';
                            iconBg = '#22c55e';
                        } else if (newAction === 'keep') {
                            borderColor = '#3b82f6';
                            bgColor = 'rgba(59, 130, 246, 0.15)';
                            icon = '📝';
                            iconBg = '#3b82f6';
                        } else { // remove
                            borderColor = '#ef4444';
                            bgColor = 'rgba(239, 68, 68, 0.15)';
                            icon = '🗑️';
                            iconBg = '#ef4444';
                        }
                        
                        regionEl.style.borderColor = borderColor;
                        regionEl.style.background = bgColor;
                        
                        // Update action indicator
                        const actionIndicator = regionEl.children[0];
                        if (actionIndicator) {
                            actionIndicator.style.background = iconBg;
                            actionIndicator.textContent = icon;
                        }
                        
                        // Update title
                        const titleParts = regionEl.title.split(' | ');
                        regionEl.title = 'Action: ' + newAction.toUpperCase() + ' | ' + titleParts.slice(1).join(' | ');
                        
                        console.log('Visual update complete for region', regionIndex);
                    }
                    
                    function updateGlobalState(regionIndex, newAction) {
                        console.log('=== updateGlobalState START ===', regionIndex, newAction);
                        
                        // Read ALL current data-action attributes to build complete state
                        const allRegions = document.querySelectorAll('.ocr-region');
                        const actions = [];
                        
                        allRegions.forEach((region, index) => {
                            const action = region.getAttribute('data-action') || 'translate';
                            actions.push(action);
                            console.log('Region', index, 'data-action:', action);
                        });
                        
                        console.log('Complete actions array:', actions);
                        
                        // Update global state
                        if (window.updateRegionActions) {
                            window.updateRegionActions(actions);
                        } else {
                            console.error('window.updateRegionActions not found');
                        }
                        
                        console.log('=== updateGlobalState END ===');
                    }
                    </script>
                    '''
                    
                    # Display interactive OCR
                    st.components.v1.html(ocr_html + ocr_js, height=400)
                    
                    # Debug display - show current actions
                    with st.expander("🔍 Debug: Current Region Actions", expanded=False):
                        for i, action in enumerate(st.session_state['region_actions']):
                            region_text = result['text_regions'][i]['text'][:30] if i < len(result['text_regions']) else "N/A"
                            st.write(f"Region {i}: **{action}** - '{region_text}...'")
                    
                    # Hidden input for region actions with explicit ID
                    region_actions_json = st.text_input(
                        "region-actions",
                        value=json.dumps(st.session_state['region_actions']),
                        key="region_actions_input",
                        label_visibility="hidden",
                        help="JavaScript communication channel"
                    )
                    
                    
                    # Update actions
                    try:
                        new_actions = json.loads(region_actions_json)
                        if new_actions != st.session_state['region_actions']:
                            st.session_state['region_actions'] = new_actions
                            st.rerun()
                    except:
                        pass
                    
                    # Reprocess button to apply region actions
                    st.write("")
                    if st.button("🔄 Apply Actions & Reprocess", key="reprocess_with_actions", type="secondary"):
                        if result['success']:
                            with st.spinner("Reprocessing with your actions..."):
                                # Apply current region actions to existing text regions
                                for i, region in enumerate(result['text_regions']):
                                    if i < len(st.session_state['region_actions']):
                                        action = st.session_state['region_actions'][i]
                                        region['action'] = action
                                        
                                        # Update region data based on action
                                        if action == 'keep':
                                            region['translated_text'] = region['text']  # Keep original
                                            region['translation_quality'] = 1.0
                                            region['action_taken'] = 'kept_original'
                                        elif action == 'remove':
                                            region['translated_text'] = ''  # Remove text
                                            region['translation_quality'] = 0.0
                                            region['should_remove'] = True
                                            region['action_taken'] = 'removed'
                                        # translate action keeps existing translation
                                
                                # Reprocess only the image rendering part
                                try:
                                    # Get engines
                                    ocr_engine, translation_engine, image_processor = engines
                                    processed_image, scale_factor = image_processor.resize_for_processing(result['original_image'])
                                    
                                    # Create mask only for regions that need inpainting (translate + remove)
                                    regions_to_inpaint = [
                                        region for region in result['text_regions'] 
                                        if region.get('action', 'translate') in ['translate', 'remove']
                                    ]
                                    
                                    if regions_to_inpaint:
                                        mask = image_processor.create_enhanced_mask(processed_image, regions_to_inpaint)
                                        inpainted_image = image_processor.enhanced_inpainting(processed_image, mask)
                                    else:
                                        inpainted_image = processed_image.copy()
                                    
                                    # Only render text for regions that should have text (not removed regions)
                                    regions_to_render = [
                                        region for region in result['text_regions'] 
                                        if region.get('action', 'translate') != 'remove' and region.get('translated_text', '')
                                    ]
                                    
                                    final_image = image_processor.add_translated_text(inpainted_image, regions_to_render)
                                    
                                    # Scale back to original size if needed
                                    if scale_factor != 1.0:
                                        final_size = (
                                            int(final_image.width / scale_factor),
                                            int(final_image.height / scale_factor)
                                        )
                                        final_image = final_image.resize(final_size, Image.Resampling.LANCZOS)
                                        inpainted_image = inpainted_image.resize(final_size, Image.Resampling.LANCZOS)
                                    
                                    # Update result with new images
                                    result['inpainted_image'] = inpainted_image
                                    result['final_image'] = final_image
                                    result['inpainted_base'] = inpainted_image
                                    
                                    # Update session state
                                    st.session_state['processing_result'] = result
                                    st.success(f"✅ Reprocessed with actions: {len([r for r in result['text_regions'] if r.get('action') == 'translate'])} translated, {len([r for r in result['text_regions'] if r.get('action') == 'keep'])} kept, {len([r for r in result['text_regions'] if r.get('action') == 'remove'])} removed")
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"Error during reprocessing: {e}")
                                    logger.error(f"Reprocessing error: {e}")
                                    
                
                with step_tabs[2]:
                    if result.get('inpainted_image'):
                        st.image(result['inpainted_image'], caption="Text Removed (Clean base for translation)", use_container_width=True)
                    else:
                        st.error("Inpainted image not available")
                
                with step_tabs[3]:
                    # Generate current preview image
                    ocr_engine, translation_engine, image_processor = engines
                    if st.session_state['text_adjustments']:
                        current_image = image_processor.render_text_with_adjustments(
                            result['inpainted_base'],
                            result['text_regions'],
                            st.session_state['text_adjustments']
                        )
                        st.image(current_image, caption="Final Result (with your edits)", use_container_width=True)
                    else:
                        current_image = result['final_image']
                        st.image(current_image, caption="Final Translated Result", use_container_width=True)
                
                st.divider()
                st.subheader("🎨 Click on text to edit it")
                
                # Hidden input for receiving adjustments from JavaScript
                adjustments_json = st.text_input(
                    "adjustments",
                    value=json.dumps(st.session_state['text_adjustments']),
                    key="adjustments_input",
                    label_visibility="hidden"
                )
                
                # Parse adjustments if they changed
                try:
                    new_adjustments = json.loads(adjustments_json)
                    if new_adjustments != st.session_state['text_adjustments']:
                        st.session_state['text_adjustments'] = new_adjustments
                        st.rerun()
                except (json.JSONDecodeError, TypeError):
                    pass
                
                # Create the interactive image with clickable regions
                clickable_html = create_clickable_image_html(
                    current_image, 
                    result['text_regions']
                )
                
                # Create control panel HTML
                control_panel_html = create_control_panel_html()
                
                # JavaScript handler with current adjustments
                js_handler = create_javascript_handler(st.session_state['text_adjustments'])
                
                # Add hidden input reference in JavaScript with enhanced connectivity
                hidden_input_html = '''
                <input type="hidden" id="adjustments-input" />
                <script>
                // Enhanced Streamlit connectivity with retry logic
                function connectToStreamlit() {
                    const streamlitInput = document.querySelector('input[data-testid="stTextInput-adjustments"]') ||
                                         document.querySelector('input[data-baseweb="input"][aria-label="adjustments"]') ||
                                         document.querySelector('input[type="text"][style*="display: none"]');
                    const hiddenInput = document.getElementById('adjustments-input');
                    
                    if (streamlitInput && hiddenInput && !hiddenInput.connected) {
                        hiddenInput.connected = true;
                        console.log('Connected to Streamlit input');
                        
                        hiddenInput.addEventListener('change', function() {
                            streamlitInput.value = this.value;
                            streamlitInput.dispatchEvent(new Event('input', { bubbles: true }));
                            streamlitInput.dispatchEvent(new Event('change', { bubbles: true }));
                        });
                        
                        // Also trigger on keyup for immediate response
                        hiddenInput.addEventListener('keyup', function() {
                            streamlitInput.value = this.value;
                            streamlitInput.dispatchEvent(new Event('input', { bubbles: true }));
                        });
                        
                        return true;
                    }
                    return false;
                }
                
                // Try connecting immediately and with retries
                document.addEventListener('DOMContentLoaded', function() {
                    if (!connectToStreamlit()) {
                        // Retry connection with MutationObserver
                        const observer = new MutationObserver(function(mutations) {
                            if (connectToStreamlit()) {
                                observer.disconnect();
                            }
                        });
                        observer.observe(document.body, { childList: true, subtree: true });
                        
                        // Stop trying after 10 seconds
                        setTimeout(() => observer.disconnect(), 10000);
                    }
                });
                
                // Reinitialize after Streamlit reruns
                window.addEventListener('streamlit:render', function() {
                    setTimeout(connectToStreamlit, 100);
                });
                </script>
                '''
                
                # Combine all HTML and display with enhanced initialization
                full_html = f'''
                <div class="main-container">
                    {clickable_html}
                    {control_panel_html}
                    {hidden_input_html}
                </div>
                {js_handler}
                <script>
                // Ensure initialization after HTML is loaded
                setTimeout(function() {{
                    if (window.reinitializeDragHandlers) {{
                        window.reinitializeDragHandlers();
                    }}
                    connectToStreamlit();
                }}, 500);
                </script>
                '''
                
                st.components.v1.html(full_html, height=650, scrolling=False)
                
                # Show adjustment status
                if st.session_state['text_adjustments']:
                    adjustment_count = len(st.session_state['text_adjustments'])
                    st.success(f"✨ Applied {adjustment_count} text adjustment(s)")
                    
                    # Show details of adjustments
                    with st.expander("📋 Current Adjustments", expanded=False):
                        for region_idx, adjustments in st.session_state['text_adjustments'].items():
                            if int(region_idx) < len(result['text_regions']):
                                region = result['text_regions'][int(region_idx)]
                                size_mult = adjustments.get('font_size_multiplier', 1.0)
                                font_family = adjustments.get('font_family', 'Default')
                                st.write(f"**Region {int(region_idx) + 1}:** {region['text'][:30]}...")
                                st.write(f"   Size: {size_mult:.1f}x, Font: {font_family}")
                
                # Download section
                st.divider()
                
                col_download, col_reset, col_compare = st.columns(3)
                
                with col_download:
                    buf = io.BytesIO()
                    current_image.save(buf, format='PNG')
                    st.download_button(
                        label="📥 Download Edited Image",
                        data=buf.getvalue(),
                        file_name=f"translated_{st.session_state.get('target_lang', 'uk')}_image.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                with col_reset:
                    if st.button("🔄 Reset All Edits", use_container_width=True):
                        st.session_state['text_adjustments'] = {}
                        st.rerun()
                
                with col_compare:
                    if st.button("👀 Compare Original", use_container_width=True):
                        st.session_state['show_comparison'] = not st.session_state.get('show_comparison', False)
                        st.rerun()
                
                # Show comparison if requested
                if st.session_state.get('show_comparison', False):
                    st.subheader("📊 Before vs After Comparison")
                    comp_col1, comp_col2 = st.columns(2)
                    
                    with comp_col1:
                        st.write("**Original Translation**")
                        st.image(result['final_image'], use_column_width=True)
                    
                    with comp_col2:
                        st.write("**Your Edited Version**")
                        st.image(current_image, use_column_width=True)
        
        else:
            st.info("👆 Upload an image and click 'Translate' to start editing!")
            
            # Show preview of the interface
            st.markdown("""
            **How it works:**
            
            1. **Upload** an image with text
            2. **Translate** to your target language  
            3. **Click** directly on any text in the image
            4. **Edit** content, style, and position in the popup
            5. **Apply** changes and see instant preview
            6. **Download** your customized result
            
            ✨ **Enhanced CJK Language Support** - Perfect for Chinese, Japanese, and Korean!
            
            **Features:**
            - 🎯 **Direct clicking** on text regions
            - ✏️ **Inline text editing** - Change any text content
            - 🎨 **Floating control panel** with comprehensive options
            - 🔤 **CJK font support** - Noto Sans CJK, Hiragino, Yu Gothic, etc.
            - 🎭 **Text styling** - Bold, italic, alignment options
            - 📏 **Line spacing** controls for vertical text (Japanese)
            - 🖱️ **Drag & drop** positioning (Ctrl+drag to move text)
            - ⚡ **Real-time preview** updates as you edit
            - ⌨️ **Keyboard shortcuts** (+/- for size, Esc to close, Ctrl+Enter to apply)
            - 📱 **Mobile responsive** with bottom panel on small screens
            - ♿ **Accessibility** with proper ARIA labels and focus management
            
            **Pro Tips:**
            - Hold **Ctrl/Cmd + drag** to reposition text regions
            - Use **line spacing** controls for better vertical text layout
            - **CJK fonts** automatically selected based on target language
            - **Real-time updates** - changes apply as you type!
            """)

if __name__ == "__main__": 
    main()