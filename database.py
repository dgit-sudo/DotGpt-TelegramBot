from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Table, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
from config import DATABASE_URL

Base = declarative_base()

# Database engine/session setup
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Association table for products and suppliers (many-to-many with pricing)
supplier_product = Table(
    'supplier_product',
    Base.metadata,
    Column('supplier_id', Integer, ForeignKey('suppliers.id', ondelete='CASCADE')),
    Column('product_id', Integer, ForeignKey('products.id', ondelete='CASCADE')),
)

class UserRole(enum.Enum):
    """User role enumeration"""
    BUYER = "buyer"
    SUPPLIER = "supplier"
    ADMIN = "admin"

class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # Relationships
    prices = relationship("ProductPrice", back_populates="product", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", secondary=supplier_product, back_populates="products")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name})>"

class Supplier(Base):
    """Supplier model"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    company_name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")  # pending, verified, rejected
    is_banned = Column(Boolean, default=False)  # True if rejected or banned
    active = Column(Boolean, default=True)
    language = Column(String(10), default="en")
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime)
    
    # Relationships
    prices = relationship("ProductPrice", back_populates="supplier", cascade="all, delete-orphan")
    products = relationship("Product", secondary=supplier_product, back_populates="suppliers")
    chats = relationship("Chat", back_populates="supplier")
    payment_methods = relationship("SupplierPaymentMethod", back_populates="supplier", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, company_name={self.company_name}, status={self.status})>"

class Buyer(Base):
    """Buyer model"""
    __tablename__ = "buyers"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    language = Column(String(10), default="en")
    terms_accepted = Column(Boolean, default=False)
    terms_accepted_at = Column(DateTime)
    
    # Relationships
    chats = relationship("Chat", back_populates="buyer")
    
    def __repr__(self):
        return f"<Buyer(id={self.id}, telegram_id={self.telegram_id})>"

class ProductPrice(Base):
    """Product price per supplier"""
    __tablename__ = "product_prices"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    price = Column(Float, nullable=False)  # Price per unit
    currency = Column(String(10), default="USD")
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="prices")
    supplier = relationship("Supplier", back_populates="prices")
    
    def __repr__(self):
        return f"<ProductPrice(product={self.product_id}, supplier={self.supplier_id}, price={self.price})>"

class Chat(Base):
    """Chat conversation between buyer and supplier (anonymized)"""
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey('buyers.id', ondelete='CASCADE'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))  # Optional: related product
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # Relationships
    buyer = relationship("Buyer", back_populates="chats")
    supplier = relationship("Supplier", back_populates="chats")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Chat(id={self.id}, buyer={self.buyer_id}, supplier={self.supplier_id})>"

class ChatMessage(Base):
    """Individual chat message"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    sender_id = Column(Integer, nullable=False)  # buyer_id or supplier_id
    sender_type = Column(String(20), nullable=False)  # "buyer" or "supplier"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, chat={self.chat_id})>"

class SupportChat(Base):
    """Support chat between buyer and admin (anonymized)"""
    __tablename__ = "support_chats"

    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey('buyers.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)

    # Relationships
    buyer = relationship("Buyer")
    messages = relationship("SupportMessage", back_populates="chat", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SupportChat(id={self.id}, buyer={self.buyer_id})>"


class SupportMessage(Base):
    """Support chat message between buyer and admin"""
    __tablename__ = "support_messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey('support_chats.id', ondelete='CASCADE'), nullable=False)
    sender_id = Column(Integer, nullable=False)
    sender_type = Column(String(20), nullable=False)  # "buyer" or "admin"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    chat = relationship("SupportChat", back_populates="messages")

    def __repr__(self):
        return f"<SupportMessage(id={self.id}, chat={self.chat_id})>"

class SupplierPaymentMethod(Base):
    """Payment methods supported by each supplier"""
    __tablename__ = "supplier_payment_methods"
    
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    method_name = Column(String(100), nullable=False)  # e.g., "Credit Card", "Bank Transfer"
    details = Column(Text)  # Contact info, account details, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="payment_methods")
    
    def __repr__(self):
        return f"<SupplierPaymentMethod(supplier={self.supplier_id}, method={self.method_name})>"

class AdminUser(Base):
    """Admin users - tracks who is an admin and if they're superadmin"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_superadmin = Column(Boolean, default=False)  # Only 1 superadmin allowed
    is_active = Column(Boolean, default=True)
    added_date = Column(DateTime, default=datetime.utcnow)
    added_by_telegram_id = Column(Integer)  # Who added this admin (null if superadmin)
    
    def __repr__(self):
        role = "SuperAdmin" if self.is_superadmin else "Admin"
        return f"<AdminUser(id={self.telegram_id}, {role})>"


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
