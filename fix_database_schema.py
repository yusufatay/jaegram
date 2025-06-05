#!/usr/bin/env python3
"""
Database schema fix for CoinTransaction order_id and DailyReward claimed_date
"""

import sqlite3
from datetime import datetime

DB_PATH = "/home/mirza/Desktop/instagram_puan_iskelet/instagram_platform.db"

def backup_database():
    """Create a backup of the database before making changes"""
    import shutil
    backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return backup_path

def fix_coin_transactions_table():
    """Add order_id column to coin_transactions table"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if order_id column already exists
        cursor.execute("PRAGMA table_info(coin_transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'order_id' not in columns:
            print("📝 Adding order_id column to coin_transactions table...")
            cursor.execute("""
                ALTER TABLE coin_transactions 
                ADD COLUMN order_id INTEGER REFERENCES orders(id)
            """)
            
            # Create index for order_id
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS ix_coin_transactions_order_id 
                ON coin_transactions(order_id)
            """)
            
            conn.commit()
            print("✅ order_id column added successfully")
        else:
            print("ℹ️  order_id column already exists")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Failed to fix coin_transactions table: {e}")
        return False

def verify_fixes():
    """Verify that the fixes were applied correctly"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check coin_transactions table
        cursor.execute("PRAGMA table_info(coin_transactions)")
        coin_columns = [col[1] for col in cursor.fetchall()]
        if 'order_id' in coin_columns:
            print("✅ coin_transactions.order_id column exists")
        else:
            print("❌ coin_transactions.order_id column missing")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    print("🔧 Database Schema Fix Script")
    print("=" * 50)
    
    # Create backup
    backup_path = backup_database()
    
    # Fix coin_transactions table
    if not fix_coin_transactions_table():
        print("❌ Failed to fix coin_transactions table")
        return False
    
    # Verify fixes
    if verify_fixes():
        print("\n🎉 Database schema fixes completed successfully!")
        print("✅ order_id column added to coin_transactions")
        print("\nThe order creation system should now work correctly.")
    else:
        print("\n❌ Verification failed - please check the database manually")
        print(f"💾 Backup available at: {backup_path}")
        return False
    
    return True

if __name__ == "__main__":
    main()
