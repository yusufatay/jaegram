"""
Enhanced Badge System for Instagram Platform
- Comprehensive badge categories and types
- Automatic badge awarding system
- Progress tracking and notifications
- Admin management interface
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
# models modülünü doğrudan içe aktaralım
import models
from models import (
    User, Badge, UserBadge, Task, TaskStatus, Order, # OrderStatus buradan kaldırıldı
    CoinTransaction, CoinTransactionType
)
# OrderStatus'ı models.<name> olarak kullanacağız

from enhanced_notifications import NotificationService, NotificationType, NotificationPriority

logger = logging.getLogger(__name__)

class BadgeCategory:
    """Badge category constants"""
    STARTER = "starter"          # Yeni başlayan rozetleri
    BRONZE = "bronze"           # Bronz seviye rozetler
    SILVER = "silver"           # Gümüş seviye rozetler
    GOLD = "gold"              # Altın seviye rozetler
    PLATINUM = "platinum"       # Platin seviye rozetler
    DIAMOND = "diamond"         # Elmas seviye rozetler
    INSTAGRAM = "instagram"     # Instagram ile ilgili rozetler
    ACHIEVEMENT = "achievement" # Genel başarı rozetleri
    SPECIAL = "special"         # Özel rozetler
    SEASONAL = "seasonal"       # Mevsimlik rozetler
    MILESTONE = "milestone"     # Kilometre taşı rozetleri
    SOCIAL = "social"          # Sosyal aktivite rozetleri
    LOYALTY = "loyalty"        # Sadakat rozetleri
    EXPERT = "expert"          # Uzman seviye rozetler

class BadgeType:
    """Badge type constants for requirements"""
    TASK_COMPLETION = "task_completion"
    COIN_EARNED = "coin_earned"
    COIN_SPENT = "coin_spent"
    ORDER_COMPLETION = "order_completion"
    DAILY_LOGIN = "daily_login"
    INSTAGRAM_CONNECTION = "instagram_connection"
    INSTAGRAM_FOLLOWERS = "instagram_followers"
    INSTAGRAM_POSTS = "instagram_posts"
    REFERRAL_COUNT = "referral_count"
    STREAK_DAYS = "streak_days"
    PLATFORM_USAGE = "platform_usage"
    COMMUNITY_PARTICIPATION = "community_participation"

class EnhancedBadgeSystem:
    """Enhanced badge management and awarding system"""
    
    def __init__(self, db_session_factory, notification_service: NotificationService):
        self.db_session_factory = db_session_factory
        self.notification_service = notification_service
        self.badge_definitions = self._get_badge_definitions()
    
    def _get_badge_definitions(self) -> List[Dict[str, Any]]:
        """Get comprehensive badge definitions"""
        return [
            # STARTER BADGES
            {
                "name": "Hoş Geldin! 👋",
                "description": "Platform'a ilk kez kaydoldun",
                "category": BadgeCategory.STARTER,
                "icon_url": "👋",
                "requirements": {"type": BadgeType.PLATFORM_USAGE, "action": "first_registration"},
                "points": 50,
                "rarity": "common"
            },
            {
                "name": "İlk Adım 👣",
                "description": "İlk görevini tamamladın",
                "category": BadgeCategory.STARTER,
                "icon_url": "👣",
                "requirements": {"type": BadgeType.TASK_COMPLETION, "count": 1},
                "points": 100,
                "rarity": "common"
            },
            {
                "name": "İlk Kazanç 💰",
                "description": "İlk coin'ini kazandın",
                "category": BadgeCategory.STARTER,
                "icon_url": "💰",
                "requirements": {"type": BadgeType.COIN_EARNED, "amount": 1},
                "points": 75,
                "rarity": "common"
            },
            
            # BRONZE BADGES
            {
                "name": "Görev Ustası 📋",
                "description": "5 görev tamamladın",
                "category": BadgeCategory.BRONZE,
                "icon_url": "📋",
                "requirements": {"type": BadgeType.TASK_COMPLETION, "count": 5},
                "points": 200,
                "rarity": "common"
            },
            {
                "name": "Coin Biriktirici 🪙",
                "description": "100 coin kazandın",
                "category": BadgeCategory.BRONZE,
                "icon_url": "🪙",
                "requirements": {"type": BadgeType.COIN_EARNED, "amount": 100},
                "points": 150,
                "rarity": "common"
            },
            {
                "name": "Sadık Kullanıcı 🔗",
                "description": "7 gün üst üste giriş yaptın",
                "category": BadgeCategory.BRONZE,
                "icon_url": "🔗",
                "requirements": {"type": BadgeType.STREAK_DAYS, "count": 7},
                "points": 300,
                "rarity": "uncommon"
            },
            
            # SILVER BADGES
            {
                "name": "Görev Şampiyonu 🏆",
                "description": "25 görev tamamladın",
                "category": BadgeCategory.SILVER,
                "icon_url": "🏆",
                "requirements": {"type": BadgeType.TASK_COMPLETION, "count": 25},
                "points": 500,
                "rarity": "uncommon"
            },
            {
                "name": "Zengin Kullanıcı 💎",
                "description": "1000 coin kazandın",
                "category": BadgeCategory.SILVER,
                "icon_url": "💎",
                "requirements": {"type": BadgeType.COIN_EARNED, "amount": 1000},
                "points": 750,
                "rarity": "uncommon"
            },
            {
                "name": "Haftalık Kahraman 🌟",
                "description": "1 hafta boyunca aktif kaldın",
                "category": BadgeCategory.SILVER,
                "icon_url": "🌟",
                "requirements": {"type": BadgeType.STREAK_DAYS, "count": 14},
                "points": 600,
                "rarity": "uncommon"
            },
            
            # GOLD BADGES
            {
                "name": "Efsane Kullanıcı 👑",
                "description": "100 görev tamamladın",
                "category": BadgeCategory.GOLD,
                "icon_url": "👑",
                "requirements": {"type": BadgeType.TASK_COMPLETION, "count": 100},
                "points": 1500,
                "rarity": "rare"
            },
            {
                "name": "Milyoner 💸",
                "description": "10000 coin kazandın",
                "category": BadgeCategory.GOLD,
                "icon_url": "💸",
                "requirements": {"type": BadgeType.COIN_EARNED, "amount": 10000},
                "points": 2000,
                "rarity": "rare"
            },
            {
                "name": "Aylık Şampiyon 🥇",
                "description": "30 gün üst üste aktif kaldın",
                "category": BadgeCategory.GOLD,
                "icon_url": "🥇",
                "requirements": {"type": BadgeType.STREAK_DAYS, "count": 30},
                "points": 1800,
                "rarity": "rare"
            },
            
            # PLATINUM BADGES
            {
                "name": "Platform Uzmanı 🎓",
                "description": "500 görev tamamladın",
                "category": BadgeCategory.PLATINUM,
                "icon_url": "🎓",
                "requirements": {"type": BadgeType.TASK_COMPLETION, "count": 500},
                "points": 5000,
                "rarity": "epic"
            },
            {
                "name": "Coin Kralı 👸",
                "description": "50000 coin kazandın",
                "category": BadgeCategory.PLATINUM,
                "icon_url": "👸",
                "requirements": {"type": BadgeType.COIN_EARNED, "amount": 50000},
                "points": 6000,
                "rarity": "epic"
            },
            
            # DIAMOND BADGES
            {
                "name": "Efsane Efendi 🗿",
                "description": "1000 görev tamamladın",
                "category": BadgeCategory.DIAMOND,
                "icon_url": "🗿",
                "requirements": {"type": BadgeType.TASK_COMPLETION, "count": 1000},
                "points": 15000,
                "rarity": "legendary"
            },
            {
                "name": "Mega Milyoner 💰",
                "description": "100000 coin kazandın",
                "category": BadgeCategory.DIAMOND,
                "icon_url": "💰",
                "requirements": {"type": BadgeType.COIN_EARNED, "amount": 100000},
                "points": 20000,
                "rarity": "legendary"
            },
            
            # INSTAGRAM BADGES
            {
                "name": "Instagram Bağlantısı 📸",
                "description": "Instagram hesabını bağladın",
                "category": BadgeCategory.INSTAGRAM,
                "icon_url": "📸",
                "requirements": {"type": BadgeType.INSTAGRAM_CONNECTION, "connected": True},
                "points": 300,
                "rarity": "uncommon"
            },
            {
                "name": "Popüler Kullanıcı 👥",
                "description": "1000+ takipçin var",
                "category": BadgeCategory.INSTAGRAM,
                "icon_url": "👥",
                "requirements": {"type": BadgeType.INSTAGRAM_FOLLOWERS, "count": 1000},
                "points": 800,
                "rarity": "rare"
            },
            {
                "name": "İçerik Üreticisi 📱",
                "description": "50+ paylaşımın var",
                "category": BadgeCategory.INSTAGRAM,
                "icon_url": "📱",
                "requirements": {"type": BadgeType.INSTAGRAM_POSTS, "count": 50},
                "points": 600,
                "rarity": "uncommon"
            },
            {
                "name": "Instagram Yıldızı ⭐",
                "description": "10000+ takipçin var",
                "category": BadgeCategory.INSTAGRAM,
                "icon_url": "⭐",
                "requirements": {"type": BadgeType.INSTAGRAM_FOLLOWERS, "count": 10000},
                "points": 2500,
                "rarity": "epic"
            },
            
            # SPECIAL BADGES
            {
                "name": "Beta Tester 🔬",
                "description": "Platform'un beta versiyonunu test ettin",
                "category": BadgeCategory.SPECIAL,
                "icon_url": "🔬",
                "requirements": {"type": "special", "code": "beta_tester"},
                "points": 1000,
                "rarity": "rare"
            },
            {
                "name": "Hata Avcısı 🐛",
                "description": "Önemli bir hatayı bildirdin",
                "category": BadgeCategory.SPECIAL,
                "icon_url": "🐛",
                "requirements": {"type": "special", "code": "bug_reporter"},
                "points": 750,
                "rarity": "rare"
            },
            {
                "name": "Toplum Lideri 🎖️",
                "description": "Topluluk aktivitelerinde öne çıktın",
                "category": BadgeCategory.SPECIAL,
                "icon_url": "🎖️",
                "requirements": {"type": BadgeType.COMMUNITY_PARTICIPATION, "score": 100},
                "points": 1200,
                "rarity": "epic"
            },
            
            # SEASONAL BADGES
            {
                "name": "Yılbaşı Özel 🎄",
                "description": "Yılbaşı etkinliğine katıldın",
                "category": BadgeCategory.SEASONAL,
                "icon_url": "🎄",
                "requirements": {"type": "seasonal", "event": "new_year"},
                "points": 500,
                "rarity": "rare"
            },
            {
                "name": "Sevgililer Günü 💕",
                "description": "Sevgililer günü etkinliğine katıldın",
                "category": BadgeCategory.SEASONAL,
                "icon_url": "💕",
                "requirements": {"type": "seasonal", "event": "valentines"},
                "points": 400,
                "rarity": "uncommon"
            },
            
            # MILESTONE BADGES
            {
                "name": "İlk Ay 📅",
                "description": "Platform'da 1 ay geçirdin",
                "category": BadgeCategory.MILESTONE,
                "icon_url": "📅",
                "requirements": {"type": BadgeType.PLATFORM_USAGE, "days": 30},
                "points": 300,
                "rarity": "uncommon"
            },
            {
                "name": "Bir Yıllık Üye 🗓️",
                "description": "Platform'da 1 yıl geçirdin",
                "category": BadgeCategory.MILESTONE,
                "icon_url": "🗓️",
                "requirements": {"type": BadgeType.PLATFORM_USAGE, "days": 365},
                "points": 2000,
                "rarity": "epic"
            },
            
            # SOCIAL BADGES
            {
                "name": "Arkadaş Canlısı 👫",
                "description": "5 kişiyi davet ettin",
                "category": BadgeCategory.SOCIAL,
                "icon_url": "👫",
                "requirements": {"type": BadgeType.REFERRAL_COUNT, "count": 5},
                "points": 600,
                "rarity": "uncommon"
            },
            {
                "name": "Sosyal Ağ Ustası 🌐",
                "description": "25 kişiyi davet ettin",
                "category": BadgeCategory.SOCIAL,
                "icon_url": "🌐",
                "requirements": {"type": BadgeType.REFERRAL_COUNT, "count": 25},
                "points": 2000,
                "rarity": "rare"
            }
        ]
    
    async def initialize_badges(self) -> bool:
        """Initialize all badge definitions in database"""
        db = self.db_session_factory()
        try:
            created_count = 0
            
            for badge_def in self.badge_definitions:
                # Check if badge already exists
                existing_badge = db.query(Badge).filter(Badge.name == badge_def["name"]).first()
                
                if not existing_badge:
                    badge = Badge(
                        name=badge_def["name"],
                        description=badge_def["description"],
                        category=badge_def["category"],
                        icon_url=badge_def["icon_url"],
                        requirements_json=json.dumps(badge_def["requirements"]),
                        is_active=True
                    )
                    db.add(badge)
                    created_count += 1
            
            db.commit()
            logger.info(f"Initialized {created_count} new badges")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing badges: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def check_and_award_badges(self, user_id: int) -> List[Badge]:
        """Check all badge requirements and award eligible badges"""
        db = self.db_session_factory()
        awarded_badges = []
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return awarded_badges
            
            # Get user's current badges
            current_badge_ids = {ub.badge_id for ub in db.query(UserBadge).filter(
                UserBadge.user_id == user_id
            ).all()}
            
            # Check each badge definition
            for badge_def in self.badge_definitions:
                badge = db.query(Badge).filter(Badge.name == badge_def["name"]).first()
                if not badge or badge.id in current_badge_ids:
                    continue
                
                # Check if user meets requirements
                if await self._check_badge_requirements(user_id, badge_def["requirements"], db):
                    # Award the badge
                    user_badge = UserBadge(
                        user_id=user_id,
                        badge_id=badge.id,
                        awarded_at=datetime.utcnow()
                    )
                    db.add(user_badge)
                    awarded_badges.append(badge)
                    
                    # Send notification
                    await self._send_badge_notification(user_id, badge)
            
            db.commit()
            
            if awarded_badges:
                logger.info(f"Awarded {len(awarded_badges)} badges to user {user_id}")
            
            return awarded_badges
            
        except Exception as e:
            logger.error(f"Error checking badges for user {user_id}: {e}")
            db.rollback()
            return []
        finally:
            db.close()
    
    async def _check_badge_requirements(self, user_id: int, requirements: Dict[str, Any], db: Session) -> bool:
        """Check if user meets badge requirements"""
        try:
            req_type = requirements.get("type")
            
            if req_type == BadgeType.TASK_COMPLETION:
                completed_tasks = db.query(Task).filter(
                    Task.user_id == user_id,
                    Task.status == TaskStatus.completed
                ).count()
                return completed_tasks >= requirements.get("count", 0)
            
            elif req_type == BadgeType.COIN_EARNED:
                total_earned = db.query(func.sum(CoinTransaction.amount)).filter(
                    CoinTransaction.user_id == user_id,
                    CoinTransaction.type == CoinTransactionType.earn
                ).scalar() or 0
                return total_earned >= requirements.get("amount", 0)
            
            elif req_type == BadgeType.COIN_SPENT:
                total_spent = db.query(func.sum(CoinTransaction.amount)).filter(
                    CoinTransaction.user_id == user_id,
                    CoinTransaction.type == CoinTransactionType.spend
                ).scalar() or 0
                return total_spent >= requirements.get("amount", 0)
            
            elif req_type == BadgeType.ORDER_COMPLETION:
                completed_orders = db.query(models.Order).filter( # models.Order olarak güncellendi
                    models.Order.user_id == user_id, # models.Order olarak güncellendi
                    models.Order.status == models.OrderStatus.completed # models.OrderStatus olarak güncellendi
                ).count()
                return completed_orders >= requirements.get("count", 0)
            
            elif req_type == BadgeType.STREAK_DAYS:
                # Check daily login streak (simplified)
                user = db.query(User).filter(User.id == user_id).first()
                if user and user.daily_reward_streak:
                    return user.daily_reward_streak >= requirements.get("count", 0)
                return False
            
            elif req_type == BadgeType.INSTAGRAM_CONNECTION:
                user = db.query(User).filter(User.id == user_id).first()
                return user and user.instagram_username is not None
            
            elif req_type == BadgeType.INSTAGRAM_FOLLOWERS:
                user = db.query(User).filter(User.id == user_id).first()
                return user and user.followers >= requirements.get("count", 0)
            
            elif req_type == BadgeType.PLATFORM_USAGE:
                action = requirements.get("action")
                if action == "first_registration":
                    return True  # If we're checking, user is already registered
                
                days = requirements.get("days", 0)
                if days > 0:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user and user.created_at:
                        days_on_platform = (datetime.utcnow() - user.created_at).days
                        return days_on_platform >= days
                return False
            
            # Special badges require manual awarding
            elif req_type == "special" or req_type == "seasonal":
                return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking requirements {requirements}: {e}")
            return False
    
    async def _send_badge_notification(self, user_id: int, badge: Badge):
        """Send notification for new badge"""
        try:
            await self.notification_service.create_notification(
                user_id=user_id,
                title="🎉 Yeni Rozet Kazandınız!",
                message=f"Tebrikler! '{badge.name}' rozetini kazandınız!",
                notification_type=NotificationType.BADGE_EARNED,
                priority=NotificationPriority.HIGH,
                data={
                    "badge_id": badge.id,
                    "badge_name": badge.name,
                    "badge_description": badge.description,
                    "badge_category": badge.category,
                    "badge_icon": badge.icon_url
                }
            )
        except Exception as e:
            logger.error(f"Error sending badge notification: {e}")
    
    async def award_special_badge(self, user_id: int, badge_name: str) -> bool:
        """Manually award a special badge"""
        db = self.db_session_factory()
        try:
            # Find badge
            badge = db.query(Badge).filter(Badge.name == badge_name).first()
            if not badge:
                return False
            
            # Check if user already has this badge
            existing = db.query(UserBadge).filter(
                UserBadge.user_id == user_id,
                UserBadge.badge_id == badge.id
            ).first()
            
            if existing:
                return False
            
            # Award badge
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge.id,
                awarded_at=datetime.utcnow()
            )
            db.add(user_badge)
            db.commit()
            
            # Send notification
            await self._send_badge_notification(user_id, badge)
            
            logger.info(f"Manually awarded badge '{badge_name}' to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error awarding special badge: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def get_user_badge_progress(self, user_id: int) -> Dict[str, Any]:
        """Get user's badge progress and statistics"""
        db = self.db_session_factory()
        try:
            # Get user's earned badges
            earned_badges = db.query(UserBadge, Badge).join(
                Badge, UserBadge.badge_id == Badge.id
            ).filter(UserBadge.user_id == user_id).all()
            
            # Get all available badges
            all_badges = db.query(Badge).filter(Badge.is_active == True).all()
            
            # Calculate statistics
            total_badges = len(all_badges)
            earned_count = len(earned_badges)
            progress_percentage = (earned_count / total_badges * 100) if total_badges > 0 else 0
            
            # Group by category
            category_stats = {}
            for badge in all_badges:
                category = badge.category
                if category not in category_stats:
                    category_stats[category] = {"total": 0, "earned": 0}
                category_stats[category]["total"] += 1
            
            for user_badge, badge in earned_badges:
                category = badge.category
                if category in category_stats:
                    category_stats[category]["earned"] += 1
            
            # Recent badges (last 5)
            recent_badges = sorted(earned_badges, key=lambda x: x[0].awarded_at, reverse=True)[:5]
            
            return {
                "total_badges": total_badges,
                "earned_badges": earned_count,
                "progress_percentage": round(progress_percentage, 1),
                "category_stats": category_stats,
                "recent_badges": [
                    {
                        "id": badge.id,
                        "name": badge.name,
                        "description": badge.description,
                        "category": badge.category,
                        "icon_url": badge.icon_url,
                        "earned_at": user_badge.awarded_at.isoformat()
                    }
                    for user_badge, badge in recent_badges
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting badge progress for user {user_id}: {e}")
            return {}
        finally:
            db.close()
    
    async def get_badge_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get badge leaderboard"""
        db = self.db_session_factory()
        DEFAULT_AVATAR_URL = "https://cdn.jsdelivr.net/gh/mirzass/instagram_default_avatar.png"  # You can host your own or use a static asset
        try:
            # Get users with most badges
            leaderboard = db.query(
                User.id,
                User.username,
                User.profile_pic_url,
                func.count(UserBadge.id).label('badge_count')
            ).join(
                UserBadge, User.id == UserBadge.user_id
            ).group_by(
                User.id, User.username, User.profile_pic_url
            ).order_by(
                desc('badge_count')
            ).limit(limit).all()
            
            return [
                {
                    "user_id": row.id,
                    "username": row.username,
                    "profile_pic_url": row.profile_pic_url if row.profile_pic_url else DEFAULT_AVATAR_URL,
                    "badge_count": row.badge_count,
                    "rank": idx + 1
                }
                for idx, row in enumerate(leaderboard)
            ]
            
        except Exception as e:
            logger.error(f"Error getting badge leaderboard: {e}")
            return []
        finally:
            db.close()

# Global badge system instance
enhanced_badge_system = None

def get_enhanced_badge_system(db_session_factory, notification_service):
    """Get global enhanced badge system instance"""
    global enhanced_badge_system
    if enhanced_badge_system is None:
        enhanced_badge_system = EnhancedBadgeSystem(db_session_factory, notification_service)
    return enhanced_badge_system
