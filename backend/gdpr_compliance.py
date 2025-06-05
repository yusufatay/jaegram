"""
GDPR/KVKK Compliance System
- Data access requests
- Data deletion (right to be forgotten)
- Data export in machine-readable format
- Consent management
- Data audit trails
- Privacy settings
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from models import (
    User, GDPRRequest, Task, Order, CoinTransaction, Notification,
    DeviceIPLog, UserFCMToken, InstagramCredential, ValidationLog,
    Referral, UserBadge, UserSocial, NotificationSetting
)
from enhanced_notifications import NotificationService, NotificationType, NotificationPriority
import zipfile
import io
import csv

logger = logging.getLogger(__name__)

class GDPRComplianceManager:
    """GDPR/KVKK compliance management system"""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.notification_service = NotificationService(db_session_factory)
        
        # Data retention periods (in days)
        self.retention_periods = {
            'logs': 90,          # Device/IP logs
            'notifications': 365, # Notifications
            'transactions': 2555, # 7 years for financial records
            'gdpr_requests': 90   # GDPR request logs
        }
    
    async def request_data_access(self, user_id: int) -> Dict[str, Any]:
        """Process user's data access request (GDPR Article 15)"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Check for existing pending request
            existing_request = db.query(GDPRRequest).filter(
                GDPRRequest.user_id == user_id,
                GDPRRequest.request_type == "access",
                GDPRRequest.status == "pending"
            ).first()
            
            if existing_request:
                return {
                    "success": False, 
                    "message": "Bekleyen bir veri erişim talebiniz zaten var",
                    "request_id": existing_request.id
                }
            
            # Create new request
            gdpr_request = GDPRRequest(
                user_id=user_id,
                request_type="access",
                status="pending"
            )
            db.add(gdpr_request)
            db.commit()
            
            # Notify user
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Veri Erişim Talebi Alındı 📄",
                message="GDPR kapsamındaki veri erişim talebiniz alındı. 30 gün içinde işleme alınacak.",
                notification_type=NotificationType.GDPR_REQUEST_RECEIVED,
                priority=NotificationPriority.MEDIUM,
                data={"request_id": gdpr_request.id, "request_type": "access"}
            )
            
            logger.info(f"GDPR data access request created for user {user.username} (ID: {gdpr_request.id})")
            
            return {
                "success": True,
                "message": "Veri erişim talebiniz oluşturuldu",
                "request_id": gdpr_request.id,
                "processing_time": "30 gün içinde"
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating data access request for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Veri erişim talebi oluşturulurken hata oluştu"}
        finally:
            db.close()
    
    async def request_data_deletion(self, user_id: int) -> Dict[str, Any]:
        """Process user's data deletion request (GDPR Article 17 - Right to be forgotten)"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Check for existing pending request
            existing_request = db.query(GDPRRequest).filter(
                GDPRRequest.user_id == user_id,
                GDPRRequest.request_type == "delete",
                GDPRRequest.status == "pending"
            ).first()
            
            if existing_request:
                return {
                    "success": False, 
                    "message": "Bekleyen bir veri silme talebiniz zaten var",
                    "request_id": existing_request.id
                }
            
            # Create new request
            gdpr_request = GDPRRequest(
                user_id=user_id,
                request_type="delete",
                status="pending"
            )
            db.add(gdpr_request)
            db.commit()
            
            # Notify user
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Veri Silme Talebi Alındı 🗑️",
                message="GDPR kapsamındaki veri silme talebiniz alındı. 30 gün içinde işleme alınacak.",
                notification_type=NotificationType.GDPR_REQUEST_RECEIVED,
                priority=NotificationPriority.HIGH,
                data={"request_id": gdpr_request.id, "request_type": "delete"}
            )
            
            logger.info(f"GDPR data deletion request created for user {user.username} (ID: {gdpr_request.id})")
            
            return {
                "success": True,
                "message": "Veri silme talebiniz oluşturuldu",
                "request_id": gdpr_request.id,
                "processing_time": "30 gün içinde",
                "warning": "Bu işlem geri alınamaz. Tüm verileriniz kalıcı olarak silinecektir."
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating data deletion request for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Veri silme talebi oluşturulurken hata oluştu"}
        finally:
            db.close()
    
    async def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """Export all user data in machine-readable format"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Collect all user data
            user_data = await self._collect_all_user_data(user, db)
            
            # Create data export
            export_data = {
                "export_info": {
                    "user_id": user.id,
                    "username": user.username,
                    "export_date": datetime.utcnow().isoformat(),
                    "data_format": "JSON",
                    "gdpr_compliant": True
                },
                "personal_data": user_data["personal"],
                "activity_data": user_data["activity"],
                "financial_data": user_data["financial"],
                "social_data": user_data["social"],
                "technical_data": user_data["technical"],
                "privacy_settings": user_data["privacy"]
            }
            
            # Convert to JSON
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
            
            return {
                "success": True,
                "data": json_data,
                "size_bytes": len(json_data.encode('utf-8')),
                "export_date": datetime.utcnow().isoformat(),
                "format": "application/json"
            }
            
        except Exception as e:
            logger.error(f"Error exporting data for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Veri dışa aktarılırken hata oluştu"}
        finally:
            db.close()
    
    async def _collect_all_user_data(self, user: User, db: Session) -> Dict[str, Any]:
        """Collect all user data from all tables"""
        
        # Personal data
        personal_data = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "profile_pic_url": user.profile_pic_url,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active,
            "email_verified": user.email_verified
        }
        
        # Instagram data
        instagram_cred = db.query(InstagramCredential).filter(
            InstagramCredential.user_id == user.id
        ).first()
        
        if instagram_cred:
            personal_data["instagram"] = {
                "instagram_user_id": instagram_cred.instagram_user_id,
                "username": instagram_cred.username,
                "profile_picture_url": instagram_cred.profile_picture_url,
                "connected_at": instagram_cred.created_at
            }
        
        # Activity data
        tasks = db.query(Task).filter(Task.assigned_user_id == user.id).all()
        orders = db.query(Order).filter(Order.user_id == user.id).all()
        
        activity_data = {
            "tasks": [
                {
                    "id": task.id,
                    "order_id": task.order_id,
                    "status": task.status.value if task.status else None,
                    "assigned_at": task.assigned_at,
                    "completed_at": task.completed_at,
                    "expires_at": task.expires_at
                } for task in tasks
            ],
            "orders": [
                {
                    "id": order.id,
                    "post_url": order.post_url,
                    "order_type": order.order_type.value if order.order_type else None,
                    "target_count": order.target_count,
                    "completed_count": order.completed_count,
                    "status": order.status,
                    "created_at": order.created_at
                } for order in orders
            ]
        }
        
        # Financial data
        transactions = db.query(CoinTransaction).filter(
            CoinTransaction.user_id == user.id
        ).all()
        
        financial_data = {
            "current_balance": user.coin_balance,
            "transactions": [
                {
                    "id": tx.id,
                    "amount": tx.amount,
                    "type": tx.type.value if tx.type else None,
                    "created_at": tx.created_at,
                    "note": tx.note
                } for tx in transactions
            ]
        }
        
        # Social data
        user_social = db.query(UserSocial).filter(UserSocial.user_id == user.id).first()
        referrals_made = db.query(Referral).filter(Referral.referrer_id == user.id).all()
        referral_received = db.query(Referral).filter(Referral.referred_id == user.id).first()
        badges = db.query(UserBadge).filter(UserBadge.user_id == user.id).all()
        
        social_data = {
            "referral_code": user_social.referral_code if user_social else None,
            "total_referrals": user_social.total_referrals if user_social else 0,
            "total_transferred": user_social.total_transferred if user_social else 0,
            "total_received": user_social.total_received if user_social else 0,
            "referred_by": referral_received.referrer_id if referral_received else None,
            "referrals_made": [
                {
                    "referred_user_id": ref.referred_id,
                    "created_at": ref.created_at,
                    "bonus_given": ref.bonus_given
                } for ref in referrals_made
            ],
            "badges": [
                {
                    "badge_id": badge.badge_id,
                    "awarded_at": badge.awarded_at
                } for badge in badges
            ]
        }
        
        # Technical data
        device_logs = db.query(DeviceIPLog).filter(DeviceIPLog.user_id == user.id).all()
        fcm_tokens = db.query(UserFCMToken).filter(UserFCMToken.user_id == user.id).all()
        validation_logs = db.query(ValidationLog).filter(ValidationLog.user_id == user.id).all()
        
        technical_data = {
            "device_logs": [
                {
                    "device_info": log.device_info,
                    "ip_address": log.ip_address,
                    "action": log.action,
                    "created_at": log.created_at
                } for log in device_logs
            ],
            "fcm_tokens": [
                {
                    "token": token.token[:20] + "..." if len(token.token) > 20 else token.token,  # Truncate for privacy
                    "created_at": token.created_at
                } for token in fcm_tokens
            ],
            "validation_logs": [
                {
                    "task_id": log.task_id,
                    "status": log.status,
                    "details": log.details,
                    "created_at": log.created_at
                } for log in validation_logs
            ]
        }
        
        # Privacy settings
        notification_settings = db.query(NotificationSetting).filter(
            NotificationSetting.user_id == user.id
        ).first()
        
        privacy_data = {
            "notification_settings": {
                "push_enabled": notification_settings.push_enabled if notification_settings else True,
                "email_enabled": notification_settings.email_enabled if notification_settings else True,
                "sms_enabled": notification_settings.sms_enabled if notification_settings else False,
                "order_notifications": notification_settings.order_notifications if notification_settings else True,
                "task_notifications": notification_settings.task_notifications if notification_settings else True,
                "reward_notifications": notification_settings.reward_notifications if notification_settings else True,
                "system_notifications": notification_settings.system_notifications if notification_settings else True,
                "mental_health_notifications": notification_settings.mental_health_notifications if notification_settings else True
            }
        }
        
        return {
            "personal": personal_data,
            "activity": activity_data,
            "financial": financial_data,
            "social": social_data,
            "technical": technical_data,
            "privacy": privacy_data
        }
    
    async def anonymize_user_data(self, user_id: int) -> Dict[str, Any]:
        """Anonymize user data (GDPR-compliant deletion)"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            original_username = user.username
            
            # Anonymize personal data
            user.username = f"deleted_user_{user.id}_{int(datetime.utcnow().timestamp())}"
            user.email = None
            user.full_name = None
            user.profile_pic_url = None
            user.password_hash = None
            user.instagram_session_data = None
            user.instagram_pk = None
            user.instagram_username = None
            user.email_verification_code = None
            user.two_factor_secret = None
            user.is_active = False
            
            # Remove Instagram credentials
            instagram_cred = db.query(InstagramCredential).filter(
                InstagramCredential.user_id == user_id
            ).first()
            if instagram_cred:
                db.delete(instagram_cred)
            
            # Remove FCM tokens
            db.query(UserFCMToken).filter(UserFCMToken.user_id == user_id).delete()
            
            # Anonymize device logs (keep for legal/security purposes but remove personal info)
            device_logs = db.query(DeviceIPLog).filter(DeviceIPLog.user_id == user_id).all()
            for log in device_logs:
                log.device_info = "anonymized"
                if log.ip_address:
                    # Keep first 3 octets, anonymize last octet
                    ip_parts = log.ip_address.split('.')
                    if len(ip_parts) == 4:
                        log.ip_address = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0"
            
            # Remove personal notifications but keep system ones for audit
            personal_notifications = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.type.in_(['order', 'task', 'reward'])
            )
            personal_notifications.delete()
            
            # Anonymize remaining notifications
            remaining_notifications = db.query(Notification).filter(
                Notification.user_id == user_id
            ).all()
            for notif in remaining_notifications:
                notif.message = "User data anonymized"
                notif.title = "Data anonymized"
            
            # Keep financial records for legal compliance but anonymize personal references
            transactions = db.query(CoinTransaction).filter(
                CoinTransaction.user_id == user_id
            ).all()
            for tx in transactions:
                if tx.note and original_username in tx.note:
                    tx.note = tx.note.replace(original_username, "anonymized_user")
            
            # Remove social data
            db.query(UserSocial).filter(UserSocial.user_id == user_id).delete()
            db.query(UserBadge).filter(UserBadge.user_id == user_id).delete()
            db.query(NotificationSetting).filter(NotificationSetting.user_id == user_id).delete()
            
            # Update referrals (set to null but keep for other user's records)
            referrals_as_referrer = db.query(Referral).filter(Referral.referrer_id == user_id).all()
            for ref in referrals_as_referrer:
                ref.referrer_id = None  # Anonymize but keep record
            
            referrals_as_referred = db.query(Referral).filter(Referral.referred_id == user_id).all()
            for ref in referrals_as_referred:
                ref.referred_id = None  # Anonymize but keep record
            
            # Mark GDPR request as completed
            gdpr_request = db.query(GDPRRequest).filter(
                GDPRRequest.user_id == user_id,
                GDPRRequest.request_type == "delete",
                GDPRRequest.status == "pending"
            ).first()
            
            if gdpr_request:
                gdpr_request.status = "completed"
                gdpr_request.processed_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"User data anonymized for user ID {user_id} (formerly {original_username})")
            
            return {
                "success": True,
                "message": "Kullanıcı verileri başarıyla anonimleştirildi",
                "anonymized_username": user.username,
                "anonymization_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error anonymizing user data for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Veri anonimleştirme sırasında hata oluştu"}
        finally:
            db.close()
    
    async def get_gdpr_request_status(self, user_id: int) -> Dict[str, Any]:
        """Get status of user's GDPR requests"""
        db = self.db_session_factory()
        try:
            requests = db.query(GDPRRequest).filter(
                GDPRRequest.user_id == user_id
            ).order_by(GDPRRequest.created_at.desc()).all()
            
            request_data = []
            for req in requests:
                request_data.append({
                    "id": req.id,
                    "type": req.request_type,
                    "status": req.status,
                    "created_at": req.created_at.isoformat() if req.created_at else None,
                    "processed_at": req.processed_at.isoformat() if req.processed_at else None
                })
            
            return {
                "success": True,
                "user_id": user_id,
                "requests": request_data,
                "total_requests": len(request_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting GDPR request status for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "GDPR talep durumu alınırken hata oluştu"}
        finally:
            db.close()
    
    async def update_privacy_settings(self, user_id: int, settings: Dict[str, bool]) -> Dict[str, Any]:
        """Update user's privacy and notification settings"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Get or create notification settings
            notification_settings = db.query(NotificationSetting).filter(
                NotificationSetting.user_id == user_id
            ).first()
            
            if not notification_settings:
                notification_settings = NotificationSetting(user_id=user_id)
                db.add(notification_settings)
            
            # Update settings
            valid_settings = [
                'push_enabled', 'email_enabled', 'sms_enabled',
                'order_notifications', 'task_notifications', 'reward_notifications',
                'system_notifications', 'mental_health_notifications'
            ]
            
            updated_settings = {}
            for setting_name, value in settings.items():
                if setting_name in valid_settings and isinstance(value, bool):
                    setattr(notification_settings, setting_name, value)
                    updated_settings[setting_name] = value
            
            db.commit()
            
            # Notify user of privacy settings update
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Gizlilik Ayarları Güncellendi 🔒",
                message="Bildirim ve gizlilik ayarlarınız başarıyla güncellendi.",
                notification_type=NotificationType.PRIVACY_SETTINGS_UPDATED,
                priority=NotificationPriority.LOW,
                data={"updated_settings": updated_settings}
            )
            
            return {
                "success": True,
                "message": "Gizlilik ayarları güncellendi",
                "updated_settings": updated_settings
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating privacy settings for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Gizlilik ayarları güncellenirken hata oluştu"}
        finally:
            db.close()

# Global GDPR compliance manager
gdpr_compliance_manager = None

def get_gdpr_compliance_manager(db_session_factory):
    global gdpr_compliance_manager
    if gdpr_compliance_manager is None:
        gdpr_compliance_manager = GDPRComplianceManager(db_session_factory)
    return gdpr_compliance_manager
