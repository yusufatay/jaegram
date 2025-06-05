#!/usr/bin/env python3
"""
Script to create a test user that can bypass Instagram verification for testing purposes.
This user will have mock Instagram data and can be used for immediate login testing.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models import User, InstagramCredential, InstagramProfile, SessionLocal
from passlib.context import CryptContext
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up password context (same as app.py)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    default="bcrypt",
    bcrypt__rounds=12,
    deprecated="auto"
)

def create_test_user():
    """Create a test user with mock Instagram data that bypasses verification"""
    db = SessionLocal()
    
    try:
        # Check if test user already exists
        test_user = db.query(User).filter_by(username="testuser").first()
        
        if test_user:
            logger.info("Test user already exists!")
            print(f"Test user details:")
            print(f"  Username: {test_user.username}")
            print(f"  Instagram Username: {test_user.instagram_username}")
            print(f"  Instagram PK: {test_user.instagram_pk}")
            print(f"  Coin Balance: {test_user.coin_balance}")
            print(f"  Is Active: {test_user.is_active}")
            return test_user
        
        logger.info("Creating test user...")
        
        # Create test user with mock Instagram data
        hashed_password = pwd_context.hash("testpassword123")
        test_user = User(
            username="testuser",
            password_hash=hashed_password,
            email="testuser@example.com",
            email_verified=True,  # Skip email verification
            full_name="Test User",
            profile_pic_url="https://via.placeholder.com/150",
            followers=1000,  # Mock follower count
            following=500,   # Mock following count
            coin_balance=5000,  # Give test user some coins
            is_admin=False,
            is_active=True,
            is_admin_platform=False,
            
            # Mock Instagram data - this is key for bypassing verification
            instagram_pk="12345678901",  # Mock Instagram user ID
            instagram_username="test_instagram_user",
            instagram_session_data='{"session_id": "mock_session", "csrf_token": "mock_csrf", "user_id": "12345678901"}',  # Mock session data
            
            # Set daily reward data
            last_daily_reward=None,
            daily_reward_streak=0
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create InstagramCredential record
        instagram_credential = InstagramCredential(
            user_id=test_user.id,
            instagram_user_id="12345678901",  # Same as instagram_pk
            access_token="mock_access_token_12345",
            username="test_instagram_user",
            profile_picture_url="https://via.placeholder.com/150",
            is_active=True
        )
        
        db.add(instagram_credential)
        db.commit()
        
        # Create InstagramProfile record
        instagram_profile = InstagramProfile(
            user_id=test_user.id,
            instagram_user_id="12345678901",
            username="test_instagram_user",
            bio="Test Instagram user for platform testing",
            profile_picture_url="https://via.placeholder.com/150",
            followers_count=1000,
            following_count=500,
            media_count=50,
            is_private=False,
            is_verified=False
        )
        
        db.add(instagram_profile)
        db.commit()
        
        logger.info("Test user created successfully!")
        print("\n" + "="*50)
        print("TEST USER CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"Username: {test_user.username}")
        print(f"Password: testpassword123")
        print(f"Email: {test_user.email}")
        print(f"Instagram Username: {test_user.instagram_username}")
        print(f"Instagram PK: {test_user.instagram_pk}")
        print(f"Coin Balance: {test_user.coin_balance}")
        print(f"User ID: {test_user.id}")
        print("="*50)
        print("\nThis user can now be used for testing without Instagram verification!")
        print("The user has mock Instagram data that should bypass verification checks.")
        
        return test_user
        
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

def delete_test_user():
    """Delete the test user if it exists"""
    db = SessionLocal()
    
    try:
        test_user = db.query(User).filter_by(username="testuser").first()
        
        if test_user:
            logger.info("Deleting test user...")
            db.delete(test_user)
            db.commit()
            print("Test user deleted successfully!")
        else:
            print("Test user not found!")
            
    except Exception as e:
        logger.error(f"Error deleting test user: {e}")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "delete":
        delete_test_user()
    else:
        create_test_user()
