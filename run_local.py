#!/usr/bin/env python3
"""
Direct local runner for the image translation app.
"""

import subprocess
import sys
import os
import time

def main():
    print("🌍 Image Translation App Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("app_enhanced.py"):
        print("❌ Error: app_enhanced.py not found")
        print("Please run from the imgtranslation directory")
        return 1
    
    print("🔧 Configuring Streamlit...")
    
    # Set environment variables for better compatibility
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '127.0.0.1'
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    print("✅ Starting app on http://127.0.0.1:8501")
    print("   (If browser doesn't open, manually go to the URL)")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    # Wait a moment
    time.sleep(1)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            'app_enhanced.py',
            '--server.address', '127.0.0.1',
            '--server.port', '8501',
            '--browser.serverAddress', '127.0.0.1'
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped")

if __name__ == "__main__":
    main()