# DotGPT Bot - Quick Reference Guide

## 🎯 5-Minute Quick Start

```bash
# 1. Clone
git clone https://github.com/dgit-sudo/DotGpt-TelegramBot.git
cd DotGpt-TelegramBot

# 2. Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env with BOT_TOKEN and ADMIN_IDS

# 5. Initialize database
python init_sample_data.py

# 6. Run bot
python main.py
```

---

## 📁 Project Files at a Glance

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | Bot entry point | ~70 |
| `config.py` | Settings & constants | ~40 |
| `database.py` | ORM models | ~280 |
| `database_helpers.py` | Query helpers | ~200 |
| `strings.py` | 6 languages | ~400 |
| `utils.py` | Utilities | ~100 |
| `handlers/*.py` | Bot commands | ~600 |
| **Total Code** | ~1,700 lines of production code |

---

## 🔧 Configuration Variables

Create `.env` file with:
```
BOT_TOKEN=your_token_from_botfather
ADMIN_IDS=123456789,987654321
DATABASE_URL=sqlite:///./dotgpt_bot.db
```

**Get BOT_TOKEN:** Chat @BotFather on Telegram, use `/newbot`

**Get your ID:** Chat @userinfobot on Telegram

---

## 👥 Three User Roles

### 🛍️ Buyer
- Browse products
- Compare prices
- Chat anonymously with suppliers
- Commands: `/start`, `/browse`, `/shop`

### 🏪 Supplier
- Manage products & prices
- Verify account
- Respond to inquiries
- Earn sales
- Commands: `/start`, `/supplier`

### 👨‍💼 Admin
- Verify suppliers
- Monitor all chats
- Manage users
- View statistics
- Commands: `/admin`

---

## 🗄️ Database Structure (Simple)

```
Products ←→ ProductPrice ←→ Suppliers
                                ↓
Buyers ←→ Chat ←→ ChatMessage ←→ Supplier
  ↓           ↓
 Lang      Message Type: buyer/supplier
```

**Key Tables:**
- Products (6 sample items)
- Suppliers (3 sample verified)
- Buyers (3 sample accounts)
- Chats (buyer-supplier conversations)
- ChatMessages (anonymized)
- ProductPrice (pricing per supplier)
- PaymentMethods (per supplier)

---

## 🎮 Common Commands

```bash
# Bot Commands
/start                  # Initialize, select language
/admin                  # Admin panel (admins only)
/browse                 # Browse products
/shop                   # Shopping interface
/supplier               # Supplier dashboard

# Python Commands
python init_sample_data.py    # Create sample data
python main.py                # Start bot
python -m pytest              # Run tests (if pytest installed)
```

---

## 🌍 Supported Languages

Code → Language
- `en` → English
- `es` → Español (Spanish)
- `fr` → Français (French)
- `de` → Deutsch (German)
- `it` → Italiano (Italian)
- `pt` → Português (Portuguese)

---

## 🔒 Privacy Features

✅ **What's Protected:**
- Buyer names/usernames hidden from suppliers
- No profile access for suppliers
- Anonymous chat IDs only
- Role-based access control
- Admin verification required

---

## 📊 Included Sample Data

### 6 Products
- Laptop Computer ($1299.99)
- Wireless Mouse ($45.99)
- USB-C Cable ($19.99)
- Monitor 27 inch ($599.99)
- Keyboard Mechanical ($159.99)
- Laptop Stand ($89.99)

### 3 Suppliers
- TechWorld Solutions
- Global Electronics
- Premium Hardware

### 3 Test Buyers
- johndoe (123456789)
- jane_smith (987654321)
- alex_jones (555555555)

---

## 💻 System Requirements

- Python 3.9+
- Telegram account + Bot (from @BotFather)
- 100MB disk space
- Internet connection
- Terminal/command prompt

**Optional:**
- PostgreSQL (for production)
- Docker (for containerization)
- Git (for version control)

---

## 🚀 Deployment Summary

### Local (Development)
- SQLite database
- Polling mode
- 5 minutes to setup
- Perfect for testing

### VPS/Cloud (Production)
- PostgreSQL database
- Systemd service
- 30 minutes to setup
- Scalable solution

### Docker (Flexible)
- Container-based
- Easy scaling
- Environment consistent
- 15 minutes to setup

---

## 📚 Documentation Map

```
README.md           → Installation & overview
FEATURES.md         → Complete feature list
DEPLOYMENT.md       → Production setup
DEVELOPER.md        → Development guide
API.md              → API reference
TESTING.md          → Testing guide
PROJECT_SUMMARY.md  → Project overview
QUICKSTART.md       → This file
```

---

## 🐛 Troubleshooting Quick Fixes

### "Bot doesn't respond"
```bash
# Check 1: Verify token is correct in .env
# Check 2: Ensure bot is running: python main.py
# Check 3: Check internet connection
```

### "Database error"
```bash
# Fix: Delete old database and reinitialize
rm dotgpt_bot.db
python init_sample_data.py
```

### "Permission denied"
```bash
# Make setup script executable
chmod +x setup.sh
./setup.sh
```

### "No module named 'telegram'"
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔗 Important Links

- **Telegram Bot API**: https://core.telegram.org/bots/api
- **python-telegram-bot**: https://python-telegram-bot.readthedocs.io/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **BotFather**: https://t.me/botfather

---

## ⚡ Performance Tips

1. **Use PostgreSQL** for 100+ users
2. **Add database indexes** for large queries
3. **Implement caching** for frequent lookups
4. **Monitor bot logs** regularly
5. **Backup database** daily in production

---

## 📈 Next Steps After Setup

1. ✅ Run quick start (5 min)
2. ✅ Test with sample data (5 min)
3. ✅ Try all features as buyer/supplier (10 min)
4. ✅ Explore admin panel (5 min)
5. ✅ Read documentation (20 min)
6. ✅ Customize with your data (30 min)
7. ✅ Deploy to production (1 hour)

---

## 💡 Common Customizations

### Change Sample Data
Edit `init_sample_data.py`:
- Products (line ~30)
- Suppliers (line ~50)
- Pricing (line ~80)

### Change Language Strings
Edit `strings.py`:
- Each language gets full translation
- 100+ strings included

### Add Admin Users
Edit `.env`:
```
ADMIN_IDS=123456789,987654321,111111111
```

### Change Database
Edit `.env`:
```
# SQLite (default)
DATABASE_URL=sqlite:///./dotgpt_bot.db

# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/db
```

---

## 🎓 Learning Resources

### Beginner
- Start with README.md
- Run quick start
- Test with sample data

### Intermediate
- Read FEATURES.md
- Study handlers/
- Learn database models

### Advanced
- Check DEVELOPER.md
- Examine API.md
- Extend with features

---

## 🤝 Support

For help:
1. Check README.md
2. Read FEATURES.md
3. Review TESTING.md
4. Check TROUBLESHOOTING section
5. Open GitHub issue

---

## ✅ Verification Checklist

After setup, verify:
- [ ] Bot responds to `/start`
- [ ] Can select language
- [ ] Can browse products
- [ ] Can view prices
- [ ] Can initiate chat
- [ ] Supplier sees anonymized buyer
- [ ] Admin can access `/admin`
- [ ] Database has sample data

---

## 🎉 Ready to Launch!

Your bot is production-ready with:
- ✅ Product catalog
- ✅ Multi-supplier support
- ✅ Anonymous buyer-supplier chat
- ✅ Admin controls
- ✅ 6-language UI
- ✅ Complete documentation

**Get started now!** 🚀

```bash
chmod +x setup.sh
./setup.sh
```

---

**Last Updated:** 2024
**Version:** 1.0
**Status:** Production Ready ✅
