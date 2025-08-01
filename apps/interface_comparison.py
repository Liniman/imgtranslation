#!/usr/bin/env python3
"""
Interface comparison script to demonstrate the difference between 
traditional controls and direct manipulation interface.
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(
    page_title="Interface Comparison",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ Traditional vs Direct Manipulation Interface")
st.markdown("Compare the two approaches for editing translated text in images")

# Create sample images for comparison
@st.cache_data
def create_sample_images():
    """Create sample images showing both interfaces."""
    
    # Traditional interface mockup
    traditional = Image.new('RGB', (800, 500), color='white')
    draw = ImageDraw.Draw(traditional)
    
    # Draw traditional interface layout
    # Left panel (controls)
    draw.rectangle([10, 10, 250, 490], outline='gray', width=2)
    draw.text((20, 20), "CONTROLS PANEL", fill='black')
    draw.text((20, 50), "Region 1: 'Welcome'", fill='black')
    draw.text((20, 70), "Font Size: [====|===]", fill='gray')
    draw.text((20, 90), "Font: [Arial     ▼]", fill='gray')
    draw.text((20, 120), "Region 2: 'Special Offers'", fill='black')
    draw.text((20, 140), "Font Size: [===|====]", fill='gray')
    draw.text((20, 160), "Font: [Default   ▼]", fill='gray')
    draw.text((20, 200), "❌ User must scroll", fill='red')
    draw.text((20, 220), "❌ Hard to match controls", fill='red')
    draw.text((20, 240), "❌ Two-step process", fill='red')
    
    # Right panel (preview)  
    draw.rectangle([270, 10, 790, 490], outline='gray', width=2)
    draw.text((280, 20), "PREVIEW", fill='black')
    
    # Sample translated text
    draw.rectangle([300, 80, 500, 110], outline='blue', width=1)
    draw.text((310, 90), "Ласкаво просимо", fill='black')
    
    draw.rectangle([300, 140, 520, 170], outline='blue', width=1)
    draw.text((310, 150), "Спеціальні пропозиції", fill='black')
    
    draw.text((280, 200), "❓ Which control affects", fill='orange')
    draw.text((280, 220), "   which text region?", fill='orange')
    
    # Direct manipulation interface mockup
    direct = Image.new('RGB', (800, 500), color='white')
    draw = ImageDraw.Draw(direct)
    
    # Single main area
    draw.rectangle([10, 10, 790, 490], outline='gray', width=2)
    draw.text((20, 20), "DIRECT MANIPULATION INTERFACE", fill='black')
    
    # Sample translated text with click indicators
    draw.rectangle([100, 80, 300, 110], outline='red', width=3, fill='rgba(255,0,0,0.1)')
    draw.text((110, 90), "Ласкаво просимо", fill='black')
    draw.text((310, 90), "← SELECTED (click to edit)", fill='red')
    
    draw.rectangle([100, 140, 320, 170], outline='blue', width=1)  
    draw.text((110, 150), "Спеціальні пропозиції", fill='black')
    draw.text((330, 150), "← Click to edit", fill='blue')
    
    # Floating control panel
    draw.rectangle([350, 60, 600, 180], outline='black', width=2, fill='white')
    draw.text((360, 70), "🎨 FLOATING CONTROLS", fill='black')
    draw.text((360, 95), "Font Size: [===|====] 1.2x", fill='black')
    draw.text((360, 115), "Font: [Arial     ▼]", fill='black')
    draw.text((360, 140), "[Reset] [Apply]", fill='black')
    draw.text((360, 160), "✨ Appears near selected text", fill='green')
    
    # Benefits
    draw.text((100, 220), "✅ Click directly on text", fill='green')
    draw.text((100, 240), "✅ Contextual controls", fill='green')
    draw.text((100, 260), "✅ Visual feedback", fill='green')
    draw.text((100, 280), "✅ Like Google Slides", fill='green')
    draw.text((100, 300), "✅ Mobile friendly", fill='green')
    
    return traditional, direct

# Display comparison
col1, col2 = st.columns(2)

traditional_img, direct_img = create_sample_images()

with col1:
    st.subheader("❌ Traditional Interface")
    st.image(traditional_img, use_column_width=True)
    
    st.markdown("""
    **Problems:**
    - 📋 Controls separated from preview
    - 🔍 Hard to identify which control affects which text
    - 📱 Poor mobile experience
    - 🔄 Two-step process: find control → see change
    - 😵 Cognitive load to match left and right panels
    """)

with col2:
    st.subheader("✅ Direct Manipulation Interface")
    st.image(direct_img, use_column_width=True)
    
    st.markdown("""
    **Benefits:**
    - 🎯 Click directly on text to edit it
    - 🎨 Floating controls appear where needed
    - 👀 Visual feedback shows what's selected
    - ⚡ Real-time preview updates
    - 📱 Mobile-optimized design
    - 🧠 Intuitive, familiar interaction pattern
    """)

st.divider()

# Feature comparison table
st.subheader("📊 Feature Comparison")

comparison_data = {
    "Feature": [
        "Text Selection",
        "Control Location", 
        "Visual Feedback",
        "Mobile Experience",
        "Learning Curve",
        "Real-time Updates",
        "Keyboard Shortcuts",
        "Accessibility"
    ],
    "Traditional Interface": [
        "Dropdown/List selection",
        "Fixed sidebar panel",
        "Separate preview window",
        "Difficult scrolling",
        "Need to learn mapping",
        "Manual refresh needed",
        "Limited shortcuts",
        "Standard form controls"
    ],
    "Direct Manipulation": [
        "Click directly on text",
        "Floating contextual panel",
        "Inline highlighting",
        "Touch-optimized",
        "Intuitive, familiar",
        "Instant preview updates",
        "+/- size, Esc to close",
        "Enhanced with shortcuts"
    ]
}

st.table(comparison_data)

st.divider()

# Action buttons
st.subheader("🚀 Try the Interfaces")

col_a, col_b, col_c = st.columns(3)

with col_a:
    if st.button("📋 Traditional Interface", use_container_width=True):
        st.info("Run: `streamlit run app_enhanced.py`")

with col_b:
    if st.button("🎯 Direct Manipulation", use_container_width=True, type="primary"):
        st.success("Run: `streamlit run direct_edit_app.py` or `./run_direct_editor.sh`")

with col_c:
    if st.button("🧪 Run Tests", use_container_width=True):
        st.info("Run: `python3 test_direct_editor.py`")

st.divider()

# User experience principles
st.subheader("🎨 UX Design Principles")

col_principle1, col_principle2 = st.columns(2)

with col_principle1:
    st.markdown("""
    **Direct Manipulation Benefits:**
    
    🎯 **Directness**: Users directly manipulate the objects of interest
    
    👁️ **Visibility**: All relevant options are visible in context
    
    🔄 **Immediate Feedback**: Actions have immediate, visible results
    
    ↩️ **Reversibility**: Easy to undo and try different options
    """)

with col_principle2:
    st.markdown("""
    **Implementation Details:**
    
    🖱️ **Click Detection**: HTML overlays with JavaScript event handlers
    
    📱 **Responsive Design**: Adapts to desktop and mobile devices
    
    ⚡ **Performance**: Debounced updates to avoid excessive requests
    
    ♿ **Accessibility**: Keyboard navigation and screen reader support
    """)

# Footer
st.markdown("---")
st.caption("Interface comparison for image translation text editing • Built with Streamlit")