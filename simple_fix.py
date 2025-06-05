#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

print("Starting database fix...")

# Change to backend directory
os.chdir('/home/mirza/Desktop/instagram_puan_iskelet/backend')
print("Changed to backend directory")

# Connect to database
conn = sqlite3.connect('instagram_platform.db')
cursor = conn.cursor()
print("Connected to database")

try:
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_cmd = f"cp instagram_platform.db instagram_platform.db.backup_{timestamp}"
    os.system(backup_cmd)
    print(f"Database backed up")

    # Get current user count
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Current user count: {user_count}")

    # Create new table with proper primary key
    print("Creating new users table...")
    
    cursor.execute("""
    CREATE TABLE users_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT,
        email TEXT UNIQUE,
        email_verified INTEGER DEFAULT 0,
        email_verification_code TEXT,
        email_verification_expires INTEGER,
        two_factor_enabled INTEGER DEFAULT 0,
        two_factor_secret TEXT,
        full_name TEXT,
        profile_pic_url TEXT,
        coin_balance INTEGER DEFAULT 0,
        is_admin INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        is_admin_platform INTEGER DEFAULT 0,
        created_at INTEGER,
        updated_at INTEGER,
        last_daily_reward INTEGER,
        daily_reward_streak INTEGER DEFAULT 0,
        instagram_pk TEXT UNIQUE,
        instagram_username TEXT,
        instagram_session_data TEXT,
        first_name TEXT,
        last_name TEXT,
        phone_number TEXT,
        birth_date INTEGER,
        gender TEXT,
        country TEXT,
        city TEXT,
        timezone TEXT,
        language TEXT DEFAULT 'tr',
        last_login_at INTEGER,
        last_seen_at INTEGER,
        login_count INTEGER DEFAULT 0,
        registration_ip TEXT,
        last_login_ip TEXT,
        account_status TEXT DEFAULT 'active',
        suspension_reason TEXT,
        bio TEXT,
        website_url TEXT,
        privacy_public_profile INTEGER DEFAULT 1,
        privacy_show_email INTEGER DEFAULT 0,
        privacy_show_phone INTEGER DEFAULT 0,
        privacy_show_stats INTEGER DEFAULT 1,
        theme_preference TEXT DEFAULT 'system',
        notification_email INTEGER DEFAULT 1,
        notification_push INTEGER DEFAULT 1,
        notification_sms INTEGER DEFAULT 0,
        instagram_posts_count INTEGER DEFAULT 0,
        instagram_profile_pic_url TEXT,
        instagram_bio TEXT,
        instagram_is_private INTEGER,
        instagram_is_verified INTEGER,
        instagram_external_url TEXT,
        instagram_category TEXT,
        instagram_contact_phone TEXT,
        instagram_contact_email TEXT,
        instagram_business_category TEXT,
        instagram_connected_at INTEGER,
        instagram_last_sync INTEGER,
        instagram_sync_enabled INTEGER
    )
    """)
    print("New table created")

    # Copy data
    print("Copying user data...")
    cursor.execute("""
    INSERT INTO users_new SELECT * FROM users
    """)
    print("Data copied")

    # Replace tables
    cursor.execute("DROP TABLE users")
    cursor.execute("ALTER TABLE users_new RENAME TO users")
    print("Table replaced")

    # Create indexes
    cursor.execute("CREATE INDEX ix_users_id ON users (id)")
    cursor.execute("CREATE UNIQUE INDEX ix_users_username ON users (username)")
    cursor.execute("CREATE UNIQUE INDEX ix_users_email ON users (email)")
    cursor.execute("CREATE UNIQUE INDEX ix_users_instagram_pk ON users (instagram_pk)")
    cursor.execute("CREATE INDEX ix_users_instagram_username ON users (instagram_username)")
    print("Indexes created")

    # Test autoincrement
    cursor.execute("INSERT INTO users (username, email) VALUES ('test_user', 'test@test.com')")
    cursor.execute("SELECT id FROM users WHERE username = 'test_user'")
    test_id = cursor.fetchone()[0]
    cursor.execute("DELETE FROM users WHERE username = 'test_user'")
    print(f"Autoincrement test passed - got ID: {test_id}")

    conn.commit()
    print("All changes committed")

    # Verify final count
    cursor.execute("SELECT COUNT(*) FROM users")
    final_count = cursor.fetchone()[0]
    print(f"Final user count: {final_count}")

    print("SUCCESS: Users table fixed!")

except Exception as e:
    print(f"ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
