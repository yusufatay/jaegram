#!/usr/bin/env python3
"""
Create a test user for testing Instagram scraping fallback functionality
"""
from models import User, SessionLocal
from passlib.context import CryptContext
from datetime import datetime

def create_test_user():
    """Create a test user with Instagram username but no connection data"""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == "testuser_scraping").first()
        if existing_user:
            print("Test user already exists. Updating Instagram username...")
            existing_user.instagram_username = "semihulusoyw"
            existing_user.instagram_session_data = None
            existing_user.instagram_connected_at = None
            db.commit()
            print(f"Updated existing user: {existing_user.username}")
            print(f"Instagram username: {existing_user.instagram_username}")
            print(f"Instagram session data: {existing_user.instagram_session_data}")
            return existing_user
        
        # Create password hash
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash("testpassword123")
        
        # Create new test user
        test_user = User(
            username="testuser_scraping",
            password_hash=password_hash,
            email="testuser@example.com",
            full_name="Test User for Scraping",
            coin_balance=100,
            is_admin=False,
            is_active=True,
            instagram_username="semihulusoyw",  # Set Instagram username
            instagram_session_data=None,  # No connection data - will trigger scraping
            instagram_connected_at=None,
            created_at=datetime.utcnow()
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("Test user created successfully!")
        print(f"Username: {test_user.username}")
        print(f"Password: testpassword123")
        print(f"Instagram username: {test_user.instagram_username}")
        print(f"Instagram session data: {test_user.instagram_session_data}")
        print(f"User ID: {test_user.id}")
        
        return test_user
        
    except Exception as e:
        db.rollback()
        print(f"Error creating test user: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
