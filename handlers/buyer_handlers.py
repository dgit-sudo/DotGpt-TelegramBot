from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from strings import get_string
from database_helpers import (
    get_all_active_products,
    get_product_price,
    get_supplier,
    get_buyer_chats,
    get_buyer,
    get_or_create_chat,
    get_supplier_payment_methods,
    get_or_create_support_chat,
)
from config import ITEMS_PER_PAGE
import logging

logger = logging.getLogger(__name__)

async def browse_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available products"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    buyer = get_buyer(user_id)
    if not buyer or not buyer.active:
        if query:
            await query.answer(get_string("unauthorized", language), show_alert=True)
        else:
            await update.message.reply_text(get_string("unauthorized", language))
        return
    
    products = get_all_active_products()
    
    if not products:
        if query:
            await query.edit_message_text(get_string("no_products", language))
        else:
            await update.message.reply_text(get_string("no_products", language))
        return
    
    # Show paginated products
    context.user_data['current_page'] = 0
    context.user_data['products'] = products
    await show_products_page(update, context, language, 0)

async def show_products_page(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str, page: int):
    """Show products for a specific page"""
    products = context.user_data.get('products', [])
    
    if not products:
        text = get_string("no_products", language)
        if update.callback_query:
            await update.callback_query.edit_message_text(text)
        else:
            await update.message.reply_text(text)
        return
    
    # Calculate pagination
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_products = products[start_idx:end_idx]
    
    # Build message
    message = f"🛍️ {get_string('browse_products', language)}\n\n"
    
    buttons = []
    for product in page_products:
        message += f"📦 *{product.name}*\n"
        message += f"   {product.description or 'No description'}\n\n"
        
        buttons.append([
            InlineKeyboardButton(f"ℹ️ {product.name}", callback_data=f"product_view_{product.id}")
        ])
    
    # Pagination buttons
    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton("⬅️ " + get_string("back", language), callback_data=f"page_{page-1}")
        )
    if end_idx < len(products):
        pagination_buttons.append(
            InlineKeyboardButton(get_string("next", language) + " ➡️", callback_data=f"page_{page+1}")
        )
    
    if pagination_buttons:
        buttons.append(pagination_buttons)
    
    buttons.append([InlineKeyboardButton(get_string("menu", language), callback_data="buyer_menu")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
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

async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    """Show detailed information about a product"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    # Find product
    products = context.user_data.get('products', [])
    product = next((p for p in products if p.id == product_id), None)
    
    if not product:
        await query.answer(get_string("not_found", language), show_alert=True)
        return
    
    # Get suppliers and prices for this product
    prices = product.prices
    
    message = f"""
📦 *{get_string('product_details', language)}*

{product.name}
{product.description or 'No description provided'}

📋 *{get_string('supplier', language)} & {get_string('price', language)}:*
"""
    
    if not prices:
        message += f"\n{get_string('no_products', language)}"
        await query.edit_message_text(message, parse_mode='Markdown')
        return
    
    buttons = []
    for price in prices:
        supplier = price.supplier
        if supplier and supplier.status == "verified" and not supplier.is_banned and supplier.active:
            message += f"\n🏪 {supplier.company_name}"
            message += f"\n   💰 {price.price} {price.currency}"
            message += f"\n   📦 {get_string('stock', language) if 'stock' in dir() else 'Stock'}: {price.stock}\n"
            
            buttons.append([
                InlineKeyboardButton(
                    f"📞 {supplier.company_name}",
                    callback_data=f"product_contact_{product_id}_{supplier.id}"
                )
            ])
    
    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="buyer_browse")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_product_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle product-related actions"""
    query = update.callback_query
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    
    action = query.data.split("_")
    
    if action[1] == "view":
        product_id = int(action[2])
        await show_product_details(update, context, product_id)
    
    elif action[1] == "contact":
        product_id = int(action[2])
        supplier_id = int(action[3])
        
        # Create or get chat
        buyer = get_buyer(user_id)
        if not buyer:
            await query.answer(get_string("unauthorized", language), show_alert=True)
            return
        
        chat = get_or_create_chat(buyer.id, supplier_id, product_id)
        context.user_data['current_chat'] = chat.id
        
        # Show chat message
        supplier = get_supplier(chat.supplier_id)  # This won't work - need to refactor
        await query.edit_message_text(
            text=f"{get_string('chat_with_supplier', language)}\n\n💬 {chat.id}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_string("back", language), callback_data="buyer_browse")]
            ])
        )

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination"""
    query = update.callback_query
    language = context.user_data.get('language', 'en')
    
    page = int(query.data.split("_")[1])
    await show_products_page(update, context, language, page)
    await query.answer()

async def show_buyer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show buyer menu"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    keyboard = [
        [InlineKeyboardButton(get_string("browse_products", language), callback_data="buyer_browse")],
        [InlineKeyboardButton(get_string("my_chats", language), callback_data="buyer_chats")],
        [InlineKeyboardButton(get_string("support", language), callback_data="buyer_support")],
        [InlineKeyboardButton(get_string("order_history", language), callback_data="buyer_orders")],
        [InlineKeyboardButton(get_string("settings", language), callback_data="buyer_settings")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = get_string("start_message", language)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def start_support_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start support chat for buyer"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    buyer = get_buyer(user_id)
    if not buyer:
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return

    chat_id = get_or_create_support_chat(buyer.id)
    context.user_data['current_chat_type'] = 'support'
    context.user_data['current_support_chat'] = chat_id

    await query.edit_message_text(
        text=get_string("support_chat_started", language),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("back", language), callback_data="buyer_menu")]
        ])
    )
    await query.answer()

async def handle_buyer_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle buyer menu actions"""
    query = update.callback_query
    language = context.user_data.get('language', 'en')

    action = query.data.split("_")[1]

    if action == "menu":
        await show_buyer_menu(update, context)
    elif action == "browse":
        await browse_products(update, context)
    elif action == "chats":
        from handlers.chat_handlers import show_buyer_chats
        await show_buyer_chats(update, context)
    elif action == "support":
        await start_support_chat(update, context)
    elif action == "settings":
        from handlers.start import show_language_selection
        await show_language_selection(update, context, page=0)
    else:
        await query.answer(get_string("not_found", language), show_alert=True)
