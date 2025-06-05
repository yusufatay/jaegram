#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime

def migrate_instagram_profiles_table():
    """Add missing columns to instagram_profiles table"""
    
    db_path = "instagram_platform.db"
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return False
    
    # Backup the database first
    backup_name = f"instagram_platform.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.system(f"cp {db_path} {backup_name}")
    print(f"Database backed up to: {backup_name}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Get current columns
        cursor.execute("PRAGMA table_info(instagram_profiles)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # List of columns that should exist according to the model
        required_columns = [
            ('full_name', 'VARCHAR'),
            ('external_url', 'VARCHAR'),
            ('category', 'VARCHAR'),
            ('business_category_name', 'VARCHAR'),
            ('business_phone', 'VARCHAR'),
            ('business_email', 'VARCHAR'),
            ('business_address_json', 'TEXT'),
            ('is_business_account', 'BOOLEAN DEFAULT FALSE'),
            ('is_professional_account', 'BOOLEAN DEFAULT FALSE'),
            ('professional_conversion_suggested', 'BOOLEAN DEFAULT FALSE'),
            ('account_type', 'VARCHAR'),
            ('avg_likes_per_post', 'INTEGER DEFAULT 0'),
            ('avg_comments_per_post', 'INTEGER DEFAULT 0'),
            ('engagement_rate', 'VARCHAR'),
            ('post_frequency', 'VARCHAR'),
            ('most_active_time', 'VARCHAR'),
            ('most_active_day', 'VARCHAR'),
            ('most_used_hashtags', 'TEXT'),
            ('content_categories', 'TEXT'),
            ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
        ]
        
        # Add missing columns
        added_columns = []
        for column_name, column_type in required_columns:
            if column_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE instagram_profiles ADD COLUMN {column_name} {column_type}")
                    added_columns.append(column_name)
                    print(f"Added column: {column_name}")
                except Exception as e:
                    print(f"Error adding column {column_name}: {e}")
        
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(instagram_profiles)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"\nAll columns after migration: {new_columns}")
        print(f"Successfully added {len(added_columns)} columns: {added_columns}")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting instagram_profiles table migration...")
    success = migrate_instagram_profiles_table()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
