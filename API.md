# DotGPT Bot - API Reference Guide

## Database Helpers API

### User Management Functions

#### `get_or_create_buyer(telegram_id, username, first_name, last_name)`
Create or retrieve a buyer account.

**Parameters:**
- `telegram_id` (int): Unique Telegram user ID
- `username` (str, optional): Telegram username
- `first_name` (str, optional): User's first name
- `last_name` (str, optional): User's last name

**Returns:** `Buyer` object

**Example:**
```python
buyer = get_or_create_buyer(123456789, "johndoe", "John", "Doe")
```

---

#### `get_or_create_supplier(telegram_id, company_name, username)`
Create or retrieve a supplier account.

**Parameters:**
- `telegram_id` (int): Unique Telegram user ID
- `company_name` (str): Company/business name
- `username` (str, optional): Telegram username

**Returns:** `Supplier` object

**Example:**
```python
supplier = get_or_create_supplier(987654321, "TechWorld Solutions", "techworld")
```

---

#### `get_supplier(telegram_id)`
Retrieve supplier by Telegram ID.

**Parameters:**
- `telegram_id` (int): Telegram user ID

**Returns:** `Supplier` object or `None`

**Example:**
```python
supplier = get_supplier(987654321)
if supplier and supplier.verified:
    # Process verified supplier
    pass
```

---

#### `get_buyer(telegram_id)`
Retrieve buyer by Telegram ID.

**Parameters:**
- `telegram_id` (int): Telegram user ID

**Returns:** `Buyer` object or `None`

**Example:**
```python
buyer = get_buyer(123456789)
if buyer and buyer.active:
    # Process active buyer
    pass
```

---

### Product Functions

#### `get_all_active_products()`
Get all active products in the system.

**Returns:** List of `Product` objects

**Example:**
```python
products = get_all_active_products()
for product in products:
    print(f"{product.name}: {product.description}")
```

---

#### `get_products_by_supplier(supplier_id)`
Get all products offered by a supplier.

**Parameters:**
- `supplier_id` (int): Database supplier ID

**Returns:** List of `Product` objects

**Example:**
```python
supplier = get_supplier(123456789)
products = get_products_by_supplier(supplier.id)
```

---

#### `get_product_price(product_id, supplier_id)`
Get pricing info for a product from a supplier.

**Parameters:**
- `product_id` (int): Product database ID
- `supplier_id` (int): Supplier database ID

**Returns:** `ProductPrice` object or `None`

**Example:**
```python
price_info = get_product_price(1, 1)
print(f"Price: {price_info.price} {price_info.currency}")
print(f"Stock: {price_info.stock} units")
```

---

#### `get_supplier_payment_methods(supplier_id)`
Get all payment methods offered by a supplier.

**Parameters:**
- `supplier_id` (int): Supplier database ID

**Returns:** List of `SupplierPaymentMethod` objects

**Example:**
```python
methods = get_supplier_payment_methods(supplier_id)
for method in methods:
    print(f"Accept: {method.method_name}")
```

---

### Chat Functions

#### `get_or_create_chat(buyer_id, supplier_id, product_id)`
Create or retrieve a chat between buyer and supplier.

**Parameters:**
- `buyer_id` (int): Buyer database ID
- `supplier_id` (int): Supplier database ID
- `product_id` (int, optional): Related product ID

**Returns:** `Chat` object

**Example:**
```python
chat = get_or_create_chat(buyer.id, supplier.id, product_id=1)
print(f"Chat #{chat.id} created")
```

---

#### `get_chat(chat_id)`
Retrieve a chat by ID.

**Parameters:**
- `chat_id` (int): Chat database ID

**Returns:** `Chat` object or `None`

**Example:**
```python
chat = get_chat(15)
if chat and chat.active:
    messages = get_chat_messages(chat.id)
```

---

#### `get_buyer_chats(buyer_id)`
Get all chats for a buyer.

**Parameters:**
- `buyer_id` (int): Buyer database ID

**Returns:** List of `Chat` objects

**Example:**
```python
chats = get_buyer_chats(buyer.id)
print(f"Total conversations: {len(chats)}")
```

---

#### `get_supplier_chats(supplier_id)`
Get all chats for a supplier.

**Parameters:**
- `supplier_id` (int): Supplier database ID

**Returns:** List of `Chat` objects

**Example:**
```python
supplier_chats = get_supplier_chats(supplier.id)
for chat in supplier_chats:
    print(f"Chat with buyer #{chat.buyer_id}")
```

---

#### `save_chat_message(chat_id, sender_id, sender_type, message)`
Save a message in a chat.

**Parameters:**
- `chat_id` (int): Chat database ID
- `sender_id` (int): Telegram user ID of sender
- `sender_type` (str): "buyer" or "supplier"
- `message` (str): Message text

**Returns:** `ChatMessage` object

**Example:**
```python
msg = save_chat_message(
    chat_id=15,
    sender_id=123456789,
    sender_type="buyer",
    message="Hi, is this product in stock?"
)
```

---

#### `get_chat_messages(chat_id, limit)`
Get messages from a chat.

**Parameters:**
- `chat_id` (int): Chat database ID
- `limit` (int, optional): Max messages to retrieve (default: 50)

**Returns:** List of `ChatMessage` objects

**Example:**
```python
messages = get_chat_messages(chat_id=15, limit=20)
for msg in messages:
    sender = "Buyer" if msg.sender_type == "buyer" else "Supplier"
    print(f"{sender}: {msg.message}")
```

---

#### `get_all_chats()`
Get all chats in the system (admin only).

**Returns:** List of `Chat` objects

**Example:**
```python
all_chats = get_all_chats()
print(f"Total conversations: {len(all_chats)}")
```

---

### Admin Functions

#### `get_all_suppliers()`
Get all suppliers in the system.

**Returns:** List of `Supplier` objects

**Example:**
```python
suppliers = get_all_suppliers()
verified_count = sum(1 for s in suppliers if s.verified)
```

---

#### `get_unverified_suppliers()`
Get suppliers pending verification.

**Returns:** List of unverified `Supplier` objects

**Example:**
```python
pending = get_unverified_suppliers()
for supplier in pending:
    print(f"Review: {supplier.company_name}")
```

---

#### `verify_supplier(supplier_id)`
Mark a supplier as verified.

**Parameters:**
- `supplier_id` (int): Supplier database ID

**Returns:** None

**Example:**
```python
verify_supplier(supplier_id=5)
print("Supplier verified!")
```

---

#### `block_user(telegram_id, user_type)`
Block a user (buyer or supplier).

**Parameters:**
- `telegram_id` (int): Telegram user ID
- `user_type` (str): "buyer" or "supplier"

**Returns:** None

**Example:**
```python
block_user(telegram_id=123456789, user_type="buyer")
```

---

#### `unblock_user(telegram_id, user_type)`
Unblock a previously blocked user.

**Parameters:**
- `telegram_id` (int): Telegram user ID
- `user_type` (str): "buyer" or "supplier"

**Returns:** None

**Example:**
```python
unblock_user(telegram_id=123456789, user_type="buyer")
```

---

#### `get_system_stats()`
Get system-wide statistics.

**Returns:** Dictionary with stats:
```python
{
    "total_buyers": int,
    "total_suppliers": int,
    "active_chats": int,
    "total_products": int,
    "total_messages": int
}
```

**Example:**
```python
stats = get_system_stats()
print(f"""
System Status:
- Buyers: {stats['total_buyers']}
- Suppliers: {stats['total_suppliers']}
- Active Chats: {stats['active_chats']}
- Products: {stats['total_products']}
- Messages: {stats['total_messages']}
""")
```

---

## Utility Functions (utils.py)

### Formatting Functions

#### `format_price(price, currency)`
Format price with currency symbol.

**Parameters:**
- `price` (float): Price amount
- `currency` (str): Currency code (default: "USD")

**Returns:** Formatted string

**Example:**
```python
formatted = format_price(99.99, "USD")
# Returns: "$99.99 USD"
```

---

#### `format_datetime(dt)`
Format datetime to readable string.

**Parameters:**
- `dt` (datetime): Datetime object

**Returns:** Formatted string (YYYY-MM-DD HH:MM)

**Example:**
```python
formatted = format_datetime(datetime.utcnow())
# Returns: "2024-02-15 14:30"
```

---

#### `truncate_text(text, max_length, suffix)`
Truncate text to maximum length.

**Parameters:**
- `text` (str): Text to truncate
- `max_length` (int): Maximum length (default: 100)
- `suffix` (str): Suffix when truncated (default: "...")

**Returns:** Truncated string

**Example:**
```python
short = truncate_text("This is a very long product description...", max_length=50)
```

---

### Pagination Functions

#### `paginate_items(items, page, items_per_page)`
Paginate a list of items.

**Parameters:**
- `items` (list): Items to paginate
- `page` (int): Page number (0-indexed)
- `items_per_page` (int): Items per page (default: 5)

**Returns:** Tuple of (items_for_page, total_pages, current_page)

**Example:**
```python
products = get_all_active_products()
page_items, total, current = paginate_items(products, page=0, items_per_page=5)
print(f"Showing items on page {current + 1} of {total}")
```

---

## Localization API

#### `get_string(key, language)`
Get localized string for a key.

**Parameters:**
- `key` (str): String key identifier
- `language` (str): Language code (default: "en")

**Returns:** Translated string

**Example:**
```python
from strings import get_string

welcome = get_string("welcome", "es")  # Spanish
message = get_string("browse_products", "fr")  # French
```

---

## Configuration Constants (config.py)

### Bot Settings
```python
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [123456789, 987654321, ...]
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dotgpt_bot.db")
```

### Languages
```python
SUPPORTED_LANGUAGES = ["en", "es", "fr", "de", "it", "pt"]
DEFAULT_LANGUAGE = "en"
```

### Constants
```python
ITEMS_PER_PAGE = 5
PAYMENT_METHODS = ["Credit Card", "Bank Transfer", "PayPal", "Cryptocurrency", "Cash on Delivery"]
```

---

## Database Models Quick Reference

### Product
- `id`, `name`, `description`, `category`, `image_url`
- `created_at`, `updated_at`, `active`

### Supplier
- `id`, `telegram_id`, `username`, `company_name`, `description`
- `created_at`, `verified`, `active`, `language`

### Buyer
- `id`, `telegram_id`, `username`, `first_name`, `last_name`
- `created_at`, `active`, `language`

### Chat
- `id`, `buyer_id`, `supplier_id`, `product_id`
- `created_at`, `updated_at`, `active`

### ChatMessage
- `id`, `chat_id`, `sender_id`, `sender_type`, `message`
- `created_at`, `read`

### ProductPrice
- `id`, `product_id`, `supplier_id`, `price`, `currency`, `stock`
- `created_at`, `updated_at`

### SupplierPaymentMethod
- `id`, `supplier_id`, `method_name`, `details`, `created_at`

---

## Error Handling

All database functions handle errors gracefully:

```python
try:
    buyer = get_buyer(telegram_id)
    if buyer is None:
        # Create new buyer
        buyer = get_or_create_buyer(telegram_id, username)
except Exception as e:
    logger.error(f"Database error: {e}")
    # Handle error appropriately
```

---

## Best Practices

1. **Always close database sessions**: Functions close sessions automatically
2. **Use helper functions**: Don't query DB directly in handlers
3. **Cache frequently accessed data**: Consider caching suppliers/products
4. **Validate inputs**: Sanitize all user inputs
5. **Log operations**: Use logging for debugging

---

**For more information, see DEVELOPER.md**
