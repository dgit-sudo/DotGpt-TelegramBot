# 🎯 Quick Admin Reference Card

**Print this or bookmark it** for quick command lookup while administering your bot.

---

## ⚡ Essential Commands (Copy-Paste)

```
/admin           → Open admin panel
/start           → Show language selection (test command)
/supplier        → Open supplier panel (test as supplier)
/buyer           → Open buyer panel (test as buyer)
```

---

## 🔑 Admin Panel Navigation

```
/admin
├─ 👁️  View All Chats           → See all conversations
├─ 👥 Manage Users              → Block/unblock buyers only
├─ 🏪 Manage Suppliers          → Verify/block suppliers only  
└─ 📊 System Statistics         → See usage metrics
```

---

## ✅ Admin Quick Tasks

| Task | Steps | Time |
|------|-------|------|
| **Approve supplier** | `/admin` → Manage Suppliers → Select pending → ✅ Verify | 30s |
| **Block bad user** | `/admin` → Manage Users → Find user → Block | 20s |
| **See all chats** | `/admin` → View All Chats → Click chat | 10s |
| **Check stats** | `/admin` → Statistics | 10s |
| **Read message** | `/admin` → View Chats → Click chat → Read | 30s |

---

## 🔒 Admin Superpowers

Can do:
- ✅ See any chat (buyer name hidden)
- ✅ See user IDs
- ✅ Block/unblock users
- ✅ Verify suppliers
- ✅ View statistics
- ✅ Monitor payouts

Cannot do:
- ❌ Access buyer's Telegram profile
- ❌ Message users directly
- ❌ Edit products (supplier feature)
- ❌ Set prices (supplier feature)

---

## 🚀 First-Time Setup Checklist

- [ ] 1. Bot Token from @BotFather
- [ ] 2. Your Telegram ID from @userinfobot  
- [ ] 3. Set ADMIN_IDS in .env to your ID
- [ ] 4. Deploy on Railway/Render/Fly.io
- [ ] 5. Send `/start` to test
- [ ] 6. Send `/admin` to verify admin access
- [ ] 7. Test `/admin` → Statistics
- [ ] 8. Invite test supplier
- [ ] 9. Verify supplier with `/admin`
- [ ] 10. Invite test buyer
- [ ] 11. Have buyer contact supplier
- [ ] 12. Check privacy works (buyer name hidden)

---

## 📊 Dashboard Overview (What You See in Statistics)

```
System Statistics:
├─ Total Buyers        : 5      (number of registered buyers)
├─ Total Suppliers     : 3      (number of registered suppliers)
├─ Active Chats        : 8      (ongoing negotiations)
├─ Total Products      : 6      (items in catalog)
└─ Total Messages      : 147    (lifetime messages sent)
```

---

## 🆘 Emergency Buttons

### If Bot Offline
1. Go to **railway.app**
2. Find your project
3. Click **"Restart"**
4. Wait 1 minute
5. Try bot again

### If Variables Wrong
1. Go to **railway.app**
2. Click **"Variables"**
3. Fix `BOT_TOKEN` or `ADMIN_IDS`
4. Click **"Deploy"**
5. Wait 1 minute

### If Database Down
1. Check **"Plugins"** on Railway
2. Should see **PostgreSQL** ✅
3. If missing: Click **"Create"** PostgreSQL
4. Database auto-restores

---

## 🛡️ Privacy Checklist (Automatic)

Your bot automatically:

- ✅ Hides buyer name from supplier ← Automatic
- ✅ Hides buyer username ← Automatic
- ✅ Hides buyer Telegram ID ← Automatic
- ✅ Shows only chat messages to supplier ← Automatic
- ✅ Prevents external Telegram contact ← Automatic
- ✅ Allows admin to see both sides ← Automatic for moderation

**Nothing to configure** - built-in security.

---

## 💼 Adding New Admin

### Quick Steps:

1. Get friend's Telegram ID (have them use @userinfobot)
2. Go to Railway → Variables
3. Change `ADMIN_IDS` from:
   ```
   123456789
   ```
   To:
   ```
   123456789,987654321
   ```
4. Click Deploy
5. Done! They can now use `/admin`

---

## 📱 Test Bot (All Roles)

### Test as Admin
```
/start
→ Select language
→ Click Admin button
→ See /admin panel options ✅
```

### Test as Supplier
```
/start (from different phone/account)
→ Select language
→ Click Supplier
→ Click "Register as Supplier"
→ Enter company name
→ See "Waiting for approval" message ✅
```

### Test as Buyer
```
/start (from another device)
→ Select language
→ Click Buyer
→ Click "Browse Products"
→ See 6 sample products ✅
```

---

## 🎯 Supervision Checklist (Daily)

**Morning (5 min check):**
- [ ] Send `/admin` → Works? ✅
- [ ] Click "Statistics" → Any errors? ❌
- [ ] Any new pending suppliers? → Approve if legit
- [ ] System running? (if offline last night)

**During Day (if emails/alerts):**
- [ ] Dispute between buyer-supplier? → View chat
- [ ] Abuse reported? → Click Manage Users → Block
- [ ] Scam suspected? → Block supplier

**Evening (5 min summary):**
- [ ] Check total messages per day (growth indicator)
- [ ] Any crashes in logs? (Railway → Logs)
- [ ] Database size still ok? (Railway → Plugins)

---

## 🔗 Never Share These

```
❌ BOT_TOKEN        - Keep secret in .env
❌ DATABASE_URL     - Keep secret in .env
✅ ADMIN_IDS        - OK to publish (just Telegram IDs)
✅ Bot username     - Public (@YourBotName)
```

---

## 📞 Quick Support Tips

### Bot Won't Start
- Check BOT_TOKEN is correct and inside quotes
- Restart on Railway (More → Restart)
- Check Railway logs for error messages

### Admin Panel Missing
- Check ADMIN_IDS matches your Telegram ID exactly
- No spaces: `123456789` not `123456789 `
- Redeploy after changing variables

### Database Won't Work
- Railway auto-creates PostgreSQL - check "Plugins"
- DATABASE_URL should be auto-filled
- Never delete the PostgreSQL plugin

### Buyer Sees Supplier's Name
- This is CORRECT - buyer should know supplier name
- Privacy means buyer's name hidden FROM supplier
- Turn this way: Buyer → Supplier (name shown)
- Not reverse: Supplier → Buyer (name hidden) ✓

---

## 🎓 Learning Path

**Stage 1: Deploy (40 min)**
- Create GitHub repo
- Deploy on Railway
- Test `/start`

**Stage 2: Admin Basic (30 min)**
- Send `/admin`
- Invite test supplier
- Verify supplier
- Invite test buyer

**Stage 3: Production (1 day)**
- Invite real suppliers
- Invite real buyers
- Monitor chats
- Handle disputes

**Stage 4: Scale (ongoing)**
- Add more admins
- Add more products
- Monitor statistics
- Optimize pricing

---

## 📚 Full Docs Location

- **COMPLETE_SETUP_GUIDE.md** - Step-by-step deployment
- **ADMIN_MANAGEMENT.md** - Advanced admin features
- **FEATURES.md** - All bot features
- **FREE_DEPLOYMENT.md** - All free hosting options

---

## ✨ One-Minute Summary

```
Admin's job:
1. Approve suppliers ✅
2. Block bad users ✅
3. Monitor chats ✅
4. Check statistics ✅
5. Respond to issues ✅

Everything else = Automatic ✅
```

👑 **You're the boss. The bot does the work.**

---

**Bookmark this page for quick lookup!**
