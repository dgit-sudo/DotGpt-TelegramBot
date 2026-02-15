# E-commerce Telegram Bot 🛍️

A comprehensive Telegram bot for selling products with multi-language support, supplier management, and anonymous chat functionality.

## Features

### 🌍 Multi-Language Support
- Supports 6 languages:
  - 🇬🇧 English
  - 🇪🇸 Spanish
  - 🇫🇷 French
  - 🇩🇪 German
  - 🇮🇹 Italian
  - 🇵🇹 Portuguese

### 👑 Admin Panel
- Manage all products
- Manage suppliers (promote users to suppliers)
- View all chats between buyers and suppliers
- Full control over the bot

### 🏪 Supplier Panel
- Add new products with:
  - Product name
  - Description
  - Price
  - Payment methods
- View and manage own products
- Chat with buyers anonymously
- Receive notifications for new messages

### 🛒 Buyer Features
- Browse all available products
- View product details including:
  - Name and description
  - Price and currency
  - Supplier information
  - Available payment methods
- Contact suppliers directly through the bot
- Anonymous profile (hidden from suppliers)
- In-bot chat system

### 💬 Anonymous Chat System
- Buyers can chat with suppliers about products
- Buyer's profile is hidden from suppliers
- All communication happens within the bot
- Real-time message notifications
- Message history stored in database

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/dgit-sudo/DotGpt-TelegramBot.git
cd DotGpt-TelegramBot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Configure the `.env` file:
```env
# Get your bot token from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Get your Telegram user ID from @userinfobot
ADMIN_USER_ID=your_admin_user_id_here

# Database path (default is fine for most cases)
DATABASE_URL=sqlite:///bot_database.db
```

### Getting Started

1. **Create a Telegram Bot**:
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow the instructions
   - Copy the bot token provided

2. **Get Your User ID**:
   - Search for `@userinfobot` on Telegram
   - Start a chat and it will send you your user ID

3. **Run the Bot**:
```bash
python bot.py
```

## Usage

### For Admin
1. Start the bot with `/start`
2. Select your language
3. Click "👑 Admin Panel"
4. Options:
   - Manage Products: View all products in the system
   - Manage Suppliers: Promote users to suppliers
   - View All Chats: Monitor all conversations

### For Suppliers
1. Start the bot with `/start` (after being promoted by admin)
2. Click "🏪 Supplier Panel"
3. Options:
   - My Products: View and manage your products
   - Add New Product: Create a new product listing
   - Incoming Messages: Check messages from buyers

### For Buyers
1. Start the bot with `/start`
2. Click "📦 Browse Products"
3. Select a product to view details
4. Click "📞 Contact Supplier" to start a chat
5. Send messages directly in the chat

## Database Schema

### Users
- Telegram ID (unique)
- Username, first name, last name
- Role (admin, supplier, buyer)
- Language preference
- Created timestamp

### Products
- Name and description
- Price and currency
- Supplier ID (foreign key to Users)
- Payment methods
- Active status
- Created timestamp

### Chats
- Buyer ID (foreign key to Users)
- Supplier ID (foreign key to Users)
- Product ID (foreign key to Products)
- Active status
- Created timestamp

### Messages
- Chat ID (foreign key to Chats)
- Sender ID and Receiver ID (foreign keys to Users)
- Message text
- Read status
- Created timestamp

## Architecture

```
bot.py              # Main bot application with all handlers
models.py           # Database models (SQLAlchemy)
translations.py     # Multi-language translations
requirements.txt    # Python dependencies
.env               # Configuration (not in repo)
.env.example       # Configuration template
```

## Security Features

- Admin authentication
- Role-based access control
- Anonymous buyer profiles
- Secure database storage
- Environment variable configuration

## Development

### Adding a New Language

Edit `translations.py` and add a new language dictionary following the existing pattern:

```python
TRANSLATIONS = {
    # ... existing languages ...
    'new_lang': {
        'welcome': "Welcome message in new language",
        # ... all other keys ...
    }
}
```

### Adding New Features

The bot uses the `python-telegram-bot` library with the following structure:
- Command handlers for `/start`, etc.
- Callback query handlers for button clicks
- Message handlers for text messages
- Conversation handlers for multi-step operations

## Troubleshooting

### Bot doesn't respond
- Check if the bot token is correct in `.env`
- Ensure the bot is running (`python bot.py`)
- Check internet connection

### Database errors
- Delete `bot_database.db` and restart the bot
- Check file permissions

### Admin panel not showing
- Verify `ADMIN_USER_ID` in `.env` matches your Telegram user ID
- Restart the bot after changing `.env`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For support, please open an issue on GitHub or contact the administrator.