#!/usr/bin/env python3
import sqlite3
import os

db_path = './backend/instagram_platform.db'
print(f"Checking database at: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables found:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check daily_rewards schema if it exists
        if any('daily_rewards' in str(table) for table in tables):
            cursor.execute('PRAGMA table_info(daily_rewards)')
            schema = cursor.fetchall()
            print("\ndaily_rewards schema:")
            for col in schema:
                print(f"  {col[1]} {col[2]}")
        else:
            print("\ndaily_rewards table not found")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Database file not found!")
