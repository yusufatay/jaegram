"""
Advanced Social Features System
- Referral system with bonuses
- Badge and achievement system
- Leaderboards (weekly/monthly)
- Coin transfer between users
- Social stats and rankings
"""

import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from instagram_scraper import scrape_instagram_profile_modern
from models import (
    User, Referral, Badge, UserBadge, Leaderboard, UserSocial,
    CoinTransaction, CoinTransactionType, Task, TaskStatus, SessionLocal
)
from enhanced_notifications import NotificationService, NotificationType, NotificationPriority

logger = logging.getLogger(__name__)

class SocialFeaturesManager:
    """Advanced social features management"""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.notification_service = NotificationService(db_session_factory)
        
        # Referral system settings
        self.referrer_bonus = 100  # Coins for referrer
        self.referred_bonus = 50   # Coins for referred user
        self.min_tasks_for_referral_bonus = 10  # Minimum tasks for bonus
        
        # Transfer settings
        self.min_transfer_amount = 10
        self.max_transfer_amount = 1000
        self.transfer_fee_percentage = 0.05  # 5% fee
        
        # Achievement thresholds
        self.achievement_thresholds = {
            'first_task': 1,
            'task_master': 100,
            'coin_collector': 1000,
            'social_butterfly': 5,  # referrals
            'helping_hand': 100,    # coins transferred to others
            'top_performer': 1,     # leaderboard position
        }
    
    async def generate_referral_code(self, user_id: int) -> Dict[str, Any]:
        """Generate unique referral code for user"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Check if user already has social record
            user_social = db.query(UserSocial).filter(UserSocial.user_id == user_id).first()
            
            if user_social and user_social.referral_code:
                return {
                    "success": True,
                    "referral_code": user_social.referral_code,
                    "message": "Mevcut referans kodunuz"
                }
            
            # Generate unique code
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                existing = db.query(UserSocial).filter(UserSocial.referral_code == code).first()
                if not existing:
                    break
            
            if not user_social:
                user_social = UserSocial(user_id=user_id, referral_code=code)
                db.add(user_social)
            else:
                user_social.referral_code = code
            
            db.commit()
            
            return {
                "success": True,
                "referral_code": code,
                "message": "Referans kodunuz oluşturuldu"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error generating referral code for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Referans kodu oluşturulurken hata oluştu"}
        finally:
            db.close()
    
    async def apply_referral_code(self, user_id: int, referral_code: str) -> Dict[str, Any]:
        """Apply referral code for new user"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Check if user already has a referrer
            existing_referral = db.query(Referral).filter(Referral.referred_id == user_id).first()
            if existing_referral:
                return {"success": False, "message": "Zaten bir referans kodunuz var"}
            
            # Find referrer
            referrer_social = db.query(UserSocial).filter(UserSocial.referral_code == referral_code).first()
            if not referrer_social:
                return {"success": False, "message": "Geçersiz referans kodu"}
            
            if referrer_social.user_id == user_id:
                return {"success": False, "message": "Kendi kodunuzu kullanamazsınız"}
            
            referrer = db.query(User).filter(User.id == referrer_social.user_id).first()
            if not referrer:
                return {"success": False, "message": "Referans sahibi bulunamadı"}
            
            # Create referral relationship
            referral = Referral(
                referrer_id=referrer_social.user_id,
                referred_id=user_id
            )
            db.add(referral)
            
            # Update user social records
            user_social = db.query(UserSocial).filter(UserSocial.user_id == user_id).first()
            if not user_social:
                user_social = UserSocial(user_id=user_id, referred_by=referrer_social.user_id)
                db.add(user_social)
            else:
                user_social.referred_by = referrer_social.user_id
            
            referrer_social.total_referrals += 1
            
            # Give immediate bonus to referred user
            user.coin_balance += self.referred_bonus
            transaction = CoinTransaction(
                user_id=user_id,
                amount=self.referred_bonus,
                type=CoinTransactionType.earn,
                note=f"Referans bonusu (Kod: {referral_code})"
            )
            db.add(transaction)
            
            # Notify both users
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Referans Bonusu Kazandınız! 🎁",
                message=f"Referans kodunu kullandığınız için {self.referred_bonus} coin kazandınız!",
                notification_type=NotificationType.REFERRAL_BONUS,
                priority=NotificationPriority.HIGH,
                data={"bonus_amount": self.referred_bonus, "referrer_username": referrer.username}
            )
            
            await self.notification_service.create_notification(
                user_id=referrer_social.user_id,
                title="Yeni Referans! 👥",
                message=f"{user.username} sizin referans kodunuzu kullandı!",
                notification_type=NotificationType.NEW_REFERRAL,
                priority=NotificationPriority.MEDIUM,
                data={"referred_username": user.username}
            )
            
            db.commit()
            
            # Check for achievements
            await self._check_referral_achievements(referrer_social.user_id, db)
            
            return {
                "success": True,
                "message": f"Referans kodu uygulandı! {self.referred_bonus} coin kazandınız!",
                "bonus_received": self.referred_bonus,
                "referrer_username": referrer.username
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error applying referral code for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Referans kodu uygulanırken hata oluştu"}
        finally:
            db.close()
    
    async def check_referral_bonus_eligibility(self, referred_user_id: int):
        """Check if referred user is eligible for referrer bonus"""
        db = self.db_session_factory()
        try:
            # Find referral relationship
            referral = db.query(Referral).filter(
                Referral.referred_id == referred_user_id,
                Referral.bonus_given == False
            ).first()
            
            if not referral:
                return
            
            # Check if referred user has completed enough tasks
            completed_tasks = db.query(Task).filter(
                Task.assigned_user_id == referred_user_id,
                Task.status == TaskStatus.completed
            ).count()
            
            if completed_tasks >= self.min_tasks_for_referral_bonus:
                # Give bonus to referrer
                referrer = db.query(User).filter(User.id == referral.referrer_id).first()
                referred = db.query(User).filter(User.id == referred_user_id).first()
                
                if referrer and referred:
                    referrer.coin_balance += self.referrer_bonus
                    
                    transaction = CoinTransaction(
                        user_id=referral.referrer_id,
                        amount=self.referrer_bonus,
                        type=CoinTransactionType.earn,
                        note=f"Referans bonusu ({referred.username} {self.min_tasks_for_referral_bonus} görev tamamladı)"
                    )
                    db.add(transaction)
                    
                    referral.bonus_given = True
                    
                    # Notify referrer
                    await self.notification_service.create_notification(
                        user_id=referral.referrer_id,
                        title="Referans Bonusu Kazandınız! 💰",
                        message=f"{referred.username} {self.min_tasks_for_referral_bonus} görev tamamladı! {self.referrer_bonus} coin kazandınız!",
                        notification_type=NotificationType.REFERRAL_BONUS,
                        priority=NotificationPriority.HIGH,
                        data={"bonus_amount": self.referrer_bonus, "referred_username": referred.username}
                    )
                    
                    db.commit()
                    
                    logger.info(f"Referral bonus given to {referrer.username} for referring {referred.username}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error checking referral bonus eligibility: {e}", exc_info=True)
        finally:
            db.close()
    
    async def transfer_coins(self, sender_id: int, recipient_username: str, amount: int, 
                           message: Optional[str] = None) -> Dict[str, Any]:
        """Transfer coins between users"""
        db = self.db_session_factory()
        try:
            sender = db.query(User).filter(User.id == sender_id).first()
            if not sender:
                return {"success": False, "message": "Gönderici bulunamadı"}
            
            recipient = db.query(User).filter(User.username == recipient_username).first()
            if not recipient:
                return {"success": False, "message": "Alıcı kullanıcı bulunamadı"}
            
            if sender_id == recipient.id:
                return {"success": False, "message": "Kendinize coin gönderemezsiniz"}
            
            # Validate amount
            if amount < self.min_transfer_amount:
                return {"success": False, "message": f"Minimum transfer miktarı {self.min_transfer_amount} coin"}
            
            if amount > self.max_transfer_amount:
                return {"success": False, "message": f"Maksimum transfer miktarı {self.max_transfer_amount} coin"}
            
            # Calculate fee
            fee = int(amount * self.transfer_fee_percentage)
            total_cost = amount + fee
            
            if sender.coin_balance < total_cost:
                return {"success": False, "message": f"Yetersiz bakiye (Gerekli: {total_cost} coin, Bakiye: {sender.coin_balance})"}
            
            # Process transfer
            sender.coin_balance -= total_cost
            recipient.coin_balance += amount
            
            # Create transactions
            sender_transaction = CoinTransaction(
                user_id=sender_id,
                amount=-total_cost,
                type=CoinTransactionType.spend,
                note=f"Transfer: {amount} coin -> {recipient_username} (Fee: {fee})"
            )
            db.add(sender_transaction)
            
            recipient_transaction = CoinTransaction(
                user_id=recipient.id,
                amount=amount,
                type=CoinTransactionType.earn,
                note=f"Transfer alındı: {sender.username} -> {amount} coin"
            )
            db.add(recipient_transaction)
            
            # Update social stats
            sender_social = db.query(UserSocial).filter(UserSocial.user_id == sender_id).first()
            if not sender_social:
                sender_social = UserSocial(user_id=sender_id, total_transferred=amount)
                db.add(sender_social)
            else:
                sender_social.total_transferred += amount
            
            recipient_social = db.query(UserSocial).filter(UserSocial.user_id == recipient.id).first()
            if not recipient_social:
                recipient_social = UserSocial(user_id=recipient.id, total_received=amount)
                db.add(recipient_social)
            else:
                recipient_social.total_received += amount
            
            # Notify both users
            transfer_message = f" - Mesaj: {message}" if message else ""
            
            await self.notification_service.create_notification(
                user_id=recipient.id,
                title="Coin Transferi Alındı! 💸",
                message=f"{sender.username} size {amount} coin gönderdi{transfer_message}",
                notification_type=NotificationType.COIN_TRANSFER_RECEIVED,
                priority=NotificationPriority.HIGH,
                data={"amount": amount, "sender_username": sender.username, "message": message}
            )
            
            await self.notification_service.create_notification(
                user_id=sender_id,
                title="Coin Transferi Gönderildi! 📤",
                message=f"{recipient_username} kullanıcısına {amount} coin gönderildi (Fee: {fee} coin)",
                notification_type=NotificationType.COIN_TRANSFER_SENT,
                priority=NotificationPriority.MEDIUM,
                data={"amount": amount, "recipient_username": recipient_username, "fee": fee}
            )
            
            db.commit()
            
            # Check for achievements
            await self._check_transfer_achievements(sender_id, db)
            
            return {
                "success": True,
                "message": "Transfer başarıyla tamamlandı",
                "transferred_amount": amount,
                "fee": fee,
                "new_balance": sender.coin_balance
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error transferring coins from {sender_id} to {recipient_username}: {e}", exc_info=True)
            return {"success": False, "message": "Transfer sırasında hata oluştu"}
        finally:
            db.close()
    
    async def get_leaderboard(self, period: str = "weekly", limit: int = 100) -> List[Dict[str, Any]]:
        """Get leaderboard for specified period, always using Instagram profile photo if available"""
        db = self.db_session_factory()
        DEFAULT_AVATAR_URL = "https://ui-avatars.com/api/?name=User&background=random&size=128&format=png"
        try:
            # Support "all" period for all-time leaderboard
            valid_periods = ["weekly", "monthly", "all"]
            if period not in valid_periods:
                return []
            
            def get_and_update_profile_pic(user_entry):
                # Prefer instagram_profile_pic_url, then profile_pic_url, then fetch
                pic_url = None
                user_obj = db.query(User).filter(User.id == user_entry.id).first()
                if user_obj:
                    pic_url = user_obj.instagram_profile_pic_url or user_obj.profile_pic_url
                    if not pic_url and user_obj.instagram_username:
                        # Fetch from Instagram using modern scraper and save
                        try:
                            from modern_instagram_scraper import ModernInstagramScraper
                            scraper = ModernInstagramScraper()
                            # Note: We need to handle async in sync context
                            import asyncio
                            loop = asyncio.get_event_loop()
                            result = loop.run_until_complete(scraper.scrape_profile(user_obj.instagram_username))
                            if result.get("success"):
                                profile_pic = result.get("profile_pic_url")
                                if profile_pic and profile_pic != "https://example.com/test_profile.jpg":
                                    user_obj.instagram_profile_pic_url = profile_pic
                                    db.commit()
                                    pic_url = profile_pic
                        except Exception as e:
                            logger.warning(f"Could not fetch Instagram profile pic for {user_obj.instagram_username}: {e}")
                return pic_url or DEFAULT_AVATAR_URL

            if period == "all":
                # For all-time leaderboard, use coin_balance
                leaderboard_query = db.query(
                    User.id,
                    User.username,
                    User.profile_pic_url,
                    User.coin_balance.label('total_coins'),
                    UserSocial.total_referrals
                ).outerjoin(
                    UserSocial, User.id == UserSocial.user_id
                ).filter(
                    User.is_active == True
                ).order_by(
                    desc(User.coin_balance)
                ).limit(limit)
                
                results = leaderboard_query.all()
                leaderboard_data = []
                for rank, entry in enumerate(results, 1):
                    # Count completed tasks for this user
                    completed_tasks = db.query(func.count(CoinTransaction.id)).filter(
                        CoinTransaction.user_id == entry.id,
                        CoinTransaction.type == CoinTransactionType.earn,
                        CoinTransaction.task_id.isnot(None)
                    ).scalar() or 0
                    
                    leaderboard_data.append({
                        "id": entry.id,
                        "user_id": entry.id,
                        "username": entry.username,
                        "total_coins": entry.total_coins or 0,
                        "tasks_completed": completed_tasks,
                        "rank": rank,
                        "weekly_coins": 0,  # Placeholder for all-time view
                        "monthly_coins": 0,  # Placeholder for all-time view
                        "updated_at": datetime.utcnow().isoformat(),
                        "profile_pic_url": get_and_update_profile_pic(entry)
                    })
            else:
                # For weekly/monthly, use Leaderboard table
                leaderboard_entries = db.query(
                    Leaderboard.id,
                    Leaderboard.user_id,
                    Leaderboard.rank,
                    Leaderboard.score,
                    User.username,
                    User.profile_pic_url,
                    User.coin_balance,
                    UserSocial.total_referrals
                ).join(
                    User, Leaderboard.user_id == User.id
                ).outerjoin(
                    UserSocial, User.id == UserSocial.user_id
                ).filter(
                    Leaderboard.period == period
                ).order_by(
                    Leaderboard.rank
                ).limit(limit).all()
                
                leaderboard_data = []
                for entry in leaderboard_entries:
                    # Count completed tasks for this user
                    completed_tasks = db.query(func.count(CoinTransaction.id)).filter(
                        CoinTransaction.user_id == entry.user_id,
                        CoinTransaction.type == CoinTransactionType.earn,
                        CoinTransaction.task_id.isnot(None)
                    ).scalar() or 0
                    
                    # Calculate weekly and monthly coins based on period
                    weekly_coins = entry.score if period == "weekly" else 0
                    monthly_coins = entry.score if period == "monthly" else 0
                    
                    leaderboard_data.append({
                        "id": entry.id,
                        "user_id": entry.user_id,
                        "username": entry.username,
                        "total_coins": entry.coin_balance or 0,
                        "tasks_completed": completed_tasks,
                        "rank": entry.rank,
                        "weekly_coins": weekly_coins,
                        "monthly_coins": monthly_coins,
                        "updated_at": datetime.utcnow().isoformat(),
                        "profile_pic_url": get_and_update_profile_pic(entry)
                    })
            
            return leaderboard_data
            
        except Exception as e:
            logger.error(f"Error getting {period} leaderboard: {e}", exc_info=True)
            return []
        finally:
            db.close()
    
    async def get_user_badges(self, user_id: int) -> Dict[str, Any]:
        """Get user's badges and achievements"""
        db = self.db_session_factory()
        try:
            user_badges = db.query(
                Badge.name,
                Badge.description,
                Badge.icon_url,
                UserBadge.awarded_at
            ).join(
                UserBadge, Badge.id == UserBadge.badge_id
            ).filter(
                UserBadge.user_id == user_id
            ).order_by(
                UserBadge.awarded_at.desc()
            ).all()
            
            badges_data = []
            for badge in user_badges:
                badges_data.append({
                    "name": badge.name,
                    "description": badge.description,
                    "icon_url": badge.icon_url,
                    "awarded_at": badge.awarded_at.isoformat() if badge.awarded_at else None
                })
            
            # Check for new achievements
            await self._check_all_achievements(user_id, db)
            
            return {
                "success": True,
                "user_id": user_id,
                "badges": badges_data,
                "total_badges": len(badges_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting badges for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Rozetler alınırken hata oluştu"}
        finally:
            db.close()
    
    async def get_social_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user's social statistics"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            user_social = db.query(UserSocial).filter(UserSocial.user_id == user_id).first()
            
            # Get referral stats
            referrals_made = db.query(Referral).filter(Referral.referrer_id == user_id).count()
            total_referral_earnings = db.query(func.sum(CoinTransaction.amount)).filter(
                CoinTransaction.user_id == user_id,
                CoinTransaction.type == CoinTransactionType.earn,
                CoinTransaction.note.like("%referans%")
            ).scalar() or 0
            
            # Get leaderboard position
            weekly_position = db.query(Leaderboard.rank).filter(
                Leaderboard.user_id == user_id,
                Leaderboard.period == "weekly"
            ).scalar()
            
            monthly_position = db.query(Leaderboard.rank).filter(
                Leaderboard.user_id == user_id,
                Leaderboard.period == "monthly"
            ).scalar()
            
            # Get badge count
            badge_count = db.query(UserBadge).filter(UserBadge.user_id == user_id).count()
            
            return {
                "success": True,
                "user_id": user_id,
                "username": user.username,
                "referral_code": user_social.referral_code if user_social else None,
                "referrals_made": referrals_made,
                "total_referral_earnings": total_referral_earnings,
                "total_transferred": user_social.total_transferred if user_social else 0,
                "total_received": user_social.total_received if user_social else 0,
                "badge_count": badge_count,
                "leaderboard_positions": {
                    "weekly": weekly_position,
                    "monthly": monthly_position
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting social stats for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Sosyal istatistikler alınırken hata oluştu"}
        finally:
            db.close()
    
    async def _check_all_achievements(self, user_id: int, db: Session):
        """Check and award all possible achievements for user"""
        await self._check_task_achievements(user_id, db)
        await self._check_coin_achievements(user_id, db)
        await self._check_referral_achievements(user_id, db)
        await self._check_transfer_achievements(user_id, db)
        await self._check_leaderboard_achievements(user_id, db)
    
    async def _check_task_achievements(self, user_id: int, db: Session):
        """Check and award task-related achievements"""
        completed_tasks = db.query(Task).filter(
            Task.assigned_user_id == user_id,
            Task.status == TaskStatus.completed
        ).count()
        
        # First task achievement
        if completed_tasks >= 1:
            await self._award_badge_if_not_exists(user_id, "İlk Görev 🎯", "İlk görevinizi tamamladınız", db)
        
        # Task master achievement
        if completed_tasks >= self.achievement_thresholds['task_master']:
            await self._award_badge_if_not_exists(user_id, "Görev Ustası 💪", f"{self.achievement_thresholds['task_master']} görev tamamladınız", db)
    
    async def _check_coin_achievements(self, user_id: int, db: Session):
        """Check and award coin-related achievements"""
        total_earnings = db.query(func.sum(CoinTransaction.amount)).filter(
            CoinTransaction.user_id == user_id,
            CoinTransaction.type == CoinTransactionType.earn
        ).scalar() or 0
        
        if total_earnings >= self.achievement_thresholds['coin_collector']:
            await self._award_badge_if_not_exists(user_id, "Coin Koleksiyoncusu 🪙", f"{self.achievement_thresholds['coin_collector']} coin kazandınız", db)
    
    async def _check_referral_achievements(self, user_id: int, db: Session):
        """Check and award referral-related achievements"""
        referral_count = db.query(Referral).filter(Referral.referrer_id == user_id).count()
        
        if referral_count >= self.achievement_thresholds['social_butterfly']:
            await self._award_badge_if_not_exists(user_id, "Sosyal Kelebek 🦋", f"{self.achievement_thresholds['social_butterfly']} kişi davet ettiniz", db)
    
    async def _check_transfer_achievements(self, user_id: int, db: Session):
        """Check and award transfer-related achievements"""
        user_social = db.query(UserSocial).filter(UserSocial.user_id == user_id).first()
        
        if user_social and user_social.total_transferred >= self.achievement_thresholds['helping_hand']:
            await self._award_badge_if_not_exists(user_id, "Yardımsever El 🤝", f"{self.achievement_thresholds['helping_hand']} coin transfer ettiniz", db)
    
    async def _check_leaderboard_achievements(self, user_id: int, db: Session):
        """Check and award leaderboard-related achievements"""
        top_position = db.query(func.min(Leaderboard.rank)).filter(
            Leaderboard.user_id == user_id
        ).scalar()
        
        if top_position and top_position <= self.achievement_thresholds['top_performer']:
            await self._award_badge_if_not_exists(user_id, "En İyi Performans 🏆", "Lider tablosunda 1. oldunuz", db)
    
    async def _award_badge_if_not_exists(self, user_id: int, badge_name: str, description: str, db: Session):
        """Award badge to user if they don't already have it"""
        # Get or create badge
        badge = db.query(Badge).filter(Badge.name == badge_name).first()
        if not badge:
            badge = Badge(name=badge_name, description=description)
            db.add(badge)
            db.flush()
        
        # Check if user already has this badge
        existing = db.query(UserBadge).filter(
            UserBadge.user_id == user_id,
            UserBadge.badge_id == badge.id
        ).first()
        
        if not existing:
            user_badge = UserBadge(user_id=user_id, badge_id=badge.id)
            db.add(user_badge)
            
            # Notify user
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Yeni Rozet Kazandınız! 🏆",
                message=f"Tebrikler! '{badge_name}' rozetini kazandınız!",
                notification_type=NotificationType.BADGE_EARNED,
                priority=NotificationPriority.HIGH,
                data={"badge_name": badge_name, "description": description}
            )
            
            logger.info(f"Awarded badge '{badge_name}' to user {user_id}")

    async def get_all_badges(self) -> Dict[str, Any]:
        """Get all available badges in the system"""
        db = self.db_session_factory()
        try:
            all_badges = db.query(Badge).order_by(Badge.name).all()
            
            badges_data = []
            for badge in all_badges:
                badges_data.append({
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "icon_url": badge.icon_url,
                    "created_at": badge.created_at.isoformat() if hasattr(badge, 'created_at') and badge.created_at else None
                })
            
            return {
                "success": True,
                "badges": badges_data,
                "total_badges": len(badges_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting all badges: {e}", exc_info=True)
            return {"success": False, "message": "Tüm rozetler alınırken hata oluştu"}
        finally:
            db.close()
    
# Global social features manager
social_features_manager = None

def get_social_features_manager(db_session_factory):
    global social_features_manager
    if social_features_manager is None:
        social_features_manager = SocialFeaturesManager(db_session_factory)
    return social_features_manager
