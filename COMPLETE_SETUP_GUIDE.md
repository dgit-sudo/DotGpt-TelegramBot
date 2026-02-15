# 🚀 Complete Setup Guide: Deploy & Manage Your Bot

This guide walks you through deploying your bot for **FREE** and managing it as an admin.

---

## ✅ Prerequisites (5 minutes)

Before starting, you need:

1. **Telegram Bot Token**
   - Contact @BotFather on Telegram
   - Send `/newbot`
   - Follow instructions
   - Copy the token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

2. **Your Telegram ID**
   - Search for @userinfobot
   - Send `/start`
   - It shows your ID (example: `123456789`)

3. **GitHub Account** (for easy deployment)
   - Free account at github.com
   - Push this code to your repo

---

## 🎯 Part 1: Prepare for Deployment (10 minutes)

### Step 1: Create GitHub Repository

1. Go to **github.com** 
2. Click **"New"** (top left)
3. Name it: `DotGpt-TelegramBot`
4. Click **"Create repository"**

### Step 2: Push Code to GitHub

In your terminal:

```bash
cd /workspaces/DotGpt-TelegramBot
git init
git add .
git commit -m "Initial bot setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/DotGpt-TelegramBot.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 3: Create `.env` File

Create `.env` in project root:

```
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_IDS=YOUR_TELEGRAM_ID_HERE
DATABASE_URL=sqlite:///dotgpt_bot.db
PYTHON_VERSION=3.9
```

**Example:**
```
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_IDS=123456789
DATABASE_URL=sqlite:///dotgpt_bot.db
PYTHON_VERSION=3.9
```

### Step 4: Add Requirements File

Create `requirements.txt` in project root:

```
python-telegram-bot==20.7
sqlalchemy==2.0.0
python-dotenv==1.0.0
```

---

## 🌐 Part 2: Deploy on Railway (RECOMMENDED)

### Why Railway?
- ✅ Completely FREE ($5 credit/month = $60/year free hosting)
- ✅ Auto-deploys from GitHub
- ✅ PostgreSQL built-in
- ✅ 5-minute setup
- ✅ Reliable uptime

### Railway Setup (5 minutes)

1. **Create Railway Account**
   - Go to **railway.app**
   - Click "Get Started"
   - Click "GitHub" 
   - Authorize Railway
   - Click "Create New Project"

2. **Deploy Bot**
   - Click "Deploy from GitHub"
   - Select your `DotGpt-TelegramBot` repository
   - Click "Deploy"
   - Wait 2-3 minutes

3. **Configure Environment**
   - Go to "Variables" tab
   - Add these variables:
     ```
     BOT_TOKEN = your_bot_token
     ADMIN_IDS = your_telegram_id
     DATABASE_URL = postgresql://...
     ```
   - Click "Deploy"

4. **Test Bot**
   - Open Telegram
   - Find your bot (from @BotFather)
   - Send `/start`
   - You should see language selection ✅

### Debug Railway Deployment

If bot doesn't respond:

1. Go to **railway.app** → Your Project
2. Click "Logs" 
3. Look for errors
4. Common issues:
   - `BOT_TOKEN` is wrong → Check @BotFather for correct token
   - `ADMIN_IDS` missing → Add your Telegram ID
   - Database error → Railway auto-creates PostgreSQL, check connection

---

## 🔑 Part 3: Set Yourself as Admin

### After Successful Deployment:

1. **Open Telegram**
2. **Find your bot** (from @BotFather)
3. **Send `/start`**
4. **Choose "Supplier Panel"** (tests if admin properly)
5. **If you see "Admin Panel" option** → ✅ Admin setup worked!
6. **If you only see "Buyer" or "Supplier"** → ❌ Check ADMIN_IDS

### If Admin Panel Doesn't Show:

1. Go back to Railway project
2. Click "Variables"
3. Check `ADMIN_IDS`:
   - Should be: `ADMIN_IDS = 123456789` (just your ID)
4. Look for typos ❌
5. Click "Deploy" button
6. Wait 1 minute
7. Refresh Telegram and try `/start` again

---

## 💼 Part 4: Using Admin Panel

### Access Admin Panel

Send `/admin` to your bot.

### What You Can Do:

1. **👁️ View All Chats** - See all buyer-supplier conversations
2. **👥 Manage Users** - Block/unblock suspicious users
3. **🏪 Manage Suppliers** - Verify new suppliers
4. **📊 System Stats** - See total buyers, suppliers, messages

### First Test:

1. Send `/admin`
2. You should see menu with 4 options
3. Click "System Statistics" 
4. See your database info:
   - Total Buyers: should show a number
   - Total Suppliers: 3 (from sample data)
   - Total Products: 6 (from sample data)

---

## 👤 Testing as Buyer

### Create Buyer Account:

1. **New Telegram account** (ask friend) or use different device
2. Send `/start` to bot
3. Select language (e.g., English)
4. Click "Buyer"
5. Click "Browse Products"
6. See 6 sample products with prices from 3 suppliers ✅

### Try Buying:

1. Click product (e.g., "Laptop")
2. See prices from all suppliers
3. Click "💬 Contact [Supplier Name]"
4. Send message to supplier ✅
5. Supplier receives anonymized chat

---

## 🏪 Adding Real Suppliers

### Step 1: Supplier Registration

1. Person wants to be supplier
2. Send `/start` to bot
3. Select language
4. Click "Supplier Panel"
5. Click "Register as Supplier"
6. Enter company name (e.g., "TechWorld Ltd")
7. Bot shows: "⏳ Waiting for admin approval"

### Step 2: Admin Approval

You (as admin):
1. Send `/admin` to bot
2. Click "Manage Suppliers"
3. See "⚠️ Pending Verification"
4. Click supplier name
5. Review company info
6. Click "✅ Verify Supplier"
7. Supplier is now LIVE ✅

### Step 3: Supplier Adds Products

Supplier:
1. Send `/supplier` to bot
2. Click "💰 Set Prices"
3. Browse existing products
4. Click product (e.g., "Laptop")
5. Enter price (e.g., $800)
6. Enter stock (e.g., 5)
7. Product now shows in buyer search ✅

---

## 🔒 Privacy: Protected by Default

Your bot automatically:
- ✅ Hides buyer's Telegram profile from supplier
- ✅ Shows supplier only chat messages (no profile)
- ✅ Prevents direct Telegram contact between buyer-supplier
- ✅ Keeps all communication in-bot only
- ✅ Admin can see both sides for moderation

**Nothing extra to configure** - it works by default.

---

## 📱 Multi-Language Support

Bot supports 6 languages (automatically selected):
- 🇬🇧 English
- 🇪🇸 Español (Spanish)
- 🇫🇷 Français (French)
- 🇩🇪 Deutsch (German)
- 🇮🇹 Italiano (Italian)
- 🇵🇹 Português (Portuguese)

User selects language on `/start` - everything translates automatically.

---

## 🆘 Troubleshooting

### Problem: Bot doesn't respond to `/start`

**Solution:**
1. Check bot is running:
   - Go to Railway project
   - Look at "Logs" - should show no errors
2. Check `BOT_TOKEN` is correct:
   - Copy exact token from @BotFather
   - No spaces, no extra characters
3. Restart bot:
   - Go to Railway → "More" → "Restart"
   - Wait 30 seconds
   - Try `/start` again

### Problem: Admin panel doesn't show

**Solution:**
1. Check `ADMIN_IDS`:
   - Your Telegram ID from @userinfobot
   - No spaces after ID
   - Format: `ADMIN_IDS=123456789`
2. Redeploy:
   - Click "Deploy" in Railway
   - Wait 1 minute
   - Try `/admin` again

### Problem: Database error

**Solution:**
1. Railway AUTO-creates PostgreSQL
2. Check "Plugins" in Railway:
   - Should see "PostgreSQL" ✅
3. Check DATABASE_URL variable:
   - Should be auto-filled ✅
   - Don't change it
4. If missing:
   - Click "Create" next to PostgreSQL
   - It auto-configures DATABASE_URL

### Problem: Buyer can see supplier's profile

**This is a bug** - report:
1. Go to project GitHub
2. Click "Issues"
3. Click "New Issue"
4. Describe the issue
5. Submit

**Should NOT happen** - privacy enforced by code.

---

## 📊 Monitoring Your Bot

### Daily Checks:

1. **Send yourself `/admin`**
   - Click "System Statistics"
   - See today's stats:
     - New buyers
     - New suppliers
     - Active chats
     - Messages sent

2. **Check for abusive users:**
   - `/admin` → "View All Chats"
   - Scan conversations
   - Block spam users

3. **Verify pending suppliers:**
   - `/admin` → "Manage Suppliers"
   - See pending approvals
   - Verify legitimate ones

### Weekly Checks:

1. **Backup database** (Railway does auto-backup, but recommended)
2. **Check logs** for errors
3. **Test as buyer** to ensure everything works

---

## 🔐 Scaling Up: Multiple Admins

### Add More Admins (No Code Change!)

1. Get their Telegram ID (they use @userinfobot)
2. Go to Railway Variables
3. Change:
   ```
   From: ADMIN_IDS=123456789
   To:   ADMIN_IDS=123456789,987654321,555555555
   ```
   (separate with commas, no spaces)
4. Click "Deploy"
5. All 3 can now send `/admin` ✅

### Add Unlimited Admins:
```
ADMIN_IDS=ID1,ID2,ID3,ID4,ID5,ID6,ID7,ID8,ID9,ID10
```

---

## 💰 Free vs Paid Options

### FREE (Railway) - Recommended ✅
- $5 credit/month = $60/year FREE
- Unlimited projects
- Auto-scale
- PostgreSQL included
- Perfect for small-medium business

### FREE (Render/Fly.io)
- 750 hours/month free (Render)
- 3 shared CPU (Fly.io)
- Both work, bit slower
- See FREE_DEPLOYMENT.md for details

### PAID (When You Grow)
- Railway paid: $5+/month
- AWS/Google Cloud: $15+/month
- Heroku: $7-25/month
- Only upgrade when you have 1000+ users

---

## 🎯 Next Steps

1. ✅ **Deploy on Railway** (5 min)
2. ✅ **Test bot with `/start`** (2 min)
3. ✅ **Send `/admin`** - check admin panel (2 min)
4. ✅ **Invite 1 supplier** - test registration (10 min)
5. ✅ **Invite 1 buyer** - test purchase flow (10 min)
6. ✅ **Monitor chat** - make sure privacy works (5 min)

**Total time: ~35 minutes to full working deployment**

---

## 📚 More Documentation

- **FEATURES.md** - All bot features
- **ADMIN_MANAGEMENT.md** - Advanced admin tasks
- **DATABASE.md** - Database schema details
- **API.md** - Technical API reference

---

## ✨ You're Live!

Your Telegram bot is now:
- ✅ Live 24/7 on Railway
- ✅ Supports 6 languages
- ✅ Handles multiple suppliers
- ✅ Protects buyer privacy
- ✅ Lets you manage everything
- ✅ FREE to run

**Start inviting suppliers and buyers!** 🎉

---

**Have questions?** See ADMIN_MANAGEMENT.md for detailed admin guide.
