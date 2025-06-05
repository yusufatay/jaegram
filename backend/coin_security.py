"""
Advanced Coin Security and Withdrawal System
- Secure withdrawal processing with 48h lock
- Suspicious activity detection
- Multi-layer security checks
- Locked coin management
- Real-time fraud detection
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from models import (
    User, CoinTransaction, CoinWithdrawalRequest, DeviceIPLog,
    Task, TaskStatus, CoinTransactionType, InstagramProfile, CoinWithdrawalVerification
)
from enhanced_notifications import NotificationService, NotificationType, NotificationPriority
from instagram_service import InstagramAPIService
import hashlib
import json
import random

logger = logging.getLogger(__name__)

class CoinSecurityManager:
    """Advanced coin security and withdrawal management"""
    
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory
        self.notification_service = NotificationService(db_session_factory)
        
        # Security thresholds
        self.max_hourly_earnings = 500  # Max coins per hour
        self.max_daily_earnings = 2000  # Max coins per day
        self.min_account_age_days = 7  # Minimum account age for withdrawal
        self.min_tasks_for_withdrawal = 50  # Minimum completed tasks
        self.withdrawal_lock_hours = 48  # Hours to lock withdrawal
        self.suspicious_pattern_threshold = 0.8  # Fraud score threshold
    
    async def request_withdrawal(self, user_id: int, amount: int, device_info: Optional[str] = None, 
                               ip_address: Optional[str] = None) -> Dict[str, Any]:
        """Process withdrawal request with security checks"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Basic validation
            if amount <= 0:
                return {"success": False, "message": "Geçersiz miktar"}
            
            if user.coin_balance < amount:
                return {"success": False, "message": "Yetersiz bakiye"}
            
            # Security checks
            security_check = await self._perform_security_checks(user, amount, db)
            if not security_check["passed"]:
                return {
                    "success": False, 
                    "message": security_check["message"],
                    "security_issue": True
                }
            
            # Check for existing pending withdrawals
            existing_request = db.query(CoinWithdrawalRequest).filter(
                CoinWithdrawalRequest.user_id == user_id,
                CoinWithdrawalRequest.status.in_(["pending", "locked"])
            ).first()
            
            if existing_request:
                return {
                    "success": False, 
                    "message": "Bekleyen veya kilitli bir çekim talebiniz zaten var"
                }
            
            # Create withdrawal request
            withdrawal_request = CoinWithdrawalRequest(
                user_id=user_id,
                amount=amount,
                status="pending"
            )
            
            # Calculate fraud score
            fraud_score = await self._calculate_fraud_score(user, db)
            
            if fraud_score > self.suspicious_pattern_threshold:
                withdrawal_request.status = "locked"
                withdrawal_request.suspicious = True
                withdrawal_request.locked_until = datetime.utcnow() + timedelta(hours=self.withdrawal_lock_hours * 2)
                
                # Log suspicious activity
                device_log = DeviceIPLog(
                    user_id=user_id,
                    device_info=device_info,
                    ip_address=ip_address,
                    action=f"suspicious_withdrawal_request_fraud_score_{fraud_score:.2f}"
                )
                db.add(device_log)
                
                # Notify user
                await self.notification_service.create_notification(
                    user_id=user_id,
                    title="Çekim Talebi Güvenlik İncelemesinde 🔒",
                    message=f"Güvenlik nedeniyle çekim talebiniz incelemeye alındı. {withdrawal_request.locked_until.strftime('%d.%m.%Y %H:%M')} tarihine kadar bekleyiniz.",
                    notification_type=NotificationType.WITHDRAWAL_LOCKED,
                    priority=NotificationPriority.HIGH,
                    data={"amount": amount, "fraud_score": fraud_score}
                )
                
                # Notify admins
                await self._notify_admins_suspicious_activity(user, fraud_score, amount, db)
                
            else:
                # Normal processing - lock for 48 hours
                withdrawal_request.locked_until = datetime.utcnow() + timedelta(hours=self.withdrawal_lock_hours)
                
                # Lock coins in user balance
                locked_amount = min(amount, user.coin_balance)
                user.coin_balance -= locked_amount
                
                # Create locked coin transaction
                locked_transaction = CoinTransaction(
                    user_id=user_id,
                    amount=-locked_amount,
                    type=CoinTransactionType.withdraw,
                    note=f"Çekim talebi için kilitlendi (Talep #{withdrawal_request.id})"
                )
                db.add(locked_transaction)
                
                # Notify user
                await self.notification_service.create_notification(
                    user_id=user_id,
                    title="Çekim Talebi Alındı ⏳",
                    message=f"{amount} coin çekim talebiniz alındı. 48 saat içinde işleme alınacak.",
                    notification_type=NotificationType.WITHDRAWAL_PENDING,
                    priority=NotificationPriority.MEDIUM,
                    data={"amount": amount, "unlock_time": withdrawal_request.locked_until.isoformat()}
                )
            
            # Log withdrawal request
            device_log = DeviceIPLog(
                user_id=user_id,
                device_info=device_info,
                ip_address=ip_address,
                action=f"withdrawal_request_{amount}_coins"
            )
            db.add(device_log)
            
            db.add(withdrawal_request)
            db.commit()
            
            logger.info(f"Withdrawal request created for user {user.username}: {amount} coins, status: {withdrawal_request.status}")
            
            return {
                "success": True,
                "message": "Çekim talebi oluşturuldu",
                "withdrawal_id": withdrawal_request.id,
                "status": withdrawal_request.status,
                "locked_until": withdrawal_request.locked_until.isoformat() if withdrawal_request.locked_until else None
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error processing withdrawal request for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Çekim talebi işlenirken hata oluştu"}
        finally:
            db.close()
    
    async def request_withdrawal_with_instagram_verification(
        self, 
        user_id: int, 
        amount: int, 
        device_info: str, 
        ip_address: str,
        instagram_verification_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request coin withdrawal with mandatory Instagram verification
        """
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Check if user has verified Instagram account
            instagram_profile = db.query(InstagramProfile).filter(
                InstagramProfile.user_id == user_id,
                InstagramProfile.is_verified == True
            ).first()
            
            if not instagram_profile:
                return {
                    "success": False, 
                    "message": "Coin çekimi için önce Instagram hesabınızı doğrulamanız gerekiyor",
                    "requires_instagram_verification": True
                }
            
            # Verify Instagram account is still active
            instagram_service = InstagramAPIService()
            try:
                profile_data = await instagram_service.get_user_profile_data(user, db)
                if not profile_data or profile_data.get('is_private') is None:
                    # Instagram account no longer accessible
                    instagram_profile.is_verified = False
                    db.commit()
                    return {
                        "success": False,
                        "message": "Instagram hesabınız artık erişilebilir değil. Lütfen tekrar doğrulayın",
                        "requires_instagram_verification": True
                    }
            except Exception as e:
                logger.warning(f"Could not verify Instagram account for user {user_id}: {e}")
                return {
                    "success": False,
                    "message": "Instagram hesabınız doğrulanamadı. Lütfen tekrar bağlayın",
                    "requires_instagram_verification": True
                }
            
            # Check additional security requirements for large withdrawals
            if amount > 1000:  # Large withdrawal threshold
                # Require additional verification for large amounts
                if not instagram_verification_code:
                    verification_code = self._generate_verification_code()
                    
                    # Store verification code temporarily
                    verification = CoinWithdrawalVerification(
                        user_id=user_id,
                        verification_code=verification_code,
                        amount=amount,
                        expires_at=datetime.utcnow() + timedelta(minutes=15)
                    )
                    db.add(verification)
                    db.commit()
                    
                    # Send verification through Instagram DM or post requirement
                    await self._send_instagram_verification(user_id, verification_code, instagram_profile)
                    
                    return {
                        "success": False,
                        "message": f"Büyük miktarlı çekimler için ek doğrulama gereklidir. Instagram hesabınızda paylaştığımız kodu girin.",
                        "requires_verification_code": True,
                        "verification_method": "instagram_post"
                    }
                else:
                    # Verify the provided code
                    verification = db.query(CoinWithdrawalVerification).filter(
                        CoinWithdrawalVerification.user_id == user_id,
                        CoinWithdrawalVerification.verification_code == instagram_verification_code,
                        CoinWithdrawalVerification.expires_at > datetime.utcnow(),
                        CoinWithdrawalVerification.is_used == False
                    ).first()
                    
                    if not verification:
                        return {
                            "success": False,
                            "message": "Geçersiz veya süresi dolmuş doğrulama kodu"
                        }
                    
                    # Mark verification as used
                    verification.is_used = True
                    db.commit()
            
            # Enhanced fraud detection with Instagram data
            fraud_score = await self._calculate_enhanced_fraud_score(user, instagram_profile, db)
            
            # Proceed with standard withdrawal request
            return await self.request_withdrawal(user_id, amount, device_info, ip_address)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error in Instagram-verified withdrawal request: {e}")
            return {"success": False, "message": "Sistem hatası oluştu"}
        finally:
            db.close()

    async def _perform_security_checks(self, user: User, amount: int, db: Session) -> Dict[str, Any]:
        """Perform comprehensive security checks"""
        now = datetime.utcnow()
        
        # Check account age
        if user.created_at:
            account_age = (now - user.created_at).days
            if account_age < self.min_account_age_days:
                return {
                    "passed": False,
                    "message": f"Hesabınız en az {self.min_account_age_days} günlük olmalı"
                }
        
        # Check minimum completed tasks
        completed_tasks = db.query(Task).filter(
            Task.assigned_user_id == user.id,
            Task.status == TaskStatus.completed
        ).count()
        
        if completed_tasks < self.min_tasks_for_withdrawal:
            return {
                "passed": False,
                "message": f"En az {self.min_tasks_for_withdrawal} görev tamamlamalısınız"
            }
        
        # Check hourly earnings limit
        one_hour_ago = now - timedelta(hours=1)
        hourly_earnings = db.query(func.sum(CoinTransaction.amount)).filter(
            CoinTransaction.user_id == user.id,
            CoinTransaction.type == CoinTransactionType.earn,
            CoinTransaction.created_at >= one_hour_ago
        ).scalar() or 0
        
        if hourly_earnings > self.max_hourly_earnings:
            return {
                "passed": False,
                "message": "Saatlik kazanç limitini aştınız. Lütfen daha sonra tekrar deneyin"
            }
        
        # Check daily earnings limit
        one_day_ago = now - timedelta(days=1)
        daily_earnings = db.query(func.sum(CoinTransaction.amount)).filter(
            CoinTransaction.user_id == user.id,
            CoinTransaction.type == CoinTransactionType.earn,
            CoinTransaction.created_at >= one_day_ago
        ).scalar() or 0
        
        if daily_earnings > self.max_daily_earnings:
            return {
                "passed": False,
                "message": "Günlük kazanç limitini aştınız"
            }
        
        # Check for rapid consecutive withdrawals
        recent_withdrawals = db.query(CoinWithdrawalRequest).filter(
            CoinWithdrawalRequest.user_id == user.id,
            CoinWithdrawalRequest.requested_at >= now - timedelta(hours=24)
        ).count()
        
        if recent_withdrawals >= 3:
            return {
                "passed": False,
                "message": "24 saat içinde çok fazla çekim talebi oluşturdunuz"
            }
        
        return {"passed": True, "message": "Güvenlik kontrolleri başarılı"}
    
    async def _calculate_fraud_score(self, user: User, db: Session) -> float:
        """Calculate fraud risk score (0.0 to 1.0)"""
        score = 0.0
        now = datetime.utcnow()
        
        # Factor 1: Account age (newer accounts = higher risk)
        if user.created_at:
            account_age_days = (now - user.created_at).days
            if account_age_days < 1:
                score += 0.4
            elif account_age_days < 7:
                score += 0.2
            elif account_age_days < 30:
                score += 0.1
        
        # Factor 2: Task completion patterns
        recent_tasks = db.query(Task).filter(
            Task.assigned_user_id == user.id,
            Task.status == TaskStatus.completed,
            Task.completed_at >= now - timedelta(hours=24)
        ).all()
        
        if len(recent_tasks) > 30:  # Too many tasks in 24h
            score += 0.3
        
        # Check for rapid task completion (less than 2 minutes per task on average)
        if len(recent_tasks) > 5:
            total_time = 0
            for task in recent_tasks:
                if task.assigned_at and task.completed_at:
                    task_duration = (task.completed_at - task.assigned_at).total_seconds()
                    total_time += task_duration
            
            avg_time_per_task = total_time / len(recent_tasks)
            if avg_time_per_task < 120:  # Less than 2 minutes average
                score += 0.3
        
        # Factor 3: Device/IP patterns
        recent_devices = db.query(DeviceIPLog).filter(
            DeviceIPLog.user_id == user.id,
            DeviceIPLog.created_at >= now - timedelta(days=7)
        ).all()
        
        unique_ips = set()
        unique_devices = set()
        
        for log in recent_devices:
            if log.ip_address:
                unique_ips.add(log.ip_address)
            if log.device_info:
                unique_devices.add(log.device_info)
        
        # Multiple IPs/devices in short time = suspicious
        if len(unique_ips) > 5:
            score += 0.2
        if len(unique_devices) > 3:
            score += 0.2
        
        # Factor 4: Earnings vs tasks ratio
        total_earnings = db.query(func.sum(CoinTransaction.amount)).filter(
            CoinTransaction.user_id == user.id,
            CoinTransaction.type == CoinTransactionType.earn
        ).scalar() or 0
        
        total_completed_tasks = db.query(Task).filter(
            Task.assigned_user_id == user.id,
            Task.status == TaskStatus.completed
        ).count()
        
        if total_completed_tasks > 0:
            earnings_per_task = total_earnings / total_completed_tasks
            if earnings_per_task > 20:  # Unusually high earnings per task
                score += 0.2
        
        return min(1.0, score)  # Cap at 1.0
    
    async def _notify_admins_suspicious_activity(self, user: User, fraud_score: float, 
                                               amount: int, db: Session):
        """Notify admins about suspicious withdrawal activity"""
        admin_users = db.query(User).filter(User.is_admin == True).all()
        
        for admin in admin_users:
            await self.notification_service.create_notification(
                user_id=admin.id,
                title="Şüpheli Çekim Talebi 🚨",
                message=f"Kullanıcı {user.username} için yüksek risk skoru: {fraud_score:.2f} (Miktar: {amount} coin)",
                notification_type=NotificationType.SECURITY_ALERT,
                priority=NotificationPriority.URGENT,
                data={
                    "suspicious_user_id": user.id,
                    "fraud_score": fraud_score,
                    "withdrawal_amount": amount
                }
            )
    
    async def get_withdrawal_status(self, user_id: int) -> Dict[str, Any]:
        """Get user's withdrawal status and history"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Current pending/locked withdrawals
            current_withdrawal = db.query(CoinWithdrawalRequest).filter(
                CoinWithdrawalRequest.user_id == user_id,
                CoinWithdrawalRequest.status.in_(["pending", "locked"])
            ).first()
            
            # Withdrawal history (last 10)
            withdrawal_history = db.query(CoinWithdrawalRequest).filter(
                CoinWithdrawalRequest.user_id == user_id
            ).order_by(CoinWithdrawalRequest.requested_at.desc()).limit(10).all()
            
            # Calculate available balance (total - locked)
            locked_amount = 0
            if current_withdrawal and current_withdrawal.status == "pending":
                locked_amount = current_withdrawal.amount
            
            available_balance = user.coin_balance
            
            # Security status
            security_check = await self._perform_security_checks(user, 1, db)  # Dummy amount for check
            fraud_score = await self._calculate_fraud_score(user, db)
            
            return {
                "success": True,
                "user_id": user_id,
                "total_balance": user.coin_balance + locked_amount,
                "available_balance": available_balance,
                "locked_amount": locked_amount,
                "current_withdrawal": {
                    "id": current_withdrawal.id if current_withdrawal else None,
                    "amount": current_withdrawal.amount if current_withdrawal else None,
                    "status": current_withdrawal.status if current_withdrawal else None,
                    "requested_at": current_withdrawal.requested_at.isoformat() if current_withdrawal and current_withdrawal.requested_at else None,
                    "locked_until": current_withdrawal.locked_until.isoformat() if current_withdrawal and current_withdrawal.locked_until else None
                },
                "withdrawal_history": [
                    {
                        "id": w.id,
                        "amount": w.amount,
                        "status": w.status,
                        "requested_at": w.requested_at.isoformat() if w.requested_at else None,
                        "processed_at": w.processed_at.isoformat() if w.processed_at else None
                    } for w in withdrawal_history
                ],
                "security_status": {
                    "can_withdraw": security_check["passed"],
                    "fraud_score": fraud_score,
                    "risk_level": "high" if fraud_score > 0.7 else "medium" if fraud_score > 0.4 else "low"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting withdrawal status for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Durum bilgisi alınırken hata oluştu"}
        finally:
            db.close()
    
    async def cancel_withdrawal(self, user_id: int, withdrawal_id: int) -> Dict[str, Any]:
        """Cancel a pending withdrawal and unlock coins"""
        db = self.db_session_factory()
        try:
            withdrawal = db.query(CoinWithdrawalRequest).filter(
                CoinWithdrawalRequest.id == withdrawal_id,
                CoinWithdrawalRequest.user_id == user_id,
                CoinWithdrawalRequest.status == "pending"
            ).first()
            
            if not withdrawal:
                return {"success": False, "message": "İptal edilebilir çekim talebi bulunamadı"}
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Unlock coins
            user.coin_balance += withdrawal.amount
            
            # Create unlock transaction
            unlock_transaction = CoinTransaction(
                user_id=user_id,
                amount=withdrawal.amount,
                type=CoinTransactionType.earn,
                note=f"Çekim talebi iptali (Talep #{withdrawal.id})"
            )
            db.add(unlock_transaction)
            
            # Cancel withdrawal
            withdrawal.status = "cancelled"
            withdrawal.processed_at = datetime.utcnow()
            
            # Notify user
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Çekim Talebi İptal Edildi ↩️",
                message=f"{withdrawal.amount} coin çekim talebiniz iptal edildi ve bakiyenize iade edildi.",
                notification_type=NotificationType.WITHDRAWAL_CANCELLED,
                priority=NotificationPriority.MEDIUM,
                data={"amount": withdrawal.amount}
            )
            
            db.commit()
            
            logger.info(f"Withdrawal {withdrawal_id} cancelled for user {user.username}")
            
            return {
                "success": True,
                "message": "Çekim talebi iptal edildi ve bakiyenize iade edildi",
                "refunded_amount": withdrawal.amount,
                "new_balance": user.coin_balance
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error cancelling withdrawal {withdrawal_id} for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Çekim iptali sırasında hata oluştu"}
        finally:
            db.close()

    async def _send_instagram_verification(self, user_id: int, verification_code: str, instagram_profile):
        """Send verification code through Instagram"""
        try:
            # For now, we'll create a notification for the user to post the code
            # In a real implementation, this could integrate with Instagram's API
            await self.notification_service.create_notification(
                user_id=user_id,
                title="Instagram Doğrulama Gerekli 📱",
                message=f"Coin çekimi için Instagram hesabınızda '{verification_code}' kodunu story olarak paylaşın veya bio'nuza ekleyin. Kod 15 dakika geçerlidir.",
                notification_type=NotificationType.SECURITY_ALERT,
                priority=NotificationPriority.HIGH,
                data={
                    "verification_code": verification_code,
                    "instagram_username": instagram_profile.username,
                    "verification_method": "instagram_post"
                }
            )
        except Exception as e:
            logger.error(f"Error sending Instagram verification: {e}")

    def _generate_verification_code(self) -> str:
        """Generate a secure verification code"""
        return f"IGV{random.randint(100000, 999999)}"

    async def _calculate_enhanced_fraud_score(self, user, instagram_profile, db: Session) -> float:
        """Enhanced fraud detection using Instagram profile data"""
        base_score = await self._calculate_fraud_score(user, db)
        
        # Instagram-based risk factors
        instagram_risk = 0.0
        
        # Account age factor
        if instagram_profile.created_at:
            account_age_days = (datetime.utcnow() - instagram_profile.created_at).days
            if account_age_days < 30:
                instagram_risk += 0.3  # New Instagram account
            elif account_age_days < 90:
                instagram_risk += 0.1  # Relatively new account
        
        # Follower count factor
        if instagram_profile.followers_count < 50:
            instagram_risk += 0.2  # Very low followers
        elif instagram_profile.followers_count < 200:
            instagram_risk += 0.1  # Low followers
        
        # Profile completeness
        if not instagram_profile.bio or len(instagram_profile.bio.strip()) < 10:
            instagram_risk += 0.1  # Incomplete profile
        
        if not instagram_profile.profile_picture_url:
            instagram_risk += 0.1  # No profile picture
        
        # Posting activity
        if instagram_profile.media_count < 5:
            instagram_risk += 0.2  # Very few posts
        elif instagram_profile.media_count < 20:
            instagram_risk += 0.1  # Few posts
        
        # Private account factor (lower risk for private accounts)
        if instagram_profile.is_private:
            instagram_risk -= 0.1  # Slight reduction for private accounts
        
        return min(1.0, base_score + instagram_risk)

    async def verify_withdrawal_eligibility(self, user_id: int) -> Dict[str, Any]:
        """Comprehensive withdrawal eligibility check"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"eligible": False, "reason": "Kullanıcı bulunamadı"}
            
            checks = {
                "minimum_balance": False,
                "account_age": False,
                "instagram_verified": False,
                "no_pending_withdrawals": False,
                "not_suspicious": False,
                "completed_tasks": False
            }
            
            reasons = []
            
            # Minimum balance check
            if user.coins >= 100:  # Minimum withdrawal amount
                checks["minimum_balance"] = True
            else:
                reasons.append("En az 100 coin gereklidir")
            
            # Account age check (7 days minimum)
            account_age = (datetime.utcnow() - user.created_at).days
            if account_age >= 7:
                checks["account_age"] = True
            else:
                reasons.append(f"Hesabınız en az 7 günlük olmalıdır ({account_age} gün)")
            
            # Instagram verification check
            instagram_profile = db.query(InstagramProfile).filter(
                InstagramProfile.user_id == user_id,
                InstagramProfile.is_verified == True
            ).first()
            
            if instagram_profile:
                checks["instagram_verified"] = True
            else:
                reasons.append("Instagram hesabı doğrulanmalıdır")
            
            # No pending withdrawals
            pending_withdrawal = db.query(CoinWithdrawalRequest).filter(
                CoinWithdrawalRequest.user_id == user_id,
                CoinWithdrawalRequest.status.in_(["pending", "locked"])
            ).first()
            
            if not pending_withdrawal:
                checks["no_pending_withdrawals"] = True
            else:
                reasons.append("Bekleyen bir çekim talebiniz var")
            
            # User not flagged as suspicious
            if not user.is_suspicious:
                checks["not_suspicious"] = True
            else:
                reasons.append("Hesabınız güvenlik incelemesi altında")
            
            # Minimum task completion requirement
            completed_tasks = db.query(Task).filter(
                Task.assigned_user_id == user_id,
                Task.status == TaskStatus.completed
            ).count()
            
            if completed_tasks >= 5:  # Minimum 5 completed tasks
                checks["completed_tasks"] = True
            else:
                reasons.append(f"En az 5 görev tamamlanmalıdır ({completed_tasks}/5)")
            
            all_checks_passed = all(checks.values())
            
            return {
                "eligible": all_checks_passed,
                "checks": checks,
                "reasons": reasons,
                "minimum_withdrawal": 100,
                "current_balance": user.coins,
                "instagram_verified": instagram_profile is not None
            }
            
        except Exception as e:
            logger.error(f"Error checking withdrawal eligibility: {e}")
            return {"eligible": False, "reason": "Sistem hatası"}
        finally:
            db.close()

    async def calculate_user_security_score(self, user_id: int) -> Dict[str, Any]:
        """Calculate user's security score (public method)"""
        db = self.db_session_factory()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "Kullanıcı bulunamadı"}
            
            # Calculate fraud score
            fraud_score = await self._calculate_fraud_score(user, db)
            security_score = 1.0 - fraud_score  # Convert fraud risk to security score
            
            # Risk level classification
            if security_score >= 0.8:
                risk_level = "low"
            elif security_score >= 0.6:
                risk_level = "medium"
            else:
                risk_level = "high"
            
            return {
                "success": True,
                "security_score": round(security_score, 2),
                "fraud_risk": round(fraud_score, 2),
                "risk_level": risk_level,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error calculating security score for user {user_id}: {e}", exc_info=True)
            return {"success": False, "message": "Güvenlik skoru hesaplanamadı"}
        finally:
            db.close()

# Global coin security manager
coin_security_manager = None

def get_coin_security_manager(db_session_factory):
    global coin_security_manager
    if coin_security_manager is None:
        coin_security_manager = CoinSecurityManager(db_session_factory)
    return coin_security_manager
