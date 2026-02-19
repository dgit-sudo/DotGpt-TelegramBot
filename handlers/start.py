from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from strings import STRINGS
from translation_utils import get_all_languages, get_language_name
from config import SUPPORTED_LANGUAGES
from database_helpers import get_buyer, get_chat
import logging

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler - Show language selection with all world languages"""
    user = update.effective_user

    buyer = get_buyer(user.id)
    current_chat_id = context.user_data.get('current_chat')
    if buyer and current_chat_id:
        active_chat = get_chat(current_chat_id)
        if active_chat and active_chat.active and active_chat.buyer_id == buyer.id:
            await update.message.reply_text("💬 You already have an active chat. Wait for the seller to end it.")
            return
        context.user_data.pop('current_chat', None)
    
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
    """Show language selection with pagination
    
    Page 0: English, Persian, Burmese, Indonesian, Russian (featured languages)
    Page 1+: All other languages (6 per page)
    """
    
    # Featured languages for first page
    featured_langs = ["en", "fa", "my", "id", "ru"]
    
    # Get all available languages
    all_languages = get_all_languages()
    
    # Create list of remaining languages (all except featured)
    all_lang_codes = sorted(all_languages.keys())
    remaining_langs = [code for code in all_lang_codes if code not in featured_langs]
    
    # Define languages per page for remaining languages
    langs_per_page = 6
    total_remaining_pages = (len(remaining_langs) + langs_per_page - 1) // langs_per_page
    total_pages = 1 + total_remaining_pages  # 1 for featured page + remaining pages
    
    # Build keyboard based on current page
    keyboard = []
    
    if page == 0:
        # Show featured languages on first page
        for lang_code in featured_langs:
            if lang_code in all_languages:
                lang_name = all_languages[lang_code]
                keyboard.append([
                    InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
                ])
        
        # Add pagination buttons if there are more pages
        pagination_buttons = []
        if total_pages > 1:
            pagination_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
            pagination_buttons.append(InlineKeyboardButton("More languages ➡️", callback_data="lang_page_1"))
        
        if pagination_buttons:
            keyboard.append(pagination_buttons)
    else:
        # Show remaining languages on pages 1+
        page_idx = page - 1  # Convert to index for remaining_langs
        start_idx = page_idx * langs_per_page
        end_idx = start_idx + langs_per_page
        page_langs = remaining_langs[start_idx:end_idx]
        
        for lang_code in page_langs:
            lang_name = all_languages[lang_code]
            keyboard.append([
                InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
            ])
        
        # Add pagination buttons
        pagination_buttons = []
        if page > 1:
            pagination_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"lang_page_{page-1}"))
        elif page == 1:
            pagination_buttons.append(InlineKeyboardButton("⬅️ Featured", callback_data="lang_page_0"))
        
        pagination_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="noop"))
        
        if page < total_pages - 1:
            pagination_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"lang_page_{page+1}"))
        
        if pagination_buttons:
            keyboard.append(pagination_buttons)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if page == 0:
        welcome_message = f"""
🛍️ *{STRINGS['en']['welcome']}*

🌐 *Select your language:*

{STRINGS['en']['language_select']}
"""
    else:
        welcome_message = f"""
🛍️ *{STRINGS['en']['welcome']}*

🌐 *More languages:*

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
