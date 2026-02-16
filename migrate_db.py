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

def run_migrations():
    """Run all database migrations"""
    print("Running database migrations...")
    migrate_supplier_table()
    print("Database migrations complete!")

if __name__ == "__main__":
    run_migrations()
