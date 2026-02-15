# DotGPT Bot - Testing Guide

## 🧪 Unit Testing Setup

### Install Testing Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov
```

### Test Structure
```
tests/
├── __init__.py
├── test_database.py          # Database tests
├── test_handlers.py          # Handler tests
├── test_strings.py           # Localization tests
└── conftest.py               # Shared test fixtures
```

## 🔍 Manual Testing Checklist

### Pre-Launch Testing

#### 1. Setup Testing
- [ ] Database initializes without errors
- [ ] Sample data creates successfully
- [ ] Bot token is valid
- [ ] Admin IDs configured correctly
- [ ] Environment variables load properly

#### 2. Start Command Testing
- [ ] `/start` displays language selection
- [ ] All 6 languages selectable
- [ ] Language persists after selection
- [ ] Main menu displays after language selection

#### 3. Buyer Features Testing

**Product Browsing**
- [ ] Browse products shows all items
- [ ] Pagination works forward and backward
- [ ] Product details display correctly
- [ ] Prices show from all suppliers
- [ ] Payment methods display correctly

**Chat System**
- [ ] Can initiate chat with supplier
- [ ] Chat message sends successfully
- [ ] Buyer profile stays hidden from supplier
- [ ] Messages appear in chat history
- [ ] Multiple chats can be created

**Settings**
- [ ] Language change works
- [ ] Preferences save correctly
- [ ] Order history displays

#### 4. Supplier Features Testing

**Registration**
- [ ] New supplier can register
- [ ] Company name is required
- [ ] Account shows as pending verification
- [ ] Cannot access supplier panel until verified

**Product Management**
- [ ] Can add products
- [ ] Can set prices
- [ ] Can set stock levels
- [ ] Can update product details
- [ ] Can delete products

**Payment Methods**
- [ ] Can add payment methods
- [ ] Multiple methods supported
- [ ] Details save correctly
- [ ] Buyers see supplier payment options

**Inquiries**
- [ ] Can see buyer inquiries
- [ ] Can respond to chats
- [ ] Cannot see buyer profile
- [ ] Chat history visible

#### 5. Admin Features Testing

**Authentication**
- [ ] Only admins can access `/admin`
- [ ] Non-admins see unauthorized message
- [ ] Admin menu displays all options

**Supplier Management**
- [ ] Can view pending suppliers
- [ ] Can verify suppliers
- [ ] Verified suppliers appear as verified to buyers

**Chat Viewing**
- [ ] Can see all chats
- [ ] Can view chat messages
- [ ] Can view participants (anonymized for buyer)

**Statistics**
- [ ] Total users counts correctly
- [ ] Total suppliers counts correctly
- [ ] Active chats count correct
- [ ] Product count accurate

**User Management**
- [ ] Can block users
- [ ] Can unblock users
- [ ] Blocked users cannot access bot

### 6. Localization Testing

Test each language:
- [ ] English (en)
- [ ] Spanish (es)
- [ ] French (fr)
- [ ] German (de)
- [ ] Italian (it)
- [ ] Portuguese (pt)

For each language:
- [ ] Menu items display correctly
- [ ] All messages translated
- [ ] Buttons show translated text
- [ ] No missing translations

### 7. Database Testing

```bash
# Test database connection
python -c "from database import SessionLocal; db = SessionLocal(); print('Connected!'); db.close()"

# Check tables created
sqlite3 dotgpt_bot.db ".tables"

# Verify data
sqlite3 dotgpt_bot.db "SELECT COUNT(*) FROM products;"
```

### 8. Error Handling Testing

- [ ] Invalid data rejected
- [ ] User errors show helpful messages
- [ ] Database errors don't crash bot
- [ ] Graceful degradation on API errors

---

## 🎯 Test Scenarios

### Scenario 1: Complete Buyer Journey
1. New user sends `/start`
2. Selects language (test all 6)
3. Chooses buyer option
4. Browses products
5. Views product details
6. Contacts supplier
7. Sends chat message
8. Receives supplier response

**Expected Result:** Chat created, messages exchanged, profile hidden

### Scenario 2: Supplier Verification Flow
1. New user sends `/start`
2. Chooses supplier option
3. Registers company
4. Admin verifies supplier
5. Supplier adds products
6. Supplier sets prices
7. Supplier adds payment methods
8. Supplier receives and replies to buyer inquiry

**Expected Result:** Full flow completed without errors

### Scenario 3: Admin Oversight
1. Admin uses `/admin`
2. Views all chats
3. Views statistics
4. Verifies pending supplier
5. Blocks problematic user
6. Unblocks user
7. Views system stats

**Expected Result:** All admin functions work correctly

### Scenario 4: Multi-Language Support
1. User selects Spanish
2. All messages display in Spanish
3. User switches to French
4. All messages display in French
5. Preference persists

**Expected Result:** Seamless language switching

---

## 🐛 Known Test Cases to Cover

### Edge Cases
- [ ] User with no username
- [ ] Very long product names
- [ ] Products with no description
- [ ] Messages with special characters
- [ ] Rapid button clicks
- [ ] Network timeouts
- [ ] Concurrent requests

### Boundary Tests
- [ ] Empty product list
- [ ] Single product in system
- [ ] Pagination edge cases
- [ ] Very long messages
- [ ] Unicode characters in all languages

---

## 📊 Performance Testing

### Load Testing
```bash
# Test with multiple concurrent users
# Would require load testing tools like:
# - Apache JMeter
# - Locust
# - pytest-benchmark
```

### Metrics to Monitor
- Response time per action: < 2 seconds
- Database query time: < 100ms
- Memory usage: < 500MB
- CPU usage: < 50%

---

## 🔐 Security Testing

- [ ] SQL injection attempts blocked
- [ ] XSS prevention working
- [ ] Unauthorized access prevented
- [ ] Admin-only features protected
- [ ] Buyer profiles hidden from suppliers
- [ ] Rate limiting (future)

---

## 📝 Sample Test Cases

### Test Case 1: Product Browsing
```python
async def test_browse_products():
    # Create test user
    user = get_or_create_buyer(123456789, "testuser")
    
    # Get products
    products = get_all_active_products()
    
    # Assert
    assert len(products) > 0
    assert all(p.active for p in products)
```

### Test Case 2: Chat Creation
```python
async def test_create_chat():
    buyer = get_or_create_buyer(111111111)
    supplier = get_or_create_supplier(222222222, "Test Supplier")
    
    chat = get_or_create_chat(buyer.id, supplier.id)
    
    assert chat is not None
    assert chat.buyer_id == buyer.id
    assert chat.supplier_id == supplier.id
```

### Test Case 3: Supplier Verification
```python
def test_verify_supplier():
    from database_helpers import verify_supplier
    
    supplier = get_or_create_supplier(333333333, "Test Co")
    assert not supplier.verified
    
    verify_supplier(supplier.id)
    
    updated = get_supplier(333333333)
    assert updated.verified
```

---

## 🚀 Continuous Integration

### GitHub Actions Workflow (Optional)
Create `.github/workflows/tests.yml`:
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov
```

---

## 📋 Regression Testing

Keep a checklist of critical flows:
- User Registration
- Product Browsing
- Chat Creation
- Supplier Verification
- Admin Panel Access
- Language Selection

Run these before any release.

---

## ✅ Pre-Release Checklist

Before deploying to production:
- [ ] All unit tests pass
- [ ] All manual test cases pass
- [ ] Performance targets met
- [ ] Security checklist reviewed
- [ ] Documentation updated
- [ ] Database migrations tested
- [ ] Error handling verified
- [ ] Localization complete
- [ ] Admin features tested
- [ ] Load testing passed

