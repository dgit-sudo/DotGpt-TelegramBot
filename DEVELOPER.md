# DotGPT Shop Bot - Developer Documentation

## 🏗️ Project Architecture

```
┌─────────────────────────────────────────────────────┐
│          Telegram Bot API (python-telegram-bot)     │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────────┐
│                   Main Bot (main.py)                │
│  - Handler setup and initialization                 │
│  - Event routing and dispatching                    │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼──────┐  ┌───▼──────┐  ┌───▼──────┐
│ Handlers │  │ Database │  │  Strings │
│          │  │  Models  │  │ & Config │
└──────────┘  └──────────┘  └──────────┘
    │              │
    │              ▼
    │         ┌──────────────┐
    │         │  SQLAlchemy  │
    │         │   ORM Lib    │
    │         └──────────────┘
    │              │
    └──────────────┼──────────────┐
                   │              │
            ┌──────▼──────┐  ┌────▼──────┐
            │  SQLite DB  │  │PostgreSQL │
            │  (Default)  │  │(Production)
            └─────────────┘  └───────────┘
```

## 📁 File Structure & Responsibilities

### Core Files

| File | Purpose |
|------|---------|
| `main.py` | Bot initialization and handler registry |
| `config.py` | Configuration constants and enums |
| `database.py` | SQLAlchemy ORM models and DB setup |
| `database_helpers.py` | Database query helper functions |
| `strings.py` | Multi-language string management |
| `utils.py` | Utility functions and formatters |

### Handler Files

| File | Purpose |
|------|---------|
| `handlers/start.py` | `/start` command handler |
| `handlers/language_selection.py` | Language selection logic |
| `handlers/buyer_handlers.py` | Buyer interface and commands |
| `handlers/supplier_handlers.py` | Supplier panel and management |
| `handlers/admin_handlers.py` | Admin features and controls |
| `handlers/chat_handlers.py` | Chat system and messaging |

## 🔄 Data Flow

### User Interaction Flow

```
User sends message/clicks button
    ↓
Telegram sends update to bot
    ↓
Main.py routes to appropriate handler
    ↓
Handler processes request
    ↓
Query/update database if needed
    ↓
Format response message
    ↓
Send reply with keyboard markup
    ↓
Update user state in context_data
```

### Database Model Relationships

```
Buyer (1) ──────┬──────── (Many) Chat (Many) ──────┬──────── (1) Supplier
               Many                                One

Product (1) ──────┬──────── (Many) ProductPrice (Many) ──────┬──────── (1) Supplier
               Many                                      Many

Supplier (1) ────────────── (Many) SupplierPaymentMethod (1) Supplier

Chat (1) ──────────── (Many) ChatMessage
```

## 📝 Database Models

### Product Model
```python
class Product:
    id: int (PRIMARY KEY)
    name: str
    description: text
    category: str
    image_url: str
    created_at: datetime
    updated_at: datetime
    active: bool (default=True)
```

### Supplier Model
```python
class Supplier:
    id: int (PRIMARY KEY)
    telegram_id: int (UNIQUE)
    username: str
    company_name: str
    description: text
    created_at: datetime
    verified: bool (default=False)
    active: bool (default=True)
    language: str (default='en')
```

### Buyer Model
```python
class Buyer:
    id: int (PRIMARY KEY)
    telegram_id: int (UNIQUE)
    username: str
    first_name: str
    last_name: str
    created_at: datetime
    active: bool (default=True)
    language: str (default='en')
```

### Chat Model
```python
class Chat:
    id: int (PRIMARY KEY)
    buyer_id: int (FOREIGN KEY)
    supplier_id: int (FOREIGN KEY)
    product_id: int (FOREIGN KEY, nullable)
    created_at: datetime
    updated_at: datetime
    active: bool (default=True)
```

### ChatMessage Model
```python
class ChatMessage:
    id: int (PRIMARY KEY)
    chat_id: int (FOREIGN KEY)
    sender_id: int
    sender_type: str ('buyer' or 'supplier')
    message: text
    created_at: datetime
    read: bool (default=False)
```

### ProductPrice Model
```python
class ProductPrice:
    id: int (PRIMARY KEY)
    product_id: int (FOREIGN KEY)
    supplier_id: int (FOREIGN KEY)
    price: float
    currency: str (default='USD')
    stock: int (default=0)
    created_at: datetime
    updated_at: datetime
```

### SupplierPaymentMethod Model
```python
class SupplierPaymentMethod:
    id: int (PRIMARY KEY)
    supplier_id: int (FOREIGN KEY)
    method_name: str
    details: text
    created_at: datetime
```

## 🛠️ Adding New Features

### Example: Adding a Product Review System

#### 1. Create Model (database.py)
```python
class ProductReview(Base):
    __tablename__ = "product_reviews"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    buyer_id = Column(Integer, ForeignKey('buyers.id'))
    rating = Column(Integer)  # 1-5
    review_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product")
    buyer = relationship("Buyer")
```

#### 2. Create Helper Function (database_helpers.py)
```python
def save_review(product_id: int, buyer_id: int, rating: int, text: str):
    db = SessionLocal()
    review = ProductReview(
        product_id=product_id,
        buyer_id=buyer_id,
        rating=rating,
        review_text=text
    )
    db.add(review)
    db.commit()
    db.close()
    return review

def get_product_reviews(product_id: int):
    db = SessionLocal()
    reviews = db.query(ProductReview).filter(
        ProductReview.product_id == product_id
    ).all()
    db.close()
    return reviews
```

#### 3. Create Handler
```python
# handlers/review_handlers.py
async def add_review(update, context):
    # Implementation
    pass

async def view_reviews(update, context):
    # Implementation
    pass
```

#### 4. Register in main.py
```python
from handlers import review_handlers

self.app.add_handler(CallbackQueryHandler(
    review_handlers.add_review,
    pattern=r"^review_add_"
))
```

## 🌐 Localization System

### Adding New Language

1. **Add to SUPPORTED_LANGUAGES** (config.py)
```python
SUPPORTED_LANGUAGES = ["en", "es", "fr", "de", "it", "pt", "ja"]  # Add "ja"
```

2. **Add Strings Dictionary** (strings.py)
```python
"ja": {
    "welcome": "DotGPT Shop Botへようこそ 🛍️",
    "start_message": "こんにちは！DotGPT Shop Botです。何をしたいですか？",
    # ... all other strings
}
```

3. **Update Language Selection** (handlers/language_selection.py)
```python
buttons = [
    # ... existing buttons
    [InlineKeyboardButton("日本語", callback_data="lang_ja")],
]
```

## 🔌 Extension Points

### Custom Handlers
Create new handler files and register in `main.py`:
```python
from handlers import custom_handlers

self.app.add_handler(CommandHandler("custom", custom_handlers.my_command))
```

### Custom Database Queries
Add helper functions to `database_helpers.py`:
```python
def get_custom_data(filter_param):
    db = SessionLocal()
    result = db.query(SomeModel).filter(...).all()
    db.close()
    return result
```

### Custom Utilities
Add to `utils.py`:
```python
def my_utility_function(param):
    return processed_result
```

## 🧪 Testing Guidelines

### Unit Test Example
```python
import pytest
from database_helpers import get_or_create_buyer

def test_create_buyer():
    buyer = get_or_create_buyer(123456789, "testuser", "Test", "User")
    
    assert buyer.telegram_id == 123456789
    assert buyer.username == "testuser"
    assert buyer.first_name == "Test"
```

### Handler Test Example
```python
@pytest.mark.asyncio
async def test_start_command(update, context):
    from handlers import start
    
    await start.start_command(update, context)
    
    # Assert message sent
    assert update.message.reply_text.called
```

## 🔐 Security Considerations

### Database Security
```python
# Always use parameterized queries
db.query(User).filter(User.id == user_id)  # ✅ Safe

# Never concatenate strings
db.query(f"SELECT * FROM users WHERE id = {user_id}")  # ❌ Unsafe
```

### Input Validation
```python
def validate_input(user_input: str) -> bool:
    if not user_input or len(user_input) > 1000:
        return False
    return True
```

### Authorization Checks
```python
if user_id not in ADMIN_IDS:
    await query.answer("Unauthorized", show_alert=True)
    return
```

## 📊 Performance Tips

1. **Use Database Indexes**
```python
telegram_id = Column(Integer, unique=True, index=True)
```

2. **Batch Operations**
```python
# Instead of loop with individual queries
users = db.query(User).filter(...).all()  # Single query
for user in users:
    process(user)
```

3. **Connection Pooling**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

## 🚀 Deployment Optimization

### For Production:
1. Use PostgreSQL instead of SQLite
2. Enable database connection pooling
3. Implement caching layer (Redis)
4. Use webhook instead of polling
5. Monitor with logging and error tracking
6. Regular database backups

## 📚 Useful Resources

- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/20/orm/)
- [Telegram Bot API Reference](https://core.telegram.org/bots/api)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/MyFeature`
3. Make changes with tests
4. Push to branch: `git push origin feature/MyFeature`
5. Submit pull request

---

Ready to extend? Start by creating your handler, add models, register in main.py!
