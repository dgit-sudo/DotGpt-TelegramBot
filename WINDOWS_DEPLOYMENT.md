# 🪟 WINDOWS - Complete Telegram Bot Deployment Guide

## Your Goal: Deploy Bot & Get Public Link on Windows

This guide is **100% for Windows users**. Every step is specific to Windows.

---

## ⚡ QUICK OVERVIEW

1. **Download Fly.io for Windows** (10 min)
2. **Get Bot Token from BotFather** (5 min)
3. **Deploy Bot** (5 min)
4. **Get Public Link** (instant)
5. **Test on Telegram** (1 min)

**Total: ~25 minutes** ✅

---

## 📋 REQUIREMENTS

Before you start, you need:
- ✅ Windows 10 or Windows 11
- ✅ Internet connection
- ✅ Administrator access (for some steps)
- ✅ Telegram app installed
- ✅ Administrator command prompt (PowerShell or CMD)

---

## STEP 1: Download Fly CLI for Windows

### Option A: Using Direct Download (RECOMMENDED)

1. **Go to GitHub releases:**
   https://github.com/superfly/flyctl/releases

2. **Look for Windows version:**
   Find: `flyctl_Windows_x86_64.zip` (NOT the arm64 version)
   
   Example filename:
   ```
   flyctl_Windows_x86_64.zip
   ```

3. **Download it:**
   Click the download link and save to Downloads folder

4. **Extract the zip:**
   - Right-click: `flyctl_Windows_x86_64.zip`
   - Extract All...
   - Choose: `C:\Program Files\flyctl` (create folder if needed)
   
5. **Move the `flyctl.exe` file:**
   - Go to extracted folder
   - Find file: `flyctl.exe`
   - Copy it to: `C:\Program Files\flyctl\`
   
   **Result:** `C:\Program Files\flyctl\flyctl.exe`

### Option B: Using PowerShell (Advanced)

If you're comfortable with PowerShell:

```powershell
# Download (run in PowerShell as Administrator)
$Version = "0.1.145"  # Check latest version on GitHub
$URL = "https://github.com/superfly/flyctl/releases/download/v${Version}/flyctl_Windows_x86_64.zip"
$Output = "$env:USERPROFILE\Downloads\flyctl.zip"

Invoke-WebRequest -Uri $URL -OutFile $Output
Expand-Archive -Path $Output -DestinationPath "C:\Program Files\flyctl"
```

---

## STEP 2: Add Fly CLI to Windows PATH

This allows you to run `flyctl` from anywhere in PowerShell/CMD.

### How to Add to PATH:

1. **Open Environment Variables:**
   - Right-click: **Start Menu** → This PC
   - Click: **Properties**
   - Left sidebar: **Advanced system settings**
   - Bottom: **Environment Variables** button

2. **Edit PATH:**
   - Under "User variables" or "System variables"
   - Find: **Path**
   - Click: **Edit...**
   - Click: **New**
   - Type: `C:\Program Files\flyctl`
   - Click: **OK**
   - Click: **OK** again

3. **Restart PowerShell/CMD:**
   - Close all PowerShell and Command Prompt windows
   - Open a NEW PowerShell/CMD window
   - This loads the updated PATH

### Verify Installation:

```powershell
flyctl version
```

You should see something like:
```
flyctl v0.1.145
```

If you see "command not found" error:
- Check PATH was added correctly
- Restart your computer (sometimes needed)
- Try opening PowerShell again

---

## STEP 3: Get Bot Token from BotFather

### On Your Phone/Telegram Desktop:

1. **Open Telegram**
   - Desktop app or phone app (both work)

2. **Search for @BotFather**
   - Click magnifying glass (🔍)
   - Type: `BotFather`
   - Click first result

3. **Start BotFather:**
   - Click: **Start**
   - You'll see menu

4. **Create New Bot:**
   - Send message: `/newbot`
   - Or click: **New Bot** button if shown

5. **Name Your Bot:**
   - BotFather asks: "Alright! New bot. How are we going to call it?"
   - Type: `DotGPT Shop Bot`
   - Send

6. **Bot Username:**
   - BotFather asks: "Alright! What will be the bot's username?"
   - Type: `dotgpt_yourname_bot`
   - **IMPORTANT:** Must end with `_bot`
   - Example: `dotgpt_john_bot`
   - Send

7. **Get Token:**
   - BotFather responds with:
   ```
   Done! Congratulations on your new bot. You will find it at
   t.me/dotgpt_john_bot. You can now add a description, about
   section and profile picture for your bot, see /help for a
   list of commands.
   
   Use this token to access the HTTP API:
   123456:ABCdefGHIjklMNOpqrSTUvwxYZ123456789
   ```

8. **SAVE THE TOKEN:**
   - **VERY IMPORTANT:** Copy and save this token somewhere safe
   - Example: `123456:ABCdefGHIjklMNOpqrSTUvwxYZ123456789`
   - Save to Notepad on your computer
   - DO NOT share this token!

---

## STEP 4: Login to Fly.io

### In PowerShell or Command Prompt:

```powershell
flyctl auth signup
```

Follow the prompts:

1. **Select signup method:**
   - Type: `1` for Email
   - Press: Enter

2. **Enter email address:**
   - Type your email
   - Press: Enter

3. **Check email:**
   - Look for verification email from Fly.io
   - Click verification link

4. **Set password:**
   - Back in terminal
   - Type strong password
   - Press: Enter

5. **Confirm:**
   - You'll see: "Successfully logged in"

### Verify Login:

```powershell
flyctl auth whoami
```

You should see your email address.

---

## STEP 5: Prepare for Deployment

### Open PowerShell/CMD as Administrator:

1. **Press:** `Win + X`
2. **Click:** **Windows Terminal (Admin)** or **PowerShell (Admin)**
3. **Click:** **Yes** if prompted

### Navigate to Bot Folder:

```powershell
cd C:\Users\YourUsername\Desktop
# OR wherever DotGpt-TelegramBot folder is located
```

Example full path:
```powershell
cd C:\Users\John\Desktop\DotGpt-TelegramBot
```

### Verify You're in Right Folder:

```powershell
ls
```

You should see:
```
main.py
config.py
database.py
requirements.txt
... (other files)
```

If you don't see these files, you're in the wrong folder. Navigate to correct location.

---

## STEP 6: Create Fly App

### Run Launch Command:

```powershell
flyctl launch
```

### Answer the Prompts:

**1. "App name?"**
- Type: `dotgpt-yourname-bot` (must be unique)
- Example: `dotgpt-john-bot`
- Press: Enter

**2. "Select Organization?"**
- Usually just press: Enter (default)
- Or select your organization if shown

**3. "Select Region?"**
- Type region code nearest to you:
  - `sjc` - US West (San Francisco)
  - `ord` - US Central (Chicago)
  - `iad` - US East (Virginia)
  - `lax` - US West (Los Angeles)
  - `lhr` - Europe (London)
  - `cdg` - Europe (Paris)
  - `dfw` - US South (Dallas)
  - `ams` - Europe (Amsterdam)
  - `syd` - Australia
- Example: `sjc`
- Press: Enter

**4. "Setup Postgres?"**
- Type: `N`
- Press: Enter

**5. "Setup Redis?"**
- Type: `N`
- Press: Enter

**6. "Deploy now?"**
- Type: `N`
- Press: Enter

### Result:

You should see:
```
Created app 'dotgpt-john-bot'
Wrote config to fly.toml
```

This creates:
- `fly.toml` (configuration file)
- `.dockerignore` (Docker ignore file)

---

## STEP 7: Set Bot Token

### Run This Command:

Replace `YOUR_TOKEN_HERE` with your actual token from BotFather:

```powershell
flyctl secrets set BOT_TOKEN="YOUR_TOKEN_HERE"
```

### Example:

```powershell
flyctl secrets set BOT_TOKEN="123456:ABCdefGHIjklMNOpqrSTUvwxYZ123456789"
```

### Verify the Secret Was Set:

```powershell
flyctl secrets list
```

You should see:
```
NAME       DIGEST                             CREATED AT
BOT_TOKEN  sha256:abc123def456...            just now
```

---

## STEP 8: Deploy Your Bot

### Run Deploy:

```powershell
flyctl deploy
```

### Watch the Log:

The deployment will:
1. Build Docker image (1-2 minutes)
2. Upload to Fly.io (30 seconds)
3. Start your bot (30 seconds)

**Watch for SUCCESS message:**

```
✓ Image built successfully
✓ Pushed to registry
✓ Waiting for tasks to start
✓ Tasks are now running
...
🤖 DotGPT Bot started successfully!
```

### If There's an Error:

Check the logs:
```powershell
flyctl logs
```

Common errors:
- **Token not found:** Did you run `flyctl secrets set` command?
- **Build failed:** Is `requirements.txt` in the folder?
- **Port issue:** Bot uses port 8080 (should be fine)

---

## STEP 9: Get Your Public Link

### Your Bot Link is:

```
https://t.me/dotgpt_yourname_bot
```

Replace `dotgpt_yourname_bot` with the username you chose in BotFather.

### Example:
If your bot's username is `dotgpt_john_bot`, your link is:
```
https://t.me/dotgpt_john_bot
```

### Web Access (Optional):

Your bot also has a web URL:
```
https://dotgpt-john-bot.fly.dev
```

(Replace with your app name)

---

## STEP 10: Test Your Bot on Telegram

### On Your Phone or Telegram Desktop:

1. **Copy the link:**
   ```
   https://t.me/dotgpt_yourname_bot
   ```

2. **Paste in browser or Telegram:**
   - In Telegram: Click the link
   - In browser: Paste in address bar and press Enter

3. **Click "Open" or "Start"**

4. **See the Bot:**
   You should see:
   ```
   Welcome to DotGPT Shop Bot 🛍️
   
   Select your language / Selecciona tu idioma / ...
   
   [English] [Español] [Français] ...
   ← Previous    Page 1/15    Next →
   ```

5. **Click a Language:**
   The main menu should appear:
   ```
   πŸ'€ Browse Products
   🏪 Supplier Dashboard
   ...
   ```

✅ **BOT IS WORKING!**

---

## 🎉 SUCCESS!

Your bot is now:
- ✅ Live on Telegram
- ✅ Available 24/7
- ✅ Supporting 100+ languages
- ✅ Public link working
- ✅ Completely FREE

---

## 📝 USEFUL COMMANDS (For Later)

### Check Status:
```powershell
flyctl status
```

### View Logs:
```powershell
flyctl logs
```

### Restart Bot:
```powershell
flyctl restart
```

### Update Bot Code:

After making changes:
```powershell
flyctl deploy
```

### Update Token (If Needed):
```powershell
flyctl secrets set BOT_TOKEN="new_token"
flyctl restart
```

### Destroy App (If You Want):
```powershell
flyctl apps destroy dotgpt-john-bot
```

---

## 🆘 TROUBLESHOOTING

### "flyctl command not found"

**Solution:**
1. Check PATH was added correctly
2. Restart PowerShell
3. Or use full path: `C:\Program Files\flyctl\flyctl.exe`

### "Bot doesn't respond in Telegram"

**Solution:**
1. Check logs: `flyctl logs`
2. Restart: `flyctl restart`
3. Make sure token was set: `flyctl secrets list`

### "Token error"

**Solution:**
1. Copy token again from @BotFather
2. Run: `flyctl secrets set BOT_TOKEN="new_token"`
3. Restart: `flyctl restart`

### "Deployment failed"

**Solution:**
1. Check logs: `flyctl logs`
2. Make sure `requirements.txt` exists
3. Try again: `flyctl deploy`

### "Can't access bot link"

**Solution:**
1. Wait 1-2 minutes for bot to fully start
2. Check Telegram search for your bot
3. If still not showing, check bot is running: `flyctl status`

---

## 💾 BACKUP YOUR TOKEN

**VERY IMPORTANT:**

Save your token somewhere safe:
```
Bot Token: 123456:ABCdefGHIjklMNOpqrSTUvwxYZ123456789
Bot Username: dotgpt_john_bot
Bot Public Link: https://t.me/dotgpt_john_bot
Fly App Name: dotgpt-john-bot
Fly Public URL: https://dotgpt-john-bot.fly.dev
```

Keep this file safe. You'll need it if you redeploy.

---

## 📊 WHAT YOU GET

After deployment:

✅ **Public Telegram Bot Link:**
```
https://t.me/dotgpt_yourname_bot
```

✅ **Web URL:**
```
https://dotgpt-yourname-bot.fly.dev
```

✅ **Bot Features:**
- 100+ languages
- Real-time translation
- Buyer/Supplier system
- Admin dashboard
- Chat with privacy
- FREE forever

✅ **Your Bot is:**
- Running 24/7
- Always available
- Completely FREE
- Fully functional
- Production-ready

---

## 🎬 NEXT STEPS

1. **Share your bot link** with friends to test
2. **Experience the features** yourself
3. **Manage your bot** with Fly.io dashboard (optional)
4. **Update code** anytime with `flyctl deploy`

---

## 📞 QUICK REFERENCE

### Essential Commands:

```powershell
# First time setup
flyctl auth signup
flyctl launch
flyctl secrets set BOT_TOKEN="your_token"
flyctl deploy

# Later management
flyctl logs              # See what's happening
flyctl status            # Check if bot is running
flyctl restart           # Restart bot
flyctl deploy            # Update bot code
flyctl secrets list      # See your secrets
flyctl info              # Bot information
```

---

## ✨ YOU'RE DONE!

Your Telegram bot is now:
- 🚀 Live and public
- 💬 Responding to messages
- 🌍 Supporting 100+ languages
- 💰 Completely FREE
- ⏰ Running 24/7

**Congratulations!** 🎉

---

## 🔗 YOUR PUBLIC LINKS

**Bot Link:**
```
https://t.me/dotgpt_yourname_bot
```

**Web URL:**
```
https://dotgpt-yourname-bot.fly.dev
```

**Share these links with anyone!**
They can start using your bot immediately!

---

**Last Updated:** February 2026  
**Platform:** Windows 10/11  
**Status:** ✅ Production Ready  
**Cost:** FREE FOREVER 🚀
