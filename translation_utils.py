"""
Translation utilities for multi-language support.
Supports all world languages with automatic translation.
"""

import asyncio
import logging
from typing import Optional, Dict

try:
    from googletrans import Translator, LANGUAGES
    GOOGLETRANS_AVAILABLE = True
except Exception:
    Translator = None
    LANGUAGES = {}
    GOOGLETRANS_AVAILABLE = False

from config import SUPPORTED_LANGUAGES
from strings import STRINGS

logger = logging.getLogger(__name__)

FALLBACK_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "ru": "Russian",
    "zh": "Chinese (Simplified)",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "bn": "Bengali",
    "tr": "Turkish",
    "id": "Indonesian",
    "vi": "Vietnamese",
    "th": "Thai",
    "pl": "Polish",
    "uk": "Ukrainian",
    "nl": "Dutch",
    "el": "Greek",
    "sv": "Swedish",
    "da": "Danish",
    "no": "Norwegian",
    "fi": "Finnish",
    "cs": "Czech",
    "hu": "Hungarian",
    "ro": "Romanian",
    "sr": "Serbian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "sl": "Slovenian",
    "sk": "Slovak",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "mt": "Maltese",
    "ga": "Irish",
    "cy": "Welsh",
    "be": "Belarusian",
    "ka": "Georgian",
    "hy": "Armenian",
    "az": "Azerbaijani",
    "kk": "Kazakh",
    "uz": "Uzbek",
    "tk": "Turkmen",
    "tg": "Tajik",
    "ky": "Kyrgyz",
    "mn": "Mongolian",
    "fa": "Persian",
    "ur": "Urdu",
    "pa": "Punjabi",
    "gu": "Gujarati",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "si": "Sinhala",
    "my": "Burmese",
    "km": "Khmer",
    "lo": "Lao",
    "jv": "Javanese",
    "su": "Sundanese",
    "ms": "Malay",
    "fil": "Filipino",
    "ceb": "Cebuano",
    "eo": "Esperanto",
    "ca": "Catalan",
    "gl": "Galician",
    "eu": "Basque",
    "sq": "Albanian",
    "mk": "Macedonian",
    "is": "Icelandic",
    "af": "Afrikaans",
    "zu": "Zulu",
    "xh": "Xhosa",
    "yo": "Yoruba",
    "ig": "Igbo",
    "sw": "Swahili",
    "ha": "Hausa",
    "am": "Amharic",
    "ti": "Tigrinya",
    "rw": "Kinyarwanda",
    "som": "Somali",
    "ckb": "Kurdish (Central)",
    "ps": "Pashto",
    "as": "Assamese",
    "or": "Odia",
    "kok": "Konkani",
    "doi": "Dogri",
    "mni": "Manipuri",
    "sat": "Santali",
    "brx": "Bodo",
    "mai": "Maithili",
    "ne": "Nepali",
    "new": "Newari",
    "bo": "Tibetan",
    "dz": "Dzongkha",
    "snd": "Sindhi",
    "cmn": "Mandarin Chinese",
    "cdo": "Min Dong Chinese",
    "wuu": "Wu Chinese",
    "yue": "Cantonese",
    "hsn": "Xiang Chinese",
    "gan": "Gan Chinese",
    "hak": "Hakka Chinese",
}

# Build language names from STRINGS
ALL_LANGUAGES = {}
for lang_code in SUPPORTED_LANGUAGES:
    # Try to get from language_changed string in STRINGS
    if lang_code in STRINGS and "language_changed" in STRINGS[lang_code]:
        # Extract language name from "Language changed to {name}" string
        changed_str = STRINGS[lang_code]["language_changed"]  # e.g., "Language changed to English ✓"
        parts = changed_str.split("to ")
        if len(parts) > 1:
            name = parts[1].replace(" ✓", "").strip()
            ALL_LANGUAGES[lang_code] = name
        else:
            ALL_LANGUAGES[lang_code] = FALLBACK_LANGUAGES.get(lang_code, lang_code)
    else:
        ALL_LANGUAGES[lang_code] = FALLBACK_LANGUAGES.get(lang_code, lang_code)

# Initialize translator if available
translator = Translator() if GOOGLETRANS_AVAILABLE else None

# Cache for translations to avoid repeated API calls
translation_cache: Dict[str, str] = {}

# Map of language names to language codes
LANGUAGE_MAP = {
    lang_name.lower(): lang_code
    for lang_code, lang_name in ALL_LANGUAGES.items()
}

# Reverse map for getting language name from code
LANGUAGE_NAMES = ALL_LANGUAGES.copy()


def get_all_languages() -> Dict[str, str]:
    """
    Get all supported languages.
    
    Returns:
        Dict: Language code -> Language name mapping
        Example: {'en': 'English', 'es': 'Spanish', ...}
    """
    return ALL_LANGUAGES.copy()


def get_language_code(language_name: str) -> Optional[str]:
    """
    Get language code from language name.
    
    Args:
        language_name: Name of language (e.g., 'English', 'Spanish')
    
    Returns:
        Language code (e.g., 'en', 'es') or None if not found
    """
    name_lower = language_name.lower()
    
    # Try exact match first
    if name_lower in LANGUAGE_MAP:
        return LANGUAGE_MAP[name_lower]
    
    # Try first word match (for compound names)
    first_word = name_lower.split()[0]
    if first_word in LANGUAGE_MAP:
        return LANGUAGE_MAP[first_word]
    
    return None


def get_language_name(language_code: str) -> str:
    """
    Get language name from language code.
    
    Args:
        language_code: Language code (e.g., 'en', 'es')
    
    Returns:
        Language name (e.g., 'English', 'Spanish')
    """
    return ALL_LANGUAGES.get(language_code, f"Unknown ({language_code})")


async def translate_text(
    text: str,
    source_lang: str = 'auto',
    target_lang: str = 'en'
) -> str:
    """
    Translate text from source language to target language.
    
    Args:
        text: Text to translate
        source_lang: Source language code (default: 'auto' for auto-detect)
        target_lang: Target language code (default: 'en' for English)
    
    Returns:
        Translated text
    """
    # Don't translate empty text
    if not text or len(text.strip()) == 0:
        return text
    
    # If same language, no need to translate
    if source_lang == target_lang and source_lang != 'auto':
        return text
    
    # Check cache first
    cache_key = f"{text[:50]}_{source_lang}_{target_lang}"
    if cache_key in translation_cache:
        return translation_cache[cache_key]
    
    if translator is None:
        return text

    try:
        # Run translation in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: translator.translate(
                text,
                src=source_lang if source_lang else 'auto',
                dest=target_lang
            )
        )
        
        translated = result['text'] if isinstance(result, dict) else result.text
        
        # Cache the result
        translation_cache[cache_key] = translated
        
        return translated
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text  # Return original text if translation fails


async def translate_message(
    message: str,
    buyer_language: str,
    supplier_language: str,
    sender_type: str = 'buyer'
) -> str:
    """
    Translate a chat message between buyer and supplier.
    
    If sender is buyer, translate from buyer's language to supplier's language.
    If sender is supplier, translate from supplier's language to buyer's language.
    
    Args:
        message: The message text
        buyer_language: Buyer's preferred language code
        supplier_language: Supplier's preferred language code
        sender_type: 'buyer' or 'supplier'
    
    Returns:
        Translated message (or original if same language or error)
    """
    if sender_type == 'buyer':
        # Message from buyer to supplier (buyer lang -> supplier lang)
        return await translate_text(message, buyer_language, supplier_language)
    else:
        # Message from supplier to buyer (supplier lang -> buyer lang)
        return await translate_text(message, supplier_language, buyer_language)


def get_supported_language_list(limit: Optional[int] = None) -> Dict[str, str]:
    """
    Get list of supported languages for display in bot.
    
    Args:
        limit: Maximum number of languages to return (None for all)
    
    Returns:
        Dict of language codes to names, sorted alphabetically
    """
    langs = dict(sorted(ALL_LANGUAGES.items(), key=lambda x: x[1]))
    
    if limit:
        # Return most popular languages first
        popular = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh-cn', 'ja', 'ko']
        popular_langs = {k: langs[k] for k in popular if k in langs}
        
        if len(popular_langs) < limit:
            remaining = {k: v for k, v in langs.items() if k not in popular_langs}
            popular_langs.update(dict(list(remaining.items())[:limit - len(popular_langs)]))
        
        return popular_langs
    
    return langs


def clear_translation_cache():
    """Clear the translation cache to free memory."""
    global translation_cache
    translation_cache.clear()
    logger.info("Translation cache cleared")


# Language selection interface text (multilingual)
LANGUAGE_UI_TEXT = {
    'en': "Select your language (Tap to see more):",
    'es': "Selecciona tu idioma (Toca para ver más):",
    'fr': "Sélectionnez votre langue (Appuyez pour voir plus):",
    'de': "Wählen Sie Ihre Sprache (Tippen Sie auf Mehr anzeigen):",
    'it': "Seleziona la tua lingua (Tocca per visualizzare di più):",
    'pt': "Selecione seu idioma (Toque para ver mais):",
    'ru': "Выберите свой язык (Нажмите, чтобы увидеть больше):",
    'ja': "言語を選択してください (タップして詳細を表示):",
    'zh-cn': "选择您的语言 (点击查看更多):",
    'ko': "언어를 선택하세요 (더보기를 탭하세요):",
}


def get_language_selection_text(user_language: str = 'en') -> str:
    """
    Get language selection prompt in user's language.
    
    Args:
        user_language: User's preferred language code
    
    Returns:
        Language selection text in user's language
    """
    return LANGUAGE_UI_TEXT.get(user_language, LANGUAGE_UI_TEXT['en'])
