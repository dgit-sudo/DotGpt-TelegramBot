from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from strings import get_string
from database_helpers import (
    get_or_create_supplier,
    get_supplier,
    get_supplier_chats,
    get_products_by_supplier,
    create_supplier_verification_request,
)
from config import ADMIN_IDS
import logging

logger = logging.getLogger(__name__)

# Conversation states
ENTER_COMPANY_NAME = 1

async def supplier_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle supplier registration - instant verification request"""
    user_id = update.effective_user.id
    user = update.effective_user
    language = context.user_data.get('language', 'en')
    
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
    
    # New supplier - create with pending status and send verification request
    supplier = get_or_create_supplier(
        user_id, 
        user.username or "User", 
        f"{user.first_name} {user.last_name or ''}".strip() or "Supplier"
    )
    
    # Send notification to admin about new verification request
    await send_verification_request_to_admin(supplier, context)
    
    # Notify supplier
    await update.message.reply_text(
        get_string("supplier_request_sent", language),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("menu", language), callback_data="buyer_menu")]
        ])
    )

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
    keyboard = [
        [InlineKeyboardButton(get_string("my_products", language), callback_data="supplier_products")],
        [InlineKeyboardButton(get_string("buyer_inquiries", language), callback_data="supplier_inquiries")],
        [InlineKeyboardButton(get_string("payment_settings", language), callback_data="supplier_payment")],
        [InlineKeyboardButton(get_string("supplier_stats", language), callback_data="supplier_stats")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
🏪 {get_string("supplier_panel", language)}

{supplier.company_name}
✅ {get_string('success', language)}
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

async def show_supplier_inquiries(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    action = query.data.split("_")[1]
    
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
    
    await query.answer()
