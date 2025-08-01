# 🎨 Interactive Text Editor Guide

The Interactive Text Editor allows you to fine-tune translated text appearance in real-time after the initial translation is complete. This feature provides immediate visual feedback and eliminates the need to re-process the entire image when making adjustments.

## 🚀 How to Access the Interactive Editor

1. **Upload an image** using the main Streamlit interface
2. **Run the translation** by clicking "🚀 Translate Image"
3. **Switch to the Interactive Editor tab** in the results section
4. **Start customizing** text properties with real-time preview

## ✨ Key Features

### Real-Time Text Adjustment
- **Font Size Control**: Adjust each text region independently with precision sliders
- **Quick Size Buttons**: Use 🔽 Smaller, ↩️ Reset, and 🔼 Bigger for rapid adjustments
- **Font Family Selection**: Choose from available system fonts for better matching
- **Live Preview**: See changes instantly without re-processing the entire image

### User-Friendly Interface
- **Region-Based Controls**: Each detected text region has its own adjustment panel
- **Smart Defaults**: Starts with optimized font sizes and intelligent font selection
- **Before/After Comparison**: Toggle between original and edited versions
- **Adjustment Summary**: Track all changes made to each text region

### Advanced Text Handling
- **Intelligent Text Fitting**: Automatically wraps or truncates text that doesn't fit
- **Font Matching**: Uses system fonts that best match the original text style
- **Precise Positioning**: Maintains original text positioning and alignment
- **Quality Preservation**: No loss in image quality during adjustments

## 🎯 Step-by-Step Usage

### Step 1: Upload and Translate
```
1. Select target language from the sidebar
2. Upload your image file
3. Click "🚀 Translate Image"
4. Wait for translation to complete
```

### Step 2: Access Interactive Editor
```
1. Look for the "🎨 Interactive Editor" tab in results
2. Click to switch from the default "📊 Details" view
3. You'll see controls on the left and live preview on the right
```

### Step 3: Adjust Text Properties
```
For each text region:
1. Expand the region panel (first one is open by default)
2. Review the original and translated text
3. Use quick buttons for fast size changes:
   - 🔽 Smaller: Reduce size by 0.2x
   - ↩️ Reset: Return to original size
   - 🔼 Bigger: Increase size by 0.2x
4. Use the "Precise Font Size" slider for fine-tuning
5. Select a different "Font Family" if needed
```

### Step 4: Review and Download
```
1. Check the live preview for your changes
2. Use "👀 Compare with Original" to see before/after
3. Review the "📋 Current Adjustments Summary"
4. Click "📥 Download Edited Image" when satisfied
```

## 🔧 Technical Details

### Font Size Multipliers
- **Default**: 1.0x (original automatic sizing)
- **Range**: 0.5x to 2.0x (50% to 200% of original size)
- **Step Size**: 0.1x for precise control
- **Quick Adjustments**: ±0.2x increments with buttons

### Font Selection
- **Available Fonts**: Dynamically detected system fonts
- **Smart Fallbacks**: Automatically falls back to best available font
- **Language Support**: Optimized font selection for different languages
- **Default Option**: Uses original intelligent font matching when "Default" is selected

### Text Fitting Algorithm
1. **Primary**: Uses original translated text if it fits
2. **Word Wrapping**: Breaks long text into multiple lines when possible
3. **Truncation**: Adds "..." when text is too long for available space
4. **Intelligent Bounds**: Respects original text region boundaries

## 🎨 UI Components Explained

### Left Panel: Text Controls
- **Stats Bar**: Shows text regions count, active adjustments, and available fonts
- **Region Expanders**: Collapsible panels for each text region
- **Quick Action Buttons**: Fast size adjustments and region resets
- **Precision Sliders**: Fine-tune exact font sizes
- **Font Selectors**: Choose from available system fonts
- **Global Controls**: Reset all adjustments or refresh preview

### Right Panel: Live Preview
- **Status Indicators**: Shows whether adjustments are applied
- **Interactive Preview**: Real-time image updates as you adjust settings
- **Action Buttons**: Download edited image or compare with original
- **Comparison View**: Side-by-side before/after comparison
- **Adjustment Summary**: Detailed list of all current modifications

## 💡 Tips for Best Results

### Font Size Adjustments
- **Start Small**: Make incremental changes to avoid over-sizing
- **Check Fit**: Ensure text doesn't exceed original region boundaries
- **Language Consideration**: Some languages may require larger fonts for readability

### Font Selection
- **Match Style**: Try to match the original font style (serif vs sans-serif)
- **Test Readability**: Ensure the chosen font is readable at the target size
- **Language Support**: Verify the font supports your target language characters

### Workflow Optimization
- **Adjust Largest Regions First**: Start with the most prominent text
- **Use Quick Buttons**: For rapid experimentation with sizes
- **Save Intermediate Results**: Download versions you like before continuing
- **Compare Frequently**: Use the comparison feature to validate changes

## 🚨 Troubleshooting

### Preview Not Updating
- Click the "🔄 Refresh Preview" button
- Try adjusting any slider slightly to trigger an update
- Check if there are any error messages in the debug section

### Text Too Small/Large
- Use the "↩️ Reset" button for individual regions
- Try the "🔄 Reset All" button to start over
- Adjust the precision slider for fine control

### Font Not Changing
- Ensure the selected font appears in the available fonts list
- Try selecting "Default" to use automatic font matching
- Some fonts may look similar; check the adjustment summary to confirm changes

### Performance Issues
- The preview updates automatically; avoid rapid slider movements
- Use quick buttons for faster adjustments
- Close unused region expanders to improve performance

## 🔮 Advanced Features

### Batch Adjustments
Currently, each region must be adjusted individually. Future versions may include:
- Global font size multipliers
- Style presets for consistent adjustments
- Copy settings between regions

### Custom Font Upload
The system uses available system fonts. To add more fonts:
1. Install fonts on your system
2. Restart the application
3. New fonts will appear in the selection list

### API Integration
The interactive editing functionality can be integrated into other applications:
```python
from core.image_processor import ImageProcessor

processor = ImageProcessor()
adjustments = {0: {'font_size_multiplier': 1.5}}
result = processor.render_text_with_adjustments(base_image, regions, adjustments)
```

## 📞 Support

If you encounter issues with the Interactive Text Editor:
1. Check the debug information in the error expander
2. Verify your image has been successfully translated
3. Ensure you have sufficient system fonts installed
4. Try refreshing the preview or resetting adjustments

The Interactive Text Editor enhances your image translation workflow by providing immediate, visual control over the final output quality.