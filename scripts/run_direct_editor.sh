#!/bin/bash

# Direct Manipulation Text Editor Launcher
# This script launches the Google Slides-like text editing interface

echo "🚀 Starting Direct Manipulation Text Editor..."
echo "================================================"

# Check if required dependencies are available
echo "📋 Checking dependencies..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

if ! python3 -c "import streamlit" &> /dev/null; then
    echo "❌ Streamlit is required but not installed."
    echo "💡 Install with: pip install streamlit"
    exit 1
fi

if ! python3 -c "from core import OCREngine, TranslationEngine, ImageProcessor" &> /dev/null; then
    echo "❌ Core modules not found. Please ensure you're in the correct directory."
    exit 1
fi

echo "✅ All dependencies available"

# Run tests first to ensure everything works
echo ""
echo "🧪 Running tests to ensure everything works..."
if python3 test_direct_editor.py; then
    echo "✅ All tests passed!"
else
    echo "❌ Tests failed. Please check the errors above."
    exit 1
fi

echo ""
echo "🌟 Launching Direct Manipulation Text Editor..."
echo ""
echo "📖 How to use:"
echo "   1. Upload an image with text"
echo "   2. Click 'Translate Image'"
echo "   3. Click directly on text in the image to edit it"
echo "   4. Use the floating control panel to adjust font size and style"
echo "   5. Download your edited result"
echo ""
echo "🎯 Features:"
echo "   • Click directly on text (like Google Slides)"
echo "   • Floating control panel appears near selected text"
echo "   • Real-time preview updates"
echo "   • Keyboard shortcuts (+/- for size, Esc to close)"
echo "   • Mobile responsive design"
echo ""
echo "🔧 Keyboard shortcuts:"
echo "   • Esc: Close control panel"
echo "   • +/=: Increase font size"
echo "   • -: Decrease font size"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Launch Streamlit app
streamlit run direct_edit_app.py