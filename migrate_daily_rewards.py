#!/usr/bin/env python3
"""
Database migration script to fix daily_rewards table schema mismatch.
Changes:
- coins_awarded -> coin_amount
- streak_day -> consecutive_days
"""

import sqlite3
import os
from datetime import datetime

def migrate_daily_rewards_table():
    """Migrate daily_rewards table to match the model expectations"""
    db_path = './backend/instagram_platform.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Daily Rewards Table Migration ===")
        print(f"Starting migration at {datetime.now()}")
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_rewards'")
        if not cursor.fetchone():
            print("daily_rewards table doesn't exist. Nothing to migrate.")
            return True
        
        # Get current schema
        cursor.execute('PRAGMA table_info(daily_rewards)')
        current_schema = cursor.fetchall()
        print("\nCurrent schema:")
        for col in current_schema:
            print(f"  {col[1]} {col[2]}")
        
        # Check if migration is needed
        column_names = [col[1] for col in current_schema]
        needs_migration = 'coins_awarded' in column_names or 'streak_day' in column_names
        
        if not needs_migration:
            print("\nMigration not needed - table already has correct schema!")
            return True
        
        print("\nMigration needed - renaming columns...")
        
        # Step 1: Create a new table with the correct schema
        cursor.execute('''
            CREATE TABLE daily_rewards_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                reward_date DATETIME,
                coin_amount INTEGER NOT NULL DEFAULT 0,
                consecutive_days INTEGER,
                created_at DATETIME,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✓ Created new table with correct schema")
        
        # Step 2: Copy data from old table to new table
        cursor.execute('''
            INSERT INTO daily_rewards_new (id, user_id, reward_date, coin_amount, consecutive_days, created_at)
            SELECT id, user_id, reward_date, 
                   COALESCE(coins_awarded, 0) as coin_amount,
                   streak_day as consecutive_days,
                   created_at
            FROM daily_rewards
        ''')
        
        # Get count of migrated records
        cursor.execute('SELECT COUNT(*) FROM daily_rewards_new')
        migrated_count = cursor.fetchone()[0]
        print(f"✓ Migrated {migrated_count} records")
        
        # Step 3: Drop the old table
        cursor.execute('DROP TABLE daily_rewards')
        print("✓ Dropped old table")
        
        # Step 4: Rename the new table
        cursor.execute('ALTER TABLE daily_rewards_new RENAME TO daily_rewards')
        print("✓ Renamed new table to daily_rewards")
        
        # Commit the changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Verify the new schema
        cursor.execute('PRAGMA table_info(daily_rewards)')
        new_schema = cursor.fetchall()
        print("\nNew schema:")
        for col in new_schema:
            print(f"  {col[1]} {col[2]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_daily_rewards_table()
    if success:
        print("\n🎉 Database migration completed successfully!")
        print("The daily_rewards table now matches the model expectations.")
    else:
        print("\n💥 Migration failed! Please check the error messages above.")
