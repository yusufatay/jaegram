#!/usr/bin/env python3
"""
Database cleanup script to fix broken profile picture URLs
This script will replace all instances of 'https://example.com/test_profile.jpg' 
and other broken example.com URLs with NULL in the database.
"""

import sqlite3
import sys
import os

def cleanup_broken_urls():
    """Clean up broken URLs in the database"""
    
    # Database path
    db_path = 'backend/instagram_platform.db' if os.path.exists('backend/instagram_platform.db') else 'instagram_platform.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"🔧 Cleaning up broken URLs in database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List of broken URLs to replace
        broken_urls = [
            'https://example.com/test_profile.jpg',
            'https://example.com/test_pic.jpg',
            'https://your-cdn.com/default_avatar.png'
        ]
        
        # Track changes
        total_changes = 0
        
        # Clean up users table
        print("\n📋 Cleaning users table...")
        for broken_url in broken_urls:
            # Update profile_pic_url
            cursor.execute(
                "UPDATE users SET profile_pic_url = NULL WHERE profile_pic_url = ?",
                (broken_url,)
            )
            changes = cursor.rowcount
            if changes > 0:
                print(f"  ✅ Fixed {changes} entries in users.profile_pic_url")
                total_changes += changes
            
            # Update instagram_profile_pic_url
            cursor.execute(
                "UPDATE users SET instagram_profile_pic_url = NULL WHERE instagram_profile_pic_url = ?",
                (broken_url,)
            )
            changes = cursor.rowcount
            if changes > 0:
                print(f"  ✅ Fixed {changes} entries in users.instagram_profile_pic_url")
                total_changes += changes
        
        # Clean up instagram_credentials table
        print("\n📋 Cleaning instagram_credentials table...")
        for broken_url in broken_urls:
            cursor.execute(
                "UPDATE instagram_credentials SET profile_picture_url = NULL WHERE profile_picture_url = ?",
                (broken_url,)
            )
            changes = cursor.rowcount
            if changes > 0:
                print(f"  ✅ Fixed {changes} entries in instagram_credentials.profile_picture_url")
                total_changes += changes
        
        # Clean up instagram_profiles table
        print("\n📋 Cleaning instagram_profiles table...")
        for broken_url in broken_urls:
            cursor.execute(
                "UPDATE instagram_profiles SET profile_picture_url = NULL WHERE profile_picture_url = ?",
                (broken_url,)
            )
            changes = cursor.rowcount
            if changes > 0:
                print(f"  ✅ Fixed {changes} entries in instagram_profiles.profile_picture_url")
                total_changes += changes
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Cleanup complete! Fixed {total_changes} broken URLs in database.")
        
        # Verify cleanup
        print("\n🔍 Verifying cleanup...")
        verification_passed = True
        
        for broken_url in broken_urls:
            # Check users table
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE profile_pic_url = ? OR instagram_profile_pic_url = ?",
                (broken_url, broken_url)
            )
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  ❌ Still found {count} broken URLs in users table: {broken_url}")
                verification_passed = False
            
            # Check instagram_credentials table
            cursor.execute(
                "SELECT COUNT(*) FROM instagram_credentials WHERE profile_picture_url = ?",
                (broken_url,)
            )
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  ❌ Still found {count} broken URLs in instagram_credentials table: {broken_url}")
                verification_passed = False
            
            # Check instagram_profiles table
            cursor.execute(
                "SELECT COUNT(*) FROM instagram_profiles WHERE profile_picture_url = ?",
                (broken_url,)
            )
            count = cursor.fetchone()[0]
            if count > 0:
                print(f"  ❌ Still found {count} broken URLs in instagram_profiles table: {broken_url}")
                verification_passed = False
        
        if verification_passed:
            print("  ✅ All broken URLs successfully removed!")
        else:
            print("  ⚠️  Some broken URLs may still remain")
        
        # Show current state
        print("\n📊 Current database state:")
        cursor.execute("SELECT COUNT(*) FROM users WHERE profile_pic_url IS NOT NULL")
        users_with_pics = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE instagram_profile_pic_url IS NOT NULL")
        users_with_instagram_pics = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        print(f"  👥 Total users: {total_users}")
        print(f"  🖼️  Users with profile_pic_url: {users_with_pics}")
        print(f"  📱 Users with instagram_profile_pic_url: {users_with_instagram_pics}")
        
        conn.close()
        return verification_passed
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Database URL Cleanup Script")
    print("=" * 50)
    
    success = cleanup_broken_urls()
    
    if success:
        print("\n🎉 Cleanup completed successfully!")
        print("💡 You can now test the application - no more 404 errors for profile pictures!")
    else:
        print("\n❌ Cleanup failed. Please check the errors above.")
        sys.exit(1)
