#!/usr/bin/env python3
"""
Test script for the direct manipulation text editor.
This validates the core functionality before running the Streamlit app.
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont
import json
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.image_processor import ImageProcessor

def create_test_image_with_text() -> tuple:
    """
    Create a test image with text and mock text regions for testing.
    
    Returns:
        Tuple of (test_image, mock_text_regions)
    """
    # Create a test image
    image = Image.new('RGB', (600, 400), color='lightblue')
    draw = ImageDraw.Draw(image)
    
    # Add some test text to the image
    try:
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_medium = ImageFont.truetype("arial.ttf", 18)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Draw test text
    draw.text((50, 50), "Welcome to Our Store", font=font_large, fill='black')
    draw.text((50, 100), "Special Offers Today!", font=font_medium, fill='darkblue')
    draw.text((50, 150), "Fresh Fruits & Vegetables", font=font_medium, fill='darkgreen')
    draw.text((50, 200), "Open 24/7", font=font_large, fill='red')
    
    # Create mock text regions that would come from OCR
    mock_regions = [
        {
            'text': 'Welcome to Our Store',
            'translated_text': 'Ласкаво просимо до нашого магазину',
            'bbox_rect': (50, 50, 200, 30),
            'target_language': 'uk',
            'confidence': 0.95,
            'is_bold': True
        },
        {
            'text': 'Special Offers Today!',
            'translated_text': 'Спеціальні пропозиції сьогодні!',
            'bbox_rect': (50, 100, 180, 25),
            'target_language': 'uk',
            'confidence': 0.92,
            'is_bold': False
        },
        {
            'text': 'Fresh Fruits & Vegetables',
            'translated_text': 'Свіжі фрукти та овочі',
            'bbox_rect': (50, 150, 220, 25),
            'target_language': 'uk',
            'confidence': 0.88,
            'is_bold': False
        },
        {
            'text': 'Open 24/7',
            'translated_text': 'Відкрито 24/7',
            'bbox_rect': (50, 200, 120, 30),
            'target_language': 'uk',
            'confidence': 0.97,
            'is_bold': True
        }
    ]
    
    return image, mock_regions

def test_image_processor_integration():
    """Test that the ImageProcessor works with our direct editing system."""
    print("🧪 Testing ImageProcessor Integration")
    print("=" * 50)
    
    try:
        # Initialize processor
        processor = ImageProcessor()
        print("✅ ImageProcessor initialized")
        
        # Create test data
        test_image, mock_regions = create_test_image_with_text()
        print("✅ Test image and regions created")
        
        # Test rendering with no adjustments
        result_image = processor.render_text_with_adjustments(
            test_image, mock_regions, adjustments={}
        )
        print("✅ Rendered with no adjustments")
        
        # Test rendering with adjustments
        test_adjustments = {
            0: {'font_size_multiplier': 1.5, 'font_family': None},
            1: {'font_size_multiplier': 0.8, 'font_family': 'Arial.ttf'},
            2: {'font_size_multiplier': 1.2, 'font_family': None},
            3: {'font_size_multiplier': 1.0, 'font_family': 'Default'}
        }
        
        adjusted_image = processor.render_text_with_adjustments(
            test_image, mock_regions, adjustments=test_adjustments
        )
        print("✅ Rendered with adjustments")
        
        # Save test results
        test_output_dir = "/tmp"
        result_image.save(os.path.join(test_output_dir, "test_direct_editor_original.png"))
        adjusted_image.save(os.path.join(test_output_dir, "test_direct_editor_adjusted.png"))
        print(f"✅ Test images saved to {test_output_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ ImageProcessor integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_html_generation():
    """Test HTML generation functions."""
    print("\n🌐 Testing HTML Generation")
    print("=" * 50)
    
    try:
        # Import the functions from our app
        from direct_edit_app import create_clickable_image_html, create_control_panel_html, create_javascript_handler
        
        # Create test data
        test_image, mock_regions = create_test_image_with_text()
        
        # Test clickable image HTML generation
        clickable_html = create_clickable_image_html(test_image, mock_regions, "test-image")
        assert len(clickable_html) > 0
        assert "text-region" in clickable_html
        assert "data-region" in clickable_html
        print("✅ Clickable image HTML generated")
        
        # Test control panel HTML
        control_html = create_control_panel_html()
        assert len(control_html) > 0
        assert "control-panel" in control_html
        assert "size-slider" in control_html
        print("✅ Control panel HTML generated")
        
        # Test JavaScript handler
        test_adjustments = {0: {'font_size_multiplier': 1.2}}
        js_handler = create_javascript_handler(test_adjustments)
        assert len(js_handler) > 0
        assert "selectTextRegion" in js_handler
        assert "adjustSize" in js_handler
        print("✅ JavaScript handler generated")
        
        # Save HTML for manual inspection
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Direct Editor Test</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .test-note {{ background: #e8f4fd; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="test-note">
                <h2>Direct Text Editor Test</h2>
                <p>This is a test of the HTML generation for the direct manipulation interface.</p>
                <p>In the actual Streamlit app, these components would be interactive.</p>
            </div>
            
            <div class="main-container">
                {clickable_html}
                {control_html}
            </div>
            
            {js_handler}
        </body>
        </html>
        """
        
        with open("/tmp/test_direct_editor.html", "w", encoding="utf-8") as f:
            f.write(full_html)
        print("✅ Complete HTML test file saved to /tmp/test_direct_editor.html")
        
        return True
        
    except Exception as e:
        print(f"❌ HTML generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_serialization():
    """Test JSON serialization of adjustments."""
    print("\n📄 Testing JSON Serialization")
    print("=" * 50)
    
    try:
        # Test adjustment serialization
        test_adjustments = {
            0: {'font_size_multiplier': 1.5, 'font_family': 'Arial.ttf'},
            1: {'font_size_multiplier': 0.8, 'font_family': None},
            2: {'font_size_multiplier': 1.2, 'font_family': 'Default'}
        }
        
        # Serialize to JSON
        json_str = json.dumps(test_adjustments)
        print(f"✅ Serialized adjustments: {json_str[:50]}...")
        
        # Deserialize from JSON
        deserialized = json.loads(json_str)
        # Note: JSON converts integer keys to strings, so we need to handle that
        expected = {str(k): v for k, v in test_adjustments.items()}
        assert deserialized == expected
        print("✅ Deserialization successful")
        
        # Test edge cases
        empty_adjustments = {}
        empty_json = json.dumps(empty_adjustments)
        assert json.loads(empty_json) == {}
        print("✅ Empty adjustments handled correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
        return False

def test_font_availability():
    """Test font availability and selection."""
    print("\n🔤 Testing Font Availability")
    print("=" * 50)
    
    try:
        processor = ImageProcessor()
        
        # Get available fonts
        available_fonts = processor.get_available_fonts()
        print(f"✅ Found {len(available_fonts)} available fonts")
        
        # Test font name conversion
        test_fonts = ['Arial', 'Default', 'DejaVu Sans', 'Liberation Sans']
        for font_name in test_fonts:
            font_file = processor.get_font_file_from_name(font_name)
            print(f"   '{font_name}' -> '{font_file}'")
        
        # Test font loading
        test_font = processor.get_best_font("Test Text", 16, 'uk', False)
        assert test_font is not None
        print("✅ Font loading successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Font availability test failed: {e}")
        return False

def run_all_tests():
    """Run all tests for the direct manipulation editor."""
    print("🚀 Direct Manipulation Text Editor Test Suite")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise
    
    # Run tests
    tests = [
        ("ImageProcessor Integration", test_image_processor_integration),
        ("HTML Generation", test_html_generation),
        ("JSON Serialization", test_json_serialization),
        ("Font Availability", test_font_availability)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The direct manipulation editor is ready to use.")
        print("\n🚀 To run the interactive editor:")
        print("   streamlit run direct_edit_app.py")
        print("\n📁 Test files created:")
        print("   /tmp/test_direct_editor_original.png")
        print("   /tmp/test_direct_editor_adjusted.png") 
        print("   /tmp/test_direct_editor.html")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)