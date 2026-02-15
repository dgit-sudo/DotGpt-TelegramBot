from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from strings import get_string, STRINGS
from translation_utils import get_language_name
from database_helpers import (
    get_or_create_buyer,
    get_or_create_supplier,
    get_superadmin,
    is_superadmin,
    is_admin,
    make_superadmin,
    get_all_admins
)
from config import ADMIN_IDS
import logging

logger = logging.getLogger(__name__)

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle language selection from any language code"""
    query = update.callback_query
    user = query.from_user
    
    # Extract language code (handles lang_XX format)
    callback_data = query.data
    
    if callback_data.startswith("lang_page_"):
        # Pagination button clicked
        page = int(callback_data.split("_")[2])
        from handlers.start import show_language_selection
        await show_language_selection(update, context, page=page)
        await query.answer()
        return
    
    if callback_data == "noop":
        # Pagination info button (do nothing)
        await query.answer("Select a language to continue", show_alert=False)
        return
    
    # Extract language code
    language = callback_data.split("_")[1]
    
    # Verify it's a valid language code
    from translation_utils import get_all_languages
    valid_languages = get_all_languages()
    
    if language not in valid_languages:
        await query.answer("Invalid language selected", show_alert=True)
        return
    
    # Save language preference
    context.user_data['language'] = language
    
    # Create or update buyer record with language preference
    get_or_create_buyer(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language=language  # Pass language to database
    )
    
    # Check if there's any superadmin - if not, make this user the superadmin
    if get_superadmin() is None and len(get_all_admins()) == 0:
        # This is the first admin user - make them superadmin
        make_superadmin(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        context.user_data['is_superadmin'] = True
        context.user_data['is_admin'] = True
        await query.answer(f"✨ You are the SUPERADMIN! ✨")
    else:
        # Not the first user - check their admin status
        context.user_data['is_superadmin'] = is_superadmin(user.id)
        context.user_data['is_admin'] = is_admin(user.id)
        await query.answer(f"Language changed to {get_language_name(language)}")
    
    # Show main menu
    await show_main_menu(update, context, language)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Show main menu based on user type and their language"""
    user_id = update.effective_user.id
    query = update.callback_query
    
    # Check user type from context or database
    is_superadmin_user = context.user_data.get('is_superadmin', False) or is_superadmin(user_id)
    is_admin_user = context.user_data.get('is_admin', False) or is_admin(user_id)
    
    # Get translated strings for this language
    # Use default English if language not in STRINGS
    lang_strings = STRINGS.get(language, STRINGS["en"])
    
    # Create keyboard based on user type
    keyboard = []
    
    if is_superadmin_user:
        # Superadmin menu with special permissions
        keyboard = [
            [InlineKeyboardButton("👑 Superadmin Panel", callback_data="superadmin_menu")],
            [InlineKeyboardButton(lang_strings.get("admin_panel", "👨‍💼 Admin Panel"), callback_data="admin_menu")],
            [InlineKeyboardButton(lang_strings.get("browse_products", "🛍️ Browse Products"), callback_data="buyer_menu")],
            [InlineKeyboardButton(lang_strings.get("supplier_panel", "📊 Supplier Dashboard"), callback_data="supplier_register")],
        ]
    elif is_admin_user:
        # Regular admin menu
        keyboard = [
            [InlineKeyboardButton(lang_strings.get("admin_panel", "👨‍💼 Admin Panel"), callback_data="admin_menu")],
            [InlineKeyboardButton(lang_strings.get("browse_products", "🛍️ Browse Products"), callback_data="buyer_menu")],
            [InlineKeyboardButton(lang_strings.get("supplier_panel", "📊 Supplier Dashboard"), callback_data="supplier_register")],
        ]
    else:
        # Regular menu - Buyer or Supplier option
        keyboard = [
            [InlineKeyboardButton("👤 " + lang_strings.get("browse_products", "Browse Products"), callback_data="buyer_menu")],
            [InlineKeyboardButton("🏪 " + lang_strings.get("supplier_panel", "Supplier Dashboard"), callback_data="supplier_register")],
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    lang_name = get_language_name(language)
    
    # Add role indicator if admin
    role_text = ""
    if is_superadmin_user:
        role_text = "\n👑 *SUPERADMIN - You can manage other admins*"
    elif is_admin_user:
        role_text = "\n👨‍💼 *You are an Admin*"
    
    message = f"""
{lang_strings.get('welcome', 'Welcome')} 👋

🌐 Language: *{lang_name}*{role_text}

{lang_strings.get('start_message', 'What would you like to do?')}
"""
    
    if query:
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

