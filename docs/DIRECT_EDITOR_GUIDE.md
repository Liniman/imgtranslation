# Direct Manipulation Text Editor

A Google Slides-like text editing interface for the image translation app that allows users to click directly on text elements in the image to edit them.

## 🚀 Quick Start

```bash
# Run the direct manipulation editor
streamlit run direct_edit_app.py

# Or test the functionality first
python3 test_direct_editor.py
```

## ✨ Features

### 🎯 Direct Text Selection
- **Click on any text** in the translated image to select it
- **Visual feedback** with colored borders and highlights
- **No need to match** left-side controls with right-side preview

### 🎨 Floating Control Panel
- **Appears near selected text** for intuitive editing
- **Font size adjustment** with slider and quick buttons (+/-)
- **Font family selection** from available system fonts
- **Reset and Apply** buttons for easy management

### ⚡ Real-time Preview
- **Instant updates** as you adjust text properties
- **Debounced changes** to avoid performance issues
- **Live preview** shows exactly what you'll download

### ⌨️ Keyboard Shortcuts
- **Esc**: Close control panel
- **+/=**: Increase font size
- **-**: Decrease font size

### 📱 Responsive Design
- **Desktop**: Floating panel positioned near selected text
- **Mobile**: Panel slides up from bottom for easy access
- **Touch-friendly** controls for all devices

## 🎮 How To Use

### 1. Upload and Translate
1. Upload an image containing text
2. Select target language
3. Click "🚀 Translate Image"

### 2. Direct Text Editing
1. **Click on any text** in the translated image
2. **Control panel appears** near the selected text
3. **Adjust font size** using:
   - Quick buttons (- and +)
   - Precise slider control
4. **Change font family** from dropdown menu
5. **Apply changes** to see instant preview

### 3. Fine-tuning and Export
1. **Compare** original vs edited versions
2. **Reset individual regions** or all edits
3. **Download** your customized result

## 🛠️ Technical Implementation

### Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │  HTML/CSS/JS     │    │ Image Processor │
│   Backend       │◄──►│  Frontend        │◄──►│   Rendering     │
│                 │    │                  │    │                 │
│ • Session State │    │ • Click Detection│    │ • Font Handling │
│ • Image Data    │    │ • Control Panel  │    │ • Text Fitting  │
│ • Adjustments   │    │ • Visual Effects │    │ • Real-time Gen │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

#### 1. Clickable Image Overlay
```html
<div class="image-container">
    <img src="..." />
    <div class="text-region" onclick="selectTextRegion(0)">...</div>
    <div class="text-region" onclick="selectTextRegion(1)">...</div>
</div>
```

#### 2. Floating Control Panel
```html
<div class="control-panel" id="control-panel">
    <div class="size-controls">
        <button onclick="adjustSize(-0.2)">−</button>
        <input type="range" class="size-slider" />
        <button onclick="adjustSize(0.2)">+</button>
    </div>
    <select class="font-selector">...</select>
</div>
```

#### 3. JavaScript ↔ Streamlit Communication
```javascript
// Update adjustments and trigger Streamlit rerun
function triggerStreamlitUpdate() {
    const hiddenInput = document.getElementById('adjustments-input');
    hiddenInput.value = JSON.stringify(currentAdjustments);
    hiddenInput.dispatchEvent(new Event('change'));
}
```

### Data Flow
1. **User clicks** text region → JavaScript selects region
2. **User adjusts** controls → JavaScript updates local state
3. **JavaScript triggers** update → Streamlit receives new adjustments
4. **Streamlit reruns** → ImageProcessor generates new preview
5. **New image displayed** → User sees instant feedback

## 🎨 Styling and UX

### Visual Design
- **Clean, modern interface** with rounded corners and shadows
- **Subtle animations** for smooth transitions
- **Color-coded feedback**: Blue for hover, red for selected
- **Professional appearance** suitable for business use

### Interaction Design
- **Direct manipulation** paradigm like Google Slides/PowerPoint
- **Contextual controls** appear where needed
- **Progressive disclosure** - only show controls when editing
- **Consistent visual language** throughout the interface

### Accessibility
- **Keyboard navigation** with standard shortcuts
- **High contrast** colors for text and borders
- **Screen reader friendly** with proper ARIA labels
- **Touch-friendly** controls for mobile devices

## 🧪 Testing

The `test_direct_editor.py` script validates:

### Core Functionality
- ✅ ImageProcessor integration
- ✅ HTML generation
- ✅ JavaScript handler creation
- ✅ JSON serialization/deserialization
- ✅ Font availability and loading

### Test Coverage
```bash
python3 test_direct_editor.py
```

Creates test files:
- `/tmp/test_direct_editor_original.png` - Base rendering
- `/tmp/test_direct_editor_adjusted.png` - With adjustments
- `/tmp/test_direct_editor.html` - Interactive HTML demo

## 🔧 Customization

### Adding New Controls
1. **Add HTML** in `create_control_panel_html()`
2. **Add JavaScript** handlers in `create_javascript_handler()`
3. **Update data flow** in adjustment processing

### Styling Changes
- **CSS classes** are defined in the main app file
- **Responsive breakpoints** can be adjusted for different devices
- **Color scheme** can be modified in the CSS variables

### New Features
- **Text content editing** (not just styling)
- **Color picker** for text colors
- **Rotation and positioning** controls
- **Multiple font weight** options

## 🚀 Performance Considerations

### Optimization Strategies
- **Debounced updates** (500ms delay) to reduce server calls
- **Efficient image encoding** with base64 for HTML embedding
- **Smart caching** of font objects and rendering components
- **Progressive loading** for large images

### Memory Management
- **Session state cleanup** when starting new translations
- **Image resize** for processing to stay within reasonable limits
- **Font cache** to avoid repeated font loading

## 🔍 Troubleshooting

### Common Issues

#### Control Panel Not Appearing
- Check browser console for JavaScript errors
- Ensure text regions have valid bounding boxes
- Verify HTML structure is complete

#### Real-time Updates Not Working
- Check Streamlit session state synchronization
- Verify hidden input element connection
- Look for JSON serialization errors

#### Font Issues
- Check system font availability
- Verify font file paths are correct
- Use fallback fonts for compatibility

### Debug Mode
Enable debug logging:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📋 Comparison with Traditional Interface

| Feature | Traditional Interface | Direct Manipulation Interface |
|---------|----------------------|--------------------------------|
| **Text Selection** | Dropdown/list navigation | Direct clicking on image |
| **Visual Feedback** | Separate preview pane | Inline highlighting |
| **Control Location** | Fixed sidebar | Contextual floating panel |
| **User Experience** | Two-step process | Single-step interaction |
| **Learning Curve** | Need to understand mapping | Intuitive, familiar pattern |
| **Mobile Experience** | Difficult scrolling | Optimized touch interface |
| **Accessibility** | Traditional form controls | Enhanced with shortcuts |

## 🎯 Future Enhancements

### Planned Features
- **Drag and drop** text repositioning
- **Inline text editing** without popup
- **Batch operations** for multiple regions
- **Undo/redo** functionality
- **Templates** for common adjustments

### Advanced Capabilities
- **Smart text fitting** with automatic wrapping
- **Style transfer** between regions
- **Custom font upload** functionality
- **Advanced typography** controls

## 📚 Related Files

- `direct_edit_app.py` - Main application
- `test_direct_editor.py` - Test suite
- `core/image_processor.py` - Text rendering engine
- `app_enhanced.py` - Traditional interface (for comparison)

---

**Created with ❤️ for intuitive image translation editing**