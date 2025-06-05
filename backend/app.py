# Kullanıcı profili
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Optional
from dotenv import load_dotenv 
import os
from dotenv import load_dotenv
load_dotenv() 


# Development mode for testing
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
SIMULATE_INSTAGRAM_CHALLENGES = os.getenv('SIMULATE_INSTAGRAM_CHALLENGES', 'false').lower() == 'true'

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status, Body, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import create_engine, select, and_, or_, func, desc
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import Optional, Dict, List, Union
from jose import JWTError, jwt
from datetime import datetime, timedelta
import time
import asyncio
import bcrypt
from passlib.context import CryptContext
import os
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, TwoFactorRequired, ChallengeRequired, BadPassword, ClientError, UserNotFound
import json
import sys
import importlib.util
import asyncio

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_instagram_collector import enhanced_instagram_collector
except ImportError:
    # If running from parent directory, try different import path
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))
    from enhanced_instagram_collector import enhanced_instagram_collector

from models import (
    Base, User, Order, Task, CoinTransaction, ValidationLog, OrderType, OrderStatus, TaskStatus, 
    CoinTransactionType, Notification, UserFCMToken, InstagramCredential, DailyReward, 
    EmailVerification, UserStatistics, InstagramProfile,
    # New models
    Referral, Badge, UserBadge, Leaderboard, NotificationSetting, DeviceIPLog, 
    GDPRRequest, UserEducation, MentalHealthLog, CoinWithdrawalRequest, UserSocial
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import requests

# Import new services
from instagram_service import InstagramAPIService
from selenium_instagram_service import SeleniumInstagramService
from background_jobs import BackgroundJobManager
from coin_security import CoinSecurityManager
from social_features import SocialFeaturesManager
from gdpr_compliance import GDPRComplianceManager
from user_education import UserEducationService, EducationModuleType
from mental_health import MentalHealthService

# Import dependencies for shared services
from dependencies import get_db, get_current_user, get_instagram_service

import logging 
import firebase_admin 
from firebase_admin import credentials, messaging
import firebase_admin
import logging

# Enhanced Notifications Import
from enhanced_notifications import (
    NotificationService,
    RealTimeNotificationManager, 
    NotificationType,
    NotificationPriority
)

# Enhanced Badge System Import
from enhanced_badge_system import (
    EnhancedBadgeSystem,
    BadgeCategory,
    BadgeType,
    get_enhanced_badge_system
) 

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Updated CryptContext configuration to work with latest bcrypt version
pwd_context = CryptContext(
    schemes=["bcrypt"],
    default="bcrypt",
    bcrypt__rounds=12,  # Explicitly set rounds
    deprecated="auto"
)

# --- Application Configuration ---
# Helper function to get int from env or default
def get_int_env(var_name: str, default: int) -> int:
    try:
        return int(os.getenv(var_name, default))
    except ValueError:
        logger.warning(f"Invalid value for {var_name} in environment. Using default: {default}")
        return default

# Helper function to get float from env or default (if needed in future)
# def get_float_env(var_name: str, default: float) -> float:
#     try:
#         return float(os.getenv(var_name, default))
#     except ValueError:
#         logger.warning(f"Invalid value for {var_name} in environment. Using default: {default}")
#         return default

# For Order Creation
DEFAULT_COIN_COST_PER_TARGET_UNIT = get_int_env("DEFAULT_COIN_COST_PER_TARGET_UNIT", 1)
MIN_ORDER_TARGET_COUNT = get_int_env("MIN_ORDER_TARGET_COUNT", 5)
MAX_ORDER_TARGET_COUNT = get_int_env("MAX_ORDER_TARGET_COUNT", 1000)

# For Task Completion
DEFAULT_COIN_REWARD_PER_TASK = get_int_env("DEFAULT_COIN_REWARD_PER_TASK", 10)

# Task Settings
DEFAULT_TASK_EXPIRATION_HOURS = get_int_env("DEFAULT_TASK_EXPIRATION_HOURS", 24)

# For Coin Withdrawal
MIN_COMPLETED_TASKS_FOR_WITHDRAWAL = get_int_env("MIN_COMPLETED_TASKS_FOR_WITHDRAWAL", 5)

# For Order Creation - Comment Length
MIN_COMMENT_LENGTH = get_int_env("MIN_COMMENT_LENGTH", 3)
MAX_COMMENT_LENGTH = get_int_env("MAX_COMMENT_LENGTH", 100)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/instagram_platform")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Function to create admin and test users on startup
def create_admin_user():
    """Create admin and test users if they don't exist"""
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter_by(username="admin").first()
        
        if not admin_user:
            logger.info("Creating admin user...")
            # Create admin user with special properties
            hashed_password = pwd_context.hash("admin")
            admin_user = User(
                username="admin",
                password_hash=hashed_password,
                full_name="System Administrator",
                is_admin_platform=True,
                coin_balance=999999,  # Give admin lots of coins
                # No Instagram data required for admin
                instagram_pk=None,
                instagram_username=None,
                instagram_session_data=None,
                profile_pic_url=None
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            logger.info("Admin user created successfully!")
        else:
            logger.info("Admin user already exists")
        
        # Check if test user exists
        test_user = db.query(User).filter_by(username="testuser").first()
        
        if not test_user:
            logger.info("Creating test user...")
            # Create test user with mock Instagram data
            hashed_password = pwd_context.hash("testpassword123")
            test_user = User(
                username="testuser",
                password_hash=hashed_password,
                full_name="Test User",
                is_admin_platform=False,
                coin_balance=1000,  # Give test user some coins
                # Mock Instagram data for test user
                instagram_pk="12345678901",  # Mock Instagram PK
                instagram_username="testuser_instagram",
                instagram_session_data='{"test": "mock_session_data"}',
                profile_pic_url=None  # Don't use broken URL for test user
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            logger.info("Test user created successfully!")
        else:
            logger.info("Test user already exists")
            
        # Create sample tasks/orders if none exist
        create_sample_tasks(db)
            
    except Exception as e:
        logger.error(f"Error creating admin/test users: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_tasks(db: Session):
    """Create sample tasks/orders for testing"""
    try:
        # Check if we already have tasks
        existing_orders = db.query(Order).count()
        if existing_orders > 0:
            logger.info("Sample tasks already exist")
            return
            
        logger.info("Creating sample tasks...")
        
        # Sample Instagram accounts and posts for tasks
        sample_tasks = [
            {
                "title": "Instagram Hesabını Takip Et",
                "description": "@example_account hesabını takip et ve 50 coin kazan!",
                "order_type": OrderType.follow,
                "post_url": "https://instagram.com/example_account",
                "target_count": 100,
                "coin_reward": 50,
                "priority": 1
            },
            {
                "title": "Fotoğrafı Beğen",
                "description": "Bu güzel fotoğrafı beğen ve 25 coin kazan!",
                "order_type": OrderType.like,
                "post_url": "https://instagram.com/p/example_post_1/",
                "target_count": 200,
                "coin_reward": 25,
                "priority": 2
            },
            {
                "title": "Sanat Hesabını Takip Et",
                "description": "@art_gallery hesabını takip et, sanatı destekle!",
                "order_type": OrderType.follow,
                "post_url": "https://instagram.com/art_gallery",
                "target_count": 75,
                "coin_reward": 60,
                "priority": 1
            },
            {
                "title": "Doğa Fotoğrafını Beğen",
                "description": "Bu muhteşem doğa manzarasını beğen!",
                "order_type": OrderType.like,
                "post_url": "https://instagram.com/p/nature_post_1/",
                "target_count": 150,
                "coin_reward": 30,
                "priority": 2
            },
            {
                "title": "Yemek Kanalını Takip Et",
                "description": "@food_lover hesabını takip et, lezzetli tarifler için!",
                "order_type": OrderType.follow,
                "post_url": "https://instagram.com/food_lover",
                "target_count": 90,
                "coin_reward": 55,
                "priority": 1
            },
            {
                "title": "Motivasyon Paylaşımını Beğen",
                "description": "Bu motivasyon verici paylaşımı beğen!",
                "order_type": OrderType.like,
                "post_url": "https://instagram.com/p/motivation_post/",
                "target_count": 120,
                "coin_reward": 35,
                "priority": 2
            }
        ]
        
        for task_data in sample_tasks:
            # Create order
            order = Order(
                order_type=task_data["order_type"],
                post_url=task_data["post_url"],
                target_count=task_data["target_count"],
                completed_count=0,
                status="active",
                created_at=datetime.now()
            )
            db.add(order)
            db.flush()  # To get the order ID
            
            logger.info(f"Created sample order: {task_data['title']}")
        
        db.commit()
        logger.info(f"Created {len(sample_tasks)} sample tasks successfully!")
        
    except Exception as e:
        logger.error(f"Error creating sample tasks: {e}")
        db.rollback()

# Define lifespan function for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    # Startup
    logger.info("Starting Instagram Coin Platform with advanced features...")
    
    # Create admin and test users if they don't exist
    create_admin_user()
    
    # Initialize database session for services
    db = SessionLocal()
    try:
        # Initialize all managers (they don't need async initialization in our current implementation)
        logger.info("Starting background job manager...")
        await background_job_manager.start()
        
        logger.info("All services initialized successfully")
        
        yield  # This is where the app runs
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        db.close()
        
        # Shutdown
        logger.info("Shutting down Instagram Coin Platform...")
        try:
            await background_job_manager.stop()
            logger.info("All services shut down successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Instagram Coin Platform API",
    description="Advanced Instagram task-based coin earning platform with social features, GDPR compliance, and security",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için. Production'da spesifik domain'leri belirtin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize background job manager with Instagram service from dependencies
from dependencies import instagram_service_instance
background_job_manager = BackgroundJobManager(SessionLocal, instagram_api_service=instagram_service_instance)

# Initialize advanced services (those that need session factory)
# instagram_service_instance is now created in dependencies.py
selenium_service = SeleniumInstagramService()
# background_job_manager will be initialized after getting instagram service from dependencies
coin_security_manager = CoinSecurityManager(SessionLocal)
social_features_manager = SocialFeaturesManager(SessionLocal)
gdpr_compliance_manager = GDPRComplianceManager(SessionLocal)

# Services that expect db sessions will be created per-request in endpoints
# mental_health_service and user_education_service

# Initialize notification services
from enhanced_notifications import initialize_notification_service
initialize_notification_service(SessionLocal)
notification_service = NotificationService(SessionLocal)
realtime_notification_manager = RealTimeNotificationManager()

# Initialize enhanced badge system
enhanced_badge_system = get_enhanced_badge_system(SessionLocal, notification_service)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set. Application cannot start.")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  

# FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY") 
# if not FCM_SERVER_KEY: 
#     print("WARNING: FCM_SERVER_KEY is not set. Push notifications will not work.") 

# --- Firebase Admin SDK Setup --- 
GOOGLE_APPLICATION_CREDENTIALS_JSON_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON_PATH")
if GOOGLE_APPLICATION_CREDENTIALS_JSON_PATH and os.path.exists(GOOGLE_APPLICATION_CREDENTIALS_JSON_PATH):
    try:
        # Check if Firebase app already exists
        try:
            firebase_admin.get_app()
            logger.info("Firebase Admin SDK already initialized.")
        except ValueError:
            # App doesn't exist, initialize it
            cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS_JSON_PATH)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}. Push notifications will not work.", exc_info=True)
        # Uygulamanın çalışmaya devam etmesine izin ver, ancak push'lar çalışmayacak.
else:
    logger.warning("GOOGLE_APPLICATION_CREDENTIALS_JSON_PATH environment variable not set or file not found. Push notifications will not work.")
# --- END Firebase Admin SDK Setup ---

sessions = {}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None

class InstagramLoginRequest(BaseModel):
    username: str
    password: str
    verification_code: Optional[str] = None
    # proxy: Optional[str] = None 

class InstagramChallengeRequest(BaseModel):
    username: str
    challenge_code: str

class InstagramChallengeResponse(BaseModel):
    success: bool
    challenge_required: bool
    message: str
    challenge_url: Optional[str] = None
    challenge_details: Optional[Dict] = None
    username: Optional[str] = None

class InstagramLoginResponse(BaseModel):
    access_token: str
    token_type: str
    message: Optional[str] = None
    requires_2fa: bool = False
    user_id: Optional[int] = None
    # Additional fields for successful login
    success: bool = True
    username: Optional[str] = None
    full_name: Optional[str] = None
    user_data: Optional[Dict] = None 

class UserLogin(BaseModel):
    username: str
    password: str

class OrderCreate(BaseModel):
    post_url: str
    order_type: OrderType
    target_count: int
    comment_text: Optional[str] = None 

class TaskComplete(BaseModel):
    task_id: int

class WithdrawRequest(BaseModel):
    amount: int

# Enhanced request/response models for new features
class ReferralCodeRequest(BaseModel):
    referrer_code: str

class CoinTransferRequest(BaseModel):
    recipient_username: str
    amount: int
    message: Optional[str] = None

class NotificationSettingsUpdate(BaseModel):
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    task_reminders: Optional[bool] = None
    achievement_alerts: Optional[bool] = None
    social_notifications: Optional[bool] = None

class GDPRDataRequest(BaseModel):
    request_type: str  # 'export' or 'delete'
    reason: Optional[str] = None

class EducationModuleProgress(BaseModel):
    module_id: str
    lesson_id: str
    completed: bool = True

class MentalHealthMoodReport(BaseModel):
    mood_score: int  # 1-10 scale
    notes: Optional[str] = None

class CoinWithdrawalRequest(BaseModel):
    amount: int
    withdrawal_method: str  # 'bank_transfer', 'paypal', etc.
    account_details: Dict[str, str]

class AdminUserAction(BaseModel):
    action: str  # 'suspend', 'unsuspend', 'ban', 'unban'
    reason: Optional[str] = None
    duration_hours: Optional[int] = None

class SuspiciousActivityReport(BaseModel):
    activity_type: str
    description: str
    evidence: Optional[Dict] = None

class InstagramProfileStats(BaseModel):
    instagram_user_id: str
    username: str
    full_name: Optional[str] = None
    profile_pic_url: Optional[str] = None
    media_count: Optional[int] = None
    is_private: Optional[bool] = None
    is_verified: Optional[bool] = None

class ProfileResponse(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    profile_pic_url: str | None = None
    coin_balance: int
    diamondBalance: int
    completed_tasks: int
    active_tasks: int
    is_admin_platform: bool = False
    followers_count: int = 0
    following_count: int = 0
    instagram_stats: Optional[InstagramProfileStats] = None

class ActiveTaskResponse(BaseModel):
    task_id: int
    order_id: int
    expires_at: datetime | None = None
    order_post_url: str | None = None
    order_type: OrderType | None = None

class TaskSchema(BaseModel):
    id: int
    order_id: int
    service_type: str  # e.g., "like", "follow"
    target_url: Optional[str] = None # URL for the task (e.g. post to like)
    status: str
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True # For Pydantic v2, use orm_mode = True for v1

def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login")), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise credentials_exception
    return user

# --- DAILY REWARD SYSTEM ---
@app.post("/daily-reward", tags=["User Actions"])
async def claim_daily_reward_legacy(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Legacy daily reward endpoint - redirects to new enhanced endpoint
    """
    # Redirect to the enhanced daily reward endpoint
    from instagram_endpoints import claim_daily_reward_extended
    return await claim_daily_reward_extended(current_user, db)

# Kullanıcı kayıt
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=user.username).first():
        raise HTTPException(status_code=400, detail="Kullanıcı adı zaten kayıtlı.")
    hashed = pwd_context.hash(user.password)
    db_user = User(username=user.username, password_hash=hashed, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Kayıt başarılı."}

# Kullanıcı login (platform specific)
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for username: '{form_data.username}'")

    # --- BEGIN TEST USER BYPASS ---
    if form_data.username == "testuser" and form_data.password == "testpassword":
        logger.info(f"Attempting test user login for '{form_data.username}'")
        user = db.query(User).filter_by(username=form_data.username).first()
        if not user:
            logger.info(f"Test user '{form_data.username}' not found. Creating new test user.")
            hashed_password = pwd_context.hash("testpassword")
            user = User(
                username="testuser",
                password_hash=hashed_password,
                full_name="Test User",
                coin_balance=0,  # Default coin balance
                is_admin_platform=False,  # Default to not admin
                # Initialize other essential fields from your User model with defaults if necessary
                # email=f"{form_data.username}@example.com", # Example if email is required
                # created_at=datetime.utcnow(), # Example
                # last_login_at=datetime.utcnow() # Example
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Test user '{form_data.username}' created successfully.")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = jwt.encode(
            {"sub": user.username, "exp": datetime.utcnow() + access_token_expires},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        logger.info(f"Test user login successful for '{form_data.username}'. Token created.")
        return {"access_token": access_token, "token_type": "bearer"}
    # --- END TEST USER BYPASS ---

    user = db.query(User).filter_by(username=form_data.username).first()

    if not user:
        logger.info(f"User '{form_data.username}' not found. Attempting to auto-register.")
        # Auto-registration logic
        hashed_password = pwd_context.hash(form_data.password)
        new_user_data = User(username=form_data.username, password_hash=hashed_password)
        db.add(new_user_data)
        try:
            db.commit()
            db.refresh(new_user_data)
            logger.info(f"User '{form_data.username}' auto-registered successfully during login attempt.")
            user = new_user_data # The newly created user is now 'user' for token generation
        except IntegrityError:
            db.rollback()
            logger.error(f"Auto-registration for '{form_data.username}' failed due to integrity error (e.g., race condition or username became non-unique).")
            # It's possible another request registered the user between the initial check and this commit.
            # Try fetching the user again in this specific scenario.
            user = db.query(User).filter_by(username=form_data.username).first()
            if not user: # Still not found, or some other integrity error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not process login/registration. Please try again.",
                )
            # If user is found now, proceed to password check as if they existed initially.
            # This means the original 'if not user:' path was for a genuine new user,
            # but a race condition occurred. Now we treat it as an existing user.
            password_verified = pwd_context.verify(form_data.password, user.password_hash)
            if not password_verified:
                logger.warning(f"Password verification failed for user '{form_data.username}' after auto-registration race condition resolution.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Incorrect password.",
                )
    else: # User exists, verify password
        password_verified = pwd_context.verify(form_data.password, user.password_hash)
        if not password_verified:
            logger.warning(f"Password verification failed for existing user '{form_data.username}'.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password.",
            )

    logger.info(f"User '{form_data.username}' authenticated successfully (login or auto-register).")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode({"sub": user.username, "exp": datetime.utcnow() + access_token_expires}, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Login successful for user '{form_data.username}'. Token created.")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login-instagram", response_model=Union[InstagramLoginResponse, InstagramChallengeResponse])
async def login_instagram(
    request_data: InstagramLoginRequest, 
    db: Session = Depends(get_db),
    instagram_service: InstagramAPIService = Depends(get_instagram_service)
):
    """
    Advanced Instagram login with comprehensive error handling
    Supports 2FA, challenge handling, and proper session management
    Special case: admin/admin login bypasses Instagram authentication
    """
    try:
        logger.info(f"Instagram authentication attempt for user: {request_data.username}")
        
        # Special case: Admin login (bypasses Instagram authentication)
        if request_data.username.lower() == "admin" and request_data.password == "admin":
            logger.info("Admin login detected - bypassing Instagram authentication")
            
            # Find admin user in database
            admin_user = db.query(User).filter_by(username="admin").first()
            
            if not admin_user:
                logger.error("Admin user not found in database!")
                raise HTTPException(
                    status_code=500,
                    detail="Admin kullanıcısı bulunamadı. Lütfen sistem yöneticisiyle iletişime geçin."
                )
            
            # Update admin user in our database
            admin_user.last_login = datetime.utcnow()
            db.commit()
            
            # Create platform access token for admin
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            platform_access_token = jwt.encode(
                {"sub": admin_user.username, "exp": datetime.utcnow() + access_token_expires}, 
                SECRET_KEY, 
                algorithm=ALGORITHM
            )
            
            logger.info("Admin login successful - returning admin access token")
            
            return InstagramLoginResponse(
                access_token=platform_access_token,
                token_type="bearer",
                requires_2fa=False,
                message="Admin girişi başarılı!",
                success=True,
                user_id=999999,  # Special admin ID
                username="admin",
                full_name="System Administrator",
                user_data={
                    "is_admin": True,
                    "bypass_instagram": True,
                    "coin_balance": admin_user.coin_balance
                }
            )
        
        # Special case: Test user login (bypasses Instagram authentication for testing)
        if request_data.username.lower() == "testuser" and request_data.password == "testpassword123":
            logger.info("Test user login detected - bypassing Instagram authentication")
            
            # Find test user in database
            test_user = db.query(User).filter_by(username="testuser").first()
            
            if not test_user:
                logger.error("Test user not found in database!")
                raise HTTPException(
                    status_code=404,
                    detail="Test kullanıcısı bulunamadı. Lütfen test kullanıcısını oluşturun."
                )
            
            # Update test user in our database with mock Instagram data
            test_user.last_login = datetime.utcnow()
            # Removed follower/following count updates as per requirement
            test_user.instagram_posts_count = 250 # Mock posts count
            test_user.instagram_bio = "Test kullanıcısı - Mock Instagram profili"
            test_user.instagram_is_verified = True  # Make test user verified for testing
            test_user.instagram_last_sync = datetime.utcnow()
            
            # Also update/create instagram_profiles table entry for consistency
            instagram_profile = db.query(InstagramProfile).filter_by(user_id=test_user.id).first()
            if not instagram_profile:
                # Generate unique Instagram user ID for test user based on their user ID
                unique_ig_user_id = f"test_{test_user.id}_{int(datetime.utcnow().timestamp())}"
                instagram_profile = InstagramProfile(
                    user_id=test_user.id,
                    instagram_user_id=unique_ig_user_id,
                    username=test_user.instagram_username,
                    full_name=test_user.full_name,
                    bio=test_user.instagram_bio,
                    profile_picture_url=test_user.profile_pic_url,
                    media_count=250,
                    is_verified=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(instagram_profile)
            else:
                # Update existing profile but don't change the instagram_user_id to avoid conflicts
                instagram_profile.media_count = 250
                instagram_profile.bio = test_user.instagram_bio
                instagram_profile.is_verified = True
                instagram_profile.updated_at = datetime.utcnow()
            
            db.commit()
            
            # Create platform access token for test user
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            platform_access_token = jwt.encode(
                {"sub": test_user.username, "exp": datetime.utcnow() + access_token_expires}, 
                SECRET_KEY, 
                algorithm=ALGORITHM
            )
            
            logger.info("Test user login successful - saved mock Instagram data to database")
            
            return InstagramLoginResponse(
                access_token=platform_access_token,
                token_type="bearer",
                requires_2fa=False,
                message="Test kullanıcısı Instagram girişi başarılı! (Mock data)",
                success=True,
                user_id=test_user.instagram_pk,  # Using the mock Instagram PK
                username=test_user.instagram_username,  # Using the mock Instagram username
                full_name=test_user.full_name,
                user_data={
                    "id": test_user.id,
                    "username": test_user.username,
                    "instagram_username": test_user.instagram_username,
                    "full_name": test_user.full_name,
                    "profile_pic_url": test_user.profile_pic_url,
                    "coins": test_user.coin_balance,
                    "is_admin": test_user.is_admin_platform,
                    "bypass_instagram": True,
                    "test_mode": True
                }
            )
        
        # Regular Instagram authentication for non-admin users
        # Use our advanced Instagram service for authentication
        auth_result = await instagram_service.authenticate_user(
            username=request_data.username,
            password=request_data.password
        )
        
        if not auth_result["success"]:
            error_type = auth_result.get("error_type", "unknown")
            error_message = auth_result.get("message") or auth_result.get("details") or auth_result.get("error", "Unknown error")
            
            if auth_result.get("requires_challenge") or error_type == "challenge_required":
                # Return challenge information using the proper model
                return InstagramChallengeResponse(
                    success=False,
                    challenge_required=True,
                    message=error_message,
                    challenge_url=auth_result.get("challenge_url"),
                    challenge_details=auth_result.get("challenge_data"),
                    username=request_data.username
                )
            elif error_type == "2fa_required":
                return InstagramChallengeResponse(
                    success=False,
                    challenge_required=True,
                    message=error_message,
                    challenge_url=None,
                    challenge_details={"type": "2fa"},
                    username=request_data.username
                )
            elif error_type == "bad_password" or error_type == "bad_credentials":
                raise HTTPException(
                    status_code=401, 
                    detail=error_message
                )
            elif error_type == "rate_limited":
                raise HTTPException(
                    status_code=429, 
                    detail=error_message
                )
            elif error_type == "user_not_found":
                raise HTTPException(
                    status_code=404, 
                    detail=error_message
                )
            elif error_type == "account_suspended":
                raise HTTPException(
                    status_code=403, 
                    detail=error_message
                )
            elif error_type == "connection_error":
                raise HTTPException(
                    status_code=503, 
                    detail=error_message
                )
            elif error_type == "authentication_failed":
                # Handle Instagram API authentication failures (400 errors)
                raise HTTPException(
                    status_code=401, 
                    detail=error_message
                )
            else:
                # Generic error handling
                raise HTTPException(
                    status_code=400, 
                    detail=error_message
                )
        
        # Authentication successful - extract data
        # Safely extract data with proper validation
        if not auth_result.get("user_data"):
            raise HTTPException(
                status_code=500,
                detail="Authentication response missing user data"
            )
        
        if not auth_result.get("session_data"):
            raise HTTPException(
                status_code=500,
                detail="Authentication response missing session data"
            )
            
        # Client is optional - may not be available in all authentication modes
        client = auth_result.get("client")
        if not client:
            logger.warning("Client not available in authentication response - continuing without client reference")
        
        user_data = auth_result["user_data"]
        session_data = auth_result["session_data"]
        client = auth_result.get("client")
        
        ig_pk_str = user_data.get("instagram_pk")
        ig_username = user_data.get("username")
        
        if not ig_pk_str or not ig_username:
            raise HTTPException(
                status_code=500,
                detail="Missing required user data fields"
            )
        
        logger.info(f"Instagram authentication successful for {ig_username} (PK: {ig_pk_str})")
        
        # Check if user already exists in our platform
        # First check by Instagram PK (most reliable)
        user = db.query(User).filter(User.instagram_pk == ig_pk_str).first()
        
        # If not found by Instagram PK, check by username
        if not user:
            user = db.query(User).filter(User.username == ig_username).first()
            if user:
                logger.info(f"Found existing user by username {ig_username}, updating Instagram PK")
                # Update the user's Instagram PK if it was missing
                user.instagram_pk = ig_pk_str
                user.instagram_username = ig_username
        
        if not user:
            # Create new platform user
            logger.info(f"Creating new platform user for Instagram user {ig_username}")
            
            # Generate a unique username if the Instagram username already exists
            unique_username = ig_username
            counter = 1
            while db.query(User).filter(User.username == unique_username).first():
                unique_username = f"{ig_username}_{counter}"
                counter += 1
                if counter > 100:  # Safety limit
                    raise HTTPException(
                        status_code=500,
                        detail="Unable to generate unique username"
                    )
            
            if unique_username != ig_username:
                logger.info(f"Username {ig_username} already exists, using {unique_username}")
            
            user = User(
                username=unique_username,
                instagram_pk=ig_pk_str,
                instagram_username=ig_username,
                full_name=user_data["full_name"],
                profile_pic_url=user_data["profile_pic_url"],
                instagram_session_data=json.dumps(session_data),
                coin_balance=0,  # Start with 0 coins
                is_admin_platform=False
            )
            db.add(user)
            
            try:
                db.flush()  # Get user.id
                
                # Create InstagramCredential record
                instagram_cred = InstagramCredential(
                    user_id=user.id,
                    instagram_user_id=ig_pk_str,
                    access_token="session_based",  # We use session data instead
                    username=ig_username,
                    profile_picture_url=user_data["profile_pic_url"]
                )
                db.add(instagram_cred)
                
                # Save session to cache
                instagram_service.save_session(user.id, client)
                
                logger.info(f"Created new user and Instagram credentials for {ig_username} (platform username: {unique_username})")
                
            except IntegrityError as ie:
                db.rollback()
                logger.error(f"IntegrityError creating user {ig_username}: {ie}")
                # Try to find the existing user one more time
                existing_user = db.query(User).filter(
                    or_(User.instagram_pk == ig_pk_str, User.username == ig_username)
                ).first()
                if existing_user:
                    logger.info(f"Found existing user after IntegrityError, using existing user: {existing_user.username}")
                    user = existing_user
                    # Update the existing user with new session data
                    user.instagram_session_data = json.dumps(session_data)
                    user.full_name = user_data["full_name"]
                    user.profile_pic_url = user_data["profile_pic_url"]
                    if not user.instagram_pk:
                        user.instagram_pk = ig_pk_str
                    if not user.instagram_username:
                        user.instagram_username = ig_username
                else:
                    raise HTTPException(
                        status_code=500, 
                        detail="Kullanıcı oluşturulurken veritabanı hatası oluştu."
                    )
                
        else:
            # Update existing user
            logger.info(f"Updating existing user {user.username} with new Instagram session")
            user.instagram_session_data = json.dumps(session_data)
            user.full_name = user_data["full_name"]
            user.profile_pic_url = user_data["profile_pic_url"]
            
            # Update Instagram credentials
            instagram_cred = db.query(InstagramCredential).filter(
                InstagramCredential.user_id == user.id
            ).first()
            
            if instagram_cred:
                instagram_cred.username = ig_username
                instagram_cred.profile_picture_url = user_data["profile_pic_url"]
            else:
                # Create if doesn't exist
                instagram_cred = InstagramCredential(
                    user_id=user.id,
                    instagram_user_id=ig_pk_str,
                    access_token="session_based",
                    username=ig_username,
                    profile_picture_url=user_data["profile_pic_url"]
                )
                db.add(instagram_cred)
            
            # Save updated session
            instagram_service.save_session(user.id, client)
        
        # Commit all changes
        db.commit()
        
        # CRITICAL FIX: Collect and save comprehensive Instagram profile data
        try:
            if client:
                logger.info(f"[PROFILE_DEBUG] Starting comprehensive Instagram profile data collection for {ig_username}")
                logger.info(f"[PROFILE_DEBUG] Client type: {type(client)}, ig_pk_str: {ig_pk_str}")
                
                # Get comprehensive profile data using the authenticated client
                logger.info(f"[PROFILE_DEBUG] Calling get_full_user_info...")
                full_profile_data = await instagram_service.get_full_user_info(client, ig_pk_str)
                logger.info(f"[PROFILE_DEBUG] get_full_user_info returned: {full_profile_data}")
                
                if full_profile_data:
                    logger.info(f"[PROFILE_DEBUG] Retrieved full profile data for {ig_username}: posts={full_profile_data.get('media_count', 0)}")
                    
                    # Save the comprehensive profile data to database
                    logger.info(f"[PROFILE_DEBUG] Calling _save_instagram_profile_data...")
                    await instagram_service._save_instagram_profile_data(db, user.id, full_profile_data)
                    logger.info(f"[PROFILE_DEBUG] Profile data saved, committing to database...")
                    db.commit()
                    logger.info(f"[PROFILE_DEBUG] Database commit completed")
                    
                    # Update user_data with the comprehensive data for response (excluding follower/following)
                    user_data.update({
                        "media_count": full_profile_data.get("media_count", 0)
                    })
                    
                    logger.info(f"[PROFILE_DEBUG] Successfully saved comprehensive Instagram profile data for {ig_username}")
                else:
                    logger.warning(f"[PROFILE_DEBUG] Could not retrieve comprehensive profile data for {ig_username}, using basic data")
            else:
                logger.warning(f"[PROFILE_DEBUG] No client available for comprehensive profile data collection for {ig_username}")
        except Exception as profile_error:
            logger.error(f"[PROFILE_DEBUG] Error collecting comprehensive profile data for {ig_username}: {profile_error}")
            logger.error(f"[PROFILE_DEBUG] Exception type: {type(profile_error)}")
            import traceback
            logger.error(f"[PROFILE_DEBUG] Full traceback: {traceback.format_exc()}")
            # Continue with login even if profile data collection fails
        
        # CRITICAL FIX: Call enhanced_instagram_collector to sync real data
        try:
            if client:
                logger.info(f"[COLLECTOR_DEBUG] Starting enhanced_instagram_collector sync for user {user.id}")
                
                # The client is already stored in enhanced_instagram_collector via save_session()
                # Now call sync to collect real Instagram data
                sync_result = await enhanced_instagram_collector.sync_user_instagram_data(user.id)
                
                if sync_result.get("success"):
                    logger.info(f"[COLLECTOR_DEBUG] Successfully synced Instagram data for user {user.id}: {sync_result.get('message')}")
                else:
                    logger.warning(f"[COLLECTOR_DEBUG] Failed to sync Instagram data for user {user.id}: {sync_result.get('message')}")
            else:
                logger.warning(f"[COLLECTOR_DEBUG] No client available for enhanced collector sync for user {user.id}")
        except Exception as collector_error:
            logger.error(f"[COLLECTOR_DEBUG] Error in enhanced_instagram_collector sync for user {user.id}: {collector_error}")
            logger.error(f"[COLLECTOR_DEBUG] Exception type: {type(collector_error)}")
            import traceback
            logger.error(f"[COLLECTOR_DEBUG] Full traceback: {traceback.format_exc()}")
            # Continue with login even if collector sync fails
        
        # Create platform access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        platform_access_token = jwt.encode(
            {"sub": user.username, "exp": datetime.utcnow() + access_token_expires}, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
        
        logger.info(f"Instagram login completed successfully for {ig_username}")
        
        return InstagramLoginResponse(
            access_token=platform_access_token,
            token_type="bearer",
            requires_2fa=False,
            message="Instagram girişi başarılı!",
            user_id=user_data["instagram_pk"],
            username=user_data["username"],
            full_name=user_data["full_name"]
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during Instagram login for {request_data.username}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Instagram girişi sırasında beklenmedik hata: {str(e)}"
        )

# Global dict to store pending challenges for manual terminal input
pending_manual_challenges = {}

@app.post("/login-instagram-challenge")
async def login_instagram_challenge(request_data: InstagramChallengeRequest, db: Session = Depends(get_db)):
    """
    Handle Instagram challenge response - Manual Terminal Input System
    """
    try:
        username = request_data.username
        challenge_code = request_data.challenge_code
        
        # TERMINAL OUTPUT - Show the code for manual entry
        print("\n" + "="*60)
        print(f"🔐 INSTAGRAM CHALLENGE CODE FOR: {username}")
        print(f"📱 CODE TO ENTER: {challenge_code}")
        print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
        print("="*60)
        print(f"👤 Go to Instagram and manually enter this code for {username}")
        print("✅ After entering the code on Instagram, the system will wait for confirmation...")
        print("="*60 + "\n")
        
        # Store the challenge request
        pending_manual_challenges[username] = {
            "code": challenge_code,
            "timestamp": datetime.now(),
            "status": "waiting_manual_entry"
        }
        
        # Wait for a reasonable time (simulate the process)
        await asyncio.sleep(5)
        
        # For now, simulate a successful manual entry
        # In real scenario, you would manually confirm success
        print(f"⏳ Waiting for manual confirmation for {username}...")
        
        # Simulate successful login (you can modify this part)
        # For demo purposes, we'll assume success after manual entry
        
        # Check if user exists or create new user
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            # Generate a simple Instagram PK for manual users
            ig_pk = str(abs(hash(username)) % 10000000000)
            
            # Create new user
            user = User(
                username=username,
                instagram_pk=ig_pk,
                instagram_username=username,
                full_name=f"{username} (Manual Entry)",
                profile_pic_url="",
                instagram_session_data=json.dumps({"manual_auth": True, "code": challenge_code}),
                coin_balance=0,
                is_admin_platform=False
            )
            db.add(user)
            db.commit()
            
            committed_user = db.query(User).filter(User.username == username).first()
            if committed_user is None or committed_user.id is None:
                logger.error(f"CRITICAL FAILURE: User ID is None even after commit and re-fetch for {username}.")
                raise HTTPException(status_code=500, detail="Internal server error: Failed to retrieve user ID after creation.")
            user = committed_user 

            # Create Instagram credentials
            instagram_cred = InstagramCredential(
                user_id=user.id,
                instagram_user_id=ig_pk,
                access_token="manual_session",
                username=username,
                profile_picture_url=""
            )
            db.add(instagram_cred)
        else:
            # Update existing user with manual auth
            user.instagram_session_data = json.dumps({"manual_auth": True, "code": challenge_code})
        
        db.commit()
        
        # Clean up pending challenge
        if username in pending_manual_challenges:
            del pending_manual_challenges[username]
        
        # Create platform token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        platform_access_token = jwt.encode(
            {"sub": user.username, "exp": datetime.utcnow() + access_token_expires}, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
        
        print(f"✅ Manual challenge completed successfully for {username}")
        print(f"🎉 User logged in via manual Instagram authentication\n")
        
        return InstagramLoginResponse(
            access_token=platform_access_token,
            token_type="bearer",
            requires_2fa=False,
            message=f"Instagram challenge başarıyla tamamlandı! Giriş yapılıyor...",
            success=True,
            user_id=user.instagram_pk,
            username=username,
            full_name=user.full_name,
            user_data={
                "id": user.id,
                "username": user.username,
                "instagram_username": user.instagram_username,
                "full_name": user.full_name,
                "profile_pic_url": user.profile_pic_url,
                "coins": user.coin_balance,
                "is_admin": user.is_admin_platform,
                "manual_auth": True
            }
        )
        
    except Exception as e:
        logger.error(f"Error in manual challenge system for {request_data.username}: {e}")
        raise HTTPException(status_code=500, detail=f"Manuel challenge sistemi hatası: {str(e)}")

@app.get("/instagram/challenge-status/{username}")
async def get_challenge_status(
    username: str, 
    db: Session = Depends(get_db),
    instagram_service: InstagramAPIService = Depends(get_instagram_service)
):
    """
    Get challenge status for a user
    """
    try:
        result = await instagram_service.get_challenge_status(username)
        return JSONResponse(
            status_code=200,
            content=result
        )
    except Exception as e:
        logger.error(f"Get challenge status failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to get challenge status: {str(e)}"
            }
        )

@app.delete("/instagram/challenge/{username}")
async def clear_challenge(
    username: str, 
    db: Session = Depends(get_db),
    instagram_service: InstagramAPIService = Depends(get_instagram_service)
):
    """
    Clear challenge for a user
    """
    try:
        result = await instagram_service.clear_challenge(username)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Challenge cleared successfully"
            }
        )
    except Exception as e:
        logger.error(f"Clear challenge failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to clear challenge: {str(e)}"
            }
        )

@app.post("/instagram/challenge-resolve", response_model=Union[InstagramLoginResponse, InstagramChallengeResponse])
async def resolve_instagram_challenge(
    request_data: InstagramChallengeRequest, 
    db: Session = Depends(get_db),
    instagram_service: InstagramAPIService = Depends(get_instagram_service)
):
    """
    Resolve Instagram challenge with verification code (public endpoint for login flow)
    """
    try:
        logger.info(f"Instagram challenge resolution attempt for user: {request_data.username}")
        
        # Use our Instagram service to resolve the challenge
        result = await instagram_service.resolve_challenge(
            username=request_data.username,
            challenge_code=request_data.challenge_code
        )
        
        if result["success"]:
            # Challenge resolved successfully - extract data
            user_data = result["user_data"]
            session_data = result["session_data"]
            client = result.get("client")  # Client might not be available for simulated challenges
            
            ig_pk_str = user_data["instagram_pk"]
            ig_username = user_data["username"]
            
            logger.info(f"Instagram challenge resolved successfully for {ig_username} (PK: {ig_pk_str})")
            
            # Check if user already exists in our platform (check by both instagram_pk and username)
            user = db.query(User).filter(
                or_(User.instagram_pk == ig_pk_str, User.username == ig_username)
            ).first()
            
            if not user:
                # Create new platform user
                logger.info(f"Creating new platform user for Instagram user {ig_username}")
                user = User(
                    username=ig_username,
                    instagram_pk=ig_pk_str,
                    instagram_username=ig_username,
                    full_name=user_data["full_name"],
                    profile_pic_url=user_data["profile_pic_url"],
                    instagram_session_data=json.dumps(session_data),
                    coin_balance=0,  # Start with 0 coins
                    is_admin_platform=False
                )
                db.add(user)
                
                try:
                    # Commit the user first to get the ID
                    db.commit()
                    db.refresh(user)  # Refresh to get the generated ID
                    
                    logger.info(f"Created new user with ID: {user.id}")
                    
                    # Create InstagramCredential record
                    instagram_cred = InstagramCredential(
                        user_id=user.id,
                        instagram_user_id=ig_pk_str,
                        access_token="session_based",  # We use session data instead
                        username=ig_username,
                        profile_picture_url=user_data["profile_pic_url"]
                    )
                    db.add(instagram_cred)
                    
                    db.commit()
                    logger.info(f"New user created with ID: {user.id}")
                    
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error creating new user: {e}")
                    raise HTTPException(status_code=500, detail="Kullanıcı oluşturulurken hata oluştu")
            else:
                # Update existing user
                logger.info(f"Updating existing user {user.id} with new session data")
                user.instagram_session_data = json.dumps(session_data)
                user.full_name = user_data["full_name"]
                user.profile_pic_url = user_data["profile_pic_url"]
                
                # Update Instagram credential
                instagram_cred = db.query(InstagramCredential).filter(
                    InstagramCredential.user_id == user.id
                ).first()
                if instagram_cred:
                    instagram_cred.profile_picture_url = user_data["profile_pic_url"]
                
                db.commit()
            
            # CRITICAL FIX: Collect and save comprehensive Instagram profile data after challenge resolution
            try:
                if client:
                    logger.info(f"Collecting comprehensive Instagram profile data for {ig_username} after challenge resolution")
                    
                    # Get comprehensive profile data using the authenticated client
                    full_profile_data = await instagram_service.get_full_user_info(client, ig_pk_str)
                    if full_profile_data:
                        logger.info(f"Retrieved full profile data for {ig_username}: followers={full_profile_data.get('follower_count', 0)}, following={full_profile_data.get('following_count', 0)}, posts={full_profile_data.get('media_count', 0)}")
                        
                        # Save the comprehensive profile data to database
                        await instagram_service._save_instagram_profile_data(db, user.id, full_profile_data)
                        db.commit()
                        
                        logger.info(f"Successfully saved comprehensive Instagram profile data for {ig_username} after challenge resolution")
                    else:
                        logger.warning(f"Could not retrieve comprehensive profile data for {ig_username} after challenge resolution")
                else:
                    logger.warning(f"No client available for comprehensive profile data collection for {ig_username} after challenge resolution")
            except Exception as profile_error:
                logger.error(f"Error collecting comprehensive profile data for {ig_username} after challenge resolution: {profile_error}")
                # Continue with login even if profile data collection fails
            
            # Generate access token for the authenticated user
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = jwt.encode(
                {"sub": str(user.id), "exp": datetime.utcnow() + access_token_expires}, 
                SECRET_KEY, 
                algorithm=ALGORITHM
            )
            
            return InstagramLoginResponse(
                success=True,
                message="Instagram challenge başarıyla çözüldü ve giriş yapıldı!",
                access_token=access_token,
                token_type="bearer",
                user_data={
                    "id": user.id,
                    "username": user.username,
                    "instagram_username": user.instagram_username,
                    "full_name": user.full_name,
                    "profile_pic_url": user.profile_pic_url,
                    "coins": user.coin_balance,
                    "is_admin": user.is_admin_platform
                }
            )
        else:
            # Challenge resolution failed
            error_message = result.get("message", "Challenge kodu doğrulanamadı")
            
            # Check if this is an invalid code error that should still allow retry
            if result.get("error_type") == "invalid_code" or "geçersiz" in error_message.lower():
                return InstagramChallengeResponse(
                    success=False,
                    challenge_required=True,
                    message=error_message,
                    challenge_url=None,
                    challenge_details={"error": "invalid_code"},
                    username=request_data.username
                )
            else:
                # Other errors - treat as permanent failure
                raise HTTPException(
                    status_code=400,
                    detail=error_message
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Instagram challenge resolution error for {request_data.username}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Challenge çözülürken hata oluştu: {str(e)}"
        )


# ============================================================================
# SOCIAL FEATURES ENDPOINTS
# ============================================================================

@app.post("/social/referral/use", tags=["Social Features"])
def use_referral_code(
    request: ReferralCodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Use a referral code to get bonus coins"""
    try:
        result = asyncio.run(social_features_manager.apply_referral_code(current_user.id, request.referrer_code))
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error using referral code: {e}")
        raise HTTPException(status_code=500, detail="Referans kodu kullanılırken hata oluştu")

@app.get("/social/referral/my-code", tags=["Social Features"])
def get_my_referral_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's referral code and statistics"""
    try:
        # Generate referral code if not exists
        result = asyncio.run(social_features_manager.generate_referral_code(current_user.id))
        if result["success"]:
            # Get referral stats
            user_social = db.query(UserSocial).filter(UserSocial.user_id == current_user.id).first()
            referrals_count = db.query(Referral).filter(Referral.referrer_id == current_user.id).count()
            
            return {
                "success": True,
                "referral_code": result["referral_code"],
                "referrals_count": referrals_count,
                "total_earnings": user_social.total_referral_earnings if user_social else 0
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting referral code: {e}")
        raise HTTPException(status_code=500, detail="Referrans kodu alınamadı")

@app.post("/social/transfer-coins", tags=["Social Features"])
async def transfer_coins(
    request: CoinTransferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer coins to another user"""
    try:
        result = await social_features_manager.transfer_coins(
            current_user.id, request.recipient_username, 
            request.amount, request.message
        )
        return result
    except Exception as e:
        logger.error(f"Error transferring coins: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/coins/transfer", tags=["Coins"])
async def transfer_coins_legacy(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transfer coins to another user (frontend compatible endpoint)"""
    try:
        # Map frontend data to internal request format
        request = CoinTransferRequest(
            recipient_username=data.get("recipient_username"),
            amount=data.get("amount"),
            message=data.get("note")  # Frontend sends 'note' but backend expects 'message'
        )
        
        result = await social_features_manager.transfer_coins(
            current_user.id, request.recipient_username, 
            request.amount, request.message
        )
        return result
    except Exception as e:
        logger.error(f"Error transferring coins: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/social/leaderboard", tags=["Social Features"])
async def get_leaderboard(
    period: str = "weekly",
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get leaderboard for specified period"""
    try:
        leaderboard = await social_features_manager.get_leaderboard(period, limit)
        return leaderboard
    except Exception as e:
        logger.error(f"Error getting leaderboard: {e}")
        raise HTTPException(status_code=500, detail="Leaderboard alınamadı")

@app.get("/social/badges", tags=["Social Features"])
async def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's badges and achievements"""
    try:
        badges = await social_features_manager.get_user_badges(current_user.id)
        return badges
    except Exception as e:
        logger.error(f"Error getting badges: {e}")
        raise HTTPException(status_code=500, detail="Rozetler alınamadı")

@app.get("/social/badges/all", tags=["Social Features"])
async def get_all_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available badges"""
    try:
        badges = await social_features_manager.get_all_badges()
        return badges
    except Exception as e:
        logger.error(f"Error getting all badges: {e}")
        raise HTTPException(status_code=500, detail="Tüm rozetler alınamadı")

@app.get("/social/stats", tags=["Social Features"])
async def get_social_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive social statistics"""
    try:
        stats = await social_features_manager.get_social_stats(current_user.id)
        return stats
    except Exception as e:
        logger.error(f"Error getting social stats: {e}")
        raise HTTPException(status_code=500, detail="Sosyal istatistikler alınamadı")

# ============================================================================
# NOTIFICATION SETTINGS ENDPOINTS
# ============================================================================

@app.get("/notifications/settings", tags=["Notifications"])
def get_notification_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's notification preferences"""
    try:
        settings = db.query(NotificationSetting).filter_by(user_id=current_user.id).first()
        if not settings:
            # Create default settings
            settings = NotificationSetting(user_id=current_user.id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return {
            "email_notifications": settings.email_enabled,
            "push_notifications": settings.push_enabled,
            "task_reminders": settings.task_notifications,
            "achievement_alerts": settings.reward_notifications,
            "social_notifications": settings.system_notifications
        }
    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        raise HTTPException(status_code=500, detail="Bildirim ayarları alınamadı")

@app.put("/notifications/settings", tags=["Notifications"])
def update_notification_settings(
    settings: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's notification preferences"""
    try:
        user_settings = db.query(NotificationSetting).filter_by(user_id=current_user.id).first()
        if not user_settings:
            user_settings = NotificationSetting(user_id=current_user.id)
            db.add(user_settings)
        
        # Update only provided fields
        if settings.email_notifications is not None:
            user_settings.email_enabled = settings.email_notifications
        if settings.push_notifications is not None:
            user_settings.push_enabled = settings.push_notifications
        if settings.task_reminders is not None:
            user_settings.task_notifications = settings.task_reminders
        if settings.achievement_alerts is not None:
            user_settings.reward_notifications = settings.achievement_alerts
        if settings.social_notifications is not None:
            user_settings.system_notifications = settings.social_notifications
        
        db.commit()
        return {"message": "Bildirim ayarları güncellendi"}
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(status_code=500, detail="Bildirim ayarları güncellenemedi")

# ============================================================================
# GDPR COMPLIANCE ENDPOINTS
# ============================================================================

@app.post("/gdpr/data-request", tags=["GDPR"])
def create_gdpr_data_request(
    request: GDPRDataRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request data export or deletion (GDPR compliance)"""
    try:
        result = gdpr_compliance_manager.create_data_request(
            db, current_user.id, request.request_type, request.reason
        )
        return result
    except Exception as e:
        logger.error(f"Error creating GDPR request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gdpr/data-requests", tags=["GDPR"])
def get_my_gdpr_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's GDPR data requests"""
    try:
        requests = db.query(GDPRRequest).filter_by(user_id=current_user.id).order_by(desc(GDPRRequest.created_at)).all()
        return [
            {
                "id": req.id,
                "request_type": req.request_type,
                "status": req.status,
                "created_at": req.created_at,
                "processed_at": req.processed_at,
                "download_url": req.download_url
            }
            for req in requests
        ]
    except Exception as e:
        logger.error(f"Error getting GDPR requests: {e}")
        raise HTTPException(status_code=500, detail="GDPR istekleri alınamadı")

@app.get("/gdpr/privacy-settings", tags=["GDPR"])
def get_privacy_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's privacy settings"""
    try:
        settings = gdpr_compliance_manager.get_privacy_settings(db, current_user.id)
        return settings
    except Exception as e:
        logger.error(f"Error getting privacy settings: {e}")
        raise HTTPException(status_code=500, detail="Gizlilik ayarları alınamadı")

# ============================================================================
# USER EDUCATION ENDPOINTS
# ============================================================================

@app.get("/education/modules", tags=["Education"])
def get_education_modules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available education modules"""
    try:
        service = UserEducationService(db)
        progress = service.get_user_education_progress(current_user.id)
        return progress
    except Exception as e:
        logger.error(f"Error getting education modules: {e}")
        raise HTTPException(status_code=500, detail="Eğitim modülleri alınamadı")

@app.get("/education/module/{module_id}", tags=["Education"])
def get_education_module(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific education module content"""
    try:
        service = UserEducationService(db)
        # Convert string to enum
        module_type = EducationModuleType(module_id)
        module = service.start_education_module(current_user.id, module_type)
        return module
    except ValueError:
        raise HTTPException(status_code=404, detail="Geçersiz modül ID")
    except Exception as e:
        logger.error(f"Error getting education module: {e}")
        raise HTTPException(status_code=404, detail="Eğitim modülü bulunamadı")

@app.post("/education/progress", tags=["Education"])
def update_education_progress(
    progress: EducationModuleProgress,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update progress on education module"""
    try:
        service = UserEducationService(db)
        module_type = EducationModuleType(progress.module_id)
        result = service.complete_education_step(
            current_user.id, module_type, progress.lesson_id
        )
        return result
    except ValueError:
        raise HTTPException(status_code=400, detail="Geçersiz modül veya ders ID")
    except Exception as e:
        logger.error(f"Error updating education progress: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/education/quiz/{module_id}", tags=["Education"])
def get_module_quiz(
    module_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz for education module"""
    try:
        service = UserEducationService(db)
        # Find quiz steps in the module
        module_type = EducationModuleType(module_id)
        if module_type in service.education_modules:
            module_info = service.education_modules[module_type]
            quiz_steps = [step for step in module_info["steps"] if step["type"] == "quiz"]
            if quiz_steps:
                return {"quiz": quiz_steps[0]}
        
        raise HTTPException(status_code=404, detail="Quiz bulunamadı")
    except ValueError:
        raise HTTPException(status_code=404, detail="Geçersiz modül ID")
    except Exception as e:
        logger.error(f"Error getting module quiz: {e}")
        raise HTTPException(status_code=404, detail="Quiz bulunamadı")

# ============================================================================
# MENTAL HEALTH & WELLNESS ENDPOINTS
# ============================================================================

@app.post("/wellness/mood-report", tags=["Mental Health"])
def report_mood(
    mood_report: MentalHealthMoodReport,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Report daily mood for wellness tracking"""
    try:
        service = MentalHealthService(db)
        result = service.record_mood(
            current_user.id, mood_report.mood_score, mood_report.notes
        )
        return result
    except Exception as e:
        logger.error(f"Error recording mood: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wellness/status", tags=["Mental Health"])
def get_wellness_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current wellness status and recommendations"""
    try:
        service = MentalHealthService(db)
        status = service.get_wellness_status(current_user.id)
        return status
    except Exception as e:
        logger.error(f"Error getting wellness status: {e}")
        raise HTTPException(status_code=500, detail="Wellness durumu alınamadı")

@app.get("/wellness/recommendations", tags=["Mental Health"])
def get_wellness_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized wellness recommendations"""
    try:
        service = MentalHealthService(db)
        recommendations = service.get_wellness_recommendations(current_user.id)
        return recommendations
    except Exception as e:
        logger.error(f"Error getting wellness recommendations: {e}")
        raise HTTPException(status_code=500, detail="Wellness önerileri alınamadı")

# ============================================================================
# COIN SECURITY & WITHDRAWAL ENDPOINTS  
# ============================================================================

@app.post("/coins/withdraw", tags=["Coin Management"])
def request_coin_withdrawal(
    withdrawal_request: CoinWithdrawalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request coin withdrawal with security checks"""
    try:
        result = coin_security_manager.create_withdrawal_request(
            db, current_user.id, withdrawal_request.amount,
            withdrawal_request.withdrawal_method, withdrawal_request.account_details
        )
        return result
    except Exception as e:
        logger.error(f"Error creating withdrawal request: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/coins/withdrawal-history", tags=["Coin Management"])
def get_withdrawal_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's withdrawal history"""
    try:
        history = db.query(CoinWithdrawalRequest).filter_by(user_id=current_user.id).order_by(desc(CoinWithdrawalRequest.created_at)).all()
        return [
            {
                "id": req.id,
                "amount": req.amount,
                "status": req.status,
                "created_at": req.created_at,
                "processed_at": req.processed_at,
                "withdrawal_method": req.withdrawal_method
            }
            for req in history
        ]
    except Exception as e:
        logger.error(f"Error getting withdrawal history: {e}")
        raise HTTPException(status_code=500, detail="Çekim geçmişi alınamadı")

@app.get("/coins/security-score", tags=["Coin Management"])
async def get_security_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's current security score"""
    try:
        result = await coin_security_manager.calculate_user_security_score(current_user.id)
        if result["success"]:
            return {
                "security_score": result["security_score"],
                "fraud_risk": result["fraud_risk"],
                "risk_level": result["risk_level"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        logger.error(f"Error calculating security score: {e}")
        raise HTTPException(status_code=500, detail="Güvenlik skoru hesaplanamadı")

# ============================================================================
# ADVANCED INSTAGRAM INTEGRATION ENDPOINTS
# ============================================================================

@app.get("/instagram/profile/{username}", tags=["Instagram"])
def get_instagram_profile(
    username: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    instagram_service: InstagramAPIService = Depends(get_instagram_service)
):
    """Get Instagram profile information"""
    try:
        if not current_user.instagram_session_data:
            raise HTTPException(status_code=403, detail="Instagram bağlantısı gerekli")
        
        profile = instagram_service.get_profile_info(current_user.instagram_session_data, username)
        return profile
    except Exception as e:
        logger.error(f"Error getting Instagram profile: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/instagram/my-posts", tags=["Instagram"])
def get_my_recent_posts(
    limit: int = 12,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    instagram_service: InstagramAPIService = Depends(get_instagram_service)
):
    """Get user's recent Instagram posts"""
    try:
        if not current_user.instagram_session_data:
            raise HTTPException(status_code=403, detail="Instagram bağlantısı gerekli")
        
        posts = instagram_service.get_recent_posts(current_user.instagram_session_data, current_user.instagram_pk, limit)
        return posts
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/admin/user/{user_id}/action", tags=["Admin"])
def admin_user_action(
    user_id: int,
    action: AdminUserAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform admin action on a user"""
    try:
        if not current_user.is_admin_platform:
            raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
        
        target_user = db.query(User).filter(User.id == user_id).first()
        if not target_user:
            raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
        
        # Process admin action
        if action.action == "ban":
            target_user.is_banned = True
        elif action.action == "unban":
            target_user.is_banned = False
        elif action.action == "make_admin":
            target_user.is_admin_platform = True
        elif action.action == "remove_admin":
            target_user.is_admin_platform = False
        else:
            raise HTTPException(status_code=400, detail="Geçersiz işlem")
        
        db.commit()
        return {"message": f"Action '{action.action}' applied to user {target_user.username}"}
    except Exception as e:
        logger.error(f"Error in admin action: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/admin/suspicious-activities", tags=["Admin"])
def get_suspicious_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of suspicious activities for admin review"""
    try:
        if not current_user.is_admin_platform:
            raise HTTPException(status_code=403, detail="Admin yetkisi gerekli")
        
        # Get users with high fraud scores
        suspicious_users = coin_security_manager.get_suspicious_users(db)
        return suspicious_users
    except Exception as e:
        logger.error(f"Error getting suspicious activities: {e}")
        raise HTTPException(status_code=500, detail="Şüpheli aktiviteler alınamadı")

@app.post("/admin/report-suspicious", tags=["Admin"])
def report_suspicious_activity(
    report: SuspiciousActivityReport,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Report suspicious activity"""
    try:
        # Log the suspicious activity report
        logger.warning(f"Suspicious activity reported by {current_user.username}: {report.activity_type} - {report.description}")
        
        # You could store this in a dedicated table for admin review
        return {"message": "Şüpheli aktivite raporu kaydedildi"}
    except Exception as e:
        logger.error(f"Error reporting suspicious activity: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Sipariş oluştur
@app.post("/create-order")
def create_order(order_data: OrderCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if the user has Instagram session data (primary requirement)
    if not current_user.instagram_session_data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Bu işlem için Instagram hesabınızın bağlı olması gerekmektedir. Lütfen profil sayfanızdan Instagram ile giriş yapın."
        )
    
    # Optional: Check instagram credentials table for additional info
    instagram_cred = db.query(InstagramCredential).filter(InstagramCredential.user_id == current_user.id).first()
    if not instagram_cred:
        # If session data exists but credential is missing, create a basic one
        try:
            instagram_cred = InstagramCredential(
                user_id=current_user.id,
                instagram_user_id=current_user.instagram_pk or "unknown",
                access_token="session_based_auth",
                username=current_user.instagram_username,
                profile_picture_url=current_user.profile_pic_url
            )
            db.add(instagram_cred)
            db.commit()
            logger.info(f"Created basic InstagramCredential for user {current_user.username} during order creation")
        except Exception as e:
            logger.warning(f"Could not create InstagramCredential for user {current_user.username}: {e}")
            # Continue anyway since session_data is the primary requirement

    if not (MIN_ORDER_TARGET_COUNT <= order_data.target_count <= MAX_ORDER_TARGET_COUNT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Hedef sayı {MIN_ORDER_TARGET_COUNT} ile {MAX_ORDER_TARGET_COUNT} arasında olmalıdır."
        )

    if order_data.order_type == OrderType.comment:
        if not order_data.comment_text:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Yorum siparişleri için 'comment_text' alanı zorunludur.")
        if not (MIN_COMMENT_LENGTH <= len(order_data.comment_text) <= MAX_COMMENT_LENGTH):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Yorum metni en az {MIN_COMMENT_LENGTH}, en fazla {MAX_COMMENT_LENGTH} karakter olabilir.")

    try:
        cl = get_instagrapi_client_for_user(current_user, db)
        media_pk = cl.media_pk_from_url(order_data.post_url)
        media_info = cl.media_info(media_pk)
        if not media_info:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Gönderi bulunamadı veya özel: {order_data.post_url}")
    except HTTPException: # Re-raise HTTPException from get_instagrapi_client_for_user or media_info check
        raise
    except Exception as e:
        logger.error(f"Gönderi URL doğrulama hatası ({order_data.post_url}) kullanıcı {current_user.username}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Gönderi URL'si doğrulanamadı: {str(e)}")
    
    total_cost = order_data.target_count * DEFAULT_COIN_COST_PER_TARGET_UNIT
    if current_user.coin_balance < total_cost:
        raise HTTPException(status_code=status.HTTP_402_FORBIDDEN, detail=f"Sipariş için yetersiz coin. Gerekli: {total_cost}, Mevcut: {current_user.coin_balance}")

    try:
        db_order = Order(
            user_id=current_user.id,
            post_url=order_data.post_url,
            order_type=order_data.order_type,
            target_count=order_data.target_count,
            status=OrderStatus.active,
            comment_text=order_data.comment_text if order_data.order_type == OrderType.comment else None
        )
        db.add(db_order)
        db.flush() # Assign an ID to db_order

        current_user.coin_balance -= total_cost
        
        coin_tx = CoinTransaction(
            user_id=current_user.id, 
            amount=-total_cost, 
            type=CoinTransactionType.spend, 
            order_id=db_order.id, 
            note=f"{order_data.order_type.value} siparişi ({db_order.id}) için {order_data.target_count} adet"
        )
        db.add(coin_tx)
        
        # Create tasks with proper fields populated
        tasks_to_create = []
        for _ in range(order_data.target_count):
            task = Task(
                order_id=db_order.id, 
                status=TaskStatus.pending,
                url=order_data.post_url,
                task_type=order_data.order_type.value,
                comment_text=order_data.comment_text if order_data.order_type == OrderType.comment else None
            )
            tasks_to_create.append(task)
        
        db.add_all(tasks_to_create)
        
        db.commit()
        # db.refresh(db_order) # Not strictly necessary as we commit, but good for having updated state if used immediately
        # db.refresh(current_user) # For coin_balance, also good practice

        logger.info(f"User {current_user.username} created order {db_order.id} ({order_data.order_type.value}) for URL {order_data.post_url}. Cost: {total_cost} coins.")
        
        # Create enhanced notification for successful order
        notification_service.create_notification_sync(
            user_id=current_user.id,
            title="Sipariş Oluşturuldu! 🎯",
            message=f"{order_data.order_type.value.title()} siparişiniz başarıyla oluşturuldu. Hedef: {order_data.target_count}",
            notification_type=NotificationType.ORDER_CREATED,
            priority=NotificationPriority.MEDIUM,
            data={"order_id": db_order.id, "target_count": order_data.target_count, "cost": total_cost}
        )
        
        return {"order_id": db_order.id, "message": "Sipariş başarıyla oluşturuldu."}
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Sipariş oluşturulurken veritabanı hatası (kullanıcı: {current_user.username}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sipariş oluşturulurken bir veritabanı hatası oluştu.")
    except Exception as e: # Catch any other unexpected error
        db.rollback()
        logger.error(f"Sipariş oluşturulurken beklenmedik genel hata (kullanıcı: {current_user.username}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Sipariş oluşturulurken beklenmedik bir hata oluştu.")

# Görev al
@app.post("/take-task")
def take_task(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        active_task_count = db.query(Task).filter_by(assigned_user_id=current_user.id, status=TaskStatus.assigned).count()
        if active_task_count > 0: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Zaten aktif bir göreviniz var. Yenisini almadan önce onu tamamlayın veya süresinin dolmasını bekleyin.")
        
        task_to_assign = db.query(Task).join(Order).filter(
            Task.status == TaskStatus.pending,
            Order.user_id != current_user.id, 
            Order.status == OrderStatus.active 
        ).with_for_update().first()

        if not task_to_assign:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Şu anda size uygun boş görev bulunmamaktadır.")
        
        task_to_assign.status = TaskStatus.assigned
        task_to_assign.assigned_user_id = current_user.id
        task_to_assign.assigned_at = datetime.utcnow()
        task_to_assign.expires_at = datetime.utcnow() + timedelta(hours=DEFAULT_TASK_EXPIRATION_HOURS)
        
        db.commit()
        
        logger.info(f"User {current_user.username} took task {task_to_assign.id} for order {task_to_assign.order_id}.")
        
        # Enhanced notification for task assignment
        notification_service.create_notification_sync(
            user_id=current_user.id,
            title="Yeni Görev Alındı! 🎯",
            message=f"Yeni göreviniz başarıyla atandı. Son teslim: {task_to_assign.expires_at.strftime('%d.%m.%Y %H:%M')}",
            notification_type=NotificationType.TASK_ASSIGNED,
            priority=NotificationPriority.HIGH,
            data={"task_id": task_to_assign.id, "order_id": task_to_assign.order_id, "expires_at": str(task_to_assign.expires_at)}
        )
        
        return {"task_id": task_to_assign.id, "order_id": task_to_assign.order_id, "expires_at": task_to_assign.expires_at}
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Görev alma sırasında veritabanı hatası (kullanıcı: {current_user.username}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Görev alınırken bir veritabanı hatası oluştu.")
    except HTTPException: # FastAPI'nin kendi hatalarını tekrar fırlat
        raise
    except Exception as e: 
        db.rollback()
        logger.error(f"Görev alma sırasında beklenmedik genel hata (kullanıcı: {current_user.username}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Görev alınırken beklenmedik bir hata oluştu.")

# Görev tamamla
@app.post("/complete-task")
def complete_task(data: TaskComplete, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter(
        Task.id == data.task_id,
        Task.assigned_user_id == current_user.id,
        Task.status == TaskStatus.assigned
    ).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Size atanmış aktif görev bulunamadı veya ID yanlış.")
    
    order = db.query(Order).filter_by(id=task.order_id).first()
    if not order:
        logger.error(f"Data integrity issue: Task {task.id} found but its Order {task.order_id} not found for user {current_user.username}.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Görevin bağlı olduğu sipariş bulunamadı. Lütfen sistem yöneticisine başvurun.")

    if order.status != OrderStatus.active:
        logger.warn(f"User {current_user.username} trying to complete task {task.id} for a non-active order {order.id} (status: {order.status}).")
        task.status = TaskStatus.failed 
        
        # Create and add ValidationLog for aborted task
        aborted_log = ValidationLog(
            task_id=task.id, 
            user_id=current_user.id, 
            validation_type=task.task_type,
            url=task.url,
            success=False,
            status="aborted_order_inactive", 
            details=f"Order {order.id} is no longer active (status: {order.status})."
        )
        db.add(aborted_log)
        try:
            db.flush() 
            task.validation_log_id = aborted_log.id
            db.commit()
        except SQLAlchemyError as e_log_commit:
            db.rollback()
            logger.error(f"Failed to commit ValidationLog for aborted task {task.id} due to order inactivity: {e_log_commit}", exc_info=True)
            # Fallback to just marking task as failed if logging fails, though this is unlikely if flush worked.
            # However, the original HTTPException should still be raised.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bu görevin ait olduğu sipariş artık aktif değil (Durum: {order.status.value}). Görev tamamlanamadı.")

    validation_status = "pending"
    validation_details = ""
    action_performed_successfully = False
    ig_client = None
    media_pk_str = None
    
    try: 
        try: 
            ig_client = get_instagrapi_client_for_user(current_user, db)
            if order.order_type == OrderType.like or order.order_type == OrderType.comment:
                media_pk = ig_client.media_pk_from_url(order.post_url)
                if not media_pk: raise ValueError("Gönderi URL'sinden media PK alınamadı.")
                media_pk_str = str(media_pk)

            if order.order_type == OrderType.like:
                if not media_pk_str: raise ValueError("Beğeni için Media PK mevcut değil.")
                if ig_client.media_like(media_pk_str): action_performed_successfully = True
            elif order.order_type == OrderType.follow:
                target_username = Client().username_from_url(order.post_url)
                if not target_username: raise ValueError("Takip için kullanıcı adı çıkarılamadı.")
                target_user_pk = ig_client.user_id_from_username(target_username)
                if not target_user_pk: raise ValueError(f"'{target_username}' PK'sı alınamadı.")
                if ig_client.user_follow(str(target_user_pk)): action_performed_successfully = True
            elif order.order_type == OrderType.comment:
                if not order.comment_text: raise ValueError("Yorum metni eksik.")
                if not media_pk_str: raise ValueError("Yorum için Media PK mevcut değil.")
                comment_result = ig_client.media_comment(media_pk_str, order.comment_text)
                if comment_result and hasattr(comment_result, 'pk') and comment_result.pk: action_performed_successfully = True
            
            if action_performed_successfully:
                validation_status = "success"
                validation_details = f"Instagram action {order.order_type.value} successful for {order.post_url}."
                logger.info(f"User {current_user.username} successfully performed {order.order_type.value} for task {task.id} on {order.post_url}.")
            else:
                validation_status = "failed"
                validation_details = f"Instagram action {order.order_type.value} for {order.post_url} returned a non-successful status or failed."
                logger.warn(f"User {current_user.username} failed Instagram action {order.order_type.value} for task {task.id} on {order.post_url}. Instagrapi call did not confirm success.")

        except HTTPException as http_exc: 
            raise http_exc 
        except Exception as e: 
            action_performed_successfully = False
            validation_status = "failed"
            validation_details = f"Error during Instagram action {order.order_type.value} for {order.post_url}: {str(e)}"
            logger.error(f"User {current_user.username} - Error during Instagram action for task {task.id} on {order.post_url}: {e}", exc_info=True)
        
        # --- Database Update Section ---
        
        validation_log = ValidationLog(
            task_id=task.id, 
            user_id=current_user.id,
            validation_type=order.order_type.value,
            url=order.post_url,
            success=action_performed_successfully,
            status=validation_status, 
            details=validation_details
        )
        db.add(validation_log)
        db.flush() 
        task.validation_log_id = validation_log.id

        if action_performed_successfully:
            task.status = TaskStatus.completed
            task.completed_at = datetime.utcnow()
            
            order.completed_count += 1
            if order.completed_count >= order.target_count:
                order.status = "completed"
                logger.info(f"Order {order.id} is now fully completed.")

            reward = DEFAULT_COIN_REWARD_PER_TASK  
            current_user.coin_balance += reward 
            
            coin_tx = CoinTransaction(
                user_id=current_user.id, 
                amount=reward, 
                type=CoinTransactionType.earn, 
                task_id=task.id, 
                note=f"Görev ({task.id}) tamamlandı: {order.order_type.value} on {order.post_url}"
            )
            db.add(coin_tx)
            db.commit() 

            # Check for level up and achievements
            completed_tasks_count = db.query(Task).filter_by(assigned_user_id=current_user.id, status=TaskStatus.completed).count()
            
            # Determine current level
            old_level = getattr(current_user, 'level', 'Bronz')
            new_level = "Bronz"
            level_bonus = 0
            
            if completed_tasks_count >= 100:
                new_level = "Platin"
                level_bonus = 500
            elif completed_tasks_count >= 50:
                new_level = "Altın"
                level_bonus = 200
            elif completed_tasks_count >= 20:
                new_level = "Gümüş"
                level_bonus = 100
            
            # Check if user leveled up
            level_milestones = {"Bronz": 0, "Gümüş": 20, "Altın": 50, "Platin": 100}
            if level_milestones.get(new_level, 0) > level_milestones.get(old_level, 0):
                # User leveled up! Award bonus coins
                current_user.coin_balance += level_bonus
                
                # Create level up transaction
                level_tx = CoinTransaction(
                    user_id=current_user.id,
                    amount=level_bonus,
                    type=CoinTransactionType.earn,
                    note=f"Seviye yükseltme bonusu: {new_level}"
                )
                db.add(level_tx)
                db.commit()
                
                # Send level up notification
                notification_service.create_notification_sync(
                    user_id=current_user.id,
                    title=f"Seviye Yükseltme! 🎖️",
                    message=f"Tebrikler! {new_level} seviyesine yükseldiniz ve {level_bonus} bonus coin kazandınız!",
                    notification_type=NotificationType.LEVEL_UP,
                    priority=NotificationPriority.HIGH,
                    data={"new_level": new_level, "bonus_coins": level_bonus, "total_balance": current_user.coin_balance}
                )
            
            # Check for achievement milestones
            if completed_tasks_count in [1, 5, 10, 25, 50, 100]:
                achievement_bonus = completed_tasks_count * 5  # 5 coins per milestone task
                current_user.coin_balance += achievement_bonus
                
                # Create achievement transaction
                achievement_tx = CoinTransaction(
                    user_id=current_user.id,
                    amount=achievement_bonus,
                    type=CoinTransactionType.earn,
                    note=f"Başarım bonusu: {completed_tasks_count} görev tamamlandı"
                )
                db.add(achievement_tx)
                db.commit()
                
                # Send achievement notification
                notification_service.create_notification_sync(
                    user_id=current_user.id,
                    title="Başarım Kazanıldı! 🏆",
                    message=f"Harika! {completed_tasks_count} görev tamladınız ve {achievement_bonus} bonus coin kazandınız!",
                    notification_type=NotificationType.ACHIEVEMENT_UNLOCKED,
                    priority=NotificationPriority.HIGH,
                    data={"milestone": completed_tasks_count, "bonus_coins": achievement_bonus}
                ) 

            # Enhanced notifications after successful commit
            logger.info(f"Task {task.id} completed successfully by user {current_user.username}. Order {order.id} progress: {order.completed_count}/{order.target_count}. Coins awarded: {reward}.")
            
            # Notify task completer about coin reward
            notification_service.create_notification_sync(
                user_id=current_user.id,
                title="Görev Tamamlandı! 🎉",
                message=f"Tebrikler! {reward} coin kazandınız. Yeni bakiye: {current_user.coin_balance}",
                notification_type=NotificationType.TASK_COMPLETED,
                priority=NotificationPriority.MEDIUM,
                data={"reward": reward, "balance": current_user.coin_balance, "task_id": task.id}
            )
            
            # Notify order owner about task completion
            order_owner = db.query(User).filter_by(id=order.user_id).first()
            if order_owner:
                notification_service.create_notification_sync(
                    user_id=order_owner.id,
                    title="Sipariş Güncellemesi 📈",
                    message=f"'{order.post_url}' siparişinizin bir görevi tamamlandı. İlerleme: {order.completed_count}/{order.target_count}",
                    notification_type=NotificationType.ORDER_UPDATE,
                    priority=NotificationPriority.LOW,
                    data={"order_id": order.id, "progress": f"{order.completed_count}/{order.target_count}"}
                )
                
                # Send completion notification if order is fully completed
                if order.status == "completed":
                    notification_service.create_notification_sync(
                        user_id=order_owner.id,
                        title="Sipariş Tamamlandı! ✅",
                        message=f"'{order.post_url}' siparişiniz tamamen tamamlandı! Hedef: {order.target_count}",
                        notification_type=NotificationType.ORDER_COMPLETED,
                        priority=NotificationPriority.HIGH,
                        data={"order_id": order.id, "target_count": order.target_count}
                    )
            
            # Check and award badges after successful task completion
            try:
                import asyncio
                # Run badge checking in background - don't wait for it to complete
                asyncio.create_task(enhanced_badge_system.check_and_award_badges(current_user.id))
            except Exception as badge_error:
                # Don't fail the task completion if badge checking fails
                logger.warning(f"Badge checking failed for user {current_user.id}: {badge_error}")
            
            return {"message": "Görev başarıyla tamamlandı ve coin kazandınız.", "coin": current_user.coin_balance, "validation_details": validation_details}
        else:
            task.status = TaskStatus.failed
            db.commit() 

            logger.warn(f"Task {task.id} for order {order.id} by user {current_user.username} failed. Reason: {validation_details}")
            notify_user_task_update(current_user.id, db) 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Instagram işlemi gerçekleştirilemedi veya başarısız oldu: {validation_details}")

    except HTTPException as http_exc: 
        db.rollback() 
        raise http_exc
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"SQLAlchemyError in complete_task (task {data.task_id}, user {current_user.username}): {str(e)}", exc_info=True)
        # Attempt to save a validation log for DB error if possible (task might not be set if initial query failed)
        # This specific logging is tricky here because validation_log might already be added or not.
        # The existing detailed logging for this case is good.
        raise HTTPException(status_code=500, detail="Görev tamamlanırken bir veritabanı hatası oluştu.")
    except Exception as e: 
        db.rollback() 
        logger.error(f"Generic unexpected error in complete_task (task {data.task_id}, user {current_user.username}): {str(e)}", exc_info=True)
        if task and task.status == TaskStatus.assigned: 
            task.status = TaskStatus.failed
            try: 
                # Try to add a validation log for this unexpected error
                if not task.validation_log_id: 
                    unexpected_val_log = ValidationLog(task_id=task.id, user_id=current_user.id, status="error_unexpected_complete", details=str(e)[:250])
                    db.add(unexpected_val_log)
                db.commit()
            except: 
                db.rollback()
        raise HTTPException(status_code=500, detail="Görev tamamlanırken genel beklenmedik bir hata oluştu.")

# Coin çekme
@app.post("/withdraw-coins")
def withdraw_coins(data: WithdrawRequest, current_user_param: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_for_withdrawal = db.query(User).filter_by(id=current_user_param.id).with_for_update().first()
    if not user_for_withdrawal: 
        logger.error(f"User ID {current_user_param.id} from token not found in DB for withdrawal, or query failed.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kullanıcı bulunamadı.")

    try:
        completed_count = db.query(Task).filter_by(assigned_user_id=user_for_withdrawal.id, status=TaskStatus.completed).count()
        if completed_count < MIN_COMPLETED_TASKS_FOR_WITHDRAWAL:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Coin çekebilmek için en az {MIN_COMPLETED_TASKS_FOR_WITHDRAWAL} görev tamamlamalısınız. Tamamlanan: {completed_count}")
        
        if user_for_withdrawal.coin_balance < data.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Yetersiz coin. Çekilmek istenen: {data.amount}, Mevcut: {user_for_withdrawal.coin_balance}")
        
        if data.amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Çekilecek coin miktarı pozitif olmalıdır.")

        user_for_withdrawal.coin_balance -= data.amount
        db.add(CoinTransaction(user_id=user_for_withdrawal.id, amount=-data.amount, type=CoinTransactionType.withdraw, note=f"Coin çekim: {data.amount}"))
        db.commit()
        
        logger.info(f"User {user_for_withdrawal.username} withdrew {data.amount} coins. New balance: {user_for_withdrawal.coin_balance}")
        notify_user_coin_update(user_for_withdrawal.id, db) 
        
        return {"message": "Coin çekildi.", "coin": user_for_withdrawal.coin_balance}
    
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Coin çekme sırasında veritabanı hatası (kullanıcı: {user_for_withdrawal.username}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Para çekme işlemi sırasında bir veritabanı hatası oluştu.")
    except Exception as e: 
        db.rollback()
        logger.error(f"Coin çekme sırasında beklenmedik genel hata (kullanıcı: {user_for_withdrawal.username}): {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Para çekme işlemi sırasında beklenmedik bir hata oluştu.")

# Aktif görev
@app.get("/tasks/active", response_model=ActiveTaskResponse | None)
def get_active_task(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(Task).filter_by(assigned_user_id=current_user.id, status=TaskStatus.assigned).first()
    if not task:
        return None

    order_info = db.query(Order.post_url, Order.order_type).filter_by(id=task.order_id).first()

    return ActiveTaskResponse(
        task_id=task.id, 
        order_id=task.order_id, 
        expires_at=task.expires_at,
        order_post_url=order_info.post_url if order_info else None,
        order_type=order_info.order_type if order_info else None
    )

# Kullanıcının siparişleri
@app.get("/orders/mine")
def get_my_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = db.query(Order).filter_by(user_id=current_user.id).all()
    return {"orders": [{"id": o.id, "post_url": o.post_url, "order_type": o.order_type.value, "target_count": o.target_count, "completed_count": o.completed_count, "status": o.status} for o in orders]}

@app.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Special case for admin user
    if current_user.username == "admin":
        logger.info("Returning admin profile data")
        return ProfileResponse(
            id=current_user.id,
            username=current_user.username,
            full_name=current_user.full_name or "System Administrator",
            profile_pic_url=None,
            coin_balance=int(current_user.coin_balance or 0),
            diamondBalance=int(current_user.coin_balance or 0),
            completed_tasks=0,
            active_tasks=0,
            is_admin_platform=True,
            followers_count=0,
            following_count=0,
            instagram_stats=None
        )

    # Calculate completed and active tasks
    completed_tasks_count = db.query(func.count(Task.id)).filter(
        Task.assigned_user_id == current_user.id,
        Task.status == TaskStatus.completed
    ).scalar() or 0

    active_tasks_count = db.query(func.count(Task.id)).filter(
        Task.assigned_user_id == current_user.id,
        Task.status == TaskStatus.assigned
    ).scalar() or 0

    # Default values
    followers_count = 0
    following_count = 0
    profile_pic_url = None
    instagram_stats_data: Optional[InstagramProfileStats] = None

    # Try to get Instagram info if available
    if current_user.instagram_username and current_user.instagram_pk:
        try:
            from modern_instagram_scraper import ModernInstagramScraper
            scraper = ModernInstagramScraper()
            scraped_data = await scraper.scrape_profile(current_user.instagram_username)
            logger.info(f"Modern scraper Instagram data for {current_user.instagram_username}: {scraped_data}")
            
            if scraped_data.get("success"):
                followers_count = scraped_data.get("followers_count", 0) or 0
                following_count = scraped_data.get("following_count", 0) or 0
                profile_pic_url = scraped_data.get("profile_pic_url")
                
                # Update user's Instagram data with fresh scraped data
                if profile_pic_url and profile_pic_url != "https://example.com/test_profile.jpg":
                    current_user.instagram_profile_pic_url = profile_pic_url
                
                # Update other Instagram data
                if scraped_data.get("posts_count"):
                    current_user.instagram_posts_count = scraped_data["posts_count"]
                if scraped_data.get("is_verified") is not None:
                    current_user.instagram_is_verified = scraped_data["is_verified"]
                if scraped_data.get("is_private") is not None:
                    current_user.instagram_is_private = scraped_data["is_private"]
                if scraped_data.get("bio"):
                    current_user.instagram_bio = scraped_data["bio"]
                    
                current_user.instagram_last_sync = datetime.utcnow()
                db.commit()
                
            else:
                followers_count = 0
                following_count = 0
                profile_pic_url = None
        except Exception as scrape_error:
            logger.warning(f"Could not scrape Instagram data for {current_user.instagram_username}: {scrape_error}")
            followers_count = 0
            following_count = 0
            profile_pic_url = None

        # Fallbacks for profile photo
        if not profile_pic_url:
            profile_pic_url = current_user.instagram_profile_pic_url
        if not profile_pic_url:
            profile_pic_url = current_user.profile_pic_url
        # Never return the broken placeholder
        if not profile_pic_url or profile_pic_url == "https://example.com/test_profile.jpg":
            profile_pic_url = None  # Use None instead of broken URL

        instagram_stats_data = InstagramProfileStats(
            instagram_user_id=current_user.instagram_pk or "0",
            username=current_user.instagram_username or current_user.username,
            full_name=current_user.full_name or current_user.username,
            profile_pic_url=profile_pic_url,
            media_count=current_user.instagram_posts_count or 0,
            is_private=current_user.instagram_is_private or False,
            is_verified=current_user.instagram_is_verified or False
        )

    elif hasattr(current_user, 'instagram_credential') and current_user.instagram_credential and current_user.instagram_credential.instagram_user_id:
        cred = current_user.instagram_credential
        followers_count = cred.followers_count or 0 if hasattr(cred, "followers_count") else 0
        following_count = cred.following_count or 0 if hasattr(cred, "following_count") else 0
        profile_pic_url = cred.profile_picture_url or current_user.profile_pic_url
        if not profile_pic_url or profile_pic_url == "https://example.com/test_profile.jpg":
            profile_pic_url = None
        instagram_stats_data = InstagramProfileStats(
            instagram_user_id=cred.instagram_user_id,
            username=cred.username or current_user.username,
            full_name=current_user.full_name or current_user.username,
            profile_pic_url=profile_pic_url,
            media_count=0,
            is_private=False,
            is_verified=False
        )
    else:
        # No Instagram info, fallback to user profile_pic_url or default
        profile_pic_url = current_user.profile_pic_url
        if not profile_pic_url or profile_pic_url == "https://example.com/test_profile.jpg":
            profile_pic_url = None

    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name or "",
        profile_pic_url=profile_pic_url,
        coin_balance=int(current_user.coin_balance or 0),
        diamondBalance=int(current_user.coin_balance or 0),
        completed_tasks=int(completed_tasks_count or 0),
        active_tasks=int(active_tasks_count or 0),
        is_admin_platform=bool(current_user.is_admin_platform or False),
        followers_count=int(followers_count or 0),
        following_count=int(following_count or 0),
        instagram_stats=instagram_stats_data
    )
# User-specific endpoints for frontend compatibility
@app.get("/user/instagram-profile", tags=["User"])
async def get_user_instagram_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's Instagram profile information"""
    try:
        if not current_user.instagram_username:
            # Return empty profile instead of 404 for better frontend handling
            return {
                "success": False,
                "instagram_user_id": "0",
                "username": "",
                "full_name": current_user.full_name or current_user.username,
                "profile_pic_url": current_user.profile_pic_url or "",
                "followers_count": 0,
                "following_count": 0,
                "media_count": 0,
                "is_private": False,
                "is_verified": False,
                "message": "Instagram profili bağlı değil"
            }
        
        # Use existing Instagram scraping logic from profile endpoint
        from modern_instagram_scraper import ModernInstagramScraper
        scraper = ModernInstagramScraper()
        scraped_data = await scraper.scrape_profile(current_user.instagram_username)
        
        if scraped_data.get("success"):
            return {
                "success": True,
                "instagram_user_id": current_user.instagram_pk or "0",
                "username": current_user.instagram_username,
                "full_name": current_user.full_name or current_user.username,
                "profile_pic_url": scraped_data.get("profile_pic_url") or "",
                "followers_count": int(scraped_data.get("followers_count", 0) or 0),
                "following_count": int(scraped_data.get("following_count", 0) or 0),
                "media_count": int(scraped_data.get("posts_count", 0) or 0),
                "is_private": bool(scraped_data.get("is_private", False)),
                "is_verified": bool(scraped_data.get("is_verified", False))
            }
        else:
            # Fallback to stored data
            return {
                "success": True,
                "instagram_user_id": current_user.instagram_pk or "0",
                "username": current_user.instagram_username,
                "full_name": current_user.full_name or current_user.username,
                "profile_pic_url": current_user.profile_pic_url or "",
                "followers_count": int(current_user.instagram_followers_count or 0),
                "following_count": int(current_user.instagram_following_count or 0),
                "media_count": int(current_user.instagram_posts_count or 0),
                "is_private": bool(current_user.instagram_is_private or False),
                "is_verified": bool(current_user.instagram_is_verified or False)
            }
    except Exception as e:
        logger.error(f"Error getting user Instagram profile: {e}")
        # Return structured response instead of raising exception
        return {
            "success": False,
            "instagram_user_id": "0", 
            "username": "",
            "full_name": current_user.full_name or current_user.username,
            "profile_pic_url": current_user.profile_pic_url or "",
            "followers_count": 0,
            "following_count": 0,
            "media_count": 0,
            "is_private": False,
            "is_verified": False,
            "message": "Instagram profil bilgileri alınamadı"
        }

@app.get("/user/badges", tags=["User"])
async def get_user_badges_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's badges and achievements - wrapper for frontend compatibility"""
    try:
        badges = await social_features_manager.get_user_badges(current_user.id)
        return badges
    except Exception as e:
        logger.error(f"Error getting user badges: {e}")
        raise HTTPException(status_code=500, detail="Rozetler alınamadı")
    

@app.get("/tasks", response_model=List[TaskSchema], tags=["Tasks"])
def get_tasks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Base query
    query = db.query(
        Task.id,
        Task.order_id,
        Order.order_type,
        Order.post_url,  # Corrected from target_url previously
        Task.status,
        Task.assigned_at,
        Task.completed_at,
        Task.expires_at
    ) # Ensure this parenthesis is correctly placed and closes the db.query arguments

    # Join with Order table
    query = query.join(Order, Task.order_id == Order.id)

    # Filter by current user and relevant task statuses
    query = query.filter(Task.assigned_user_id == current_user.id)
    query = query.filter(Task.status == TaskStatus.assigned) 

    # Order by when the task was assigned
    query = query.order_by(desc(Task.assigned_at))

    # Execute the query
    user_tasks_query_results = query.all()

    tasks_response = []
    for task_data in user_tasks_query_results:
        tasks_response.append(TaskSchema(
            id=task_data[0],
            order_id=task_data[1],
            service_type=task_data[2].value if hasattr(task_data[2], 'value') else str(task_data[2]),
            target_url=task_data[3],
            status=task_data[4].value if hasattr(task_data[4], 'value') else str(task_data[4]),
            assigned_at=task_data[5],
            completed_at=task_data[6],
            expires_at=task_data[7]
        ))
    
    return tasks_response

# Bildirimler
class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    created_at: datetime

@app.get("/notifications", response_model=list[NotificationResponse])
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter_by(user_id=current_user.id).order_by(desc(Notification.created_at)).all()
    return [NotificationResponse(id=n.id, message=n.message, is_read=n.read, created_at=n.created_at) for n in notifs]

@app.post("/notifications/read/{notif_id}")
def mark_notification_read(notif_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter_by(id=notif_id, user_id=current_user.id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Bildirim bulunamadı.")
    notif.read = True
    db.commit()
    return {"message": "Bildirim okundu."}

# Admin yetkilendirme
def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Yönetici yetkisi gerekli.")
    return current_user

# Admin paneli endpointleri
@app.get("/admin/users")
def admin_list_users(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "full_name": u.full_name, "is_admin": u.is_admin, "coin": u.coin_balance} for u in users]

@app.get("/admin/orders")
def admin_list_orders(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return [{"id": o.id, "user_id": o.user_id, "post_url": o.post_url, "order_type": o.order_type.value, "target_count": o.target_count, "completed_count": o.completed_count, "status": o.status} for o in orders]

@app.get("/admin/tasks")
def admin_list_tasks(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return [{"id": t.id, "order_id": t.order_id, "assigned_user_id": t.assigned_user_id, "status": t.status.value, "assigned_at": t.assigned_at, "completed_at": t.completed_at} for t in tasks]

@app.get("/admin/coin-transactions")
def admin_list_coin_transactions(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    txs = db.query(CoinTransaction).all()
    return [{"id": tx.id, "user_id": tx.user_id, "amount": tx.amount, "type": tx.type.value, "created_at": tx.created_at, "note": tx.note} for tx in txs]

# İstatistikler
@app.get("/stats/user")
def user_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    completed_tasks = db.query(Task).filter_by(assigned_user_id=current_user.id, status=TaskStatus.completed).count()
    total_coins_earned = db.query(CoinTransaction).filter_by(user_id=current_user.id, type=CoinTransactionType.earn).with_entities(func.sum(CoinTransaction.amount)).scalar() or 0
    total_withdrawn = db.query(CoinTransaction).filter_by(user_id=current_user.id, type=CoinTransactionType.withdraw).with_entities(func.sum(CoinTransaction.amount)).scalar() or 0
    return {
        "completed_tasks": completed_tasks,
        "total_coins_earned": total_coins_earned,
        "total_withdrawn": abs(total_withdrawn)
    }

@app.get("/stats/system")
def system_stats(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_tasks = db.query(Task).count()
    total_completed_tasks = db.query(Task).filter_by(status=TaskStatus.completed).count()
    total_coins = db.query(CoinTransaction).with_entities(func.sum(CoinTransaction.amount)).scalar() or 0
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_tasks": total_tasks,
        "total_completed_tasks": total_completed_tasks,
        "total_coins": total_coins
    }

# Import enhanced notification system
from enhanced_notifications import (
    notification_manager, NotificationService, NotificationStats,
    NotificationType, NotificationPriority, cleanup_old_notifications
)

# Initialize enhanced notification service
notification_service = NotificationService(db_session_factory=SessionLocal)

# Legacy websockets for backward compatibility
active_websockets: Dict[int, WebSocket] = {}

@app.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    user = None 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user = db.query(User).filter_by(username=username).first()
        if not user:
            await websocket.close()
            return
        
        # Use enhanced notification manager
        await notification_manager.connect(websocket, user.id)
        
        # Keep legacy support
        active_websockets[user.id] = websocket
        
        # Send welcome message with current stats
        notification_service = NotificationService(db)
        await notification_service.create_notification(
            user_id=user.id,
            title="Gerçek Zamanlı Bildirimler Aktif! 🔔",
            message="Artık tüm güncellemeleri anında alacaksınız.",
            notification_type=NotificationType.SYSTEM_UPDATE,
            priority=NotificationPriority.LOW,
            send_push=False,
            send_realtime=True
        )
        
        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed
            logger.info(f"Received message from user {user.id}: {data}")
            
    except WebSocketDisconnect:
        if user:
            notification_manager.disconnect(user.id)
            if user.id in active_websockets:
                del active_websockets[user.id]

# Bildirim gönderme fonksiyonu (örnek)
def send_notification(user_id: int, message: str, db: Session):
    notif = Notification(user_id=user_id, message=message)
    db.add(notif)
    db.commit()
    db.refresh(notif) 
    ws = active_websockets.get(user_id)
    if ws:
        import asyncio
        asyncio.create_task(ws.send_json({"type": "new_notification", "id": notif.id, "message": message, "is_read": notif.is_read, "created_at": str(notif.created_at)}))

@app.post("/admin/ban-user/{user_id}")
def admin_ban_user(user_id: int, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    user.is_active = False
    db.commit()
    send_notification(user_id, "Hesabınız admin tarafından banlandı.", db)
    return {"message": "Kullanıcı banlandı."}

@app.post("/admin/coin-adjust/{user_id}")
def admin_coin_adjust(user_id: int, amount: int, note: str = "Admin işlemi", admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
    user.coin_balance += amount
    db.add(CoinTransaction(user_id=user_id, amount=amount, type=CoinTransactionType.earn if amount > 0 else CoinTransactionType.withdraw, note=note))
    db.commit()
    send_notification(user_id, f"Admin tarafından {amount} coin {(amount > 0 and 'eklendi' or 'çıkarıldı')}.", db)
    return {"message": f"Kullanıcıya {amount} coin {(amount > 0 and 'eklendi' or 'çıkarıldı')}."}

@app.post("/fcm/register")
def register_fcm_token(token: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(UserFCMToken).filter_by(token=token).first()
    if not existing:
        db.add(UserFCMToken(user_id=current_user.id, token=token))
        db.commit()
    return {"message": "FCM token kaydedildi."}

@app.post("/admin/send-push")
def admin_send_push(user_id: int, title: str, body: str, admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    tokens = [t.token for t in db.query(UserFCMToken).filter_by(user_id=user_id).all()]
    if not tokens:
        raise HTTPException(status_code=404, detail="Kullanıcıya ait FCM token yok.")
    
    if not firebase_admin._apps: 
        logger.error("Firebase Admin SDK not initialized. Cannot send push notification.")
        raise HTTPException(status_code=500, detail="Push bildirim servisi konfigüre edilmemiş.")

    messages_to_send = []
    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )
        messages_to_send.append(message)
    
    if not messages_to_send:
        return {"message": "Gönderilecek geçerli token bulunamadı."}

    try:
        batch_response = messaging.send_all(messages_to_send)
        logger.info(f"FCM send_all response: SuccessCount: {batch_response.success_count}, FailureCount: {batch_response.failure_count}")
        
        if batch_response.failure_count > 0:
            for i, response in enumerate(batch_response.responses):
                if not response.success:
                    original_token = tokens[i] 
                    logger.error(f"Failed to send FCM to token {original_token}: {response.exception}")
                    if isinstance(response.exception, (messaging.UnregisteredError, messaging.InvalidRegistrationTokenError)):
                        logger.info(f"Token {original_token} seems invalid. Consider removing it from UserFCMToken.")
                        # db.query(UserFCMToken).filter_by(token=original_token).delete()
                        # db.commit() 
        
        return {"message": f"Push notification(s) sent. Success: {batch_response.success_count}, Failed: {batch_response.failure_count}"}
    except firebase_admin.exceptions.FirebaseError as e:
        logger.error(f"FirebaseError sending push notification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Push bildirimi gönderilirken Firebase hatası: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error sending push notification: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Push bildirimi gönderilirken beklenmedik bir hata oluştu: {str(e)}")

def notify_user_task_update(user_id: int, db: Session):
    ws = active_websockets.get(user_id)
    if ws:
        active_task_db = db.query(Task).filter(Task.assigned_user_id == user_id, Task.status == TaskStatus.assigned).first()
        
        active_task_payload = None
        if active_task_db:
            order_info = db.query(Order).filter_by(id=active_task_db.order_id).first()
            active_task_payload = {
                "task_id": active_task_db.id, 
                "order_id": active_task_db.order_id,
                "order_post_url": order_info.post_url if order_info else None,
                "order_type": order_info.order_type.value if order_info else None,
                "status": active_task_db.status.value, 
                "assigned_at": str(active_task_db.assigned_at) if active_task_db.assigned_at else None,
                "expires_at": str(active_task_db.expires_at) if active_task_db.expires_at else None
            }

        completed_tasks_count = db.query(Task).filter(Task.assigned_user_id == user_id, Task.status == TaskStatus.completed).count()

        import asyncio
        asyncio.create_task(ws.send_json({
            "type": "task_update",
            "active_task": active_task_payload,
            "completed_tasks_count": completed_tasks_count
        }))

def notify_user_coin_update(user_id: int, db: Session):
    ws = active_websockets.get(user_id)
    if ws:
        from .models import User 
        user = db.query(User).filter_by(id=user_id).first()
        import asyncio
        asyncio.create_task(ws.send_json({
            "type": "coin_update",
            "coin": user.coin_balance
        }))

# Helper function to get a logged-in Instagrapi client for a user
def get_instagrapi_client_for_user(user: User, db: Session) -> Client:
    # Bypass Instagram session validation for test users
    if user.username == "testuser" or user.instagram_pk == "12345678901":
        logger.info(f"Bypassing Instagram session validation for test user: {user.username}")
        # Create a mock client for test users - don't actually connect to Instagram
        cl = Client()
        # Set minimal mock settings to avoid session validation
        mock_settings = {
            "uuids": {"phone_id": "test-phone-id", "uuid": "test-uuid", "client_session_id": "test-session"},
            "cookies": {},
            "last_login": time.time(),
            "device_settings": {"device_id": "test-device"},
            "user_agent": "Instagram Test Agent"
        }
        cl.set_settings(mock_settings)
        logger.info(f"Mock Instagram client created for test user {user.username}")
        return cl
    
    # Check if user has Instagram session data
    if not user.instagram_session_data:
        logger.warn(f"User {user.username} (ID: {user.id}) has no saved Instagram session data.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Instagram oturumunuz geçersiz veya süresi dolmuş. Lütfen tekrar Instagram ile giriş yapın.")
    
    # Create new client instance to avoid LateInitializationError
    try:
        cl = Client()
        logger.debug(f"Attempting to load Instagram session for user {user.username} (ID: {user.id}).")
        
        # Parse session data
        settings_json = user.instagram_session_data
        settings = json.loads(settings_json)
        
        # Validate and fix session structure
        if not isinstance(settings, dict):
            logger.error(f"Invalid session data format for user {user.username}")
            raise ValueError("Invalid session data format")
            
        # Ensure all required keys exist with proper defaults
        required_keys = ['uuids', 'cookies', 'device_settings', 'user_agent', 'last_login']
        for key in required_keys:
            if key not in settings:
                if key == 'uuids':
                    settings[key] = {
                        "phone_id": cl.generate_uuid(),
                        "uuid": cl.generate_uuid(),
                        "client_session_id": cl.generate_uuid(),
                        "advertising_id": cl.generate_uuid(),
                        "device_id": f"android-{cl.generate_uuid()}"
                    }
                elif key == 'cookies':
                    settings[key] = {}
                elif key == 'device_settings':
                    settings[key] = {
                        "app_version": "269.0.0.18.75",
                        "android_version": 29,
                        "android_release": "10",
                        "dpi": "480dpi",
                        "resolution": "1080x2340",
                        "manufacturer": "OnePlus",
                        "device": "OnePlus6T",
                        "model": "ONEPLUS A6013",
                        "cpu": "qcom",
                        "version_code": "314665256"
                    }
                elif key == 'user_agent':
                    settings[key] = cl.user_agent
                elif key == 'last_login':
                    settings[key] = time.time()
                    
                logger.info(f"Added missing session key '{key}' for user {user.username}")
        
        # Set the settings on the client
        cl.set_settings(settings)
        
        # Skip session validation for recently logged in users (within last hour)
        # This helps avoid the LateInitializationError and session conflicts
        if user.instagram_connected_at and user.instagram_connected_at > datetime.utcnow() - timedelta(hours=1):
            logger.info(f"Skipping session validation for recently logged in user {user.username}")
            return cl
        
        # For older sessions, do a lightweight validation
        try:
            # Use a simpler validation method that's less likely to cause conflicts
            user_id = cl.user_id
            if user_id and str(user_id) == str(user.instagram_pk):
                logger.info(f"Instagram session validated via user_id for user {user.username}")
                return cl
            else:
                logger.warn(f"Session user_id mismatch for user {user.username}. Expected: {user.instagram_pk}, Got: {user_id}")
                raise LoginRequired("Session user mismatch")
                
        except (LoginRequired, ClientError, AttributeError) as e:
            logger.warn(f"Instagram session validation failed for user {user.username}: {e}")
            # Clear invalid session data
            user.instagram_session_data = None
            user.instagram_pk = None
            user.instagram_username = None
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Instagram oturumunuz geçersiz veya süresi dolmuş. Lütfen tekrar Instagram ile giriş yapın."
            )
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode Instagram session JSON for user {user.username}: {e}")
        user.instagram_session_data = None
        user.instagram_pk = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Instagram oturum verisi bozuk. Lütfen tekrar giriş yapın.")
    except Exception as e:
        logger.error(f"Unexpected error loading Instagram session for user {user.username}: {e}")
        # Don't clear session data for unexpected errors, just return error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Instagram oturumu yüklenirken bir hata oluştu.")
    
    return cl

# Arka plan görevi için fonksiyon
def process_expired_tasks_logic(db: Session):
    try:
        expired_tasks_query = db.query(Task).join(Order).filter( 
            Task.status == TaskStatus.assigned,
            Task.expires_at < datetime.utcnow()
        )
        expired_tasks = expired_tasks_query.all()

        if not expired_tasks:
            logger.info("No expired tasks to process.")
            return

        users_to_notify = {} 
        tasks_processed_count = 0

        for task in expired_tasks:
            previous_user_id = task.assigned_user_id
            original_order_id = task.order_id
            
            logger.info(f"Processing expired task ID {task.id} for order {original_order_id}, previously assigned to user ID: {previous_user_id}")
            
            task.status = TaskStatus.pending 
            task.assigned_user_id = None
            task.assigned_at = None
            task.expires_at = None 

            validation_log = ValidationLog(
                user_id=previous_user_id,
                task_id=task.id,
                validation_type=task.task_type,
                url=task.url,
                success=False,
                details="Görev süresi doldu, otomatik olarak havuza geri alındı.",
                created_at=datetime.utcnow()
            )
            db.add(validation_log)
            try:
                db.flush() 
                if validation_log.id:
                    task.validation_log_id = validation_log.id
                else: 
                    logger.warning(f"Could not obtain validation_log.id for expired task {task.id} after flush.")
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemyError during flush or assigning validation_log_id for expired task {task.id}: {e}", exc_info=True)
            
            tasks_processed_count +=1

            if previous_user_id:
                message = f"ID: {task.id} (Sipariş: {original_order_id}) olan görevinizin süresi doldu ve görev havuzuna geri alındı."
                if previous_user_id not in users_to_notify:
                    users_to_notify[previous_user_id] = []
                users_to_notify[previous_user_id].append(message)
        
        if tasks_processed_count > 0:
            db.commit()
            logger.info(f"Successfully processed and committed {tasks_processed_count} expired tasks.")
            
            for user_id, messages in users_to_notify.items():
                for msg_content in messages:
                    send_notification(user_id, msg_content, db) 
                notify_user_task_update(user_id, db) 
        else:
            logger.info("No tasks were effectively changed to require a commit in this run of process_expired_tasks_logic.")

    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"SQLAlchemyError during task expiration processing: {str(e)}", exc_info=True)
    except Exception as e:
        db.rollback() 
        logger.error(f"An unexpected error occurred during task expiration processing: {str(e)}", exc_info=True)

@app.post("/tasks/process-expirations", status_code=status.HTTP_202_ACCEPTED)
async def trigger_process_expired_tasks(background_tasks: BackgroundTasks, admin: User = Depends(get_admin_user)):
    def run_with_db_session():
        db = SessionLocal()
        try:
            process_expired_tasks_logic(db)
        finally:
            db.close()
            
    background_tasks.add_task(run_with_db_session)
    return {"message": "Süresi dolmuş görevleri işleme süreci arka planda başlatıldı."}

# Enhanced Notification System Endpoints
@app.post("/admin/cleanup-notifications")
def trigger_notification_cleanup(background_tasks: BackgroundTasks, admin: User = Depends(get_admin_user)):
    """Admin endpoint to trigger notification cleanup"""
    def run_cleanup():
        try:
            cleanup_old_notifications()
            logger.info("Notification cleanup completed successfully")
        except Exception as e:
            logger.error(f"Notification cleanup failed: {e}")
    
    background_tasks.add_task(run_cleanup)
    return {"message": "Notification cleanup process started in background."}

@app.get("/notification-stats")
def get_notification_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get notification statistics for current user"""
    stats = notification_service.get_user_stats(current_user.id)
    return {
        "total_notifications": stats["total_notifications"],
        "unread_count": stats["unread_count"],
        "last_notification": stats["last_notification_time"].isoformat() if stats["last_notification_time"] else None,
        "notification_types": stats["notification_types"]
    }

# Daily Reward System
@app.get("/daily-reward-status")
async def get_daily_reward_status_enhanced(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get daily reward status for current user using DailyReward table"""
    try:
        from sqlalchemy import func
        today = datetime.utcnow().date()

        # Check if already claimed today
        today_reward = db.query(DailyReward).filter(
            DailyReward.user_id == current_user.id,
            func.date(DailyReward.claimed_date) == today.isoformat()
        ).first()
        can_claim = today_reward is None

        # Get latest reward for streak calculation
        latest_reward = db.query(DailyReward).filter(
            DailyReward.user_id == current_user.id
        ).order_by(desc(DailyReward.claimed_date)).first()

        current_streak = 0
        if latest_reward:
            latest_date = latest_reward.claimed_date
            if isinstance(latest_date, str):
                latest_date = datetime.strptime(latest_date.split()[0], '%Y-%m-%d').date()
            elif isinstance(latest_date, datetime):
                latest_date = latest_date.date()
            if latest_date == today:
                current_streak = latest_reward.consecutive_days
            elif latest_date == today - timedelta(days=1):
                current_streak = latest_reward.consecutive_days

        # Calculate next reward amount
        next_consecutive_days = current_streak + 1 if can_claim else current_streak
        base_reward = 50
        bonus_multiplier = min(next_consecutive_days, 7)
        next_reward = base_reward + (bonus_multiplier * 10)
        if next_consecutive_days == 7:
            next_reward += 200  # Weekly bonus

        return {
            "can_claim": can_claim,
            "streak": current_streak or 0,
            "next_reward": next_reward or 0,
            "last_claim": latest_reward.claimed_date.isoformat() if latest_reward else None,
            "current_balance": current_user.coin_balance or 0
        }

    except Exception as e:
        logger.error(f"Daily reward status error: {e}")
        raise HTTPException(status_code=500, detail="Günlük ödül durumu alınamadı")

@app.post("/claim-daily-reward")
async def claim_daily_reward_enhanced(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Enhanced daily reward claiming with proper streak calculation and DailyReward table usage"""
    try:
        today = datetime.utcnow().date()
        from sqlalchemy import func
        existing_reward = db.query(DailyReward).filter(
            DailyReward.user_id == current_user.id,
            func.date(DailyReward.claimed_date) == today.isoformat()
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
            func.date(DailyReward.claimed_date) == yesterday.isoformat()
        ).first()
        consecutive_days = (yesterday_reward.consecutive_days + 1) if yesterday_reward else 1

        base_reward = 50
        bonus_multiplier = min(consecutive_days, 7)
        total_reward = base_reward + (bonus_multiplier * 10)
        if consecutive_days == 7:
            total_reward += 200

        # Create reward record
        daily_reward = DailyReward(
            user_id=current_user.id,
            coin_amount=total_reward,
            consecutive_days=consecutive_days,
            claimed_date=today
        )
        db.add(daily_reward)

        # Update user balance and streak
        current_user.coin_balance = (current_user.coin_balance or 0) + total_reward
        current_user.daily_reward_streak = consecutive_days
        current_user.last_daily_reward = datetime.utcnow()

        # Create transaction record
        transaction = CoinTransaction(
            user_id=current_user.id,
            amount=total_reward,
            type=CoinTransactionType.earn,
            note=f"Günlük ödül - {consecutive_days}. gün (Bonus: {bonus_multiplier}x)"
        )
        db.add(transaction)
        db.commit()

        # Notification
        try:
            from enhanced_notifications import notification_service, NotificationType
            await notification_service.create_notification(
                user_id=current_user.id,
                title="Günlük Ödül Alındı! 💎",
                message=f"{total_reward} coin kazandınız! Seri: {consecutive_days} gün",
                notification_type=NotificationType.DAILY_LOGIN,
            )
        except Exception as e:
            logger.error(f"Failed to send daily reward notification: {e}")

        # Badge check
        try:
            import asyncio
            asyncio.create_task(enhanced_badge_system.check_and_award_badges(current_user.id))
        except Exception as badge_error:
            logger.warning(f"Badge checking failed for user {current_user.id} after daily reward: {badge_error}")

        return {
            "success": True,
            "message": f"Günlük ödül alındı! +{total_reward} coin",
            "coins_earned": total_reward,
            "total_balance": current_user.coin_balance or 0,
            "streak": consecutive_days or 0,
            "consecutive_days": consecutive_days or 0,
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

# Coins endpoint - Enhanced with Diamond compatibility
@app.get("/coins", tags=["Diamond System"])
def get_user_coins(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's current coin/diamond balance and recent transactions - Frontend compatible"""
    try:
        # Get recent coin transactions
        recent_transactions = db.query(CoinTransaction).filter(
            CoinTransaction.user_id == current_user.id
        ).order_by(CoinTransaction.created_at.desc()).limit(10).all()
        
        transactions_list = []
        for tx in recent_transactions:
            transactions_list.append({
                "id": tx.id,
                "amount": tx.amount,
                "type": tx.type.value,
                "note": tx.note,
                "created_at": tx.created_at.isoformat()
            })
        
        # Calculate totals
        total_earned = db.query(func.sum(CoinTransaction.amount)).filter(
            CoinTransaction.user_id == current_user.id,
            CoinTransaction.type == CoinTransactionType.earn
        ).scalar() or 0
        
        total_spent = db.query(func.sum(CoinTransaction.amount)).filter(
            CoinTransaction.user_id == current_user.id,
            CoinTransaction.type == CoinTransactionType.spend
        ).scalar() or 0
        
        # Return both coin and diamond compatible response
        balance = int(current_user.coin_balance or 0)
        
        return {
            "success": True,
            # Legacy coin fields (backward compatibility)
            "current_balance": balance,
            "recent_transactions": transactions_list,
            "total_earned": int(total_earned or 0),
            "total_spent": int(abs(total_spent or 0)),
            # Diamond frontend compatibility fields
            "diamondBalance": balance,
            "diamond_balance": balance,
            "diamond_transactions": transactions_list,
            "diamonds_earned": int(total_earned or 0),
            "diamonds_spent": int(abs(total_spent or 0)),
            # System info
            "currency_name": "diamond",
            "currency_symbol": "💎"
        }
    except Exception as e:
        logger.error(f"Error getting coins for user {current_user.id}: {e}")
        raise HTTPException(status_code=500, detail=f"Diamond bilgileri alınamadı: {str(e)}")

# Email Verification
@app.post("/send-verification-email")
async def send_verification_email(email: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import random
    import string
    
    # Generate 6-digit verification code
    verification_code = ''.join(random.choices(string.digits, k=6))
    expires_at = datetime.now() + timedelta(minutes=15)
    
    # Delete old verification codes
    db.query(EmailVerification).filter(EmailVerification.user_id == current_user.id).delete()
    
    # Create new verification record
    email_verification = EmailVerification(
        user_id=current_user.id,
        verification_code=verification_code,
        expires_at=expires_at
    )
    db.add(email_verification)
    
    # Update user email
    current_user.email = email
    
    db.commit()
    
    # Enhanced notification sent via notification service
    try:
        await notification_service.create_notification(
            user_id=current_user.id,
            title="E-posta Doğrulama Kodu 📧",
            message=f"Doğrulama kodunuz: {verification_code}",
            notification_type=NotificationType.EMAIL_VERIFICATION,
            priority=NotificationPriority.HIGH
        )
    except Exception as e:
        logger.warning(f"Failed to send email verification notification: {e}")
    
    logger.info(f"Email verification code for user {current_user.username}: {verification_code}")
    
    return {
        "success": True,
        "message": "Doğrulama kodu e-posta adresinize gönderildi.",
        "expires_in_minutes": 15
    }

@app.post("/verify-email")
def verify_email(verification_code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Find verification record
    verification = db.query(EmailVerification).filter(
        EmailVerification.user_id == current_user.id,
        EmailVerification.verification_code == verification_code,
        EmailVerification.expires_at > datetime.now(),
        EmailVerification.verified == False
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz veya süresi dolmuş doğrulama kodu."
        )
    
    # Mark as verified
    verification.verified = True
    current_user.email_verified = True
    
    # Give bonus coins for email verification
    bonus_coins = 100
    current_user.coin_balance += bonus_coins
    
    coin_transaction = CoinTransaction(
        user_id=current_user.id,
        amount=bonus_coins,
        type=CoinTransactionType.earn,
        note="E-posta doğrulama bonusu"
    )
    db.add(coin_transaction)
    
    db.commit()
    
    return {
        "success": True,
        "message": "E-posta adresiniz başarıyla doğrulandı!",
        "bonus_coins": bonus_coins,
        "new_balance": current_user.coin_balance
    }

# Two-Factor Authentication Endpoints
import pyotp
import qrcode
import io
import base64
import secrets

class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: List[str]

class TwoFactorVerifyRequest(BaseModel):
    token: str

@app.post("/setup-2fa", response_model=TwoFactorSetupResponse)
def setup_2fa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA zaten etkinleştirilmiş."
        )
    
    # Generate secret key
    secret = pyotp.random_base32()
    
    # Generate QR code
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user.username,
        issuer_name="Instagram Puan App"
    )
    
    # Create QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Convert to base64
    qr_code_b64 = base64.b64encode(img_buffer.getvalue()).decode()
    qr_code_data_url = f"data:image/png;base64,{qr_code_b64}"
    
    # Generate backup codes
    backup_codes = [str(secrets.randbelow(10**8)).zfill(8) for _ in range(10)]
    
    # Store temporarily (will be confirmed after verification)
    current_user.two_factor_secret = secret
    db.commit()
    
    return TwoFactorSetupResponse(
        secret=secret,
        qr_code=qr_code_data_url,
        backup_codes=backup_codes
    )

@app.post("/verify-2fa-setup")
def verify_2fa_setup(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA zaten etkinleştirilmiş."
        )
    
    if not current_user.two_factor_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA kurulumu başlatılmamış."
        )
    
    # Verify token
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz doğrulama kodu."
        )
    
    # Enable 2FA
    current_user.two_factor_enabled = True
    
    # Give bonus coins for enabling 2FA
    bonus_coins = 200
    current_user.coin_balance += bonus_coins
    
    coin_transaction = CoinTransaction(
        user_id=current_user.id,
        amount=bonus_coins,
        type=CoinTransactionType.earn,
        note="2FA etkinleştirme bonusu"
    )
    db.add(coin_transaction)
    
    db.commit()
    
    return {
        "success": True,
        "message": "2FA başarıyla etkinleştirildi!",
        "bonus_coins": bonus_coins,
        "new_balance": current_user.coin_balance
    }

@app.post("/disable-2fa")
def disable_2fa(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA etkinleştirilmemiş."
        )
    
    # Verify token
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if not totp.verify(request.token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz doğrulama kodu."
        )
    
    # Disable 2FA
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    
    db.commit()
    
    return {
        "success": True,
        "message": "2FA başarıyla devre dışı bırakıldı."
    }

# Statistics and Notifications Endpoints
from models import Notification, UserStatistics
import json

@app.get("/statistics")
def get_user_statistics(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user statistics for the statistics screen - REAL DATA ONLY"""
    try:
        # Get or create user statistics - force recalculation for real data
        stats = db.query(UserStatistics).filter(UserStatistics.user_id == current_user.id).first()
        
        # Always recalculate real values from existing data
        completed_tasks = db.query(Task).filter(
            Task.assigned_user_id == current_user.id,
            Task.status == TaskStatus.completed
        ).count()
        
        active_tasks = db.query(Task).filter(
            Task.assigned_user_id == current_user.id,
            Task.status == TaskStatus.assigned
        ).count()
        
        # Generate REAL weekly earnings data (last 7 days)
        weekly_data = []
        from datetime import timedelta
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=6-i)
            daily_earnings = db.query(func.sum(CoinTransaction.amount)).filter(
                CoinTransaction.user_id == current_user.id,
                CoinTransaction.type == CoinTransactionType.earn,
                func.date(CoinTransaction.created_at) == date.date()
            ).scalar() or 0
            weekly_data.append(int(daily_earnings))
        
        # Calculate REAL task distribution from completed tasks
        like_tasks = db.query(Task).join(Order).filter(
            Task.assigned_user_id == current_user.id,
            Order.order_type == OrderType.like,
            Task.status == TaskStatus.completed
        ).count()
        
        follow_tasks = db.query(Task).join(Order).filter(
            Task.assigned_user_id == current_user.id,
            Order.order_type == OrderType.follow,
            Task.status == TaskStatus.completed
        ).count()
        
        comment_tasks = db.query(Task).join(Order).filter(
            Task.assigned_user_id == current_user.id,
            Order.order_type == OrderType.comment,
            Task.status == TaskStatus.completed
        ).count()
        
        # Calculate actual task distribution percentages
        total_tasks = like_tasks + follow_tasks + comment_tasks
        if total_tasks > 0:
            task_dist = {
                'like': round((like_tasks / total_tasks) * 100, 1),
                'follow': round((follow_tasks / total_tasks) * 100, 1),
                'comment': round((comment_tasks / total_tasks) * 100, 1),
                'other': round(((total_tasks - like_tasks - follow_tasks - comment_tasks) / total_tasks) * 100, 1) if total_tasks > like_tasks + follow_tasks + comment_tasks else 0
            }
        else:
            # Only use defaults when NO tasks exist - show 0s for transparency
            task_dist = {'like': 0.0, 'follow': 0.0, 'comment': 0.0, 'other': 0.0}
        
        # Determine level based on REAL completed tasks
        level = "Bronz"
        if completed_tasks >= 100:
            level = "Platin"
        elif completed_tasks >= 50:
            level = "Altın"
        elif completed_tasks >= 20:
            level = "Gümüş"
        
        # Calculate total earnings from ALL coin transactions
        total_earnings = db.query(func.sum(CoinTransaction.amount)).filter(
            CoinTransaction.user_id == current_user.id,
            CoinTransaction.type == CoinTransactionType.earn
        ).scalar() or 0
        
        # Update or create statistics record with REAL data
        if stats:
            stats.total_earnings = int(total_earnings)
            stats.completed_tasks = completed_tasks
            stats.active_tasks = active_tasks
            stats.daily_streak = current_user.daily_reward_streak or 0
            stats.level = level
            stats.weekly_earnings = json.dumps(weekly_data)
            stats.task_distribution = json.dumps(task_dist)
            stats.last_updated = datetime.utcnow()
        else:
            stats = UserStatistics(
                user_id=current_user.id,
                total_earnings=int(total_earnings),
                completed_tasks=completed_tasks,
                active_tasks=active_tasks,
                daily_streak=current_user.daily_reward_streak or 0,
                level=level,
                weekly_earnings=json.dumps(weekly_data),
                task_distribution=json.dumps(task_dist)
            )
            db.add(stats)
        
        db.commit()
        db.refresh(stats)
        
        return {
            "total_earnings": int(total_earnings or 0),
            "completed_tasks": int(completed_tasks or 0),
            "active_tasks": int(active_tasks or 0),
            "daily_streak": int(current_user.daily_reward_streak or 0),
            "level": level,
            "weekly_earnings": weekly_data,
            "task_distribution": task_dist
        }
        
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"İstatistikler alınamadı: {str(e)}")

@app.get("/notifications-v2")
def get_notifications_v2(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """Get user notifications"""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
    
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False
    ).count()
    
    return {
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "read": n.read,
                "created_at": n.created_at
            } for n in notifications
        ],
        "unread_count": unread_count
    }

@app.get("/badges/leaderboard", tags=["Enhanced Badges"])
async def get_badge_leaderboard(limit: int = 50):
    """Get badge leaderboard"""
    try:
        leaderboard = await enhanced_badge_system.get_badge_leaderboard(limit)
        return {
            "success": True,
            "leaderboard": leaderboard
        }
    except Exception as e:
        logger.error(f"Error getting badge leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/badges/categories", tags=["Enhanced Badges"])
async def get_badge_categories():
    """Get all available badge categories"""
    try:
        categories = {
            BadgeCategory.STARTER: "Yeni Başlayan",
            BadgeCategory.BRONZE: "Bronz",
            BadgeCategory.SILVER: "Gümüş",
            BadgeCategory.GOLD: "Altın",
            BadgeCategory.PLATINUM: "Platin",
            BadgeCategory.DIAMOND: "Elmas",
            BadgeCategory.INSTAGRAM: "Instagram",
            BadgeCategory.ACHIEVEMENT: "Başarı",
            BadgeCategory.SPECIAL: "Özel",
            BadgeCategory.SEASONAL: "Mevsimlik",
            BadgeCategory.MILESTONE: "Kilometre Taşı",
            BadgeCategory.SOCIAL: "Sosyal",
            BadgeCategory.LOYALTY: "Sadakat",
            BadgeCategory.EXPERT: "Uzman"
        }
        
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Error getting badge categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include additional endpoints
try:
    from additional_endpoints import router as additional_router
    app.include_router(additional_router, prefix="", tags=["Additional"])
    logger.info("✅ Additional endpoints loaded successfully")
except Exception as e:
    logger.warning(f"Could not load additional endpoints: {e}")

# Include Instagram and social endpoints
try:
    from instagram_endpoints import instagram_router, social_router, tasks_router, rewards_router
    app.include_router(instagram_router)
    app.include_router(social_router)
    app.include_router(tasks_router)
    app.include_router(rewards_router)
    logger.info("✅ Instagram social endpoints loaded successfully")
except Exception as e:
    logger.warning(f"Could not load Instagram endpoints: {e}")

# Manual login status response model
class ManualLoginStatusResponse(BaseModel):
    success: bool
    status: str
    message: str
    user_data: Optional[Dict] = None
    session_cookies: Optional[List] = None
    challenge_info: Optional[Dict] = None
    current_url: Optional[str] = None

class ManualLoginOpenRequest(BaseModel):
    username: Optional[str] = None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)