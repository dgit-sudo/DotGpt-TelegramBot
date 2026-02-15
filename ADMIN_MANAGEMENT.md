# 👨‍💼 Admin Management Guide

Complete guide to manage admins, suppliers, and products through the bot.

---

## 🔑 Initial Setup (After Deployment)

### Step 1: Find Your Telegram ID
1. Search for **@userinfobot** on Telegram
2. Send `/start`
3. It shows your ID (example: `123456789`)

### Step 2: Add Yourself as Admin
**Before deployment:**

Edit `.env`:
```
ADMIN_IDS=123456789
```

**After deployment (if you forgot):**

In Railway/Render dashboard:
1. Go to Variables
2. Edit `ADMIN_IDS`
3. Add your ID: `123456789`
4. Redeploy

### Step 3: Access Admin Panel
Send `/admin` to your bot
- If you see admin options → ✅ You're admin
- If you see error → ❌ Check ADMIN_IDS

---

## 👥 Adding More Admins

### Method 1: Through Bot (Easy)
**Coming Soon** - Will add command: `/make_admin @username`

For now, use Method 2:

### Method 2: Edit .env (Current Method)

**Get ID of new admin:**
1. Have them start the bot
2. They send `/start`
3. They send any message to get ID from logs
4. Or they find it with @userinfobot

**Add Admin:**

In your deployment platform (Railway/Render):
1. Go to Variables
2. Find `ADMIN_IDS`
3. Change from: `123456789`
4. Change to: `123456789,987654321,555555555`
5. Redeploy

```
ADMIN_IDS=123456789,987654321,555555555
```

**Separate multiple IDs with commas, no spaces after commas**

---

## 🏪 Adding Suppliers

### Through Bot Interface (Recommended)

#### For New User (Self-Registration)
1. New person starts bot: `/start`
2. They choose "Supplier Panel"
3. They enter company name
4. Bot notifies admins
5. Admin approves with `/admin` → "Approve Supplier"

#### For Existing User

Admin can directly promote users:
**Coming Soon** - Will add: `/make_supplier @username`

For now:
1. User sends `/start`
2. Choose "Supplier Panel"
3. Register company
4. Admin approves

---

## 🎯 Complete Admin Workflow

### Admin Gets Notified
When someone tries to register as supplier or buyer is blocked, admin gets notified automatically.

### Approving Suppliers

1. **Receive notification** (automatic)
2. **Send `/admin`** to bot
3. **Go to "Manage Suppliers"**
4. **Click pending supplier**
5. **Click "✅ Verify Supplier"**
6. **Supplier gets verified** ✅

---

## 📊 Admin Panel Full Guide

### Access Admin Panel
```
/admin
```

### Available Options:

#### 1. 👁️ View All Chats
- See every buyer-supplier conversation
- Click chat to read messages
- Monitor for abuse
- Check if supplier is helpful

#### 2. 👥 Manage Users
- **Block User:** Prevent them from using bot
- **Unblock User:** Restore access
- Reason: Report abuse, fraud, etc.

#### 3. 🏪 Manage Suppliers
- **View pending:** Suppliers awaiting approval
- **Verify:** Approve supplier to go live
- **Block:** Remove bad suppliers
- Check company info before approving

#### 4. 📊 System Statistics
- **Total Buyers:** Active customers
- **Total Suppliers:** Active vendors
- **Active Chats:** Ongoing negotiations
- **Total Products:** Items in catalog
- **Total Messages:** Communication volume

---

## 🚫 Blocking/Unblocking Users

### Why Block Users?
- Spammers
- Scammers
- Inappropriate behavior
- Fraud attempts

### How to Block
1. `/admin` → "Manage Users"
2. Find user (by ID or username)
3. Click "🚫 Block User"
4. They can't access bot anymore

### How to Unblock
1. `/admin` → "Manage Users"
2. Find user
3. Click "🔓 Unblock User"
4. They can access bot again

---

## ✅ Supplier Verification Process

### What Admins Check:
1. **Company Name** → Is it legitimate?
2. **Payment Methods** → Can they actually receive payment?
3. **Products** → Are they real items?
4. **Pricing** → Reasonable prices?

### Verification Steps
1. `/admin` → "Manage Suppliers"
2. See "⚠️ Unverified" count
3. Click supplier name
4. Review company info
5. Click "✅ Verify" if legit
6. Supplier now appears in buyer searches

### Reject Supplier
Don't verify = Auto-rejected (stays unverified)

---

## 📦 Product Management

### Add Product (Supplier)
1. Supplier sends `/supplier` (if verified)
2. Click "📦 My Products"
3. Click "➕ Add Product"
4. Enter:
   - Product name
   - Description
   - Category
5. Click "Create"

### Link Product to Supplier
Automatically done when supplier adds it.

**Multiple suppliers can sell same product** at different prices.

Example:
- Supplier A: Laptop $1000
- Supplier B: Laptop $900
- Buyer sees both options

### Set Price & Stock
1. Supplier: `/supplier`
2. "💰 Set Prices"
3. Select product
4. Enter price
5. Enter stock quantity
6. Save

### Edit Product
1. Supplier: `/supplier`
2. "📝 Manage Products"
3. Click product name
4. Edit details
5. Click "Update"

---

## 💬 Chat System & Product Linking

### How Chat Works (Privacy Protected)

#### Buyer Perspective:
1. Browse products
2. Choose product from Supplier A
3. Click "💬 Contact Supplier"
4. Chat with Supplier A about THAT product
5. Supplier never sees buyer's name/profile

#### Supplier Perspective:
1. See notification: "New inqury for Laptop"
2. Click chat
3. Chat with anonymous buyer
4. Can only see messages about Laptop
5. Can't see buyer's Telegram profile
6. Communication ONLY through bot

#### Admin Perspective:
1. `/admin` → "View All Chats"
2. See all buyer-supplier conversations
3. Can moderate if needed
4. See product being discussed

### Key Privacy Features:
- ✅ Buyer name hidden
- ✅ Buyer Telegram ID hidden
- ✅ Buyer profile hidden
- ✅ Chat is product-specific
- ✅ Communication only in bot
- ✅ Admin can see both sides

---

## 🔒 Preventing Profile Viewing

### Suppliers Cannot:
- See buyer's Telegram username
- See buyer's phone number
- See buyer's profile picture
- Know buyer's real identity
- Contact buyer outside bot
- Access buyer's telegram profile

### Only See:
- Messages in chat
- Product being discussed
- Chat ID (anonymous)

### If Supplier Tries to View Profile:
They can't - system prevents it.
They only see: "🔒 The buyer's profile is kept private for security."

---

## 📝 Audit Log (For Admins)

Track all admin actions:
- Who verified suppliers
- Who blocked users
- When actions taken
- Why users blocked

**Currently logged in bot logs**
**Future: Detailed audit dashboard**

---

## ⚡ Quick Commands

| Action | Command | Where |
|--------|---------|-------|
| Access Admin Panel | `/admin` | Any chat |
| View Chats | `/admin` → "View All Chats" | Admin panel |
| Verify Supplier | `/admin` → "Manage Suppliers" | Admin panel |
| Block User | `/admin` → "Manage Users" | Admin panel |
| Unblock User | `/admin` → "Manage Users" | Admin panel |
| See Stats | `/admin` → "Statistics" | Admin panel |

---

## 🔐 Role-Based Access

### Admin Access:
```
✅ View all chats
✅ Manage all users
✅ Verify suppliers
✅ Block/unblock users
✅ View statistics
❌ Can't be blocked
```

### Supplier Access (After Verification):
```
✅ Manage own products
✅ Set own prices
✅ View buyer inquiries
✅ Chat with buyers
✅ See payment history
❌ Can't view buyer profiles
❌ Can't contact outside bot
```

### Buyer Access:
```
✅ Browse products
✅ Compare prices
✅ Chat with suppliers
✅ View order history
❌ Can't see supplier private info
❌ Can't bypass anonymity
```

---

## 🆘 Common Admin Tasks

### Task 1: Approve New Supplier
```
1. /admin
2. "Manage Suppliers" → "Pending Verification"
3. Click supplier name
4. Review company info
5. Click "✅ Verify"
6. Done! Supplier is now active
```

### Task 2: Block Spammer
```
1. /admin
2. "Manage Users"
3. Find spam user
4. Click "🚫 Block"
5. User blocked - can't use bot
```

### Task 3: Monitor Sale
```
1. /admin
2. "View All Chats"
3. Click chat between buyer & supplier
4. Read conversation
5. Check product being sold
6. Monitor payment plan
```

### Task 4: Check System Health
```
1. /admin
2. "System Statistics"
3. See:
   - Total buyers
   - Total suppliers
   - Active negotiations
   - Total products
   - Message volume
```

---

## 📈 Multiple Admins Setup

### Add Admin #2:

1. Get their Telegram ID (from @userinfobot)
2. In your deployment platform:
   - Railway/Render: Edit Variables
3. Change:
   ```
   From: ADMIN_IDS=123456789
   To:   ADMIN_IDS=123456789,987654321
   ```
4. Redeploy
5. They can now send `/admin`

### Add Admin #3:
```
ADMIN_IDS=123456789,987654321,555555555
```

**All admins have equal access**
No hierarchy - all can verify suppliers, block users, etc.

---

## 🎯 Best Practices

### For New Suppliers:
1. ✅ Check company registration
2. ✅ Verify legitimate business
3. ✅ Check initial prices reasonable
4. ✅ Approve once verified
5. ❌ Don't approve suspicious accounts

### For Buyer-Supplier Chat:
1. ✅ Monitor for scams
2. ✅ Check payment methods legitimate
3. ✅ Remove abusive suppliers
4. ❌ Don't interfere unless necessary

### For System Security:
1. ✅ Regular audits
2. ✅ Block suspicious accounts
3. ✅ Monitor volume
4. ✅ Keep backup of database

---

## 🔄 Enable Bot-Only Chat (Enforced)

**Already Implemented:**
- Supplier can only talk through bot
- Buyer gets anonymous ID
- No way to exchange personal info in chat
- No phone numbers, emails, or social media
- System sanitizes messages

**Checked automatically** - no config needed.

---

## 📞 Support for Admins

If features don't work:
1. Check `/admin` shows
2. Verify ADMIN_IDS is set
3. Restart bot
4. Check logs for errors

---

## 🎉 You're Ready!

You now have complete control:
- ✅ Add/remove users
- ✅ Verify suppliers
- ✅ Monitor chats
- ✅ Block bad actors
- ✅ View statistics
- ✅ Ensure privacy

**Next Steps:**
1. Deploy bot
2. Add your friends as admins
3. Invite suppliers
4. Invite buyers
5. Monitor chats
6. Scale business

---

**For deployment questions:** See FREE_DEPLOYMENT.md
**For feature questions:** See FEATURES.md
