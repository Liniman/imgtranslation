#!/usr/bin/env python3
"""
Setup script to configure DeepL API for better translation quality.
"""

import os
import sys

def setup_deepl_api():
    """Guide user through DeepL API setup."""
    
    print("🌍 DeepL API Setup for Enhanced Translation")
    print("=" * 50)
    print()
    print("DeepL provides superior context-aware translation quality compared to Google Translate.")
    print("This is especially important for marketing brand images that may appear on websites.")
    print()
    
    # Check if API key already exists
    existing_key = os.getenv('DEEPL_API_KEY')
    if existing_key:
        print(f"✅ DeepL API key already configured: {existing_key[:8]}...")
        response = input("Do you want to update it? (y/N): ").lower()
        if response != 'y':
            print("👍 Keeping existing API key")
            return
    
    print("📝 To get started:")
    print("1. Go to https://www.deepl.com/pro-api")
    print("2. Sign up for a free account (500,000 characters/month free)")
    print("3. Copy your API key from the account settings")
    print()
    
    api_key = input("Enter your DeepL API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Translation will fall back to Google Translate.")
        return
    
    # Validate API key format (DeepL keys end with :fx for free tier)
    if not (api_key.endswith(':fx') or len(api_key) >= 20):
        print("⚠️  Warning: This doesn't look like a valid DeepL API key.")
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            return
    
    # Set up environment variable
    env_file = '.env'
    env_content = f"DEEPL_API_KEY={api_key}\n"
    
    # Check if .env exists and update it
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        # Remove existing DEEPL_API_KEY lines
        lines = [line for line in lines if not line.startswith('DEEPL_API_KEY')]
        
        # Add new key
        lines.append(env_content)
        
        with open(env_file, 'w') as f:
            f.writelines(lines)
    else:
        with open(env_file, 'w') as f:
            f.write(env_content)
    
    # Set for current session
    os.environ['DEEPL_API_KEY'] = api_key
    
    print()
    print("✅ DeepL API key configured successfully!")
    print(f"📁 Saved to: {os.path.abspath(env_file)}")
    print()
    print("🔄 To use the new API key:")
    print("   1. Restart your terminal/IDE")
    print("   2. Or run: source .env")
    print("   3. Run the translation app again")
    print()
    print("💡 The translation engine will now use DeepL for much better quality!")

def test_deepl_connection():
    """Test the DeepL API connection."""
    try:
        from core.translator import TranslationEngine
        
        print("\n🧪 Testing DeepL API connection...")
        
        # Initialize with DeepL as primary
        translator = TranslationEngine(primary_provider='deepl')
        
        # Test translation
        test_text = "Take 1 liquid softgel daily"
        result, quality = translator.translate_text(test_text, 'uk')
        
        if quality > 0.5:
            print(f"✅ DeepL API working! Test translation:")
            print(f"   '{test_text}' → '{result}' (quality: {quality:.2f})")
        else:
            print("⚠️  DeepL API may not be working properly. Check your API key.")
            
    except Exception as e:
        print(f"❌ Error testing DeepL API: {e}")
        print("💡 Make sure you've installed requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    setup_deepl_api()
    
    # Test connection if requested
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_deepl_connection()