"""
Setup script for E-commerce Telegram Bot
Helps initialize the database and verify configuration
"""
import os
import sys
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("📝 Please create a .env file from .env.example:")
        print("   cp .env.example .env")
        print("   Then edit it with your bot token and admin user ID")
        return False
    print("✅ .env file found")
    return True

def check_env_variables():
    """Check if required environment variables are set"""
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    admin_id = os.getenv('ADMIN_USER_ID')
    
    issues = []
    
    if not token or token == 'your_bot_token_here':
        issues.append("TELEGRAM_BOT_TOKEN is not set or using default value")
    else:
        print(f"✅ Bot token configured: {token[:10]}...")
    
    if not admin_id or admin_id == 'your_admin_user_id_here':
        issues.append("ADMIN_USER_ID is not set or using default value")
    else:
        print(f"✅ Admin user ID configured: {admin_id}")
    
    if issues:
        print("\n❌ Configuration issues found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n📝 Please edit your .env file with correct values:")
        print("   - Get bot token from @BotFather on Telegram")
        print("   - Get your user ID from @userinfobot on Telegram")
        return False
    
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import telegram
        print(f"✅ python-telegram-bot installed (version {telegram.__version__})")
    except ImportError:
        print("❌ python-telegram-bot not installed")
        print("   Run: pip install -r requirements.txt")
        return False
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy installed (version {sqlalchemy.__version__})")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

def initialize_database():
    """Initialize the database"""
    try:
        from models import init_db
        load_dotenv()
        
        database_url = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')
        engine = init_db(database_url)
        
        print(f"✅ Database initialized: {database_url}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def main():
    """Run setup checks"""
    print("=" * 50)
    print("E-commerce Telegram Bot - Setup Checker")
    print("=" * 50)
    print()
    
    checks = [
        ("Checking .env file", check_env_file),
        ("Checking environment variables", check_env_variables),
        ("Checking dependencies", check_dependencies),
        ("Initializing database", initialize_database),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        print(f"\n{check_name}...")
        if not check_func():
            all_passed = False
            if check_name in ["Checking .env file", "Checking environment variables"]:
                print("\n❌ Setup cannot continue without proper configuration")
                break
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ Setup complete! You can now run the bot:")
        print("   python bot.py")
    else:
        print("❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)
    print("=" * 50)

if __name__ == '__main__':
    main()
