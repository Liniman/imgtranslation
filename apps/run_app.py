"""
Application launcher - choose between original and enhanced versions.
"""

import sys
import os
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description='Launch Image Translation App')
    parser.add_argument(
        '--version', 
        choices=['original', 'enhanced'], 
        default='enhanced',
        help='Choose app version to run (default: enhanced)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8501,
        help='Port to run the app on (default: 8501)'
    )
    
    args = parser.parse_args()
    
    # Determine which app to run
    if args.version == 'original':
        app_file = 'streamlit_app.py'
        print("🚀 Launching Original Image Translator...")
        print("   Features: Basic OCR, single image processing")
    else:
        app_file = 'app_enhanced.py'
        print("🚀 Launching Enhanced Image Translator Pro...")
        print("   Features: Advanced OCR, batch processing, smart fonts, better inpainting")
    
    # Check if app file exists
    if not os.path.exists(app_file):
        print(f"❌ Error: {app_file} not found!")
        return 1
    
    print(f"   Running on: http://localhost:{args.port}")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Run streamlit
    try:
        cmd = [sys.executable, '-m', 'streamlit', 'run', app_file, '--server.port', str(args.port)]
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())