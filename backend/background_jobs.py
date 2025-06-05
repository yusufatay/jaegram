"""
Advanced Background Job System
- Task expiration handling
- Post liveness checking
- Suspicious activity detection
- Coin withdrawal processing
- Mental health notifications
- GDPR request processing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import (
    User, Task, Order, CoinTransaction, CoinWithdrawalRequest, 
    TaskStatus, OrderType, CoinTransactionType, NotificationSetting,
    MentalHealthLog, DeviceIPLog, GDPRRequest, Leaderboard, UserBadge, Badge
)
from instagram_service import InstagramAPIService # Changed from instagram_service
from enhanced_notifications import NotificationService, NotificationType, NotificationPriority
import json

logger = logging.getLogger(__name__)

class BackgroundJobManager:
    """Advanced background job manager for all system maintenance tasks"""
    
    def __init__(self, db_session_factory, instagram_api_service: InstagramAPIService): # Added instagram_api_service
        self.db_session_factory = db_session_factory
        self.notification_service = NotificationService(db_session_factory)
        self.instagram_api_service = instagram_api_service # Store the instance
        self.running = False
        self.background_tasks = []
        self.job_intervals = {
            'expire_tasks': 300,  # 5 minutes
            'check_post_liveness': 600,  # 10 minutes
            'detect_suspicious_activity': 900,  # 15 minutes
            'process_withdrawals': 1800,  # 30 minutes
            'send_mental_health_notifications': 3600,  # 1 hour
            'update_leaderboards': 7200,  # 2 hours
            'process_gdpr_requests': 21600,  # 6 hours
            'cleanup_old_data': 86400,  # 24 hours
        }
    
    async def start(self):
        """Start all background jobs"""
        self.running = True
        logger.info("Starting background job manager...")
        
        # Start all jobs concurrently in the background
        tasks = [
            asyncio.create_task(self._run_periodic_job('expire_tasks', self.expire_tasks)),
            asyncio.create_task(self._run_periodic_job('check_post_liveness', self.check_post_liveness)),
            asyncio.create_task(self._run_periodic_job('detect_suspicious_activity', self.detect_suspicious_activity)),
            asyncio.create_task(self._run_periodic_job('process_withdrawals', self.process_coin_withdrawals)),
            asyncio.create_task(self._run_periodic_job('send_mental_health_notifications', self.send_mental_health_notifications)),
            asyncio.create_task(self._run_periodic_job('update_leaderboards', self.update_leaderboards)),
            asyncio.create_task(self._run_periodic_job('process_gdpr_requests', self.process_gdpr_requests)),
            asyncio.create_task(self._run_periodic_job('cleanup_old_data', self.cleanup_old_data)),
        ]
        
        # Store tasks for proper cleanup later
        self.background_tasks = tasks
        logger.info("Background jobs started successfully")
    
    async def stop(self):
        """Stop all background jobs"""
        self.running = False
        
        # Cancel all background tasks
        if hasattr(self, 'background_tasks'):
            for task in self.background_tasks:
                if not task.done():
                    task.cancel()
        
        logger.info("Background job manager stopped")
    
    def is_running(self) -> bool:
        """Check if background jobs are running"""
        return self.running
    
    async def _run_periodic_job(self, job_name: str, job_func):
        """Run a job periodically"""
        interval = self.job_intervals[job_name]
        
        while self.running:
            try:
                logger.debug(f"Running background job: {job_name}")
                await job_func()
                logger.debug(f"Completed background job: {job_name}")
            except Exception as e:
                logger.error(f"Error in background job {job_name}: {e}", exc_info=True)
            
            await asyncio.sleep(interval)
    
    async def expire_tasks(self):
        """Handle expired tasks"""
        db = self.db_session_factory()
        try:
            now = datetime.utcnow()
            expired_tasks = db.query(Task).filter(
                Task.status == TaskStatus.assigned,
                Task.expires_at < now
            ).all()
            
            if not expired_tasks:
                return
            
            users_to_notify = set()
            expired_count = 0
            
            for task in expired_tasks:
                try:
                    # Mark task as expired
                    task.status = TaskStatus.expired
                    users_to_notify.add(task.assigned_user_id)
                    expired_count += 1
                    
                    # Create notification
                    await self.notification_service.create_notification(
                        user_id=task.assigned_user_id,
                        title="Görev Süresi Doldu ⏰",
                        message=f"Görev #{task.id} süresi doldu ve iptal edildi.",
                        notification_type=NotificationType.TASK_EXPIRED,
                        priority=NotificationPriority.MEDIUM,
                        data={"task_id": task.id, "order_id": task.order_id}
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing expired task {task.id}: {e}")
                    continue
            
            db.commit()
            
            if expired_count > 0:
                logger.info(f"Processed {expired_count} expired tasks, notified {len(users_to_notify)} users")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in expire_tasks job: {e}", exc_info=True)
        finally:
            db.close()
    
    async def check_post_liveness(self):
        """Check if posts in active orders are still alive"""
        db = self.db_session_factory()
        try:
            # Get active orders
            active_orders = db.query(Order).filter(Order.status == "active").all()
            
            for order in active_orders:
                try:
                    # Get a user with Instagram credentials to check the post
                    user_with_ig = db.query(User).filter(
                        User.instagram_session_data.isnot(None)
                    ).first()
                    
                    if not user_with_ig:
                        continue
                    
                    # Get the InstagramAPIService instance from app context or pass it
                    # For now, assuming it's globally available or passed differently.
                    # This needs to be resolved based on how app.py provides it.
                    # Placeholder: instagram_api_service = get_instagram_service_instance()
                    # This line will cause an error if instagram_service is not defined.
                    # We need to ensure the correct service instance is used here.
                    # Assuming app.py makes instagram_service (the instance) available globally
                    # or we need to adjust how it's accessed here.
                    
                    # Corrected to use the class name for static/instance methods if not directly importing an instance
                    # However, the original code `from instagram_service import instagram_service` implies
                    # it expected to import an *instance*. Since we changed `instagram_service.py` to define
                    # a class `InstagramAPIService` and `app.py` creates an instance of it, 
                    # `background_jobs.py` needs access to that *instance*.

                    # Simplest fix for now, assuming app.py will make its instance available
                    # or this BackgroundJobManager will be instantiated with it.
                    # For now, let's assume it's passed or globally accessible via app.py's setup.
                    # This will likely require a change in app.py to pass the instance or a refactor here.

                    # If `instagram_service` was meant to be the module and then call a method:
                    # result = await InstagramAPIService().validate_like_action(...) # This would be wrong if it needs state

                    # The original code `from instagram_service import instagram_service` suggests it was importing an instance.
                    # Since `instagram_service.py` now only defines the class `InstagramAPIService`,
                    # and `app.py` creates an instance `instagram_service = InstagramAPIService(...)`,
                    # `background_jobs.py` needs access to *that specific instance*.

                    # This is a common dependency injection problem.
                    # For now, I will assume that `app.py` makes its `instagram_service` instance
                    # somehow accessible to `background_jobs.py`. 
                    # A proper fix would be to pass the instance of InstagramAPIService to BackgroundJobManager.
                    # Let's assume for the purpose of this fix that `instagram_service` is the instance from `app.py`
                    # and the import at the top should be `from app import instagram_service` or similar, 
                    # or `BackgroundJobManager` should receive it in `__init__`.
                    
                    # Given the current error, the import `from instagram_service import instagram_service` is failing.
                    # It should be `from instagram_service import InstagramAPIService` (to get the class)
                    # and then an *instance* of `InstagramAPIService` must be used.
                    
                    # Let's assume BackgroundJobManager gets the instance. This requires changing its __init__.
                    # For now, to fix the immediate import error, I changed the import at the top.
                    # But the call below will fail if `instagram_service` is not an initialized instance.
                    
                    # This part of the code needs the actual INSTANCE of InstagramAPIService.
                    # The import `from instagram_service import instagram_service` was trying to get an instance.
                    # Since `instagram_service.py` no longer provides a global instance, this is an issue.
                    # `app.py` creates an instance: `instagram_service = InstagramAPIService(db_session_maker=SessionLocal)`
                    # `background_jobs.py` needs this instance.

                    # The import in background_jobs.py should be: `from app import instagram_service_instance # or whatever app.py calls its instance`
                    # Or, `BackgroundJobManager` should take `instagram_service_instance` as an __init__ argument.

                    # Let's modify `BackgroundJobManager` to accept the instagram_service instance.

                    # First, change the import in background_jobs.py to import the class:
                    # from instagram_service import InstagramAPIService (already done in a previous step by me)

                    # Then, BackgroundJobManager.__init__ needs to accept it.
                    # And app.py needs to pass it when creating BackgroundJobManager.

                    # The current error is specifically the import at line 26 of background_jobs.py.
                    # `from instagram_service import instagram_service`
                    # This needs to be changed because `instagram_service.py` doesn't export `instagram_service` anymore.
                    # It exports `InstagramAPIService` (the class).

                    # The simplest way to resolve the *current* ImportError, assuming the rest of the logic
                    # in `check_post_liveness` expects an *instance* named `instagram_service`:
                    # We need to ensure that `background_jobs.py` gets the instance created in `app.py`.

                    # Change the import in `background_jobs.py`:
                    # from app import instagram_service_instance # or whatever app.py calls its instance
                    # This creates a circular dependency if app also imports from background_jobs.

                    # Alternative: Modify BackgroundJobManager to take the service as a parameter.
                    # This is cleaner.

                    # In background_jobs.py:
                    # Remove: from instagram_service import instagram_service
                    # Add to __init__: self.instagram_api_service = instagram_api_service (passed in)
                    # Change calls from `instagram_service.method()` to `self.instagram_api_service.method()`

                    # In app.py:
                    # `instagram_service_instance = InstagramAPIService(db_session_maker=SessionLocal)`
                    # `background_job_manager = BackgroundJobManager(SessionLocal, instagram_service_instance)`

                    # Let's apply this. First, modify background_jobs.py

                    result = await self.instagram_api_service.validate_like_action(
                        user_with_ig, order.post_url, db
                    )
                    
                    if not result.get("success") and "not found" in result.get("message", "").lower():
                        # Post is no longer accessible, cancel order
                        order.status = "cancelled"
                        
                        # Cancel all related tasks
                        related_tasks = db.query(Task).filter(
                            Task.order_id == order.id,
                            Task.status == TaskStatus.assigned
                        ).all()
                        
                        for task in related_tasks:
                            task.status = TaskStatus.failed
                            
                            # Notify user
                            await self.notification_service.create_notification(
                                user_id=task.assigned_user_id,
                                title="Görev İptal Edildi 📋",
                                message="Hedef gönderi erişilemez durumda olduğu için görev iptal edildi.",
                                notification_type=NotificationType.TASK_CANCELLED,
                                priority=NotificationPriority.HIGH
                            )
                        
                        # Notify order creator
                        await self.notification_service.create_notification(
                            user_id=order.user_id,
                            title="Sipariş İptal Edildi 📋",
                            message="Gönderiniz erişilemez durumda olduğu için sipariş iptal edildi.",
                            notification_type=NotificationType.ORDER_CANCELLED,
                            priority=NotificationPriority.HIGH
                        )
                        
                        logger.warning(f"Cancelled order {order.id} due to inaccessible post: {order.post_url}")
                    
                    # Rate limiting
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error checking post liveness for order {order.id}: {e}")
                    continue
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in check_post_liveness job: {e}", exc_info=True)
        finally:
            db.close()
    
    async def detect_suspicious_activity(self):
        """Detect and handle suspicious user activity"""
        db = self.db_session_factory()
        try:
            now = datetime.utcnow()
            one_hour_ago = now - timedelta(hours=1)
            
            # Check for rapid task completion (more than 10 tasks in 1 hour)
            suspicious_users = db.query(
                Task.assigned_user_id,
                func.count(Task.id).label('task_count')
            ).filter(
                Task.status == TaskStatus.completed,
                Task.completed_at >= one_hour_ago
            ).group_by(Task.assigned_user_id).having(
                func.count(Task.id) > 10
            ).all()
            
            for user_id, task_count in suspicious_users:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    continue
                
                # Log suspicious activity
                device_log = DeviceIPLog(
                    user_id=user_id,
                    action="suspicious_rapid_completion",
                    device_info=f"Completed {task_count} tasks in 1 hour"
                )
                db.add(device_log)
                
                # Lock user's withdrawals temporarily
                pending_withdrawals = db.query(CoinWithdrawalRequest).filter(
                    CoinWithdrawalRequest.user_id == user_id,
                    CoinWithdrawalRequest.status == "pending"
                ).all()
                
                for withdrawal in pending_withdrawals:
                    withdrawal.status = "locked"
                    withdrawal.suspicious = True
                    withdrawal.locked_until = now + timedelta(hours=48)
                
                # Notify admins
                admin_users = db.query(User).filter(User.is_admin == True).all()
                for admin in admin_users:
                    await self.notification_service.create_notification(
                        user_id=admin.id,
                        title="Şüpheli Aktivite Tespit Edildi 🚨",
                        message=f"Kullanıcı {user.username} ({user_id}) 1 saatte {task_count} görev tamamladı.",
                        notification_type=NotificationType.SECURITY_ALERT,
                        priority=NotificationPriority.URGENT,
                        data={"suspicious_user_id": user_id, "task_count": task_count}
                    )
                
                logger.warning(f"Detected suspicious activity for user {user.username}: {task_count} tasks in 1 hour")
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in detect_suspicious_activity job: {e}", exc_info=True)
        finally:
            db.close()
    
    async def process_coin_withdrawals(self):
        """Process pending coin withdrawal requests"""
        db = self.db_session_factory()
        try:
            now = datetime.utcnow()
            
            # Process withdrawals that have been pending for 48 hours
            pending_since = now - timedelta(hours=48)
            
            withdrawals_to_process = db.query(CoinWithdrawalRequest).filter(
                CoinWithdrawalRequest.status == "pending",
                CoinWithdrawalRequest.requested_at <= pending_since,
                CoinWithdrawalRequest.suspicious == False
            ).all()
            
            for withdrawal in withdrawals_to_process:
                try:
                    user = db.query(User).filter(User.id == withdrawal.user_id).first()
                    if not user:
                        withdrawal.status = "rejected"
                        continue
                    
                    # Final security check
                    recent_suspicious = db.query(DeviceIPLog).filter(
                        DeviceIPLog.user_id == withdrawal.user_id,
                        DeviceIPLog.action.like("%suspicious%"),
                        DeviceIPLog.created_at >= now - timedelta(days=7)
                    ).first()
                    
                    if recent_suspicious:
                        withdrawal.status = "locked"
                        withdrawal.locked_until = now + timedelta(days=7)
                        withdrawal.suspicious = True
                        continue
                    
                    # Process withdrawal
                    withdrawal.status = "approved"
                    withdrawal.processed_at = now
                    
                    # Create transaction record
                    transaction = CoinTransaction(
                        user_id=user.id,
                        amount=-withdrawal.amount,
                        type=CoinTransactionType.withdraw,
                        note=f"Çekim işlemi onaylandı (İstek #{withdrawal.id})"
                    )
                    db.add(transaction)
                    
                    # Notify user
                    await self.notification_service.create_notification(
                        user_id=user.id,
                        title="Para Çekme Onaylandı ✅",
                        message=f"{withdrawal.amount} coin çekim talebiniz onaylandı ve işleme alındı.",
                        notification_type=NotificationType.WITHDRAWAL_APPROVED,
                        priority=NotificationPriority.HIGH,
                        data={"amount": withdrawal.amount, "withdrawal_id": withdrawal.id}
                    )
                    
                    logger.info(f"Approved withdrawal {withdrawal.id} for user {user.username}: {withdrawal.amount} coins")
                    
                except Exception as e:
                    logger.error(f"Error processing withdrawal {withdrawal.id}: {e}")
                    withdrawal.status = "rejected"
                    continue
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in process_coin_withdrawals job: {e}", exc_info=True)
        finally:
            db.close()
    
    async def send_mental_health_notifications(self):
        """Send mental health and wellbeing notifications"""
        db = self.db_session_factory()
        try:
            now = datetime.utcnow()
            one_day_ago = now - timedelta(days=1)
            
            # Find users who have been very active (completed many tasks)
            very_active_users = db.query(
                Task.assigned_user_id,
                func.count(Task.id).label('task_count')
            ).filter(
                Task.status == TaskStatus.completed,
                Task.completed_at >= one_day_ago
            ).group_by(Task.assigned_user_id).having(
                func.count(Task.id) > 20  # More than 20 tasks in 24 hours
            ).all()
            
            mental_health_messages = [
                "Mola vermeyi unutmayın! Sağlığınız coinlerden daha değerli. 🌱",
                "Düzenli ara vermeyi unutmayın. Kendinize zaman ayırın! 🧘‍♀️",
                "Çok aktifsiniz! Biraz dinlenme zamanı gelmiş olabilir. 😊",
                "Harika iş çıkarıyorsunuz! Ara sıra nefes almayı da unutmayın. 🌸",
                "Başarılarınız muhteşem! Kendinizi ödüllendirmeyi de unutmayın. 🎉"
            ]
            
            for user_id, task_count in very_active_users:
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user:
                        continue
                    
                    # Check notification settings
                    settings = db.query(NotificationSetting).filter(
                        NotificationSetting.user_id == user_id
                    ).first()
                    
                    if settings and not settings.mental_health_notifications:
                        continue
                    
                    # Check if we've sent a mental health notification recently
                    recent_notification = db.query(MentalHealthLog).filter(
                        MentalHealthLog.user_id == user_id,
                        MentalHealthLog.sent_at >= now - timedelta(hours=6)
                    ).first()
                    
                    if recent_notification:
                        continue
                    
                    # Send notification
                    import random
                    message = random.choice(mental_health_messages)
                    
                    await self.notification_service.create_notification(
                        user_id=user_id,
                        title="Sağlığınızı Unutmayın 💚",
                        message=message,
                        notification_type=NotificationType.MENTAL_HEALTH,
                        priority=NotificationPriority.LOW,
                        send_push=True,
                        send_realtime=True
                    )
                    
                    # Log the notification
                    mental_log = MentalHealthLog(
                        user_id=user_id,
                        notification_type="activity_reminder"
                    )
                    db.add(mental_log)
                    
                    logger.info(f"Sent mental health notification to user {user.username} (completed {task_count} tasks)")
                    
                except Exception as e:
                    logger.error(f"Error sending mental health notification to user {user_id}: {e}")
                    continue
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in send_mental_health_notifications job: {e}", exc_info=True)
        finally:
            db.close()
    
    async def update_leaderboards(self):
        """Update weekly and monthly leaderboards"""
        db = self.db_session_factory()
        try:
            now = datetime.utcnow()
            
            # Weekly leaderboard
            week_start = now - timedelta(days=7)
            weekly_scores = db.query(
                CoinTransaction.user_id,
                func.sum(CoinTransaction.amount).label('total_earned')
            ).filter(
                CoinTransaction.type == CoinTransactionType.earn,
                CoinTransaction.created_at >= week_start
            ).group_by(CoinTransaction.user_id).order_by(
                func.sum(CoinTransaction.amount).desc()
            ).limit(100).all()
            
            # Clear existing weekly leaderboard
            db.query(Leaderboard).filter(Leaderboard.period == "weekly").delete()
            
            # Add new weekly entries
            for rank, (user_id, score) in enumerate(weekly_scores, 1):
                leaderboard_entry = Leaderboard(
                    period="weekly",
                    user_id=user_id,
                    score=score or 0,
                    rank=rank
                )
                db.add(leaderboard_entry)
            
            # Monthly leaderboard
            month_start = now - timedelta(days=30)
            monthly_scores = db.query(
                CoinTransaction.user_id,
                func.sum(CoinTransaction.amount).label('total_earned')
            ).filter(
                CoinTransaction.type == CoinTransactionType.earn,
                CoinTransaction.created_at >= month_start
            ).group_by(CoinTransaction.user_id).order_by(
                func.sum(CoinTransaction.amount).desc()
            ).limit(100).all()
            
            # Clear existing monthly leaderboard
            db.query(Leaderboard).filter(Leaderboard.period == "monthly").delete()
            
            # Add new monthly entries
            for rank, (user_id, score) in enumerate(monthly_scores, 1):
                leaderboard_entry = Leaderboard(
                    period="monthly",
                    user_id=user_id,
                    score=score or 0,
                    rank=rank
                )
                db.add(leaderboard_entry)
            
            # Award badges for top performers
            await self._award_leaderboard_badges(weekly_scores[:3], "weekly", db)
            await self._award_leaderboard_badges(monthly_scores[:3], "monthly", db)
            
            db.commit()
            logger.info(f"Updated leaderboards: {len(weekly_scores)} weekly, {len(monthly_scores)} monthly entries")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in update_leaderboards job: {e}", exc_info=True)
        finally:
            db.close()
    
    async def _award_leaderboard_badges(self, top_users: List, period: str, db: Session):
        """Award badges to top leaderboard users"""
        badge_names = {
            ("weekly", 1): "Haftalık Şampiyon 🥇",
            ("weekly", 2): "Haftalık İkinci 🥈", 
            ("weekly", 3): "Haftalık Üçüncü 🥉",
            ("monthly", 1): "Aylık Şampiyon 👑",
            ("monthly", 2): "Aylık İkinci 🌟",
            ("monthly", 3): "Aylık Üçüncü ⭐"
        }
        
        for rank, (user_id, score) in enumerate(top_users, 1):
            badge_name = badge_names.get((period, rank))
            if not badge_name:
                continue
            
            # Get or create badge
            badge = db.query(Badge).filter(Badge.name == badge_name).first()
            if not badge:
                badge = Badge(
                    name=badge_name,
                    description=f"{period.title()} lider tablosunda {rank}. sıra ödülü"
                )
                db.add(badge)
                db.flush()
            
            # Check if user already has this badge for this period
            existing = db.query(UserBadge).filter(
                UserBadge.user_id == user_id,
                UserBadge.badge_id == badge.id
            ).first()
            
            if not existing:
                user_badge = UserBadge(
                    user_id=user_id,
                    badge_id=badge.id
                )
                db.add(user_badge)
                
                # Notify user
                await self.notification_service.create_notification(
                    user_id=user_id,
                    title="Yeni Rozet Kazandınız! 🏆",
                    message=f"Tebrikler! '{badge_name}' rozetini kazandınız!",
                    notification_type=NotificationType.BADGE_EARNED,
                    priority=NotificationPriority.HIGH,
                    data={"badge_name": badge_name, "period": period, "rank": rank}
                )
    
    async def process_gdpr_requests(self):
        """Process GDPR data access and deletion requests"""
        db = self.db_session_factory()
        try:
            pending_requests = db.query(GDPRRequest).filter(
                GDPRRequest.status == "pending"
            ).all()
            
            for request in pending_requests:
                try:
                    user = db.query(User).filter(User.id == request.user_id).first()
                    if not user:
                        request.status = "completed"
                        continue
                    
                    if request.request_type == "access":
                        # Prepare user data export
                        user_data = await self._prepare_user_data_export(user, db)
                        
                        # Notify user that data is ready
                        await self.notification_service.create_notification(
                            user_id=user.id,
                            title="Verileriniz Hazır 📄",
                            message="GDPR veri erişim talebiniz hazırlandı. Verilerinizi indirebilirsiniz.",
                            notification_type=NotificationType.GDPR_DATA_READY,
                            priority=NotificationPriority.HIGH,
                            data={"request_id": request.id, "data_size": len(str(user_data))}
                        )
                        
                    elif request.request_type == "delete":
                        # Anonymize user data (GDPR compliant deletion)
                        await self._anonymize_user_data(user, db)
                        
                        # Notify user
                        await self.notification_service.create_notification(
                            user_id=user.id,
                            title="Verileriniz Silindi 🗑️",
                            message="GDPR veri silme talebiniz tamamlandı. Kişisel verileriniz anonimleştirildi.",
                            notification_type=NotificationType.GDPR_DATA_DELETED,
                            priority=NotificationPriority.HIGH
                        )
                    
                    request.status = "completed"
                    request.processed_at = datetime.utcnow()
                    
                    logger.info(f"Processed GDPR {request.request_type} request for user {user.username}")
                    
                except Exception as e:
                    logger.error(f"Error processing GDPR request {request.id}: {e}")
                    request.status = "failed"
                    continue
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in process_gdpr_requests job: {e}", exc_info=True)
        finally:
            db.close()
    
    async def _prepare_user_data_export(self, user: User, db: Session) -> Dict:
        """Prepare user data for GDPR export"""
        # This would typically generate a comprehensive data export
        # For now, return basic structure
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": str(user.created_at),
            "note": "Complete data export would include all user activities, transactions, etc."
        }
    
    async def _anonymize_user_data(self, user: User, db: Session):
        """Anonymize user data for GDPR deletion"""
        # This would implement proper GDPR-compliant data anonymization
        # For now, just clear personal information
        user.email = None
        user.full_name = None
        user.instagram_session_data = None
        user.instagram_pk = None
        user.profile_pic_url = None
        # Note: In real implementation, you'd need to handle related data carefully
    
    async def cleanup_old_data(self):
        """Clean up old logs and temporary data"""
        db = self.db_session_factory()
        try:
            now = datetime.utcnow()
            
            # Clean up old device/IP logs (older than 90 days)
            old_logs_cutoff = now - timedelta(days=90)
            deleted_logs = db.query(DeviceIPLog).filter(
                DeviceIPLog.created_at < old_logs_cutoff
            ).delete()
            
            # Clean up old mental health logs (older than 30 days)
            mental_health_cutoff = now - timedelta(days=30)
            deleted_mental = db.query(MentalHealthLog).filter(
                MentalHealthLog.sent_at < mental_health_cutoff
            ).delete()
            
            # Clean up completed GDPR requests (older than 30 days)
            gdpr_cutoff = now - timedelta(days=30)
            deleted_gdpr = db.query(GDPRRequest).filter(
                GDPRRequest.status == "completed",
                GDPRRequest.processed_at < gdpr_cutoff
            ).delete()
            
            db.commit()
            
            if deleted_logs or deleted_mental or deleted_gdpr:
                logger.info(f"Cleaned up old data: {deleted_logs} device logs, {deleted_mental} mental health logs, {deleted_gdpr} GDPR requests")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in cleanup_old_data job: {e}", exc_info=True)
        finally:
            db.close()

# Global background job manager
background_job_manager = None

def get_background_job_manager(db_session_factory):
    global background_job_manager
    if background_job_manager is None:
        background_job_manager = BackgroundJobManager(db_session_factory)
    return background_job_manager
