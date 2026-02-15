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
)
from database_helpers import is_admin
import logging

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    chat_type = context.user_data.get('current_chat_type', 'supplier')
    
    # Check if user is in a chat
    current_chat_id = context.user_data.get('current_chat')
    current_support_chat_id = context.user_data.get('current_support_chat')
    
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

        save_support_message(
            chat_id=current_support_chat_id,
            sender_id=user_id,
            sender_type=sender_type,
            message=update.message.text
        )

        await update.message.reply_text(get_string("message_sent", language))
        return

    if not current_chat_id:
        # Check if it's a command
        if update.message.text.startswith('/'):
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
        message=update.message.text
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
                    if supplier_lang != buyer.language:
                        display_message = await translate_message(
                            msg.message,
                            buyer_lang=buyer.language,
                            supplier_lang=supplier_lang,
                            sender_type='supplier'
                        )
                elif supplier and msg.sender_type == 'buyer':
                    # Supplier reading buyer message - translate from buyer lang to supplier lang
                    buyer_lang = chat.buyer.language if chat.buyer else 'en'
                    if buyer_lang != supplier.language:
                        display_message = await translate_message(
                            msg.message,
                            buyer_lang=buyer_lang,
                            supplier_lang=supplier.language,
                            sender_type='buyer'
                        )
            except Exception as e:
                logger.warning(f"Translation error: {e}. Showing original message.")
            
            message_text += f"\n{sender}: {display_message}\n"
    
    message_text += "\n" + "=" * 30 + "\n"
    message_text += f"\n{get_string('type_message', language)}\n"
    
    buttons = [
        [InlineKeyboardButton(get_string("back", language), callback_data="chat_back")],
    ]
    
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
