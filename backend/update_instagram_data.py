#!/usr/bin/env python3
"""
Script to update existing users' Instagram data using the modern scraper
"""
import sys
import os
import asyncio
import logging

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from models import User, InstagramProfile
from modern_instagram_scraper import ModernInstagramScraper
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///instagram_platform.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def update_user_instagram_data():
    """Update Instagram data for all users with Instagram usernames"""
    db = SessionLocal()
    scraper = ModernInstagramScraper()
    
    try:
        # Get all users with Instagram usernames
        users_with_instagram = db.query(User).filter(
            User.instagram_username.isnot(None),
            User.instagram_username != ""
        ).all()
        
        logger.info(f"Found {len(users_with_instagram)} users with Instagram usernames")
        
        updated_count = 0
        error_count = 0
        
        for user in users_with_instagram:
            try:
                logger.info(f"Updating Instagram data for user {user.username} (@{user.instagram_username})")
                
                # Scrape latest Instagram data
                result = await scraper.scrape_profile(user.instagram_username)
                
                if result.get("success"):
                    # Update user's Instagram data
                    profile_pic_url = result.get("profile_pic_url")
                    if profile_pic_url and profile_pic_url != "https://example.com/test_profile.jpg":
                        user.instagram_profile_pic_url = profile_pic_url
                        logger.info(f"Updated profile pic for {user.username}: {profile_pic_url}")
                    
                    if result.get("posts_count") is not None:
                        user.instagram_posts_count = result["posts_count"]
                    
                    if result.get("is_verified") is not None:
                        user.instagram_is_verified = result["is_verified"]
                    
                    if result.get("is_private") is not None:
                        user.instagram_is_private = result["is_private"]
                    
                    if result.get("bio"):
                        user.instagram_bio = result["bio"]
                    
                    user.instagram_last_sync = datetime.utcnow()
                    
                    # Update or create Instagram profile entry
                    instagram_profile = db.query(InstagramProfile).filter(
                        InstagramProfile.user_id == user.id
                    ).first()
                    
                    if not instagram_profile:
                        instagram_profile = InstagramProfile(
                            user_id=user.id,
                            instagram_user_id=user.instagram_pk or "",
                            username=user.instagram_username
                        )
                        db.add(instagram_profile)
                    
                    # Update Instagram profile fields
                    instagram_profile.username = user.instagram_username
                    instagram_profile.full_name = result.get("full_name", "")
                    instagram_profile.bio = result.get("bio", "")
                    if profile_pic_url and profile_pic_url != "https://example.com/test_profile.jpg":
                        instagram_profile.profile_picture_url = profile_pic_url
                    instagram_profile.media_count = result.get("posts_count", 0)
                    instagram_profile.is_private = result.get("is_private", False)
                    instagram_profile.is_verified = result.get("is_verified", False)
                    instagram_profile.updated_at = datetime.utcnow()
                    
                    db.commit()
                    updated_count += 1
                    logger.info(f"✅ Successfully updated {user.username}")
                    
                else:
                    logger.warning(f"❌ Failed to scrape data for {user.username} (@{user.instagram_username})")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Error updating {user.username}: {e}")
                error_count += 1
                db.rollback()
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(1)
        
        logger.info(f"\n📊 Update Summary:")
        logger.info(f"✅ Successfully updated: {updated_count} users")
        logger.info(f"❌ Errors: {error_count} users")
        logger.info(f"📈 Total processed: {len(users_with_instagram)} users")
        
    except Exception as e:
        logger.error(f"Script error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting Instagram data update script...")
    asyncio.run(update_user_instagram_data())
    print("✅ Script completed!")
