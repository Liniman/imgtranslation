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
    
    def _get_supplement_dictionary(self, target_lang: str) -> Dict[str, str]:
        """Get supplement-specific translation dictionary."""
        if target_lang == 'uk':  # Ukrainian
            return {
                'softgel': 'м\'яка капсула',
                'liquid softgel': 'рідка м\'яка капсула', 
                'capsule': 'капсула',
                'tablet': 'таблетка',
                'daily': 'щодня',
                'take': 'приймайте',
                'take 1': 'приймайте 1',
                'omega-3': 'омега-3',
                'fish oil': 'риб\'ячий жир',
                'triple strength': 'потрійна сила',
                'mg': 'мг',
                'mcg': 'мкг'
            }
        return {}
    
    def _apply_supplement_dictionary(self, text: str, translated: str, target_lang: str) -> str:
        """Apply supplement-specific terminology corrections."""
        dictionary = self._get_supplement_dictionary(target_lang)
        
        # Apply dictionary replacements
        corrected = translated
        for english_term, target_term in dictionary.items():
            # Case-insensitive replacement
            pattern = re.compile(re.escape(english_term), re.IGNORECASE)
            corrected = pattern.sub(target_term, corrected)
        
        return corrected
    
    def _translate_with_provider(self, text: str, target_lang: str, source_lang: str, provider: str) -> Tuple[str, float]:
        """
        Translate text using specific provider with domain-specific improvements.
        
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
                
                # Apply domain-specific corrections
                corrected = self._apply_supplement_dictionary(text, translated, target_lang)
                
                # Calculate quality score on corrected translation
                quality = self._calculate_translation_quality(text, corrected, target_lang)
                
                logger.debug(f"Google Translate: '{text}' -> '{translated}' -> '{corrected}' (quality: {quality:.2f})")
                return corrected, quality
                
        except Exception as e:
            logger.error(f"Translation failed with {provider}: {e}")
            return text, 0.0
    
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
        
        # Context-aware cleaning for supplements/medical text
        # Fix common supplement text patterns
        supplement_patterns = {
            r'Take\s+(\d+)\s+liquid': r'Take \1 liquid softgel',  # Fix incomplete OCR
            r'softgel\s+daily': 'softgel daily',  # Normalize spacing
            r'(\d+)\s*mg': r'\1 mg',  # Fix spacing in dosages
            r'(\d+)\s*mcg': r'\1 mcg',  # Fix spacing in dosages
        }
        
        for pattern, replacement in supplement_patterns.items():
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
        
        # Check for untranslated technical terms that should be translated
        untranslated_terms = ['softgel', 'capsule', 'tablet', 'liquid', 'daily', 'take']
        untranslated_count = sum(1 for term in untranslated_terms 
                               if term.lower() in translated.lower())
        if untranslated_count > 0:
            score *= max(0.3, 1.0 - (untranslated_count * 0.2))
        
        # Check for literal translation issues
        literal_issues = [
            ('liquid', 'рідину'),  # Wrong context - should be about capsules
            ('take 1 liquid', 'візьміть 1 рідину'),  # Completely wrong context
        ]
        
        for original_phrase, bad_translation in literal_issues:
            if original_phrase.lower() in original.lower() and bad_translation.lower() in translated.lower():
                score *= 0.1  # Very bad literal translation
        
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