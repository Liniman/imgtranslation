"""
Enhanced Text Editor Component for Production Batch System

Provides direct text content editing and drag-and-drop repositioning capabilities
for professional image translation workflows.

Key Features:
- Direct inline text editing (click-to-edit)
- Drag-and-drop text region repositioning
- Real-time preview updates
- Template-based styling system
- Keyboard shortcuts for efficiency
- Batch text operations
"""

import streamlit as st
import json
import base64
import io
from typing import List, Dict, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, asdict
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class TextEdit:
    """Represents a text edit operation."""
    region_id: str
    original_text: str
    translated_text: str
    edited_text: str
    position: Tuple[int, int]
    bbox: Tuple[int, int, int, int]
    font_size: int
    font_family: str
    is_repositioned: bool = False
    edit_timestamp: str = None

class EnhancedTextEditor:
    """Enhanced text editor with direct editing and repositioning capabilities."""
    
    def __init__(self, image_processor):
        self.image_processor = image_processor
        self.active_edits = {}
        self.edit_history = []
    
    def create_editable_interface(self, image: Image.Image, text_regions: List[Dict], 
                                 image_id: str = "edit-image") -> str:
        """
        Create enhanced editable interface with direct text editing and repositioning.
        
        Args:
            image: PIL Image to display
            text_regions: List of text regions with translations
            image_id: Unique ID for the image element
            
        Returns:
            HTML string with enhanced editing interface
        """
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Calculate display dimensions
        display_width = min(900, image.width)
        display_height = int(image.height * (display_width / image.width))
        
        # Scale factors
        scale_x = display_width / image.width
        scale_y = display_height / image.height
        
        # Create HTML structure
        html_parts = []
        
        # Main container with image
        html_parts.append(f'''
        <div class="enhanced-editor-container" id="{image_id}-container">
            <div class="image-wrapper" style="width: {display_width}px; height: {display_height}px; position: relative;">
                <img id="{image_id}" 
                     src="data:image/png;base64,{img_str}"
                     style="width: {display_width}px; height: {display_height}px; display: block;"
                     alt="Editable translated image">
        ''')
        
        # Add editable text regions
        for i, region in enumerate(text_regions):
            if 'bbox_rect' not in region or 'translated_text' not in region:
                continue
                
            x, y, w, h = region['bbox_rect']
            
            # Scale coordinates
            scaled_x = int(x * scale_x)
            scaled_y = int(y * scale_y)
            scaled_w = int(w * scale_x)
            scaled_h = int(h * scale_y)
            
            # Region data
            region_data = {
                'index': i,
                'original': region.get('text', ''),
                'translated': region['translated_text'],
                'bbox': [x, y, w, h],
                'scaled_bbox': [scaled_x, scaled_y, scaled_w, scaled_h],
                'language': region.get('target_language', 'uk'),
                'confidence': region.get('confidence', 0.0)
            }
            
            html_parts.append(f'''
            <div class="editable-text-region" 
                 id="region-{i}"
                 data-region='{json.dumps(region_data)}'
                 style="position: absolute; 
                        left: {scaled_x}px; 
                        top: {scaled_y}px; 
                        width: {scaled_w}px; 
                        height: {scaled_h}px;
                        border: 2px solid rgba(59, 130, 246, 0.5);
                        background: rgba(59, 130, 246, 0.1);
                        cursor: move;
                        z-index: 100;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: {max(12, min(scaled_h * 0.6, 24))}px;
                        color: #1f2937;
                        font-weight: 500;
                        text-align: center;
                        padding: 2px;
                        box-sizing: border-box;
                        overflow: hidden;
                        white-space: nowrap;
                        text-overflow: ellipsis;"
                 draggable="true"
                 onclick="startTextEdit({i})"
                 ondragstart="startDrag(event, {i})"
                 ondragend="endDrag(event, {i})"
                 onmouseover="highlightRegion({i}, true)"
                 onmouseout="highlightRegion({i}, false)"
                 title="Click to edit text • Drag to reposition">
                {region['translated_text'][:50] if len(region['translated_text']) > 50 else region['translated_text']}
            </div>
            ''')
        
        html_parts.append('</div></div>')
        
        return '\n'.join(html_parts)
    
    def create_editing_panel_html(self) -> str:
        """Create the enhanced editing panel with direct text editing."""
        return '''
        <div class="enhanced-edit-panel" id="edit-panel" style="display: none;">
            <div class="panel-header">
                <h3 id="panel-title">Edit Text Region</h3>
                <button class="close-btn" onclick="closeEditPanel()">×</button>
            </div>
            
            <div class="edit-content">
                <!-- Original text display -->
                <div class="text-section">
                    <label class="edit-label">Original Text:</label>
                    <div class="original-text-display" id="original-text-display">
                        Original text will appear here
                    </div>
                </div>
                
                <!-- Direct text editing -->
                <div class="text-section">
                    <label class="edit-label">Edit Translation:</label>
                    <textarea class="text-editor" 
                              id="text-editor"
                              placeholder="Edit the translated text here..."
                              rows="3"
                              onInput="updateTextPreview()"
                              onKeyDown="handleTextEditorKeys(event)"></textarea>
                    <div class="editor-help">
                        <small>💡 Press Ctrl+Enter to apply, Esc to cancel</small>
                    </div>
                </div>
                
                <!-- Position controls -->
                <div class="position-section">
                    <label class="edit-label">Position:</label>
                    <div class="position-controls">
                        <button class="pos-btn" onclick="nudgePosition(-1, 0)" title="Move Left">←</button>
                        <button class="pos-btn" onclick="nudgePosition(0, -1)" title="Move Up">↑</button>
                        <button class="pos-btn" onclick="nudgePosition(0, 1)" title="Move Down">↓</button>
                        <button class="pos-btn" onclick="nudgePosition(1, 0)" title="Move Right">→</button>
                        <button class="pos-btn reset" onclick="resetPosition()" title="Reset Position">⌂</button>
                    </div>
                    <div class="position-info">
                        <small>Position: <span id="position-display">0, 0</span></small>
                    </div>
                </div>
                
                <!-- Font controls -->
                <div class="font-section">
                    <label class="edit-label">Font Style:</label>
                    <div class="font-controls">
                        <select class="font-selector" id="font-selector" onchange="updateFontFamily(this.value)">
                            <option value="Default">Default</option>
                            <option value="Arial">Arial</option>
                            <option value="DejaVu Sans">DejaVu Sans</option>
                            <option value="Liberation Sans">Liberation Sans</option>
                        </select>
                        
                        <div class="size-controls">
                            <button class="size-btn" onclick="adjustFontSize(-0.1)">A-</button>
                            <span id="font-size-display">1.0x</span>
                            <button class="size-btn" onclick="adjustFontSize(0.1)">A+</button>
                        </div>
                    </div>
                </div>
                
                <!-- Action buttons -->
                <div class="action-buttons">
                    <button class="action-btn secondary" onclick="resetAllChanges()">
                        🔄 Reset
                    </button>
                    <button class="action-btn secondary" onclick="previewChanges()">
                        👁️ Preview
                    </button>
                    <button class="action-btn primary" onclick="applyTextEdit()">
                        ✅ Apply
                    </button>
                </div>
                
                <!-- Edit status -->
                <div class="edit-status" id="edit-status"></div>
            </div>
        </div>
        
        <!-- Batch edit controls -->
        <div class="batch-edit-controls" id="batch-controls" style="display: none;">
            <div class="batch-header">
                <h4>Batch Text Operations</h4>
                <button class="close-btn" onclick="closeBatchControls()">×</button>
            </div>
            
            <div class="batch-content">
                <!-- Template system -->
                <div class="template-section">
                    <label class="edit-label">Apply Template:</label>
                    <select class="template-selector" id="template-selector" onchange="applyTemplate(this.value)">
                        <option value="">Select a template...</option>
                        <option value="large-title">Large Title Style</option>
                        <option value="body-text">Body Text Style</option>
                        <option value="small-caption">Small Caption Style</option>
                        <option value="custom">Custom Style</option>
                    </select>
                </div>
                
                <!-- Bulk operations -->
                <div class="bulk-operations">
                    <label class="edit-label">Bulk Actions:</label>
                    <div class="bulk-buttons">
                        <button class="bulk-btn" onclick="findAndReplace()">🔍 Find & Replace</button>
                        <button class="bulk-btn" onclick="alignAllText()">📐 Align All</button>
                        <button class="bulk-btn" onclick="uniformSizing()">📏 Uniform Size</button>
                        <button class="bulk-btn" onclick="exportEdits()">📋 Export Edits</button>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    def create_enhanced_javascript(self) -> str:
        """Create enhanced JavaScript for direct editing and repositioning."""
        return '''
        <script>
        let currentEditRegion = null;
        let textEdits = {};
        let draggedElement = null;
        let dragOffset = {x: 0, y: 0};
        let originalPositions = {};
        
        // Text editing functions
        function startTextEdit(regionIndex) {
            const regionEl = document.getElementById(`region-${regionIndex}`);
            if (!regionEl) return;
            
            currentEditRegion = regionIndex;
            const regionData = JSON.parse(regionEl.dataset.region);
            
            // Show edit panel
            const panel = document.getElementById('edit-panel');
            panel.style.display = 'block';
            panel.classList.add('visible');
            
            // Populate edit panel
            document.getElementById('original-text-display').textContent = regionData.original;
            document.getElementById('text-editor').value = regionData.translated;
            document.getElementById('text-editor').focus();
            
            // Update position display
            const [x, y] = regionData.scaled_bbox;
            document.getElementById('position-display').textContent = `${x}, ${y}`;
            
            // Highlight region
            highlightRegion(regionIndex, true, '#ef4444');
        }
        
        function updateTextPreview() {
            if (currentEditRegion === null) return;
            
            const newText = document.getElementById('text-editor').value;
            const regionEl = document.getElementById(`region-${currentEditRegion}`);
            
            if (regionEl && newText.trim()) {
                regionEl.textContent = newText.length > 50 ? newText.substring(0, 50) + '...' : newText;
                regionEl.style.borderColor = '#f59e0b'; // Orange for modified
                
                // Store edit
                if (!textEdits[currentEditRegion]) {
                    textEdits[currentEditRegion] = {};
                }
                textEdits[currentEditRegion].editedText = newText;
            }
        }
        
        function applyTextEdit() {
            if (currentEditRegion === null) return;
            
            const newText = document.getElementById('text-editor').value.trim();
            if (!newText) {
                showEditStatus('Please enter some text', 'error');
                return;
            }
            
            // Apply the edit
            const regionEl = document.getElementById(`region-${currentEditRegion}`);
            if (regionEl) {
                regionEl.textContent = newText.length > 50 ? newText.substring(0, 50) + '...' : newText;
                regionEl.style.borderColor = '#10b981'; // Green for applied
                
                // Store in edits
                if (!textEdits[currentEditRegion]) {
                    textEdits[currentEditRegion] = {};
                }
                textEdits[currentEditRegion].editedText = newText;
                textEdits[currentEditRegion].isEdited = true;
            }
            
            showEditStatus('Text updated successfully!', 'success');
            
            // Trigger Streamlit update
            triggerStreamlitUpdate();
            
            setTimeout(() => {
                closeEditPanel();
            }, 1000);
        }
        
        function closeEditPanel() {
            const panel = document.getElementById('edit-panel');
            panel.style.display = 'none';
            panel.classList.remove('visible');
            
            if (currentEditRegion !== null) {
                highlightRegion(currentEditRegion, false);
                currentEditRegion = null;
            }
        }
        
        // Drag and drop repositioning
        function startDrag(event, regionIndex) {
            draggedElement = document.getElementById(`region-${regionIndex}`);
            const rect = draggedElement.getBoundingClientRect();
            const containerRect = draggedElement.parentElement.getBoundingClientRect();
            
            dragOffset.x = event.clientX - rect.left;
            dragOffset.y = event.clientY - rect.top;
            
            // Store original position
            if (!originalPositions[regionIndex]) {
                originalPositions[regionIndex] = {
                    left: draggedElement.style.left,
                    top: draggedElement.style.top
                };
            }
            
            draggedElement.style.zIndex = '200';
            draggedElement.style.opacity = '0.8';
            
            // Prevent text editing during drag
            event.stopPropagation();
        }
        
        function endDrag(event, regionIndex) {
            if (!draggedElement) return;
            
            const containerRect = draggedElement.parentElement.getBoundingClientRect();
            const newX = event.clientX - containerRect.left - dragOffset.x;
            const newY = event.clientY - containerRect.top - dragOffset.y;
            
            // Constrain to container bounds
            const maxX = containerRect.width - draggedElement.offsetWidth;
            const maxY = containerRect.height - draggedElement.offsetHeight;
            
            const constrainedX = Math.max(0, Math.min(newX, maxX));
            const constrainedY = Math.max(0, Math.min(newY, maxY));
            
            draggedElement.style.left = `${constrainedX}px`;
            draggedElement.style.top = `${constrainedY}px`;
            draggedElement.style.zIndex = '100';
            draggedElement.style.opacity = '1';
            draggedElement.style.borderColor = '#f59e0b'; // Orange for repositioned
            
            // Store position change
            if (!textEdits[regionIndex]) {
                textEdits[regionIndex] = {};
            }
            textEdits[regionIndex].newPosition = [constrainedX, constrainedY];
            textEdits[regionIndex].isRepositioned = true;
            
            draggedElement = null;
            
            // Trigger Streamlit update
            triggerStreamlitUpdate();
        }
        
        // Position nudging
        function nudgePosition(deltaX, deltaY) {
            if (currentEditRegion === null) return;
            
            const regionEl = document.getElementById(`region-${currentEditRegion}`);
            if (!regionEl) return;
            
            const currentLeft = parseInt(regionEl.style.left) || 0;
            const currentTop = parseInt(regionEl.style.top) || 0;
            
            const newLeft = Math.max(0, currentLeft + (deltaX * 5));
            const newTop = Math.max(0, currentTop + (deltaY * 5));
            
            regionEl.style.left = `${newLeft}px`;
            regionEl.style.top = `${newTop}px`;
            
            // Update position display
            document.getElementById('position-display').textContent = `${newLeft}, ${newTop}`;
            
            // Store position change
            if (!textEdits[currentEditRegion]) {
                textEdits[currentEditRegion] = {};
            }
            textEdits[currentEditRegion].newPosition = [newLeft, newTop];
            textEdits[currentEditRegion].isRepositioned = true;
            
            triggerStreamlitUpdate();
        }
        
        function resetPosition() {
            if (currentEditRegion === null) return;
            
            const regionEl = document.getElementById(`region-${currentEditRegion}`);
            if (!regionEl || !originalPositions[currentEditRegion]) return;
            
            regionEl.style.left = originalPositions[currentEditRegion].left;
            regionEl.style.top = originalPositions[currentEditRegion].top;
            regionEl.style.borderColor = 'rgba(59, 130, 246, 0.5)';
            
            // Remove position edit
            if (textEdits[currentEditRegion]) {
                delete textEdits[currentEditRegion].newPosition;
                delete textEdits[currentEditRegion].isRepositioned;
            }
            
            triggerStreamlitUpdate();
        }
        
        // Font controls
        function adjustFontSize(delta) {
            if (currentEditRegion === null) return;
            
            const regionEl = document.getElementById(`region-${currentEditRegion}`);
            if (!regionEl) return;
            
            const currentSize = parseFloat(regionEl.style.fontSize) || 16;
            const newSize = Math.max(8, Math.min(48, currentSize + (delta * currentSize)));
            
            regionEl.style.fontSize = `${newSize}px`;
            document.getElementById('font-size-display').textContent = `${(newSize / 16).toFixed(1)}x`;
            
            // Store font change
            if (!textEdits[currentEditRegion]) {
                textEdits[currentEditRegion] = {};
            }
            textEdits[currentEditRegion].fontSize = newSize;
            
            triggerStreamlitUpdate();
        }
        
        function updateFontFamily(fontFamily) {
            if (currentEditRegion === null) return;
            
            const regionEl = document.getElementById(`region-${currentEditRegion}`);
            if (!regionEl) return;
            
            regionEl.style.fontFamily = fontFamily === 'Default' ? '' : fontFamily;
            
            // Store font change
            if (!textEdits[currentEditRegion]) {
                textEdits[currentEditRegion] = {};
            }
            textEdits[currentEditRegion].fontFamily = fontFamily;
            
            triggerStreamlitUpdate();
        }
        
        // Utility functions
        function highlightRegion(regionIndex, highlight, color = '#3b82f6') {
            const regionEl = document.getElementById(`region-${regionIndex}`);
            if (!regionEl) return;
            
            if (highlight) {
                regionEl.style.borderColor = color;
                regionEl.style.backgroundColor = `${color}20`;
                regionEl.style.boxShadow = `0 0 0 2px ${color}30`;
            } else {
                regionEl.style.borderColor = 'rgba(59, 130, 246, 0.5)';
                regionEl.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                regionEl.style.boxShadow = 'none';
            }
        }
        
        function showEditStatus(message, type) {
            const statusEl = document.getElementById('edit-status');
            statusEl.textContent = message;
            statusEl.className = `edit-status ${type}`;
            
            setTimeout(() => {
                statusEl.textContent = '';
                statusEl.className = 'edit-status';
            }, 3000);
        }
        
        function triggerStreamlitUpdate() {
            // Store edits in hidden input for Streamlit
            const hiddenInput = document.getElementById('text-edits-input');
            if (hiddenInput) {
                hiddenInput.value = JSON.stringify(textEdits);
                hiddenInput.dispatchEvent(new Event('change', {bubbles: true}));
            }
        }
        
        // Keyboard shortcuts
        function handleTextEditorKeys(event) {
            if (event.ctrlKey && event.key === 'Enter') {
                event.preventDefault();
                applyTextEdit();
            } else if (event.key === 'Escape') {
                event.preventDefault();
                closeEditPanel();
            }
        }
        
        // Global keyboard shortcuts
        document.addEventListener('keydown', function(event) {
            if (currentEditRegion !== null) return; // Don't interfere with text editing
            
            if (event.key === 'Escape') {
                closeEditPanel();
                closeBatchControls();
            } else if (event.ctrlKey && event.key === 'b') {
                event.preventDefault();
                toggleBatchControls();
            }
        });
        
        // Batch operations
        function toggleBatchControls() {
            const controls = document.getElementById('batch-controls');
            if (controls.style.display === 'none') {
                controls.style.display = 'block';
            } else {
                controls.style.display = 'none';
            }
        }
        
        function closeBatchControls() {
            document.getElementById('batch-controls').style.display = 'none';
        }
        
        function findAndReplace() {
            const findText = prompt('Find text:');
            if (!findText) return;
            
            const replaceText = prompt('Replace with:');
            if (replaceText === null) return;
            
            let replacedCount = 0;
            
            // Process all regions
            document.querySelectorAll('.editable-text-region').forEach((regionEl, index) => {
                const regionData = JSON.parse(regionEl.dataset.region);
                const currentText = textEdits[index]?.editedText || regionData.translated;
                
                if (currentText.includes(findText)) {
                    const newText = currentText.replace(new RegExp(findText, 'g'), replaceText);
                    
                    // Update display
                    regionEl.textContent = newText.length > 50 ? newText.substring(0, 50) + '...' : newText;
                    regionEl.style.borderColor = '#10b981';
                    
                    // Store edit
                    if (!textEdits[index]) {
                        textEdits[index] = {};
                    }
                    textEdits[index].editedText = newText;
                    textEdits[index].isEdited = true;
                    
                    replacedCount++;
                }
            });
            
            alert(`Replaced ${replacedCount} instances of "${findText}" with "${replaceText}"`);
            triggerStreamlitUpdate();
        }
        
        // Initialize drag and drop for container
        document.addEventListener('DOMContentLoaded', function() {
            const container = document.querySelector('.enhanced-editor-container');
            if (container) {
                container.addEventListener('dragover', function(event) {
                    event.preventDefault();
                });
                
                container.addEventListener('drop', function(event) {
                    event.preventDefault();
                });
            }
        });
        </script>
        '''
    
    def create_enhanced_css(self) -> str:
        """Create enhanced CSS for the editing interface."""
        return '''
        <style>
        .enhanced-editor-container {
            position: relative;
            margin: 1rem 0;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
            background: white;
        }
        
        .image-wrapper {
            position: relative;
            background: #f8fafc;
        }
        
        .editable-text-region {
            transition: all 0.2s ease;
            user-select: none;
            border-radius: 4px;
        }
        
        .editable-text-region:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .enhanced-edit-panel {
            position: fixed;
            top: 50%;
            right: 2rem;
            transform: translateY(-50%);
            width: 380px;
            max-height: 80vh;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            border: 1px solid #e2e8f0;
            z-index: 2000;
            overflow-y: auto;
        }
        
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 1.5rem 1rem;
            border-bottom: 1px solid #e2e8f0;
            background: #f8fafc;
            margin: -1px -1px 0;
            border-radius: 16px 16px 0 0;
        }
        
        .panel-header h3 {
            margin: 0;
            color: #1f2937;
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #6b7280;
            padding: 0.25rem;
            border-radius: 6px;
            transition: all 0.2s ease;
        }
        
        .close-btn:hover {
            background: #e5e7eb;
            color: #374151;
        }
        
        .edit-content {
            padding: 1.5rem;
        }
        
        .text-section, .position-section, .font-section {
            margin-bottom: 1.5rem;
        }
        
        .edit-label {
            display: block;
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.5rem;
            font-size: 0.875rem;
        }
        
        .original-text-display {
            background: #f3f4f6;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 0.875rem;
            color: #6b7280;
            min-height: 2.5rem;
        }
        
        .text-editor {
            width: 100%;
            min-height: 80px;
            padding: 0.75rem;
            border: 2px solid #d1d5db;
            border-radius: 8px;
            font-family: inherit;
            font-size: 0.875rem;
            resize: vertical;
            transition: border-color 0.2s ease;
        }
        
        .text-editor:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        
        .editor-help {
            margin-top: 0.5rem;
            color: #6b7280;
        }
        
        .position-controls {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        .pos-btn {
            padding: 0.5rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s ease;
        }
        
        .pos-btn:hover {
            background: #f3f4f6;
            border-color: #9ca3af;
        }
        
        .pos-btn.reset {
            grid-column: 2;
            background: #fef3c7;
            border-color: #f59e0b;
        }
        
        .pos-btn.reset:hover {
            background: #fde68a;
        }
        
        .position-info {
            color: #6b7280;
            font-size: 0.75rem;
        }
        
        .font-controls {
            display: flex;
            gap: 0.75rem;
            align-items: center;
        }
        
        .font-selector {
            flex: 1;
            padding: 0.5rem 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            font-size: 0.875rem;
        }
        
        .size-controls {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .size-btn {
            width: 36px;
            height: 36px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .size-btn:hover {
            background: #f3f4f6;
            border-color: #9ca3af;
        }
        
        #font-size-display {
            min-width: 45px;
            text-align: center;
            font-size: 0.875rem;
            font-weight: 600;
            color: #374151;
        }
        
        .action-buttons {
            display: flex;
            gap: 0.75rem;
            margin-top: 2rem;
        }
        
        .action-btn {
            flex: 1;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 0.875rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            border: none;
        }
        
        .action-btn.primary {
            background: #3b82f6;
            color: white;
        }
        
        .action-btn.primary:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }
        
        .action-btn.secondary {
            background: #f3f4f6;
            color: #374151;
            border: 1px solid #d1d5db;
        }
        
        .action-btn.secondary:hover {
            background: #e5e7eb;
        }
        
        .edit-status {
            margin-top: 1rem;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            font-size: 0.875rem;
            text-align: center;
        }
        
        .edit-status.success {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #bbf7d0;
        }
        
        .edit-status.error {
            background: #fef2f2;
            color: #dc2626;
            border: 1px solid #fecaca;
        }
        
        /* Batch controls */
        .batch-edit-controls {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            width: 400px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.2);
            border: 1px solid #e2e8f0;
            z-index: 1500;
        }
        
        .batch-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e2e8f0;
            background: #f8fafc;
            border-radius: 12px 12px 0 0;
        }
        
        .batch-header h4 {
            margin: 0;
            color: #1f2937;
            font-size: 1rem;
            font-weight: 600;
        }
        
        .batch-content {
            padding: 1.5rem;
        }
        
        .template-section, .bulk-operations {
            margin-bottom: 1rem;
        }
        
        .template-selector {
            width: 100%;
            padding: 0.5rem 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
        }
        
        .bulk-buttons {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
            margin-top: 0.5rem;
        }
        
        .bulk-btn {
            padding: 0.5rem 0.75rem;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background: white;
            cursor: pointer;
            font-size: 0.8rem;
            transition: all 0.2s ease;
        }
        
        .bulk-btn:hover {
            background: #f3f4f6;
            border-color: #9ca3af;
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .enhanced-edit-panel {
                position: fixed;
                bottom: 0;
                right: 0;
                left: 0;
                top: auto;
                transform: none;
                width: auto;
                max-height: 70vh;
                border-radius: 12px 12px 0 0;
            }
            
            .batch-edit-controls {
                left: 1rem;
                right: 1rem;
                width: auto;
                transform: none;
            }
        }
        
        /* Animation classes */
        .enhanced-edit-panel.visible {
            animation: slideInRight 0.3s ease-out;
        }
        
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translate(100px, -50%);
            }
            to {
                opacity: 1;
                transform: translateY(-50%);
            }
        }
        </style>
        '''

def create_enhanced_editor_interface(image: Image.Image, text_regions: List[Dict], 
                                   image_id: str = "enhanced-editor") -> str:
    """
    Create the complete enhanced editor interface.
    
    Args:
        image: PIL Image to edit
        text_regions: List of text regions with translations
        image_id: Unique identifier for the image
        
    Returns:
        Complete HTML interface with CSS and JavaScript
    """
    editor = EnhancedTextEditor(None)
    
    # Generate interface components
    editable_interface = editor.create_editable_interface(image, text_regions, image_id)
    editing_panel = editor.create_editing_panel_html()
    css_styles = editor.create_enhanced_css()
    javascript_code = editor.create_enhanced_javascript()
    
    # Hidden input for Streamlit communication
    hidden_input = '''
    <input type="hidden" id="text-edits-input" />
    <script>
    // Connect to Streamlit
    document.addEventListener('DOMContentLoaded', function() {
        const streamlitInput = document.querySelector('input[data-testid="stTextInput-text-edits"]');
        const hiddenInput = document.getElementById('text-edits-input');
        
        if (streamlitInput && hiddenInput) {
            hiddenInput.addEventListener('change', function() {
                streamlitInput.value = this.value;
                streamlitInput.dispatchEvent(new Event('input', {bubbles: true}));
            });
        }
    });
    </script>
    '''
    
    # Combine all components
    complete_interface = f'''
    {css_styles}
    <div class="enhanced-text-editor">
        {editable_interface}
        {editing_panel}
        {hidden_input}
    </div>
    {javascript_code}
    '''
    
    return complete_interface