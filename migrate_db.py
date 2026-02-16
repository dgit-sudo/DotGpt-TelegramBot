"""
Database migration script to add new columns to existing tables.
This handles schema changes when new columns are added to models.
"""

from sqlalchemy import inspect, text
from database import engine

def migrate_supplier_table():
    """Add status and is_banned columns to suppliers table if they don't exist"""
    inspector = inspect(engine)
    
    if 'suppliers' not in inspector.get_table_names():
        print("suppliers table not found - will be created by init_db()")
        return
    
    columns = {col['name'] for col in inspector.get_columns('suppliers')}
    
    with engine.connect() as conn:
        # Add status column if missing
        if 'status' not in columns:
            print("Adding 'status' column to suppliers table...")
            try:
                conn.execute(text("""
                    ALTER TABLE suppliers ADD COLUMN status VARCHAR(20) DEFAULT 'pending'
                """))
                conn.commit()
                print("✓ Added 'status' column")
            except Exception as e:
                print(f"Error adding status column: {e}")
                conn.rollback()
        
        # Add is_banned column if missing
        if 'is_banned' not in columns:
            print("Adding 'is_banned' column to suppliers table...")
            try:
                conn.execute(text("""
                    ALTER TABLE suppliers ADD COLUMN is_banned BOOLEAN DEFAULT 0
                """))
                conn.commit()
                print("✓ Added 'is_banned' column")
            except Exception as e:
                print(f"Error adding is_banned column: {e}")
                conn.rollback()

        if 'terms_accepted' not in columns:
            print("Adding 'terms_accepted' column to suppliers table...")
            try:
                conn.execute(text("""
                    ALTER TABLE suppliers ADD COLUMN terms_accepted BOOLEAN DEFAULT 0
                """))
                conn.commit()
                print("✓ Added 'terms_accepted' column")
            except Exception as e:
                print(f"Error adding terms_accepted column: {e}")
                conn.rollback()

        if 'terms_accepted_at' not in columns:
            print("Adding 'terms_accepted_at' column to suppliers table...")
            try:
                conn.execute(text("""
                    ALTER TABLE suppliers ADD COLUMN terms_accepted_at DATETIME
                """))
                conn.commit()
                print("✓ Added 'terms_accepted_at' column")
            except Exception as e:
                print(f"Error adding terms_accepted_at column: {e}")
                conn.rollback()

        if 'auto_translate' not in columns:
            print("Adding 'auto_translate' column to suppliers table...")
            try:
                conn.execute(text("""
                    ALTER TABLE suppliers ADD COLUMN auto_translate BOOLEAN DEFAULT 1
                """))
                conn.commit()
                print("✓ Added 'auto_translate' column")
            except Exception as e:
                print(f"Error adding auto_translate column: {e}")
                conn.rollback()

        if 'language' not in columns:
            print("Adding 'language' column to suppliers table...")
            try:
                conn.execute(text("""
                    ALTER TABLE suppliers ADD COLUMN language VARCHAR(10) DEFAULT 'en'
                """))
                conn.commit()
                print("✓ Added 'language' column")
            except Exception as e:
                print(f"Error adding language column: {e}")
                conn.rollback()

def migrate_buyer_table():
    """Add terms acceptance columns to buyers table if they don't exist"""
    inspector = inspect(engine)

    if 'buyers' not in inspector.get_table_names():
        print("buyers table not found - will be created by init_db()")
        return

    columns = {col['name'] for col in inspector.get_columns('buyers')}

    with engine.connect() as conn:
        if 'terms_accepted' not in columns:
            print("Adding 'terms_accepted' column to buyers table...")
            try:
                conn.execute(text("""
                    ALTER TABLE buyers ADD COLUMN terms_accepted BOOLEAN DEFAULT 0
                """))
                conn.commit()
                print("✓ Added 'terms_accepted' column")
            except Exception as e:
                print(f"Error adding terms_accepted column: {e}")
                conn.rollback()

        if 'terms_accepted_at' not in columns:
            print("Adding 'terms_accepted_at' column to buyers table...")
            try:
                conn.execute(text("""
                    ALTER TABLE buyers ADD COLUMN terms_accepted_at DATETIME
                """))
                conn.commit()
                print("✓ Added 'terms_accepted_at' column")
            except Exception as e:
                print(f"Error adding terms_accepted_at column: {e}")
                conn.rollback()

def run_migrations():
    """Run all database migrations"""
    print("Running database migrations...")
    migrate_supplier_table()
    migrate_buyer_table()
    print("Database migrations complete!")

if __name__ == "__main__":
    run_migrations()
