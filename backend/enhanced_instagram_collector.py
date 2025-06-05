"""
Enhanced Instagram Data Collector Service
Comprehensive Instagram profile and data management
"""

import logging
import bs4
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired, ChallengeRequired, TwoFactorRequired,
    ClientError, UserNotFound, MediaNotFound
)

from models import (
    User, InstagramProfile, InstagramCredential, InstagramPost, 
    InstagramConnection, UserActivityLog, SessionLocal
)

# --- SCRAPING FALLBACK ---
# Legacy scraper import removed; only modern scraper is used now

logger = logging.getLogger(__name__)

class EnhancedInstagramDataCollector:
    """Enhanced Instagram data collection and profile management"""
    
    def __init__(self, db_session_maker=None):
        self.db_session_maker = db_session_maker or SessionLocal
        self.clients = {}  # Store authenticated clients by user_id
        
    async def collect_complete_user_data(self, user_id: int, client: Client = None) -> Dict[str, Any]:
        """Collect complete Instagram data for a user"""
        try:
            logger.info(f"[ENHANCED_COLLECTOR] Starting data collection for user {user_id}")
            db = self.db_session_maker()
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user or not user.instagram_username:
                logger.warning(f"[ENHANCED_COLLECTOR] No Instagram username for user {user_id}")
                return {"success": False, "message": "Instagram bağlantısı bulunamadı"}
            
            logger.info(f"[ENHANCED_COLLECTOR] Found Instagram username: {user.instagram_username}")
            
            # Get or use provided client
            if not client and user_id in self.clients:
                client = self.clients[user_id]
                logger.info(f"[ENHANCED_COLLECTOR] Using stored client for user {user_id}")
            
            if not client:
                logger.error(f"[ENHANCED_COLLECTOR] No client available for user {user_id}")
                return {"success": False, "message": "Instagram istemcisi bulunamadı"}
            
            logger.info(f"[ENHANCED_COLLECTOR] Client found, collecting profile data for {user.instagram_username}")
            
            # Collect all data - excluding connections (followers/following) as per requirement
            profile_data = await self._collect_profile_data(client, user.instagram_username)
            logger.info(f"[ENHANCED_COLLECTOR] Profile data collected: {profile_data}")
            
            posts_data = await self._collect_posts_data(client, user.instagram_username)
            logger.info(f"[ENHANCED_COLLECTOR] Posts data collected: {len(posts_data.get('posts', []))} posts")
            
            # Update database
            await self._update_user_instagram_data(db, user, profile_data)
            logger.info(f"[ENHANCED_COLLECTOR] User Instagram data updated")
            
            await self._save_posts_data(db, user_id, posts_data)
            logger.info(f"[ENHANCED_COLLECTOR] Posts data saved")
            
            # Log activity
            await self._log_user_activity(db, user_id, "instagram_data_sync", {
                "profile_updated": bool(profile_data),
                "posts_count": len(posts_data.get("posts", [])),
            })
            
            db.commit()
            db.close()
            
            logger.info(f"[ENHANCED_COLLECTOR] Successfully completed data collection for user {user_id}")
            
            return {
                "success": True,
                "message": "Instagram verileri başarıyla güncellendi",
                "data": {
                    "profile": profile_data,
                    "posts_count": len(posts_data.get("posts", [])),
                }
            }
            
        except Exception as e:
            logger.error(f"[ENHANCED_COLLECTOR] Complete data collection error for user {user_id}: {e}")
            logger.error(f"[ENHANCED_COLLECTOR] Exception type: {type(e)}")
            import traceback
            logger.error(f"[ENHANCED_COLLECTOR] Full traceback: {traceback.format_exc()}")
            return {"success": False, "message": f"Veri toplama hatası: {str(e)}"}
    
    async def _collect_profile_data(self, client: Client, username: str) -> Dict[str, Any]:
        """Collect comprehensive profile data"""
        try:
            logger.info(f"[PROFILE_COLLECT] Getting user info for {username}")
            
            # Get user info
            user_info = client.user_info_by_username(username)
            logger.info(f"[PROFILE_COLLECT] Got user info: followers={user_info.follower_count}, posts={user_info.media_count}, verified={user_info.is_verified}")
            
            profile_data = {
                "instagram_user_id": str(user_info.pk),
                "username": user_info.username,
                "full_name": user_info.full_name or "",
                "bio": user_info.biography or "",
                "profile_picture_url": str(user_info.profile_pic_url) if user_info.profile_pic_url else None,
                "followers_count": user_info.follower_count,
                "following_count": user_info.following_count,
                "media_count": user_info.media_count,
                "is_private": user_info.is_private,
                "is_verified": user_info.is_verified,
                "external_url": str(user_info.external_url) if user_info.external_url else None,
                "category": user_info.category,
                "business_category_name": getattr(user_info, 'business_category_name', None),
                "is_business_account": user_info.is_business,
                "is_professional_account": getattr(user_info, 'is_professional_account', False),
                "account_type": getattr(user_info, 'account_type', 'personal'),
                "business_phone": getattr(user_info, 'business_phone_number', None),
                "business_email": getattr(user_info, 'business_email', None),
            }

            # Check if this is a new/empty Instagram account
            is_empty_account = (
                user_info.media_count == 0 and 
                user_info.follower_count == 0 and 
                user_info.following_count == 0
            )
            
            if is_empty_account:
                logger.info(f"[PROFILE_COLLECT] Detected new/empty Instagram account: {username}")
                profile_data["account_status"] = "new_empty"
                profile_data["account_status_message"] = "Bu hesap yeni oluşturulmuş veya içerik yok"
                
                # For empty accounts, enhance with basic info we can still gather
                try:
                    # Get account creation info if available
                    account_created = getattr(user_info, 'date_joined', None)
                    if account_created:
                        profile_data["account_created"] = account_created
                        
                    logger.info(f"[PROFILE_COLLECT] Enhanced empty account data for {username}")
                except Exception as e:
                    logger.debug(f"[PROFILE_COLLECT] Could not get additional empty account info: {e}")
            else:
                profile_data["account_status"] = "active"
                profile_data["account_status_message"] = f"{user_info.media_count} gönderi, {user_info.follower_count} takipçi"
            
            logger.info(f"[PROFILE_COLLECT] Profile data prepared with {profile_data['media_count']} posts, verified={profile_data['is_verified']}, status={profile_data['account_status']}")
            
            # Try to get additional business info
            try:
                if user_info.is_business:
                    business_info = getattr(user_info, 'business_contact_method', None)
                    if business_info:
                        profile_data["business_address_json"] = json.dumps(business_info)
            except:
                pass
                
            return profile_data
            
        except Exception as e:
            logger.error(f"[PROFILE_COLLECT] Profile data collection error for {username}: {e}")
            logger.error(f"[PROFILE_COLLECT] Exception type: {type(e)}")
            import traceback
            logger.error(f"[PROFILE_COLLECT] Full traceback: {traceback.format_exc()}")
            return {}
    
    async def _collect_posts_data(self, client: Client, username: str, limit: int = 50) -> Dict[str, Any]:
        """Collect recent posts data"""
        try:
            user_id = client.user_id_from_username(username)
            medias = client.user_medias(user_id, amount=limit)
            
            posts = []
            total_likes = 0
            total_comments = 0
            
            for media in medias:
                post_data = {
                    "instagram_post_id": str(media.pk),
                    "caption": media.caption_text or "",
                    "media_type": str(media.media_type),
                    "media_url": str(media.thumbnail_url) if media.thumbnail_url else None,
                    "likes_count": media.like_count,
                    "comments_count": media.comment_count,
                    "posted_at": media.taken_at,
                    "location": str(media.location.name) if media.location else None,
                }
                
                # Extract hashtags
                if media.caption_text:
                    hashtags = [tag.strip() for tag in media.caption_text.split() if tag.startswith('#')]
                    post_data["hashtags"] = json.dumps(hashtags[:10])  # Limit to 10 hashtags
                
                posts.append(post_data)
                total_likes += media.like_count
                total_comments += media.comment_count
            
            # Calculate engagement metrics
            avg_likes = total_likes // len(posts) if posts else 0
            avg_comments = total_comments // len(posts) if posts else 0
            
            return {
                "posts": posts,
                "avg_likes_per_post": avg_likes,
                "avg_comments_per_post": avg_comments,
                "total_posts_analyzed": len(posts)
            }
            
        except Exception as e:
            logger.error(f"Posts data collection error: {e}")
            return {"posts": []}
    
    # Removed _collect_connections_data method as per requirement to not collect follower/following data
    
    async def _update_user_instagram_data(self, db: Session, user: User, profile_data: Dict[str, Any]):
        """Update user and Instagram profile data"""
        if not profile_data:
            return
        
        # Update User table Instagram fields - removed follower/following fields as per requirement
        user.instagram_posts_count = profile_data.get("media_count", 0)
        user.instagram_profile_pic_url = profile_data.get("profile_picture_url")
        user.instagram_bio = profile_data.get("bio")
        user.instagram_is_private = profile_data.get("is_private", False)
        user.instagram_is_verified = profile_data.get("is_verified", False)
        user.instagram_external_url = profile_data.get("external_url")
        user.instagram_category = profile_data.get("category")
        user.instagram_contact_phone = profile_data.get("business_phone")
        user.instagram_contact_email = profile_data.get("business_email")
        user.instagram_business_category = profile_data.get("business_category_name")
        user.instagram_last_sync = datetime.utcnow()
        
        # Update or create InstagramProfile
        instagram_profile = db.query(InstagramProfile).filter(
            InstagramProfile.user_id == user.id
        ).first()
        
        if not instagram_profile:
            instagram_profile = InstagramProfile(
                user_id=user.id,
                instagram_user_id=profile_data.get("instagram_user_id", ""),
                username=profile_data.get("username", "")
            )
            db.add(instagram_profile)
        
        # Update Instagram profile fields
        for field, value in profile_data.items():
            if hasattr(instagram_profile, field):
                setattr(instagram_profile, field, value)
        
        instagram_profile.updated_at = datetime.utcnow()
    
    async def _save_posts_data(self, db: Session, user_id: int, posts_data: Dict[str, Any]):
        """Save Instagram posts data"""
        posts = posts_data.get("posts", [])
        
        for post_data in posts:
            # Check if post already exists
            existing_post = db.query(InstagramPost).filter(
                InstagramPost.instagram_post_id == post_data["instagram_post_id"]
            ).first()
            
            if not existing_post:
                post = InstagramPost(
                    user_id=user_id,
                    **post_data
                )
                db.add(post)
            else:
                # Update engagement metrics
                existing_post.likes_count = post_data["likes_count"]
                existing_post.comments_count = post_data["comments_count"]
                existing_post.updated_at = datetime.utcnow()
        
        # Update profile engagement metrics
        instagram_profile = db.query(InstagramProfile).filter(
            InstagramProfile.user_id == user_id
        ).first()
        
        if instagram_profile:
            instagram_profile.avg_likes_per_post = posts_data.get("avg_likes_per_post", 0)
            instagram_profile.avg_comments_per_post = posts_data.get("avg_comments_per_post", 0)
    
    # Removed _save_connections_data method as per requirement to not collect follower/following data
    
    async def _log_user_activity(self, db: Session, user_id: int, activity_type: str, details: Dict[str, Any]):
        """Log user activity"""
        activity_log = UserActivityLog(
            user_id=user_id,
            activity_type=activity_type,
            activity_details=json.dumps(details),
            created_at=datetime.utcnow()
        )
        db.add(activity_log)
    
    async def sync_user_instagram_data(self, user_id: int) -> Dict[str, Any]:
        """Main function to sync all Instagram data for a user"""
        try:
            # Get client for user
            client = self.clients.get(user_id)
            if not client:
                return {"success": False, "message": "Instagram oturumu bulunamadı"}
            
            # Collect complete data
            result = await self.collect_complete_user_data(user_id, client)
            
            return result
            
        except Exception as e:
            logger.error(f"Instagram data sync error for user {user_id}: {e}")
            return {"success": False, "message": f"Senkronizasyon hatası: {str(e)}"}
    
    def store_client(self, user_id: int, client: Client):
        """Store authenticated client for user"""
        logger.info(f"[ENHANCED_COLLECTOR] Storing client for user {user_id}, client type: {type(client)}")
        self.clients[user_id] = client
        logger.info(f"[ENHANCED_COLLECTOR] Instagram client stored for user {user_id}. Total clients: {len(self.clients)}")
        logger.info(f"[ENHANCED_COLLECTOR] Current stored user_ids: {list(self.clients.keys())}")
    
    def get_client(self, user_id: int) -> Optional[Client]:
        """Get stored client for user"""
        return self.clients.get(user_id)
    
    def remove_client(self, user_id: int):
        """Remove stored client for user"""
        if user_id in self.clients:
            del self.clients[user_id]
            logger.info(f"Instagram client removed for user {user_id}")
    
    async def scrape_public_profile(self, username: str) -> dict:
        """Herkese açık Instagram profilini scraping ile çek - Modern scraper only (no legacy fallback)"""
        try:
            from modern_instagram_scraper import scrape_instagram_profile_modern
            import asyncio
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, scrape_instagram_profile_modern, username)

            if result.get("success") and result.get("profile"):
                profile = result["profile"]
                logger.info(f"[MODERN_SCRAPER] Successfully scraped {username} with modern scraper")
                return {
                    "success": True,
                    "followers_count": profile.get("followers_count", 0),
                    "following_count": profile.get("following_count", 0),
                    "profile_pic_url": profile.get("profile_pic_url", ""),
                    "full_name": profile.get("full_name", ""),
                    "bio": profile.get("bio", ""),
                    "media_count": profile.get("media_count", 0),
                    "is_private": profile.get("is_private", False),
                    "is_verified": profile.get("is_verified", False),
                    "username": profile.get("username", username)
                }
            else:
                return result
        except Exception as e:
            logger.error(f"[MODERN_SCRAPER] Scraping failed for {username}: {e}")
            return {"success": False, "message": str(e)}

# Global instance
enhanced_instagram_collector = EnhancedInstagramDataCollector()
