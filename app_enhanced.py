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
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
    
    with col2:
        if 'result' in st.session_state:
            result = st.session_state['result']
            
            if result['success']:
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