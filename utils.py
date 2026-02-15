"""
Utility functions for DotGPT Bot
"""

from datetime import datetime
from typing import List, Dict, Any
from database_helpers import get_product_price
from strings import get_string

def format_price(price: float, currency: str = "USD") -> str:
    """Format price with currency"""
    return f"${price:.2f} {currency}" if currency == "USD" else f"{price:.2f} {currency}"

def format_datetime(dt: datetime) -> str:
    """Format datetime to readable string"""
    return dt.strftime("%Y-%m-%d %H:%M")

def create_product_message(product, language: str = "en") -> str:
    """Create formatted product display message"""
    message = f"""
📦 {product.name}

{product.description or get_string('no_products', language)}

📂 {get_string('product_details', language)}:
Category: {product.category or 'Uncategorized'}
"""
    return message

def create_supplier_message(supplier, language: str = "en") -> str:
    """Create formatted supplier display message"""
    verify_status = "✅ Verified" if supplier.verified else "⏳ Pending Verification"
    
    message = f"""
🏪 {supplier.company_name}

{supplier.description or 'No description provided'}

Status: {verify_status}
Member Since: {format_datetime(supplier.created_at)}
"""
    return message

def paginate_items(items: List[Any], page: int, items_per_page: int = 5) -> tuple:
    """
    Paginate items
    Returns (items_for_page, total_pages, current_page)
    """
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    
    return items[start_idx:end_idx], total_pages, page

def create_pagination_buttons(current_page: int, total_pages: int, action_prefix: str, language: str = "en"):
    """Create pagination inline buttons"""
    from telegram import InlineKeyboardButton
    from strings import get_string
    
    buttons = []
    
    if current_page > 0:
        buttons.append(InlineKeyboardButton(
            f"⬅️ {get_string('back', language)}",
            callback_data=f"{action_prefix}_page_{current_page - 1}"
        ))
    
    if current_page < total_pages - 1:
        buttons.append(InlineKeyboardButton(
            f"{get_string('next', language)} ➡️",
            callback_data=f"{action_prefix}_page_{current_page + 1}"
        ))
    
    return buttons

def get_user_display_name(user) -> str:
    """Get user's display name (for buyers)"""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    elif user.first_name:
        return user.first_name
    elif user.username:
        return f"@{user.username}"
    else:
        return f"User #{user.id}"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) > max_length:
        return text[:max_length - len(suffix)] + suffix
    return text

def format_chat_message(message, language: str = "en") -> str:
    """Format a single chat message for display"""
    sender_label = "You" if message.sender_type == "self" else get_string('supplier', language) if message.sender_type == "supplier" else get_string('browse_products', language)
    timestamp = format_datetime(message.created_at)
    
    return f"[{timestamp}] {sender_label}: {message.message}"

def is_url(text: str) -> bool:
    """Check if text is a URL"""
    return text.startswith(('http://', 'https://', 'www.'))

def format_currency_options() -> Dict[str, str]:
    """Get available currency options"""
    return {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "INR": "₹",
        "BRL": "R$",
    }
