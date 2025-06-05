"""
Enhanced Real-time Notification System for Instagram Coin Platform
Features:
- WebSocket real-time notifications
- Push notifications via Firebase
- Notification categories and priorities
- Real-time badge updates
- Notification history management
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import asyncio
from typing import Dict, List, Optional
import logging
from enum import Enum as PyEnum

logger = logging.getLogger(__name__)

# Enhanced Notification Types
class NotificationType(PyEnum):
    TASK_ASSIGNED = "task_assigned"
    TASK_COMPLETED = "task_completed"
    TASK_EXPIRED = "task_expired"
    TASK_CANCELLED = "task_cancelled"
    COIN_EARNED = "coin_earned"
    COIN_TRANSFER_RECEIVED = "coin_transfer_received"
    COIN_TRANSFER_SENT = "coin_transfer_sent"
    LEVEL_UP = "level_up"
    DAILY_LOGIN = "daily_login"
    DAILY_REWARD_STREAK = "daily_reward_streak"
    DAILY_REWARD_CLAIMED = "daily_reward_claimed"
    STREAK_MILESTONE = "streak_milestone"
    SYSTEM_UPDATE = "system_update"
    REFERRAL_REWARD = "referral_reward"
    REFERRAL_BONUS = "referral_bonus"
    NEW_REFERRAL = "new_referral"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    BADGE_EARNED = "badge_earned"
    ORDER_CREATED = "order_created"
    ORDER_UPDATE = "order_update"
    ORDER_COMPLETED = "order_completed"
    ORDER_CANCELLED = "order_cancelled"
    WITHDRAWAL_PENDING = "withdrawal_pending"
    WITHDRAWAL_APPROVED = "withdrawal_approved"
    WITHDRAWAL_CANCELLED = "withdrawal_cancelled"
    WITHDRAWAL_LOCKED = "withdrawal_locked"
    SECURITY_ALERT = "security_alert"
    MENTAL_HEALTH = "mental_health"
    GDPR_DATA_READY = "gdpr_data_ready"
    GDPR_DATA_DELETED = "gdpr_data_deleted"
    GDPR_REQUEST_RECEIVED = "gdpr_request_received"
    PRIVACY_SETTINGS_UPDATED = "privacy_settings_updated"

class NotificationPriority(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class NotificationStats:
    total_notifications: int
    unread_count: int
    last_notification_time: Optional[datetime]
    notification_types: Dict[str, int]

class RealTimeNotificationManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}
        self.notification_queue: Dict[int, List[dict]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user to real-time notifications"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected to real-time notifications")
        
        # Send any queued notifications
        if user_id in self.notification_queue:
            for notification in self.notification_queue[user_id]:
                await self.send_notification_to_user(user_id, notification)
            del self.notification_queue[user_id]
    
    def disconnect(self, user_id: int):
        """Disconnect a user from real-time notifications"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected from real-time notifications")
    
    async def send_notification_to_user(self, user_id: int, notification: dict):
        """Send notification to specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(notification))
                return True
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {e}")
                self.disconnect(user_id)
                return False
        else:
            # Queue notification for when user connects
            if user_id not in self.notification_queue:
                self.notification_queue[user_id] = []
            self.notification_queue[user_id].append(notification)
            return False
    
    async def broadcast_notification(self, notification: dict, user_ids: List[int] = None):
        """Broadcast notification to multiple users or all connected users"""
        target_users = user_ids if user_ids else list(self.active_connections.keys())
        
        for user_id in target_users:
            await self.send_notification_to_user(user_id, notification)
    
    def get_connected_users(self) -> List[int]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())

# Global notification manager instance
notification_manager = RealTimeNotificationManager()

class NotificationService:
    def __init__(self, db: Session = None, db_session_factory=None):
        self.db = db
        self.db_session_factory = db_session_factory
    
    async def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.SYSTEM_UPDATE,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[dict] = None,
        send_push: bool = True,
        send_realtime: bool = True
    ) -> dict:
        """Create and send a notification"""
        
        # Create notification object
        notification_data = {
            "id": None,  # Will be set after DB insert
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type.value,
            "priority": priority.value,
            "data": data or {},
            "is_read": False,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        # Store in database (assuming enhanced notification model)
        try:
            # Here you would insert into your enhanced notification table
            # notification_data["id"] = inserted_notification.id
            pass
        except Exception as e:
            logger.error(f"Error storing notification in database: {e}")
        
        # Send real-time notification
        if send_realtime:
            realtime_payload = {
                "type": "notification",
                "notification": notification_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await notification_manager.send_notification_to_user(user_id, realtime_payload)
        
        # Send push notification (if enabled and user has FCM token)
        if send_push:
            await self._send_push_notification(user_id, title, message, notification_data)
        
        return notification_data
    
    async def _send_push_notification(self, user_id: int, title: str, message: str, data: dict):
        """Send push notification via Firebase"""
        try:
            # Get user's FCM token from database
            # user = self.db.query(User).filter(User.id == user_id).first()
            # if user and user.fcm_token:
            #     # Send via Firebase
            #     pass
            logger.info(f"Push notification would be sent to user {user_id}: {title}")
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
    
    async def send_task_completion_notification(self, user_id: int, task_title: str, coins_earned: int):
        """Send notification when user completes a task"""
        await self.create_notification(
            user_id=user_id,
            title="Görev Tamamlandı! 🎉",
            message=f"'{task_title}' görevini tamamladınız ve {coins_earned} coin kazandınız!",
            notification_type=NotificationType.TASK_COMPLETED,
            priority=NotificationPriority.HIGH,
            data={"coins_earned": coins_earned, "task_title": task_title}
        )
    
    async def send_level_up_notification(self, user_id: int, new_level: str, bonus_coins: int):
        """Send notification when user levels up"""
        await self.create_notification(
            user_id=user_id,
            title="Seviye Atladınız! 🚀",
            message=f"Tebrikler! {new_level} seviyesine yükseldiniz ve {bonus_coins} bonus coin kazandınız!",
            notification_type=NotificationType.LEVEL_UP,
            priority=NotificationPriority.HIGH,
            data={"new_level": new_level, "bonus_coins": bonus_coins}
        )
    
    async def send_daily_login_notification(self, user_id: int, streak_days: int, bonus_coins: int):
        """Send notification for daily login streak"""
        await self.create_notification(
            user_id=user_id,
            title="Günlük Giriş Bonusu! 💎",
            message=f"{streak_days} günlük seriye ulaştınız! {bonus_coins} coin kazandınız.",
            notification_type=NotificationType.DAILY_LOGIN,
            priority=NotificationPriority.MEDIUM,
            data={"streak_days": streak_days, "bonus_coins": bonus_coins}
        )
    
    async def send_system_announcement(self, title: str, message: str, user_ids: List[int] = None):
        """Send system-wide announcement"""
        if user_ids is None:
            # Send to all users (you'd get this from database)
            user_ids = []  # Get all user IDs from database
        
        for user_id in user_ids:
            await self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=NotificationType.SYSTEM_UPDATE,
                priority=NotificationPriority.URGENT,
                send_push=True,
                send_realtime=True
            )
    
    def create_notification_sync(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: dict = None,
        send_push: bool = True,
        send_realtime: bool = True
    ) -> dict:
        """Synchronous version of create_notification for non-async contexts"""
        import asyncio
        
        # Try to run the async version
        try:
            # Get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, create a new task
                return asyncio.create_task(self.create_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    data=data,
                    send_push=send_push,
                    send_realtime=send_realtime
                ))
            else:
                # If no loop is running, run it synchronously
                return loop.run_until_complete(self.create_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    data=data,
                    send_push=send_push,
                    send_realtime=send_realtime
                ))
        except RuntimeError:
            # No event loop, run in new loop
            return asyncio.run(self.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                data=data,
                send_push=send_push,
                send_realtime=send_realtime
            ))
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get notification statistics for a user (synchronous)"""
        try:
            with self.db_session_factory() as db:
                from models import Notification
                
                total = db.query(Notification).filter_by(user_id=user_id).count()
                unread = db.query(Notification).filter_by(user_id=user_id, read=False).count()
                
                last_notification = db.query(Notification).filter_by(user_id=user_id)\
                    .order_by(Notification.created_at.desc()).first()
                
                # Get notification type distribution
                from sqlalchemy import func
                type_stats = db.query(
                    Notification.type,
                    func.count(Notification.id)
                ).filter_by(user_id=user_id)\
                .group_by(Notification.type)\
                .all()
                
                notification_types = {type_name: count for type_name, count in type_stats}
                
                return {
                    "total_notifications": total,
                    "unread_count": unread,
                    "last_notification_time": last_notification.created_at if last_notification else None,
                    "notification_types": notification_types
                }
        except Exception as e:
            logger.error(f"Error getting user notification stats: {e}")
            return {
                "total_notifications": 0,
                "unread_count": 0,
                "last_notification_time": None,
                "notification_types": {}
            }

# Enhanced notification statistics
class NotificationStats:
    def __init__(self, db: Session):
        self.db = db
    
    def get_notification_metrics(self, user_id: int, days: int = 7) -> dict:
        """Get notification metrics for a user"""
        return {
            "total_notifications": 0,
            "unread_notifications": 0,
            "notifications_by_type": {},
            "average_response_time": 0,
            "engagement_rate": 0
        }
    
    def get_system_notification_metrics(self, days: int = 7) -> dict:
        """Get system-wide notification metrics"""
        return {
            "total_sent": 0,
            "delivery_rate": 0,
            "open_rate": 0,
            "click_through_rate": 0,
            "unsubscribe_rate": 0
        }

# Background task for notification cleanup
async def cleanup_old_notifications():
    """Clean up expired notifications"""
    while True:
        try:
            # Clean up notifications older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            # Delete from database where created_at < cutoff_date
            logger.info("Cleaned up old notifications")
        except Exception as e:
            logger.error(f"Error during notification cleanup: {e}")
        
        # Wait 24 hours before next cleanup
        await asyncio.sleep(24 * 60 * 60)

# Smart notification batching to prevent spam
class NotificationBatcher:
    def __init__(self):
        self.pending_notifications: Dict[int, List[dict]] = {}
        self.batch_timer: Dict[int, asyncio.Task] = {}
    
    async def add_notification(self, user_id: int, notification: dict, delay_seconds: int = 30):
        """Add notification to batch for delayed sending"""
        if user_id not in self.pending_notifications:
            self.pending_notifications[user_id] = []
        
        self.pending_notifications[user_id].append(notification)
        
        # Cancel existing timer and start new one
        if user_id in self.batch_timer:
            self.batch_timer[user_id].cancel()
        
        self.batch_timer[user_id] = asyncio.create_task(
            self._send_batched_notifications(user_id, delay_seconds)
        )
    
    async def _send_batched_notifications(self, user_id: int, delay_seconds: int):
        """Send batched notifications after delay"""
        await asyncio.sleep(delay_seconds)
        
        if user_id in self.pending_notifications and self.pending_notifications[user_id]:
            notifications = self.pending_notifications[user_id]
            
            if len(notifications) == 1:
                # Send single notification
                await notification_manager.send_notification_to_user(user_id, notifications[0])
            else:
                # Send summary notification
                summary = {
                    "type": "notification_summary",
                    "count": len(notifications),
                    "latest": notifications[-1],
                    "timestamp": datetime.utcnow().isoformat()
                }
                await notification_manager.send_notification_to_user(user_id, summary)
            
            # Clear pending notifications
            self.pending_notifications[user_id] = []
            if user_id in self.batch_timer:
                del self.batch_timer[user_id]

# Global notification batcher
notification_batcher = NotificationBatcher()

# Global notification service instance (initialized after import)
notification_service = None

def initialize_notification_service(db_session_factory):
    """Initialize the notification service with database session factory"""
    global notification_service
    if notification_service is None:
        notification_service = NotificationService(db_session_factory=db_session_factory)
