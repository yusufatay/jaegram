"""
User Education and Interactive Guide System
Real educational content, tutorials, and interactive onboarding for users
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
import logging
from enum import Enum

from models import User, UserEducation, Badge, UserBadge, CoinTransaction, CoinTransactionType

logger = logging.getLogger(__name__)

class EducationModuleType(str, Enum):
    ONBOARDING = "onboarding"
    INSTAGRAM_BASICS = "instagram_basics"
    COIN_SYSTEM = "coin_system"
    SOCIAL_FEATURES = "social_features"
    SECURITY_PRIVACY = "security_privacy"
    PLATFORM_GUIDELINES = "platform_guidelines"
    ADVANCED_FEATURES = "advanced_features"

class EducationStepType(str, Enum):
    TUTORIAL = "tutorial"
    INTERACTIVE = "interactive"
    QUIZ = "quiz"
    VIDEO = "video"
    PRACTICE = "practice"

class UserEducationService:
    def __init__(self, db: Session):
        self.db = db
        
        # Define education modules with structured content
        self.education_modules = {
            EducationModuleType.ONBOARDING: {
                "title": "Platform'a Hoş Geldiniz! 🎉",
                "description": "Instagram Coin Platform'unu nasıl kullanacağınızı öğrenin",
                "duration_minutes": 10,
                "coin_reward": 100,
                "badge_id": "onboarding_complete",
                "steps": [
                    {
                        "id": "welcome",
                        "type": EducationStepType.TUTORIAL,
                        "title": "Hoş Geldiniz!",
                        "content": "Bu platform ile Instagram'da gerçek etkileşimler alabilir ve coin kazanabilirsiniz.",
                        "duration_seconds": 30
                    },
                    {
                        "id": "account_setup", 
                        "type": EducationStepType.INTERACTIVE,
                        "title": "Hesap Kurulumu",
                        "content": "Instagram hesabınızı bağlayın ve profilinizi tamamlayın",
                        "action_required": "connect_instagram",
                        "duration_seconds": 120
                    },
                    {
                        "id": "first_task",
                        "type": EducationStepType.PRACTICE,
                        "title": "İlk Göreviniz",
                        "content": "Bir görev alın ve tamamlayın",
                        "action_required": "complete_task",
                        "duration_seconds": 180
                    }
                ]
            },
            EducationModuleType.INSTAGRAM_BASICS: {
                "title": "Instagram Temelleri 📱",
                "description": "Instagram'da etkili etkileşim yöntemlerini öğrenin",
                "duration_minutes": 15,
                "coin_reward": 75,
                "badge_id": "instagram_expert",
                "steps": [
                    {
                        "id": "like_best_practices",
                        "type": EducationStepType.TUTORIAL,
                        "title": "Beğeni En İyi Uygulamaları",
                        "content": "Doğal ve anlamlı beğeniler nasıl yapılır",
                        "duration_seconds": 180
                    },
                    {
                        "id": "follow_etiquette",
                        "type": EducationStepType.TUTORIAL,
                        "title": "Takip Etme Görgü Kuralları",
                        "content": "Kaliteli hesapları takip etme stratejileri",
                        "duration_seconds": 120
                    },
                    {
                        "id": "comment_guidelines",
                        "type": EducationStepType.QUIZ,
                        "title": "Yorum Yazma Rehberi",
                        "content": "Anlamlı ve değerli yorumlar yazma",
                        "questions": [
                            {
                                "question": "Hangi tür yorumlar daha değerlidir?",
                                "options": ["Emoji", "Kısa kelimeler", "Anlamlı cümleler", "Kopya yorumlar"],
                                "correct": 2
                            }
                        ],
                        "duration_seconds": 240
                    }
                ]
            },
            EducationModuleType.COIN_SYSTEM: {
                "title": "Coin Sistemi 💰",
                "description": "Coin kazanma, harcama ve güvenlik özelliklerini öğrenin",
                "duration_minutes": 12,
                "coin_reward": 50,
                "badge_id": "coin_master",
                "steps": [
                    {
                        "id": "earning_coins",
                        "type": EducationStepType.TUTORIAL,
                        "title": "Coin Kazanma",
                        "content": "Görevleri tamamlayarak ve referanslarla coin kazanın",
                        "duration_seconds": 150
                    },
                    {
                        "id": "spending_coins",
                        "type": EducationStepType.TUTORIAL,
                        "title": "Coin Harcama",
                        "content": "Siparişler oluşturarak coinlerinizi kullanın",
                        "duration_seconds": 120
                    },
                    {
                        "id": "withdrawal_security",
                        "type": EducationStepType.INTERACTIVE,
                        "title": "Güvenli Para Çekme",
                        "content": "Güvenlik önlemlerini öğrenin ve ilk çekim talebinizi oluşturun",
                        "action_required": "learn_withdrawal",
                        "duration_seconds": 180
                    }
                ]
            },
            EducationModuleType.SECURITY_PRIVACY: {
                "title": "Güvenlik ve Gizlilik 🔒",
                "description": "Hesap güvenliği ve gizlilik ayarlarınızı öğrenin",
                "duration_minutes": 20,
                "coin_reward": 125,
                "badge_id": "security_champion",
                "steps": [
                    {
                        "id": "account_security",
                        "type": EducationStepType.TUTORIAL,
                        "title": "Hesap Güvenliği",
                        "content": "Güçlü şifreler ve iki faktörlü kimlik doğrulama",
                        "duration_seconds": 300
                    },
                    {
                        "id": "privacy_settings",
                        "type": EducationStepType.INTERACTIVE,
                        "title": "Gizlilik Ayarları",
                        "content": "Kişisel verilerinizi koruyun",
                        "action_required": "review_privacy",
                        "duration_seconds": 240
                    },
                    {
                        "id": "fraud_prevention",
                        "type": EducationStepType.QUIZ,
                        "title": "Dolandırıcılık Önleme",
                        "content": "Şüpheli aktiviteleri tanıma ve raporlama",
                        "questions": [
                            {
                                "question": "Şüpheli bir aktivite fark ettiğinizde ne yapmalısınız?",
                                "options": ["Görmezden gel", "Hemen rapor et", "Arkadaşlarınla paylaş", "Panik yap"],
                                "correct": 1
                            }
                        ],
                        "duration_seconds": 180
                    }
                ]
            }
        }

    def get_user_education_progress(self, user_id: int) -> Dict[str, Any]:
        """Get user's education progress across all modules"""
        try:
            education_records = self.db.query(UserEducation).filter(
                UserEducation.user_id == user_id
            ).all()
            
            progress = {}
            for module_type in EducationModuleType:
                module_record = next(
                    (r for r in education_records if r.module_type == module_type.value), 
                    None
                )
                
                if module_record:
                    progress[module_type.value] = {
                        "completed": module_record.completed,
                        "progress_data": module_record.progress_data or {},
                        "completed_at": module_record.completed_at.isoformat() if module_record.completed_at else None,
                        "current_step": module_record.current_step,
                        "score": module_record.score
                    }
                else:
                    progress[module_type.value] = {
                        "completed": False,
                        "progress_data": {},
                        "completed_at": None,
                        "current_step": None,
                        "score": 0
                    }
                
                # Add module metadata
                if module_type.value in self.education_modules:
                    module_info = self.education_modules[module_type]
                    progress[module_type.value].update({
                        "title": module_info["title"],
                        "description": module_info["description"],
                        "duration_minutes": module_info["duration_minutes"],
                        "coin_reward": module_info["coin_reward"],
                        "total_steps": len(module_info["steps"])
                    })

            return {
                "user_id": user_id,
                "modules": progress,
                "overall_completion": len([m for m in progress.values() if m["completed"]]) / len(EducationModuleType) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting education progress for user {user_id}: {e}")
            raise

    def start_education_module(self, user_id: int, module_type: EducationModuleType) -> Dict[str, Any]:
        """Start or resume an education module"""
        try:
            if module_type not in self.education_modules:
                raise ValueError(f"Invalid module type: {module_type}")
            
            module_info = self.education_modules[module_type]
            
            # Check if user already has this module
            education_record = self.db.query(UserEducation).filter(
                and_(
                    UserEducation.user_id == user_id,
                    UserEducation.module_type == module_type.value
                )
            ).first()
            
            if not education_record:
                education_record = UserEducation(
                    user_id=user_id,
                    module_type=module_type.value,
                    started_at=datetime.utcnow(),
                    current_step=module_info["steps"][0]["id"],
                    progress_data={"step_index": 0, "steps_completed": []},
                    score=0
                )
                self.db.add(education_record)
                self.db.flush()
            
            return {
                "education_id": education_record.id,
                "module": {
                    "type": module_type.value,
                    "title": module_info["title"],
                    "description": module_info["description"],
                    "duration_minutes": module_info["duration_minutes"],
                    "coin_reward": module_info["coin_reward"],
                    "steps": module_info["steps"]
                },
                "progress": {
                    "current_step": education_record.current_step,
                    "progress_data": education_record.progress_data or {},
                    "score": education_record.score,
                    "started_at": education_record.started_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error starting education module {module_type} for user {user_id}: {e}")
            raise

    def complete_education_step(
        self, 
        user_id: int, 
        module_type: EducationModuleType, 
        step_id: str,
        interaction_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Complete a step in an education module"""
        try:
            education_record = self.db.query(UserEducation).filter(
                and_(
                    UserEducation.user_id == user_id,
                    UserEducation.module_type == module_type.value
                )
            ).first()
            
            if not education_record:
                raise ValueError("Education module not started")
            
            if education_record.completed:
                raise ValueError("Module already completed")
            
            module_info = self.education_modules[module_type]
            steps = module_info["steps"]
            
            # Find current step
            step_index = next(
                (i for i, step in enumerate(steps) if step["id"] == step_id),
                None
            )
            
            if step_index is None:
                raise ValueError(f"Invalid step_id: {step_id}")
            
            current_step = steps[step_index]
            progress_data = education_record.progress_data or {"step_index": 0, "steps_completed": []}
            
            # Update progress
            if step_id not in progress_data["steps_completed"]:
                progress_data["steps_completed"].append(step_id)
            
            # Calculate score based on step type and interaction
            step_score = self._calculate_step_score(current_step, interaction_data)
            education_record.score += step_score
            
            # Move to next step or complete module
            if step_index < len(steps) - 1:
                next_step = steps[step_index + 1]
                education_record.current_step = next_step["id"]
                progress_data["step_index"] = step_index + 1
            else:
                # Module completed
                education_record.completed = True
                education_record.completed_at = datetime.utcnow()
                education_record.current_step = None
                
                # Award completion rewards
                self._award_completion_rewards(user_id, module_type, education_record.score)
            
            education_record.progress_data = progress_data
            self.db.commit()
            
            return {
                "step_completed": step_id,
                "score_earned": step_score,
                "total_score": education_record.score,
                "module_completed": education_record.completed,
                "next_step": education_record.current_step,
                "progress_percentage": len(progress_data["steps_completed"]) / len(steps) * 100
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error completing education step {step_id} for user {user_id}: {e}")
            raise

    def _calculate_step_score(self, step: Dict, interaction_data: Optional[Dict]) -> int:
        """Calculate score for completing a step"""
        base_score = {
            EducationStepType.TUTORIAL: 10,
            EducationStepType.INTERACTIVE: 15,
            EducationStepType.QUIZ: 20,
            EducationStepType.VIDEO: 10,
            EducationStepType.PRACTICE: 25
        }.get(step["type"], 10)
        
        # Bonus for quiz performance
        if step["type"] == EducationStepType.QUIZ and interaction_data:
            correct_answers = interaction_data.get("correct_answers", 0)
            total_questions = len(step.get("questions", []))
            if total_questions > 0:
                quiz_bonus = int((correct_answers / total_questions) * 10)
                base_score += quiz_bonus
        
        return base_score

    def _award_completion_rewards(self, user_id: int, module_type: EducationModuleType, final_score: int):
        """Award coins and badges for module completion"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return
            
            module_info = self.education_modules[module_type]
            coin_reward = module_info["coin_reward"]
            
            # Award coins
            user.coin_balance += coin_reward
            
            # Create coin transaction record
            coin_tx = CoinTransaction(
                user_id=user_id,
                amount=coin_reward,
                type=CoinTransactionType.earn,
                note=f"Eğitim modülü tamamlama: {module_info['title']} (Skor: {final_score})"
            )
            self.db.add(coin_tx)
            
            # Award badge if specified
            badge_id = module_info.get("badge_id")
            if badge_id:
                self._award_education_badge(user_id, badge_id, module_type.value)
            
            logger.info(f"Awarded {coin_reward} coins to user {user_id} for completing {module_type.value}")
            
        except Exception as e:
            logger.error(f"Error awarding completion rewards to user {user_id}: {e}")

    def _award_education_badge(self, user_id: int, badge_id: str, module_type: str):
        """Award a badge for education completion"""
        try:
            # Check if badge already exists
            existing_badge = self.db.query(UserBadge).join(Badge).filter(
                and_(
                    UserBadge.user_id == user_id,
                    Badge.badge_type == badge_id
                )
            ).first()
            
            if existing_badge:
                return
            
            # Find or create badge
            badge = self.db.query(Badge).filter(Badge.badge_type == badge_id).first()
            if not badge:
                badge_info = {
                    "onboarding_complete": {
                        "name": "Platform Yeni Üyesi",
                        "description": "Platform onboarding'ini başarıyla tamamladı",
                        "icon_url": "🎓"
                    },
                    "instagram_expert": {
                        "name": "Instagram Uzmanı",
                        "description": "Instagram temelleri eğitimini tamamladı",
                        "icon_url": "📱"
                    },
                    "coin_master": {
                        "name": "Coin Ustası",
                        "description": "Coin sistemi eğitimini tamamladı",
                        "icon_url": "💰"
                    },
                    "security_champion": {
                        "name": "Güvenlik Şampiyonu",
                        "description": "Güvenlik ve gizlilik eğitimini tamamladı",
                        "icon_url": "🔒"
                    }
                }.get(badge_id, {
                    "name": "Eğitim Rozetı",
                    "description": f"{module_type} eğitimini tamamladı",
                    "icon_url": "🏆"
                })
                
                badge = Badge(
                    badge_type=badge_id,
                    name=badge_info["name"],
                    description=badge_info["description"],
                    icon_url=badge_info["icon_url"],
                    rarity="common",
                    points_required=0
                )
                self.db.add(badge)
                self.db.flush()
            
            # Award badge to user
            user_badge = UserBadge(
                user_id=user_id,
                badge_id=badge.id,
                earned_at=datetime.utcnow()
            )
            self.db.add(user_badge)
            
            logger.info(f"Awarded badge {badge_id} to user {user_id} for education completion")
            
        except Exception as e:
            logger.error(f"Error awarding education badge {badge_id} to user {user_id}: {e}")

    def get_recommended_modules(self, user_id: int) -> List[Dict[str, Any]]:
        """Get recommended education modules for a user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return []
            
            progress = self.get_user_education_progress(user_id)
            recommendations = []
            
            # Always recommend onboarding first
            if not progress["modules"][EducationModuleType.ONBOARDING.value]["completed"]:
                recommendations.append({
                    "module_type": EducationModuleType.ONBOARDING.value,
                    "priority": "high",
                    "reason": "Platform'a başlamak için temel bilgiler"
                })
            
            # Recommend based on user activity
            if user.instagram_session_data and not progress["modules"][EducationModuleType.INSTAGRAM_BASICS.value]["completed"]:
                recommendations.append({
                    "module_type": EducationModuleType.INSTAGRAM_BASICS.value,
                    "priority": "medium",
                    "reason": "Instagram hesabınız bağlı, etkileşim kalitesini artırın"
                })
            
            if user.coin_balance > 0 and not progress["modules"][EducationModuleType.COIN_SYSTEM.value]["completed"]:
                recommendations.append({
                    "module_type": EducationModuleType.COIN_SYSTEM.value,
                    "priority": "medium",
                    "reason": "Coinlerinizi daha etkili kullanmayı öğrenin"
                })
            
            return recommendations[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommended modules for user {user_id}: {e}")
            return []

    def get_education_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get education statistics for a user"""
        try:
            education_records = self.db.query(UserEducation).filter(
                UserEducation.user_id == user_id
            ).all()
            
            completed_modules = [r for r in education_records if r.completed]
            total_score = sum(r.score for r in education_records)
            total_time_spent = sum(
                (r.completed_at - r.started_at).total_seconds() / 3600 
                for r in completed_modules if r.completed_at and r.started_at
            )
            
            return {
                "modules_completed": len(completed_modules),
                "total_modules": len(EducationModuleType),
                "completion_percentage": len(completed_modules) / len(EducationModuleType) * 100,
                "total_score": total_score,
                "total_hours_spent": round(total_time_spent, 1),
                "average_score": total_score / len(education_records) if education_records else 0,
                "badges_earned": self.db.query(UserBadge).filter(UserBadge.user_id == user_id).count()
            }
            
        except Exception as e:
            logger.error(f"Error getting education statistics for user {user_id}: {e}")
            return {}
