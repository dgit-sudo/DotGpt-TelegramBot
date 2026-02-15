# 🚀 Deploy on Fly.io - Complete Guide

## Why Fly.io? 

✅ **Truly Free Forever** - No credit card required  
✅ **Generous Limits** - 3 shared-cpu VMs free  
✅ **Perfect for Bots** - Always-on 24/7 availability  
✅ **Simple Deployment** - Just 5 minutes setup  
✅ **Great Performance** - Fast, reliable, global  
✅ **Database Included** - SQLite works great  

---

## ⚡ QUICK START (5 Minutes)

### Step 1️⃣: Install Fly CLI

**On Mac:**
```bash
brew install flyctl
```

**On Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**On Windows:**
Download from: https://github.com/superfly/flyctl/releases

Then verify:
```bash
flyctl version
```

### Step 2️⃣: Create Fly.io Account

```bash
flyctl auth signup
```

Choose "email" for signup (fastest option)
- Enter your email
- Verify email
- Set password
- Done!

Verify login:
```bash
flyctl auth whoami
```

### Step 3️⃣: Prepare Your Bot

Navigate to your bot directory:
```bash
cd /workspaces/DotGpt-TelegramBot
```

### Step 4️⃣: Create Fly.io App

```bash
flyctl launch
```

When prompted:
- **App name**: Enter something like `dotgpt-bot` (must be unique)
- **Region**: Choose closest to you (e.g., `sjc` for US West)
- **Postgres database**: Press `N` (we use SQLite)
- **Redis cache**: Press `N` (not needed)
- **Deploy now**: Press `N` (we'll configure first)

This creates:
- `fly.toml` (configuration file)
- `.dockerignore` (Docker ignore file)

### Step 5️⃣: Set Environment Variables

```bash
flyctl secrets set BOT_TOKEN="your_token_from_botfather"
```

Replace `your_token_from_botfather` with your actual token from BotFather.

Verify it was set:
```bash
flyctl secrets list
```

### Step 6️⃣: Deploy!

```bash
flyctl deploy
```

Watch the logs until you see:
```
🤖 DotGPT Bot started successfully!
```

### Step 7️⃣: Test Your Bot

Open Telegram and:
1. Search for your bot (if public) or use the BotFather link
2. Click `/start`
3. Select a language
4. Test buying/selling features

**Done! 🎉 Your bot is live!**

---

## 📋 DETAILED WALKTHROUGH

### Get Your Bot Token

If you don't have a token yet:

1. **Open Telegram** and search for `@BotFather`
2. **Click "Start"**
3. **Send `/newbot`**
   ```
   /newbot
   ```
4. **Name your bot**
   ```
   DotGPT Shop Bot
   ```
5. **Username** (must end with "bot")
   ```
   dotgpt_mybot_bot
   ```
6. **Copy the token** (looks like: `123456:ABC-1A2B3C4D5E6F`)
7. **Save it somewhere safe**

### Complete Fly.io Setup

#### Installing Fly CLI

**Mac Users:**
```bash
# Install
brew install flyctl

# Verify
flyctl version
```

**Linux Users:**
```bash
# Download and install
curl -L https://fly.io/install.sh | sh

# Add to PATH
export PATH="/home/$USER/.fly/bin:$PATH"

# Verify
flyctl version
```

**Windows Users:**
1. Go to: https://github.com/superfly/flyctl/releases
2. Download: `flyctl_Windows_x86_64.zip`
3. Extract to a folder
4. Add folder to PATH (System Environment Variables)
5. Open Command Prompt and verify:
   ```
   flyctl version
   ```

#### Login to Fly.io

```bash
# Sign up with email
flyctl auth signup

# Or login if you already have account
flyctl auth login
```

Follow the prompts:
- Choose email signup
- Verify your email
- Set strong password
- Save credentials

#### Initialize Your Project

```bash
cd /workspaces/DotGpt-TelegramBot

# Create Fly.io app
flyctl launch
```

**Prompts explained:**

| Prompt | Answer | Reason |
|--------|--------|--------|
| **App Name** | `dotgpt-bot` | Unique identifier (will be `yourname-dotgpt-bot.fly.dev`) |
| **Postgres** | `N` | We use SQLite (lighter, free) |
| **Redis** | `N` | Not needed for this bot |
| **Deploy now** | `N` | We'll configure secrets first |

#### Configure Bot Token

```bash
# Set your bot token
flyctl secrets set BOT_TOKEN="YOUR_TOKEN_HERE"
```

Replace `YOUR_TOKEN_HERE` with your actual token from BotFather.

**Example:**
```bash
flyctl secrets set BOT_TOKEN="123456:ABC-1A2B3C4D5E6F7G8H9I0J"
```

**Verify it was set:**
```bash
flyctl secrets list
```

You should see:
```
NAME       DIGEST                   CREATED AT
BOT_TOKEN  sha256:abc123...        2 minutes ago
```

#### Deploy Your Bot

```bash
# Deploy
flyctl deploy
```

This will:
1. Build a Docker image
2. Upload to Fly.io
3. Start your app
4. Show live logs

**Watch for success message:**
```
🤖 DotGPT Bot started successfully!
📊 Database initialized!
🌍 Multi-language support enabled!
```

If you see errors, check logs:
```bash
flyctl logs
```

#### Monitor Your Bot

**View logs:**
```bash
flyctl logs
```

**View status:**
```bash
flyctl status
```

**View app info:**
```bash
flyctl info
```

**View all apps:**
```bash
flyctl apps list
```

---

## 🧪 TESTING YOUR BOT

### Test on Telegram

1. **Open Telegram**
2. **Search for your bot** (use the username from BotFather)
3. **Click "Start"**
4. **You should see:**
   ```
   Welcome to DotGPT Shop Bot 🛍️
   
   Select your language:
   [English] [Español] [Français] ...
   ```
5. **Click a language**
6. **Main menu appears:**
   ```
   👤 Browse Products
   🏪 Supplier Dashboard
   ```
7. **Test each feature**

### Test Logs

Check bot logs in real-time:
```bash
flyctl logs -n 50
```

This shows last 50 log entries. You should see:
- User messages
- Language selections
- Database queries
- Translation operations

---

## 🔧 MANAGING YOUR BOT

### Update Bot Code

After making changes to `main.py`:

```bash
# Go to your repo
cd /workspaces/DotGpt-TelegramBot

# Commit changes
git add .
git commit -m "Update bot features"

# Redeploy
flyctl deploy
```

### Check Resource Usage

```bash
# Memory usage
flyctl resources

# Current metrics
flyctl info
```

### Restart Bot

```bash
flyctl restart
```

### Scale (if needed)

```bash
# Scale to 2 instances (uses more free tier)
flyctl scale memory 512

# Check status
flyctl status
```

### View Secrets

```bash
# List all secrets
flyctl secrets list

# Update secret
flyctl secrets set BOT_TOKEN="new_token"

# Remove secret
flyctl secrets destroy BOT_TOKEN
```

---

## 📊 FLY.IO FREE TIER LIMITS

| Resource | Free Limit | Enough For |
|----------|-----------|-----------|
| **Shared VMs** | 3 total | Multiple bots |
| **Memory per VM** | 256 MB | Telegram bots |
| **Disk Storage** | 3 GB total | Database + files |
| **Bandwidth** | 30 GB/month | ~10,000 messages/day |
| **Duration** | Forever free | Permanent hosting |

---

## 🐛 TROUBLESHOOTING

### Bot not responding

**Check logs:**
```bash
flyctl logs
```

Look for errors. Common issues:

1. **"No token found"**
   ```bash
   flyctl secrets list
   ```
   If empty, set token again:
   ```bash
   flyctl secrets set BOT_TOKEN="your_token"
   ```

2. **"Connection error"**
   - Bot might be crashing
   - Check logs: `flyctl logs`
   - Restart: `flyctl restart`

3. **"Database locked"**
   - SQLite file issue
   - Usually fixes itself
   - If not: `flyctl restart`

### High CPU/Memory Usage

**Check usage:**
```bash
flyctl resources
```

**If too high:**
```bash
# Restart app
flyctl restart

# Or scale up memory
flyctl scale memory 512
```

### Can't deploy

**Common causes:**

1. **Missing requirements.txt**
   ```bash
   # Regenerate
   pip freeze > requirements.txt
   git add requirements.txt
   git commit -m "Add requirements"
   flyctl deploy
   ```

2. **Python version mismatch**
   - Edit `fly.toml`
   - Ensure Python 3.9+ specified
   - Redeploy

3. **Syntax errors**
   - Check your code: `python -m py_compile main.py`
   - Fix errors
   - Redeploy

### Database issues

**Check database:**
```bash
# Restart (clears any locks)
flyctl restart

# Check logs for DB errors
flyctl logs | grep -i database
```

---

## 🌐 MAKING BOT PUBLIC

### Option 1: Via BotFather

In BotFather, set:
- **Bot Name** - Display name
- **Description** - What it does
- **Menu button** - Commands
- **Privacy** - Public

### Option 2: Share Bot Link

Anyone can access via:
```
https://t.me/yourbot_username
```

Get link from BotFather message.

---

## 📱 ACCESSING BOT FROM ANYWHERE

Your bot is available at:

```
https://yourname-dotgpt-bot.fly.dev
```

Or directly search Telegram for your bot username.

---

## 🚀 ADVANCED: Custom Domain

If you want custom domain:

1. **Buy domain** (GoDaddy, Namecheap, etc.)
2. **Configure DNS** to point to Fly.io
3. **Link to Fly.io:**
   ```bash
   flyctl certs add yourdomain.com
   ```

(Advanced - optional for most users)

---

## 💾 BACKUP YOUR DATA

### Download Database

```bash
# Remote database to local
flyctl sftp shell

# Then download data
```

### Backup Strategy

1. Weekly download of SQLite database
2. Keep git repo with code
3. Store secrets separately

---

## ⚡ COMMANDS CHEAT SHEET

```bash
# Account
flyctl auth signup              # Create account
flyctl auth login               # Login
flyctl auth whoami              # Check logged in

# Project Management
flyctl launch                   # Create new app
flyctl deploy                   # Deploy/redeploy
flyctl status                   # Check status
flyctl logs                     # View logs
flyctl restart                  # Restart bot

# Secrets
flyctl secrets set KEY=VALUE    # Add secret
flyctl secrets list             # View secrets
flyctl secrets destroy KEY      # Remove secret

# Monitoring
flyctl resources                # Resource usage
flyctl info                     # App details
flyctl scale memory SIZE        # Scale memory
```

---

## 🎯 NEXT STEPS

1. **Deploy now** using steps above
2. **Test your bot** on Telegram
3. **Monitor logs** for issues
4. **Make updates** to code as needed
5. **Share bot** with friends

---

## 📞 SUPPORT

### Having Issues?

1. **Check Fly.io Docs:** https://fly.io/docs
2. **View Bot Logs:** `flyctl logs`
3. **Check Telegram:** Ensure bot is running (`flyctl status`)
4. **Restart Bot:** `flyctl restart`
5. **Redeploy:** `flyctl deploy`

### Common Commands

```bash
# See everything
flyctl help

# Get help for command
flyctl help deploy

# Check version
flyctl version
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Fly CLI installed (`flyctl version` works)
- [ ] Fly.io account created (`flyctl auth whoami` shows your email)
- [ ] Bot token from BotFather in hand
- [ ] App created (`flyctl launch` completed)
- [ ] Bot token set (`flyctl secrets list` shows BOT_TOKEN)
- [ ] Code deployed (`flyctl deploy` succeeded)
- [ ] Bot is responding on Telegram (`/start` works)
- [ ] Features working (language selection, chat, etc.)
- [ ] Logs look clean (`flyctl logs` has no errors)

**Once all checked: You're done! 🎉**

---

## 🎓 LEARNING MORE

- **Fly.io Docs:** https://fly.io/docs
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Python Telegram Bot:** https://python-telegram-bot.readthedocs.io

---

**Last Updated:** February 2026  
**Status:** ✅ Production Ready  
**Cost:** FREE FOREVER 🚀
