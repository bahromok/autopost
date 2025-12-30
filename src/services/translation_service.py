"""Translation service with fallback mechanisms."""

from typing import Optional
import translators as ts
from loguru import logger

from src.config.settings import settings


class TranslationService:
    """Service for text translation."""
    
    # Translation backends in order of preference
    BACKENDS = ["bing", "google", "yandex"]
    
    @staticmethod
    def translate(
        text: str,
        target_lang: str,
        source_lang: str = "en",
        backend: Optional[str] = None,
    ) -> str:
        """
        Translate text with fallback mechanisms.
        
        Args:
            text: Text to translate
            target_lang: Target language code (uz, ru, etc.)
            source_lang: Source language code (default: en)
            backend: Preferred backend (default: from settings)
        
        Returns:
            Translated text or original text if translation fails
        """
        if not text or not settings.enable_translation:
            return text
        
        # Determine backends to try
        preferred_backend = backend or settings.translation_backend
        backends_to_try = [preferred_backend] + [
            b for b in TranslationService.BACKENDS if b != preferred_backend
        ]
        
        # Try each backend
        for translator_backend in backends_to_try:
            try:
                logger.info(
                    f"Translating to {target_lang} using {translator_backend}"
                )
                translated = ts.translate_text(
                    text,
                    translator=translator_backend,
                    from_language=source_lang,
                    to_language=target_lang,
                )
                
                if translated and translated != text:
                    logger.success(
                        f"Translation successful with {translator_backend}: "
                        f"{translated[:50]}..."
                    )
                    return translated
                
            except Exception as e:
                logger.warning(
                    f"Translation failed with {translator_backend}: {e}"
                )
                continue
        
        # All backends failed
        logger.error(
            f"All translation backends failed for target language {target_lang}. "
            "Returning original text."
        )
        return text
    
    @staticmethod
    def translate_to_uzbek(text: str) -> str:
        """Translate text to Uzbek."""
        return TranslationService.translate(
            text, target_lang=settings.translation_target_lang
        )
    
    @staticmethod
    def translate_to_russian(text: str) -> str:
        """Translate text to Russian."""
        return TranslationService.translate(
            text, target_lang=settings.translation_secondary_lang
        )
    
    @staticmethod
    def translate_multi(text: str) -> dict:
        """
        Translate text to multiple languages.
        
        Returns:
            Dictionary with language codes as keys and translations as values
        """
        return {
            "en": text,  # Original English
            "uz": TranslationService.translate_to_uzbek(text),
            "ru": TranslationService.translate_to_russian(text),
        }
