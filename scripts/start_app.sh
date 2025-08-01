#!/bin/bash

echo "🚀 Starting Image Translation App..."
echo "Checking dependencies..."

# Check if we're in the right directory
if [ ! -f "app_enhanced.py" ]; then
    echo "❌ Error: app_enhanced.py not found"
    echo "Please run this script from the imgtranslation directory"
    exit 1
fi

# Kill any existing streamlit processes
echo "Stopping any existing processes..."
lsof -ti:8501 | xargs kill -9 2>/dev/null || true
lsof -ti:8502 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 2

echo "✅ Starting Enhanced Image Translation App..."
echo "🌐 Interface will be available at: http://localhost:8501"
echo "📖 Features: Ukrainian translation, batch processing, smart fonts"
echo "⏹️  Press Ctrl+C to stop"
echo ""

# Start the app
python3 -m streamlit run app_enhanced.py --server.port=8501 --server.address=localhost --server.headless=false