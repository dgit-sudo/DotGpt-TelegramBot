# 🚀 FREE Telegram Bot Deployment Guide

## Complete Free Deployment Options (No Credit Card Required)

---

## 🌟 RECOMMENDED: FLY.IO (Most Generous Free Tier)

**✅ Truly Free Forever | ✅ Generous Limits | ✅ Perfect for Bots**

→ **[Complete Fly.io Guide](FLY_IO_DEPLOYMENT.md)** (Step-by-step tutorial)

**Why Fly.io?**
- 3 shared VMs completely free (vs Railway's limited hours)
- No credit card required
- Perfect for 24/7 bot operation  
- Global server availability
- Super simple 5-minute setup

**Quick Start:**
```bash
# Install Fly CLI
brew install flyctl  # Mac
# or visit: https://flyctl.io/install for other OS

# Login
flyctl auth signup

# Deploy your bot
cd /workspaces/DotGpt-TelegramBot
flyctl launch
flyctl secrets set BOT_TOKEN="your_token_here"
flyctl deploy
```

Done! Your bot runs 24/7 forever free.

→ **[See full Fly.io guide with all details](FLY_IO_DEPLOYMENT.md)**

---

## Option 1: RAILWAY.APP ⭐ (Alternative - Easier UI)

### Step 1: Create Free Account
1. Go to https://railway.app
2. Click "Start Project"
3. Sign up with GitHub (free)
4. Authorize Railway

### Step 2: Create New Project
1. Click "Create New Project"
2. Select "GitHub Repo"
3. Search for `DotGpt-TelegramBot`
4. Click "Deploy"

### Step 3: Add Variables
In Railway Dashboard:
1. Go to Variables tab
2. Add:
   ```
   BOT_TOKEN = your_token_from_botfather
   ADMIN_IDS = your_telegram_id
   DATABASE_URL = automatically created (PostgreSQL)
   ```

### Step 4: Add Procfile
Create `Procfile` in your repo root:
```
worker: python main.py
```

### Step 5: Deploy
1. Push code to GitHub
2. Railway auto-deploys
3. Check logs for "Bot started successfully"
4. Done! ✅

**Free Tier:** 500 hours/month (enough for 24/7 bot)  
**Cost:** FREE (limited time eval, then may require payment)

---

## Option 2: RENDER.COM (Free with limits)

### Step 1: Create Account
1. Go to https://render.com
2. Sign up with GitHub (free)

### Step 2: Create New Service
1. Dashboard → New +
2. Select "Web Service"
3. Connect your GitHub repo
4. Name: `dotgpt-bot`

### Step 3: Configuration
```
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### Step 4: Environment Variables
Add in Render dashboard:
```
BOT_TOKEN = your_token
ADMIN_IDS = your_id
DATABASE_URL = (database provided automatically)
```

### Step 5: Add Database
1. Create New → PostgreSQL
2. Connect to Web Service
3. Render auto-sets DATABASE_URL

**Free Tier:** 750 hours/month
**Cost:** FREE (with 15-minute inactivity sleep)

---

## Option 3: FLY.IO (Free with generous limits)

### Step 1: Install CLI
```bash
curl -L https://fly.io/install.sh | sh
```

### Step 2: Login & Initialize
```bash
flyctl auth login
cd DotGpt-TelegramBot
flyctl launch
```

### Step 3: Configure fly.toml
Update auto-generated `fly.toml`:
```toml
[env]
BOT_TOKEN = "your_token_here"
ADMIN_IDS = "your_id_here"

[build]
dockerfile = "Dockerfile"
```

### Step 4: Create Dockerfile
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Step 5: Deploy
```bash
flyctl deploy
```

**Free Tier:** 3 shared CPU, 256MB RAM
**Cost:** FREE

---

## Option 4: HEROKU (Paid but cheap - $7/month)

If Railway/Render don't work, Heroku is a good backup.

```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create dotgpt-bot
heroku addons:create heroku-postgresql:hobby-dev

# Add variables
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_IDS=your_id

# Deploy
git push heroku main
```

**Cost:** $7/month (database) + $7/month (dyno) = $14/month

---

## Option 5: REPLIT (Super Simple, Free)

### Step 1: Create Account
1. Go to https://replit.com
2. Sign up (free)

### Step 2: Import Project
1. Click "Create" → "Import from GitHub"
2. Paste: `https://github.com/dgit-sudo/DotGpt-TelegramBot`

### Step 3: Add Secrets
1. Click "Secrets" (🔒 icon)
2. Add:
   ```
   BOT_TOKEN = your_token
   ADMIN_IDS = your_id
   DATABASE_URL = file:///tmp/bot.db
   ```

### Step 4: Install & Run
```bash
pip install -r requirements.txt
python init_sample_data.py
python main.py
```

### Step 5: Keep Online (Free)
Use Uptime Robot to ping your Replit:
1. Go to https://uptimerobot.com (free)
2. Create monitor pointing to your Replit URL
3. Checks every 5 minutes = bot stays online

**Cost:** FREE

---

## 🎯 MY RECOMMENDATION

### For Best Free Experience:
**Use Railway.app** because:
- ✅ Easiest setup (5 minutes)
- ✅ Most generous free tier
- ✅ Auto-deploys from GitHub
- ✅ PostgreSQL included
- ✅ No sleep/downtime
- ✅ Good documentation

---

## Complete Step-by-Step for Railway (Recommended)

### Prerequisites:
1. GitHub account (free)
2. Telegram Bot Token (from @BotFather)
3. Your Telegram ID (from @userinfobot)
4. This repository

### Total Time: 10 minutes

#### Step 1: Push to GitHub
```bash
cd DotGpt-TelegramBot
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/DotGpt-TelegramBot
git push -u origin main
```

#### Step 2: Create Railway Account
1. Go to https://railway.app
2. Click "Start Project"
3. Sign up with GitHub
4. Authorize and confirm

#### Step 3: Create New Project
1. Dashboard → "Create New Project"
2. Select "Deploy from GitHub repo"
3. Find `DotGpt-TelegramBot`
4. Click "Deploy"

#### Step 4: Add PostgreSQL Database
1. In Railway dashboard click "Add"
2. Select "PostgreSQL"
3. Auto-connects to your service

#### Step 5: Configure Environment
1. Click your service
2. Go to "Variables"
3. Add:
   ```
   BOT_TOKEN=YOUR_TOKEN_FROM_BOTFATHER
   ADMIN_IDS=YOUR_TELEGRAM_ID
   ```
4. `DATABASE_URL` is auto-created

#### Step 6: Add Procfile
In your repository root, create `Procfile`:
```
worker: python main.py
```

Push to GitHub:
```bash
git add Procfile
git commit -m "Add Procfile"
git push
```

#### Step 7: Deploy
Railway auto-deploys on push. Check logs:
1. Click service
2. Click "Deployments"
3. Watch logs - should see "Bot started successfully"

**That's it! Your bot is live!** 🎉

---

## Testing Your Deployed Bot

```bash
# Find your bot's Telegram username
# Go to @BotFather, /mybots → your bot

# Send /start
# Bot should respond with language selection
```

---

## Environment Variables Explained

```
BOT_TOKEN              → Your unique bot token from @BotFather
ADMIN_IDS              → Your Telegram ID (or multiple: 123,456,789)
DATABASE_URL           → Auto-created by platform (don't change)
LOG_LEVEL              → INFO (optional)
```

---

## Common Issues & Fixes

### "Bot doesn't respond"
- Check BOT_TOKEN is correct
- Check internet connection
- Check logs in deployment platform

### "Database connection error"
- Platform auto-creates DATABASE_URL
- Don't manually set it
- Wait 5 minutes for creation

### "Logs show import error"
```bash
# Push requirements.txt
git add requirements.txt
git push
```

### "Bot offline after no activity"
- Railway: No sleep (24/7 online)
- Render: Auto-sleeps after 15 min (but restarts on request)
- Replit: Use Uptime Robot to keep alive

---

## Monitoring Your Bot

### Railway Dashboard
- Real-time logs
- Deployment history
- Resource usage
- Alerts

### Check Bot Status
```bash
# Send this to your bot channel
/admin
# Should show admin panel
```

---

## Scaling Up (If Needed)

### More Users?
- Railway: Scales automatically
- Render: Add payment method ($7+/month)
- Fly.io: Increase resources ($5+/month)

### More Database?
All free tiers include:
- PostgreSQL with good limits
- Auto-backups
- Free scaling

---

## Summary Table

| Platform | Free Tier | Setup Time | Auto-Deploy | Uptime |
|----------|-----------|-----------|------------|--------|
| Railway | 500h/mo | 5 min | Yes | 24/7 |
| Render | 750h/mo | 10 min | Yes | 15m sleep |
| Fly.io | 3 CPU | 15 min | Yes | 24/7 |
| Replit | Unlimited | 10 min | Manual | 5m sleep* |
| Heroku | $14/mo | 10 min | Yes | 24/7 |

*Use Uptime Robot to keep online

---

## Next Steps After Deployment

1. ✅ Deploy bot (done!)
2. ✅ Add admins (see ADMIN_MANAGEMENT.md)
3. ✅ Add suppliers (see ADMIN_MANAGEMENT.md)
4. ✅ Add products (through supplier interface)
5. ✅ Test with buyers

---

## Backup Your Database

For Railway/Render (auto-backup):
- Database backed up daily
- Access backups in platform dashboard

For Replit:
```bash
# Download database
# Download from sidebar
```

---

**Now Go Deploy!** 🚀

Choose Railway for easiest experience.

Questions? Check ADMIN_MANAGEMENT.md for user management.
