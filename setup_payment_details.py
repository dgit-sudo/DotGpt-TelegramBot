#!/usr/bin/env python3
"""
Setup payment details in the database
Run this script once to configure all payment methods
"""

import sys
sys.path.insert(0, '/workspaces/DotGpt-TelegramBot')

from database import init_db
from database_helpers import set_payment_details

# Initialize database
init_db()

# Payment details in a structured format
payment_details = {
    "methods": [
        {
            "name": "Binance ID",
            "details": "822706871",
            "type": "crypto"
        },
        {
            "name": "Binance P2P/UPI",
            "details": "UQBZJStS9Pam2kAmBGfyLPyLlBMeyLALiNrAShaUIZxlQv1S",
            "type": "crypto"
        },
        {
            "name": "TON Wallet",
            "details": "0x59a820d6d0893cf222eadcb0441b2f6e33d84481",
            "type": "crypto"
        },
        {
            "name": "BEP20 Wallet",
            "details": "(Binance Smart Chain) 0x59a820d6d0893cf222eadcb0441b2f6e33d84481",
            "type": "crypto"
        },
        {
            "name": "Indonesia - SeaBank",
            "details": "901790751710 (A.N: HN)",
            "type": "bank"
        },
        {
            "name": "Iran - Card",
            "details": "6219861989001408 (Mr. Aliyari)",
            "type": "card"
        },
        {
            "name": "India - UPI",
            "details": "+918140760999",
            "type": "upi"
        },
        {
            "name": "Bangladesh - bKash",
            "details": "01619940361",
            "instructions": "Dial *247# or open bKash app → Send Money → Enter number → Enter amount → Confirm with PIN → Send screenshot",
            "type": "mobile_money"
        }
    ],
    "note": "For other local payment methods, sellers should contact admin"
}

# Format as readable string for display
formatted_details = """
💳 **PAYMENT METHODS - Pay to EXACTLY these details only** 💳

🪙 **CRYPTOCURRENCY:**
├─ Binance ID: 822706871
├─ Binance P2P: UQBZJStS9Pam2kAmBGfyLPyLlBMeyLALiNrAShaUIZxlQv1S
├─ TON Wallet: 0x59a820d6d0893cf222eadcb0441b2f6e33d84481
└─ BEP20 (BSC): 0x59a820d6d0893cf222eadcb0441b2f6e33d84481

🏦 **BANK TRANSFERS:**
└─ Indonesia SeaBank: 901790751710 (A.N: HN)

💳 **CARDS:**
└─ Iran: 6219861989001408 (Mr. Aliyari)

📱 **MOBILE PAYMENTS:**
├─ India UPI: +918140760999
└─ Bangladesh bKash: 01619940361
   (Dial *247# → Send Money → 01619940361 → Confirm PIN → Send screenshot)

⚠️ **IMPORTANT:** Send payment screenshot as proof to the seller!

For other local payment methods, contact admin at support.
"""

instructions = """
1. Pay EXACTLY to one of the methods above
2. Send a screenshot of payment confirmation to the seller
3. The seller will review your proof
4. Admin will verify and confirm the transaction
5. Stock will be reduced only after admin approval

⚠️ WARNING: Pay only to the methods listed above!
Do not trust any other payment details provided in chat.
"""

# Store in database
print("🔧 Setting up payment details...")
try:
    payment_record = set_payment_details(
        payment_method="multiple_global",
        details=str(payment_details),  # Store structured data as string
        instructions=formatted_details  # Store formatted display string
    )
    print(f"✅ Payment details configured successfully!")
    print(f"📋 Payment record ID: {payment_record.id}")
    print("\n📝 Payment details will be displayed to buyers when they view products:")
    print(formatted_details)
except Exception as e:
    print(f"❌ Error setting up payment details: {e}")
    sys.exit(1)

print("\n✨ Setup complete! Buyers will now see these payment details before entering seller chat.")
