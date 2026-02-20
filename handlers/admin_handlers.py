from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from strings import get_string
from database_helpers import (
    get_all_suppliers,
    get_unverified_suppliers,
    get_all_chats,
    get_historical_chats,
    get_chat,
    get_chat_messages,
    get_system_stats,
    get_system_stats_usernames,
    get_sales_leaderboard,
    get_referral_leaderboard,
    search_user_by_telegram_id,
    verify_supplier,
    reject_supplier,
    block_user,
    unblock_user,
    is_admin,
    is_superadmin,
    get_all_admins,
    get_admin,
    add_admin,
    remove_admin,
    get_all_products,
    create_product,
    delete_product,
    get_product_by_id,
    get_buyer_by_id,
    get_buyer,
    get_supplier_by_id,
    get_supplier,
    attach_product_to_supplier,
    get_verified_suppliers,
    get_out_of_stock_suppliers,
    update_product_stock,
    end_chat,
    get_pending_sale_proofs,
    get_sale_by_id,
    approve_sale,
    reject_sale,
)
from config import ADMIN_IDS
import logging

logger = logging.getLogger(__name__)

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin menu"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    
    # Check if user is admin (database-driven)
    if not is_admin(user_id):
        await update.message.reply_text(
            get_string("unauthorized", language)
        )
        return
    
    await show_admin_panel(update, context, language)

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Show admin panel"""
    user_id = update.effective_user.id
    is_superadmin_user = is_superadmin(user_id)
    
    keyboard = []
    
    # Add superadmin panel option if user is superadmin
    if is_superadmin_user:
        keyboard.append([InlineKeyboardButton("👑 Superadmin Panel", callback_data="superadmin_menu")])
    
    keyboard.extend([
        [InlineKeyboardButton(get_string("view_all_chats", language), callback_data="admin_view_chats")],
        [InlineKeyboardButton("🕘 Historical Chats", callback_data="admin_historical_chats")],
        [InlineKeyboardButton(get_string("manage_users", language), callback_data="admin_manage_users")],
        [InlineKeyboardButton(get_string("manage_suppliers_admin", language), callback_data="admin_suppliers")],
        [InlineKeyboardButton(get_string("manage_products_admin", language), callback_data="admin_manage_products")],
        [InlineKeyboardButton("�🔍 " + get_string("pending_sales", language), callback_data="admin_pending_sales")],
        [InlineKeyboardButton(get_string("support", language), callback_data="admin_support_chats")],
        [InlineKeyboardButton(get_string("system_stats", language), callback_data="admin_stats")],
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
👨‍💼 {get_string("admin_panel", language)}

{get_string("start_message", language)}
"""
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await update.callback_query.answer()
    else:
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def show_all_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all chats admin view"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    chats = get_all_chats()
    
    message = f"👁️ {get_string('view_all_chats', language)}\n\n"
    
    if not chats:
        message += get_string("no_chats", language)
        buttons = [[InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")]]
    else:
        buttons = []
        message += f"Total: {len(chats)} chats\n\n"
        
        for chat in chats:
            buyer = get_buyer_by_id(chat.buyer_id)
            supplier = get_supplier_by_id(chat.supplier_id)
            product = get_product_by_id(chat.product_id) if chat.product_id else None

            buyer_label = f"@{buyer.username}" if buyer and buyer.username else f"Buyer {chat.buyer_id}"
            seller_label = supplier.company_name if supplier else f"Seller {chat.supplier_id}"
            product_label = product.name if product else "General"

            message += f"{buyer_label} ↔ {seller_label} • {product_label}\n"
            
            buttons.append([
                InlineKeyboardButton(
                    f"📊 {buyer_label} • {product_label}",
                    callback_data=f"admin_chat_{chat.id}"
                )
            ])
        
        buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup
    )
    await query.answer()

async def show_system_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system statistics"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    stats = get_system_stats()
    details = get_system_stats_usernames(limit=10)
    buyers = details.get("buyers", [])
    suppliers = details.get("suppliers", [])
    
    message = f"""
📊 {get_string("system_stats", language)}

👥 Total Buyers: {stats['total_buyers']}
🏪 Total Suppliers: {stats['total_suppliers']}
💬 Active Chats: {stats['active_chats']}
📦 Total Products: {stats['total_products']}
💭 Total Messages: {stats['total_messages']}
"""

    message += "\n👥 Recent Buyer Usernames:\n"
    if buyers:
        for buyer in buyers:
            buyer_username = f"@{buyer.username}" if buyer.username else "No username"
            message += f"• {buyer_username} (ID: {buyer.telegram_id})\n"
    else:
        message += "• None\n"

    message += "\n🏪 Recent Seller Usernames:\n"
    if suppliers:
        for supplier in suppliers:
            seller_username = f"@{supplier.username}" if supplier.username else "No username"
            message += f"• {supplier.company_name} ({seller_username}, ID: {supplier.telegram_id})\n"
    else:
        message += "• None\n"
    
    buttons = [
        [InlineKeyboardButton("🏆 Sales Leaderboard", callback_data="admin_stats_leaderboard")],
        [InlineKeyboardButton("🎯 Referral Leaderboard", callback_data="admin_stats_referrals")],
        [InlineKeyboardButton("🔎 Search User (Ban/Unban)", callback_data="admin_stats_search")],
        [InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def show_sales_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show leaderboard for top sellers and buyers by approved sales"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    leaderboard = get_sales_leaderboard(limit=10)
    top_sellers = leaderboard.get("top_sellers", [])
    top_buyers = leaderboard.get("top_buyers", [])

    message = "🏆 Sales Leaderboard\n\n"
    message += "Top Sellers (Approved Sales):\n"
    if not top_sellers:
        message += "• No sales yet\n"
    else:
        for index, item in enumerate(top_sellers, 1):
            supplier = item["supplier"]
            sales_count = item["sales_count"]
            seller_username = f"@{supplier.username}" if supplier.username else "No username"
            message += f"{index}. {supplier.company_name} ({seller_username}) - {sales_count}\n"

    message += "\nTop Buyers (Approved Purchases):\n"
    if not top_buyers:
        message += "• No purchases yet\n"
    else:
        for index, item in enumerate(top_buyers, 1):
            buyer = item["buyer"]
            sales_count = item["sales_count"]
            buyer_name = " ".join(filter(None, [buyer.first_name, buyer.last_name])) or "Unknown"
            buyer_username = f"@{buyer.username}" if buyer.username else "No username"
            message += f"{index}. {buyer_name} ({buyer_username}) - {sales_count}\n"

    buttons = [[InlineKeyboardButton(get_string("back", language), callback_data="admin_stats")]]
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()

async def show_referral_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show referral leaderboard with user type and referral counts"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    rows = get_referral_leaderboard(limit=20)
    message = "🎯 Referral Leaderboard (Join-based)\n\n"

    if not rows:
        message += "• No referrals yet\n"
    else:
        for index, row in enumerate(rows, 1):
            username = f"@{row['username']}" if row.get('username') else f"ID:{row['telegram_id']}"
            user_type = row.get('user_type', 'user')
            count = row.get('referrals_count', 0)
            message += f"{index}. {username} | Type: {user_type} | Referrals: {count}\n"

    buttons = [[InlineKeyboardButton(get_string("back", language), callback_data="admin_stats")]]
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()

async def prompt_user_search_for_moderation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prompt admin for telegram id to ban/unban"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    context.user_data['stats_user_search_mode'] = True
    await query.edit_message_text(
        text="🔎 Search user for Ban/Unban\n\nSend Telegram ID (numbers only).",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("back", language), callback_data="admin_stats")]
        ])
    )
    await query.answer()

async def show_user_moderation_result(update: Update, context: ContextTypes.DEFAULT_TYPE, telegram_id: int):
    """Show moderation options for searched user"""
    language = context.user_data.get('language', 'en')
    result = search_user_by_telegram_id(telegram_id)

    admin_user = result.get("admin")
    if admin_user and (admin_user.is_superadmin or admin_user.is_active):
        await update.message.reply_text("❌ Admins/Superadmins cannot be banned/unbanned here.")
        return

    buyer = result.get("buyer")
    supplier = result.get("supplier")

    if not buyer and not supplier:
        await update.message.reply_text("❌ User not found.")
        return

    message = f"👤 Search Result for {telegram_id}\n\n"
    buttons = []

    if buyer:
        buyer_username = f"@{buyer.username}" if buyer.username else "No username"
        buyer_status = "Active" if buyer.active else "Blocked"
        message += f"Buyer: {buyer_username} ({buyer_status})\n"
        buyer_action = "ban" if buyer.active else "unban"
        buyer_label = "🚫 Ban Buyer" if buyer.active else "✅ Unban Buyer"
        buttons.append([
            InlineKeyboardButton(
                buyer_label,
                callback_data=f"admin_stats_toggle_buyer_{telegram_id}_{buyer_action}"
            )
        ])

    if supplier:
        supplier_username = f"@{supplier.username}" if supplier.username else "No username"
        supplier_status = "Active" if supplier.active else "Blocked"
        message += f"Seller: {supplier.company_name} ({supplier_username}, {supplier_status})\n"
        supplier_action = "ban" if supplier.active else "unban"
        supplier_label = "🚫 Ban Seller" if supplier.active else "✅ Unban Seller"
        buttons.append([
            InlineKeyboardButton(
                supplier_label,
                callback_data=f"admin_stats_toggle_supplier_{telegram_id}_{supplier_action}"
            )
        ])

    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_stats")])

    await update.message.reply_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def toggle_user_access_from_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, user_type: str, telegram_id: int, action: str):
    """Toggle buyer/seller access from stats moderation panel"""
    query = update.callback_query

    admin_user = get_admin(telegram_id)
    if admin_user and (admin_user.is_superadmin or admin_user.is_active):
        await query.answer("❌ Admins/Superadmins cannot be modified.", show_alert=True)
        return

    if action == "ban":
        block_user(telegram_id, user_type)
        await query.answer("✅ User banned", show_alert=True)
    else:
        unblock_user(telegram_id, user_type)
        await query.answer("✅ User unbanned", show_alert=True)

    await show_system_stats(update, context)

async def show_historical_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show historical chats (ended or sale-related) for admin view"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    chats = get_historical_chats()
    message = "🕘 Historical Chats\n\n"

    if not chats:
        message += get_string("no_chats", language)
        buttons = [[InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")]]
    else:
        buttons = []
        message += f"Total: {len(chats)} chats\n\n"

        for chat in chats:
            buyer = get_buyer_by_id(chat.buyer_id)
            supplier = get_supplier_by_id(chat.supplier_id)
            product = get_product_by_id(chat.product_id) if chat.product_id else None

            buyer_label = f"@{buyer.username}" if buyer and buyer.username else f"Buyer {chat.buyer_id}"
            seller_label = supplier.company_name if supplier else f"Seller {chat.supplier_id}"
            product_label = product.name if product else "General"
            state_label = "Ended" if not chat.active else "Sale-linked"

            message += f"{buyer_label} ↔ {seller_label} • {product_label} ({state_label})\n"
            buttons.append([
                InlineKeyboardButton(
                    f"📂 {buyer_label} • {product_label}",
                    callback_data=f"admin_chat_{chat.id}"
                )
            ])

        buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")])

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await query.answer()

async def show_admin_chat_details(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Show full chat details for admin, including buyer/seller profiles and product info"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    chat = get_chat(chat_id)
    if not chat:
        await query.answer(get_string("not_found", language), show_alert=True)
        return

    buyer = get_buyer_by_id(chat.buyer_id)
    supplier = get_supplier_by_id(chat.supplier_id)
    product = get_product_by_id(chat.product_id) if chat.product_id else None
    messages = get_chat_messages(chat_id, limit=20)

    buyer_name = " ".join(filter(None, [buyer.first_name if buyer else None, buyer.last_name if buyer else None])) if buyer else "N/A"
    if not buyer_name:
        buyer_name = "N/A"
    supplier_name = supplier.company_name if supplier else "N/A"
    product_name = product.name if product else "General / Not specified"
    status = "✅ Active" if chat.active else "❌ Inactive"

    message = f"📊 Chat #{chat.id} Details\n\n"
    message += f"Status: {status}\n"
    message += f"Product: {product_name}\n\n"
    message += f"👤 Buyer: {buyer_name}\n"
    message += f"   Buyer DB ID: {chat.buyer_id}\n"
    message += f"   Buyer Telegram ID: {buyer.telegram_id if buyer else 'N/A'}\n"
    message += f"   Buyer Username: @{buyer.username if buyer and buyer.username else 'N/A'}\n\n"
    message += f"🏪 Seller: {supplier_name}\n"
    message += f"   Seller DB ID: {chat.supplier_id}\n"
    message += f"   Seller Telegram ID: {supplier.telegram_id if supplier else 'N/A'}\n"
    message += f"   Seller Username: @{supplier.username if supplier and supplier.username else 'N/A'}\n\n"
    message += "📜 Last Messages:\n"
    message += "-" * 30 + "\n"

    if not messages:
        message += "No messages yet.\n"
    else:
        for msg in messages:
            sender = "Buyer" if msg.sender_type == "buyer" else "Seller"
            text = msg.message or ""
            if len(text) > 100:
                text = text[:100] + "..."
            message += f"\n{sender}: {text}\n"

    buttons = []
    if chat.active:
        buttons.append([InlineKeyboardButton("🛑 End Chat", callback_data=f"admin_end_chat_{chat.id}")])
    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_view_chats")])

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def end_chat_by_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Allow admin to end an active chat"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    chat = get_chat(chat_id)
    if not chat:
        await query.answer(get_string("not_found", language), show_alert=True)
        return

    if not chat.active:
        await query.answer("Chat is already ended.", show_alert=True)
        await show_admin_chat_details(update, context, chat_id)
        return

    if not end_chat(chat_id, chat.supplier_id):
        await query.answer("❌ Failed to end chat.", show_alert=True)
        return

    await query.answer("✅ Chat ended.", show_alert=True)
    await show_admin_chat_details(update, context, chat_id)

async def show_suppliers_management(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show suppliers management panel with pending verification requests"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    unverified = get_unverified_suppliers()
    all_suppliers = get_all_suppliers()
    
    message = f"""
🏪 {get_string("manage_suppliers_admin", language)}

Pending: {len(unverified)}
verified: {len([s for s in all_suppliers if s.status == 'verified'])}
Total: {len(all_suppliers)}
"""
    
    buttons = []
    
    if unverified:
        message += f"\n\n👤 {get_string('supplier_verification_requests', language)}:\n"
        for supplier in unverified:
            message += f"  • {supplier.company_name} (@{supplier.username})\n"
            buttons.append([
                InlineKeyboardButton(f"✅ Verify: {supplier.company_name}", callback_data=f"admin_verify_{supplier.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{supplier.id}")
            ])
    else:
        message += "\n\nAll suppliers verified or no pending requests.\n"
    
    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def handle_admin_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin actions"""
    query = update.callback_query
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    
    # Check admin access (database-driven)
    if not is_admin(user_id):
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    action_parts = query.data.split("_")
    action = action_parts[1]
    
    if action == "view" and action_parts[2] == "chats":
        await show_all_chats(update, context)
    elif action == "historical" and action_parts[2] == "chats":
        await show_historical_chats(update, context)
    elif action == "stats":
        if len(action_parts) == 2:
            await show_system_stats(update, context)
        elif action_parts[2] == "leaderboard":
            await show_sales_leaderboard(update, context)
        elif action_parts[2] == "referrals":
            await show_referral_leaderboard(update, context)
        elif action_parts[2] == "search":
            await prompt_user_search_for_moderation(update, context)
        elif action_parts[2] == "toggle":
            user_type = action_parts[3]
            target_telegram_id = int(action_parts[4])
            toggle_action = action_parts[5]
            await toggle_user_access_from_stats(update, context, user_type, target_telegram_id, toggle_action)
    elif action == "menu":
        await show_admin_panel(update, context, language)
    elif action == "suppliers":
        await show_suppliers_management(update, context)
    elif action == "manage" and action_parts[2] == "users":
        await show_manage_users(update, context)
    elif action == "manage" and action_parts[2] == "products":
        await show_manage_products(update, context)
    elif action == "chat":
        chat_id = int(action_parts[2])
        await show_admin_chat_details(update, context, chat_id)
    elif action == "end" and action_parts[2] == "chat":
        chat_id = int(action_parts[3])
        await end_chat_by_admin(update, context, chat_id)
    elif action == "add" and action_parts[2] == "product":
        if len(action_parts) == 3:
            await show_add_product_form(update, context)
        elif len(action_parts) == 5 and action_parts[3] == "supplier":
            supplier_id = int(action_parts[4])
            await finalize_new_product(update, context, supplier_id)
    elif action == "restock" and action_parts[2] == "product":
        product_id = int(action_parts[3])
        await show_restock_supplier_select(update, context, product_id)
    elif action == "restock" and action_parts[2] == "supplier":
        product_id = int(action_parts[3])
        supplier_id = int(action_parts[4])
        await show_restock_form(update, context, product_id, supplier_id)
    elif action == "support" and action_parts[2] == "chats":
        from handlers.chat_handlers import show_support_chats
        await show_support_chats(update, context)
    elif action == "delete" and action_parts[2] == "product":
        product_id = int(action_parts[3])
        await show_delete_product_confirm(update, context, product_id)
    elif action == "delete" and action_parts[2] == "confirm":
        product_id = int(action_parts[3])
        await delete_product_and_refresh(update, context, product_id)
    elif action == "pending" and action_parts[2] == "sales":
        await show_pending_sales(update, context, language)
    elif action == "review" and action_parts[2] == "sale":
        sale_id = int(action_parts[3])
        await review_sale(update, context, sale_id, language)
    elif action == "approve" and action_parts[2] == "sale":
        sale_id = int(action_parts[3])
        await approve_sale_handler(update, context, sale_id, user_id, language)
    elif action == "reject" and action_parts[2] == "sale":
        sale_id = int(action_parts[3])
        await reject_sale_handler(update, context, sale_id, user_id, language)
    elif action == "verify":
        supplier_id = int(action_parts[2])
        verify_supplier(supplier_id)
        await query.answer(get_string("success", language), show_alert=True)
        await show_suppliers_management(update, context)
    elif action == "reject" and len(action_parts) == 3:
        supplier_id = int(action_parts[2])
        reject_supplier(supplier_id)
        await query.answer("❌ Supplier rejected and banned", show_alert=True)
        await show_suppliers_management(update, context)
    
    await query.answer()

async def show_manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show manage users panel (admins/superadmins)"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    admins = get_all_admins()
    message = f"👥 {get_string('manage_users', language)}\n\n"
    message += f"Admins: {len(admins)}\n"

    buttons = []

    if is_superadmin(user_id):
        buttons.extend([
            [InlineKeyboardButton(get_string("add_admin", language), callback_data="superadmin_add_admin_form")],
            [InlineKeyboardButton(get_string("remove_admin", language), callback_data="superadmin_remove_admin_list")],
            [InlineKeyboardButton(get_string("list_admins", language), callback_data="superadmin_list_admins")],
        ])
    else:
        # Regular admins can only view support chats and suppliers
        buttons.append([InlineKeyboardButton(get_string("support", language), callback_data="admin_support_chats")])

    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def show_manage_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin product management"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    products = get_all_products()
    message = f"📦 {get_string('manage_products_admin', language)}\n\n"

    if not products:
        message += get_string("no_products", language)
    else:
        for product in products:
            message += f"• {product.name} (ID: {product.id})\n"

    buttons = [
        [InlineKeyboardButton(get_string("add_product", language), callback_data="admin_add_product")],
    ]

    if products:
        for product in products:
            buttons.append([
                InlineKeyboardButton(
                    f"🗑️ Delete {product.name}",
                    callback_data=f"admin_delete_product_{product.id}"
                )
            ])

        for product in products:
            out_of_stock = get_out_of_stock_suppliers(product.id)
            if out_of_stock:
                buttons.append([
                    InlineKeyboardButton(
                        f"➕ Restock {product.name}",
                        callback_data=f"admin_restock_product_{product.id}"
                    )
                ])

    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def show_add_product_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add product flow"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    context.user_data['admin_add_product'] = {
        "step": "name",
        "data": {},
    }

    await query.edit_message_text(
        text="➕ Add Product\n\nSend the product name:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")]
        ])
    )
    await query.answer()

async def show_new_product_supplier_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select verified seller to attach to new product"""
    language = context.user_data.get('language', 'en')
    suppliers = get_verified_suppliers()

    if not suppliers:
        await update.message.reply_text(get_string("not_found", language))
        return

    buttons = []
    message = "🔗 Select seller for this product:\n\n"
    for supplier in suppliers:
        message += f"✅ {supplier.company_name}\n"
        buttons.append([
            InlineKeyboardButton(
                supplier.company_name,
                callback_data=f"admin_add_product_supplier_{supplier.id}"
            )
        ])

    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")])
    reply_markup = InlineKeyboardMarkup(buttons)

    if update.callback_query:
        await update.callback_query.edit_message_text(text=message, reply_markup=reply_markup)
        await update.callback_query.answer()
    else:
        await update.message.reply_text(text=message, reply_markup=reply_markup)

async def finalize_new_product(update: Update, context: ContextTypes.DEFAULT_TYPE, supplier_id: int):
    """Create the product and attach it to the selected seller"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    flow = context.user_data.get('admin_add_product')
    if not flow:
        await query.answer(get_string("not_found", language), show_alert=True)
        return

    data = flow.get('data', {})
    if not data.get('name') or data.get('price') is None:
        context.user_data.pop('admin_add_product', None)
        await query.answer(get_string("operation_failed", language), show_alert=True)
        return

    product = create_product(
        name=data['name'],
        description=data.get('description'),
        category=data.get('category')
    )

    result = attach_product_to_supplier(
        product_id=product.id,
        supplier_id=supplier_id,
        price=data['price'],
        stock=data.get('stock', -1),
        currency="USD"
    )

    context.user_data.pop('admin_add_product', None)

    if result:
        await query.edit_message_text(
            text=f"✅ Product created and linked to seller: {product.name} (ID: {product.id})",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")]
            ])
        )
    else:
        await query.edit_message_text(
            text=get_string("operation_failed", language),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")]
            ])
        )
    await query.answer()

async def show_delete_product_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    """Confirm product deletion"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    product = get_product_by_id(product_id)
    if not product:
        await query.answer(get_string("not_found", language), show_alert=True)
        return

    message = f"🗑️ Delete product?\n\n{product.name} (ID: {product.id})"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Delete", callback_data=f"admin_delete_confirm_{product_id}")],
        [InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")],
    ])

    await query.edit_message_text(text=message, reply_markup=reply_markup)
    await query.answer()

async def delete_product_and_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    """Delete product and refresh management view"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    if delete_product(product_id):
        await query.answer(get_string("success", language), show_alert=True)
    else:
        await query.answer(get_string("operation_failed", language), show_alert=True)

    await show_manage_products(update, context)

async def show_restock_supplier_select(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    """Select out-of-stock seller to restock"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    product = get_product_by_id(product_id)
    if not product:
        await query.answer(get_string("not_found", language), show_alert=True)
        return

    suppliers = get_out_of_stock_suppliers(product_id)
    if not suppliers:
        await query.edit_message_text(
            text="✅ No out-of-stock sellers for this product.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")]
            ])
        )
        await query.answer()
        return

    message = f"➕ Restock {product.name}\n\nSelect seller:\n"
    buttons = []
    for supplier in suppliers:
        buttons.append([
            InlineKeyboardButton(
                supplier["supplier_name"],
                callback_data=f"admin_restock_supplier_{product_id}_{supplier['supplier_id']}"
            )
        ])

    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")])
    await query.edit_message_text(text=message, reply_markup=InlineKeyboardMarkup(buttons))
    await query.answer()

async def show_restock_form(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int, supplier_id: int):
    """Ask admin for new stock quantity"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    product = get_product_by_id(product_id)
    supplier = get_supplier_by_id(supplier_id)
    if not product or not supplier:
        await query.answer(get_string("not_found", language), show_alert=True)
        return

    context.user_data['admin_restock'] = {
        "step": "stock",
        "product_id": product_id,
        "supplier_id": supplier_id,
    }

    await query.edit_message_text(
        text=f"➕ Restock {product.name} for {supplier.company_name}\n\nSend new stock quantity:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")]
        ])
    )
    await query.answer()

async def show_attach_product_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Select product to attach"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    products = get_all_products()
    if not products:
        await query.edit_message_text(get_string("no_products", language))
        await query.answer()
        return

    buttons = []
    message = "🔗 Select product to attach:\n\n"
    for product in products:
        message += f"• {product.name} (ID: {product.id})\n"
        buttons.append([
            InlineKeyboardButton(product.name, callback_data=f"admin_attach_product_{product.id}")
        ])

    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=message, reply_markup=reply_markup)
    await query.answer()

async def show_attach_supplier_select(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    """Select verified supplier to attach to product"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    from database_helpers import get_verified_suppliers
    suppliers = get_verified_suppliers()
    if not suppliers:
        await query.edit_message_text(get_string("not_found", language))
        await query.answer()
        return

    buttons = []
    message = "🔗 Select seller to attach:\n\n"
    for supplier in suppliers:
        message += f"✅ {supplier.company_name}\n"
        buttons.append([
            InlineKeyboardButton(supplier.company_name, callback_data=f"admin_attach_supplier_{product_id}_{supplier.id}")
        ])

    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")])
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text=message, reply_markup=reply_markup)
    await query.answer()

async def show_attach_price_form(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int, supplier_id: int):
    """Ask admin for USD price and stock"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query

    product = get_product_by_id(product_id)
    supplier = get_supplier_by_id(supplier_id)
    if not product or not supplier:
        await query.answer(get_string("not_found", language), show_alert=True)
        return

    context.user_data['admin_attach_product'] = {
        "step": "price",
        "product_id": product_id,
        "supplier_id": supplier_id,
    }

    await query.edit_message_text(
        text=f"💰 Set price for {product.name} at {supplier.company_name}\n\n{get_string('enter_usd_price', language)}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("back", language), callback_data="admin_manage_products")]
        ])
    )
    await query.answer()


# ==================== SUPERADMIN PANEL ====================

async def show_superadmin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show superadmin panel menu"""
    query = update.callback_query
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    
    # Verify user is superadmin
    if not is_superadmin(user_id):
        await query.answer("❌ Only superadmin can access this!", show_alert=True)
        return
    
    keyboard = [
        [InlineKeyboardButton("➕ Add New Admin", callback_data="superadmin_add_admin_form")],
        [InlineKeyboardButton("❌ Remove Admin", callback_data="superadmin_remove_admin_list")],
        [InlineKeyboardButton("👥 List All Admins", callback_data="superadmin_list_admins")],
        [InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_menu")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
👑 SUPERADMIN PANEL

You have exclusive rights to:
✅ Add new admins
✅ Remove admins
✅ View all admins

Choose an option:
"""
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()


async def show_add_admin_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show form to add new admin"""
    query = update.callback_query
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    
    # Verify user is superadmin
    if not is_superadmin(user_id):
        await query.answer("❌ Only superadmin can add admins!", show_alert=True)
        return
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="superadmin_menu")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = """
➕ ADD NEW ADMIN

Send me the Telegram ID of the user you want to make an admin.

Example: 123456789

⚠️ Make sure the user has used the bot at least once!
"""
    
    context.user_data['waiting_for_admin_id'] = True
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()


async def show_remove_admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of admins to remove"""
    query = update.callback_query
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    
    # Verify user is superadmin
    if not is_superadmin(user_id):
        await query.answer("❌ Only superadmin can remove admins!", show_alert=True)
        return
    
    all_admins = get_all_admins()
    
    if not all_admins:
        message = "❌ No admins to remove (other than you)"
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="superadmin_menu")]]
    else:
        buttons = []
        message = "❌ SELECT ADMIN TO REMOVE\n\n"
        
        for admin in all_admins:
            # Don't allow removing superadmin
            role = "👑 SUPERADMIN" if admin.is_superadmin else "👨‍💼 Admin"
            
            if admin.is_superadmin:
                message += f"• {role} - @{admin.username or 'No username'} (ID: {admin.telegram_id})\n"
                message += "  ⚠️ Cannot remove superadmin\n\n"
            else:
                message += f"• {role} - @{admin.username or 'No username'} (ID: {admin.telegram_id})\n"
                buttons.append([
                    InlineKeyboardButton(
                        f"❌ Remove {admin.username or admin.telegram_id}",
                        callback_data=f"superadmin_confirm_remove_{admin.telegram_id}"
                    )
                ])
        
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="superadmin_menu")])
        keyboard = buttons
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()


async def show_confirm_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show confirmation before removing admin"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Verify user is superadmin
    if not is_superadmin(user_id):
        await query.answer("❌ Only superadmin can remove admins!", show_alert=True)
        return
    
    # Extract admin_id to remove
    admin_id_to_remove = int(query.data.split("_")[3])
    
    admin = get_admin(admin_id_to_remove)
    if not admin:
        await query.answer("❌ Admin not found!", show_alert=True)
        return
    
    # Store the admin_id in context for confirmation
    context.user_data['admin_to_remove'] = admin_id_to_remove
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm Remove", callback_data="superadmin_execute_remove"),
            InlineKeyboardButton("❌ Cancel", callback_data="superadmin_remove_admin_list"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = f"""
⚠️ CONFIRM REMOVAL

You are about to remove:
• Name: {admin.first_name or 'Unknown'}
• Username: @{admin.username or 'No username'}
• Telegram ID: {admin.telegram_id}

This action cannot be undone!

Are you sure?
"""
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()


async def execute_remove_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Execute the removal of an admin"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    # Verify user is superadmin
    if not is_superadmin(user_id):
        await query.answer("❌ Only superadmin can remove admins!", show_alert=True)
        return
    
    admin_id_to_remove = context.user_data.get('admin_to_remove')
    
    if not admin_id_to_remove:
        await query.answer("❌ No admin selected!", show_alert=True)
        return
    
    # Remove the admin
    success = remove_admin(admin_id_to_remove, user_id)
    
    if success:
        await query.answer("✅ Admin removed successfully!", show_alert=True)
        context.user_data.pop('admin_to_remove', None)
        await show_remove_admin_list(update, context)
    else:
        await query.answer("❌ Failed to remove admin!", show_alert=True)


async def show_list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of all current admins"""
    query = update.callback_query
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    
    # Verify user is superadmin
    if not is_superadmin(user_id):
        await query.answer("❌ Only superadmin can view this!", show_alert=True)
        return
    
    all_admins = get_all_admins()
    
    if not all_admins:
        message = "❌ No admins found"
    else:
        message = "👥 ALL CURRENT ADMINS\n\n"
        
        for admin in all_admins:
            role = "👑 SUPERADMIN" if admin.is_superadmin else "👨‍💼 Admin"
            status = "✅ Active" if admin.is_active else "❌ Inactive"
            
            message += f"{role}\n"
            message += f"• Name: {admin.first_name or 'Unknown'} {admin.last_name or ''}\n"
            message += f"• Username: @{admin.username or 'No username'}\n"
            message += f"• ID: {admin.telegram_id}\n"
            message += f"• Status: {status}\n"
            message += f"• Added: {admin.added_date.strftime('%Y-%m-%d %H:%M') if admin.added_date else 'Unknown'}\n"
            
            if admin.added_by_telegram_id:
                message += f"• Added by: {admin.added_by_telegram_id}\n"
            
            message += "\n"
    
    keyboard = [
        [InlineKeyboardButton("🔙 Back", callback_data="superadmin_menu")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

# ==================== ADMIN ID INPUT HANDLER ====================

async def process_add_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process the telegram ID sent by superadmin to add as admin"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')

    # Handle admin product creation flow
    if context.user_data.get('admin_add_product'):
        if not is_admin(user_id):
            await update.message.reply_text(get_string("unauthorized", language))
            context.user_data.pop('admin_add_product', None)
            return

        flow = context.user_data['admin_add_product']
        step = flow.get('step')
        text = update.message.text.strip()

        if step == "name":
            flow['data']['name'] = text
            flow['step'] = "description"
            await update.message.reply_text("Send product description:")
            return
        if step == "description":
            if not text:
                await update.message.reply_text("❌ Description cannot be empty. Send product description:")
                return
            flow['data']['description'] = text
            flow['step'] = "category"
            await update.message.reply_text("Send product category:")
            return
        if step == "category":
            if not text:
                await update.message.reply_text("❌ Category cannot be empty. Send product category:")
                return
            flow['data']['category'] = text
            flow['step'] = "price"
            await update.message.reply_text("Send product price (USD):")
            return
        if step == "price":
            try:
                price = float(text)
                if price <= 0:
                    raise ValueError()
            except ValueError:
                await update.message.reply_text("❌ Please send a valid price (e.g. 19.99)")
                return
            flow['data']['price'] = price
            flow['step'] = "stock"
            await update.message.reply_text("Send stock quantity (number) or '-' to skip:")
            return
        if step == "stock":
            if text in {"-", "skip", "Skip"}:
                flow['data']['stock'] = -1
            else:
                try:
                    stock = int(text)
                    if stock < 0:
                        raise ValueError()
                except ValueError:
                    await update.message.reply_text("❌ Please send a valid stock number (e.g. 10) or '-' to skip")
                    return

                flow['data']['stock'] = stock
            flow['step'] = "supplier"
            await show_new_product_supplier_select(update, context)
            return

    if context.user_data.get('stats_user_search_mode'):
        if not is_admin(user_id):
            await update.message.reply_text(get_string("unauthorized", language))
            context.user_data.pop('stats_user_search_mode', None)
            return

        text = update.message.text.strip()
        try:
            target_telegram_id = int(text)
        except ValueError:
            await update.message.reply_text("❌ Please send a valid Telegram ID (numbers only).")
            return

        context.user_data.pop('stats_user_search_mode', None)
        await show_user_moderation_result(update, context, target_telegram_id)
        return

    if context.user_data.get('admin_restock'):
        if not is_admin(user_id):
            await update.message.reply_text(get_string("unauthorized", language))
            context.user_data.pop('admin_restock', None)
            return

        flow = context.user_data['admin_restock']
        step = flow.get('step')
        text = update.message.text.strip()

        if step == "stock":
            try:
                stock = int(text)
                if stock < 0:
                    raise ValueError()
            except ValueError:
                await update.message.reply_text("❌ Please send a valid stock number (e.g. 10)")
                return

            result = update_product_stock(
                product_id=flow['product_id'],
                supplier_id=flow['supplier_id'],
                stock=stock
            )
            context.user_data.pop('admin_restock', None)
            if result:
                await update.message.reply_text("✅ Stock updated")
            else:
                await update.message.reply_text(get_string("operation_failed", language))
            return
    
    # Check if user is waiting for admin ID input
    if not context.user_data.get('waiting_for_admin_id', False):
        # Not waiting for admin ID, let other handlers process this
        from handlers import chat_handlers
        await chat_handlers.handle_message(update, context)
        return
    
    # Check if user is superadmin
    if not is_superadmin(user_id):
        await update.message.reply_text(
            "❌ Only superadmin can add admins!",
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_admin_id'] = False
        return
    
    # Extract the admin ID
    try:
        new_admin_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text(
            "❌ Please send a valid Telegram ID (numbers only)",
            parse_mode='Markdown'
        )
        return
    
    # Check if user is trying to add themselves
    if new_admin_id == user_id:
        await update.message.reply_text(
            "❌ You are already superadmin!",
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_admin_id'] = False
        return
    
    # Check if user is already an admin
    if is_admin(new_admin_id):
        admin = get_admin(new_admin_id)
        admin_type = "SUPERADMIN" if admin.is_superadmin else "Admin"
        await update.message.reply_text(
            f"⚠️ User {new_admin_id} is already an {admin_type}!",
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_admin_id'] = False
        return
    
    # Try to add the admin
    new_admin = add_admin(
        telegram_id=new_admin_id,
        added_by_telegram_id=user_id,
        username=None,
        first_name=None,
        last_name=None
    )
    
    if new_admin:
        await update.message.reply_text(
            f"""
✅ SUCCESS!

New admin added:
• ID: {new_admin_id}
• Added by: Superadmin

The user will become an admin when they next interact with the bot.
""",
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_admin_id'] = False
    else:
        await update.message.reply_text(
            "❌ Failed to add admin. Please try again.",
            parse_mode='Markdown'
        )
    
    # Show superadmin menu again
    keyboard = [
        [InlineKeyboardButton("👑 Superadmin Panel", callback_data="superadmin_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Returning to superadmin panel...",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ============================================================================
# SALE VERIFICATION HANDLERS
# ============================================================================

async def show_pending_sales(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show list of pending sales awaiting verification"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    if not is_admin(user_id):
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Get pending sales
    pending_sales = get_pending_sale_proofs()
    
    if not pending_sales:
        message = get_string("no_pending_sales", language)
        buttons = [[InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    message = f"📋 {get_string('pending_sales', language)}\n\n"
    message += f"Found {len(pending_sales)} sales awaiting verification:\n\n"
    
    buttons = []
    for sale in pending_sales:
        buyer_name = sale.buyer.first_name or "Anonymous Buyer"
        supplier_name = sale.supplier.company_name if sale.supplier else "Unknown"
        product_name = sale.product.name if sale.product else "Unknown Product"
        
        message += f"📌 Sale #{sale.id}\n"
        message += f"  Buyer: {buyer_name}\n"
        message += f"  Seller: {supplier_name}\n"
        message += f"  Product: {product_name}\n"
        message += f"  Status: {sale.status}\n\n"
        
        buttons.append([
            InlineKeyboardButton(f"Review Sale #{sale.id}", callback_data=f"admin_review_sale_{sale.id}")
        ])
    
    buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")])
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def review_sale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Review a specific sale with payment proof"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    if not is_admin(user_id):
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Extract sale_id from callback data: admin_review_sale_{sale_id}
    sale_id = int(query.data.split("_")[-1])
    
    sale = get_sale_by_id(sale_id)
    if not sale:
        await query.answer(get_string("not_found", language), show_alert=True)
        return
    
    message = f"""
👁️ {get_string('review_sale', language)}

{get_string('sale_status', language)}: {sale.status}
{get_string('buyer', language)}: {sale.buyer.first_name or 'Anonymous'}
{get_string('seller', language)}: {sale.supplier.company_name}
{get_string('product', language)}: {sale.product.name if sale.product else 'Unknown'}
Quantity: {sale.quantity}

📸 Payment Proof:
"""
    
    if sale.proof:
        for proof in sale.proof:
            message += f"\nType: {proof.file_type}\n"
            if proof.caption:
                message += f"Description: {proof.caption}\n"
    else:
        message += "\n(No proof attached)"
    
    # Store sale ID for approval/rejection
    context.user_data['reviewing_sale_id'] = sale_id
    
    buttons = [
        [InlineKeyboardButton(get_string("approve_sale", language), callback_data=f"admin_approve_sale_{sale_id}")],
        [InlineKeyboardButton(get_string("reject_sale", language), callback_data=f"admin_reject_sale_{sale_id}")],
        [InlineKeyboardButton(get_string("back", language), callback_data="admin_pending_sales")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def approve_sale_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a sale (reduce stock and mark as verified)"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    if not is_admin(user_id):
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Extract sale_id from callback data: admin_approve_sale_{sale_id}
    sale_id = int(query.data.split("_")[-1])
    
    # Approve sale (this also reduces stock if tracked)
    success = approve_sale(sale_id, user_id)
    
    if success:
        await query.answer(get_string("sale_verified", language), show_alert=True)
    else:
        await query.answer(get_string("error", language), show_alert=True)
    
    # Show pending sales again
    await show_pending_sales(update, context)

async def reject_sale_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject a sale (mark as rejected, do not reduce stock)"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    if not is_admin(user_id):
        await query.answer(get_string("unauthorized", language), show_alert=True)
        return
    
    # Extract sale_id from callback data: admin_reject_sale_{sale_id}
    sale_id = int(query.data.split("_")[-1])
    
    # Reject sale
    success = reject_sale(sale_id, user_id)
    
    if success:
        await query.answer(get_string("sale_rejected", language), show_alert=True)
    else:
        await query.answer(get_string("error", language), show_alert=True)
    
    # Show pending sales again
    await show_pending_sales(update, context)


# ============= CSV PRODUCT IMPORT =============

async def request_csv_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Request CSV file upload from admin"""
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    if not is_admin(user_id):
        await query.answer("Unauthorized", show_alert=True)
        return
    
    # Reset CSV import context
    context.user_data['csv_import_state'] = 'waiting_for_file'
    context.user_data['csv_products'] = []
    context.user_data['csv_current_index'] = 0
    
    message = """
📊 **CSV Product Import**

Please upload a CSV file with the following format:

```
Product Name
Item 1
Item 2
Item 3
...
```

One product name per line. I will guide you through the rest!

⚠️ Duplicate names will be detected and handled.
"""
    
    if query:
        await query.edit_message_text(
            text=message,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text=message,
            parse_mode='Markdown'
        )


async def handle_csv_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle CSV file upload for product import"""
    import csv
    import io
    
    user_id = update.effective_user.id
    language = context.user_data.get('language', 'en')
    
    if not is_admin(user_id):
        return
    
    # Check if in CSV import mode
    if context.user_data.get('csv_import_state') != 'waiting_for_file':
        return
    
    # Get the file
    if not update.message.document:
        await update.message.reply_text("❌ Please upload a CSV file")
        return
    
    file = await update.message.document.get_file()
    file_content = await file.download_as_bytearray()
    
    try:
        # Parse CSV
        text_content = file_content.decode('utf-8')
        reader = csv.reader(io.StringIO(text_content))
        
        product_names = []
        for row in reader:
            if row and row[0].strip():  # Skip empty rows
                product_names.append(row[0].strip())
        
        if not product_names:
            await update.message.reply_text("❌ No products found in CSV")
            context.user_data['csv_import_state'] = None
            return
        
        # Check for duplicates in CSV
        from database_helpers import get_all_products
        existing_products = {p.name.lower() for p in get_all_products()}
        
        duplicates_in_csv = []
        conflicts_with_existing = []
        valid_products = []
        
        for product_name in product_names:
            lower_name = product_name.lower()
            if lower_name in [p.lower() for p in duplicates_in_csv]:
                duplicates_in_csv.append(product_name)
            elif lower_name in existing_products:
                conflicts_with_existing.append(product_name)
            else:
                valid_products.append(product_name)
        
        # Build conflict report
        conflict_msg = f"📊 **CSV Upload Report**\n\n"
        conflict_msg += f"✅ **Valid products:** {len(valid_products)}\n"
        
        if duplicates_in_csv:
            conflict_msg += f"⚠️ **Duplicates in CSV:** {len(duplicates_in_csv)}\n"
            conflict_msg += f"   {', '.join(duplicates_in_csv[:5])}"
            if len(duplicates_in_csv) > 5:
                conflict_msg += f" ... and {len(duplicates_in_csv) - 5} more\n"
        
        if conflicts_with_existing:
            conflict_msg += f"🚫 **Already exist:** {len(conflicts_with_existing)}\n"
            conflict_msg += f"   {', '.join(conflicts_with_existing[:5])}"
            if len(conflicts_with_existing) > 5:
                conflict_msg += f" ... and {len(conflicts_with_existing) - 5} more\n"
        
        conflict_msg += f"\n**Proceeding with {len(valid_products)} products**\n"
        conflict_msg += "Next: I'll ask for supplier and price for each product."
        
        await update.message.reply_text(conflict_msg, parse_mode='Markdown')
        
        # Store valid products and move to next step
        context.user_data['csv_products'] = [
            {'name': name, 'supplier_id': None, 'price': None}
            for name in valid_products
        ]
        context.user_data['csv_current_index'] = 0
        context.user_data['csv_import_state'] = 'asking_supplier'
        
        # Ask for first product's supplier
        await ask_for_product_details(update, context, language)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error parsing CSV: {str(e)}")
        context.user_data['csv_import_state'] = None


async def ask_for_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Ask for supplier and price for current product"""
    products = context.user_data.get('csv_products', [])
    current_idx = context.user_data.get('csv_current_index', 0)
    
    if current_idx >= len(products):
        # All done, show confirmation
        await show_csv_import_summary(update, context, language)
        return
    
    current_product = products[current_idx]
    product_name = current_product['name']
    
    from database_helpers import get_verified_suppliers
    suppliers = get_verified_suppliers()
    
    if not suppliers:
        await update.message.reply_text("❌ No verified suppliers available. Please add suppliers first.")
        context.user_data['csv_import_state'] = None
        return
    
    # Build supplier keyboard
    buttons = []
    for supplier in suppliers:
        buttons.append([
            InlineKeyboardButton(
                supplier.company_name,
                callback_data=f"csv_select_supplier_{current_idx}_{supplier.id}"
            )
        ])
    
    buttons.append([InlineKeyboardButton("❌ Cancel Import", callback_data="admin_menu")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    message = f"""
📦 **Product {current_idx + 1} of {len(products)}**

**Name:** {product_name}

👤 Select supplier to assign:
"""
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def handle_csv_supplier_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle supplier selection for CSV product"""
    query = update.callback_query
    language = context.user_data.get('language', 'en')
    
    # Extract product index and supplier ID
    parts = query.data.split("_")
    product_idx = int(parts[3])
    supplier_id = int(parts[4])
    
    products = context.user_data.get('csv_products', [])
    if product_idx >= len(products):
        await query.answer("Invalid product index", show_alert=True)
        return
    
    # Store supplier ID
    products[product_idx]['supplier_id'] = supplier_id
    context.user_data['csv_products'] = products
    
    # Ask for price
    from database_helpers import get_supplier_by_id
    supplier = get_supplier_by_id(supplier_id)
    
    message = f"""
💰 **Enter Price**

Product: {products[product_idx]['name']}
Supplier: {supplier.company_name}

Please reply with the product price (numbers only, e.g., 100 or 99.99):
"""
    
    await query.edit_message_text(message, parse_mode='Markdown')
    context.user_data['csv_current_index'] = product_idx
    context.user_data['csv_import_state'] = 'asking_price'


async def handle_csv_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle price input for CSV product"""
    language = context.user_data.get('language', 'en')
    
    if context.user_data.get('csv_import_state') != 'asking_price':
        return
    
    try:
        price = float(update.message.text)
        if price <= 0:
            await update.message.reply_text("❌ Price must be greater than 0")
            return
    except ValueError:
        await update.message.reply_text("❌ Invalid price format. Please enter a number.")
        return
    
    # Store price and move to next product
    products = context.user_data.get('csv_products', [])
    current_idx = context.user_data.get('csv_current_index', 0)
    
    products[current_idx]['price'] = price
    context.user_data['csv_products'] = products
    context.user_data['csv_current_index'] = current_idx + 1
    context.user_data['csv_import_state'] = 'asking_supplier'
    
    # Ask for next product or show summary
    if current_idx + 1 < len(products):
        await ask_for_product_details(update, context, language)
    else:
        await show_csv_import_summary(update, context, language)


async def show_csv_import_summary(update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
    """Show summary and ask for confirmation before importing"""
    products = context.user_data.get('csv_products', [])
    
    message = "📋 **Import Summary**\n\n"
    message += f"Total products to import: {len(products)}\n\n"
    
    from database_helpers import get_supplier_by_id
    
    for idx, product in enumerate(products, 1):
        supplier = get_supplier_by_id(product['supplier_id'])
        message += f"{idx}. **{product['name']}**\n"
        message += f"   Supplier: {supplier.company_name}\n"
        message += f"   Price: {product['price']}\n\n"
    
    message += "✅ Click below to confirm import, or ❌ to cancel"
    
    buttons = [
        [InlineKeyboardButton("✅ Confirm & Import", callback_data="csv_confirm_import")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    context.user_data['csv_import_state'] = 'awaiting_confirmation'


async def handle_csv_import_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and save all CSV imported products"""
    query = update.callback_query
    language = context.user_data.get('language', 'en')
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await query.answer("Unauthorized", show_alert=True)
        return
    
    products = context.user_data.get('csv_products', [])
    
    if not products:
        await query.answer("No products to import", show_alert=True)
        return
    
    try:
        from database_helpers import create_product, attach_product_to_supplier, update_product_price
        
        imported_count = 0
        for product_data in products:
            # Create product
            product = create_product(
                name=product_data['name'],
                description=f"Imported from CSV",
                category="Imported",
                active=True
            )
            
            # Attach to supplier
            attach_product_to_supplier(product.id, product_data['supplier_id'])
            
            # Set price
            if product_data['price']:
                update_product_price(product.id, product_data['supplier_id'], product_data['price'])
            
            imported_count += 1
        
        # Clear context
        context.user_data['csv_products'] = []
        context.user_data['csv_import_state'] = None
        
        message = f"✅ **Import Successful!**\n\nImported {imported_count} products\n\nAll products have been added with their assigned suppliers and prices."
        await query.edit_message_text(message, parse_mode='Markdown')
        
        # Show admin menu
        await show_admin_panel(update, context, language)
        
    except Exception as e:
        await query.answer(f"Error importing: {str(e)}", show_alert=True)
        logger.error(f"CSV import error: {e}")
        context.user_data['csv_import_state'] = None
    await show_pending_sales(update, context)