from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from strings import get_string
from database_helpers import (
    get_all_suppliers,
    get_unverified_suppliers,
    get_all_chats,
    get_system_stats,
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
    get_supplier_by_id,
    attach_product_to_supplier,
    get_verified_suppliers,
    get_out_of_stock_suppliers,
    update_product_stock,
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
        [InlineKeyboardButton(get_string("manage_users", language), callback_data="admin_manage_users")],
        [InlineKeyboardButton(get_string("manage_suppliers_admin", language), callback_data="admin_suppliers")],
        [InlineKeyboardButton(get_string("manage_products_admin", language), callback_data="admin_manage_products")],
        [InlineKeyboardButton("🔍 " + get_string("pending_sales", language), callback_data="admin_pending_sales")],
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
            status = "✅ Active" if chat.active else "❌ Inactive"
            message += f"Chat #{chat.id} - Buyer: {chat.buyer_id}, Supplier: {chat.supplier_id} - {status}\n"
            
            buttons.append([
                InlineKeyboardButton(f"📊 Chat #{chat.id}", callback_data=f"admin_chat_{chat.id}")
            ])
        
        buttons.append([InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

async def show_system_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system statistics"""
    language = context.user_data.get('language', 'en')
    query = update.callback_query
    
    stats = get_system_stats()
    
    message = f"""
📊 {get_string("system_stats", language)}

👥 Total Buyers: {stats['total_buyers']}
🏪 Total Suppliers: {stats['total_suppliers']}
💬 Active Chats: {stats['active_chats']}
📦 Total Products: {stats['total_products']}
💭 Total Messages: {stats['total_messages']}
"""
    
    buttons = [
        [InlineKeyboardButton(get_string("back", language), callback_data="admin_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    await query.answer()

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
    elif action == "stats":
        await show_system_stats(update, context)
    elif action == "menu":
        await show_admin_panel(update, context, language)
    elif action == "suppliers":
        await show_suppliers_management(update, context)
    elif action == "manage" and action_parts[2] == "users":
        await show_manage_users(update, context)
    elif action == "manage" and action_parts[2] == "products":
        await show_manage_products(update, context)
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