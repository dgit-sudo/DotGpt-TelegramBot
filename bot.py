"""
E-commerce Telegram Bot
A bot for selling products with multi-language support, supplier management, and anonymous chat
"""
import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from models import init_db, get_session, User, Product, Chat, Message
from translations import get_text, TRANSLATIONS

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')

# Initialize database
engine = init_db(DATABASE_URL)

# Conversation states
(SELECTING_LANGUAGE, PRODUCT_NAME, PRODUCT_DESCRIPTION, PRODUCT_PRICE, 
 PRODUCT_PAYMENT, CHATTING, WAITING_FOR_MESSAGE) = range(7)


def get_user_language(user_id):
    """Get user's language preference"""
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if user:
            return user.language
        return 'en'
    finally:
        session.close()


def get_or_create_user(telegram_user, role='buyer'):
    """Get or create user in database"""
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(telegram_id=telegram_user.id).first()
        if not user:
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                role=role
            )
            session.add(user)
            session.commit()
        return user
    finally:
        session.close()


def is_admin(user_id):
    """Check if user is admin"""
    if user_id == ADMIN_USER_ID:
        return True
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        return user and user.role == 'admin'
    finally:
        session.close()


def is_supplier(user_id):
    """Check if user is supplier"""
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        return user and user.role in ['supplier', 'admin']
    finally:
        session.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = update.effective_user
    get_or_create_user(user, role='admin' if user.id == ADMIN_USER_ID else 'buyer')
    
    # Language selection
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
         InlineKeyboardButton("🇪🇸 Español", callback_data='lang_es')],
        [InlineKeyboardButton("🇫🇷 Français", callback_data='lang_fr'),
         InlineKeyboardButton("🇩🇪 Deutsch", callback_data='lang_de')],
        [InlineKeyboardButton("🇮🇹 Italiano", callback_data='lang_it'),
         InlineKeyboardButton("🇵🇹 Português", callback_data='lang_pt')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    lang = get_user_language(user.id)
    await update.message.reply_text(get_text(lang, 'welcome'), reply_markup=reply_markup)


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set user language"""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace('lang_', '')
    user_id = update.effective_user.id
    
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        if user:
            user.language = lang_code
            session.commit()
    finally:
        session.close()
    
    await query.edit_message_text(get_text(lang_code, 'language_set'))
    await show_main_menu(update, context)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu based on user role"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'browse_products'), callback_data='browse_products')],
        [InlineKeyboardButton(get_text(lang, 'my_chats'), callback_data='my_chats')],
        [InlineKeyboardButton(get_text(lang, 'settings'), callback_data='settings')],
    ]
    
    if is_supplier(user_id):
        keyboard.insert(1, [InlineKeyboardButton(get_text(lang, 'supplier_panel'), callback_data='supplier_panel')])
    
    if is_admin(user_id):
        keyboard.insert(0, [InlineKeyboardButton(get_text(lang, 'admin_panel'), callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.message.reply_text(
            get_text(lang, 'main_menu'),
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            get_text(lang, 'main_menu'),
            reply_markup=reply_markup
        )


async def browse_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Browse available products"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    session = get_session(engine)
    try:
        products = session.query(Product).filter_by(is_active=True).all()
        
        if not products:
            await query.edit_message_text(get_text(lang, 'no_products'))
            return
        
        keyboard = []
        for product in products:
            keyboard.append([InlineKeyboardButton(
                f"{product.name} - {product.price} {product.currency}",
                callback_data=f'product_{product.id}'
            )])
        keyboard.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='main_menu')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            get_text(lang, 'product_list'),
            reply_markup=reply_markup
        )
    finally:
        session.close()


async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show product details"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.replace('product_', ''))
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    session = get_session(engine)
    try:
        product = session.query(Product).filter_by(id=product_id).first()
        
        if not product:
            await query.edit_message_text("Product not found")
            return
        
        supplier_name = product.supplier.first_name or product.supplier.username or "Unknown"
        
        text = get_text(lang, 'product_details',
                       name=product.name,
                       price=product.price,
                       currency=product.currency,
                       supplier=supplier_name,
                       payment=product.payment_methods or "Not specified",
                       description=product.description or "No description")
        
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'contact_supplier'), 
                                 callback_data=f'contact_{product_id}')],
            [InlineKeyboardButton(get_text(lang, 'back'), callback_data='browse_products')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        session.close()


async def contact_supplier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a chat with supplier"""
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.replace('contact_', ''))
    buyer_id = update.effective_user.id
    lang = get_user_language(buyer_id)
    
    session = get_session(engine)
    try:
        product = session.query(Product).filter_by(id=product_id).first()
        if not product:
            await query.edit_message_text("Product not found")
            return
        
        buyer = session.query(User).filter_by(telegram_id=buyer_id).first()
        
        # Check if chat already exists
        chat = session.query(Chat).filter_by(
            buyer_id=buyer.id,
            supplier_id=product.supplier_id,
            product_id=product_id,
            is_active=True
        ).first()
        
        if not chat:
            chat = Chat(
                buyer_id=buyer.id,
                supplier_id=product.supplier_id,
                product_id=product_id
            )
            session.add(chat)
            session.commit()
        
        context.user_data['active_chat'] = chat.id
        context.user_data['chat_mode'] = True
        
        await query.edit_message_text(
            get_text(lang, 'chat_with_supplier', product=product.name) + "\n\n" +
            get_text(lang, 'type_message')
        )
        
        return WAITING_FOR_MESSAGE
    finally:
        session.close()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages in chat"""
    if not context.user_data.get('chat_mode'):
        return
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    chat_id = context.user_data.get('active_chat')
    
    if not chat_id:
        return
    
    session = get_session(engine)
    try:
        chat = session.query(Chat).filter_by(id=chat_id).first()
        if not chat:
            return
        
        sender = session.query(User).filter_by(telegram_id=user_id).first()
        
        # Determine receiver
        if sender.id == chat.buyer_id:
            receiver_id = chat.supplier_id
            receiver_telegram_id = chat.supplier.telegram_id
        else:
            receiver_id = chat.buyer_id
            receiver_telegram_id = chat.buyer.telegram_id
        
        # Save message
        message = Message(
            chat_id=chat.id,
            sender_id=sender.id,
            receiver_id=receiver_id,
            message_text=update.message.text
        )
        session.add(message)
        session.commit()
        
        await update.message.reply_text(get_text(lang, 'message_sent'))
        
        # Notify receiver
        receiver_lang = get_user_language(receiver_telegram_id)
        sender_name = get_text(receiver_lang, 'buyer_anonymous') if sender.id == chat.buyer_id else sender.first_name
        
        try:
            await context.bot.send_message(
                chat_id=receiver_telegram_id,
                text=get_text(receiver_lang, 'new_message', sender=sender_name) + f"\n\n{update.message.text}"
            )
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    finally:
        session.close()


async def my_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's chats"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        
        # Get chats where user is buyer or supplier
        chats = session.query(Chat).filter(
            ((Chat.buyer_id == user.id) | (Chat.supplier_id == user.id)) &
            (Chat.is_active == True)
        ).all()
        
        if not chats:
            await query.edit_message_text(
                get_text(lang, 'no_chats'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(lang, 'back'), callback_data='main_menu')
                ]])
            )
            return
        
        keyboard = []
        for chat in chats:
            product_name = chat.product.name if chat.product else "Unknown"
            other_user = chat.supplier if chat.buyer_id == user.id else chat.buyer
            other_name = get_text(lang, 'buyer_anonymous') if chat.buyer_id != user.id else other_user.first_name
            
            keyboard.append([InlineKeyboardButton(
                f"{product_name} - {other_name}",
                callback_data=f'openchat_{chat.id}'
            )])
        
        keyboard.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text(lang, 'my_chats'),
            reply_markup=reply_markup
        )
    finally:
        session.close()


async def open_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Open a specific chat"""
    query = update.callback_query
    await query.answer()
    
    chat_id = int(query.data.replace('openchat_', ''))
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    context.user_data['active_chat'] = chat_id
    context.user_data['chat_mode'] = True
    
    session = get_session(engine)
    try:
        chat = session.query(Chat).filter_by(id=chat_id).first()
        product_name = chat.product.name if chat.product else "Unknown"
        
        await query.edit_message_text(
            get_text(lang, 'chat_with_supplier', product=product_name) + "\n\n" +
            get_text(lang, 'type_message')
        )
    finally:
        session.close()
    
    return WAITING_FOR_MESSAGE


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings menu"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'change_language'), callback_data='change_language')],
        [InlineKeyboardButton(get_text(lang, 'back'), callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        get_text(lang, 'settings_menu'),
        reply_markup=reply_markup
    )


async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Change language"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
         InlineKeyboardButton("🇪🇸 Español", callback_data='lang_es')],
        [InlineKeyboardButton("🇫🇷 Français", callback_data='lang_fr'),
         InlineKeyboardButton("🇩🇪 Deutsch", callback_data='lang_de')],
        [InlineKeyboardButton("🇮🇹 Italiano", callback_data='lang_it'),
         InlineKeyboardButton("🇵🇹 Português", callback_data='lang_pt')],
        [InlineKeyboardButton(get_text(lang, 'back'), callback_data='settings')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        get_text(lang, 'select_language'),
        reply_markup=reply_markup
    )


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text("Unauthorized")
        return
    
    lang = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'manage_products'), callback_data='admin_products')],
        [InlineKeyboardButton(get_text(lang, 'manage_suppliers'), callback_data='admin_suppliers')],
        [InlineKeyboardButton(get_text(lang, 'view_all_chats'), callback_data='admin_chats')],
        [InlineKeyboardButton(get_text(lang, 'back'), callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        get_text(lang, 'admin_menu'),
        reply_markup=reply_markup
    )


async def admin_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage products as admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    session = get_session(engine)
    try:
        products = session.query(Product).all()
        
        keyboard = []
        for product in products:
            status = "✅" if product.is_active else "❌"
            keyboard.append([InlineKeyboardButton(
                f"{status} {product.name}",
                callback_data=f'admin_edit_product_{product.id}'
            )])
        
        keyboard.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='admin_panel')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text(lang, 'manage_products'),
            reply_markup=reply_markup
        )
    finally:
        session.close()


async def admin_suppliers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manage suppliers as admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    session = get_session(engine)
    try:
        users = session.query(User).filter_by(role='buyer').all()
        
        keyboard = []
        for user in users:
            name = user.first_name or user.username or f"ID: {user.telegram_id}"
            keyboard.append([InlineKeyboardButton(
                f"Make Supplier: {name}",
                callback_data=f'make_supplier_{user.id}'
            )])
        
        keyboard.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='admin_panel')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text(lang, 'manage_suppliers'),
            reply_markup=reply_markup
        )
    finally:
        session.close()


async def make_supplier(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Make a user a supplier"""
    query = update.callback_query
    await query.answer()
    
    user_db_id = int(query.data.replace('make_supplier_', ''))
    admin_id = update.effective_user.id
    lang = get_user_language(admin_id)
    
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(id=user_db_id).first()
        if user:
            user.role = 'supplier'
            session.commit()
            await query.edit_message_text(get_text(lang, 'user_is_supplier'))
    finally:
        session.close()


async def admin_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all chats as admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    session = get_session(engine)
    try:
        chats = session.query(Chat).filter_by(is_active=True).all()
        
        if not chats:
            await query.edit_message_text(
                get_text(lang, 'no_chats'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(lang, 'back'), callback_data='admin_panel')
                ]])
            )
            return
        
        text = "All Active Chats:\n\n"
        for chat in chats:
            buyer_name = chat.buyer.first_name or f"ID: {chat.buyer.telegram_id}"
            supplier_name = chat.supplier.first_name or f"ID: {chat.supplier.telegram_id}"
            product_name = chat.product.name if chat.product else "Unknown"
            text += f"Chat #{chat.id}: {buyer_name} ↔ {supplier_name} (Product: {product_name})\n"
        
        keyboard = [[InlineKeyboardButton(get_text(lang, 'back'), callback_data='admin_panel')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup)
    finally:
        session.close()


async def supplier_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show supplier panel"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    keyboard = [
        [InlineKeyboardButton(get_text(lang, 'my_products'), callback_data='supplier_products')],
        [InlineKeyboardButton(get_text(lang, 'add_new_product'), callback_data='add_product')],
        [InlineKeyboardButton(get_text(lang, 'incoming_messages'), callback_data='my_chats')],
        [InlineKeyboardButton(get_text(lang, 'back'), callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        get_text(lang, 'supplier_menu'),
        reply_markup=reply_markup
    )


async def supplier_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show supplier's products"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        products = session.query(Product).filter_by(supplier_id=user.id).all()
        
        if not products:
            await query.edit_message_text(
                get_text(lang, 'no_products'),
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(get_text(lang, 'back'), callback_data='supplier_panel')
                ]])
            )
            return
        
        keyboard = []
        for product in products:
            status = "✅" if product.is_active else "❌"
            keyboard.append([InlineKeyboardButton(
                f"{status} {product.name} - {product.price} {product.currency}",
                callback_data=f'edit_product_{product.id}'
            )])
        
        keyboard.append([InlineKeyboardButton(get_text(lang, 'back'), callback_data='supplier_panel')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text(lang, 'my_products'),
            reply_markup=reply_markup
        )
    finally:
        session.close()


async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start adding a new product"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    await query.edit_message_text(get_text(lang, 'enter_product_name'))
    return PRODUCT_NAME


async def product_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save product name and ask for description"""
    context.user_data['new_product'] = {'name': update.message.text}
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    await update.message.reply_text(get_text(lang, 'enter_product_description'))
    return PRODUCT_DESCRIPTION


async def product_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save product description and ask for price"""
    context.user_data['new_product']['description'] = update.message.text
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    await update.message.reply_text(get_text(lang, 'enter_product_price'))
    return PRODUCT_PRICE


async def product_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save product price and ask for payment methods"""
    try:
        price = float(update.message.text)
        context.user_data['new_product']['price'] = price
        
        user_id = update.effective_user.id
        lang = get_user_language(user_id)
        
        await update.message.reply_text(get_text(lang, 'enter_payment_methods'))
        return PRODUCT_PAYMENT
    except ValueError:
        user_id = update.effective_user.id
        lang = get_user_language(user_id)
        await update.message.reply_text(get_text(lang, 'invalid_price'))
        return PRODUCT_PRICE


async def product_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save product payment methods and create product"""
    context.user_data['new_product']['payment_methods'] = update.message.text
    
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    session = get_session(engine)
    try:
        user = session.query(User).filter_by(telegram_id=user_id).first()
        
        product = Product(
            name=context.user_data['new_product']['name'],
            description=context.user_data['new_product']['description'],
            price=context.user_data['new_product']['price'],
            payment_methods=context.user_data['new_product']['payment_methods'],
            supplier_id=user.id
        )
        session.add(product)
        session.commit()
        
        await update.message.reply_text(get_text(lang, 'product_added'))
        await show_main_menu(update, context)
    finally:
        session.close()
        context.user_data.pop('new_product', None)
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    
    context.user_data.clear()
    
    await update.message.reply_text(get_text(lang, 'cancel'))
    await show_main_menu(update, context)
    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    
    if query.data.startswith('lang_'):
        await set_language(update, context)
    elif query.data == 'main_menu':
        await show_main_menu(update, context)
    elif query.data == 'browse_products':
        await browse_products(update, context)
    elif query.data.startswith('product_'):
        await show_product(update, context)
    elif query.data.startswith('contact_'):
        await contact_supplier(update, context)
    elif query.data == 'my_chats':
        await my_chats(update, context)
    elif query.data.startswith('openchat_'):
        await open_chat(update, context)
    elif query.data == 'settings':
        await settings(update, context)
    elif query.data == 'change_language':
        await change_language(update, context)
    elif query.data == 'admin_panel':
        await admin_panel(update, context)
    elif query.data == 'admin_products':
        await admin_products(update, context)
    elif query.data == 'admin_suppliers':
        await admin_suppliers(update, context)
    elif query.data.startswith('make_supplier_'):
        await make_supplier(update, context)
    elif query.data == 'admin_chats':
        await admin_chats(update, context)
    elif query.data == 'supplier_panel':
        await supplier_panel(update, context)
    elif query.data == 'supplier_products':
        await supplier_products(update, context)
    elif query.data == 'add_product':
        await add_product_start(update, context)


def main():
    """Start the bot"""
    if not TOKEN:
        logger.error("No bot token found! Please set TELEGRAM_BOT_TOKEN in .env file")
        return
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add conversation handler for adding products
    add_product_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_product_start, pattern='^add_product$')],
        states={
            PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_name)],
            PRODUCT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_description)],
            PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_price)],
            PRODUCT_PAYMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, product_payment)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(add_product_conv)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
