# ⚡ Instant Deployment - Copy & Paste

## 🚀 Deploy in 5 Minutes to Fly.io

This is a pure reference sheet - just copy, paste, and fill in blanks!

---

## STEP 1: Get Token from BotFather

1. Telegram: Search `@BotFather`
2. Send: `/newbot`
3. Name: `DotGPT Shop Bot`
4. Username: `dotgpt_yourname_bot`
5. **COPY THE TOKEN** ⬅️ Save this!

Token looks like: `123456:ABCabcDEF123xyz`

---

## STEP 2: Install Fly CLI

### Mac:
```bash
brew install flyctl
```

### Linux:
```bash
curl -L https://fly.io/install.sh | sh
export PATH="/home/$USER/.fly/bin:$PATH"
```

### Windows:
1. Go: https://github.com/superfly/flyctl/releases/latest
2. Download: `flyctl_Windows_x86_64.zip`
3. Extract & add to PATH

**Test:**
```bash
flyctl version
```

---

## STEP 3: Login to Fly.io

```bash
flyctl auth signup
```

Follow prompts (email signup is easiest)

**Test:**
```bash
flyctl auth whoami
```

---

## STEP 4: Deploy

```bash
# Go to bot folder
cd /path/to/DotGpt-TelegramBot

# Launch app
flyctl launch
```

**Answers:**
- App name: `dotgpt-bot` ← or your unique name
- Region: `sjc` ← or your closest region
- Postgres: `N`
- Redis: `N`
- Deploy: `N`

---

## STEP 5: Set Bot Token

```bash
flyctl secrets set BOT_TOKEN="123456:ABCabcDEF123xyz"
```

Replace with YOUR token from BotFather!

**Verify:**
```bash
flyctl secrets list
```

---

## STEP 6: Deploy!

```bash
flyctl deploy
```

**Success message:**
```
🤖 DotGPT Bot started successfully!
```

---

## ✅ Test on Telegram

1. Open Telegram
2. Search: `@dotgpt_yourname_bot`
3. Click "Start"
4. See language selection → ✅ WORKING!

---

## 📊 Common Commands After Deploy

```bash
# View logs
flyctl logs

# Restart bot
flyctl restart

# Check status
flyctl status

# View resources
flyctl resources

# Update token (if needed)
flyctl secrets set BOT_TOKEN="new_token"
flyctl restart

# Redeploy after code changes
flyctl deploy
```

---

## 🆘 Quick Fix

Something not working?

```bash
# 1. Check status
flyctl status

# 2. View logs
flyctl logs

# 3. Restart
flyctl restart

# 4. Redeploy
flyctl deploy
```

---

## 📞 More Help

👉 **[Full Fly.io Guide](FLY_IO_DEPLOYMENT.md)**  
👉 **[Hosting Comparison](HOSTING_COMPARISON.md)**  
👉 **[Complete Setup](COMPLETE_SETUP_GUIDE.md)**

---

**That's it! Your bot is live! 🎉**
