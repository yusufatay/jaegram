"""
Additional Instagram and System Endpoints
Bu dosya eksik olan tüm endpoint'leri içerir
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any
import json
import os

# Import models and dependencies
from models import User, Task, Order, CoinTransaction, OrderType, TaskStatus, SessionLocal
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT and security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

logger = logging.getLogger(__name__)

# Create router
additional_router = APIRouter()

# ==============================================================================
# EKSIK INSTAGRAM ENDPOINT'LERİ
# ==============================================================================

@additional_router.get("/instagram/profile")
async def get_instagram_profile(current_user: User = Depends(get_current_user)):
    """Get Instagram profile information"""
    try:
        profile_data = {
            "username": current_user.instagram_username or "Bağlı değil",
            "full_name": current_user.full_name or "Kullanıcı",
            "profile_pic_url": current_user.profile_pic_url or "",
            "instagram_pk": current_user.instagram_pk or "0",
            "follower_count": 1234,  # Mock data
            "following_count": 567,   # Mock data
            "is_verified": False,
            "is_connected": bool(current_user.instagram_username),
            "connection_status": "connected" if current_user.instagram_username else "disconnected",
            "last_sync": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "profile": profile_data
        }
        
    except Exception as e:
        logger.error(f"Failed to get Instagram profile: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Profile alınamadı: {str(e)}"}
        )

@additional_router.get("/instagram/connection-status")
async def get_instagram_connection_status(current_user: User = Depends(get_current_user)):
    """Get Instagram connection status"""
    try:
        is_connected = bool(current_user.instagram_username)
        
        return {
            "success": True,
            "connected": is_connected,
            "status": "connected" if is_connected else "disconnected",
            "username": current_user.instagram_username or None,
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get connection status: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Bağlantı durumu alınamadı: {str(e)}"}
        )

@additional_router.get("/instagram/posts")
async def get_instagram_posts(
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get user's Instagram posts"""
    try:
        # Mock post data for now
        mock_posts = [
            {
                "id": f"post_{i}",
                "media_url": f"https://picsum.photos/400/400?random={i}",
                "caption": f"Bu benim {i}. postum!",
                "like_count": 150 + i * 10,
                "comment_count": 25 + i * 2,
                "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "media_type": "photo"
            }
            for i in range(1, min(limit + 1, 11))
        ]
        
        return {
            "success": True,
            "posts": mock_posts,
            "count": len(mock_posts),
            "has_more": len(mock_posts) >= limit
        }
        
    except Exception as e:
        logger.error(f"Failed to get Instagram posts: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Postlar alınamadı: {str(e)}"}
        )

@additional_router.get("/instagram/analytics")
async def get_instagram_analytics(current_user: User = Depends(get_current_user)):
    """Get Instagram analytics"""
    try:
        # Mock analytics data
        analytics = {
            "engagement_rate": 4.5,
            "avg_likes": 250,
            "avg_comments": 15,
            "recent_growth": {
                "followers": 125,
                "following": 50,
                "posts": 8
            },
            "top_posts": [
                {
                    "id": "top_post_1",
                    "like_count": 500,
                    "comment_count": 45,
                    "engagement_rate": 8.2
                }
            ],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "analytics": analytics
        }
        
    except Exception as e:
        logger.error(f"Failed to get Instagram analytics: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Analytics alınamadı: {str(e)}"}
        )

@additional_router.get("/instagram/sync-errors")
async def get_instagram_sync_errors(current_user: User = Depends(get_current_user)):
    """Get Instagram sync errors"""
    try:
        # Mock error data
        errors = [
            {
                "id": 1,
                "type": "sync_error",
                "message": "Rate limit exceeded",
                "timestamp": datetime.utcnow().isoformat(),
                "resolved": False
            }
        ]
        
        return {
            "success": True,
            "errors": errors,
            "count": len(errors)
        }
        
    except Exception as e:
        logger.error(f"Failed to get sync errors: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Sync hatalar alınamadı: {str(e)}"}
        )

@additional_router.get("/instagram/account-health")
async def get_instagram_account_health(current_user: User = Depends(get_current_user)):
    """Get Instagram account health status"""
    try:
        health_status = {
            "overall_score": 85,
            "connection_stable": True,
            "rate_limit_status": "normal",
            "last_action": datetime.utcnow().isoformat(),
            "warnings": [],
            "recommendations": [
                "Düzenli olarak içerik paylaşmaya devam edin",
                "Etkileşim oranınızı artırmak için hashtag kullanın"
            ]
        }
        
        return {
            "success": True,
            "health": health_status
        }
        
    except Exception as e:
        logger.error(f"Failed to get account health: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Hesap sağlığı alınamadı: {str(e)}"}
        )

# ==============================================================================
# ÖRNEK GÖREVLER OLUŞTURMA
# ==============================================================================

def create_sample_tasks_for_users(db: Session):
    """Create sample tasks for testing"""
    try:
        # Check if sample tasks already exist
        existing_tasks = db.query(Task).filter(Task.description.like("%Örnek%")).count()
        if existing_tasks > 0:
            logger.info("Sample tasks already exist, skipping creation")
            return
        
        # Get admin user to create orders
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.warning("Admin user not found, cannot create sample tasks")
            return
        
        # Sample Instagram posts and profiles for tasks
        sample_posts = [
            "https://instagram.com/p/sample1",
            "https://instagram.com/p/sample2", 
            "https://instagram.com/p/sample3"
        ]
        
        sample_profiles = [
            "https://instagram.com/sample_user1",
            "https://instagram.com/sample_user2",
            "https://instagram.com/sample_user3"
        ]
        
        # Create sample orders and tasks
        task_types = [
            ("like", sample_posts, "Bu postu beğen"),
            ("follow", sample_profiles, "Bu hesabı takip et"),
            ("comment", sample_posts, "Bu posta yorum yap")
        ]
        
        for task_type, urls, description_template in task_types:
            for i, url in enumerate(urls, 1):
                # Create order
                order = Order(
                    creator_user_id=admin_user.id,
                    order_type=OrderType.like if task_type == "like" else 
                              OrderType.follow if task_type == "follow" else 
                              OrderType.comment,
                    post_url=url,
                    target_count=10,
                    coin_cost_per_target=1,
                    total_coin_cost=10,
                    status="active",
                    comment_text="Harika post! 👍" if task_type == "comment" else None,
                    created_at=datetime.utcnow()
                )
                db.add(order)
                db.flush()
                
                # Create multiple tasks for this order
                for task_num in range(5):
                    task = Task(
                        assigned_user_id=None,  # Unassigned
                        order_id=order.id,
                        action_type=task_type,
                        action_url=url,
                        description=f"Örnek Görev {i}-{task_num+1}: {description_template}",
                        status=TaskStatus.available,
                        coin_reward=10,
                        created_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(hours=24)
                    )
                    db.add(task)
        
        db.commit()
        logger.info("✅ Sample tasks created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create sample tasks: {e}")
        db.rollback()

@additional_router.post("/admin/create-sample-tasks")
async def create_sample_tasks_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint to create sample tasks"""
    try:
        create_sample_tasks_for_users(db)
        return {"success": True, "message": "Sample tasks created successfully"}
    except Exception as e:
        logger.error(f"Failed to create sample tasks: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Sample tasks oluşturulamadı: {str(e)}"}
        )

# ==============================================================================
# GÜNLÜK HEDİYE SİSTEMİ GELİŞTİRMESİ
# ==============================================================================

@additional_router.get("/daily-reward-info")
async def get_daily_reward_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed daily reward information"""
    try:
        # Calculate streak bonus
        streak = current_user.daily_reward_streak or 0
        base_reward = 50
        
        # Bonus calculation
        if streak >= 30:
            bonus_multiplier = 3.0
            bonus_name = "Aylık Şampiyon"
        elif streak >= 14:
            bonus_multiplier = 2.5
            bonus_name = "İki Haftalık Kahraman"
        elif streak >= 7:
            bonus_multiplier = 2.0
            bonus_name = "Haftalık Aslan"
        elif streak >= 3:
            bonus_multiplier = 1.5
            bonus_name = "Kararlı Kullanıcı"
        else:
            bonus_multiplier = 1.0
            bonus_name = "Başlangıç"
        
        total_reward = int(base_reward * bonus_multiplier)
        
        # Check if already claimed today
        from models import DailyReward
        today = datetime.utcnow().date()
        already_claimed = db.query(DailyReward).filter(
            DailyReward.user_id == current_user.id,
            DailyReward.claim_date == today
        ).first() is not None
        
        return {
            "success": True,
            "can_claim": not already_claimed,
            "already_claimed": already_claimed,
            "streak": streak,
            "base_reward": base_reward,
            "bonus_multiplier": bonus_multiplier,
            "total_reward": total_reward,
            "bonus_name": bonus_name,
            "next_milestone": 30 if streak < 30 else None,
            "days_to_next": (30 - streak) if streak < 30 else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to get daily reward info: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Günlük hediye bilgisi alınamadı: {str(e)}"}
        )

# Export router
router = additional_router
