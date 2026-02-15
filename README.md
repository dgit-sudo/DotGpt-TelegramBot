# 🤖 DotGPT Shop - Telegram Bot for Multi-Supplier E-Commerce

**A complete, production-ready Telegram bot for selling products with multiple suppliers, 6 languages, and secure buyer-supplier communication.**

---

## 🎯 What This Bot Does

✅ **Buyers** browse products from multiple suppliers and chat anonymously  
✅ **Suppliers** register, add products, set prices, and handle inquiries  
✅ **Admins** verify suppliers, monitor chats, manage users  
✅ **Supported** in 6 languages (English, Spanish, French, German, Italian, Portuguese)  
✅ **Privacy** - Buyer profiles hidden from suppliers, in-bot communication only  
✅ **FREE** to deploy on Railway, Render, Fly.io, or Replit  

---

## 🚀 Quick Start (35 minutes)

### ⏰ Before You Start
You need:
1. **Telegram Bot Token** - Get from [@BotFather](https://t.me/botfather)
2. **Your Telegram ID** - Get from [@userinfobot](https://t.me/userinfobot)
3. **GitHub Account** - For easy deployment

### 📖 Complete Setup Guide
**→ [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)** ← Start here!

Covers:
- How to create bot token ✅
- How to deploy FREE on Railway (5 min) ✅
- How to test the bot ✅
- How to add suppliers and admins ✅

### ⚙️ Install & Run Locally (for testing)

```bash
# 1. Clone this repo
git clone <your-repo-url>
cd DotGpt-TelegramBot

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
echo "BOT_TOKEN=YOUR_TOKEN_HERE" > .env
echo "ADMIN_IDS=YOUR_TELEGRAM_ID" >> .env

# 5. Run bot
python main.py
```

Bot will print: `Bot is running...` when ready.

---

## ✨ Features

### 🛍️ **Buyer Features**
- Browse products from multiple suppliers
- View prices from different suppliers for the same product
- See supplier-specific payment methods
- Initiate anonymous chats with suppliers (profile hidden)
- Chat with suppliers about specific products
- View order history and active chats

### 🏪 **Supplier Features**
- Register and get verified by admin
- Manage products and pricing
- View buyer inquiries with anonymized buyer profiles
- Chat with buyers securely
- Configure payment methods
- Track statistics and analytics

### 👨‍💼 **Admin Features**
- Approve/reject new suppliers
- View all chats in the system
- Manage all users (buyers and suppliers)
- Block/unblock abusive users
- Monitor system statistics
- No code changes needed to add new admins (just edit ADMIN_IDS)

### 🌍 **6-Language Support**
- 🇬🇧 English
- 🇪🇸 Spanish (Español)
- 🇫🇷 French (Français)
- 🇩🇪 German (Deutsch)
- 🇮🇹 Italian (Italiano)
- 🇵🇹 Portuguese (Português)

User selects language on `/start` - everything auto-translates.

### 🔒 **Privacy & Security (Default)**
- ✅ Buyer name hidden from supplier
- ✅ Buyer Telegram ID hidden from supplier
- ✅ Communication only through bot (no direct contact)
- ✅ Verification system for suppliers
- ✅ Admin can block users for abuse
- ✅ Role-based access control

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) | **START HERE** - Deploy in 35 minutes |
| [ADMIN_QUICK_REFERENCE.md](ADMIN_QUICK_REFERENCE.md) | Quick admin commands and checklist |
| [ADMIN_MANAGEMENT.md](ADMIN_MANAGEMENT.md) | Detailed admin operations guide |
| [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md) | Free hosting options (Railway, Render, Fly.io) |
| [FEATURES.md](FEATURES.md) | Complete feature list |
| [DEVELOPER.md](DEVELOPER.md) | Developer setup and extending the bot |

---

## 💻 Deployment Options

### FREE Hosting (Recommended)

| Platform | Free Tier | Setup Time | Uptime | Database |
|----------|-----------|-----------|--------|----------|
| **Railway** ⭐ | $5/month credit ($60/year) | 5 min | 99.9% | Auto PostgreSQL |
| **Render** | 750 hours/month | 10 min | 99% | Auto PostgreSQL |
| **Fly.io** | 3 CPU shared | 15 min | 99.9% | Buy separately |
| **Replit** | Unlimited free | 10 min | Need Uptime Robot | SQLite in storage |

**→ [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md)** for exact step-by-step setup for each platform.

### Paid Hosting (When You Scale)
- AWS, Google Cloud, Azure (from $15/month)
- Heroku (from $7/month)
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

---

## 🏃 Quick Commands

After deployment, test these commands in Telegram:

```
/start           # Initialize bot, select language
/admin           # Access admin panel (if you're admin)
/buyer           # Switch to buyer mode
/supplier        # Switch to supplier mode (must be verified first)
```

---

## 📋 Requirements

- Python 3.9+
- pip (Python package manager)
- Telegram Bot Token (Get from [@BotFather](https://t.me/botfather))
- Environment variables in `.env` file
- SQLite (default) or PostgreSQL

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/dgit-sudo/DotGpt-TelegramBot.git
cd DotGpt-TelegramBot
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
```
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=123456789,987654321
DATABASE_URL=sqlite:///./dotgpt_bot.db
```

### 5. Initialize database
```bash
python init_sample_data.py
```

This will create:
- Database tables
- 6 sample products
- 3 sample suppliers (verified)
- 3 sample buyers
- Payment methods for each supplier

### 6. Run the bot
```bash
python main.py
```

## 📁 Project Structure

```
DotGpt-TelegramBot/
├── main.py                      # Main bot entry point
├── config.py                    # Configuration settings
├── database.py                  # SQLAlchemy models
├── database_helpers.py          # Database utility functions
├── strings.py                   # Localization strings (6 languages)
├── init_sample_data.py          # Sample data initialization
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                    # This file
└── handlers/                    # Bot command handlers
    ├── __init__.py
    ├── start.py                 # /start command
    ├── language_selection.py    # Language selection
    ├── buyer_handlers.py        # Buyer interface
    ├── supplier_handlers.py     # Supplier dashboard
    ├── admin_handlers.py        # Admin panel
    └── chat_handlers.py         # Chat system
```

## 🎮 Usage

### For Buyers
1. Start the bot: `/start`
2. Select language
3. Choose "Browse Products"
4. Browse available products
5. View prices from different suppliers
6. Contact suppliers and chat anonymously

### For Suppliers
1. Start the bot: `/start`
2. Select language
3. Choose "Supplier Panel"
4. Register company (requires admin verification)
5. Add products and set prices
6. Configure payment methods
7. Respond to buyer inquiries

### For Admins
1. Use `/admin` command
2. Access admin panel with these options:
   - View all chats
   - Manage users
   - Verify suppliers
   - View system statistics

## 💾 Database Schema

### Products
- Product ID, name, description, category, status

### Suppliers
- Supplier ID, company name, contact info, verification status, payment methods

### Buyers
- Buyer ID, account info, language preference

### Chats
- Chat ID, participant IDs, messages, status

### Pricing
- Product-Supplier-Price relationship with stock levels

### Payments
- Supplier payment method options

## 🔄 Communication Flow

```
Buyer (Anonymous)
    ↓
Chat System
    ↓
Supplier (No Access to Buyer Profile)
```

Suppliers can:
- See chat messages
- Respond to inquiries
- Share payment details
- Cannot see buyer's personal information

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token from BotFather | Yes |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs | Yes |
| `DATABASE_URL` | Database connection URL | No (defaults to SQLite) |

### Database Options

**SQLite (Default):**
```
DATABASE_URL=sqlite:///./dotgpt_bot.db
```

**PostgreSQL:**
```
DATABASE_URL=postgresql://user:password@localhost:5432/dotgpt_db
```

## 📊 Payment Methods

Currently supported payment method types (configurable per supplier):
- Credit Card
- Bank Transfer
- PayPal
- Cryptocurrency
- Cash on Delivery

Each supplier can configure which methods they accept.

---

## ✅ Installation Complete?

**Next Steps:**

1. **To Deploy (Recommended):** See [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
2. **To Run Locally:** See instructions above in "Quick Start" section
3. **To Be Admin:** See [ADMIN_QUICK_REFERENCE.md](ADMIN_QUICK_REFERENCE.md)

---

## 🐛 Troubleshooting

### Bot doesn't respond after `/start`
1. Check `BOT_TOKEN` is exactly right (copy from @BotFather)
2. Run `python main.py` and verify `Bot is running...` message
3. Wait 10 seconds and try `/start` again

### Can't access admin panel (no `/admin` button)
1. Get your Telegram ID from @userinfobot
2. Check `.env` has: `ADMIN_IDS=YOUR_ID_HERE` (no spaces)
3. Restart bot: `Ctrl+C` then `python main.py`

### Database errors (can't start bot)
```bash
# Delete old database
rm dotgpt_bot.db

# Reinitialize with sample data
python init_sample_data.py

# Start again
python main.py
```

### See more help → [ADMIN_MANAGEMENT.md](ADMIN_MANAGEMENT.md#-support-for-admins)

---

## 🔐 Security Best Practices

1. **Never share `.env` file** - It has your BOT_TOKEN (secret)
2. **Keep ADMIN_IDS private** - These IDs can be public but don't post them online
3. **Use strong PostgreSQL password** if using production database
4. **Regularly update** python-telegram-bot package: `pip install --upgrade python-telegram-bot`

---

## 📚 Want to Learn More?

| I Want To... | Read This |
|---|---|
| Deploy to production RIGHT NOW | [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) |
| Manage suppliers and admins | [ADMIN_MANAGEMENT.md](ADMIN_MANAGEMENT.md) |
| Quick admin commands reference | [ADMIN_QUICK_REFERENCE.md](ADMIN_QUICK_REFERENCE.md) |
| Explore all features | [FEATURES.md](FEATURES.md) |
| Understand the code | [DEVELOPER.md](DEVELOPER.md) |
| Deploy on free platforms | [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md) |
| Production deployment | [DEPLOYMENT.md](DEPLOYMENT.md) |

---

## ❓ FAQ

**Q: Is it really FREE?**
A: Yes! Railway gives you $5/month credit ($60/year free). That's enough for bots with up to 100K users.

**Q: Can I change the product names?**
A: Yes! Use `init_sample_data.py` as a template and modify it, or use the admin panel to add products.

**Q: How many languages can I add?**
A: Currently 6 languages. To add more, edit `strings.py` - follow the same structure.

**Q: Can I use a different database?**
A: Yes! The code uses SQLAlchemy, so it supports PostgreSQL, MySQL, etc. See `.env` examples.

**Q: What if my bot gets deleted?**
A: Get a new token from @BotFather and change `BOT_TOKEN` in `.env`, then redeploy.

---

## 🎉 Ready to Launch?

1. ✅ Have Telegram Bot Token? (Get from @BotFather)
2. ✅ Know your Telegram ID? (Get from @userinfobot)
3. ✅ Ready to deploy? → **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)**

**Total time to live deployment: 35 minutes**

---

**Questions?** Check the documentation files above or open a GitHub issue.

**Made with ❤️ by DotGPT**
