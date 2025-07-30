"""
Translation engine with multiple provider support and quality filtering.
"""

from googletrans import Translator
from typing import List, Dict, Optional, Tuple
import logging
import time
import re

logger = logging.getLogger(__name__)


class TranslationEngine:
    """Enhanced translation engine with fallback providers and quality checks."""
    
    def __init__(self, primary_provider: str = 'google', fallback_providers: List[str] = None):
        """
        Initialize translation engine.
        
        Args:
            primary_provider: Primary translation service ('google')
            fallback_providers: List of fallback providers (currently only 'google')
        """
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or []
        self.providers = {}
        self.translation_cache = {}
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize translation service providers."""
        try:
            # Initialize Google Translate
            if self.primary_provider == 'google' or 'google' in self.fallback_providers:
                self.providers['google'] = Translator()
                logger.info("Google Translate initialized successfully")
            
            logger.info(f"Translation engine initialized with providers: {list(self.providers.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize translation providers: {e}")
            raise
    
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
        
        # Try primary provider first
        result = self._translate_with_provider(cleaned_text, target_lang, source_lang, self.primary_provider)
        
        if result[1] > 0.5:  # Good quality translation
            self.translation_cache[cache_key] = result
            return result
        
        # Try fallback providers if primary failed
        for provider in self.fallback_providers:
            if provider in self.providers:
                logger.info(f"Trying fallback provider: {provider}")
                result = self._translate_with_provider(cleaned_text, target_lang, source_lang, provider)
                if result[1] > 0.5:
                    self.translation_cache[cache_key] = result
                    return result
        
        # Return best attempt or original text
        self.translation_cache[cache_key] = result if result[1] > 0 else (text, 0.0)
        return self.translation_cache[cache_key]
    
    def _translate_with_provider(self, text: str, target_lang: str, source_lang: str, provider: str) -> Tuple[str, float]:
        """
        Translate text using specific provider.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            source_lang: Source language code
            provider: Provider name
            
        Returns:
            Tuple of (translated_text, quality_score)
        """
        if provider not in self.providers:
            logger.error(f"Provider {provider} not available")
            return text, 0.0
        
        try:
            if provider == 'google':
                translator = self.providers['google']
                
                # Handle rate limiting
                time.sleep(0.1)  # Small delay to avoid rate limits
                
                result = translator.translate(text, dest=target_lang, src=source_lang)
                translated = result.text
                
                # Calculate quality score
                quality = self._calculate_translation_quality(text, translated, target_lang)
                
                logger.debug(f"Google Translate: '{text}' -> '{translated}' (quality: {quality:.2f})")
                return translated, quality
                
        except Exception as e:
            logger.error(f"Translation failed with {provider}: {e}")
            return text, 0.0
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for translation.
        
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
        
        # Fix common character substitutions
        char_fixes = {
            '0': 'O',  # Zero to O in some contexts
            '1': 'I',  # One to I in some contexts
            '5': 'S',  # Five to S in some contexts
        }
        
        # Apply fixes only if they make sense contextually
        # This is a simplified approach - more sophisticated methods would use language models
        
        return cleaned.strip()
    
    def _calculate_translation_quality(self, original: str, translated: str, target_lang: str) -> float:
        """
        Calculate translation quality score.
        
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
        
        # Check for untranslated parts (still in original language)
        if target_lang == 'uk':  # Ukrainian
            # If translating to Ukrainian, check for Latin characters
            latin_chars = sum(1 for c in translated if c.isascii() and c.isalpha())
            total_chars = sum(1 for c in translated if c.isalpha())
            if total_chars > 0 and latin_chars / total_chars > 0.7:
                score *= 0.3  # Likely not translated properly
        
        # Check for common translation errors
        error_indicators = [
            'Error',
            'Failed',
            'Unable',
            '错误',  # Chinese error
            'エラー',  # Japanese error
        ]
        
        if any(indicator in translated for indicator in error_indicators):
            score *= 0.1
        
        # Bonus for reasonable character diversity
        unique_chars = len(set(translated.lower()))
        if unique_chars > 3:  # At least some character diversity
            score *= 1.1
        
        return min(score, 1.0)
    
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