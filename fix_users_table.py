#!/usr/bin/env python3
"""
Script to manually add missing columns to the users table
"""

import sqlite3
import os

# Database path
DB_PATH = "instagram_platform.db"

# List of columns to add to users table
COLUMNS_TO_ADD = [
    ("first_name", "TEXT"),
    ("last_name", "TEXT"),
    ("phone_number", "TEXT"),
    ("birth_date", "TEXT"),
    ("gender", "TEXT"),
    ("country", "TEXT"),
    ("city", "TEXT"),
    ("timezone", "TEXT"),
    ("language", "TEXT DEFAULT 'tr'"),
    ("last_login_at", "TEXT"),
    ("last_seen_at", "TEXT"),
    ("login_count", "INTEGER DEFAULT 0"),
    ("registration_ip", "TEXT"),
    ("last_login_ip", "TEXT"),
    ("account_status", "TEXT DEFAULT 'active'"),
    ("suspension_reason", "TEXT"),
    ("bio", "TEXT"),
    ("website_url", "TEXT"),
    ("privacy_public_profile", "BOOLEAN DEFAULT 1"),
    ("privacy_show_email", "BOOLEAN DEFAULT 0"),
    ("privacy_show_phone", "BOOLEAN DEFAULT 0"),
    ("privacy_show_stats", "BOOLEAN DEFAULT 1"),
    ("theme_preference", "TEXT DEFAULT 'system'"),
    ("notification_email", "BOOLEAN DEFAULT 1"),
    ("notification_push", "BOOLEAN DEFAULT 1"),
    ("notification_sms", "BOOLEAN DEFAULT 0"),
    ("instagram_followers", "INTEGER DEFAULT 0"),
    ("instagram_following", "INTEGER DEFAULT 0"),
    ("instagram_posts_count", "INTEGER DEFAULT 0"),
    ("instagram_profile_pic_url", "TEXT"),
    ("instagram_bio", "TEXT"),
    ("instagram_is_private", "BOOLEAN DEFAULT 0"),
    ("instagram_is_verified", "BOOLEAN DEFAULT 0"),
    ("instagram_external_url", "TEXT"),
    ("instagram_category", "TEXT"),
    ("instagram_contact_phone", "TEXT"),
    ("instagram_contact_email", "TEXT"),
    ("instagram_business_category", "TEXT"),
    ("instagram_connected_at", "TEXT"),
    ("instagram_last_sync", "TEXT"),
    ("instagram_sync_enabled", "BOOLEAN DEFAULT 1")
]

def column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns

def main():
    print(f"Looking for database at: {os.path.abspath(DB_PATH)}")
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found!")
        return
    
    print(f"Database found! Connecting...")
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Adding missing columns to users table...")
    
    # Add each column if it doesn't exist
    for column_name, column_type in COLUMNS_TO_ADD:
        if not column_exists(cursor, "users", column_name):
            try:
                sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                cursor.execute(sql)
                print(f"✓ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                print(f"✗ Error adding column {column_name}: {e}")
        else:
            print(f"- Column {column_name} already exists")
    
    # Commit changes
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()
