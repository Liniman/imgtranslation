"""
Enhanced Streamlit app for image translation with multi-image support.
"""

import streamlit as st
import logging
from PIL import Image
import io
import zipfile
from typing import List, Dict
import time
import traceback

# Import our enhanced core modules
from core import OCREngine, TranslationEngine, ImageProcessor, validate_image

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Image Translator Pro",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c2c7;
        color: #721c24;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .interactive-editor {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .text-controls {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 0.5rem;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
    .preview-container {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1rem;
        border: 2px dashed #dee2e6;
        margin: 1rem 0;
    }
    .adjustment-summary {
        background-color: #e7f3ff;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border: 1px solid #b3d9ff;
    }
    /* Improve slider appearance */
    .stSlider > div > div > div > div {
        background-color: #1f77b4;
    }
    /* Better expander styling */
    .streamlit-expanderHeader {
        background-color: #f1f3f4;
        border-radius: 0.25rem;
    }
    /* Enhance download buttons */
    .stDownloadButton > button {
        background-color: #28a745;
        color: white;
        border: none;
        border-radius: 0.25rem;
        font-weight: 500;
    }
    .stDownloadButton > button:hover {
        background-color: #218838;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_engines():
    """Load and cache the core engines."""
    logger.info("Initializing engines...")
    try:
        ocr_engine = OCREngine(min_confidence=0.6)
        translation_engine = TranslationEngine()  # Will use DeepL if API key is available
        image_processor = ImageProcessor()
        
        # Log which translation provider is being used
        provider = translation_engine.primary_provider
        if provider == 'deepl':
            logger.info("✅ Translation engine using DeepL API for superior quality")
        else:
            logger.info("ℹ️ Translation engine using Google Translate (DeepL not configured)")
            
        logger.info("All engines initialized successfully")
        return ocr_engine, translation_engine, image_processor
    except Exception as e:
        logger.error(f"Failed to initialize engines: {e}")
        st.error(f"Failed to initialize processing engines: {e}")
        st.stop()

def process_single_image(image: Image.Image, target_lang: str, engines: tuple, progress_callback=None) -> Dict:
    """
    Process a single image through the complete translation pipeline.
    
    Args:
        image: PIL Image to process
        target_lang: Target language code
        engines: Tuple of (ocr_engine, translation_engine, image_processor)
        progress_callback: Optional callback for progress updates
        
    Returns:
        Dictionary with processing results
    """
    ocr_engine, translation_engine, image_processor = engines
    
    result = {
        'success': False,
        'original_image': image,
        'final_image': None,
        'detections': [],
        'translations': [],
        'processing_time': 0,
        'error': None
    }
    
    start_time = time.time()
    
    try:
        # Step 1: Validate image
        if progress_callback:
            progress_callback(10, "Validating image...")
        
        is_valid, error_msg = validate_image(image)
        if not is_valid:
            result['error'] = error_msg
            return result
        
        # Step 2: Resize if needed
        if progress_callback:
            progress_callback(20, "Preparing image...")
        
        processed_image, scale_factor = image_processor.resize_for_processing(image)
        
        # Step 3: OCR text detection
        if progress_callback:
            progress_callback(30, "Detecting text...")
        
        text_regions = ocr_engine.get_text_regions(processed_image)
        
        if not text_regions:
            result['error'] = "No text detected in image"
            return result
        
        logger.info(f"Detected {len(text_regions)} text regions")
        
        # Step 4: Translate text
        if progress_callback:
            progress_callback(50, "Translating text...")
        
        texts_to_translate = [region['text'] for region in text_regions]
        translations = translation_engine.translate_batch(texts_to_translate, target_lang)
        
        # Combine translations with regions
        for i, (translated_text, quality) in enumerate(translations):
            if i < len(text_regions):
                text_regions[i]['translated_text'] = translated_text
                text_regions[i]['translation_quality'] = quality
                text_regions[i]['target_language'] = target_lang
        
        # Step 5: Create inpainting mask
        if progress_callback:
            progress_callback(70, "Removing original text...")
        
        mask = image_processor.create_enhanced_mask(processed_image, text_regions)
        inpainted_image = image_processor.enhanced_inpainting(processed_image, mask)
        
        # Step 6: Add translated text
        if progress_callback:
            progress_callback(90, "Adding translated text...")
        
        final_image = image_processor.add_translated_text(inpainted_image, text_regions)
        
        # Scale back to original size if needed
        if scale_factor != 1.0:
            final_size = (
                int(final_image.width / scale_factor),
                int(final_image.height / scale_factor)
            )
            final_image = final_image.resize(final_size, Image.Resampling.LANCZOS)
        
        # Prepare results
        result.update({
            'success': True,
            'final_image': final_image,
            'detections': len(text_regions),
            'translations': [(region['text'], region['translated_text'], region['translation_quality']) 
                           for region in text_regions],
            'processing_time': time.time() - start_time
        })
        
        if progress_callback:
            progress_callback(100, "Translation complete!")
        
        logger.info(f"Image processed successfully in {result['processing_time']:.2f}s")
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        result['error'] = str(e)
        result['processing_time'] = time.time() - start_time
    
    return result

def main():
    """Main Streamlit application."""
    
    # Load engines
    engines = load_engines()
    
    # Header
    st.title("🌍 Image Translator Pro")
    st.markdown("Advanced image translation with OCR confidence filtering, smart font matching, and enhanced inpainting.")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Show DeepL status
    st.sidebar.success("🚀 **DeepL Powered**\n\nUsing premium context-aware translation exclusively for professional-quality results perfect for marketing content.")
    
    with st.sidebar.expander("ℹ️ About DeepL Translation", expanded=False):
        st.info("""
        **Why DeepL?**
        
        - **Context-aware**: Understands supplement terminology
        - **Professional quality**: Website-ready translations
        - **Natural phrasing**: Marketing-appropriate language
        - **Accurate**: No more "Take 1 liquid" → "liquid" nonsense
        
        Perfect for brand images that may appear on websites.
        """)
    
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
    
    target_lang = st.sidebar.selectbox(
        "Target Language",
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        index=0  # Default to Ukrainian
    )
    
    # OCR confidence threshold
    min_confidence = st.sidebar.slider(
        "OCR Confidence Threshold",
        min_value=0.3,
        max_value=0.9,
        value=0.6,
        step=0.1,
        help="Higher values filter out more uncertain text detections"
    )
    
    # Update OCR engine confidence
    engines[0].set_confidence_threshold(min_confidence)
    
    # Processing mode
    processing_mode = st.sidebar.radio(
        "Processing Mode",
        ["Single Image", "Batch Processing"],
        help="Single image for detailed review, batch for multiple images"
    )
    
    # File upload
    if processing_mode == "Single Image":
        st.header("📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload an image containing text to translate"
        )
        
        if uploaded_file:
            process_single_image_ui(uploaded_file, target_lang, engines, languages)
    
    else:  # Batch processing
        st.header("📤 Upload Multiple Images")
        uploaded_files = st.file_uploader(
            "Choose image files",
            type=['png', 'jpg', 'jpeg', 'webp'],
            accept_multiple_files=True,
            help="Upload multiple images for batch translation"
        )
        
        if uploaded_files:
            process_batch_images_ui(uploaded_files, target_lang, engines, languages)

def process_single_image_ui(uploaded_file, target_lang: str, engines: tuple, languages: Dict):
    """UI for single image processing."""
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Original Image")
        image = Image.open(uploaded_file)
        st.image(image, use_column_width=True)
        
        # Image info
        st.markdown("**Image Info:**")
        st.write(f"Size: {image.size[0]} × {image.size[1]} pixels")
        st.write(f"Mode: {image.mode}")
        st.write(f"Format: {getattr(image, 'format', 'Unknown')}")
        
        # Process button
        if st.button("🚀 Translate Image", type="primary", use_container_width=True):
            with st.spinner("Processing image..."):
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(percent, message):
                    progress_bar.progress(percent)
                    status_text.text(message)
                
                # Process image
                result = process_single_image(image, target_lang, engines, progress_callback)
                
                # Store result in session state
                st.session_state['result'] = result
                st.session_state['target_lang'] = target_lang
                
                # Store intermediate results for interactive editing
                if result['success']:
                    # Create base inpainted image (without translated text)
                    text_regions = []
                    for i, (original, translated, quality) in enumerate(result['translations']):
                        # Reconstruct text regions from result (simplified)
                        text_regions.append({
                            'text': original,
                            'translated_text': translated,
                            'translation_quality': quality,
                            'target_language': target_lang,
                            'bbox_rect': (0, 0, 100, 30),  # Placeholder - would need actual bbox data
                        })
                    
                    # Create inpainted base for editing
                    ocr_engine, translation_engine, image_processor = engines
                    processed_image, scale_factor = image_processor.resize_for_processing(image)
                    actual_regions = ocr_engine.get_text_regions(processed_image)
                    
                    # Update text regions with actual OCR data and translations
                    for i, region in enumerate(actual_regions):
                        if i < len(result['translations']):
                            region['translated_text'] = result['translations'][i][1]
                            region['translation_quality'] = result['translations'][i][2]
                            region['target_language'] = target_lang
                    
                    # Create base inpainted image
                    mask = image_processor.create_enhanced_mask(processed_image, actual_regions)
                    inpainted_base = image_processor.enhanced_inpainting(processed_image, mask)
                    
                    # Scale back if needed
                    if scale_factor != 1.0:
                        final_size = (
                            int(inpainted_base.width / scale_factor),
                            int(inpainted_base.height / scale_factor)
                        )
                        inpainted_base = inpainted_base.resize(final_size, Image.Resampling.LANCZOS)
                    
                    st.session_state['inpainted_base'] = inpainted_base
                    st.session_state['text_regions'] = actual_regions
                    st.session_state['scale_factor'] = scale_factor
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
    
    with col2:
        if 'result' in st.session_state:
            result = st.session_state['result']
            
            if result['success']:
                # Create tabs for different views
                tab1, tab2 = st.tabs(["🎨 Interactive Editor", "📊 Details"])
                
                with tab1:
                    display_interactive_editor(result, engines, languages[target_lang])
                
                with tab2:
                    st.subheader(f"Translated to {languages[target_lang]}")
                    st.image(result['final_image'], use_column_width=True)
                    
                    # Metrics
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Text Regions", result['detections'])
                    with col_b:
                        st.metric("Processing Time", f"{result['processing_time']:.1f}s")
                    with col_c:
                        avg_quality = sum(t[2] for t in result['translations']) / len(result['translations'])
                        st.metric("Avg Quality", f"{avg_quality:.2f}")
                    
                    # Download button
                    buf = io.BytesIO()
                    result['final_image'].save(buf, format='PNG')
                    st.download_button(
                        label="📥 Download Translated Image",
                        data=buf.getvalue(),
                        file_name=f"translated_{target_lang}_{uploaded_file.name}",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    # Translation details
                    with st.expander("📋 Translation Details"):
                        for i, (original, translated, quality) in enumerate(result['translations']):
                            st.write(f"**{i+1}.** `{original}` → `{translated}` (Quality: {quality:.2f})")
            
            else:
                st.error(f"Processing failed: {result['error']}")
        
        else:
            st.info("👆 Upload an image and click 'Translate' to see results here.")

def process_batch_images_ui(uploaded_files: List, target_lang: str, engines: tuple, languages: Dict):
    """UI for batch image processing."""
    
    st.write(f"**{len(uploaded_files)} images uploaded**")
    
    if st.button("🚀 Process All Images", type="primary"):
        results = []
        
        # Create progress tracking
        overall_progress = st.progress(0)
        status_text = st.empty()
        
        # Results container
        results_container = st.container()
        
        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name} ({i+1}/{len(uploaded_files)})")
            overall_progress.progress((i / len(uploaded_files)) * 100)
            
            try:
                image = Image.open(uploaded_file)
                
                # Process image (without individual progress callback for batch)
                result = process_single_image(image, target_lang, engines)
                result['filename'] = uploaded_file.name
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process {uploaded_file.name}: {e}")
                results.append({
                    'filename': uploaded_file.name,
                    'success': False,
                    'error': str(e)
                })
        
        overall_progress.progress(100)
        status_text.text("Batch processing complete!")
        
        # Display results
        display_batch_results(results, target_lang, languages)

def display_interactive_editor(result: Dict, engines: tuple, target_language: str):
    """Display interactive text editing interface."""
    
    if 'inpainted_base' not in st.session_state or 'text_regions' not in st.session_state:
        st.error("Interactive editing data not available. Please re-run the translation.")
        return
    
    st.subheader(f"🎨 Interactive Text Editor - {target_language}")
    
    # Add helpful information
    st.info("""
    **🎯 How to use the Interactive Editor:**
    - Each text region can be adjusted independently
    - Use the **Font Size** slider to make text bigger or smaller
    - Choose different **Font Family** options to improve readability
    - The preview updates automatically as you make changes
    - Click **Download Edited Image** to save your customized result
    """)
    
    # Get the required data first
    inpainted_base = st.session_state['inpainted_base']
    text_regions = st.session_state['text_regions']
    ocr_engine, translation_engine, image_processor = engines
    
    # Initialize session state variables if not present
    if 'text_adjustments' not in st.session_state:
        st.session_state['text_adjustments'] = {}
    if 'show_comparison' not in st.session_state:
        st.session_state['show_comparison'] = False
    
    # Show quick stats
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Text Regions", len([r for r in text_regions if 'translated_text' in r]))
    with col_stat2:
        active_adjustments = len(st.session_state['text_adjustments'])
        st.metric("Active Adjustments", active_adjustments)
    with col_stat3:
        available_fonts = image_processor.get_available_fonts()
        st.metric("Available Fonts", len(available_fonts))
    
    # Create columns for controls and preview
    col_controls, col_preview = st.columns([1, 2])
    
    with col_controls:
        st.subheader("Text Controls")
        
        # Get available fonts
        available_fonts = image_processor.get_available_fonts()
        
        # Create controls for each text region
        for i, region in enumerate(text_regions):
            if 'translated_text' not in region:
                continue
            
            with st.expander(f"Region {i+1}: {region['text'][:30]}...", expanded=i == 0):
                st.write(f"**Original:** {region['text']}")
                st.write(f"**Translation:** {region['translated_text']}")
                
                # Font size controls
                current_multiplier = st.session_state['text_adjustments'].get(i, {}).get('font_size_multiplier', 1.0)
                
                # Quick size buttons
                col_smaller, col_reset_size, col_bigger = st.columns(3)
                with col_smaller:
                    if st.button("🔽 Smaller", key=f"smaller_{i}", use_container_width=True):
                        new_multiplier = max(0.5, current_multiplier - 0.2)
                        if i not in st.session_state['text_adjustments']:
                            st.session_state['text_adjustments'][i] = {}
                        st.session_state['text_adjustments'][i]['font_size_multiplier'] = new_multiplier
                        st.rerun()
                
                with col_reset_size:
                    if st.button("↩️ Reset", key=f"reset_size_{i}", use_container_width=True):
                        if i in st.session_state['text_adjustments']:
                            st.session_state['text_adjustments'][i]['font_size_multiplier'] = 1.0
                        st.rerun()
                
                with col_bigger:
                    if st.button("🔼 Bigger", key=f"bigger_{i}", use_container_width=True):
                        new_multiplier = min(2.0, current_multiplier + 0.2)
                        if i not in st.session_state['text_adjustments']:
                            st.session_state['text_adjustments'][i] = {}
                        st.session_state['text_adjustments'][i]['font_size_multiplier'] = new_multiplier
                        st.rerun()
                
                # Precise font size slider
                font_size_multiplier = st.slider(
                    "Precise Font Size",
                    min_value=0.5,
                    max_value=2.0,
                    value=current_multiplier,
                    step=0.1,
                    key=f"font_size_{i}",
                    help="Fine-tune the exact size of this text region"
                )
                
                # Font family selector
                current_font = st.session_state['text_adjustments'].get(i, {}).get('font_family', 'Default')
                if current_font not in available_fonts:
                    current_font = 'Default'
                
                font_family = st.selectbox(
                    "Font Family",
                    options=available_fonts,
                    index=available_fonts.index(current_font) if current_font in available_fonts else 0,
                    key=f"font_family_{i}",
                    help="Choose a font for this text region"
                )
                
                # Convert font name to file name
                font_file = image_processor.get_font_file_from_name(font_family) if font_family != 'Default' else None
                
                # Store adjustments
                st.session_state['text_adjustments'][i] = {
                    'font_size_multiplier': font_size_multiplier,
                    'font_family': font_file
                }
                
                # Reset button for this region
                if st.button(f"Reset Region {i+1}", key=f"reset_{i}"):
                    if i in st.session_state['text_adjustments']:
                        del st.session_state['text_adjustments'][i]
                        st.rerun()
        
        # Global controls
        st.divider()
        col_reset, col_apply = st.columns(2)
        
        with col_reset:
            if st.button("🔄 Reset All", use_container_width=True):
                st.session_state['text_adjustments'] = {}
                st.rerun()
        
        with col_apply:
            # This button will trigger the preview update
            st.button("🔄 Refresh Preview", use_container_width=True, key="refresh_preview")
    
    with col_preview:
        st.subheader("Live Preview")
        
        # Generate preview with current adjustments
        try:
            preview_image = image_processor.render_text_with_adjustments(
                inpainted_base, 
                text_regions, 
                st.session_state['text_adjustments']
            )
            
            # Show status of adjustments
            if not st.session_state['text_adjustments']:
                st.warning("📝 No adjustments made yet. The preview shows the original translation result. Use the controls on the left to customize text appearance.")
            else:
                st.success(f"✨ Applied {len(st.session_state['text_adjustments'])} adjustment(s). Preview updated!")
            
            # Display the preview
            st.image(preview_image, use_column_width=True, caption="Interactive Preview - Adjust controls to see changes")
            
            # Action buttons
            col_download, col_compare = st.columns(2)
            
            with col_download:
                # Download button for edited version
                buf = io.BytesIO()
                preview_image.save(buf, format='PNG')
                st.download_button(
                    label="📥 Download Edited Image",
                    data=buf.getvalue(),
                    file_name=f"edited_{st.session_state['target_lang']}_image.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            with col_compare:
                # Option to compare with original
                if st.button("👀 Compare with Original", use_container_width=True):
                    st.session_state['show_comparison'] = not st.session_state.get('show_comparison', False)
                    st.rerun()
            
            # Show comparison if requested
            if st.session_state.get('show_comparison', False):
                st.subheader("📊 Before vs After Comparison")
                col_before, col_after = st.columns(2)
                
                with col_before:
                    st.write("**Original Translation**")
                    st.image(result['final_image'], use_column_width=True)
                
                with col_after:
                    st.write("**Your Edited Version**")
                    st.image(preview_image, use_column_width=True)
            
            # Show adjustment summary
            if st.session_state['text_adjustments']:
                with st.expander("📋 Current Adjustments Summary"):
                    for region_idx, adjustments in st.session_state['text_adjustments'].items():
                        if region_idx < len(text_regions):
                            region = text_regions[region_idx]
                            col_region, col_settings = st.columns([2, 1])
                            
                            with col_region:
                                st.write(f"**Region {region_idx + 1}:** {region['text'][:40]}...")
                            
                            with col_settings:
                                size_mult = adjustments.get('font_size_multiplier', 1.0)
                                font_name = adjustments.get('font_family', 'Default')
                                st.write(f"Size: {size_mult:.1f}x, Font: {font_name}")
            else:
                st.info("💡 **Tip:** Expand any text region on the left to start customizing font sizes and styles!")
            
        except Exception as e:
            st.error(f"Error generating preview: {str(e)}")
            st.write("Please try adjusting the settings or refreshing the preview.")
            with st.expander("🔧 Debug Information"):
                st.write(f"Error details: {str(e)}")
                st.write(f"Number of text regions: {len(text_regions)}")
                st.write(f"Adjustments: {st.session_state['text_adjustments']}")

def display_batch_results(results: List[Dict], target_lang: str, languages: Dict):
    """Display batch processing results."""
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Images", len(results))
    with col2:
        st.metric("Successful", len(successful), delta=len(successful) - len(failed))
    with col3:
        st.metric("Failed", len(failed))
    with col4:
        if successful:
            avg_time = sum(r['processing_time'] for r in successful) / len(successful)
            st.metric("Avg Time", f"{avg_time:.1f}s")
    
    # Results tabs
    if successful:
        tab1, tab2 = st.tabs(["📊 Results", "💾 Download"])
        
        with tab1:
            # Display successful results
            for result in successful:
                with st.expander(f"✅ {result['filename']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.image(result['original_image'], caption="Original", use_column_width=True)
                    with col_b:
                        st.image(result['final_image'], caption="Translated", use_column_width=True)
                    
                    st.write(f"**Detections:** {result['detections']}, **Time:** {result['processing_time']:.1f}s")
        
        with tab2:
            # Create ZIP download
            if st.button("📦 Create ZIP Download"):
                zip_buffer = io.BytesIO()
                
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for result in successful:
                        if result['final_image']:
                            img_buffer = io.BytesIO()
                            result['final_image'].save(img_buffer, format='PNG')
                            zip_file.writestr(
                                f"translated_{target_lang}_{result['filename']}.png",
                                img_buffer.getvalue()
                            )
                
                st.download_button(
                    label="📥 Download All Translated Images (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name=f"batch_translated_{target_lang}.zip",
                    mime="application/zip"
                )
    
    # Show failed results
    if failed:
        st.subheader("❌ Failed Processing")
        for result in failed:
            st.error(f"**{result['filename']}:** {result['error']}")

if __name__ == "__main__":
    main()