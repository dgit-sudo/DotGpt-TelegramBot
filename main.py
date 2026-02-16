import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, ADMIN_IDS
from database import init_db
from migrate_db import run_migrations
from strings import get_string

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Database and run migrations
init_db()
run_migrations()

# Import handlers
from handlers import (
    start,
    language_selection,
    buyer_handlers,
    supplier_handlers,
    admin_handlers,
    chat_handlers,
)

class DotGPTBot:
    def __init__(self):
        self.app = None
    
    def admin_id_filter(self):
        """Create a filter for admin ID input"""
        async def check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
            # Check if message exists and is text
            if not update.message or not update.message.text:
                return False
            # Check if waiting for admin ID
            return context.user_data.get('waiting_for_admin_id', False) and update.message.text.isdigit()
        
        return check
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        # Start command
        self.app.add_handler(CommandHandler("start", start.start_command))
        
        # Language selection
        self.app.add_handler(CallbackQueryHandler(
            language_selection.select_language,
            pattern=r"^lang_"
        ))

        self.app.add_handler(CallbackQueryHandler(
            language_selection.handle_terms_action,
            pattern=r"^terms_"
        ))
        
        # Admin commands
        self.app.add_handler(CommandHandler("admin", admin_handlers.admin_menu))
        
        # Buyer commands
        self.app.add_handler(CommandHandler("browse", buyer_handlers.browse_products))
        self.app.add_handler(CommandHandler("shop", buyer_handlers.browse_products))
        
        # Supplier commands
        self.app.add_handler(CommandHandler("supplier", supplier_handlers.supplier_panel))
        
        # Admin ID input handler (before general message handler)
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,  # Only plain text messages
            admin_handlers.process_add_admin_id
        ))
        
        # Chat handlers
        self.app.add_handler(MessageHandler(
            None,
            chat_handlers.handle_message
        ))
        
        # Callback handlers
        self.app.add_handler(CallbackQueryHandler(
            buyer_handlers.handle_product_action,
            pattern=r"^product_"
        ))

        self.app.add_handler(CallbackQueryHandler(
            buyer_handlers.handle_buyer_action,
            pattern=r"^buyer_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            buyer_handlers.handle_pagination,
            pattern=r"^page_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            supplier_handlers.handle_supplier_action,
            pattern=r"^supplier_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            supplier_handlers.handle_supplier_language_selection,
            pattern=r"^supplier_lang_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            admin_handlers.handle_admin_action,
            pattern=r"^admin_"
        ))

        self.app.add_handler(CallbackQueryHandler(
            chat_handlers.handle_support_action,
            pattern=r"^support_"
        ))
        
        # Superadmin handlers
        self.app.add_handler(CallbackQueryHandler(
            admin_handlers.show_superadmin_menu,
            pattern=r"^superadmin_menu$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            admin_handlers.show_add_admin_form,
            pattern=r"^superadmin_add_admin_form$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            admin_handlers.show_remove_admin_list,
            pattern=r"^superadmin_remove_admin_list$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            admin_handlers.show_confirm_remove_admin,
            pattern=r"^superadmin_confirm_remove_"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            admin_handlers.execute_remove_admin,
            pattern=r"^superadmin_execute_remove$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            admin_handlers.show_list_admins,
            pattern=r"^superadmin_list_admins$"
        ))
        
        self.app.add_handler(CallbackQueryHandler(
            chat_handlers.handle_chat_action,
            pattern=r"^chat_"
        ))
    
    async def on_startup(self, app=None):
        """Called when the bot starts"""
        logger.info("🤖 DotGPT Bot started successfully!")
    
    async def on_shutdown(self, app=None):
        """Called when the bot shuts down"""
        logger.info("🛑 DotGPT Bot shutting down...")
    
    def run(self):
        """Run the bot"""
        builder = Application.builder().token(BOT_TOKEN)
        if hasattr(builder, "post_init"):
            builder = builder.post_init(self.on_startup)
        if hasattr(builder, "post_shutdown"):
            builder = builder.post_shutdown(self.on_shutdown)
        self.app = builder.build()
        
        # Setup handlers
        self.setup_handlers()
        
        # Start polling
        logger.info("Starting bot polling...")
        self.app.run_polling()

if __name__ == '__main__':
    bot = DotGPTBot()
    bot.run()
