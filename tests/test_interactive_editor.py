#!/usr/bin/env python3
"""
Test script for the interactive text editing functionality.
This script tests the new features without requiring Streamlit to run.
"""

import sys
import os
from PIL import Image, ImageDraw
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.image_processor import ImageProcessor

def test_interactive_features():
    """Test the new interactive editing features."""
    print("🧪 Testing Interactive Text Editor Features")
    print("=" * 50)
    
    # Initialize image processor
    print("1. Initializing ImageProcessor...")
    try:
        processor = ImageProcessor()
        print("   ✅ ImageProcessor initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize ImageProcessor: {e}")
        return False
    
    # Test font discovery
    print("\n2. Testing font discovery...")
    try:
        available_fonts = processor.get_available_fonts()
        print(f"   ✅ Found {len(available_fonts)} available fonts:")
        for i, font in enumerate(available_fonts[:5]):  # Show first 5
            print(f"      {i+1}. {font}")
        if len(available_fonts) > 5:
            print(f"      ... and {len(available_fonts) - 5} more")
    except Exception as e:
        print(f"   ❌ Font discovery failed: {e}")
        return False
    
    # Test font name conversion
    print("\n3. Testing font name conversion...")
    try:
        test_font_names = ['Arial', 'Default', 'DejaVu Sans']
        for font_name in test_font_names:
            font_file = processor.get_font_file_from_name(font_name)
            print(f"   '{font_name}' -> '{font_file}'")
        print("   ✅ Font name conversion working")
    except Exception as e:
        print(f"   ❌ Font name conversion failed: {e}")
        return False
    
    # Test text rendering with adjustments
    print("\n4. Testing text rendering with adjustments...")
    try:
        # Create a test image
        test_image = Image.new('RGB', (400, 200), color='white')
        
        # Create mock text regions
        text_regions = [
            {
                'text': 'Hello World',
                'translated_text': 'Привіт Світ',
                'bbox_rect': (50, 50, 150, 30),
                'target_language': 'uk',
                'confidence': 0.95
            },
            {
                'text': 'Test Text',
                'translated_text': 'Тестовий Текст',
                'bbox_rect': (50, 120, 180, 30),
                'target_language': 'uk',
                'confidence': 0.90
            }
        ]
        
        # Test with no adjustments
        result_image = processor.render_text_with_adjustments(
            test_image, text_regions, adjustments={}
        )
        print("   ✅ Rendered text with no adjustments")
        
        # Test with adjustments
        adjustments = {
            0: {'font_size_multiplier': 1.5, 'font_family': None},
            1: {'font_size_multiplier': 0.8, 'font_family': 'Arial.ttf'}
        }
        
        result_image = processor.render_text_with_adjustments(
            test_image, text_regions, adjustments=adjustments
        )
        print("   ✅ Rendered text with adjustments")
        
        # Save test result
        result_image.save('/tmp/test_interactive_render.png')
        print("   ✅ Test result saved to /tmp/test_interactive_render.png")
        
    except Exception as e:
        print(f"   ❌ Text rendering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test text fitting functionality
    print("\n5. Testing text fitting functionality...")
    try:
        test_image = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(test_image)
        
        # Test with long text that needs truncation
        long_text = "This is a very long text that should be truncated or wrapped"
        font = processor.get_best_font(long_text, 16, 'en', False)
        
        fitted_text = processor._fit_text_to_bounds(long_text, 180, 30, font, draw)
        print(f"   Original: '{long_text}'")
        print(f"   Fitted: '{fitted_text}'")
        print("   ✅ Text fitting working")
        
    except Exception as e:
        print(f"   ❌ Text fitting test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Interactive editing features are ready to use.")
    print("\n📝 Summary of new features:")
    print("   - Real-time font size adjustment with multipliers")
    print("   - Font family selection from available system fonts")
    print("   - Intelligent text fitting and wrapping")
    print("   - Streamlit UI with interactive controls")
    print("   - Before/after comparison functionality")
    
    return True

def test_streamlit_components():
    """Test that all required Streamlit components are available."""
    print("\n🌐 Testing Streamlit Integration...")
    
    try:
        import streamlit as st
        print("   ✅ Streamlit is available")
        
        # Test if we can import the enhanced app
        import app_enhanced
        print("   ✅ Enhanced app imports successfully")
        
        print("   ℹ️  To run the interactive editor:")
        print("      streamlit run app_enhanced.py")
        
    except ImportError as e:
        print(f"   ⚠️  Streamlit not available: {e}")
        print("   ℹ️  Install with: pip install streamlit")
    except Exception as e:
        print(f"   ❌ App import error: {e}")

if __name__ == "__main__":
    print("🚀 Interactive Text Editor Test Suite")
    print("=====================================")
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    success = test_interactive_features()
    test_streamlit_components()
    
    if success:
        print("\n✨ Ready to use! Run 'streamlit run app_enhanced.py' to start the interactive editor.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)