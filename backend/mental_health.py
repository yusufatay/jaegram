"""
Mental Health and Wellness Monitoring System
Real mental health notifications, usage pattern analysis, and wellness features
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import json
import logging
from enum import Enum

from models import User, MentalHealthLog, Task, Order, CoinTransaction, UserStatistics, Notification

logger = logging.getLogger(__name__)

class MentalHealthRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UsagePattern(str, Enum):
    HEALTHY = "healthy"
    EXCESSIVE = "excessive"
    OBSESSIVE = "obsessive"
    CONCERNING = "concerning"

class WellnessMetric(str, Enum):
    USAGE_TIME = "usage_time"
    TASK_FREQUENCY = "task_frequency" 
    COIN_OBSESSION = "coin_obsession"
    SOCIAL_VALIDATION = "social_validation"
    SLEEP_DISRUPTION = "sleep_disruption"
    MOOD_TRACKING = "mood_tracking"

class MentalHealthService:
    def __init__(self, db: Session):
        self.db = db
        
        # Wellness thresholds and guidelines
        self.thresholds = {
            "daily_hours_limit": 4.0,  # Maximum healthy daily usage hours
            "daily_tasks_limit": 50,   # Maximum healthy daily tasks
            "hourly_tasks_limit": 10,  # Maximum tasks per hour
            "consecutive_hours_limit": 2.0,  # Maximum consecutive usage hours
            "late_night_cutoff": 23,   # Hour after which usage is concerning
            "early_morning_cutoff": 6,  # Hour before which usage is concerning
            "coin_obsession_threshold": 1000,  # Coins spent/earned per day threshold
            "task_completion_rate_low": 0.3,  # Below this rate indicates frustration
            "break_reminder_interval": 60,  # Minutes between break reminders
        }
        
        # Wellness tips and resources
        self.wellness_tips = {
            "break_reminder": [
                "🌟 Kısa bir mola verin! Gözlerinizi dinlendirin ve derin nefes alın.",
                "💚 5 dakikalık yürüyüş yapmak hem zihninize hem bedeninize iyi gelir.",
                "🧘 Mindfulness: Bu anın farkında olun ve kendinizi nasıl hissettiğinizi kontrol edin.",
                "💧 Su içmeyi unutmayın! Hidrate kalmak odaklanmanıza yardımcı olur.",
                "🌸 Pencereden dışarıya bakın ve doğayla bağlantı kurun."
            ],
            "excessive_usage": [
                "⚡ Çok aktif görünüyorsunuz! Dinlenme zamanı gelmiş olabilir.",
                "🎯 Hedeflerinizi gözden geçirin ve sürdürülebilir bir tempo belirleyin.",
                "⏰ Düzenli molalar almanız uzun vadede daha verimli olmanızı sağlar.",
                "🤝 Arkadaşlarınızla sosyal aktiviteler planlayın.",
                "📚 Yeni bir hobi veya beceri öğrenmeyi düşünün."
            ],
            "mood_support": [
                "💝 Kendinize karşı nazik olun. Mükemmel olmak zorunda değilsiniz.",
                "🌈 Her küçük ilerleme kutlanmaya değer!",
                "🤲 Yardıma ihtiyacınız varsa çekinmeden destek alın.",
                "🌱 Zorluklar büyüme fırsatlarıdır.",
                "⭐ Bugün kendiniz için gurur duyabileceğiniz bir şey yapın."
            ]
        }

    def analyze_user_wellness(self, user_id: int) -> Dict[str, Any]:
        """Comprehensive wellness analysis for a user"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Get recent activity data
            recent_logs = self._get_recent_mental_health_logs(user_id, days=7)
            usage_patterns = self._analyze_usage_patterns(user_id)
            risk_assessment = self._assess_mental_health_risk(user_id, usage_patterns)
            recommendations = self._generate_wellness_recommendations(user_id, risk_assessment, usage_patterns)
            
            return {
                "user_id": user_id,
                "assessment_date": datetime.utcnow().isoformat(),
                "risk_level": risk_assessment["level"],
                "risk_score": risk_assessment["score"],
                "usage_patterns": usage_patterns,
                "recent_logs": recent_logs,
                "recommendations": recommendations,
                "wellness_metrics": self._calculate_wellness_metrics(user_id),
                "support_resources": self._get_support_resources(risk_assessment["level"])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing wellness for user {user_id}: {e}")
            raise

    def log_mental_health_event(
        self, 
        user_id: int, 
        event_type: str, 
        severity: str,
        description: str,
        metadata: Optional[Dict] = None
    ) -> int:
        """Log a mental health related event"""
        try:
            log_entry = MentalHealthLog(
                user_id=user_id,
                event_type=event_type,
                severity=severity,
                description=description,
                metadata=metadata or {},
                logged_at=datetime.utcnow()
            )
            
            self.db.add(log_entry)
            self.db.flush()
            
            # Trigger immediate intervention if critical
            if severity == "critical":
                self._trigger_crisis_intervention(user_id, log_entry.id)
            elif severity == "high":
                self._schedule_wellness_check(user_id)
            
            return log_entry.id
            
        except Exception as e:
            logger.error(f"Error logging mental health event for user {user_id}: {e}")
            raise

    def _get_recent_mental_health_logs(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get recent mental health logs for analysis"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            logs = self.db.query(MentalHealthLog).filter(
                and_(
                    MentalHealthLog.user_id == user_id,
                    MentalHealthLog.logged_at >= cutoff_date
                )
            ).order_by(desc(MentalHealthLog.logged_at)).all()
            
            return [
                {
                    "id": log.id,
                    "event_type": log.event_type,
                    "severity": log.severity,
                    "description": log.description,
                    "metadata": log.metadata or {},
                    "logged_at": log.logged_at.isoformat()
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Error getting recent mental health logs for user {user_id}: {e}")
            return []

    def _analyze_usage_patterns(self, user_id: int) -> Dict[str, Any]:
        """Analyze user's usage patterns for mental health insights"""
        try:
            now = datetime.utcnow()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_ago = today - timedelta(days=7)
            
            # Get recent tasks and orders
            recent_tasks = self.db.query(Task).filter(
                and_(
                    Task.user_id == user_id,
                    Task.created_at >= week_ago
                )
            ).all()
            
            recent_orders = self.db.query(Order).filter(
                and_(
                    Order.user_id == user_id,
                    Order.created_at >= week_ago
                )
            ).all()
            
            # Analyze patterns
            daily_activity = self._analyze_daily_activity(recent_tasks, recent_orders)
            hourly_distribution = self._analyze_hourly_distribution(recent_tasks, recent_orders)
            task_completion_patterns = self._analyze_task_completion_patterns(recent_tasks)
            
            # Determine overall usage pattern
            usage_pattern = self._classify_usage_pattern(daily_activity, hourly_distribution, task_completion_patterns)
            
            return {
                "pattern_type": usage_pattern,
                "daily_activity": daily_activity,
                "hourly_distribution": hourly_distribution,
                "task_completion": task_completion_patterns,
                "analysis_period": {
                    "start": week_ago.isoformat(),
                    "end": now.isoformat(),
                    "days": 7
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing usage patterns for user {user_id}: {e}")
            return {"pattern_type": "unknown"}

    def _analyze_daily_activity(self, tasks: List, orders: List) -> Dict[str, Any]:
        """Analyze daily activity levels"""
        daily_stats = {}
        
        for task in tasks:
            date_key = task.created_at.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {"tasks": 0, "orders": 0, "hours_active": set()}
            daily_stats[date_key]["tasks"] += 1
            daily_stats[date_key]["hours_active"].add(task.created_at.hour)
        
        for order in orders:
            date_key = order.created_at.date().isoformat()
            if date_key not in daily_stats:
                daily_stats[date_key] = {"tasks": 0, "orders": 0, "hours_active": set()}
            daily_stats[date_key]["orders"] += 1
            daily_stats[date_key]["hours_active"].add(order.created_at.hour)
        
        # Convert hours_active sets to counts
        for date_key in daily_stats:
            daily_stats[date_key]["hours_active"] = len(daily_stats[date_key]["hours_active"])
        
        # Calculate averages
        if daily_stats:
            avg_tasks = sum(day["tasks"] for day in daily_stats.values()) / len(daily_stats)
            avg_orders = sum(day["orders"] for day in daily_stats.values()) / len(daily_stats)
            avg_hours = sum(day["hours_active"] for day in daily_stats.values()) / len(daily_stats)
        else:
            avg_tasks = avg_orders = avg_hours = 0
        
        return {
            "daily_breakdown": daily_stats,
            "averages": {
                "tasks_per_day": round(avg_tasks, 1),
                "orders_per_day": round(avg_orders, 1),
                "active_hours_per_day": round(avg_hours, 1)
            }
        }

    def _analyze_hourly_distribution(self, tasks: List, orders: List) -> Dict[str, Any]:
        """Analyze hourly activity distribution"""
        hourly_counts = {hour: 0 for hour in range(24)}
        
        for task in tasks:
            hourly_counts[task.created_at.hour] += 1
        
        for order in orders:
            hourly_counts[order.created_at.hour] += 1
        
        # Identify peak hours and concerning patterns
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if any(hourly_counts.values()) else 12
        late_night_activity = sum(hourly_counts[hour] for hour in range(23, 24)) + sum(hourly_counts[hour] for hour in range(0, 6))
        total_activity = sum(hourly_counts.values())
        
        return {
            "hourly_distribution": hourly_counts,
            "peak_hour": peak_hour,
            "late_night_percentage": (late_night_activity / total_activity * 100) if total_activity > 0 else 0,
            "concerning_hours": late_night_activity > total_activity * 0.2 if total_activity > 0 else False
        }

    def _analyze_task_completion_patterns(self, tasks: List) -> Dict[str, Any]:
        """Analyze task completion patterns for frustration indicators"""
        if not tasks:
            return {"completion_rate": 0, "average_completion_time": 0, "frustration_indicators": []}
        
        completed_tasks = [t for t in tasks if t.status == "completed" and t.completed_at]
        completion_rate = len(completed_tasks) / len(tasks)
        
        # Calculate average completion time
        completion_times = []
        for task in completed_tasks:
            if task.assigned_at:
                completion_time = (task.completed_at - task.assigned_at).total_seconds() / 60  # minutes
                completion_times.append(completion_time)
        
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # Identify frustration indicators
        frustration_indicators = []
        if completion_rate < self.thresholds["task_completion_rate_low"]:
            frustration_indicators.append("low_completion_rate")
        
        if avg_completion_time > 30:  # Taking more than 30 minutes average
            frustration_indicators.append("slow_completion")
        
        failed_tasks = [t for t in tasks if t.status == "failed"]
        if len(failed_tasks) > len(tasks) * 0.3:
            frustration_indicators.append("high_failure_rate")
        
        return {
            "completion_rate": round(completion_rate, 2),
            "average_completion_time": round(avg_completion_time, 1),
            "frustration_indicators": frustration_indicators,
            "total_tasks": len(tasks),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks)
        }

    def _classify_usage_pattern(self, daily_activity: Dict, hourly_distribution: Dict, task_completion: Dict) -> UsagePattern:
        """Classify overall usage pattern"""
        avg_hours = daily_activity["averages"]["active_hours_per_day"]
        avg_tasks = daily_activity["averages"]["tasks_per_day"]
        late_night_percentage = hourly_distribution["late_night_percentage"]
        completion_rate = task_completion["completion_rate"]
        
        # Classify based on multiple factors
        if (avg_hours > self.thresholds["daily_hours_limit"] or 
            avg_tasks > self.thresholds["daily_tasks_limit"] or
            late_night_percentage > 30):
            if completion_rate < 0.3:
                return UsagePattern.OBSESSIVE
            else:
                return UsagePattern.EXCESSIVE
        elif late_night_percentage > 20 or len(task_completion["frustration_indicators"]) > 1:
            return UsagePattern.CONCERNING
        else:
            return UsagePattern.HEALTHY

    def _assess_mental_health_risk(self, user_id: int, usage_patterns: Dict) -> Dict[str, Any]:
        """Assess mental health risk level"""
        risk_score = 0
        risk_factors = []
        
        pattern_type = usage_patterns.get("pattern_type", "unknown")
        
        # Risk scoring based on usage patterns
        if pattern_type == UsagePattern.OBSESSIVE:
            risk_score += 40
            risk_factors.append("obsessive_usage_pattern")
        elif pattern_type == UsagePattern.EXCESSIVE:
            risk_score += 25
            risk_factors.append("excessive_usage")
        elif pattern_type == UsagePattern.CONCERNING:
            risk_score += 15
            risk_factors.append("concerning_usage_pattern")
        
        # Late night usage
        late_night_percentage = usage_patterns.get("hourly_distribution", {}).get("late_night_percentage", 0)
        if late_night_percentage > 30:
            risk_score += 20
            risk_factors.append("excessive_late_night_usage")
        elif late_night_percentage > 15:
            risk_score += 10
            risk_factors.append("some_late_night_usage")
        
        # Task completion frustration
        frustration_indicators = usage_patterns.get("task_completion", {}).get("frustration_indicators", [])
        if len(frustration_indicators) > 2:
            risk_score += 25
            risk_factors.append("high_frustration_indicators")
        elif len(frustration_indicators) > 0:
            risk_score += 10
            risk_factors.append("some_frustration_indicators")
        
        # Recent mental health logs
        recent_logs = self._get_recent_mental_health_logs(user_id, days=3)
        critical_logs = [log for log in recent_logs if log["severity"] in ["high", "critical"]]
        if critical_logs:
            risk_score += 30
            risk_factors.append("recent_critical_mental_health_events")
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = MentalHealthRiskLevel.CRITICAL
        elif risk_score >= 50:
            risk_level = MentalHealthRiskLevel.HIGH
        elif risk_score >= 25:
            risk_level = MentalHealthRiskLevel.MEDIUM
        else:
            risk_level = MentalHealthRiskLevel.LOW
        
        return {
            "level": risk_level,
            "score": risk_score,
            "factors": risk_factors,
            "assessment_date": datetime.utcnow().isoformat()
        }

    def _generate_wellness_recommendations(self, user_id: int, risk_assessment: Dict, usage_patterns: Dict) -> List[Dict[str, Any]]:
        """Generate personalized wellness recommendations"""
        recommendations = []
        risk_level = risk_assessment["level"]
        pattern_type = usage_patterns.get("pattern_type", "unknown")
        
        # Critical risk recommendations
        if risk_level == MentalHealthRiskLevel.CRITICAL:
            recommendations.extend([
                {
                    "type": "immediate_action",
                    "priority": "critical",
                    "title": "Acil Destek",
                    "description": "Profesyonel destek almayı düşünün",
                    "action": "contact_support",
                    "resources": ["crisis_hotline", "mental_health_professionals"]
                },
                {
                    "type": "usage_break",
                    "priority": "high",
                    "title": "Platform Molası",
                    "description": "24 saat platform kullanımından uzak durun",
                    "action": "take_break",
                    "duration_hours": 24
                }
            ])
        
        # High risk recommendations
        elif risk_level == MentalHealthRiskLevel.HIGH:
            recommendations.extend([
                {
                    "type": "usage_limit",
                    "priority": "high",
                    "title": "Kullanım Sınırı",
                    "description": "Günlük kullanımınızı 2 saatla sınırlayın",
                    "action": "set_daily_limit",
                    "limit_hours": 2
                },
                {
                    "type": "wellness_check",
                    "priority": "medium",
                    "title": "Wellness Kontrolü",
                    "description": "Kendinizi nasıl hissettiğinizi değerlendirin",
                    "action": "mood_check"
                }
            ])
        
        # Pattern-specific recommendations
        if pattern_type == UsagePattern.EXCESSIVE:
            recommendations.append({
                "type": "break_reminder",
                "priority": "medium",
                "title": "Düzenli Molalar",
                "description": "Her saatte 10 dakika mola verin",
                "action": "schedule_breaks",
                "interval_minutes": 60
            })
        
        if usage_patterns.get("hourly_distribution", {}).get("late_night_percentage", 0) > 20:
            recommendations.append({
                "type": "sleep_hygiene",
                "priority": "medium",
                "title": "Uyku Hijyeni",
                "description": "Gece 23:00'ten sonra platform kullanımını durdurun",
                "action": "set_night_mode",
                "cutoff_hour": 23
            })
        
        # General wellness recommendations
        recommendations.extend([
            {
                "type": "mindfulness",
                "priority": "low",
                "title": "Mindfulness Egzersizi",
                "description": "Günde 5 dakika nefes egzersizi yapın",
                "action": "practice_mindfulness"
            },
            {
                "type": "physical_activity",
                "priority": "low",
                "title": "Fiziksel Aktivite",
                "description": "Günde en az 30 dakika yürüyüş yapın",
                "action": "increase_physical_activity"
            }
        ])
        
        return recommendations[:5]  # Return top 5 recommendations

    def _calculate_wellness_metrics(self, user_id: int) -> Dict[str, Any]:
        """Calculate various wellness metrics"""
        try:
            now = datetime.utcnow()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Today's activity
            today_tasks = self.db.query(Task).filter(
                and_(
                    Task.user_id == user_id,
                    Task.created_at >= today
                )
            ).count()
            
            today_orders = self.db.query(Order).filter(
                and_(
                    Order.user_id == user_id,
                    Order.created_at >= today
                )
            ).count()
            
            # Recent wellness trends
            week_ago = today - timedelta(days=7)
            weekly_logs = self.db.query(MentalHealthLog).filter(
                and_(
                    MentalHealthLog.user_id == user_id,
                    MentalHealthLog.logged_at >= week_ago
                )
            ).count()
            
            return {
                "today_tasks": today_tasks,
                "today_orders": today_orders,
                "weekly_mental_health_logs": weekly_logs,
                "last_calculated": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating wellness metrics for user {user_id}: {e}")
            return {}

    def _get_support_resources(self, risk_level: MentalHealthRiskLevel) -> List[Dict[str, Any]]:
        """Get appropriate support resources based on risk level"""
        base_resources = [
            {
                "type": "self_help",
                "title": "Kendi Kendine Yardım Rehberi",
                "description": "Zihinsel sağlığınızı iyileştirmek için pratik öneriler",
                "url": "https://example.com/self-help-guide"
            },
            {
                "type": "relaxation",
                "title": "Rahatlama Teknikleri",
                "description": "Stres azaltma ve rahatlama egzersizleri",
                "url": "https://example.com/relaxation-techniques"
            }
        ]
        
        if risk_level in [MentalHealthRiskLevel.HIGH, MentalHealthRiskLevel.CRITICAL]:
            base_resources.extend([
                {
                    "type": "crisis_support",
                    "title": "Kriz Destek Hattı",
                    "description": "7/24 profesyonel destek",
                    "phone": "182",  # Turkey's psychological first aid hotline
                    "urgent": True
                },
                {
                    "type": "professional_help",
                    "title": "Profesyonel Destek",
                    "description": "Uzman psikolog ve psikiyatrist rehberi",
                    "url": "https://example.com/find-therapist"
                }
            ])
        
        return base_resources

    def _trigger_crisis_intervention(self, user_id: int, log_id: int):
        """Trigger immediate crisis intervention procedures"""
        try:
            # Create high-priority notification
            notification = Notification(
                user_id=user_id,
                title="🆘 Acil Destek Gerekli",
                message="Size destek olmak istiyoruz. Lütfen kriz destek hattını arayın: 182",
                type="mental_health_crisis",
                priority="critical",
                data=json.dumps({"log_id": log_id, "crisis_intervention": True})
            )
            self.db.add(notification)
            
            # Log intervention
            intervention_log = MentalHealthLog(
                user_id=user_id,
                event_type="crisis_intervention_triggered",
                severity="info",
                description=f"Crisis intervention triggered for log {log_id}",
                metadata={"original_log_id": log_id, "intervention_time": datetime.utcnow().isoformat()}
            )
            self.db.add(intervention_log)
            
            self.db.commit()
            logger.critical(f"Crisis intervention triggered for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error triggering crisis intervention for user {user_id}: {e}")

    def _schedule_wellness_check(self, user_id: int):
        """Schedule a wellness check for the user"""
        try:
            # Create wellness check notification
            notification = Notification(
                user_id=user_id,
                title="💚 Wellness Kontrolü",
                message="Kendinizi nasıl hissettiğinizi merak ediyoruz. Kısa bir wellness anketi doldurur musunuz?",
                type="wellness_check",
                priority="medium",
                data=json.dumps({"wellness_check": True, "scheduled_at": datetime.utcnow().isoformat()})
            )
            self.db.add(notification)
            self.db.commit()
            
            logger.info(f"Wellness check scheduled for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling wellness check for user {user_id}: {e}")

    def submit_mood_report(self, user_id: int, mood_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a mood report from the user"""
        try:
            # Validate mood data
            required_fields = ["mood_level", "energy_level", "stress_level"]
            for field in required_fields:
                if field not in mood_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create mental health log
            log_id = self.log_mental_health_event(
                user_id=user_id,
                event_type="mood_report",
                severity="info",
                description=f"User mood report: {mood_data['mood_level']}/10",
                metadata={
                    "mood_level": mood_data["mood_level"],
                    "energy_level": mood_data["energy_level"],
                    "stress_level": mood_data["stress_level"],
                    "notes": mood_data.get("notes", ""),
                    "submit_time": datetime.utcnow().isoformat()
                }
            )
            
            # Analyze mood and provide response
            response = self._analyze_mood_report(mood_data)
            
            self.db.commit()
            
            return {
                "log_id": log_id,
                "thank_you_message": "Mood raporunuz için teşekkürler! Bu bilgiler size daha iyi destek olmamıza yardımcı oluyor.",
                "recommendations": response["recommendations"],
                "follow_up_needed": response["follow_up_needed"]
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error submitting mood report for user {user_id}: {e}")
            raise

    def _analyze_mood_report(self, mood_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mood report and generate response"""
        mood_level = mood_data["mood_level"]
        energy_level = mood_data["energy_level"]
        stress_level = mood_data["stress_level"]
        
        recommendations = []
        follow_up_needed = False
        
        # Low mood recommendations
        if mood_level <= 3:
            follow_up_needed = True
            recommendations.extend([
                "💙 Kendinize karşı nazik olun ve sevdiklerinizle vakit geçirin",
                "🌱 Küçük, başarılabilir hedefler belirleyin",
                "☀️ Mümkünse güneş ışığından yararlanın"
            ])
        
        # Low energy recommendations
        if energy_level <= 3:
            recommendations.extend([
                "😴 Yeterli uyku aldığınızdan emin olun (7-9 saat)",
                "🥗 Besleyici yiyecekler tüketin",
                "💧 Bol su için"
            ])
        
        # High stress recommendations
        if stress_level >= 7:
            follow_up_needed = True
            recommendations.extend([
                "🧘 Derin nefes alma egzersizleri yapın",
                "📝 Stres kaynaklarınızı yazarak açıklığa kavuşturun",
                "🎵 Rahatlatıcı müzik dinleyin"
            ])
        
        return {
            "recommendations": recommendations[:3],  # Top 3 recommendations
            "follow_up_needed": follow_up_needed
        }
