from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text, Enum, create_engine, Date
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum
from datetime import datetime
import os

# Database yeri
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./instagram_platform.db")

# engine ve SessionLocal sadece model tanımı için burada, uygulama genelinde dependencies.py kullanılacak

Base = declarative_base()

class OrderStatus(enum.Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    email_verified = Column(Boolean, default=False)
    email_verification_code = Column(String, nullable=True)
    email_verification_expires = Column(DateTime, nullable=True)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    profile_pic_url = Column(String, nullable=True)
    coin_balance = Column(Integer, default=0)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_admin_platform = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_daily_reward = Column(DateTime, nullable=True) # For daily reward feature
    daily_reward_streak = Column(Integer, default=0) # Daily reward streak counter
    
    # Enhanced User Information
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    gender = Column(String, nullable=True)  # 'male', 'female', 'other', 'prefer_not_to_say'
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    language = Column(String, default='tr')  # Default Turkish
    last_login_at = Column(DateTime, nullable=True)
    last_seen_at = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)
    registration_ip = Column(String, nullable=True)
    last_login_ip = Column(String, nullable=True)
    account_status = Column(String, default='active')  # 'active', 'suspended', 'banned', 'pending'
    suspension_reason = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    website_url = Column(String, nullable=True)
    
    # User Preferences
    privacy_public_profile = Column(Boolean, default=True)
    privacy_show_email = Column(Boolean, default=False)
    privacy_show_phone = Column(Boolean, default=False)
    privacy_show_stats = Column(Boolean, default=True)
    theme_preference = Column(String, default='system')  # 'light', 'dark', 'system'
    notification_email = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    notification_sms = Column(Boolean, default=False)
    
    # Instagram specific fields (enhanced) - removed follower/following fields as per requirement
    instagram_pk = Column(String, unique=True, index=True, nullable=True)
    instagram_username = Column(String, index=True, nullable=True)
    instagram_session_data = Column(String, nullable=True) # Stores JSON string of instagrapi session
    instagram_posts_count = Column(Integer, default=0)
    instagram_profile_pic_url = Column(String, nullable=True)
    instagram_bio = Column(Text, nullable=True)
    instagram_is_private = Column(Boolean, default=False)
    instagram_is_verified = Column(Boolean, default=False)
    instagram_external_url = Column(String, nullable=True)
    instagram_category = Column(String, nullable=True)
    instagram_contact_phone = Column(String, nullable=True)
    instagram_contact_email = Column(String, nullable=True)
    instagram_business_category = Column(String, nullable=True)
    instagram_connected_at = Column(DateTime, nullable=True)
    instagram_last_sync = Column(DateTime, nullable=True)
    instagram_sync_enabled = Column(Boolean, default=True)

    orders = relationship("Order", back_populates="user")
    tasks = relationship("Task", back_populates="assigned_user")
    coin_transactions = relationship("CoinTransaction", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    fcm_tokens = relationship("UserFCMToken", back_populates="user")
    instagram_credential = relationship("InstagramCredential", back_populates="user", uselist=False, cascade="all, delete-orphan")
    daily_rewards = relationship("DailyReward", back_populates="user")
    statistics = relationship("UserStatistics", back_populates="user", uselist=False, cascade="all, delete-orphan")
    instagram_profile = relationship("InstagramProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    user_login_history = relationship("UserLoginHistory", back_populates="user", cascade="all, delete-orphan")

class OrderType(enum.Enum):
    like = "like"
    follow = "follow"
    comment = "comment"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    post_url = Column(Text, nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    target_count = Column(Integer, nullable=False)
    completed_count = Column(Integer, default=0)
    status = Column(Enum(OrderStatus), default=OrderStatus.active)  # Use the enum here
    comment_text = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="orders")
    tasks = relationship("Task", back_populates="order")

class TaskStatus(enum.Enum):
    pending = "pending"
    assigned = "assigned"
    in_progress = "in_progress"
    completed = "completed"
    expired = "expired"
    failed = "failed"

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)
    assigned_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    # Task specific fields for validation
    url = Column(Text, nullable=True)  # Instagram post/profile URL
    task_type = Column(String, nullable=True)  # 'like', 'follow', 'comment'
    comment_text = Column(Text, nullable=True)  # For comment tasks
    validation_log_id = Column(Integer, ForeignKey("validation_logs.id"), nullable=True)
    order = relationship("Order", back_populates="tasks")
    assigned_user = relationship("User", back_populates="tasks")
    validation_log = relationship(
        "ValidationLog",
        primaryjoin='Task.id == ValidationLog.task_id',
        uselist=False,
        back_populates="task"
    )

class CoinTransactionType(enum.Enum):
    earn = "earn"
    spend = "spend"
    withdraw = "withdraw"
    admin = "admin"

class CoinTransaction(Base):
    __tablename__ = "coin_transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Integer, nullable=False)
    type = Column(Enum(CoinTransactionType), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    note = Column(Text, nullable=True)
    user = relationship("User", back_populates="coin_transactions")

class ValidationLog(Base):
    __tablename__ = "validation_logs"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    validation_type = Column(String, nullable=True)  # 'like', 'follow', 'comment'
    url = Column(Text, nullable=True)  # Instagram post/profile URL
    success = Column(Boolean, default=False)  # Whether validation was successful
    status = Column(String) # e.g., "success", "failure_post_not_found", "failure_action_blocked"
    details = Column(String, nullable=True) # e.g., error message from instagrapi
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    task = relationship(
        "Task",
        primaryjoin='ValidationLog.task_id == Task.id',
        back_populates="validation_log"
    )
    user = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'order', 'task', 'reward', 'system'
    read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="notifications")

class UserFCMToken(Base):
    __tablename__ = "user_fcm_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User", back_populates="fcm_tokens")

class InstagramCredential(Base):
    __tablename__ = "instagram_credentials"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    instagram_user_id = Column(String(255), nullable=False, unique=True, index=True) # Instagram's own user ID (pk)
    access_token = Column(Text, nullable=False)
    access_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    username = Column(String(255), nullable=True, index=True) # Instagram username
    profile_picture_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="instagram_credential")

class DailyReward(Base):
    __tablename__ = "daily_rewards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    claimed_date = Column(Date, nullable=False)  # Use Date type for proper date comparison
    coin_amount = Column(Integer, nullable=False)
    consecutive_days = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="daily_rewards")

class EmailVerification(Base):
    __tablename__ = "email_verifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    verification_code = Column(String(6), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")

# User Statistics Model
class UserStatistics(Base):
    __tablename__ = "user_statistics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    total_earnings = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    active_tasks = Column(Integer, default=0)
    daily_streak = Column(Integer, default=0)
    level = Column(String, default="Bronz")
    weekly_earnings = Column(String, nullable=True)  # JSON string for 7 days
    task_distribution = Column(String, nullable=True)  # JSON string for pie chart
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="statistics")


class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), index=True)
    referred_id = Column(Integer, ForeignKey("users.id"), index=True)
    bonus_given = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Badge(Base):
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    icon = Column(String, nullable=True)  # For emoji or simple icon representations
    category = Column(String, default="achievement")  # gold, silver, bronze, instagram, achievement, special
    requirements_json = Column(String, nullable=True)  # JSON string for requirements
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserBadge(Base):
    __tablename__ = "user_badges"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), index=True)
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())

class Leaderboard(Base):
    __tablename__ = "leaderboards"
    id = Column(Integer, primary_key=True, index=True)
    period = Column(String, nullable=False)  # e.g., 'weekly', 'monthly'
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    score = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationSetting(Base):
    __tablename__ = "notification_settings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    push_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    order_notifications = Column(Boolean, default=True)
    task_notifications = Column(Boolean, default=True)
    reward_notifications = Column(Boolean, default=True)
    system_notifications = Column(Boolean, default=True)
    mental_health_notifications = Column(Boolean, default=True)

class DeviceIPLog(Base):
    __tablename__ = "device_ip_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    device_info = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    action = Column(String, nullable=True)  # e.g., 'login', 'register', 'withdrawal'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GDPRRequest(Base):
    __tablename__ = "gdpr_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    request_type = Column(String, nullable=False)  # 'access', 'delete'
    status = Column(String, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

class UserEducation(Base):
    __tablename__ = "user_education"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    step = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

class MentalHealthLog(Base):
    __tablename__ = "mental_health_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    notification_type = Column(String, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

class CoinWithdrawalRequest(Base):
    __tablename__ = "coin_withdrawal_requests"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Integer, nullable=False)
    status = Column(String, default='pending')  # 'pending', 'approved', 'rejected', 'locked'
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    suspicious = Column(Boolean, default=False)

class UserSocial(Base):
    __tablename__ = "user_social"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    referred_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    referral_code = Column(String, unique=True, nullable=True)
    total_referrals = Column(Integer, default=0)
    total_transferred = Column(Integer, default=0)
    total_received = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CoinWithdrawalVerification(Base):
    __tablename__ = "coin_withdrawal_verifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    verification_code = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InstagramProfile(Base):
    __tablename__ = "instagram_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    instagram_user_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    # Removed followers_count and following_count as per requirement
    media_count = Column(Integer, default=0)
    is_private = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Enhanced Instagram Profile Information
    full_name = Column(String, nullable=True)
    external_url = Column(String, nullable=True)
    category = Column(String, nullable=True)
    business_category_name = Column(String, nullable=True)
    business_phone = Column(String, nullable=True)
    business_email = Column(String, nullable=True)
    business_address_json = Column(Text, nullable=True)  # JSON string for address
    is_business_account = Column(Boolean, default=False)
    is_professional_account = Column(Boolean, default=False)
    professional_conversion_suggested = Column(Boolean, default=False)
    account_type = Column(String, nullable=True)  # 'personal', 'business', 'creator'
    
    # Engagement Metrics
    avg_likes_per_post = Column(Integer, default=0)
    avg_comments_per_post = Column(Integer, default=0)
    engagement_rate = Column(String, nullable=True)  # Stored as percentage string
    
    # Posting Patterns
    post_frequency = Column(String, nullable=True)  # 'daily', 'weekly', 'monthly'
    most_active_time = Column(String, nullable=True)  # Hour of day
    most_active_day = Column(String, nullable=True)  # Day of week
    
    # Content Analysis
    most_used_hashtags = Column(Text, nullable=True)  # JSON array
    content_categories = Column(Text, nullable=True)  # JSON array
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="instagram_profile")

# User Session Management
class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    session_token = Column(String, unique=True, nullable=False)
    device_info = Column(Text, nullable=True)  # JSON string with device details
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    location = Column(String, nullable=True)  # Country/City from IP
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="user_sessions")

# User Login History
class UserLoginHistory(Base):
    __tablename__ = "user_login_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    login_method = Column(String, nullable=True)  # 'password', 'social', 'token'
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    device_info = Column(Text, nullable=True)  # JSON string
    location = Column(String, nullable=True)  # Derived from IP
    login_status = Column(String, nullable=False)  # 'success', 'failed', 'blocked'
    failure_reason = Column(String, nullable=True)  # If login failed
    session_duration = Column(Integer, nullable=True)  # In minutes
    logged_out_at = Column(DateTime(timezone=True), nullable=True)
    logout_method = Column(String, nullable=True)  # 'manual', 'timeout', 'forced'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="user_login_history")

# Enhanced Instagram Data Storage
class InstagramPost(Base):
    __tablename__ = "instagram_posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    instagram_post_id = Column(String, unique=True, nullable=False)
    caption = Column(Text, nullable=True)
    media_type = Column(String, nullable=True)  # 'photo', 'video', 'carousel'
    media_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    hashtags = Column(Text, nullable=True)  # JSON array
    mentions = Column(Text, nullable=True)  # JSON array
    location = Column(String, nullable=True)
    
    # Engagement tracking
    last_likes_count = Column(Integer, default=0)
    last_comments_count = Column(Integer, default=0)
    engagement_rate = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Instagram Followers/Following Analytics
class InstagramConnection(Base):
    __tablename__ = "instagram_connections"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    instagram_user_id = Column(String, nullable=False)  # Target user's IG ID
    username = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    profile_pic_url = Column(String, nullable=True)
    connection_type = Column(String, nullable=False)  # 'follower', 'following'
    is_verified = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    follower_count = Column(Integer, nullable=True)
    following_count = Column(Integer, nullable=True)
    media_count = Column(Integer, nullable=True)
    
    # Relationship tracking
    followed_back = Column(Boolean, default=False)
    interaction_score = Column(Integer, default=0)  # Based on likes/comments
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# User Activity Log
class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    activity_type = Column(String, nullable=False)  # 'login', 'logout', 'task_complete', 'coin_earn', etc.
    activity_details = Column(Text, nullable=True)  # JSON string with details
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    extra_metadata = Column(Text, nullable=True)  # Additional JSON metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
