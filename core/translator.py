"""
DeepL-powered translation engine for superior context-aware translation quality.
"""

from typing import List, Dict, Optional, Tuple
import logging
import time
import re
import requests
import os
from .memory_tracker import track_memory, memory_snapshot

logger = logging.getLogger(__name__)

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load .env on import
load_env_file()


class TranslationEngine:
    """DeepL-powered translation engine for superior context-aware translation."""
    
    def __init__(self, primary_provider: str = 'deepl'):
        """
        Initialize translation engine with DeepL only.
        
        Args:
            primary_provider: Translation service (only 'deepl' supported)
        """
        if primary_provider != 'deepl':
            raise ValueError("Only DeepL provider is supported. Use 'deepl' as primary_provider.")
            
        self.primary_provider = primary_provider
        self.fallback_providers = []  # No fallbacks - DeepL only
        self.providers = {}
        self.translation_cache = {}
        
        # DeepL API settings
        self.deepl_api_key = os.getenv('DEEPL_API_KEY')
        self.deepl_free_api = True  # Use free API by default
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize DeepL translation service."""
        try:
            if not self.deepl_api_key:
                raise ValueError(
                    "DeepL API key not found. Please set DEEPL_API_KEY environment variable. "
                    "Run 'python setup_deepl.py' to configure."
                )
            
            # Test DeepL API connection
            self.providers['deepl'] = True
            logger.info("DeepL API initialized successfully")
            logger.info("Translation engine using DeepL exclusively for premium quality")
            
        except Exception as e:
            logger.error(f"Failed to initialize DeepL: {e}")
            raise
    
    @track_memory("translate_text")
    def translate_text(self, text: str, target_lang: str, source_lang: str = 'auto') -> Tuple[str, float]:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code (auto-detect if 'auto')
            
        Returns:
            Tuple of (translated_text, quality_score)
        """
        # Check cache first
        cache_key = f"{text}_{source_lang}_{target_lang}"
        if cache_key in self.translation_cache:
            logger.debug(f"Using cached translation for: {text[:50]}...")
            return self.translation_cache[cache_key]
        
        # Clean and validate input text
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            return text, 0.0
        
        # Use DeepL exclusively
        result = self._translate_with_deepl(cleaned_text, target_lang, source_lang)
        
        # Cache and return result
        self.translation_cache[cache_key] = result
        return result
    
    
    
    def _translate_with_deepl(self, text: str, target_lang: str, source_lang: str) -> Tuple[str, float]:
        """
        Translate text using DeepL API for superior context-aware translation.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code
            
        Returns:
            Tuple of (translated_text, quality_score)
        """
        try:
            # Map language codes to DeepL format
            deepl_target = self._map_to_deepl_lang(target_lang)
            deepl_source = self._map_to_deepl_lang(source_lang) if source_lang != 'auto' else None
            
            if not deepl_target:
                logger.warning(f"Target language {target_lang} not supported by DeepL")
                return text, 0.0
            
            # Use free or pro API endpoint
            if self.deepl_free_api:
                url = "https://api-free.deepl.com/v2/translate"
            else:
                url = "https://api.deepl.com/v2/translate"
            
            # Prepare request
            headers = {
                'Authorization': f'DeepL-Auth-Key {self.deepl_api_key}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'text': text,
                'target_lang': deepl_target,
                'preserve_formatting': '1',  # Maintain text formatting
                'formality': 'default'  # Use default formality level
            }
            
            if deepl_source:
                data['source_lang'] = deepl_source
            
            # Make request with timeout
            response = requests.post(url, headers=headers, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                translated = result['translations'][0]['text']
                detected_source = result['translations'][0].get('detected_source_language', 'unknown')
                
                # Calculate quality score - DeepL typically produces high-quality results
                quality = self._calculate_translation_quality(text, translated, target_lang)
                
                # Boost quality score for DeepL as it's generally more context-aware
                quality = min(quality * 1.2, 1.0)
                
                logger.debug(f"DeepL Translate: '{text}' -> '{translated}' (detected: {detected_source}, quality: {quality:.2f})")
                return translated, quality
                
            elif response.status_code == 403:
                logger.error("DeepL API authentication failed - check API key")
                return text, 0.0
            elif response.status_code == 456:
                logger.error("DeepL API quota exceeded")
                return text, 0.0
            else:
                logger.error(f"DeepL API error: {response.status_code} - {response.text}")
                return text, 0.0
                
        except requests.exceptions.Timeout:
            logger.error("DeepL API request timed out")
            return text, 0.0
        except Exception as e:
            logger.error(f"DeepL translation failed: {e}")
            return text, 0.0
    
    def _map_to_deepl_lang(self, lang_code: str) -> Optional[str]:
        """
        Map language codes to DeepL-supported format.
        
        Args:
            lang_code: Standard language code
            
        Returns:
            DeepL language code or None if not supported
        """
        deepl_mapping = {
            'uk': 'UK',  # Ukrainian
            'en': 'EN',  # English
            'es': 'ES',  # Spanish
            'fr': 'FR',  # French
            'de': 'DE',  # German
            'it': 'IT',  # Italian
            'pt': 'PT',  # Portuguese
            'ru': 'RU',  # Russian
            'ja': 'JA',  # Japanese
            'ko': 'KO',  # Korean
            'zh': 'ZH',  # Chinese
            'nl': 'NL',  # Dutch
            'sv': 'SV',  # Swedish
            'da': 'DA',  # Danish
            'no': 'NB',  # Norwegian (Bokmål)
            'fi': 'FI',  # Finnish
            'pl': 'PL',  # Polish
            'cs': 'CS',  # Czech
            'hu': 'HU',  # Hungarian
            'tr': 'TR',  # Turkish
        }
        return deepl_mapping.get(lang_code.lower())
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for translation with context awareness.
        
        Args:
            text: Raw text from OCR
            
        Returns:
            Cleaned text ready for translation
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common OCR artifacts
        cleaned = re.sub(r'[|\\\/\-_=+~`]{3,}', '', cleaned)  # Remove line artifacts
        cleaned = re.sub(r'\.{4,}', '...', cleaned)  # Normalize multiple dots
        cleaned = re.sub(r',{2,}', ',', cleaned)  # Remove multiple commas
        
        # Basic text normalization (let the AI translate intelligently)
        patterns = {
            r'(\d+)\s*mg': r'\1 mg',  # Fix spacing in dosages
            r'(\d+)\s*mcg': r'\1 mcg',  # Fix spacing in dosages
            r'(\d+)\s*ml': r'\1 ml',  # Fix spacing in volumes
            r'(\d+)\s*%': r'\1%',  # Fix spacing in percentages
        }
        
        for pattern, replacement in patterns.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    def _calculate_translation_quality(self, original: str, translated: str, target_lang: str) -> float:
        """
        Calculate translation quality score with improved detection.
        
        Args:
            original: Original text
            translated: Translated text
            target_lang: Target language code
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        if not translated or translated == original:
            return 0.0
        
        score = 1.0
        
        # Length ratio check
        length_ratio = len(translated) / max(len(original), 1)
        if length_ratio < 0.2 or length_ratio > 5.0:  # Too short or too long
            score *= 0.5
        
        # Check for mixed-language results (major quality issue)
        if target_lang == 'uk':  # Ukrainian
            # Count Latin vs Cyrillic characters
            latin_chars = sum(1 for c in translated if c.isascii() and c.isalpha())
            cyrillic_chars = sum(1 for c in translated if '\u0400' <= c <= '\u04FF')
            total_chars = latin_chars + cyrillic_chars
            
            if total_chars > 0:
                latin_ratio = latin_chars / total_chars
                # Penalize mixed-language results heavily
                if 0.2 < latin_ratio < 0.8:  # Mixed language - bad!
                    score *= 0.2
                elif latin_ratio > 0.8:  # Mostly untranslated - very bad!
                    score *= 0.1
        
        # Check for obvious untranslated English words (but be less strict)
        english_word_pattern = r'\b[a-zA-Z]{3,}\b'
        english_words = re.findall(english_word_pattern, translated)
        if english_words and target_lang not in ['en']:
            # Only penalize if there are many untranslated words
            english_ratio = len(english_words) / max(len(translated.split()), 1)
            if english_ratio > 0.5:  # More than half the words are English
                score *= 0.6
        
        # Check for common translation errors
        error_indicators = [
            'Error', 'Failed', 'Unable',
            '错误', 'エラー',  # Other languages
        ]
        
        if any(indicator in translated for indicator in error_indicators):
            score *= 0.1
        
        # Bonus for good character diversity (but not too much)
        unique_chars = len(set(translated.lower()))
        if 3 < unique_chars < 20:  # Reasonable diversity
            score *= 1.1
        
        return min(score, 1.0)
    
    @track_memory("translate_batch")
    def translate_batch(self, texts: List[str], target_lang: str, source_lang: str = 'auto') -> List[Tuple[str, float]]:
        """
        Translate multiple texts efficiently.
        
        Args:
            texts: List of texts to translate  
            target_lang: Target language code
            source_lang: Source language code
            
        Returns:
            List of (translated_text, quality_score) tuples
        """
        results = []
        
        for text in texts:
            translated, quality = self.translate_text(text, target_lang, source_lang)
            results.append((translated, quality))
            
            # Small delay to avoid rate limiting
            time.sleep(0.05)
        
        return results
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get supported language codes and names.
        
        Returns:
            Dictionary mapping language codes to names
        """
        # Common language codes supported by Google Translate
        return {
            'uk': 'Українська (Ukrainian)',
            'en': 'English',
            'es': 'Español (Spanish)',
            'fr': 'Français (French)',
            'de': 'Deutsch (German)',
            'it': 'Italiano (Italian)',
            'pt': 'Português (Portuguese)',
            'ru': 'Русский (Russian)',
            'ja': '日本語 (Japanese)',
            'ko': '한국어 (Korean)',
            'zh': '中文 (Chinese)',
            'ar': 'العربية (Arabic)',
            'hi': 'हिन्दी (Hindi)',
            'nl': 'Nederlands (Dutch)',
            'sv': 'Svenska (Swedish)',
            'da': 'Dansk (Danish)',
            'no': 'Norsk (Norwegian)',
            'fi': 'Suomi (Finnish)',
            'pl': 'Polski (Polish)',
            'cs': 'Čeština (Czech)',
            'hu': 'Magyar (Hungarian)',
            'tr': 'Türkçe (Turkish)',
            'th': 'ไทย (Thai)',
            'vi': 'Tiếng Việt (Vietnamese)'
        }
    
    def clear_cache(self):
        """Clear translation cache."""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'cached_translations': len(self.translation_cache),
            'cache_size_mb': sum(len(k) + len(str(v)) for k, v in self.translation_cache.items()) / 1024 / 1024
        }