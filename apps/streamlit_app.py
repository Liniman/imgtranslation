import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from googletrans import Translator
import io

# Page config
st.set_page_config(
    page_title="Image Translator",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 Image Text Translator")
st.write("Upload an image and translate any text within it to your target language.")

# Initialize tools (cache for performance)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ch_sim', 'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko'])

@st.cache_resource  
def load_translator():
    return Translator()

# Core functions from notebook (simplified)
def detect_text(image, reader):
    img_array = np.array(image)
    return reader.readtext(img_array)

def translate_text(text, target_lang, translator):
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except:
        return text

def create_inpaint_mask(image, text_regions, padding=5):
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    
    for bbox, _, _, _ in text_regions:
        points = np.array(bbox)
        min_x, min_y = points.min(axis=0)
        max_x, max_y = points.max(axis=0)
        
        min_x = max(0, min_x - padding)
        min_y = max(0, min_y - padding) 
        max_x = min(image.width, max_x + padding)
        max_y = min(image.height, max_y + padding)
        
        mask_draw.rectangle([min_x, min_y, max_x, max_y], fill=255)
    
    return mask

def simple_inpaint(image, mask):
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    mask_cv = np.array(mask)
    inpainted = cv2.inpaint(img_cv, mask_cv, 3, cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))

def estimate_font_size(bbox, text, image_size):
    points = np.array(bbox)
    height = points[:, 1].max() - points[:, 1].min()
    base_size = height * 0.8
    return max(8, min(int(base_size), 200))

def add_translated_text(image, translated_results):
    result_image = image.copy()
    draw = ImageDraw.Draw(result_image)
    
    for bbox, original, translated, confidence in translated_results:
        font_size = estimate_font_size(bbox, translated, image.size)
        
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        points = np.array(bbox)
        center_x = points[:, 0].mean()
        center_y = points[:, 1].mean()
        
        bbox_text = draw.textbbox((0, 0), translated, font=font)
        text_width = bbox_text[2] - bbox_text[0]
        text_height = bbox_text[3] - bbox_text[1]
        
        text_x = int(center_x - text_width / 2)
        text_y = int(center_y - text_height / 2)
        
        # Draw outline
        for adj_x in range(-2, 3):
            for adj_y in range(-2, 3):
                if adj_x != 0 or adj_y != 0:
                    draw.text((text_x + adj_x, text_y + adj_y), translated,
                             font=font, fill='white')
        
        # Draw main text
        draw.text((text_x, text_y), translated, font=font, fill='black')
    
    return result_image

# UI
col1, col2 = st.columns([1, 2])

with col1:
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an image...", 
        type=['png', 'jpg', 'jpeg'],
        help="Upload an image containing text to translate"
    )
    
    # Language selection
    languages = {
        'es': 'Spanish', 'fr': 'French', 'de': 'German', 'it': 'Italian',
        'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese', 'ko': 'Korean',
        'zh': 'Chinese', 'ar': 'Arabic', 'hi': 'Hindi', 'en': 'English'
    }
    
    target_lang = st.selectbox(
        "Target Language",
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        index=0
    )
    
    if st.button("🚀 Translate Image", type="primary"):
        if uploaded_file is not None:
            with st.spinner("Processing image..."):
                try:
                    # Load image
                    image = Image.open(uploaded_file)
                    
                    # Load tools
                    reader = load_ocr()
                    translator = load_translator()
                    
                    # Process
                    progress = st.progress(0)
                    
                    # Step 1: Detect text
                    st.write("🔍 Detecting text...")
                    results = detect_text(image, reader)
                    progress.progress(25)
                    
                    if not results:
                        st.error("No text detected in the image.")
                        st.stop()
                    
                    # Step 2: Translate
                    st.write(f"🌐 Translating to {languages[target_lang]}...")
                    translated_results = []
                    for bbox, text, confidence in results:
                        translated = translate_text(text, target_lang, translator)
                        translated_results.append((bbox, text, translated, confidence))
                    progress.progress(50)
                    
                    # Step 3: Remove original text
                    st.write("🎨 Removing original text...")
                    mask = create_inpaint_mask(image, translated_results)
                    inpainted_image = simple_inpaint(image, mask)
                    progress.progress(75)
                    
                    # Step 4: Add translated text
                    st.write("✍️ Adding translated text...")
                    final_image = add_translated_text(inpainted_image, translated_results)
                    progress.progress(100)
                    
                    st.success("✅ Translation complete!")
                    
                    # Store results in session state
                    st.session_state.original = image
                    st.session_state.final = final_image
                    st.session_state.translations = [(orig, trans) for _, orig, trans, _ in translated_results]
                    
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
        else:
            st.warning("Please upload an image first.")

with col2:
    if 'final' in st.session_state:
        tab1, tab2 = st.tabs(["Results", "Translation Log"])
        
        with tab1:
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.subheader("Original")
                st.image(st.session_state.original, use_column_width=True)
            
            with col_b:
                st.subheader("Translated")
                st.image(st.session_state.final, use_column_width=True)
            
            # Download button
            buf = io.BytesIO()
            st.session_state.final.save(buf, format='PNG')
            st.download_button(
                label="📥 Download Translated Image",
                data=buf.getvalue(),
                file_name=f"translated_{target_lang}.png",
                mime="image/png"
            )
        
        with tab2:
            st.subheader("Translation Details")
            for i, (original, translated) in enumerate(st.session_state.translations):
                st.write(f"**{i+1}.** `{original}` → `{translated}`")
    else:
        st.info("👆 Upload an image and click 'Translate' to see results here.")

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, EasyOCR, and Google Translate")