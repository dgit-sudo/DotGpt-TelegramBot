# Quick Start Guide

## 1️⃣ Get Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the instructions:
   - Choose a name for your bot (e.g., "My Shop Bot")
   - Choose a username ending with "bot" (e.g., "myshop_bot")
4. **Copy the token** you receive (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 2️⃣ Get Your User ID

1. Search for **@userinfobot** on Telegram
2. Start a chat with it
3. It will send you your user ID (a number like: `123456789`)
4. **Copy this number**

## 3️⃣ Set Up the Bot

```bash
# Clone the repository
git clone https://github.com/dgit-sudo/DotGpt-TelegramBot.git
cd DotGpt-TelegramBot

# Install dependencies
pip install -r requirements.txt

# Create your configuration file
cp .env.example .env
nano .env  # or use any text editor
```

## 4️⃣ Configure the Bot

Edit the `.env` file and paste your token and user ID:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_USER_ID=123456789
DATABASE_URL=sqlite:///bot_database.db
```

## 5️⃣ Verify Setup

```bash
python setup.py
```

You should see:
```
✅ .env file found
✅ Bot token configured
✅ Admin user ID configured
✅ python-telegram-bot installed
✅ SQLAlchemy installed
✅ Database initialized
✅ Setup complete!
```

## 6️⃣ Run the Bot

```bash
python bot.py
```

You should see:
```
Bot started!
```

## 7️⃣ Test the Bot

1. Open Telegram and search for your bot username
2. Send `/start`
3. Select your language
4. You should see the main menu with "👑 Admin Panel" button

## 8️⃣ Using the Bot

### As Admin (First User):
- **Admin Panel** → Manage everything
- **Manage Suppliers** → Promote users to suppliers
- **View All Chats** → See all conversations

### As Supplier (After Promotion):
- **Supplier Panel** → Manage your products
- **Add New Product** → List products with prices
- **My Products** → View/edit your listings
- **Incoming Messages** → Chat with buyers

### As Buyer (Default Role):
- **Browse Products** → See all available items
- Select a product → View details and prices
- **Contact Supplier** → Start anonymous chat
- **My Chats** → View your conversations

## Common Issues

### Bot doesn't respond
- Make sure `python bot.py` is running
- Check that the bot token is correct
- Verify internet connection

### Admin panel not showing
- Confirm ADMIN_USER_ID matches your Telegram user ID
- Restart the bot after changing .env

### Permission denied
- Run with `python3` instead of `python`
- Check file permissions: `chmod +x bot.py`

## Next Steps

1. **Invite users** to your bot
2. **Promote suppliers** via Admin Panel
3. **Suppliers add products** via Supplier Panel
4. **Buyers browse and chat** with suppliers

## Support

- Read the full README.md for detailed documentation
- Check DEPLOYMENT.md for production deployment
- Run `python test_bot.py` to verify installation

Enjoy your E-commerce Bot! 🛍️
