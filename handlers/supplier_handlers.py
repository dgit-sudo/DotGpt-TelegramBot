from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from strings import get_string, STRINGS
from translation_utils import get_all_languages, get_language_name
from database_helpers import (
    get_or_create_supplier,
    get_supplier,
    get_supplier_chats,
    get_products_by_supplier,
)
from handlers.language_selection import ensure_terms_accepted
from config import ADMIN_IDS
import logging

logger = logging.getLogger(__name__)

# Conversation states
ENTER_COMPANY_NAME = 1
SELECT_SUPPLIER_LANGUAGE = 2

async def supplier_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle supplier registration - ask for language first"""
    user_id = update.effective_user.id
    user = update.effective_user
    language = context.user_data.get('language', 'en')

    if not await ensure_terms_accepted(update, context, language):
        return
    
    supplier = get_supplier(user_id)
    
    if supplier:
        # Existing supplier
        if supplier.is_banned:
            await update.message.reply_text(
                get_string("supplier_banned", language),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_string("menu", language), callback_data="buyer_menu")]
                ])
            )
            return
        
        if supplier.status == "pending":
            await update.message.reply_text(
                get_string("supplier_pending", language),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(get_string("menu", language), callback_data="buyer_menu")]
                ])
            )
            return
        
        if supplier.status == "verified":
            # Show supplier dashboard
            await show_supplier_dashboard(update, context, language, supplier)
            return
        
        # Status is rejected
        await update.message.reply_text(
            get_string("supplier_rejected", language),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_string("menu", language), callback_data="buyer_menu")]
            ])
        )
        return
    
    # New supplier - first ask for language preference
    await show_supplier_language_selection(update, context, language)

async def show_supplier_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, buyer_language: str):
    """Show language selection for supplier (seller dashboard language)"""
    query = update.callback_query
    user = update.effective_user
    
    # Get all available languages
    all_languages = get_all_languages()
    
    message = f"""
🌐 {get_string('language_select', buyer_language)}

📌 {get_string('supplier_language_select', buyer_language)}

{get_string('supplier_language_note', buyer_language)}
"""
    
    # Create language selection buttons (in 2x2 grid, with pagination)
    buttons = []
    lang_items = list(all_languages.items())
    
    for i in range(0, len(lang_items), 2):
        row = []
        for j in range(2):
            if i + j < len(lang_items):
                code, name = lang_items[i + j]
                row.append(InlineKeyboardButton(f"{name}", callback_data=f"supplier_lang_{code}"))
        if row:
            buttons.append(row)
    
    # Add back button
    buttons.append([InlineKeyboardButton(get_string("back", buyer_language), callback_data="buyer_menu")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
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

async def handle_supplier_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle supplier language selection"""
    query = update.callback_query
    user = query.from_user
    language = context.user_data.get('language', 'en')
    
    # Extract language code
    supplier_language = query.data.split("_")[2]
    
    # Validate language code
    all_languages = get_all_languages()
    if supplier_language not in all_languages:
        await query.answer(get_string("invalid_input", language), show_alert=True)
        return
    
    # Store supplier language in context
    context.user_data['supplier_language'] = supplier_language
    
    # Create supplier with language preference
    supplier = get_or_create_supplier(
        user.id,
        user.username or "User",
        f"{user.first_name} {user.last_name or ''}".strip() or "Supplier"
    )
    
    # Update supplier language preference
    from database import SessionLocal
    db = SessionLocal()
    supplier_record = db.query(get_supplier.__globals__['Supplier']).filter(
        get_supplier.__globals__['Supplier'].telegram_id == user.id
    ).first()
    if supplier_record:
        supplier_record.language = supplier_language
        db.commit()
    db.close()
    
    # Send notification to admin about new verification request
    await send_verification_request_to_admin(supplier, context)
    
    # Notify supplier
    lang_name = get_language_name(supplier_language)
    confirmation_message = f"""
✅ {get_string('supplier_language_set', language)}

🌐 {get_string('seller_language', language)}: {lang_name}

{get_string('supplier_request_sent', language)}
"""
    
    await query.edit_message_text(
        text=confirmation_message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("menu", language), callback_data="buyer_menu")]
        ]),
        parse_mode='Markdown'
    )
    
    await query.answer()

async def send_verification_request_to_admin(supplier, context: ContextTypes.DEFAULT_TYPE):
    """Send verification request notification to admin"""
    from database import SessionLocal
    try:
        db = SessionLocal()
        admin_users = db.query(db.bind.table("admin_users")).all()
        
        message = f"""
👤 NEW SUPPLIER VERIFICATION REQUEST

Company: {supplier.company_name}
Telegram ID: {supplier.telegram_id}
Username: @{supplier.username}

Click /admin to review and verify or reject.
        """
        
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=message
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
    except Exception as e:
        logger.error(f"Error sending verification request: {e}")

async def show_supplier_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str, supplier):
    """Show supplier dashboard"""
    # Check if auto-translate is enabled
    auto_translate_status = get_string("auto_translate_enabled", language) if supplier.auto_translate else get_string("auto_translate_disabled", language)
    
    keyboard = [
        [InlineKeyboardButton(get_string("my_products", language), callback_data="supplier_products")],
        [InlineKeyboardButton(get_string("buyer_inquiries", language), callback_data="supplier_inquiries")],
        [InlineKeyboardButton(get_string("supplier_stats", language), callback_data="supplier_stats")],
        [InlineKeyboardButton(get_string("supplier_settings", language), callback_data="supplier_settings")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
🏪 {get_string("supplier_panel", language)}

{supplier.company_name}
✅ {get_string('success', language)}

🌐 {get_string('seller_language', language)}: {get_language_name(supplier.language)}
{auto_translate_status}

{get_string("start_message", language)}
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
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

async def show_supplier_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show supplier's products"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    supplier = get_supplier(user_id)
    if not supplier:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    products = get_products_by_supplier(supplier.id)
    
    message = f"📦 {get_string('my_products', language)}\n\n"
    
    if not products:
        message += get_string("no_products", language)
    else:
        for product in products:
            message += f"📌 {product.name}\n"
    
    buttons = [
        [InlineKeyboardButton(get_string("back", language), callback_data="supplier_dashboard")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_supplier_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show supplier settings"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    supplier = get_supplier(user_id)
    if not supplier:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Show settings options
    auto_translate_button = (
        get_string("auto_translate_disabled", language)
        if supplier.auto_translate
        else get_string("auto_translate_enabled", language)
    )
    
    message = f"⚙️ {get_string('supplier_settings', language)}\n\n"
    message += f"🌐 {get_string('seller_language', language)}: {get_language_name(supplier.language)}\n"
    message += f"{auto_translate_button}\n\n"
    message += f"{get_string('auto_translate_toggle', language)}"
    
    buttons = [
        [InlineKeyboardButton(auto_translate_button, callback_data="toggle_auto_translate")],
        [InlineKeyboardButton(get_string("back", language), callback_data="supplier_dashboard")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def toggle_auto_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle auto-translate setting for supplier"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    supplier = get_supplier(user_id)
    if not supplier:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Toggle the setting
    from database import SessionLocal, Supplier
    db = SessionLocal()
    supplier_record = db.query(Supplier).filter(Supplier.telegram_id == user_id).first()
    
    if supplier_record:
        supplier_record.auto_translate = not supplier_record.auto_translate
        db.commit()
        new_status = supplier_record.auto_translate
    
    db.close()
    
    # Show updated settings
    await show_supplier_settings(update, context)
    
    status_text = get_string("auto_translate_enabled", language) if new_status else get_string("auto_translate_disabled", language)
    await query.answer(f"Setting updated: {status_text}", show_alert=False)


async def show_supplier_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show supplier statistics with stock information"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    supplier = get_supplier(user_id)
    if not supplier:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Get statistics
    from database_helpers import get_supplier_statistics
    stats = get_supplier_statistics(supplier.id)
    
    if not stats:
        await query.answer(get_string("not_found", language), show_alert=True)
        return
    
    # Build statistics message
    message = f"📈 {get_string('supplier_stats', language)}\n\n"
    message += f"📦 {get_string('products_count', language)}: {stats['product_count']}\n"
    message += f"📊 {get_string('total_stock', language)}: {stats['total_stock']}\n\n"
    
    # Low stock items
    message += f"⚠️ {get_string('low_stock', language)}:\n"
    if stats['low_stock_items']:
        for product_name, stock in stats['low_stock_items']:
            message += f"  • {product_name}: {stock}\n"
    else:
        message += f"  {get_string('no_low_stock', language)}\n"
    
    message += f"\n"
    
    # Out of stock items
    message += f"❌ {get_string('out_of_stock', language)}:\n"
    if stats['out_of_stock_items']:
        for product_name in stats['out_of_stock_items']:
            message += f"  • {product_name}\n"
    else:
        message += f"  {get_string('no_low_stock', language)}\n"
    
    message += f"\n"
    
    # Not tracked items
    message += f"❓ {get_string('not_tracked', language)}:\n"
    if stats['not_tracked_items']:
        for product_name in stats['not_tracked_items']:
            message += f"  • {product_name}\n"
    else:
        message += f"  None\n"
    
    # Buttons - add alert button if there are low stock or out of stock items
    buttons = []
    has_issues = stats['low_stock_items'] or stats['out_of_stock_items']
    
    if has_issues:
        buttons.append([
            InlineKeyboardButton(get_string("send_restock_alert", language), callback_data="send_restock_alert")
        ])
    
    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="supplier_dashboard")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_restock_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle sending restock alert to admins"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    supplier = get_supplier(user_id)
    if not supplier:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    from database_helpers import get_supplier_statistics
    stats = get_supplier_statistics(supplier.id)
    
    # Build alert message for admins
    alert_message = f"""
📢 RESTOCK ALERT

Seller: {supplier.company_name}
Telegram ID: {supplier.telegram_id}

Low Stock Products:
"""
    
    if stats['low_stock_items']:
        for product_name, stock in stats['low_stock_items']:
            alert_message += f"  • {product_name}: {stock} units\n"
    
    alert_message += f"\nOut of Stock Products:\n"
    if stats['out_of_stock_items']:
        for product_name in stats['out_of_stock_items']:
            alert_message += f"  • {product_name}\n"
    else:
        alert_message += "  None\n"
    
    # Send alerts to all admins
    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=alert_message
            )
        except Exception as e:
            logger.error(f"Failed to send alert to admin {admin_id}: {e}")
    
    await query.answer(get_string("alert_sent", language), show_alert=True)
    await show_supplier_statistics(update, context)


    """Show buyer inquiries for supplier"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    supplier = get_supplier(user_id)
    if not supplier:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    chats = get_supplier_chats(supplier.id)
    
    message = f"📬 {get_string('buyer_inquiries', language)}\n\n"
    message += get_string("buyer_profile_hidden", language) + "\n\n"
    
    if not chats:
        message += get_string("no_chats", language)
        buttons = [[InlineKeyboardButton(get_string("back", language), callback_data="supplier_dashboard")]]
    else:
        buttons = []
        for chat in chats:
            message += f"💬 Chat #{chat.id} - "
            message += f"Product: {chat.product.name if chat.product else 'General'}\n"
            
            buttons.append([
                InlineKeyboardButton(f"💬 Chat #{chat.id}", callback_data=f"chat_open_{chat.id}")
            ])
        
        buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="supplier_dashboard")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_supplier_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle supplier-related actions"""
    query = update.callback_query
    language = context.user_data.get('language', 'en')
    
    # Handle special non-supplier prefixed actions
    if query.data == "toggle_auto_translate":
        await toggle_auto_translate(update, context)
        return
    elif query.data == "send_restock_alert":
        await handle_restock_alert(update, context)
        return
    
    action = query.data.split("_")[1] if "_" in query.data else query.data
    
    if action == "dashboard" or action == "menu":
        user_id = update.effective_user.id
        supplier = get_supplier(user_id)
        await show_supplier_dashboard(update, context, language, supplier)
    elif action == "register":
        await supplier_panel(update, context)
    elif action == "products":
        await show_supplier_products(update, context)
    elif action == "inquiries":
        await show_supplier_inquiries(update, context)
    elif action == "settings":
        await show_supplier_settings(update, context)
    elif action == "stats":
        await show_supplier_statistics(update, context)
    
    await query.answer()
