from database import SessionLocal, Product, Supplier, Buyer, Chat, ChatMessage, ProductPrice, SupplierPaymentMethod, AdminUser, SupportChat, SupportMessage, PaymentDetails, Sale, SaleProof, DeletedMessage, UserReferral
from typing import List, Optional
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import datetime


def _referral_code_for_user(telegram_id: int) -> str:
    return f"ref_{telegram_id}"

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
        buyer = db.query(Buyer).filter(Buyer.telegram_id == telegram_id).first()
        terms_accepted = buyer.terms_accepted if buyer else False
        terms_accepted_at = buyer.terms_accepted_at if buyer else None
        supplier = Supplier(
            telegram_id=telegram_id,
            company_name=company_name,
            username=username,
            terms_accepted=terms_accepted,
            terms_accepted_at=terms_accepted_at
        )
        db.add(supplier)
        db.commit()
    db.close()
    return supplier

def has_accepted_terms(telegram_id: int) -> bool:
    """Check if user has accepted terms (buyer record)"""
    db = SessionLocal()
    buyer = db.query(Buyer).filter(Buyer.telegram_id == telegram_id).first()
    accepted = bool(buyer and buyer.terms_accepted)
    db.close()
    return accepted

def set_terms_accepted(telegram_id: int) -> None:
    """Mark terms as accepted for buyer and supplier records"""
    db = SessionLocal()
    buyer = db.query(Buyer).filter(Buyer.telegram_id == telegram_id).first()
    if buyer:
        buyer.terms_accepted = True
        buyer.terms_accepted_at = datetime.utcnow()

    supplier = db.query(Supplier).filter(Supplier.telegram_id == telegram_id).first()
    if supplier:
        supplier.terms_accepted = True
        supplier.terms_accepted_at = datetime.utcnow()

    db.commit()
    db.close()

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

def get_buyer_by_id(buyer_id: int) -> Optional[Buyer]:
    """Get buyer by internal ID"""
    db = SessionLocal()
    buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()
    db.close()
    return buyer


def get_or_create_referral_profile(telegram_id: int) -> UserReferral:
    """Ensure every user has a referral profile/code"""
    db = SessionLocal()
    profile = db.query(UserReferral).filter(UserReferral.telegram_id == telegram_id).first()

    if not profile:
        profile = UserReferral(
            telegram_id=telegram_id,
            referral_code=_referral_code_for_user(telegram_id),
            referred_by_telegram_id=None,
            referrals_count=0,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    db.close()
    return profile


def register_referral_join(joined_telegram_id: int, referrer_telegram_id: Optional[int]) -> bool:
    """Count referral only on first join (/start first-time profile creation)."""
    if not referrer_telegram_id or joined_telegram_id == referrer_telegram_id:
        get_or_create_referral_profile(joined_telegram_id)
        return False

    db = SessionLocal()

    joined_profile = db.query(UserReferral).filter(UserReferral.telegram_id == joined_telegram_id).first()
    if joined_profile:
        db.close()
        return False

    referrer_profile = db.query(UserReferral).filter(UserReferral.telegram_id == referrer_telegram_id).first()
    if not referrer_profile:
        existing_referrer = (
            db.query(Buyer).filter(Buyer.telegram_id == referrer_telegram_id).first()
            or db.query(Supplier).filter(Supplier.telegram_id == referrer_telegram_id).first()
            or db.query(AdminUser).filter(AdminUser.telegram_id == referrer_telegram_id).first()
        )
        if not existing_referrer:
            db.close()
            get_or_create_referral_profile(joined_telegram_id)
            return False

        referrer_profile = UserReferral(
            telegram_id=referrer_telegram_id,
            referral_code=_referral_code_for_user(referrer_telegram_id),
            referred_by_telegram_id=None,
            referrals_count=0,
        )
        db.add(referrer_profile)
        db.flush()

    joined_profile = UserReferral(
        telegram_id=joined_telegram_id,
        referral_code=_referral_code_for_user(joined_telegram_id),
        referred_by_telegram_id=referrer_telegram_id,
        referrals_count=0,
    )
    db.add(joined_profile)
    referrer_profile.referrals_count += 1

    db.commit()
    db.close()
    return True


def get_referral_leaderboard(limit: int = 20) -> List[dict]:
    """Referral leaderboard with inferred user type"""
    db = SessionLocal()
    rows = db.query(UserReferral).order_by(UserReferral.referrals_count.desc(), UserReferral.telegram_id.asc()).limit(limit).all()

    leaderboard = []
    for row in rows:
        admin = db.query(AdminUser).filter(
            and_(AdminUser.telegram_id == row.telegram_id, AdminUser.is_active == True)
        ).first()
        supplier = db.query(Supplier).filter(Supplier.telegram_id == row.telegram_id).first()
        buyer = db.query(Buyer).filter(Buyer.telegram_id == row.telegram_id).first()

        if admin and admin.is_superadmin:
            user_type = "superadmin"
        elif admin:
            user_type = "admin"
        elif supplier and supplier.status == "verified":
            user_type = "seller"
        elif supplier:
            user_type = "supplier"
        elif buyer:
            user_type = "buyer"
        else:
            user_type = "user"

        username = None
        if admin and admin.username:
            username = admin.username
        elif supplier and supplier.username:
            username = supplier.username
        elif buyer and buyer.username:
            username = buyer.username

        leaderboard.append({
            "telegram_id": row.telegram_id,
            "username": username,
            "user_type": user_type,
            "referrals_count": row.referrals_count,
            "referral_code": row.referral_code,
        })

    db.close()
    return leaderboard

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

def get_active_product_with_prices(product_id: int) -> Optional[Product]:
    """Get one active product with prices and suppliers eagerly loaded"""
    db = SessionLocal()
    product = (
        db.query(Product)
        .options(
            selectinload(Product.prices).selectinload(ProductPrice.supplier)
        )
        .filter(
            Product.id == product_id,
            Product.active == True
        )
        .first()
    )
    db.close()
    return product

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
    else:
        if not chat.active:
            chat.active = True
        if product_id and not chat.product_id:
            chat.product_id = product_id
        db.commit()
    db.refresh(chat)
    db.close()
    return chat

def get_chat(chat_id: int) -> Optional[Chat]:
    """Get chat by ID"""
    db = SessionLocal()
    chat = db.query(Chat).options(
        selectinload(Chat.buyer),
        selectinload(Chat.supplier),
        selectinload(Chat.messages),
    ).filter(Chat.id == chat_id).first()
    db.close()
    return chat

def end_chat(chat_id: int, supplier_id: int) -> bool:
    """End chat (supplier only for their own chat)."""
    db = SessionLocal()
    chat = db.query(Chat).filter(
        and_(Chat.id == chat_id, Chat.supplier_id == supplier_id)
    ).first()
    if not chat:
        db.close()
        return False

    chat.active = False
    db.commit()
    db.close()
    return True

def get_buyer_chats(buyer_id: int) -> List[Chat]:
    """Get all active chats for a buyer"""
    db = SessionLocal()
    chats = db.query(Chat).filter(
        Chat.buyer_id == buyer_id,
        Chat.active == True
    ).all()
    db.close()
    return chats

def get_supplier_chats(supplier_id: int) -> List[Chat]:
    """Get all active chats for a supplier"""
    db = SessionLocal()
    chats = db.query(Chat).filter(
        Chat.supplier_id == supplier_id,
        Chat.active == True
    ).all()
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
    """Get all active chats (for admin dashboards)"""
    db = SessionLocal()
    chats = db.query(Chat).filter(Chat.active == True).all()
    db.close()
    return chats

def get_historical_chats() -> List[Chat]:
    """Get historical chats: ended chats and chats with sale records"""
    db = SessionLocal()

    ended_chat_ids = {
        row[0]
        for row in db.query(Chat.id).filter(Chat.active == False).all()
    }
    sale_chat_ids = {
        row[0]
        for row in db.query(Sale.chat_id).distinct().all()
        if row[0] is not None
    }

    historical_ids = ended_chat_ids.union(sale_chat_ids)
    if not historical_ids:
        db.close()
        return []

    chats = db.query(Chat).filter(Chat.id.in_(historical_ids)).order_by(Chat.updated_at.desc()).all()
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

def end_support_chat(chat_id: int) -> bool:
    """End a support chat"""
    db = SessionLocal()
    chat = db.query(SupportChat).filter(SupportChat.id == chat_id).first()
    if not chat:
        db.close()
        return False

    chat.active = False
    db.commit()
    db.close()
    return True

def get_support_chats_for_buyer(buyer_id: int) -> List[SupportChat]:
    """Get active support chats for buyer"""
    db = SessionLocal()
    chats = db.query(SupportChat).filter(
        SupportChat.buyer_id == buyer_id,
        SupportChat.active == True
    ).all()
    db.close()
    return chats

def get_historical_support_chats_for_buyer(buyer_id: int) -> List[SupportChat]:
    """Get ended support chats for buyer"""
    db = SessionLocal()
    chats = db.query(SupportChat).filter(
        SupportChat.buyer_id == buyer_id,
        SupportChat.active == False
    ).all()
    db.close()
    return chats

def get_all_support_chats() -> List[SupportChat]:
    """Get all active support chats (admin view)"""
    db = SessionLocal()
    chats = db.query(SupportChat).filter(SupportChat.active == True).all()
    db.close()
    return chats

def get_all_historical_support_chats() -> List[SupportChat]:
    """Get all ended support chats (admin view)"""
    db = SessionLocal()
    chats = db.query(SupportChat).filter(SupportChat.active == False).all()
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

def get_system_stats_usernames(limit: int = 10) -> dict:
    """Get buyer/seller username lists for admin stats"""
    db = SessionLocal()
    buyers = db.query(Buyer).order_by(Buyer.created_at.desc()).limit(limit).all()
    suppliers = db.query(Supplier).order_by(Supplier.created_at.desc()).limit(limit).all()
    db.close()
    return {
        "buyers": buyers,
        "suppliers": suppliers,
    }

def get_sales_leaderboard(limit: int = 5) -> dict:
    """Get top sellers and buyers by approved sales count"""
    db = SessionLocal()

    top_sellers_rows = (
        db.query(Sale.supplier_id, func.count(Sale.id).label("sales_count"))
        .filter(Sale.status == "approved")
        .group_by(Sale.supplier_id)
        .order_by(func.count(Sale.id).desc())
        .limit(limit)
        .all()
    )

    top_buyers_rows = (
        db.query(Sale.buyer_id, func.count(Sale.id).label("sales_count"))
        .filter(Sale.status == "approved")
        .group_by(Sale.buyer_id)
        .order_by(func.count(Sale.id).desc())
        .limit(limit)
        .all()
    )

    top_sellers = []
    for supplier_id, sales_count in top_sellers_rows:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if supplier:
            top_sellers.append({"supplier": supplier, "sales_count": sales_count})

    top_buyers = []
    for buyer_id, sales_count in top_buyers_rows:
        buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()
        if buyer:
            top_buyers.append({"buyer": buyer, "sales_count": sales_count})

    db.close()
    return {
        "top_sellers": top_sellers,
        "top_buyers": top_buyers,
    }

def search_user_by_telegram_id(telegram_id: int) -> dict:
    """Search buyer/seller by telegram id for admin moderation"""
    db = SessionLocal()
    buyer = db.query(Buyer).filter(Buyer.telegram_id == telegram_id).first()
    supplier = db.query(Supplier).filter(Supplier.telegram_id == telegram_id).first()
    admin = db.query(AdminUser).filter(AdminUser.telegram_id == telegram_id).first()
    db.close()
    return {
        "buyer": buyer,
        "supplier": supplier,
        "admin": admin,
    }
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

def get_supplier_statistics(supplier_id: int) -> dict:
    """Get supplier statistics including product count and stock info"""
    db = SessionLocal()
    
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        db.close()
        return None
    
    products = supplier.products
    product_count = len(products)
    
    total_stock = 0
    low_stock_items = []  # Products with stock <= 5
    out_of_stock_items = []  # Products with stock == 0
    not_tracked_items = []  # Products with stock < 0
    
    for product in products:
        # Get the ProductPrice record for this supplier-product pair
        price_record = db.query(ProductPrice).filter(
            and_(ProductPrice.product_id == product.id, ProductPrice.supplier_id == supplier_id)
        ).first()
        
        if price_record:
            stock = price_record.stock
            
            if stock < 0:
                not_tracked_items.append(product.name)
            elif stock == 0:
                out_of_stock_items.append(product.name)
            elif stock <= 5:
                low_stock_items.append((product.name, stock))
            else:
                total_stock += stock
    
    db.close()
    
    return {
        'product_count': product_count,
        'total_stock': total_stock,
        'low_stock_items': low_stock_items,  # List of (product_name, stock) tuples
        'out_of_stock_items': out_of_stock_items,
        'not_tracked_items': not_tracked_items,
        'supplier_id': supplier_id
    }

def log_restock_alert(supplier_id: int, product_name: str, message: str) -> bool:
    """Log a restock alert (can be used to track which products need restocking)"""
    # This is a placeholder for storing alert notifications
    # In production, this would save to a database table or send email to admins
    # For now, just return True
    return True

# ============================================================================
# PAYMENT DETAILS HELPERS
# ============================================================================

def get_payment_details() -> List[PaymentDetails]:
    """Get all active payment details"""
    db = SessionLocal()
    details = db.query(PaymentDetails).filter(PaymentDetails.is_active == True).all()
    db.close()
    return details

def set_payment_details(payment_method: str, details: str, instructions: str = None) -> PaymentDetails:
    """Set or update payment details"""
    db = SessionLocal()
    
    # Check if this method already exists
    existing = db.query(PaymentDetails).filter(PaymentDetails.payment_method == payment_method).first()
    
    if existing:
        existing.details = details
        existing.instructions = instructions
        db.commit()
        db.refresh(existing)
        db.close()
        return existing
    
    # Create new
    payment = PaymentDetails(
        payment_method=payment_method,
        details=details,
        instructions=instructions
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    db.close()
    return payment

# ============================================================================
# SALE TRACKING & VERIFICATION HELPERS
# ============================================================================

def create_sale(chat_id: int, product_id: int, buyer_id: int, supplier_id: int, quantity: int = 1) -> Sale:
    """Create a new sale record (initially in pending status)"""
    db = SessionLocal()
    sale = Sale(
        chat_id=chat_id,
        product_id=product_id,
        buyer_id=buyer_id,
        supplier_id=supplier_id,
        quantity=quantity,
        status="pending"
    )
    db.add(sale)
    db.commit()
    db.refresh(sale)
    db.close()
    return sale

def submit_sale_proof(sale_id: int, file_id: str, file_type: str, file_name: str = None, caption: str = None) -> SaleProof:
    """Submit payment proof for a sale"""
    db = SessionLocal()
    
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    if sale:
        sale.status = "proof_submitted"
        sale.proof_submitted_at = datetime.utcnow()
    
    proof = SaleProof(
        sale_id=sale_id,
        file_id=file_id,
        file_type=file_type,
        file_name=file_name,
        caption=caption
    )
    db.add(proof)
    db.commit()
    db.refresh(proof)
    db.close()
    return proof

def get_pending_sale_proofs() -> List[Sale]:
    """Get all sales awaiting admin verification"""
    db = SessionLocal()
    sales = db.query(Sale).filter(Sale.status == "proof_submitted").all()
    db.close()
    return sales

def approve_sale(sale_id: int, admin_id: int, notes: str = None) -> bool:
    """Approve a sale (admin verified payment)"""
    db = SessionLocal()
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    
    if not sale:
        db.close()
        return False
    
    sale.status = "approved"
    sale.verified_at = datetime.utcnow()
    sale.verified_by_admin_id = admin_id
    sale.notes = notes
    db.commit()
    db.close()
    
    # Now reduce stock
    if sale.product_id and sale.supplier_id:
        from database import ProductPrice
        db = SessionLocal()
        price_record = db.query(ProductPrice).filter(
            and_(ProductPrice.product_id == sale.product_id, ProductPrice.supplier_id == sale.supplier_id)
        ).first()
        
        if price_record and price_record.stock >= 0:
            price_record.stock -= sale.quantity
            db.commit()
        
        db.close()
    
    return True

def reject_sale(sale_id: int, admin_id: int, notes: str = None) -> bool:
    """Reject a sale (admin did not verify payment)"""
    db = SessionLocal()
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    
    if not sale:
        db.close()
        return False
    
    sale.status = "rejected"
    sale.verified_at = datetime.utcnow()
    sale.verified_by_admin_id = admin_id
    sale.notes = notes
    db.commit()
    db.close()
    
    return True

def get_sale_by_id(sale_id: int) -> Optional[Sale]:
    """Get sale by ID"""
    db = SessionLocal()
    sale = db.query(Sale).filter(Sale.id == sale_id).first()
    db.close()
    return sale

# ============================================================================
# MESSAGE BACKUP HELPERS
# ============================================================================

def backup_deleted_message(chat_id: int, sender_id: int, sender_type: str, message: str, original_timestamp: datetime = None) -> DeletedMessage:
    """Create a backup of a deleted message"""
    db = SessionLocal()
    deleted_msg = DeletedMessage(
        chat_id=chat_id,
        sender_id=sender_id,
        sender_type=sender_type,
        message=message,
        original_timestamp=original_timestamp
    )
    db.add(deleted_msg)
    db.commit()
    db.refresh(deleted_msg)
    db.close()
    return deleted_msg

def get_chat_deleted_messages(chat_id: int) -> List[DeletedMessage]:
    """Get all deleted messages from a chat"""
    db = SessionLocal()
    messages = db.query(DeletedMessage).filter(DeletedMessage.chat_id == chat_id).all()
    db.close()
    return messages
