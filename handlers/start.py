from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from strings import STRINGS
from translation_utils import get_all_languages, get_language_name
from config import SUPPORTED_LANGUAGES
import logging

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler - Show language selection with all world languages"""
    user = update.effective_user
    
    # Store user info in context
    context.user_data['user_id'] = user.id
    context.user_data['username'] = user.username or "Anonymous"
    context.user_data['first_name'] = user.first_name
    context.user_data['last_name'] = user.last_name
    context.user_data['lang_page'] = 0  # Page for language selection
    
    # Get user's language (default to English)
    language = context.user_data.get('language', 'en')
    
    await show_language_selection(update, context, page=0)

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0):
    """Show language selection with pagination (6 languages per page)"""
    
    # Get all available languages
    all_languages = get_all_languages()
    lang_codes = sorted(all_languages.keys())
    
    # Define languages per page
    langs_per_page = 6
    total_pages = (len(lang_codes) + langs_per_page - 1) // langs_per_page
    
    # Get languages for current page
    start_idx = page * langs_per_page
    end_idx = start_idx + langs_per_page
    page_langs = lang_codes[start_idx:end_idx]
    
    # Create keyboard
    keyboard = []
    for lang_code in page_langs:
        lang_name = all_languages[lang_code]
        keyboard.append([
            InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
        ])
    
    # Add pagination buttons
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"lang_page_{page-1}"))
    
    pagination_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
    
    if page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"lang_page_{page+1}"))
    
    if pagination_buttons:
        keyboard.append(pagination_buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
🛍️ *{STRINGS['en']['welcome']}*

🌐 *We support 100+ languages!*

{STRINGS['en']['language_select']}

Page {page+1}/{total_pages}
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
