#!/usr/bin/env python3
"""
Script to verify the test user exists in the database with correct data.
"""

import sys
import os

print("Starting verification script...")

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)
print(f"Added to Python path: {backend_path}")

try:
    from models import User, InstagramCredential, InstagramProfile, SessionLocal
    print("Successfully imported models")
except Exception as e:
    print(f"Error importing models: {e}")
    sys.exit(1)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_test_user():
    """Verify the test user exists with correct data"""
    db = SessionLocal()
    
    try:
        # Get the test user
        test_user = db.query(User).filter_by(username="testuser").first()
        
        if not test_user:
            print("❌ Test user not found in database!")
            return False
        
        print("✅ Test user found in database!")
        print("="*50)
        print("USER DETAILS:")
        print("="*50)
        print(f"ID: {test_user.id}")
        print(f"Username: {test_user.username}")
        print(f"Email: {test_user.email}")
        print(f"Email Verified: {test_user.email_verified}")
        print(f"Full Name: {test_user.full_name}")
        print(f"Instagram PK: {test_user.instagram_pk}")
        print(f"Instagram Username: {test_user.instagram_username}")
        print(f"Coin Balance: {test_user.coin_balance}")
        print(f"Is Active: {test_user.is_active}")
        print(f"Is Admin: {test_user.is_admin}")
        print(f"Is Admin Platform: {test_user.is_admin_platform}")
        print(f"Created At: {test_user.created_at}")
        
        # Check Instagram Credential
        instagram_credential = db.query(InstagramCredential).filter_by(user_id=test_user.id).first()
        if instagram_credential:
            print("\n✅ Instagram Credential found!")
            print("="*50)
            print("INSTAGRAM CREDENTIAL DETAILS:")
            print("="*50)
            print(f"Instagram User ID: {instagram_credential.instagram_user_id}")
            print(f"Username: {instagram_credential.username}")
            print(f"Access Token: {instagram_credential.access_token[:20]}...")
            print(f"Is Active: {instagram_credential.is_active}")
            print(f"Created At: {instagram_credential.created_at}")
        else:
            print("❌ Instagram Credential not found!")
        
        # Check Instagram Profile
        instagram_profile = db.query(InstagramProfile).filter_by(user_id=test_user.id).first()
        if instagram_profile:
            print("\n✅ Instagram Profile found!")
            print("="*50)
            print("INSTAGRAM PROFILE DETAILS:")
            print("="*50)
            print(f"Instagram User ID: {instagram_profile.instagram_user_id}")
            print(f"Username: {instagram_profile.username}")
            print(f"Bio: {instagram_profile.bio}")
            print(f"Followers Count: {instagram_profile.followers_count}")
            print(f"Following Count: {instagram_profile.following_count}")
            print(f"Media Count: {instagram_profile.media_count}")
            print(f"Is Private: {instagram_profile.is_private}")
            print(f"Is Verified: {instagram_profile.is_verified}")
        else:
            print("❌ Instagram Profile not found!")
        
        print("\n" + "="*50)
        print("VERIFICATION SUMMARY:")
        print("="*50)
        
        if (test_user.instagram_pk and 
            test_user.instagram_username and 
            instagram_credential and 
            instagram_profile):
            print("✅ Test user is properly configured for testing!")
            print("✅ All Instagram data is present!")
            print("✅ User should bypass Instagram verification!")
            return True
        else:
            print("❌ Test user is missing some required data!")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying test user: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("TEST USER VERIFICATION")
    print("="*60)
    
    success = verify_test_user()
    
    print("\n" + "="*60)
    if success:
        print("✅ VERIFICATION SUCCESSFUL - Test user is ready for testing!")
    else:
        print("❌ VERIFICATION FAILED - Test user needs to be recreated!")
    print("="*60)
