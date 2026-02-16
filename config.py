import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dotgpt_bot.db")

# Supported Languages - 100+ world languages
SUPPORTED_LANGUAGES = [
    "en",  # English
    "es",  # Spanish
    "fr",  # French
    "de",  # German
    "it",  # Italian
    "pt",  # Portuguese
    "ja",  # Japanese
    "ru",  # Russian
    "zh",  # Chinese (Simplified)
    "ko",  # Korean
    "ar",  # Arabic
    "hi",  # Hindi
    "bn",  # Bengali
    "tr",  # Turkish
    "id",  # Indonesian
    "vi",  # Vietnamese
    "th",  # Thai
    "pl",  # Polish
    "uk",  # Ukrainian
    "nl",  # Dutch
    "el",  # Greek
    "sv",  # Swedish
    "da",  # Danish
    "no",  # Norwegian
    "fi",  # Finnish
    "cs",  # Czech
    "hu",  # Hungarian
    "ro",  # Romanian
    "sr",  # Serbian
    "bg",  # Bulgarian
    "hr",  # Croatian
    "sl",  # Slovenian
    "sk",  # Slovak
    "et",  # Estonian
    "lv",  # Latvian
    "lt",  # Lithuanian
    "mt",  # Maltese
    "ga",  # Irish
    "cy",  # Welsh
    "be",  # Belarusian
    "ka",  # Georgian
    "hy",  # Armenian
    "az",  # Azerbaijani
    "kk",  # Kazakh
    "uz",  # Uzbek
    "tk",  # Turkmen
    "tg",  # Tajik
    "ky",  # Kyrgyz
    "mn",  # Mongolian
    "fa",  # Persian
    "ur",  # Urdu
    "pa",  # Punjabi
    "gu",  # Gujarati
    "ta",  # Tamil
    "te",  # Telugu
    "kn",  # Kannada
    "ml",  # Malayalam
    "mr",  # Marathi
    "si",  # Sinhala
    "my",  # Burmese
    "km",  # Khmer
    "lo",  # Lao
    "jv",  # Javanese
    "su",  # Sundanese
    "ms",  # Malay
    "fil", # Filipino
    "ceb", # Cebuano
    "eo",  # Esperanto
    "ca",  # Catalan
    "gl",  # Galician
    "eu",  # Basque
    "sq",  # Albanian
    "mk",  # Macedonian
    "is",  # Icelandic
    "af",  # Afrikaans
    "zu",  # Zulu
    "xh",  # Xhosa
    "yo",  # Yoruba
    "ig",  # Igbo
    "sw",  # Swahili
    "ha",  # Hausa
    "am",  # Amharic
    "ti",  # Tigrinya
    "rw",  # Kinyarwanda
    "som", # Somali
    "ckb", # Kurdish (Central)
    "ps",  # Pashto
    "as",  # Assamese
    "or",  # Odia
    "kok", # Konkani
    "doi", # Dogri
    "mni", # Manipuri
    "sat", # Santali
    "kok", # Kokborok
    "brx", # Bodo
    "mai", # Maithili
    "ne",  # Nepali
    "new", # Newari
    "bo",  # Tibetan
    "dz",  # Dzongkha
    "snd", # Sindhi
    "cmn", # Mandarin Chinese
    "cdo", # Min Dong
    "wuu", # Wu Chinese
    "yue", # Cantonese
    "hsn", # Xiang
    "gan", # Gan
    "hak", # Hakka
    "min", # Minangkabau
    "ban", # Balinese
    "mad", # Madurese
]
DEFAULT_LANGUAGE = "en"

# Payment Methods
PAYMENT_METHODS = ["Credit Card", "Bank Transfer", "PayPal", "Cryptocurrency", "Cash on Delivery"]

# Bot States
class UserState:
    """User conversation states"""
    START = "start"
    BROWSING_PRODUCTS = "browsing"
    VIEWING_PRODUCT = "viewing_product"
    IN_CHECKOUT = "checkout"
    SUPPLIER_CHAT = "supplier_chat"
    ADMIN_MENU = "admin_menu"
    MANAGE_PRODUCTS = "manage_products"
    MANAGE_SUPPLIERS = "manage_suppliers"
    MANAGE_BUYERS = "manage_buyers"
    VIEW_CHATS = "view_chats"

# Pagination
ITEMS_PER_PAGE = 5
