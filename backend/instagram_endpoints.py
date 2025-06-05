"""
Eksik Instagram endpoint'leri ve işlevleri
Bu dosya app.py'ye import edilecek
"""

from fastapi import APIRouter, Depends, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

# Import models and dependencies - Avoid circular import
from models import User, Order, Task, TaskStatus, OrderType, CoinTransaction, CoinTransactionType, DailyReward, Leaderboard
# Import dependencies - these will be injected when including the router
from dependencies import get_current_user, get_db

logger = logging.getLogger(__name__)

# Create router for Instagram endpoints
instagram_router = APIRouter(prefix="/instagram", tags=["Instagram Extended"])

@instagram_router.get("/profile")
async def get_instagram_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Instagram profile information"""
    try:
        # Mock Instagram profile data - in real app this would come from Instagram API (excluding follower/following data)
        profile_data = {
            "username": getattr(current_user, 'instagram_username', 'test_user'),
            "full_name": current_user.full_name or "Test User",
            "profile_pic_url": "https://via.placeholder.com/150",
            "post_count": 156,
            "bio": "Instagram kullanıcısı 📱",
            "is_business": False,
            "is_verified": False,
            "external_url": "",
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "profile": profile_data
        }
        
    except Exception as e:
        logger.error(f"Instagram profile fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Profil bilgileri alınamadı: {str(e)}")

@instagram_router.get("/connection-status")
async def get_connection_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Instagram connection status"""
    try:
        # Check if user has Instagram credentials
        has_instagram = hasattr(current_user, 'instagram_username') and current_user.instagram_username
        
        status_data = {
            "is_connected": has_instagram,
            "username": getattr(current_user, 'instagram_username', None),
            "last_sync": datetime.now().isoformat() if has_instagram else None,
            "connection_status": "active" if has_instagram else "disconnected",
            "last_activity": datetime.now().isoformat(),
            "sync_enabled": True,
            "permissions": ["basic_info", "posts", "media"] if has_instagram else []
        }
        
        return {
            "success": True,
            "connection": status_data
        }
        
    except Exception as e:
        logger.error(f"Connection status error: {e}")
        raise HTTPException(status_code=500, detail=f"Bağlantı durumu kontrol edilemedi: {str(e)}")

@instagram_router.get("/posts")
async def get_instagram_posts(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's Instagram posts"""
    try:
        # Mock posts data - in real app this would come from Instagram API
        posts = []
        for i in range(min(limit, 10)):
            posts.append({
                "id": f"post_{i+1}",
                "media_type": "IMAGE",
                "media_url": f"https://via.placeholder.com/400x400?text=Post+{i+1}",
                "thumbnail_url": f"https://via.placeholder.com/150x150?text=Post+{i+1}",
                "caption": f"Instagram post #{i+1} 📸 #instagram #post",
                "like_count": 45 + (i * 12),
                "comment_count": 8 + (i * 2),
                "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                "permalink": f"https://www.instagram.com/p/post_{i+1}/"
            })
        
        return {
            "success": True,
            "posts": posts,
            "total_count": len(posts),
            "has_next": False
        }
        
    except Exception as e:
        logger.error(f"Posts fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Gönderiler alınamadı: {str(e)}")

@instagram_router.get("/analytics")
async def get_instagram_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Instagram analytics data"""
    try:
        # Mock analytics data
        analytics_data = {
            "total_likes": 1250,
            "total_comments": 340,
            "total_followers": 890,
            "engagement_rate": 8.5,
            "weekly_growth": {
                "followers": 15,
                "likes": 120,
                "comments": 25
            },
            "top_posts": [
                {
                    "id": "post_1",
                    "likes": 89,
                    "comments": 15,
                    "engagement": 12.5
                },
                {
                    "id": "post_2", 
                    "likes": 76,
                    "comments": 12,
                    "engagement": 10.8
                }
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "analytics": analytics_data
        }
        
    except Exception as e:
        logger.error(f"Analytics fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Analitik veriler alınamadı: {str(e)}")

@instagram_router.get("/sync-errors")
async def get_sync_errors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Instagram sync errors"""
    try:
        # Mock sync errors - in real app these would be from database
        errors = [
            {
                "id": 1,
                "error_type": "rate_limit",
                "message": "Instagram API rate limit exceeded",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "resolved": True
            },
            {
                "id": 2,
                "error_type": "auth_error",
                "message": "Instagram token expired",
                "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                "resolved": False
            }
        ]
        
        return {
            "success": True,
            "errors": errors,
            "total_errors": len(errors),
            "unresolved_count": len([e for e in errors if not e["resolved"]])
        }
        
    except Exception as e:
        logger.error(f"Sync errors fetch error: {e}")
        raise HTTPException(status_code=500, detail=f"Senkronizasyon hataları alınamadı: {str(e)}")

@instagram_router.get("/account-health")
async def get_account_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Instagram account health status"""
    try:
        # Mock health data
        health_data = {
            "overall_status": "good",
            "connection_quality": "excellent",
            "api_usage": {
                "daily_limit": 200,
                "used_today": 45,
                "remaining": 155
            },
            "last_issues": [
                {
                    "issue": "Temporary rate limit",
                    "severity": "low",
                    "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
                    "resolved": True
                }
            ],
            "recommendations": [
                "Hesap güvenlik ayarlarınızı kontrol edin",
                "İki faktörlü kimlik doğrulamayı aktive edin"
            ],
            "last_health_check": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "health": health_data
        }
        
    except Exception as e:
        logger.error(f"Account health error: {e}")
        raise HTTPException(status_code=500, detail=f"Hesap sağlığı kontrol edilemedi: {str(e)}")

# Social router for leaderboard fixes
social_router = APIRouter(prefix="/social", tags=["Social Features"])

@social_router.get("/my-rank")
async def get_my_rank(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's rank in leaderboard"""
    try:
        # Get user's total coin balance
        user_coins = current_user.coin_balance or 0
        
        # Count users with higher coin balance (rank calculation)
        higher_users = db.query(User).filter(User.coin_balance > user_coins).count()
        current_rank = higher_users + 1
        
        # Get total users for percentage calculation
        total_users = db.query(User).count()
        rank_percentage = (current_rank / total_users * 100) if total_users > 0 else 0
        
        # Get user's completed tasks count
        completed_tasks = db.query(Task).filter(
            Task.assigned_user_id == current_user.id,
            Task.status == TaskStatus.completed
        ).count()
        
        # Determine user level based on completed tasks
        if completed_tasks >= 100:
            level = "Elmas"
            level_color = "#E6E6FA"
        elif completed_tasks >= 50:
            level = "Altın"
            level_color = "#FFD700"
        elif completed_tasks >= 25:
            level = "Gümüş"
            level_color = "#C0C0C0"
        else:
            level = "Bronz"
            level_color = "#CD7F32"
        
        rank_data = {
            "current_rank": current_rank,
            "total_users": total_users,
            "rank_percentage": round(rank_percentage, 1),
            "user_coins": user_coins,
            "completed_tasks": completed_tasks,
            "level": level,
            "level_color": level_color,
            "next_level_requirement": {
                "Bronz": 25,
                "Gümüş": 50, 
                "Altın": 100,
                "Elmas": 100
            }.get(level, 100),
            "progress_to_next": min(100, (completed_tasks % 25) * 4) if level != "Elmas" else 100
        }
        
        return {
            "success": True,
            "rank": rank_data
        }
        
    except Exception as e:
        logger.error(f"Rank calculation error: {e}")
        raise HTTPException(status_code=500, detail=f"Sıralama hesaplanamadı: {str(e)}")

# Tasks router for sample tasks
tasks_router = APIRouter(prefix="/tasks", tags=["Tasks Extended"])

@tasks_router.post("/create-samples")
async def create_sample_tasks(
    count: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Create sample tasks for testing"""
    try:
        sample_tasks = []
        
        # Sample Instagram post URLs and profiles
        sample_posts = [
            "https://www.instagram.com/p/sample1/",
            "https://www.instagram.com/p/sample2/", 
            "https://www.instagram.com/p/sample3/",
            "https://www.instagram.com/p/sample4/",
            "https://www.instagram.com/p/sample5/"
        ]
        
        sample_profiles = [
            "https://www.instagram.com/sample_user1/",
            "https://www.instagram.com/sample_user2/",
            "https://www.instagram.com/sample_user3/",
            "https://www.instagram.com/sample_user4/",
            "https://www.instagram.com/sample_user5/"
        ]
        
        for i in range(count):
            # Create sample order
            order = Order(
                user_id=1,  # Admin user
                order_type=OrderType.like if i % 2 == 0 else OrderType.follow,
                post_url=sample_posts[i % len(sample_posts)] if i % 2 == 0 else sample_profiles[i % len(sample_profiles)],
                target_count=10 + (i * 5),
                coin_cost=(10 + (i * 5)) * 2,
                status="active",
                comment=f"Örnek görev #{i+1} - {'Beğeni' if i % 2 == 0 else 'Takip'} görevi",
                created_at=datetime.utcnow() - timedelta(hours=i),
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            db.add(order)
            db.flush()  # Get order ID
            
            sample_tasks.append({
                "order_id": order.id,
                "type": order.order_type.value,
                "url": order.post_url,
                "target": order.target_count,
                "reward": 10  # Default task reward
            })
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{count} örnek görev oluşturuldu",
            "tasks": sample_tasks
        }
        
    except Exception as e:
        logger.error(f"Sample tasks creation error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Örnek görevler oluşturulamadı: {str(e)}")

# Daily rewards router
rewards_router = APIRouter(prefix="/rewards", tags=["Daily Rewards"])

@rewards_router.post("/claim-daily")
async def claim_daily_reward_extended(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enhanced daily reward claiming"""
    try:
        today = datetime.utcnow().date()
        
        # Check if already claimed today
        existing_reward = db.query(DailyReward).filter(
            DailyReward.user_id == current_user.id,
            DailyReward.claimed_date == today
        ).first()
        
        if existing_reward:
            return {
                "success": False,
                "message": "Bugün zaten günlük ödül aldınız!",
                "next_claim": (datetime.combine(today, datetime.min.time()) + timedelta(days=1)).isoformat()
            }
        
        # Calculate consecutive days and reward
        yesterday = today - timedelta(days=1)
        yesterday_reward = db.query(DailyReward).filter(
            DailyReward.user_id == current_user.id,
            DailyReward.claimed_date == yesterday
        ).first()
        
        consecutive_days = (yesterday_reward.consecutive_days + 1) if yesterday_reward else 1
        
        # Progressive reward system
        base_reward = 50
        bonus_multiplier = min(consecutive_days, 7)  # Max 7x bonus
        total_reward = base_reward + (bonus_multiplier * 10)
        
        # Special weekly bonus
        if consecutive_days == 7:
            total_reward += 200  # Weekly bonus
        
        # Create reward record
        daily_reward = DailyReward(
            user_id=current_user.id,
            coin_amount=total_reward,
            consecutive_days=consecutive_days,
            claimed_date=today
        )
        db.add(daily_reward)
        
        # Update user balance
        current_user.coin_balance = (current_user.coin_balance or 0) + total_reward
        
        # Create transaction record
        transaction = CoinTransaction(
            user_id=current_user.id,
            amount=total_reward,
            type=CoinTransactionType.earn,
            note=f"Günlük ödül - {consecutive_days}. gün (Bonus: {bonus_multiplier}x)"
        )
        db.add(transaction)
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Günlük ödül alındı! +{total_reward} coin",
            "reward_amount": total_reward,
            "consecutive_days": consecutive_days,
            "next_claim": (datetime.combine(today, datetime.min.time()) + timedelta(days=1)).isoformat(),
            "bonus_info": {
                "base_reward": base_reward,
                "bonus_multiplier": bonus_multiplier,
                "weekly_bonus": 200 if consecutive_days == 7 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Daily reward claim error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Günlük ödül alınamadı: {str(e)}")

@rewards_router.get("/streak-info")
async def get_reward_streak_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily reward streak information"""
    try:
        today = datetime.utcnow().date()
        
        # Get latest reward
        latest_reward = db.query(DailyReward).filter(
            DailyReward.user_id == current_user.id
        ).order_by(desc(DailyReward.claimed_date)).first()
        
        if not latest_reward:
            return {
                "success": True,
                "current_streak": 0,
                "can_claim_today": True,
                "total_rewards": 0,
                "next_reward": 50
            }
        
        # Check if can claim today
        can_claim = latest_reward.claimed_date != today
        
        # Calculate current streak
        current_streak = 0
        if latest_reward.claimed_date == today:
            current_streak = latest_reward.consecutive_days
        elif latest_reward.claimed_date == today - timedelta(days=1):
            current_streak = latest_reward.consecutive_days
        
        # Get total rewards earned
        total_rewards = db.query(func.sum(DailyReward.coin_amount)).filter(
            DailyReward.user_id == current_user.id
        ).scalar() or 0
        
        # Calculate next reward amount
        next_streak = current_streak + 1 if can_claim else current_streak
        base_reward = 50
        bonus_multiplier = min(next_streak, 7)
        next_reward = base_reward + (bonus_multiplier * 10)
        if next_streak == 7:
            next_reward += 200
        
        return {
            "success": True,
            "current_streak": current_streak,
            "can_claim_today": can_claim,
            "total_rewards": total_rewards,
            "next_reward": next_reward,
            "streak_info": {
                "days": [
                    {"day": i+1, "reward": 50 + (min(i+1, 7) * 10) + (200 if i+1 == 7 else 0)}
                    for i in range(7)
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Streak info error: {e}")
        raise HTTPException(status_code=500, detail=f"Streak bilgileri alınamadı: {str(e)}")
