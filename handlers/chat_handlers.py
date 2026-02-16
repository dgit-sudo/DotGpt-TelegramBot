from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from strings import get_string
from translation_utils import translate_message, get_language_name
from database_helpers import (
    get_chat,
    get_chat_messages,
    save_chat_message,
    get_buyer,
    get_supplier,
    get_support_chat,
    get_support_messages,
    save_support_message,
    get_all_support_chats,
    get_support_chats_for_buyer,
    is_admin
)
from sqlalchemy import and_
import logging
import re

logger = logging.getLogger(__name__)

IDENTITY_PATTERNS = [
    re.compile(r"@\w{3,}"),
    re.compile(r"(https?://|www\.)\S+", re.IGNORECASE),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b\+?\d[\d\s().-]{6,}\d\b"),
    re.compile(r"\b(telegram|t\.me|telegram\.me|whatsapp|instagram|facebook|snapchat|wechat|line|viber|signal)\b", re.IGNORECASE),
]

def contains_identity_disclosure(text: str) -> bool:
    """Detect identity or contact details in a message"""
    if not text:
        return False
    return any(pattern.search(text) for pattern in IDENTITY_PATTERNS)

def has_media(message) -> bool:
    """Check if a message contains media"""
    return any([
        message.photo,
        message.document,
        message.video,
        message.audio,
        message.voice,
        message.sticker,
        message.animation,
    ])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    chat_type = context.user_data.get('current_chat_type', 'supplier')
    
    # Check if user is in a chat
    current_chat_id = context.user_data.get('current_chat')
    current_support_chat_id = context.user_data.get('current_support_chat')

    message_text = update.message.text or update.message.caption
    
    if chat_type == 'support' and current_support_chat_id:
        chat = get_support_chat(current_support_chat_id)
        if not chat:
            await update.message.reply_text(get_string("not_found", language))
            return

        buyer = get_buyer(user_id)
        sender_type = None
        if buyer and buyer.id == chat.buyer_id:
            sender_type = "buyer"
        elif is_admin(user_id):
            sender_type = "admin"
        else:
            await update.message.reply_text(get_string("unauthorized", language))
            return

        if not message_text:
            await update.message.reply_text(get_string("media_disallowed", language))
            return

        save_support_message(
            chat_id=current_support_chat_id,
            sender_id=user_id,
            sender_type=sender_type,
            message=message_text
        )

        await update.message.reply_text(get_string("message_sent", language))
        return

    if not current_chat_id:
        # Check if it's a command
        if update.message.text and update.message.text.startswith('/'):
            return
        
        # Otherwise ask user what they want to do
        await update.message.reply_text(
            get_string("start_message", language),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_string("browse_products", language), callback_data="buyer_menu")],
                [InlineKeyboardButton(get_string("supplier_panel", language), callback_data="supplier_register")],
            ])
        )
        return
    
    # Save message to chat
    chat = get_chat(current_chat_id)
    if not chat:
        await update.message.reply_text(get_string("not_found", language))
        return

    if has_media(update.message):
        await update.message.reply_text(get_string("media_disallowed", language))
        return

    if contains_identity_disclosure(message_text or ""):
        await update.message.reply_text(get_string("identity_disallowed", language))
        return
    
    # Determine sender type
    buyer = get_buyer(user_id)
    supplier = get_supplier(user_id)
    
    if buyer:
        sender_type = "buyer"
    elif supplier:
        sender_type = "supplier"
    else:
        await update.message.reply_text(get_string("unauthorized", language))
        return
    
    # Save message
    save_chat_message(
        chat_id=current_chat_id,
        sender_id=user_id,
        sender_type=sender_type,
        message=message_text
    )
    
    await update.message.reply_text(get_string("message_sent", language))

async def show_support_chat_view(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Show support chat conversation"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    chat = get_support_chat(chat_id)
    if not chat:
        await query.answer(get_string("not_found", language), show_alert=True)
        return

    buyer = get_buyer(user_id)
    if buyer and chat.buyer_id != buyer.id:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return

    if not buyer and not is_admin(user_id):
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return

    context.user_data['current_chat_type'] = 'support'
    context.user_data['current_support_chat'] = chat_id

    messages = get_support_messages(chat_id)

    message_text = f"🆘 {get_string('support', language)} #{chat_id}\n"
    message_text += get_string("buyer_profile_hidden", language) + "\n\n"
    message_text += "📜 Messages:\n"
    message_text += "-" * 30 + "\n"

    if not messages:
        message_text += get_string("no_chats", language)
    else:
        for msg in messages:
            sender = "You" if msg.sender_id == user_id else ("Admin" if msg.sender_type == "admin" else "Buyer")
            message_text += f"\n{sender}: {msg.message}\n"

    message_text += "\n" + "=" * 30 + "\n"
    message_text += f"\n{get_string('type_message', language)}\n"

    buttons = [
        [InlineKeyboardButton(get_string("back", language), callback_data="support_back")],
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_chat_view(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Show chat conversation with automatic translation"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    chat = get_chat(chat_id)
    if not chat:
        await query.answer(get_string("not_found", language), show_alert=True)
        return
    
    # Check if user has access to this chat
    buyer = get_buyer(user_id)
    supplier = get_supplier(user_id)
    
    if buyer and chat.buyer_id != buyer.id:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    if supplier and chat.supplier_id != supplier.id:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Set current chat
    context.user_data['current_chat'] = chat_id
    
    # Get messages
    messages = get_chat_messages(chat_id)
    
    message_text = f"💬 Chat #{chat_id}\n"
    message_text += get_string("buyer_profile_hidden", language) + "\n\n"
    
    # Show language info
    if buyer:
        supplier_lang = chat.supplier.language if chat.supplier else 'en'
        supplier_lang_name = get_language_name(supplier_lang)
        message_text += f"🌐 {get_string('communicating_in', language)}: {supplier_lang_name}\n\n"
    else:  # supplier
        buyer_lang = chat.buyer.language if chat.buyer else 'en'
        buyer_lang_name = get_language_name(buyer_lang)
        message_text += f"🌐 {get_string('communicating_in', language)}: {buyer_lang_name}\n\n"
    
    message_text += "📜 Messages:\n"
    message_text += "-" * 30 + "\n"
    
    if not messages:
        message_text += get_string("no_chats", language)
    else:
        for msg in messages:
            sender = "You" if msg.sender_id == user_id else f"{'Buyer' if msg.sender_type == 'buyer' else 'Supplier'}"
            
            # Translate message based on sender and receiver
            display_message = msg.message
            try:
                if buyer and msg.sender_type == 'supplier':
                    # Buyer reading supplier message - translate from supplier lang to buyer lang
                    supplier_lang = chat.supplier.language if chat.supplier else 'en'
                    supplier_obj = chat.supplier
                    # Only translate if supplier has auto_translate enabled
                    if supplier_obj and supplier_obj.auto_translate and supplier_lang != buyer.language:
                        display_message = await translate_message(
                            msg.message,
                            buyer_lang=buyer.language,
                            supplier_lang=supplier_lang,
                            sender_type='supplier'
                        )
                elif supplier and msg.sender_type == 'buyer':
                    # Supplier reading buyer message - translate from buyer lang to supplier lang
                    buyer_lang = chat.buyer.language if chat.buyer else 'en'
                    supplier_obj = supplier
                    # Only translate if supplier has auto_translate enabled
                    if supplier_obj.auto_translate and buyer_lang != supplier_obj.language:
                        display_message = await translate_message(
                            msg.message,
                            buyer_lang=buyer_lang,
                            supplier_lang=supplier_obj.language,
                            sender_type='buyer'
                        )
            except Exception as e:
                logger.warning(f"Translation error: {e}. Showing original message.")
            
            message_text += f"\n{sender}: {display_message}\n"
    
    message_text += "\n" + "=" * 30 + "\n"
    message_text += f"\n{get_string('type_message', language)}\n"
    
    buttons = []
    
    # Add sale done button for suppliers
    if supplier:
        buttons.append([InlineKeyboardButton(get_string("mark_sale_done", language), callback_data=f"sale_product_select_{chat_id}")])
    
    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="chat_back")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_chat_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle chat-related actions"""
    query = update.callback_query
    language = context.user_data.get('language', 'en')
    
    # Handle sale-related callbacks
    if query.data.startswith("sale_product_select_"):
        chat_id = int(query.data.split("_")[3])
        await show_sale_product_selection(update, context, chat_id)
        return
    elif query.data.startswith("sale_mark_"):
        parts = query.data.split("_")
        chat_id = int(parts[2])
        product_id = int(parts[3])
        await mark_sale_as_complete(update, context, chat_id, product_id)
        return
    
    action = query.data.split("_")[1]
    
    if action == "open":
        chat_id = int(query.data.split("_")[2])
        await show_chat_view(update, context, chat_id)
    elif action == "back":
        user_id = update.effective_user.id
        buyer = get_buyer(user_id)
        if buyer:
            from handlers.buyer_handlers import show_buyer_menu
            await show_buyer_menu(update, context)
        else:
            from handlers.supplier_handlers import show_supplier_inquiries
            await show_supplier_inquiries(update, context)

    await query.answer()

async def show_support_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show support chats for buyer or admin"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    buyer = get_buyer(user_id)
    if buyer:
        chats = get_support_chats_for_buyer(buyer.id)
        back_callback = "buyer_menu"
    elif is_admin(user_id):
        chats = get_all_support_chats()
        back_callback = "admin_menu"
    else:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return

    message = f"🆘 {get_string('support', language)}\n\n"

    if not chats:
        message += get_string("no_chats", language)
        buttons = [[InlineKeyboardButton(get_string("back", language), callback_data=back_callback)]]
    else:
        buttons = []
        for chat in chats:
            message += f"Support #{chat.id}\n"
            buttons.append([
                InlineKeyboardButton(f"🆘 Support #{chat.id}", callback_data=f"support_open_{chat.id}")
            ])
        buttons.append([InlineKeyboardButton(get_string("back", language), callback_data=back_callback)])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def handle_support_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle support chat actions"""
    query = update.callback_query
    language = context.user_data.get('language', 'en')

    parts = query.data.split("_")
    action = parts[1]

    if action == "open":
        chat_id = int(parts[2])
        await show_support_chat_view(update, context, chat_id)
    elif action == "back":
        if is_admin(query.from_user.id):
            from handlers.admin_handlers import show_admin_panel
            await show_admin_panel(update, context, language)
        else:
            from handlers.buyer_handlers import show_buyer_menu
            await show_buyer_menu(update, context)
    else:
        await query.answer(get_string("not_found", language), show_alert=True)
    
    await query.answer()

async def show_buyer_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show buyer's chats"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    buyer = get_buyer(user_id)
    if not buyer:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    from database_helpers import get_buyer_chats
    chats = get_buyer_chats(buyer.id)
    
    message = f"💬 {get_string('my_chats', language)}\n\n"
    
    if not chats:
        message += get_string("no_chats", language)
        buttons = [[InlineKeyboardButton(get_string("back", language), callback_data="buyer_menu")]]
    else:
        buttons = []
        for chat in chats:
            message += f"Chat #{chat.id}\n"
            buttons.append([
                InlineKeyboardButton(f"💬 Chat #{chat.id}", callback_data=f"chat_open_{chat.id}")
            ])
        
        buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="buyer_menu")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def show_sale_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Show product selection for marking a sale"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    supplier = get_supplier(user_id)
    if not supplier:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Get supplier's products
    from database_helpers import get_products_by_supplier
    products = get_products_by_supplier(supplier.id)
    
    if not products:
        await query.answer(get_string("no_products", language), show_alert=True)
        return
    
    message = f"✅ {get_string('mark_sale_done', language)}\n\n"
    message += f"{get_string('select_product', language)}:\n\n"
    
    buttons = []
    for product in products:
        buttons.append([
            InlineKeyboardButton(product.name, callback_data=f"sale_mark_{chat_id}_{product.id}")
        ])
    
    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data=f"chat_open_{chat_id}")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def mark_sale_as_complete(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, product_id: int):
    """Mark a sale as complete and reduce stock"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    supplier = get_supplier(user_id)
    if not supplier:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Reduce stock by 1
    from database_helpers import update_product_stock
    from database import SessionLocal, ProductPrice
    
    db = SessionLocal()
    price_record = db.query(ProductPrice).filter(
        and_(
            ProductPrice.product_id == product_id,
            ProductPrice.supplier_id == supplier.id
        )
    ).first()
    
    if not price_record:
        db.close()
        await query.answer(get_string("not_found", language), show_alert=True)
        return
    
    # Get current stock
    current_stock = price_record.stock
    
    # Reduce by 1 (only if stock > 0 or if stock is being tracked)
    if current_stock < 0:
        # Stock not being tracked, just mark as done without changing stock
        message = f"✅ {get_string('sale_completed', language)}!\n\n"
        message += f"Product: {price_record.product.name}\n"
        message += f"Stock tracking: Not tracked"
    else:
        # Reduce stock by 1
        price_record.stock = current_stock - 1
        db.commit()
        
        message = f"✅ {get_string('sale_completed', language)}!\n\n"
        message += f"Product: {price_record.product.name}\n"
        message += f"Stock remaining: {price_record.stock}"
    
    db.close()
    
    # Show confirmation
    buttons = [[InlineKeyboardButton(get_string("back", language), callback_data=f"chat_open_{chat_id}")]]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer(get_string("stock_reduced", language), show_alert=False)

async def handle_chat_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle chat-related actions"""
    query = update.callback_query
    language = context.user_data.get('language', 'en')
    
    action = query.data.split("_")[1]
    
    if action == "open":
        chat_id = int(query.data.split("_")[2])
        await show_chat_view(update, context, chat_id)
    elif action == "back":
        user_id = update.effective_user.id
        buyer = get_buyer(user_id)
        if buyer:
            from handlers.buyer_handlers import show_buyer_menu
            await show_buyer_menu(update, context)
        else:
            from handlers.supplier_handlers import show_supplier_inquiries
            await show_supplier_inquiries(update, context)
    
    await query.answer()

async def show_buyer_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show buyer's chats"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    buyer = get_buyer(user_id)
    if not buyer:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    from database_helpers import get_buyer_chats
    chats = get_buyer_chats(buyer.id)
    
    message = f"💬 {get_string('my_chats', language)}\n\n"
    
    if not chats:
        message += get_string("no_chats", language)
        buttons = [[InlineKeyboardButton(get_string("back", language), callback_data="buyer_menu")]]
    else:
        buttons = []
        for chat in chats:
            message += f"Chat #{chat.id}\n"
            buttons.append([
                InlineKeyboardButton(f"💬 Chat #{chat.id}", callback_data=f"chat_open_{chat.id}")
            ])
        
        buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="buyer_menu")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()
