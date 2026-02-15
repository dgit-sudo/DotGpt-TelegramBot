# 🎬 Getting Started Checklist

**Follow these exact steps to get your bot live in ~1 hour**

---

## ✅ Pre-Launch Checklist (10 minutes)

- [ ] You have a Telegram account
- [ ] You can use a code editor (VS Code, etc.)
- [ ] You have GitHub account (for easy deployment)
- [ ] You have internet connection

---

## 🔑 Step 1: Get Bot Token (5 minutes)

1. [ ] Open Telegram
2. [ ] Search for **@BotFather**
3. [ ] Send `/newbot`
4. [ ] Choose a name (e.g., "MyShopBot")
5. [ ] Choose a username (e.g., "myshopbot_bot")
6. [ ] Copy the token → **Save it somewhere safe!**
   - Looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`

---

## 🆔 Step 2: Get Your Telegram ID (3 minutes)

1. [ ] Open Telegram
2. [ ] Search for **@userinfobot**
3. [ ] Send `/start`
4. [ ] Copy your ID number → **Save it!**
   - Looks like: `123456789`

---

## 📁 Step 3: Prepare Code (5 minutes)

1. [ ] You're in `/workspaces/DotGpt-TelegramBot` folder ✅ (already done)
2. [ ] All code files are there ✅ (already done)
3. [ ] Create `.env` file with:

```
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_IDS=YOUR_TELEGRAM_ID_HERE
DATABASE_URL=sqlite:///dotgpt_bot.db
```

Replace:
- `YOUR_BOT_TOKEN_HERE` → Your token from @BotFather
- `YOUR_TELEGRAM_ID_HERE` → Your ID from @userinfobot

---

## 🌐 Step 4: Deploy on Railway (10 minutes)

**This is the easiest way to go live!**

1. [ ] Go to **railway.app**
2. [ ] Click **"Create New Project"**
3. [ ] Click **"Deploy from GitHub"**
4. [ ] Connect your GitHub account
5. [ ] Select `DotGpt-TelegramBot` repository
6. [ ] Click **"Deploy"**
7. [ ] Wait 2-3 minutes
8. [ ] When done, note your project name

### Add Environment Variables

1. [ ] In Railway, go to **"Variables"** tab
2. [ ] Click **"Add"** and add these:

```
BOT_TOKEN = your_token_from_botfather
ADMIN_IDS = your_telegram_id
DATABASE_URL = postgresql://...  (auto-filled by Railway)
```

3. [ ] Click **"Deploy"**
4. [ ] Wait 1 minute

---

## 🧪 Step 5: Test Bot (5 minutes)

1. [ ] Open Telegram
2. [ ] Find your bot (from @BotFather, click its name)
3. [ ] Send `/start`
   - You should see **language selection** ✅
4. [ ] Select language (e.g., English)
5. [ ] You should see menu with options ✅

### If Bot Doesn't Respond

- [ ] Check Railway project logs for errors
- [ ] Verify `BOT_TOKEN` is exactly copied (no spaces)
- [ ] Wait 2 more minutes
- [ ] Send `/start` again

---

## 🎮 Step 6: Become Admin (2 minutes)

1. [ ] In your Telegram bot, send `/admin`
2. [ ] You should see **Admin Panel** ✅
3. [ ] Click "System Statistics"
4. [ ] You should see numbers (users, products, chats) ✅

### If No Admin Panel

- [ ] Check that `ADMIN_IDS` matches your Telegram ID exactly
- [ ] Go back to Railway → Variables
- [ ] Edit `ADMIN_IDS` if needed
- [ ] Click "Deploy"
- [ ] Wait 1 minute
- [ ] Try `/admin` again

---

## 👥 Step 7: Test as Different Users (15 minutes)

### Test as Supplier

1. [ ] Ask a friend to text your bot (or use different device/account)
2. [ ] They send `/start`
3. [ ] They select language
4. [ ] They click **"Supplier Panel"**
5. [ ] They click **"Register as Supplier"**
6. [ ] They enter company name (e.g., "Test Company")
7. [ ] They see message: **"Waiting for admin approval"** ✅

### Approve Supplier (As Admin)

1. [ ] You send `/admin`
2. [ ] Click **"Manage Suppliers"**
3. [ ] Click their company name
4. [ ] Click **"✅ Verify Supplier"**
5. [ ] Done! They're now verified ✅

### Test as Buyer

1. [ ] Another friend/account starts bot
2. [ ] They click **"Buyer"**
3. [ ] They click **"Browse Products"**
4. [ ] They see 6 sample products ✅
5. [ ] They click a product
6. [ ] They see prices from multiple suppliers ✅
7. [ ] They click **"💬 Contact [Supplier]"**
8. [ ] They send a message
9. [ ] Supplier receives anonymous inquiry ✅

---

## 🔒 Step 8: Verify Privacy Works (5 minutes)

**Important: Make sure buyer's name is hidden from supplier**

### Supplier's View (What they see)
- They see chat messages ✅
- They see product name ✅
- They do NOT see buyer's name ❌
- They do NOT see buyer's Telegram ID ❌
- They do NOT see buyer's username ❌

### If Supplier Can See Buyer's Profile
❌ This is a bug
- Take a screenshot
- Open GitHub issue: https://github.com/YOUR_USERNAME/DotGpt-TelegramBot/issues/new
- Describe the bug

---

## 📊 Step 9: Monitor as Admin (3 minutes)

Send `/admin` and explore:

1. [ ] **👁️ View All Chats** → See buyer-supplier conversation
2. [ ] **👥 Manage Users** → Could block someone if needed
3. [ ] **🏪 Manage Suppliers** → Could verify new suppliers
4. [ ] **📊 System Statistics** → See usage metrics

---

## 🎯 Step 10: Add More Admins (2 minutes)

**Want to add a friend as admin?**

1. [ ] Get their Telegram ID (have them use @userinfobot)
2. [ ] Go to Railway → Variables
3. [ ] Change `ADMIN_IDS` from:
   ```
   123456789
   ```
   To:
   ```
   123456789,987654321,555555555
   ```
4. [ ] Click "Deploy"
5. [ ] Done! They can now use `/admin` ✅

---

## ✨ Congratulations! 🎉

Your bot is now:
- ✅ Live 24/7
- ✅ Hosting profiles of suppliers and buyers
- ✅ Processing buyer-supplier chats
- ✅ Speaking 6 languages
- ✅ Protecting buyer privacy
- ✅ Completely FREE

---

## 📈 Next: Scale Up

### Add Real Suppliers
1. Share your bot link with suppliers
2. They register through bot
3. You approve them with `/admin`
4. They add products and prices
5. They handle inquiries

### Add Real Buyers
1. Share your bot link with customers
2. They use `/start` → "Buyer" option
3. They browse products
4. They chat with suppliers
5. They buy (payment outside bot for now)

### Add Real Products
- Suppliers add through their panel, OR
- Edit `init_sample_data.py` and re-run, OR
- Use database directly (for advanced users)

---

## 🆘 Troubleshooting Quick Fix

| Problem | Fix |
|---------|-----|
| Bot doesn't respond | Check BOT_TOKEN is correct |
| No admin panel | Check ADMIN_IDS = your ID |
| Database error | Delete `dotgpt_bot.db`, run `init_sample_data.py` |
| Need to restart | Go to Railway → "More" → "Restart" |
| Lost BOT_TOKEN | Get new one from @BotFather |

---

## 📚 Need More Help?

| Question | Read This |
|----------|-----------|
| How does everything work? | [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) |
| Quick admin commands? | [ADMIN_QUICK_REFERENCE.md](ADMIN_QUICK_REFERENCE.md) |
| Detailed admin guide? | [ADMIN_MANAGEMENT.md](ADMIN_MANAGEMENT.md) |
| All features listed? | [FEATURES.md](FEATURES.md) |
| Code structure? | [DEVELOPER.md](DEVELOPER.md) |
| Different hosting? | [FREE_DEPLOYMENT.md](FREE_DEPLOYMENT.md) |

---

## ✅ Final Verification

Before you declare victory:

- [ ] Bot responds to `/start`
- [ ] You can send `/admin`
- [ ] Sample products visible to buyers
- [ ] Can approve suppliers
- [ ] Chat works between buyer-supplier
- [ ] Buyer's name hidden from supplier
- [ ] No errors in Railway logs

**All checked?** 🎉 **You're done!**

---

**Time taken: ~1 hour**

**Next**: Invite real suppliers and buyers! 🚀

---

*Questions? See documentation files or open GitHub issue*
