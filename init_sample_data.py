#!/usr/bin/env python3
"""
Sample data initialization script for DotGPT Bot
Creates test products, suppliers and sets up initial data
"""

from database import SessionLocal, init_db, Product, Supplier, ProductPrice, SupplierPaymentMethod
from migrate_db import run_migrations
from database_helpers import get_or_create_buyer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_sample_data():
    """Initialize sample data for testing"""
    init_db()
    run_migrations()
    db = SessionLocal()
    
    try:
        # Create sample products
        logger.info("Creating sample products...")
        products_data = [
            {
                "name": "Laptop Computer",
                "description": "High-performance laptop for work and gaming",
                "category": "Electronics"
            },
            {
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse with long battery life",
                "category": "Accessories"
            },
            {
                "name": "USB-C Cable",
                "description": "Durable USB-C charging and data cable",
                "category": "Cables"
            },
            {
                "name": "Monitor 27 inch",
                "description": "4K UHD monitor with USB-C support",
                "category": "Electronics"
            },
            {
                "name": "Keyboard Mechanical",
                "description": "RGB mechanical gaming keyboard",
                "category": "Accessories"
            },
            {
                "name": "Laptop Stand",
                "description": "Adjustable aluminum laptop stand",
                "category": "Accessories"
            },
        ]
        
        products = []
        for product_data in products_data:
            product = Product(
                name=product_data["name"],
                description=product_data["description"],
                category=product_data["category"],
                active=True
            )
            db.add(product)
            products.append(product)
        
        db.commit()
        logger.info(f"✅ Created {len(products)} products")
        
        # Create sample suppliers
        logger.info("Creating sample suppliers...")
        suppliers_data = [
            {
                "telegram_id": 111111111,
                "company_name": "TechWorld Solutions",
                "username": "techworld",
                "description": "Leading technology distributor"
            },
            {
                "telegram_id": 222222222,
                "company_name": "Global Electronics",
                "username": "globelec",
                "description": "International electronics supplier"
            },
            {
                "telegram_id": 333333333,
                "company_name": "Premium Hardware",
                "username": "premiumhw",
                "description": "Premium computer hardware supplier"
            },
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            supplier = Supplier(
                telegram_id=supplier_data["telegram_id"],
                company_name=supplier_data["company_name"],
                username=supplier_data["username"],
                description=supplier_data["description"],
                verified=True,
                active=True
            )
            db.add(supplier)
            suppliers.append(supplier)
        
        db.commit()
        logger.info(f"✅ Created {len(suppliers)} suppliers")
        
        # Assign products to suppliers with pricing
        logger.info("Assigning products to suppliers...")
        pricing_data = [
            # TechWorld Solutions
            (0, 0, 1299.99, 10),
            (0, 1, 45.99, 50),
            (0, 3, 599.99, 5),
            
            # Global Electronics
            (1, 0, 1199.99, 15),
            (1, 2, 19.99, 100),
            (1, 3, 549.99, 8),
            
            # Premium Hardware
            (2, 1, 49.99, 30),
            (2, 4, 159.99, 20),
            (2, 5, 89.99, 25),
        ]
        
        for supplier_idx, product_idx, price, stock in pricing_data:
            supplier = suppliers[supplier_idx]
            product = products[product_idx]
            
            # Add product to supplier relationship
            if product not in supplier.products:
                supplier.products.append(product)
            
            # Create price entry
            product_price = ProductPrice(
                product_id=product.id,
                supplier_id=supplier.id,
                price=price,
                currency="USD",
                stock=stock
            )
            db.add(product_price)
        
        db.commit()
        logger.info("✅ Assigned products to suppliers with pricing")
        
        # Add payment methods for each supplier
        logger.info("Adding payment methods...")
        payment_methods = ["Credit Card", "Bank Transfer", "PayPal"]
        
        for supplier in suppliers:
            for method in payment_methods:
                payment = SupplierPaymentMethod(
                    supplier_id=supplier.id,
                    method_name=method,
                    details=f"Contact {supplier.company_name} for {method} details"
                )
                db.add(payment)
        
        db.commit()
        logger.info("✅ Added payment methods")
        
        # Create sample buyers
        logger.info("Creating sample buyers...")
        buyers_data = [
            (123456789, "johndoe", "John", "Doe"),
            (987654321, "jane_smith", "Jane", "Smith"),
            (555555555, "alex_jones", "Alex", "Jones"),
        ]
        
        for telegram_id, username, first_name, last_name in buyers_data:
            get_or_create_buyer(telegram_id, username, first_name, last_name)
        
        logger.info(f"✅ Created {len(buyers_data)} buyers")
        
        logger.info("\n" + "="*50)
        logger.info("✅ Sample data initialized successfully!")
        logger.info("="*50)
        
        print("\n📊 Sample Data Summary:")
        print(f"  📦 Products: {len(products)}")
        print(f"  🏪 Suppliers: {len(suppliers)}")
        print(f"  👥 Buyers: {len(buyers_data)}")
        print(f"  💳 Payment Methods: {len(suppliers) * len(payment_methods)}")
        
    except Exception as e:
        logger.error(f"❌ Error initializing sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_sample_data()
