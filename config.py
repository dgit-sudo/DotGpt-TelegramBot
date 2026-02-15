import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dotgpt_bot.db")

# Supported Languages
SUPPORTED_LANGUAGES = ["en", "es", "fr", "de", "it", "pt"]
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
