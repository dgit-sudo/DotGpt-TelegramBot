from database import SessionLocal, Product, Supplier, Buyer, Chat, ChatMessage, ProductPrice, SupplierPaymentMethod, AdminUser, SupportChat, SupportMessage
from typing import List, Optional
from sqlalchemy import and_, or_

def get_or_create_buyer(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None, language: str = "en") -> Buyer:
    """Get or create buyer with language preference"""
    db = SessionLocal()
    buyer = db.query(Buyer).filter(Buyer.telegram_id == telegram_id).first()
    
    if not buyer:
        buyer = Buyer(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language=language
        )
        db.add(buyer)
        db.commit()
    else:
        # Update language if provided
        buyer.language = language
        db.commit()
    db.close()
    return buyer

def get_or_create_supplier(telegram_id: int, company_name: str, username: str = None) -> Supplier:
    """Get or create supplier"""
    db = SessionLocal()
    supplier = db.query(Supplier).filter(Supplier.telegram_id == telegram_id).first()
    
    if not supplier:
        supplier = Supplier(
            telegram_id=telegram_id,
            company_name=company_name,
            username=username
        )
        db.add(supplier)
        db.commit()
    db.close()
    return supplier

def get_supplier(telegram_id: int) -> Optional[Supplier]:
    """Get supplier by telegram ID"""
    db = SessionLocal()
    supplier = db.query(Supplier).filter(Supplier.telegram_id == telegram_id).first()
    db.close()
    return supplier

def get_buyer(telegram_id: int) -> Optional[Buyer]:
    """Get buyer by telegram ID"""
    db = SessionLocal()
    buyer = db.query(Buyer).filter(Buyer.telegram_id == telegram_id).first()
    db.close()
    return buyer

def get_products_by_supplier(supplier_id: int) -> List[Product]:
    """Get all products for a supplier"""
    db = SessionLocal()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    products = supplier.products if supplier else []
    db.close()
    return products

def get_all_products() -> List[Product]:
    """Get all products"""
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return products

def get_product_by_id(product_id: int) -> Optional[Product]:
    """Get product by ID"""
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    return product

def get_supplier_by_id(supplier_id: int) -> Optional[Supplier]:
    """Get supplier by ID"""
    db = SessionLocal()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    db.close()
    return supplier

def create_product(name: str, description: str = None, category: str = None) -> Product:
    """Create a new product"""
    db = SessionLocal()
    product = Product(
        name=name,
        description=description,
        category=category,
        active=True
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    db.close()
    return product

def delete_product(product_id: int) -> bool:
    """Delete a product and related pricing entries"""
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        db.close()
        return False

    db.query(ProductPrice).filter(ProductPrice.product_id == product_id).delete()
    product.suppliers.clear()
    db.delete(product)
    db.commit()
    db.close()
    return True

def attach_product_to_supplier(product_id: int, supplier_id: int, price: float, currency: str = "USD", stock: int = 0) -> ProductPrice:
    """Attach product to supplier with pricing"""
    db = SessionLocal()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not supplier or not product:
        db.close()
        return None

    if product not in supplier.products:
        supplier.products.append(product)

    price_entry = db.query(ProductPrice).filter(
        and_(ProductPrice.product_id == product_id, ProductPrice.supplier_id == supplier_id)
    ).first()

    if not price_entry:
        price_entry = ProductPrice(
            product_id=product_id,
            supplier_id=supplier_id,
            price=price,
            currency=currency,
            stock=stock
        )
        db.add(price_entry)
    else:
        price_entry.price = price
        price_entry.currency = currency
        price_entry.stock = stock

    db.commit()
    db.refresh(price_entry)
    db.close()
    return price_entry

def get_out_of_stock_suppliers(product_id: int) -> List[dict]:
    """Get suppliers for a product that are out of stock (stock == 0)"""
    db = SessionLocal()
    results = (
        db.query(ProductPrice, Supplier)
        .join(Supplier, ProductPrice.supplier_id == Supplier.id)
        .filter(
            ProductPrice.product_id == product_id,
            ProductPrice.stock == 0
        )
        .all()
    )

    out_of_stock = [
        {
            "supplier_id": supplier.id,
            "supplier_name": supplier.company_name,
        }
        for price, supplier in results
    ]
    db.close()
    return out_of_stock

def update_product_stock(product_id: int, supplier_id: int, stock: int) -> bool:
    """Update stock for a product-supplier price entry"""
    db = SessionLocal()
    price_entry = db.query(ProductPrice).filter(
        and_(ProductPrice.product_id == product_id, ProductPrice.supplier_id == supplier_id)
    ).first()
    if not price_entry:
        db.close()
        return False

    price_entry.stock = stock
    db.commit()
    db.close()
    return True

def get_all_active_products() -> List[Product]:
    """Get all active products"""
    db = SessionLocal()
    products = db.query(Product).filter(Product.active == True).all()
    db.close()
    return products

def get_product_price(product_id: int, supplier_id: int) -> Optional[ProductPrice]:
    """Get product price for supplier"""
    db = SessionLocal()
    price = db.query(ProductPrice).filter(
        and_(ProductPrice.product_id == product_id, ProductPrice.supplier_id == supplier_id)
    ).first()
    db.close()
    return price

def get_supplier_payment_methods(supplier_id: int) -> List[SupplierPaymentMethod]:
    """Get payment methods for supplier"""
    db = SessionLocal()
    methods = db.query(SupplierPaymentMethod).filter(
        SupplierPaymentMethod.supplier_id == supplier_id
    ).all()
    db.close()
    return methods

def get_or_create_chat(buyer_id: int, supplier_id: int, product_id: int = None) -> Chat:
    """Get or create chat between buyer and supplier"""
    db = SessionLocal()
    chat = db.query(Chat).filter(
        and_(Chat.buyer_id == buyer_id, Chat.supplier_id == supplier_id)
    ).first()
    
    if not chat:
        chat = Chat(
            buyer_id=buyer_id,
            supplier_id=supplier_id,
            product_id=product_id,
            active=True
        )
        db.add(chat)
        db.commit()
    db.close()
    return chat

def get_chat(chat_id: int) -> Optional[Chat]:
    """Get chat by ID"""
    db = SessionLocal()
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    db.close()
    return chat

def get_buyer_chats(buyer_id: int) -> List[Chat]:
    """Get all chats for a buyer"""
    db = SessionLocal()
    chats = db.query(Chat).filter(Chat.buyer_id == buyer_id).all()
    db.close()
    return chats

def get_supplier_chats(supplier_id: int) -> List[Chat]:
    """Get all chats for a supplier"""
    db = SessionLocal()
    chats = db.query(Chat).filter(Chat.supplier_id == supplier_id).all()
    db.close()
    return chats

def save_chat_message(chat_id: int, sender_id: int, sender_type: str, message: str) -> ChatMessage:
    """Save chat message"""
    db = SessionLocal()
    msg = ChatMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        sender_type=sender_type,
        message=message
    )
    db.add(msg)
    db.commit()
    db.close()
    return msg

def get_chat_messages(chat_id: int, limit: int = 50) -> List[ChatMessage]:
    """Get messages from chat"""
    db = SessionLocal()
    messages = db.query(ChatMessage).filter(
        ChatMessage.chat_id == chat_id
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    db.close()
    return list(reversed(messages))

def get_all_chats():
    """Get all chats (for admin)"""
    db = SessionLocal()
    chats = db.query(Chat).all()
    db.close()
    return chats

def get_or_create_support_chat(buyer_id: int) -> int:
    """Get or create support chat for buyer and return its id"""
    db = SessionLocal()
    chat = db.query(SupportChat).filter(
        SupportChat.buyer_id == buyer_id,
        SupportChat.active == True
    ).first()
    if not chat:
        chat = SupportChat(buyer_id=buyer_id, active=True)
        db.add(chat)
        db.commit()
        db.refresh(chat)
    chat_id = chat.id
    db.close()
    return chat_id

def get_support_chat(chat_id: int) -> Optional[SupportChat]:
    """Get support chat by ID"""
    db = SessionLocal()
    chat = db.query(SupportChat).filter(SupportChat.id == chat_id).first()
    db.close()
    return chat

def get_support_chats_for_buyer(buyer_id: int) -> List[SupportChat]:
    """Get support chats for buyer"""
    db = SessionLocal()
    chats = db.query(SupportChat).filter(SupportChat.buyer_id == buyer_id).all()
    db.close()
    return chats

def get_all_support_chats() -> List[SupportChat]:
    """Get all support chats (admin view)"""
    db = SessionLocal()
    chats = db.query(SupportChat).all()
    db.close()
    return chats

def save_support_message(chat_id: int, sender_id: int, sender_type: str, message: str) -> SupportMessage:
    """Save support chat message"""
    db = SessionLocal()
    msg = SupportMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        sender_type=sender_type,
        message=message
    )
    db.add(msg)
    db.commit()
    db.close()
    return msg

def get_support_messages(chat_id: int, limit: int = 50) -> List[SupportMessage]:
    """Get messages from support chat"""
    db = SessionLocal()
    messages = db.query(SupportMessage).filter(
        SupportMessage.chat_id == chat_id
    ).order_by(SupportMessage.created_at.desc()).limit(limit).all()
    db.close()
    return list(reversed(messages))

def get_all_suppliers() -> List[Supplier]:
    """Get all suppliers"""
    db = SessionLocal()
    suppliers = db.query(Supplier).all()
    db.close()
    return suppliers

def get_unverified_suppliers() -> List[Supplier]:
    """Get pending suppliers (not yet verified or rejected)"""
    db = SessionLocal()
    suppliers = db.query(Supplier).filter(Supplier.status == "pending").all()
    db.close()
    return suppliers

def get_verified_suppliers() -> List[Supplier]:
    """Get verified suppliers"""
    db = SessionLocal()
    suppliers = db.query(Supplier).filter(
        Supplier.status == "verified",
        Supplier.is_banned == False
    ).all()
    db.close()
    return suppliers

def verify_supplier(supplier_id: int):
    """Verify a supplier - set status to verified"""
    db = SessionLocal()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier:
        supplier.status = "verified"
        supplier.is_banned = False
        db.commit()
    db.close()

def reject_supplier(supplier_id: int):
    """Reject and ban a supplier"""
    db = SessionLocal()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier:
        supplier.status = "rejected"
        supplier.is_banned = True
        db.commit()
    db.close()

def ban_supplier(supplier_id: int):
    """Ban a supplier"""
    db = SessionLocal()
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier:
        supplier.is_banned = True
        db.commit()
    db.close()

def block_user(telegram_id: int, user_type: str):
    """Block a user (buyer or supplier)"""
    db = SessionLocal()
    if user_type == "buyer":
        user = db.query(Buyer).filter(Buyer.telegram_id == telegram_id).first()
    else:
        user = db.query(Supplier).filter(Supplier.telegram_id == telegram_id).first()
    
    if user:
        user.active = False
        db.commit()
    db.close()

def unblock_user(telegram_id: int, user_type: str):
    """Unblock a user (buyer or supplier)"""
    db = SessionLocal()
    if user_type == "buyer":
        user = db.query(Buyer).filter(Buyer.telegram_id == telegram_id).first()
    else:
        user = db.query(Supplier).filter(Supplier.telegram_id == telegram_id).first()
    
    if user:
        user.active = True
        db.commit()
    db.close()

def get_system_stats():
    """Get system statistics"""
    db = SessionLocal()
    stats = {
        "total_buyers": db.query(Buyer).count(),
        "total_suppliers": db.query(Supplier).count(),
        "active_chats": db.query(Chat).filter(Chat.active == True).count(),
        "total_products": db.query(Product).count(),
        "total_messages": db.query(ChatMessage).count(),
    }
    db.close()
    return stats
# =========== ADMIN MANAGEMENT FUNCTIONS ===========

def get_superadmin() -> Optional[AdminUser]:
    """Get the superadmin user (only 1 allowed)"""
    db = SessionLocal()
    superadmin = db.query(AdminUser).filter(AdminUser.is_superadmin == True).first()
    db.close()
    return superadmin

def is_superadmin(telegram_id: int) -> bool:
    """Check if user is superadmin"""
    db = SessionLocal()
    admin = db.query(AdminUser).filter(
        and_(AdminUser.telegram_id == telegram_id, AdminUser.is_superadmin == True)
    ).first()
    db.close()
    return admin is not None

def is_admin(telegram_id: int) -> bool:
    """Check if user is admin (superadmin or regular admin)"""
    db = SessionLocal()
    admin = db.query(AdminUser).filter(
        and_(AdminUser.telegram_id == telegram_id, AdminUser.is_active == True)
    ).first()
    db.close()
    return admin is not None

def make_superadmin(telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> AdminUser:
    """Make user the superadmin (first user becomes superadmin)"""
    db = SessionLocal()
    
    # Check if superadmin already exists
    existing_superadmin = db.query(AdminUser).filter(AdminUser.is_superadmin == True).first()
    if existing_superadmin:
        db.close()
        return existing_superadmin
    
    # Create superadmin
    admin = AdminUser(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        is_superadmin=True,
        is_active=True,
        added_by_telegram_id=None  # Superadmin is not added by anyone
    )
    db.add(admin)
    db.commit()
    db.close()
    return admin

def add_admin(telegram_id: int, added_by_telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> Optional[AdminUser]:
    """Add new admin (superadmin only)"""
    db = SessionLocal()
    
    # Check if user is superadmin
    superadmin = db.query(AdminUser).filter(
        and_(AdminUser.telegram_id == added_by_telegram_id, AdminUser.is_superadmin == True)
    ).first()
    
    if not superadmin:
        db.close()
        return None  # Only superadmin can add admins
    
    # Check if already admin
    existing_admin = db.query(AdminUser).filter(AdminUser.telegram_id == telegram_id).first()
    if existing_admin:
        db.close()
        return existing_admin
    
    # Create new admin
    admin = AdminUser(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        is_superadmin=False,
        is_active=True,
        added_by_telegram_id=added_by_telegram_id
    )
    db.add(admin)
    db.commit()
    db.close()
    return admin

def remove_admin(telegram_id: int, removed_by_telegram_id: int) -> bool:
    """Remove admin (superadmin only, cannot remove themselves)"""
    db = SessionLocal()
    
    # Check if user is superadmin
    superadmin = db.query(AdminUser).filter(
        and_(AdminUser.telegram_id == removed_by_telegram_id, AdminUser.is_superadmin == True)
    ).first()
    
    if not superadmin:
        db.close()
        return False
    
    # Cannot remove superadmin
    if telegram_id == removed_by_telegram_id:
        db.close()
        return False
    
    # Find and deactivate admin
    admin = db.query(AdminUser).filter(AdminUser.telegram_id == telegram_id).first()
    if admin and not admin.is_superadmin:  # Cannot remove superadmin
        admin.is_active = False
        db.commit()
        db.close()
        return True
    
    db.close()
    return False

def get_all_admins() -> List[AdminUser]:
    """Get all active admins"""
    db = SessionLocal()
    admins = db.query(AdminUser).filter(AdminUser.is_active == True).all()
    db.close()
    return admins

def get_admin(telegram_id: int) -> Optional[AdminUser]:
    """Get admin by telegram_id"""
    db = SessionLocal()
    admin = db.query(AdminUser).filter(AdminUser.telegram_id == telegram_id).first()
    db.close()
    return admin