#!/usr/bin/env python3
"""
Migration script to add is_active column to instagram_credentials table
"""

import sqlite3
import os
from pathlib import Path

def add_is_active_column():
    """Add is_active column to instagram_credentials table"""
    
    print("Starting migration...")
    
    # Database path
    db_path = Path(__file__).parent / "instagram_platform.db"
    print(f"Database path: {db_path}")
    
    if not db_path.exists():
        print(f"Database file {db_path} does not exist. Creating new database with updated schema.")
        return
    
    print("Database file exists, connecting...")
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        print("Checking current table schema...")
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(instagram_credentials)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Current columns: {columns}")
        
        if 'is_active' in columns:
            print("Column 'is_active' already exists in instagram_credentials table")
            return
        
        print("Adding 'is_active' column to instagram_credentials table...")
        
        # Add the column with default value
        cursor.execute("""
            ALTER TABLE instagram_credentials 
            ADD COLUMN is_active BOOLEAN DEFAULT 1
        """)
        
        print("Column added, updating existing records...")
        
        # Update existing records to have is_active = 1 (True)
        cursor.execute("""
            UPDATE instagram_credentials 
            SET is_active = 1 
            WHERE is_active IS NULL
        """)
        
        conn.commit()
        print("Successfully added 'is_active' column to instagram_credentials table")
        
        # Verify the change
        cursor.execute("PRAGMA table_info(instagram_credentials)")
        columns = cursor.fetchall()
        print("\nCurrent instagram_credentials table schema:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'} {'DEFAULT ' + str(col[4]) if col[4] is not None else ''}")
            
    except sqlite3.Error as e:
        print(f"Error adding column: {e}")
        conn.rollback()
    except Exception as e:
        print(f"Unexpected error: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    add_is_active_column()
    print("Migration script completed.")
