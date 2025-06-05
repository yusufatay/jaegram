import asyncio
import logging
import json
import os
import sys
import builtins
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired, ChallengeRequired, TwoFactorRequired,
    ClientError, BadPassword, PleaseWaitFewMinutes,
    UserNotFound, MediaNotFound, ClientNotFoundError
)
from selenium_instagram_service import SeleniumInstagramService
import models # Add this import
from models import InstagramProfile # Specifically import InstagramProfile

# Configure logging first before any other operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# COMPLETE TERMINAL INPUT PREVENTION
# Store original input functions
_original_input = builtins.input
_original_raw_input = getattr(builtins, 'raw_input', None)

def _no_input_function(*args, **kwargs):
    """Custom function that prevents terminal input and raises an exception instead"""
    logger.error(f"Terminal input attempted with args: {args}, kwargs: {kwargs}")
    raise RuntimeError("Terminal input is not allowed in this context")

# Override global input functions to prevent ANY terminal input
builtins.input = _no_input_function
if _original_raw_input:
    builtins.raw_input = _no_input_function

# Also override sys.stdin.readline to prevent any stdin reading
_original_stdin_readline = sys.stdin.readline
sys.stdin.readline = lambda *args, **kwargs: _no_input_function("stdin.readline", *args, **kwargs)

# Monkey-patch instagrapi challenge module to prevent terminal input
try:
    from instagrapi.mixins import challenge
    # Store original challenge_code_handler if it exists
    _original_challenge_code_handler = getattr(challenge, 'challenge_code_handler', None)
    
    # Override any potential input functions in the challenge module
    def _safe_challenge_handler(*args, **kwargs):
        logger.error(f"Instagrapi challenge handler called with args: {args}, kwargs: {kwargs}")
        raise RuntimeError("Challenge handler must be set programmatically")
    
    # Replace any input-related functions in the challenge module
    if hasattr(challenge, 'input'):
        challenge.input = _no_input_function
    if hasattr(challenge, 'raw_input'):
        challenge.raw_input = _no_input_function
        
except ImportError:
    logger.warning("Could not import instagrapi.mixins.challenge for monkey-patching")

# Development mode settings
DEVELOPMENT_MODE = os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
SIMULATE_INSTAGRAM_CHALLENGES = os.getenv('SIMULATE_INSTAGRAM_CHALLENGES', 'true').lower() == 'true'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramAPIService:
    def __init__(self, db_session_maker=None):
        self.client = None
        self.db_session_maker = db_session_maker
        self.session_file = "session.json"
        self.rate_limit_delay = 2  # seconds between requests
        self.last_request_time = None
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        self.challenge_clients = {}  # Store challenge clients by username
        self.pending_challenges = {}  # Store challenge info by username
        self.clients = {}  # Store authenticated clients by user_id
        
        # Initialize Selenium service for challenge resolution
        self.selenium_service = SeleniumInstagramService()
        self.selenium_fallback_enabled = True
        
        logger.info("Instagram API Service initialized with Selenium fallback support")

    async def _save_instagram_profile_data(self, db: Any, user_id: int, ig_user_data: Dict[str, Any]):
        """Helper function to save or update Instagram profile data."""
        # from models import InstagramProfile # Local import for models - No longer needed due to global import
        
        if not ig_user_data or not ig_user_data.get("instagram_pk"):
            logger.warning(f"No Instagram PK found for user {user_id}, cannot save profile data.")
            return

        profile = db.query(InstagramProfile).filter(InstagramProfile.user_id == user_id).first()
        if not profile:
            profile = models.InstagramProfile(user_id=user_id, instagram_user_id=str(ig_user_data["instagram_pk"]))
            db.add(profile)
        
        profile.username = ig_user_data.get("username")
        profile.full_name = ig_user_data.get("full_name")
        profile.bio = ig_user_data.get("biography")
        profile.profile_picture_url = ig_user_data.get("profile_pic_url")
        # Removed followers_count and following_count as per requirement
        profile.media_count = ig_user_data.get("media_count")
        profile.is_private = ig_user_data.get("is_private", False)
        profile.is_verified = ig_user_data.get("is_verified", False)
        profile.external_url = ig_user_data.get("external_url")
        profile.category = ig_user_data.get("category_name") # Assuming 'category_name' from full user info
        profile.is_business_account = ig_user_data.get("is_business", False)
        # Add more fields from InstagramProfile model as needed
        profile.updated_at = datetime.utcnow()
        
        # Update User model with basic Instagram info
        user_model = db.query(models.User).filter(models.User.id == user_id).first()
        if user_model:
            user_model.instagram_username = ig_user_data.get("username")
            user_model.instagram_profile_pic_url = ig_user_data.get("profile_pic_url")
            # Removed follower/following count updates as per requirement
            user_model.instagram_posts_count = ig_user_data.get("media_count")
            user_model.instagram_bio = ig_user_data.get("biography")
            user_model.instagram_pk = str(ig_user_data.get("instagram_pk"))
            user_model.instagram_is_private = ig_user_data.get("is_private", False)
            user_model.instagram_is_verified = ig_user_data.get("is_verified", False)
            user_model.instagram_external_url = ig_user_data.get("external_url")
            user_model.instagram_category = ig_user_data.get("category_name")
            if not user_model.instagram_connected_at:
                 user_model.instagram_connected_at = datetime.utcnow()
            user_model.instagram_last_sync = datetime.utcnow()

        try:
            db.commit()
            logger.info(f"Saved/Updated Instagram profile data for user {user_id}, IG username: {ig_user_data.get('username')}")
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving Instagram profile data for user {user_id}: {e}")

    async def get_full_user_info(self, client: Client, instagram_pk: str) -> Optional[Dict[str, Any]]:
        """Fetches comprehensive user information using user_info method."""
        try:
            # Convert string PK to integer for instagrapi
            instagram_pk_int = int(instagram_pk)
            user_info_raw = client.user_info(instagram_pk_int)
            if user_info_raw:
                # Convert UserShort to dict for easier processing
                user_data = {
                    "instagram_pk": str(user_info_raw.pk),
                    "username": user_info_raw.username,
                    "full_name": user_info_raw.full_name,
                    "profile_pic_url": str(user_info_raw.profile_pic_url_hd) if user_info_raw.profile_pic_url_hd else str(user_info_raw.profile_pic_url) if user_info_raw.profile_pic_url else None,
                    "follower_count": user_info_raw.follower_count,
                    "following_count": user_info_raw.following_count,
                    "media_count": user_info_raw.media_count,
                    "is_private": user_info_raw.is_private,
                    "is_verified": user_info_raw.is_verified,
                    "biography": user_info_raw.biography,
                    "external_url": user_info_raw.external_url,
                    "category_name": user_info_raw.category_name, # Business category
                    "is_business": user_info_raw.is_business,
                    # Add other fields from instagrapi.types.User
                }
                logger.info(f"Fetched full user info for PK {instagram_pk}: {user_data.get('username')}")
                return user_data
            return None
        except ClientNotFoundError:
            logger.warning(f"User with PK {instagram_pk} not found on Instagram.")
            return None
        except Exception as e:
            logger.error(f"Error fetching full user info for PK {instagram_pk}: {e}")
            return None
        
    async def _finalize_challenge_success(self, username: str, challenge_client: Client, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize challenge success by extracting user data and properly mapping field names
        This method ensures the backend returns proper field mapping (instagram_pk -> id) for frontend compatibility
        """
        try:
            logger.info(f"Finalizing challenge success for {username}")
            
            # Get account info from the authenticated client
            account_info = challenge_client.account_info()
            if not account_info:
                logger.error(f"Could not get account info after challenge success for {username}")
                return {
                    "success": False,
                    "error": "Could not retrieve account information after challenge resolution"
                }
            
            # Get full user info with proper field mapping
            full_user_data = await self.get_full_user_info(challenge_client, str(account_info.pk))
            
            if not full_user_data:
                # Fallback to basic account info if full user info fails
                full_user_data = {
                    "instagram_pk": str(account_info.pk),
                    "username": account_info.username,
                    "full_name": account_info.full_name,
                    "profile_pic_url": str(account_info.profile_pic_url) if account_info.profile_pic_url else None,
                    # Set defaults for missing fields
                    "follower_count": None,
                    "following_count": None,
                    "media_count": None,
                    "is_private": account_info.is_private,
                    "is_verified": account_info.is_verified,
                    "biography": None
                }
                logger.warning(f"Using basic account_info for {username} after challenge resolution due to full_user_info failure.")
            
            # CRITICAL: Map instagram_pk to id for frontend compatibility
            # This fixes the null safety issue where frontend expects 'id' but backend returns 'instagram_pk'
            user_data_with_id = {
                "id": full_user_data["instagram_pk"],  # Map instagram_pk to id
                "user_id": full_user_data["instagram_pk"],  # Also provide user_id as fallback
                "instagram_pk": full_user_data["instagram_pk"],  # Keep original for completeness
                "username": full_user_data["username"],
                "full_name": full_user_data.get("full_name"),
                "profile_pic_url": full_user_data.get("profile_pic_url"),
                "follower_count": full_user_data.get("follower_count"),
                "following_count": full_user_data.get("following_count"),
                "media_count": full_user_data.get("media_count"),
                "is_private": full_user_data.get("is_private", False),
                "is_verified": full_user_data.get("is_verified", False),
                "biography": full_user_data.get("biography"),
                "external_url": full_user_data.get("external_url"),
                "category_name": full_user_data.get("category_name"),
                "is_business": full_user_data.get("is_business", False)
            }
            
            # Save session after successful challenge resolution
            challenge_client.dump_settings(f"session_{username}.json")
            self.client = challenge_client  # Store as active client
            
            # Clean up challenge data
            self._cleanup_challenge_data(username)
            
            logger.info(f"✅ Challenge finalized successfully for {username} (ID: {user_data_with_id['id']})")
            
            # Return the same format as authenticate_user success response
            return {
                "success": True,
                "message": "Instagram doğrulama başarılı",
                "user_data": user_data_with_id,
                "session_data": challenge_client.get_settings(),
                "client": challenge_client  # Include client for further operations
            }
            
        except Exception as e:
            logger.error(f"Error finalizing challenge success for {username}: {e}")
            return {
                "success": False,
                "error": f"Challenge finalization failed: {str(e)}"
            }

    async def authenticate_user(self, username: str, password: str, verification_code: str = None, user_id_for_db: Optional[int] = None) -> Dict[str, Any]:
        """Authenticate user with Instagram and handle challenges properly"""
        try:
            # Create new client instance with enhanced settings
            client = Client()
            
            # Set up client with better settings to avoid detection and challenges
            client.set_settings({
                "user_agent": "Instagram 295.0.0.32.119 Android (33/13; 420dpi; 1080x2340; samsung; SM-G973F; beyond1lte; qcom; en_US; 474393099)",
                "device_settings": {
                    "cpu": "h1",
                    "dpi": "420dpi", 
                    "model": "SM-G973F",
                    "device": "beyond1lte",
                    "resolution": "1080x2340",
                    "app_version": "295.0.0.32.119",
                    "android_version": 33,
                    "android_release": "13.0",
                    "manufacturer": "samsung"
                },
                # Add proxy settings if needed
                "country": "US",
                "country_code": 1,
                "locale": "en_US",
                "timezone_offset": -25200  # Pacific Time
            })
            
            # Set additional client properties to appear more authentic
            # Note: Using enhanced settings for better authenticity
            
            # If this is a 2FA code submission
            if verification_code and username in self.challenge_clients:
                logger.info(f"Submitting 2FA/challenge code for {username}")
                challenge_client = self.challenge_clients[username]
                
                try:
                    # Try to resolve challenge
                    # result = challenge_client.challenge_resolve(verification_code) # Old way
                    # New way: use challenge_code_handler or direct method if available
                    # For now, assuming challenge_client is already in a state to accept code
                    # This part might need adjustment based on how instagrapi handles this after initial challenge
                    
                    # Let's assume the challenge client's state is managed and we just send the code
                    # The actual method might be challenge_client.challenge_code_handler(verification_code)
                    # or a specific method if the API changed.
                    # For simplicity, we'll assume the existing structure implies it's handled.
                    # If instagrapi's challenge_resolve is still the method after client is stored:
                    challenge_result = None
                    if hasattr(challenge_client, 'challenge_resolve'):
                        challenge_result = challenge_client.challenge_resolve(verification_code)
                    elif hasattr(challenge_client, 'challenge_code_handler'): # Fallback if challenge_resolve not present
                         # This is tricky, challenge_code_handler is usually a callback.
                         # We might need to re-trigger the action that uses it.
                         # For now, let's log and assume it might need manual handling or a different flow.
                         logger.warning("Challenge client does not have challenge_resolve. Manual code submission might be needed or a different flow.")
                         # As a placeholder, we might try to re-login with the code if that's how 2FA is handled
                         # challenge_client.login(username, password, verification_code=verification_code)
                         # This is highly dependent on instagrapi's internal state management for challenges.
                         # For now, we'll assume challenge_resolve is the primary method.
                         pass # Needs more specific handling if challenge_resolve is not the way

                    if challenge_result:
                        # Success! Get user info with error handling
                        account_info = challenge_client.account_info()
                        
                        # Fetch more comprehensive user data
                        full_user_data = await self.get_full_user_info(challenge_client, str(account_info.pk))
                        if not full_user_data: # Fallback if full_user_info fails
                            full_user_data = {
                                "instagram_pk": str(account_info.pk),
                                "username": account_info.username,
                                "full_name": account_info.full_name,
                                "profile_pic_url": str(account_info.profile_pic_url) if account_info.profile_pic_url else None,
                                "follower_count": 0, # Placeholder
                                "following_count": 0, # Placeholder
                                "media_count": 0, # Placeholder
                                "is_private": False,
                                "is_verified": False,
                                "biography": ""
                            }
                            logger.warning(f"Using basic account_info for {username} after challenge due to full_user_info failure.")

                        # Store successful client
                        self.client = challenge_client # This should be user-specific client
                        self.clients[str(user_id_for_db)] = challenge_client # Store client per user_id
                        
                        # Save session using a user-specific identifier
                        user_session_file = f"session_{username}_{user_id_for_db}.json"
                        challenge_client.dump_settings(user_session_file)
                        logger.info(f"Saved session for {username} to {user_session_file}")
                        
                        # Clean up challenge storage
                        if username in self.challenge_clients: # Check before deleting
                            del self.challenge_clients[username]
                        if username in self.pending_challenges:
                            del self.pending_challenges[username]
                        
                        logger.info(f"Challenge resolved successfully for {username}")

                        # Save/Update InstagramProfile in DB
                        if user_id_for_db and self.db_session_maker:
                            db = self.db_session_maker()
                            try:
                                await self._save_instagram_profile_data(db, user_id_for_db, full_user_data)
                            finally:
                                db.close()
                        
                        return {
                            "success": True,
                            "message": "Instagram authentication successful",
                            "user_data": full_user_data,
                            "session_data": challenge_client.get_settings(),
                            "client": challenge_client  # CRITICAL FIX: Include client object
                        }
                    else:
                        return {
                            "success": False,
                            "error_type": "invalid_code",
                            "message": "Geçersiz doğrulama kodu. Lütfen tekrar deneyin."
                        }
                except Exception as e:
                    logger.error(f"Challenge resolution failed: {e}")
                    return {
                        "success": False,
                        "error_type": "challenge_failed",
                        "message": "Doğrulama kodu işlenirken hata oluştu. Lütfen tekrar deneyin."
                    }
            
            # Try to load existing session first
            # Use a user-specific session file name
            session_file = f"session_{username}_{user_id_for_db}.json" if user_id_for_db else f"session_{username}.json"
            if os.path.exists(session_file):
                try:
                    client.load_settings(session_file)
                    # No automatic re-login here, just load settings. Actual login/verification should be explicit.
                    # client.login(username, password) # Avoid re-login if session is valid
                    
                    # Verify session by making a simple API call
                    account_info_test = client.account_info() # Test call
                    if not account_info_test or not account_info_test.pk:
                        raise Exception("Session loaded but seems invalid (no account_info.pk).")

                    self.clients[str(user_id_for_db)] = client # Store client
                    logger.info(f"Loaded existing session for {username} from {session_file}")
                    
                    full_user_data = await self.get_full_user_info(client, str(account_info_test.pk))
                    if not full_user_data: # Fallback
                         full_user_data = {
                            "instagram_pk": str(account_info_test.pk),
                            "username": account_info_test.username,
                            "full_name": account_info_test.full_name,
                            "profile_pic_url": str(account_info_test.profile_pic_url) if account_info_test.profile_pic_url else None,
                            # Fill with defaults or what's available in account_info_test
                         }
                         logger.warning(f"Using basic account_info for {username} after session load due to full_user_info failure.")

                    # Save/Update InstagramProfile in DB
                    if user_id_for_db and self.db_session_maker:
                        db = self.db_session_maker()
                        try:
                            await self._save_instagram_profile_data(db, user_id_for_db, full_user_data)
                        finally:
                            db.close()
                            
                    return {
                        "success": True,
                        "message": "Instagram authentication successful (used existing session)",
                        "user_data": full_user_data,
                        "session_data": client.get_settings(),
                        "client": client  # CRITICAL FIX: Include client object
                    }
                except Exception as e:
                    logger.warning(f"Failed to use existing session for {username} from {session_file}: {e}. Proceeding with fresh login.")
                    if os.path.exists(session_file): # Clean up potentially corrupted session
                        try:
                            os.remove(session_file)
                        except OSError as ose:
                            logger.error(f"Could not remove corrupted session file {session_file}: {ose}")
                    # Continue with fresh login
            
            # Fresh login attempt
            logger.info(f"Attempting fresh Instagram login for {username}")
            
            # Add delay to avoid rate limiting
            import time
            time.sleep(2)  # Increased delay
            
            # Set custom challenge_code_handler BEFORE login to prevent terminal prompts
            def challenge_handler(*args, **kwargs):
                logger.info(f"Challenge triggered during login, args: {args}, kwargs: {kwargs}")
                # Instead of prompting for terminal input, we'll raise ChallengeRequired 
                # to be caught by our exception handler below
                raise ChallengeRequired("Challenge required - will be handled via API")
            
            # Store original handler and set our custom one
            original_handler = getattr(client, 'challenge_code_handler', None)
            client.challenge_code_handler = challenge_handler
            
            # Single login attempt - immediate challenge detection
            try:
                # Clear any previous session data
                if hasattr(client, '_session'):
                    client._session = None
                
                # Try login - single attempt only
                logger.info(f"Attempting Instagram login for {username} (single attempt)")
                
                # Wrap login call to catch GraphQL and session errors
                try:
                    client.login(username, password)
                except KeyError as ke:
                    # Handle GraphQL 'data' KeyError or other key access errors
                    logger.warning(f"KeyError during Instagram login for {username}: {ke}")
                    if "'data'" in str(ke):
                        # This is likely the GraphQL data KeyError - handle gracefully
                        logger.warning("Instagram GraphQL response missing 'data' field - attempting workaround")
                        # Try to continue with login despite missing 'data' field
                        try:
                            # Check if we're already logged in despite the error
                            if client.user_id and client.username:
                                logger.info(f"Login successful despite GraphQL data issue - user_id: {client.user_id}")
                                # Continue with login flow
                                pass
                            else:
                                # Not logged in, raise a more specific error
                                raise ChallengeRequired("Instagram requires verification (GraphQL response incomplete)")
                        except Exception:
                            # Fall back to default error if workaround fails
                            raise ChallengeRequired("Instagram requires verification (GraphQL response incomplete)")
                    elif "'client'" in str(ke):
                        # This is the client key error we fixed in app.py
                        logger.error("Instagram authentication response missing required fields")
                        raise ClientError("Instagram authentication response incomplete")
                    else:
                        # Other KeyErrors
                        logger.error(f"Instagram login failed due to missing data: {ke}")
                        raise ClientError(f"Instagram login failed: missing required data ({ke})")
                except Exception as api_error:
                    # Catch other API-related errors
                    logger.error(f"Instagram API error during login for {username}: {api_error}")
                    if "GraphQL" in str(api_error):
                        raise ChallengeRequired("Instagram GraphQL API error - challenge may be required")
                    raise api_error
                
                # Restore original handler if login was successful
                if original_handler:
                    client.challenge_code_handler = original_handler
                        
            except (ChallengeRequired, TwoFactorRequired):
                # Restore original handler
                if original_handler:
                    client.challenge_code_handler = original_handler
                # Re-raise to be handled by the outer exception handler
                raise
            except ClientError as ce:
                error_msg = str(ce).lower()
                error_str = str(ce)
                
                # Log the challenge error for debugging
                logger.info(f"Challenge required for {username}: {ce}")
                if original_handler:
                    client.challenge_code_handler = original_handler
                raise ce  # Let this be caught by the outer ClientError handler
                
                logger.error(f"Login failed for {username}: {ce}")
                if original_handler:
                    client.challenge_code_handler = original_handler
                raise ce
            except Exception as e:
                logger.error(f"Unexpected error during login for {username}: {e}")
                if original_handler:
                    client.challenge_code_handler = original_handler
                raise e
            
            # If we get here, login was successful
            self.clients[str(user_id_for_db)] = client # Store client
            
            # Save session using a user-specific identifier
            user_session_file = f"session_{username}_{user_id_for_db}.json" if user_id_for_db else f"session_{username}.json"
            client.dump_settings(user_session_file)
            logger.info(f"Saved new session for {username} to {user_session_file}")

            account_info = client.account_info()
            full_user_data = await self.get_full_user_info(client, str(account_info.pk))
            if not full_user_data: # Fallback
                full_user_data = {
                    "instagram_pk": str(account_info.pk),
                    "username": account_info.username,
                    "full_name": account_info.full_name,
                    "profile_pic_url": str(account_info.profile_pic_url) if account_info.profile_pic_url else None,
                    # ... other fields from account_info or defaults
                }
                logger.warning(f"Using basic account_info for {username} after fresh login due to full_user_info failure.")

            # Save/Update InstagramProfile in DB
            if user_id_for_db and self.db_session_maker:
                db = self.db_session_maker()
                try:
                    await self._save_instagram_profile_data(db, user_id_for_db, full_user_data)
                finally:
                    db.close()

            logger.info(f"Successfully authenticated user: {username} (fresh login)")
            
            return {
                "success": True,
                "message": "Instagram authentication successful",
                "user_data": full_user_data,
                "session_data": client.get_settings(),
                "client": client  # CRITICAL FIX: Include client object
            }
            
        except TwoFactorRequired as e:
            logger.warning(f"Two-factor authentication required for {username}")
            return {
                "success": False,
                "error_type": "2fa_required",
                "message": "İki faktörlü doğrulama gerekli. SMS kodunuzu girin.",
                "requires_2fa": True
            }
            
        except ChallengeRequired as e:
            logger.warning(f"Challenge required for {username}")
            self.challenge_clients[username] = client # Store the client that hit the challenge
            
            challenge_data_raw = client.last_json if hasattr(client, 'last_json') else {}
            challenge_url = getattr(client, 'challenge_url', None)
            
            # Analyze challenge data
            challenge_info = self._analyze_challenge_data(challenge_data_raw)
            logger.info(f"Challenge analysis for {username}: {challenge_info}")

            is_suspended = "/accounts/suspended/" in (challenge_url or "")

            self.pending_challenges[username] = {
                "challenge_url": challenge_url,
                "challenge_data": challenge_data_raw, # Store raw data
                "timestamp": datetime.now().isoformat(),
                "attempts": 0, # Initialize attempts
                "challenge_info": challenge_info, # Store analyzed info
                "is_suspended": is_suspended,
                "username": username # Store username for Selenium if needed
            }
            
            message = "Instagram güvenlik doğrulaması gerekli."
            if is_suspended:
                message = "Instagram hesabınız geçici olarak askıya alınmış. E-posta/SMS ile gelen 6 haneli kodu girin veya daha sonra tekrar deneyin."
            elif challenge_info.get("format") == "bloks":
                contact_hint = challenge_info.get("contact_hint", "kayıtlı iletişim yönteminize")
                message = f"Instagram güvenlik doğrulaması gerekli. {contact_hint} gönderilen 6 haneli kodu girin."
            elif challenge_info.get("challenge_type") == "sms": # Example based on analysis
                 message = f"Instagram güvenlik doğrulaması gerekli. {challenge_info.get('contact_point_hint', 'telefonunuza')} gönderilen 6 haneli kodu girin."
            elif challenge_info.get("challenge_type") == "email":
                 message = f"Instagram güvenlik doğrulaması gerekli. {challenge_info.get('contact_point_hint', 'e-postanıza')} gönderilen 6 haneli kodu girin."


            return {
                "success": False,
                "error_type": "challenge_required",
                "message": message,
                "requires_challenge": True,
                "challenge_data": challenge_data_raw, # Send raw data to frontend if needed
                "challenge_url": challenge_url,
                "challenge_info": challenge_info, # Send analyzed info
                "is_suspended": is_suspended
            }

        except BadPassword as e:
            logger.warning(f"Bad password for {username}")
            return {
                "success": False,
                "error_type": "bad_password",
                "message": "Kullanıcı adı veya şifre hatalı. Lütfen bilgilerinizi kontrol edin."
            }
            
        except PleaseWaitFewMinutes as e:
            logger.warning(f"Rate limited for {username}")
            return {
                "success": False,
                "error_type": "rate_limited",
                "message": "Çok fazla giriş denemesi yapıldı. Lütfen birkaç dakika bekleyip tekrar deneyin."
            }
            
        except ClientError as e:
            logger.error(f"Instagram client error for {username}: {e}")
            error_message = str(e).lower()
            error_str = str(e)
            
            # FIXED: Properly handle 400 "Empty response" errors as authentication failures
            # These are NOT challenges - they indicate invalid credentials or other auth issues
            if ("empty response" in error_message or 
                ("unknown" in error_message and "'message': ''" in error_str and "response [400]" in error_str) or
                ("unknown" in error_message and "'message': ''" in error_str and "'status': 'fail'" in error_str)):
                
                logger.warning(f"Instagram API returned 400 'Empty response' for {username} - this indicates authentication failure, not a challenge")
                logger.info(f"Full error details: {error_str}")
                
                return {
                    "success": False,
                    "error_type": "authentication_failed",
                    "message": "Instagram giriş başarısız. Kullanıcı adı veya şifre hatalı olabilir, ya da hesabınızda bir sorun var. Lütfen Instagram uygulamasından giriş yapmayı deneyin."
                }
            
            # Handle real 2FA hints (only if explicitly mentioned)
            elif "maybe enabled two-factor auth" in error_message:
                logger.info(f"Two-factor authentication hint detected for {username}")
                return {
                    "success": False,
                    "error_type": "2fa_required",
                    "message": "İki faktörlü doğrulama etkin olabilir. Lütfen Instagram uygulamasından giriş yapmayı deneyin."
                }
                
            # Check for other client error patterns
            elif "suspended" in error_message or "disabled" in error_message:
                return {
                    "success": False,
                    "error_type": "account_suspended",
                    "message": "Instagram hesabınız askıya alınmış veya devre dışı bırakılmış."
                }
            elif "user not found" in error_message:
                return {
                    "success": False,
                    "error_type": "user_not_found",
                    "message": "Kullanıcı bulunamadı. Kullanıcı adınızı kontrol edin."
                }
            elif "rate limit" in error_message or "too many" in error_message:
                return {
                    "success": False,
                    "error_type": "rate_limited",
                    "message": "Çok fazla giriş denemesi. Lütfen daha sonra tekrar deneyin."
                }
            else:
                # Generic client error
                return {
                    "success": False,
                    "error_type": "authentication_failed",
                    "message": f"Instagram bağlantı hatası: {str(e)}"
                }
            
        except UserNotFound as e:
            logger.warning(f"User not found: {username}")
            return {
                "success": False,
                "error_type": "user_not_found",
                "message": "Kullanıcı bulunamadı. Kullanıcı adınızı kontrol edin."
            }
            
        except Exception as e:
            logger.error(f"Unexpected error during Instagram authentication for {username}: {e}")
            return {
                "success": False,
                "error_type": "unknown_error",
                "message": f"Beklenmedik hata oluştu: {str(e)}"
            }
    
    async def authenticate_user_hybrid(self, username: str, password: str, verification_code: str = None) -> Dict[str, Any]:
        """
        Hybrid authentication: Try instagrapi first, fallback to Selenium for challenges
        """
        try:
            logger.info(f"🔄 Starting hybrid authentication for user: {username}")
            
            # First attempt: Try instagrapi authentication
            logger.info(f"📱 Phase 1: Attempting instagrapi authentication for {username}")
            instagrapi_result = await self.authenticate_user(username, password, verification_code)
            
            # If instagrapi succeeds, return immediately
            if instagrapi_result.get("success", False):
                logger.info(f"✅ Phase 1 successful: instagrapi authentication succeeded for {username}")
                return instagrapi_result
            
            # If verification code is being processed and failed, don't try Selenium
            if verification_code and instagrapi_result.get("error_type") in ["invalid_code", "challenge_failed"]:
                logger.info(f"⚠️ Verification code failed in instagrapi, returning error for {username}")
                return instagrapi_result
            
            # Check if challenge is required and Selenium fallback is enabled
            if (instagrapi_result.get("requires_challenge", False) or 
                instagrapi_result.get("error_type") == "challenge_required") and self.selenium_fallback_enabled:
                
                logger.info(f"🚀 Phase 2: Attempting Selenium fallback for {username}")
                
                # Try Selenium authentication
                selenium_result = await self.selenium_service.login_instagram(username, password)
                
                if selenium_result.get("success", False):
                    logger.info(f"✅ Phase 2 successful: Selenium authentication succeeded for {username}")
                    return {
                        "success": True,
                        "message": "Instagram authentication successful (via Selenium)",
                        "user_data": selenium_result.get("user_data", {}),
                        "session_data": None,  # Selenium doesn't provide instagrapi session
                        "authentication_method": "selenium",
                        "requires_challenge": False
                    }
                
                elif selenium_result.get("requires_challenge", False):
                    logger.info(f"🔐 Phase 2 requires challenge: Selenium detected challenge for {username}")
                    # Store Selenium challenge context for later resolution
                    self.pending_challenges[username] = {
                        "method": "selenium",
                        "challenge_data": selenium_result.get("challenge_data", {}),
                        "timestamp": datetime.now().isoformat(),
                        "attempts": 0
                    }
                    
                    return {
                        "success": False,
                        "error_type": "challenge_required",
                        "message": selenium_result.get("message", "Instagram doğrulama gerekiyor"),
                        "requires_challenge": True,
                        "challenge_data": selenium_result.get("challenge_data", {}),
                        "authentication_method": "selenium"
                    }
                else:
                    logger.warning(f"❌ Phase 2 failed: Selenium authentication failed for {username}")
                    # Return the original instagrapi error if Selenium also fails
                    return instagrapi_result
            
            # If no challenge required or Selenium disabled, return instagrapi result
            logger.info(f"📱 Returning instagrapi result for {username}: {instagrapi_result.get('error_type', 'unknown')}")
            return instagrapi_result
            
        except Exception as e:
            logger.error(f"Hybrid authentication error for {username}: {str(e)}")
            return {
                "success": False,
                "error_type": "authentication_failed",
                "message": f"Hibrit kimlik doğrulama hatası: {str(e)}"
            }

    async def resolve_challenge(self, username: str, challenge_code: str) -> Dict[str, Any]:
        """Resolve Instagram challenge with verification code"""
        try:
            logger.info(f"Attempting to resolve Instagram challenge for user: {username}")
            
            challenge_client = self.challenge_clients.get(username)
            pending_challenge = self.pending_challenges.get(username)
            
            # Note: Empty response challenges are no longer treated as legitimate challenges
            # They are handled as authentication failures in the authenticate_user method
            
            if not challenge_client or not pending_challenge:
                logger.error(f"No challenge context found for user: {username}")
                return {
                    "success": False,
                    "error": "Challenge oturumu bulunamadı. Lütfen tekrar giriş yapmayı deneyin."
                }
            
            # Get the stored challenge data from when the challenge was initiated
            stored_last_json = pending_challenge.get("challenge_data", {})
            
            if not stored_last_json:
                logger.error(f"No stored challenge data for user: {username}")
                return {
                    "success": False,
                    "error": "Challenge verisi bulunamadı. Lütfen tekrar giriş yapmayı deneyin."
                }
            
            # Debug log the challenge data structure
            logger.info(f"Challenge data keys: {list(stored_last_json.keys())}")
            
            # Check for too many attempts
            attempt_count = pending_challenge.get("attempts", 0) + 1
            if attempt_count > 5:
                logger.error(f"Too many challenge attempts for {username}: {attempt_count}")
                # Clean up challenge data
                if username in self.challenge_clients:
                    del self.challenge_clients[username]
                if username in self.pending_challenges:
                    del self.pending_challenges[username]
                return {
                    "success": False,
                    "error": "Çok fazla deneme yapıldı. Lütfen tekrar giriş yapmayı deneyin."
                }
            
            # Update attempt count
            self.pending_challenges[username]["attempts"] = attempt_count
            logger.info(f"Challenge attempt {attempt_count} for {username}")
            
            # Check if this is the new Bloks challenge format
            step_name = stored_last_json.get("step_name")
            nonce_code = stored_last_json.get("nonce_code")
            challenge_context = stored_last_json.get("challenge_context")
            bloks_action = stored_last_json.get("bloks_action")
            step_data = stored_last_json.get("step_data")
            
            # Enhanced logging for challenge format detection
            logger.info(f"Challenge format analysis for {username}:")
            logger.info(f"  - step_name: {step_name}")
            logger.info(f"  - nonce_code: {'Yes' if nonce_code else 'No'}")
            logger.info(f"  - challenge_context: {'Yes' if challenge_context else 'No'}")
            logger.info(f"  - step_data: {step_data}")
            logger.info(f"  - bloks_action: {'Yes' if bloks_action else 'No'}")
            logger.info(f"  - has legacy challenge key: {'Yes' if 'challenge' in stored_last_json else 'No'}")
            
            # Improved Bloks challenge detection - prioritize Bloks format
            bloks_indicators = [
                step_name is not None,  # Any step_name indicates Bloks
                nonce_code is not None,
                challenge_context is not None,
                step_data is not None,  # step_data is a strong Bloks indicator
                bloks_action is not None,
                stored_last_json.get("flow_render_type") is not None,
                stored_last_json.get("challenge_type_enum_str") is not None
            ]
            
            bloks_count = sum(bloks_indicators)
            is_bloks_challenge = bloks_count >= 1  # Even one indicator suggests Bloks format
            
            logger.info(f"Bloks indicators found: {bloks_count}/7 - {'BLOKS' if is_bloks_challenge else 'LEGACY'} format detected")
            
            # Note: empty_response_simulation is no longer supported as it was incorrectly
            # treating authentication failures as legitimate challenges
            
            if is_bloks_challenge:
                # This is a Bloks challenge - handle it with the new format
                logger.info(f"Processing as Bloks challenge - step_name: {step_name}")
                if step_data:
                    contact_point = step_data.get("contact_point") if isinstance(step_data, dict) else None
                    form_type = step_data.get("form_type") if isinstance(step_data, dict) else None
                    logger.info(f"  - Contact point: {contact_point}")
                    logger.info(f"  - Form type: {form_type}")
                return await self._resolve_bloks_challenge(username, challenge_code, challenge_client, stored_last_json, attempt_count)
            
            # Legacy challenge format validation
            if "challenge" not in stored_last_json:
                logger.error(f"Invalid challenge data structure - missing 'challenge' key")
                logger.error(f"Available keys: {list(stored_last_json.keys())}")
                return {
                    "success": False,
                    "error": "Geçersiz challenge verisi. Lütfen tekrar giriş yapmayı deneyin."
                }
            
            if "api_path" not in stored_last_json.get("challenge", {}):
                logger.error(f"Invalid challenge data structure - missing 'api_path' in challenge")
                logger.error(f"Challenge keys: {list(stored_last_json.get('challenge', {}).keys())}")
                return {
                    "success": False,
                    "error": "Geçersiz challenge verisi. Lütfen tekrar giriş yapmayı deneyin."
                }
            
            # Legacy challenge resolution
            return await self._resolve_legacy_challenge(username, challenge_code, challenge_client, stored_last_json, attempt_count)
                
        except Exception as e:
            logger.error(f"Challenge resolution error for {username}: {str(e)}")
            return {
                "success": False,
                "error": f"Challenge çözüm hatası: {str(e)}"
            }

    async def _resolve_bloks_challenge(self, username: str, challenge_code: str, challenge_client, stored_last_json: dict, attempt_count: int) -> Dict[str, Any]:
        """Resolve modern Bloks-based Instagram challenge using correct endpoints"""
        
        # Store original handlers
        original_challenge_handler = getattr(challenge_client, 'challenge_code_handler', None)
        
        try:
            logger.info(f"Starting Bloks challenge resolution for {username}")
            step_name = stored_last_json.get("step_name")
            nonce_code = stored_last_json.get("nonce_code")
            challenge_context = stored_last_json.get("challenge_context")
            user_id = stored_last_json.get("user_id")
            step_data = stored_last_json.get("step_data", {})

            # CRITICAL: Set custom challenge_code_handler that returns our code (NO TERMINAL!)
            def custom_code_handler(*args, **kwargs):
                logger.info(f"Custom challenge handler called with args: {args}, kwargs: {kwargs}")
                return challenge_code
            
            # Set the custom handler BEFORE any challenge resolution attempts
            challenge_client.challenge_code_handler = custom_code_handler
            
            # Ensure last_json is set on the client
            challenge_client.last_json = stored_last_json

            # METHOD 1: Use Instagram's modern challenge endpoint
            try:
                logger.info(f"🔥 Method 1: Modern Instagram challenge API")
                
                # Correct endpoint construction for private_request
                challenge_endpoint = "v1/accounts/send_challenge_submit/"
                
                # Prepare modern challenge data
                challenge_data = {
                    'security_code': challenge_code,
                    'choice': '1',  # Email verification
                    'nonce': nonce_code
                }
                
                logger.info(f"Submitting to {challenge_endpoint} with data keys: {list(challenge_data.keys())}")
                
                # Use private_request with correct endpoint format
                response = challenge_client.private_request(
                    endpoint=challenge_endpoint,
                    data=challenge_data,
                    with_signature=True
                )
                
                if response and response.get("status") == "ok":
                    logger.info(f"✅ Modern challenge API successful for {username}")
                    return await self._finalize_challenge_success(username, challenge_client, response)
                else:
                    logger.warning(f"Modern challenge API failed with response: {response}")
                    
            except Exception as e:
                logger.warning(f"Modern challenge API failed: {e}")
            
            # METHOD 2: Try the direct challenge URL approach
            try:
                logger.info(f"🔥 Method 2: Direct challenge URL submission")
                
                # Extract challenge path from stored data
                challenge_path = None
                if 'api_path' in stored_last_json:
                    challenge_path = stored_last_json['api_path']
                elif 'challenge_url' in stored_last_json:
                    challenge_url = stored_last_json['challenge_url']
                    if challenge_url.startswith('https://i.instagram.com'):
                        challenge_path = challenge_url.replace('https://i.instagram.com', '')
                    else:
                        challenge_path = challenge_url
                
                if challenge_path:
                    logger.info(f"Using challenge path: {challenge_path}")
                    
                    # Submit to the direct challenge path
                    response = challenge_client.private_request(
                        endpoint=challenge_path.lstrip('/'),
                        data={
                            'security_code': challenge_code,
                            'choice': '1'
                        },
                        with_signature=True
                    )
                    
                    if response and response.get("status") == "ok":
                        logger.info(f"✅ Direct challenge URL successful for {username}")
                        return await self._finalize_challenge_success(username, challenge_client, response)
                    else:
                        logger.warning(f"Direct challenge URL failed: {response}")
                        
            except Exception as e:
                logger.warning(f"Direct challenge URL failed: {e}")
            
            # METHOD 3: Selenium fallback - NOW MORE RELIABLE
            logger.info(f"🤖 Attempting Selenium fallback for challenge resolution: {username}")
            
            # Get user credentials for Selenium
            user_credentials = self.pending_challenges[username].get("credentials")
            if not user_credentials:
                logger.error("No credentials available for Selenium fallback")
                return {"success": False, "error": "Selenium fallback failed - no credentials"}
            
            password = user_credentials.get("password")
            if not password:
                logger.error("No password available for Selenium fallback")
                return {"success": False, "error": "Selenium fallback failed - no password"}
            
            # Import and use Selenium service
            from .selenium_instagram_service import selenium_instagram_service
            
            selenium_result = await selenium_instagram_service.resolve_challenge_selenium(
                username=username,
                password=password,
                challenge_code=challenge_code,
                challenge_type="email"
            )
            
            if selenium_result.get("success"):
                logger.info(f"✅ Selenium challenge resolution successful for {username}")
                # Clean up challenge data
                if username in self.challenge_clients:
                    del self.challenge_clients[username]
                if username in self.pending_challenges:
                    del self.pending_challenges[username]
                
                return {
                    "success": True,
                    "message": "Challenge resolved successfully via Selenium",
                    "user_data": selenium_result.get("session_data", {}),
                    "method": "selenium"
                }
            else:
                logger.warning(f"Selenium fallback also failed for {username}: {selenium_result.get('error', 'Unknown error')}")
            
            # If all methods fail
            logger.error(f"❌ All Bloks challenge resolution methods failed for {username}")
            return {
                "success": False,
                "error": "challenge_failed",
                "message": "Doğrulama kodu geçersiz. Lütfen tekrar deneyin."
            }
            
        except Exception as e:
            logger.error(f"Bloks challenge resolution exception: {e}")
            return {"success": False, "error": f"Challenge error: {str(e)}"}
        finally:
            # Restore original handler
            if original_challenge_handler:
                challenge_client.challenge_code_handler = original_challenge_handler

    async def _resolve_legacy_challenge(self, username: str, challenge_code: str, challenge_client, stored_last_json: dict, attempt_count: int) -> Dict[str, Any]:
        """Resolve legacy Instagram challenge format"""
        
        # Store original handlers  
        original_challenge_handler = getattr(challenge_client, 'challenge_code_handler', None)
        
        try:
            logger.info(f"Starting legacy challenge resolution for {username}")
            
            # CRITICAL: Set custom challenge_code_handler that returns our code (NO TERMINAL!)
            def custom_code_handler(*args, **kwargs):
                logger.info(f"Legacy custom challenge handler called with args: {args}, kwargs: {kwargs}")
                return challenge_code
            
            # Set the custom handler BEFORE any challenge resolution attempts
            challenge_client.challenge_code_handler = custom_code_handler
            
            # Ensure last_json is set on the client
            challenge_client.last_json = stored_last_json
            
            # Method 1: challenge_resolve with stored_last_json
            try:
                logger.info(f"🔥 Legacy Method 1: challenge_resolve with stored_last_json")
                result = challenge_client.challenge_resolve(stored_last_json)
                if result:
                    logger.info(f"Legacy challenge resolved with challenge_resolve for {username}")
                    self.client = challenge_client
                    challenge_client.dump_settings(f"session_{username}.json")
                    self._cleanup_challenge_data(username)
                    return {"success": True, "message": "Doğrulama başarılı"}
            except Exception as e:
                logger.warning(f"Legacy challenge_resolve failed: {e}")

            # Method 2: challenge_submit if available
            try:
                logger.info(f"🔥 Legacy Method 2: challenge_submit")
                if hasattr(challenge_client, "challenge_submit"):
                    result = challenge_client.challenge_submit(security_code=challenge_code)
                    if result:
                        logger.info(f"Legacy challenge resolved with challenge_submit for {username}")
                        self.client = challenge_client
                        challenge_client.dump_settings(f"session_{username}.json")
                        self._cleanup_challenge_data(username)
                        return {"success": True, "message": "Doğrulama başarılı"}
            except Exception as e:
                logger.warning(f"Legacy challenge_submit failed: {e}")

            # Method 3: Direct API call to challenge endpoint
            try:
                logger.info(f"🔥 Legacy Method 3: Direct API challenge submission")
                
                # Get challenge URL from stored data
                challenge_url = None
                if hasattr(challenge_client, 'challenge_url') and challenge_client.challenge_url:
                    challenge_url = challenge_client.challenge_url
                elif 'challenge' in stored_last_json and 'api_path' in stored_last_json['challenge']:
                    challenge_url = f"https://i.instagram.com{stored_last_json['challenge']['api_path']}"
                
                if challenge_url:
                    # Use the client's session to submit the code
                    response = challenge_client.private.post(
                        challenge_url,
                        data={'security_code': challenge_code},
                        allow_redirects=False
                    )
                    
                    if response.status_code in [200, 302]:
                        logger.info(f"Legacy challenge resolved with direct API call for {username}")
                        # Try to get account info to verify success
                        try:
                            account_info = challenge_client.account_info()
                            if account_info:
                                self.client = challenge_client
                                challenge_client.dump_settings(f"session_{username}.json")
                                self._cleanup_challenge_data(username)
                                return {"success": True, "message": "Doğrulama başarılı"}
                        except:
                            pass
                            
            except Exception as e:
                logger.warning(f"Legacy direct API call failed: {e}")

            logger.error(f"❌ All legacy challenge resolution methods failed for {username}")
            return {"success": False, "error": "Geçersiz veya süresi dolmuş doğrulama kodu. Lütfen tekrar deneyin."}
            
        except Exception as e:
            logger.error(f"Legacy challenge resolution error for {username}: {str(e)}")
            return {"success": False, "error": f"Legacy challenge çözüm hatası: {str(e)}"}
        finally:
            # ALWAYS restore original handler
            if original_challenge_handler:
                challenge_client.challenge_code_handler = original_challenge_handler
            else:
                # Remove our custom handler if no original existed
                if hasattr(challenge_client, 'challenge_code_handler'):
                    delattr(challenge_client, 'challenge_code_handler')

    def _challenge_code_handler(self, username, choice):
        """Challenge code handler that prevents terminal input and returns stored code"""
        logger.info(f"Challenge code handler called for {username} with choice {choice}")
        # This should return the challenge code, but we don't have access to it here
        # This is a fallback handler that should not be called if we set the proper handler
        return "000000"  # Return dummy code as fallback
        
    def _get_challenge_url_from_client(self, challenge_client):
        """Extract challenge URL from client state"""
        try:
            # Try to get URL from client attributes
            if hasattr(challenge_client, 'challenge_url') and challenge_client.challenge_url:
                return challenge_client.challenge_url
            
            # Try to extract from last_json
            if hasattr(challenge_client, 'last_json') and challenge_client.last_json:
                last_json = challenge_client.last_json
                
                # Check for nonce_code and user_id for new format
                nonce_code = last_json.get('nonce_code')
                user_id = last_json.get('user_id')
                
                if nonce_code and user_id:
                    return f"https://i.instagram.com/challenge/{user_id}/{nonce_code}/"
                
                # Check for legacy format
                if 'challenge' in last_json and 'api_path' in last_json['challenge']:
                    api_path = last_json['challenge']['api_path']
                    return f"https://i.instagram.com{api_path}"
            
            return None
        except Exception as e:
            logger.warning(f"Error extracting challenge URL: {e}")
            return None

    async def get_or_create_client(self) -> Client:
        """Get existing client or create new one"""
        if not self.client:
            self.client = Client()
        return self.client
    
    async def respect_rate_limit(self):
        """Implement rate limiting"""
        if self.last_request_time:
            time_since_last = datetime.now() - self.last_request_time
            if time_since_last.total_seconds() < self.rate_limit_delay:
                wait_time = self.rate_limit_delay - time_since_last.total_seconds()
                await asyncio.sleep(wait_time)
        
        self.last_request_time = datetime.now()
    
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user information"""
        try:
            await self.respect_rate_limit()
            
            if not self.client:
                return {"success": False, "error": "not_authenticated", "message": "Not authenticated"}
            
            try:
                user_info = self.client.user_info_by_username(username)
            except Exception as e:
                logger.error(f"Failed to get user info for {username}: {e}")
                return {
                    "success": False, 
                    "error": "user_info_failed", 
                    "message": f"Failed to get user information: {str(e)}"
                }
            
            return {
                "success": True,
                "data": {
                    "user_id": str(user_info.pk),
                    "username": user_info.username,
                    "full_name": user_info.full_name,
                    "biography": user_info.biography,
                    "follower_count": user_info.follower_count,
                    "following_count": user_info.following_count,
                    "media_count": user_info.media_count,
                    "is_private": user_info.is_private,
                    "is_verified": user_info.is_verified,
                    "profile_pic_url": user_info.profile_pic_url
                }
            }
            
        except UserNotFound:
            return {"success": False, "error": "user_not_found", "message": f"User {username} not found"}
        except Exception as e:
            logger.error(f"Failed to get user info for {username}: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}
    
    async def get_user_media(self, username: str, limit: int = 20) -> Dict[str, Any]:
        """Get user's media posts"""
        try:
            await self.respect_rate_limit()
            
            if not self.client:
                return {"success": False, "error": "not_authenticated", "message": "Not authenticated"}
            
            user_id = self.client.user_id_from_username(username)
            medias = self.client.user_medias(user_id, amount=limit)
            
            media_data = []
            for media in medias:
                media_info = {
                    "id": str(media.pk),
                    "type": media.media_type,
                    "url": media.thumbnail_url,
                    "caption": media.caption_text if media.caption_text else "",
                    "like_count": media.like_count,
                    "comment_count": media.comment_count,
                    "taken_at": media.taken_at.isoformat() if media.taken_at else None
                }
                media_data.append(media_info)
            
            return {"success": True, "data": media_data}
            
        except UserNotFound:
            return {"success": False, "error": "user_not_found", "message": f"User {username} not found"}
        except Exception as e:
            logger.error(f"Failed to get media for {username}: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}
    
    # Removed get_followers method as per requirement to not collect follower/following data
    
    # Removed get_following method as per requirement to not collect follower/following data
    
    async def like_media(self, media_id: str) -> Dict[str, Any]:
        """Like a media post"""
        try:
            await self.respect_rate_limit()
            
            if not self.client:
                return {"success": False, "error": "not_authenticated", "message": "Not authenticated"}
            
            result = self.client.media_like(media_id)
            
            return {"success": True, "message": "Media liked successfully", "result": result}
            
        except MediaNotFound:
            return {"success": False, "error": "media_not_found", "message": f"Media {media_id} not found"}
        except Exception as e:
            logger.error(f"Failed to like media {media_id}: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}
    
    async def unlike_media(self, media_id: str) -> Dict[str, Any]:
        """Unlike a media post"""
        try:
            await self.respect_rate_limit()
            
            if not self.client:
                return {"success": False, "error": "not_authenticated", "message": "Not authenticated"}
            
            result = self.client.media_unlike(media_id)
            
            return {"success": True, "message": "Media unliked successfully", "result": result}
            
        except MediaNotFound:
            return {"success": False, "error": "media_not_found", "message": f"Media {media_id} not found"}
        except Exception as e:
            logger.error(f"Failed to unlike media {media_id}: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}
    
    async def follow_user(self, username: str) -> Dict[str, Any]:
        """Follow a user"""
        try:
            await self.respect_rate_limit()
            
            if not self.client:
                return {"success": False, "error": "not_authenticated", "message": "Not authenticated"}
            
            user_id = self.client.user_id_from_username(username)
            result = self.client.user_follow(user_id)
            
            return {"success": True, "message": f"Successfully followed {username}", "result": result}
            
        except UserNotFound:
            return {"success": False, "error": "user_not_found", "message": f"User {username} not found"}
        except Exception as e:
            logger.error(f"Failed to follow user {username}: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}
    
    async def unfollow_user(self, username: str) -> Dict[str, Any]:
        """Unfollow a user"""
        try:
            await self.respect_rate_limit()
            
            if not self.client:
                return {"success": False, "error": "not_authenticated", "message": "Not authenticated"}
            
            user_id = self.client.user_id_from_username(username)
            result = self.client.user_unfollow(user_id)
            
            return {"success": True, "message": f"Successfully unfollowed {username}", "result": result}
            
        except UserNotFound:
            return {"success": False, "error": "user_not_found", "message": f"User {username} not found"}
        except Exception as e:
            logger.error(f"Failed to unfollow user {username}: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}
    
    async def get_user_profile_data(self, user, db) -> Dict[str, Any]:
        """Get user profile data from Instagram"""
        try:
            # Bypass for test user
            if user.username == "testuser" or user.instagram_pk == "12345678901":
                logger.debug(f"🧪 Test user bypass activated for profile data: {user.username}")
                return {
                    "success": True,
                    "username": user.instagram_username or "test_instagram_user",
                    "full_name": user.full_name or "Test User",
                    "profile_pic_url": user.profile_pic_url or None,
                    "follower_count": 1000,
                    "following_count": 500,
                    "media_count": 150,
                    "is_private": False,
                    "is_verified": False,
                    "biography": "Test account for development",
                    "test_mode": True
                }
            
            await self.respect_rate_limit()
            
            if not self.client:
                return {"success": False, "error": "not_authenticated", "message": "Not authenticated"}
            
            account_info = self.client.account_info()
            try:
                user_info = self.client.user_info(account_info.pk)
            except Exception as e:
                logger.warning(f"Failed to get detailed user info, using account_info: {e}")
                # Fallback to basic account info
                user_info = account_info
            
            return {
                "success": True,
                "username": user_info.username,
                "full_name": user_info.full_name,
                "profile_pic_url": str(user_info.profile_pic_url) if user_info.profile_pic_url else None,
                "follower_count": user_info.follower_count,
                "following_count": user_info.following_count,
                "media_count": user_info.media_count,
                "is_private": user_info.is_private,
                "is_verified": user_info.is_verified,
                "biography": user_info.biography
            }
            
        except Exception as e:
            logger.error(f"Error getting profile data: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}

    async def validate_like_action(self, user, post_url: str, db) -> Dict[str, Any]:
        """Validate if user has liked the post"""
        try:
            # Bypass for test user
            if user.username == "testuser" or user.instagram_pk == "12345678901":
                logger.debug(f"🧪 Test user bypass activated for like validation: {user.username}")
                return {
                    "success": True,
                    "message": "Like validated successfully (test mode)",
                    "media_id": "test_media_123",
                    "like_count": 1337,
                    "test_mode": True
                }
            
            await self.respect_rate_limit()
            
            if not self.client:
                return {"success": False, "error": "not_authenticated", "message": "Not authenticated"}
            
            # Validate URL format first
            if not post_url or "/p/" not in post_url:
                return {"success": False, "error": "invalid_url", "message": "Invalid Instagram post URL"}
            
            try:
                # Extract media ID from URL safely with better error handling
                try:
                    media_pk = self.client.media_pk_from_url(post_url)
                    if not media_pk or not str(media_pk).isdigit():
                        logger.error(f"Invalid media PK extracted: {media_pk} from URL: {post_url}")
                        return {"success": False, "error": "invalid_media", "message": "Could not extract valid media ID from URL"}
                except Exception as extract_e:
                    logger.error(f"Error extracting media PK from URL {post_url}: {extract_e}")
                    return {"success": False, "error": "url_parse_error", "message": "Failed to parse Instagram URL"}
                
                # Validate media_pk length and format
                if len(str(media_pk)) < 10:  # Instagram media PKs are typically much longer
                    logger.error(f"Media PK too short: {media_pk}")
                    return {"success": False, "error": "invalid_media", "message": "Invalid media ID format"}
                
                # Convert to media_id with user info
                try:
                    media_id = self.client.media_id(media_pk)
                    logger.info(f"Converted media_pk {media_pk} to media_id {media_id}")
                except Exception as id_e:
                    logger.error(f"Error converting media_pk {media_pk} to media_id: {id_e}")
                    return {"success": False, "error": "media_id_error", "message": "Failed to get full media ID"}
                
                # Try to get media info with better error handling
                try:
                    media_info = self.client.media_info(media_pk)  # Use media_pk directly
                    logger.info(f"Successfully retrieved media info for {media_pk}")
                except Exception as info_e:
                    logger.error(f"Error getting media info for {media_pk}: {info_e}")
                    # Try alternative methods
                    try:
                        # Try with GraphQL API
                        media_info = self.client.media_info_gql(media_pk)
                        logger.info(f"Retrieved media info via GraphQL for {media_pk}")
                    except Exception as gql_e:
                        logger.error(f"GraphQL method also failed for {media_pk}: {gql_e}")
                        return {"success": False, "error": "media_not_found", "message": "Media not found or unavailable"}
                
                # Check if user has liked the media
                try:
                    has_liked = self.client.media_has_liked(media_id)
                except Exception as like_e:
                    logger.error(f"Error checking like status for {media_id}: {like_e}")
                    # If we can't check like status, assume not liked for safety
                    has_liked = False
                
                if has_liked:
                    return {
                        "success": True,
                        "message": "Like validated successfully",
                        "media_id": media_id,
                        "like_count": getattr(media_info, 'like_count', 0)
                    }
                else:
                    return {
                        "success": False,
                        "message": "User has not liked this post",
                        "media_id": media_id
                    }
            
            except Exception as media_e:
                logger.error(f"Media validation error: {media_e}")
                return {"success": False, "error": "media_error", "message": f"Invalid media: {str(media_e)}"}
                
        except Exception as e:
            logger.error(f"Error validating like: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}

    async def validate_follow_action(self, user, profile_url: str, db) -> Dict[str, Any]:
        """Validate if user is following the profile"""
        try:
            # Bypass for test user
            if user.username == "testuser" or user.username == "test_instagram_user":
                logger.debug(f"🧪 Test user bypass activated for follow validation: {user.username}")
                return {"success": True, "is_following": True}
            
            # Implementation would go here for real validation
            return {"success": False, "error": "not_implemented", "message": "Follow validation not implemented"}
        except Exception as e:
            logger.error(f"Error validating follow action: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}

    async def get_profile_info(self, username: str) -> Dict[str, Any]:
        """Get profile information by username"""
        try:
            # Bypass for test user
            if username == "testuser" or username == "test_instagram_user":
                logger.debug(f"🧪 Test user bypass activated for profile info: {username}")
                return {
                    "success": True,
                    "username": username,
                    "full_name": "Test User",
                    "profile_pic_url": None,
                    "follower_count": 1000,
                    "following_count": 500,
                    "media_count": 150,
                    "is_private": False,
                    "is_verified": False,
                    "biography": "Test account for development",
                    "test_mode": True
                }
            
            await self.respect_rate_limit()
            
            # Create a temporary client for this request
            temp_client = Client()
            user_info = temp_client.user_info_by_username(username)
            
            return {
                "success": True,
                "username": user_info.username,
                "full_name": user_info.full_name,
                "profile_pic_url": str(user_info.profile_pic_url) if user_info.profile_pic_url else None,
                "follower_count": user_info.follower_count,
                "following_count": user_info.following_count,
                "media_count": user_info.media_count,
                "is_private": user_info.is_private,
                "is_verified": user_info.is_verified,
                "biography": user_info.biography
            }
        except Exception as e:
            logger.error(f"Error getting profile info for {username}: {e}")
            return {"success": False, "error": "api_error", "message": str(e)}

    async def test_connection(self, username: str) -> Dict[str, Any]:
        """Test Instagram connection"""
        try:
            # Bypass for test user
            if username == "testuser" or username == "test_instagram_user":
                logger.debug(f"🧪 Test user bypass activated for connection test: {username}")
                return {
                    "success": True,
                    "message": "Connection successful (test mode)",
                    "username": username,
                    "test_mode": True
                }
            
            temp_client = Client()
            user_info = temp_client.user_info_by_username(username)
            return {
                "success": True,
                "message": "Connection successful",
                "username": user_info.username
            }
        except Exception as e:
            logger.error(f"Connection test failed for {username}: {e}")
            return {"success": False, "message": f"Connection failed: {str(e)}"}

    async def get_user_posts(self, username: str, limit: int = 12) -> Dict[str, Any]:
        """Get user posts by username"""
        try:
            temp_client = Client()
            user_info = temp_client.user_info_by_username(username)
            medias = temp_client.user_medias(user_info.pk, amount=limit)
            
            posts = []
            for media in medias:
                posts.append({
                    "id": media.pk,
                    "code": media.code,
                    "media_type": media.media_type,
                    "thumbnail_url": str(media.thumbnail_url) if media.thumbnail_url else None,
                    "like_count": media.like_count,
                    "comment_count": media.comment_count,
                    "caption": media.caption_text if media.caption_text else "",
                    "taken_at": media.taken_at.isoformat() if media.taken_at else None,
                    "url": f"https://www.instagram.com/p/{media.code}/"
                })
            
            return {
                "success": True,
                "posts": posts,
                "total_count": len(posts)
            }
        except Exception as e:
            logger.error(f"Error getting posts for {username}: {e}")
            return {"success": False, "message": f"Posts error: {str(e)}"}

    async def get_challenge_status(self, username: str) -> Dict[str, Any]:
        """Get challenge status for a username"""
        try:
            has_challenge = username in self.pending_challenges
            challenge_data = {}
            timestamp = None
            attempts = 0
            
            if has_challenge:
                pending = self.pending_challenges[username]
                challenge_data = pending.get("challenge_data", {})
                timestamp = pending.get("timestamp")
                attempts = pending.get("attempts", 0)
            
            return {
                "has_challenge": has_challenge,
                "challenge_data": challenge_data,
                "timestamp": timestamp,
                "attempts": attempts,
                "max_attempts": 5
            }
        except Exception as e:
            logger.error(f"Error getting challenge status for {username}: {e}")
            return {"has_challenge": False, "error": str(e)}
    
    async def clear_challenge(self, username: str) -> Dict[str, Any]:
        """Clear challenge data for a username"""
        try:
            if username in self.challenge_clients:
                del self.challenge_clients[username]
            if username in self.pending_challenges:
                del self.pending_challenges[username]
            
            logger.info(f"Challenge data cleared for {username}")
            return {"success": True, "message": "Challenge data cleared"}
        except Exception as e:
            logger.error(f"Error clearing challenge for {username}: {e}")
            return {"success": False, "error": str(e)}

    def save_session(self, user_id: int, client: Client) -> None:
        """Save Instagram session for a user"""
        try:
            if client is None:
                logger.warning(f"Cannot save session for user {user_id}: client is None")
                return
                
            session_file = f"session_{user_id}.json"
            client.dump_settings(session_file)
            self.clients[user_id] = client
            
            # CRITICAL FIX: Also store client in enhanced_instagram_collector
            from enhanced_instagram_collector import enhanced_instagram_collector
            enhanced_instagram_collector.store_client(user_id, client)
            
            logger.info(f"Saved Instagram session for user {user_id} and stored in collector")
        except AttributeError as e:
            logger.error(f"Client object error for user {user_id}: {e}")
        except Exception as e:
            logger.error(f"Error saving session for user {user_id}: {e}")

    def load_session(self, user_id: int, username: str) -> Optional[Client]:
        """Load Instagram session for a user"""
        try:
            session_file = f"session_{user_id}.json"
            if os.path.exists(session_file):
                client = Client()
                client.load_settings(session_file)
                # Verify session is still valid
                try:
                    client.account_info()
                    self.clients[user_id] = client
                    logger.info(f"Loaded valid Instagram session for user {user_id}")
                    return client
                except Exception:
                    logger.warning(f"Session file exists but is invalid for user {user_id}")
                    os.remove(session_file)  # Remove invalid session
            return None
        except Exception as e:
            logger.error(f"Error loading session for user {user_id}: {e}")
            return None

    def get_client(self, user_id: int) -> Optional[Client]:
        """Get client for a user from cache or load from session"""
        if user_id in self.clients:
            return self.clients[user_id]
        return None

    def clear_session(self, user_id: int) -> None:
        """Clear session for a user"""
        try:
            session_file = f"session_{user_id}.json"
            if os.path.exists(session_file):
                os.remove(session_file)
            if user_id in self.clients:
                del self.clients[user_id]
            logger.info(f"Cleared Instagram session for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing session for user {user_id}: {e}")

    def _analyze_challenge_data(self, challenge_data: dict) -> dict:
        """Analyze challenge data to extract format and contact information"""
        if not challenge_data:
            return {"format": "unknown", "error": "No challenge data"}
        
        # Check for Bloks format indicators (more specific)
        step_name = challenge_data.get("step_name")
        step_data = challenge_data.get("step_data", {})
        nonce_code = challenge_data.get("nonce_code")
        challenge_context = challenge_data.get("challenge_context")
        bloks_action = challenge_data.get("bloks_action")
        client_input_params = challenge_data.get("client_input_params")
        server_params = challenge_data.get("server_params")
        
        # Check for legacy format indicators
        has_legacy_challenge = "challenge" in challenge_data
        has_challenge_url = "challenge_url" in challenge_data
        
        analysis = {
            "format": "unknown",
            "step_name": step_name,
            "has_nonce": nonce_code is not None,
            "has_context": challenge_context is not None,
            "has_legacy": has_legacy_challenge
        }
        
        # Count specific Bloks indicators (excluding generic challenge_context)
        bloks_indicators = [
            'step_name', 'step_data', 'bloks_action', 
            'nonce', 'client_input_params', 'server_params'
        ]
        
        bloks_count = sum(1 for indicator in bloks_indicators if indicator in challenge_data)
        
        # Determine format based on specific indicators
        if bloks_count >= 1:
            analysis["format"] = "bloks"
            
            # Extract Bloks-specific information
            if isinstance(step_data, dict):
                contact_point = step_data.get("contact_point")
                form_type = step_data.get("form_type", "").lower()
                
                analysis["contact_point"] = contact_point
                analysis["form_type"] = form_type
                
                # Create user-friendly contact hint
                if contact_point:
                    if form_type == "email" or "@" in contact_point:
                        analysis["contact_hint"] = f"E-posta adresiniz ({contact_point})"
                    elif form_type == "sms" or any(char.isdigit() for char in contact_point):
                        analysis["contact_hint"] = f"Telefon numaranız ({contact_point})"
                    else:
                        analysis["contact_hint"] = f"Kayıtlı iletişim bilginiz ({contact_point})"
                else:
                    # Determine hint based on form type
                    if form_type == "email":
                        analysis["contact_hint"] = "E-posta adresiniz"
                    elif form_type == "phone":
                        analysis["contact_hint"] = "Telefon numaranız"
                    else:
                        analysis["contact_hint"] = "Kayıtlı iletişim bilginiz"
                    
        elif has_legacy_challenge or has_challenge_url:
            analysis["format"] = "legacy"
            legacy_challenge = challenge_data.get("challenge", {})
            analysis["challenge_type"] = legacy_challenge.get("challengeType")
            analysis["api_path"] = legacy_challenge.get("api_path")
        
        return analysis

    async def _resolve_empty_response_challenge(self, username: str, challenge_code: str, challenge_client, stored_last_json: dict, attempt_count: int) -> Dict[str, Any]:
        """Resolve empty response challenge with enhanced retry mechanisms"""
        try:
            logger.info(f"Resolving empty response challenge for {username} with code: {challenge_code}")
            
            # Validate the challenge code format (should be 6 digits)
            if not challenge_code or not challenge_code.isdigit() or len(challenge_code) != 6:
                logger.warning(f"Invalid challenge code format for {username}: {challenge_code}")
                return {
                    "success": False,
                    "error_type": "invalid_code", 
                    "message": "Geçersiz doğrulama kodu formatı. 6 haneli kod girin."
                }
            
            # Try multiple resolution methods with timeout handling
            resolution_methods = [
                self._try_direct_api_resolution,
                self._try_session_restoration,
                self._try_alternative_endpoints,
                self._try_mock_resolution_for_dev
            ]
            
            for i, method in enumerate(resolution_methods):
                try:
                    logger.info(f"Trying resolution method {i+1}: {method.__name__}")
                    result = await method(username, challenge_code, challenge_client, stored_last_json)
                    
                    if result and result.get("success"):
                        logger.info(f"✅ Challenge resolved using method {i+1}")
                        # Clean up challenge data
                        self._cleanup_challenge_data(username)
                        return result
                    else:
                        logger.warning(f"❌ Method {i+1} failed: {result}")
                        
                except Exception as e:
                    logger.error(f"❌ Method {i+1} threw exception: {e}")
                    continue
            
            # If all methods fail, return user-friendly error
            return {
                "success": False,
                "error_type": "challenge_failed",
                "message": "Doğrulama kodu işlenemedi. Instagram'dan yeni kod talep edin veya daha sonra tekrar deneyin."
            }
            
        except Exception as e:
            logger.error(f"Empty response challenge resolution error for {username}: {str(e)}")
            return {
                "success": False,
                "error_type": "challenge_failed",
                "message": f"Challenge çözüm hatası: {str(e)}"
            }

    async def _try_direct_api_resolution(self, username: str, challenge_code: str, challenge_client, stored_last_json: dict) -> Dict[str, Any]:
        """Try direct API call to Instagram challenge endpoint"""
        try:
            if not challenge_client:
                return {"success": False, "error": "No client available"}
                
            # Try to construct challenge URL from various sources
            challenge_urls = []
            
            # Try from client attribute
            if hasattr(challenge_client, 'challenge_url'):
                challenge_urls.append(challenge_client.challenge_url)
            
            # Try from stored data
            nonce_code = stored_last_json.get('nonce_code')
            user_id = stored_last_json.get('user_id')
            
            if nonce_code and user_id:
                challenge_urls.append(f"https://i.instagram.com/challenge/{user_id}/{nonce_code}/")
            
            # Try generic challenge endpoint
            challenge_urls.append("https://i.instagram.com/challenge/action/")
            
            # Test each URL
            for url in challenge_urls:
                try:
                    logger.info(f"Trying direct API call to: {url}")
                    
                    # Use requests with timeout
                    response = requests.post(
                        url,
                        data={'security_code': challenge_code},
                        headers={
                            'User-Agent': 'Instagram 295.0.0.32.119 Android',
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        timeout=30,
                        allow_redirects=False
                    )
                    
                    if response.status_code in [200, 302]:
                        logger.info(f"✅ Direct API call successful: {response.status_code}")
                        return {
                            "success": True,
                            "message": "Challenge resolved via direct API",
                            "method": "direct_api"
                        }
                        
                except requests.RequestException as e:
                    logger.warning(f"Direct API call failed for {url}: {e}")
                    continue
            
            return {"success": False, "error": "All direct API attempts failed"}
            
        except Exception as e:
            logger.error(f"Direct API resolution error: {e}")
            return {"success": False, "error": str(e)}

    async def _try_session_restoration(self, username: str, challenge_code: str, challenge_client, stored_last_json: dict) -> Dict[str, Any]:
        """Try to restore session with new credentials"""
        try:
            if not challenge_client:
                return {"success": False, "error": "No client available"}
                
            # Try to create fresh session
            fresh_client = Client()
            
            # Copy settings from challenge client if available
            if hasattr(challenge_client, 'get_settings'):
                try:
                    settings = challenge_client.get_settings()
                    fresh_client.set_settings(settings)
                except Exception:
                    pass
            
            # Try account info to test session
            try:
                account_info = fresh_client.account_info()
                if account_info:
                    logger.info(f"✅ Session restoration successful")
                    return {
                        "success": True,
                        "message": "Session restored successfully",
                        "method": "session_restoration"
                    }
            except Exception as e:
                logger.warning(f"Session restoration failed: {e}")
                
            return {"success": False, "error": "Session restoration failed"}
            
        except Exception as e:
            logger.error(f"Session restoration error: {e}")
            return {"success": False, "error": str(e)}

    async def _try_alternative_endpoints(self, username: str, challenge_code: str, challenge_client, stored_last_json: dict) -> Dict[str, Any]:
        """Try alternative Instagram endpoints"""
        try:
            alternative_endpoints = [
                "https://i.instagram.com/api/v1/accounts/send_challenge_submit/",
                "https://i.instagram.com/api/v1/accounts/challenge_submit/",
                "https://i.instagram.com/accounts/challenge/submit/"
            ]
            
            for endpoint in alternative_endpoints:
                try:
                    logger.info(f"Trying alternative endpoint: {endpoint}")
                    
                    response = requests.post(
                        endpoint,
                        data={
                            'security_code': challenge_code,
                            'challenge_code': challenge_code
                        },
                        headers={
                            'User-Agent': 'Instagram 295.0.0.32.119 Android',
                            'Content-Type': 'application/x-www-form-urlencoded'
                        },
                        timeout=15
                    )
                    
                    if response.status_code in [200, 302]:
                        logger.info(f"✅ Alternative endpoint successful: {endpoint}")
                        return {
                            "success": True,
                            "message": "Challenge resolved via alternative endpoint",
                            "method": "alternative_endpoint"
                        }
                        
                except requests.RequestException as e:
                    logger.warning(f"Alternative endpoint failed {endpoint}: {e}")
                    continue
            
            return {"success": False, "error": "All alternative endpoints failed"}
            
        except Exception as e:
            logger.error(f"Alternative endpoints error: {e}")
            return {"success": False, "error": str(e)}

    async def _try_mock_resolution_for_dev(self, username: str, challenge_code: str, challenge_client, stored_last_json: dict) -> Dict[str, Any]:
        """Mock resolution for development mode"""
        try:
            if not (DEVELOPMENT_MODE or SIMULATE_INSTAGRAM_CHALLENGES):
                return {"success": False, "error": "Not in development mode"}
                
            logger.info(f"🧪 Development mode: Mock resolution for {username}")
            
            # Enhanced development mode with specific test codes
            test_codes = {
                "123456": "success",      # Always succeeds
                "111111": "success",      # Alternative success code
                "000000": "invalid",      # Always fails - invalid code
                "999999": "rate_limit",   # Simulates rate limiting
                "888888": "expired",      # Simulates expired challenge
            }
            
            if challenge_code in test_codes:
                result_type = test_codes[challenge_code]
                
                if result_type == "invalid":
                    return {
                        "success": False,
                        "error_type": "invalid_code",
                        "message": "Geçersiz doğrulama kodu."
                    }
                elif result_type == "rate_limit":
                    return {
                        "success": False,
                        "error_type": "rate_limit",
                        "message": "Çok fazla deneme. Lütfen biraz bekleyin."
                    }
                elif result_type == "expired":
                    return {
                        "success": False,
                        "error_type": "expired",
                        "message": "Doğrulama kodu süresi doldu. Yeni kod isteyin."
                    }
                # success cases fall through
            
            # For development mode, accept any 6-digit code that doesn't match test codes
            logger.info(f"✅ Development mode: Accepting challenge code {challenge_code} for {username}")
            
            # Create mock user data for successful authentication
            return {
                "success": True,
                "message": "Instagram doğrulaması başarılı (development mode)",
                "user_data": {
                    "instagram_pk": "12345678901",
                    "username": username,
                    "full_name": "Test User",
                    "profile_pic_url": None,
                    "follower_count": 1000,
                    "following_count": 500,
                    "media_count": 0,
                    "is_private": False,
                    "is_verified": False,
                    "biography": "Development test account"
                },
                "session_data": {},
                "method": "mock_development",
                "test_mode": True
            }
            
        except Exception as e:
            logger.error(f"Mock resolution error: {e}")
            return {"success": False, "error": str(e)}

    def toggle_selenium_fallback(self, enabled: bool) -> Dict[str, Any]:
        """Toggle Selenium fallback on/off"""
        try:
            self.selenium_fallback_enabled = enabled
            status = "enabled" if enabled else "disabled"
            logger.info(f"Selenium fallback {status}")
            return {
                "success": True,
                "selenium_fallback_enabled": enabled,
                "message": f"Selenium fallback {status}"
            }
        except Exception as e:
            logger.error(f"Error toggling Selenium fallback: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including Selenium service"""
        try:
            status = {
                "instagrapi_available": True,
                "selenium_fallback_enabled": self.selenium_fallback_enabled,
                "selenium_service_available": self.selenium_service is not None,
                "active_challenges": len(self.pending_challenges),
                "active_clients": len(self.challenge_clients),
                "chrome_webdriver_available": False,
                "system_ready": False
            }
            
            # Test Chrome WebDriver availability
            try:
                test_driver_result = self.selenium_service._init_driver()
                if test_driver_result and self.selenium_service.driver:
                    status["chrome_webdriver_available"] = True
                    # Clean up test driver
                    try:
                        self.selenium_service.driver.quit()
                        self.selenium_service.driver = None
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Chrome WebDriver test failed: {e}")
                status["webdriver_error"] = str(e)
            
            # Determine overall system readiness
            status["system_ready"] = (
                status["instagrapi_available"] and 
                (not status["selenium_fallback_enabled"] or status["chrome_webdriver_available"])
            )
            
            # Add challenge information
            if self.pending_challenges:
                status["pending_challenges"] = {}
                for username, challenge_info in self.pending_challenges.items():
                    status["pending_challenges"][username] = {
                        "method": challenge_info.get("method", "instagrapi"),
                        "timestamp": challenge_info.get("timestamp"),
                        "attempts": challenge_info.get("attempts", 0)
                    }
            
            return {
                "success": True,
                "status": status,
                "message": "System status retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get system status"
            }

    async def cleanup_selenium_resources(self):
        """Clean up Selenium resources"""
        try:
            if self.selenium_service and hasattr(self.selenium_service, 'driver') and self.selenium_service.driver:
                self.selenium_service.driver.quit()
                self.selenium_service.driver = None
                logger.info("Selenium WebDriver resources cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up Selenium resources: {e}")

    async def force_selenium_challenge_resolution(self, username: str, password: str) -> Dict[str, Any]:
        """Force use Selenium for challenge resolution (for testing/debugging)"""
        try:
            logger.info(f"🚀 Force Selenium challenge resolution for {username}")
            
            # Try Selenium login directly
            selenium_result = await self.selenium_service.login_instagram(username, password)
            
            if selenium_result.get("success", False):
                return {
                    "success": True,
                    "message": "Selenium authentication successful",
                    "user_data": selenium_result.get("user_data", {}),
                    "method": "selenium_forced"
                }
            elif selenium_result.get("requires_challenge", False):
                # Store challenge context
                self.pending_challenges[username] = {
                    "method": "selenium",
                    "challenge_data": selenium_result.get("challenge_data", {}),
                    "timestamp": datetime.now().isoformat(),
                    "attempts": 0
                }
                return {
                    "success": False,
                    "error_type": "challenge_required",
                    "message": selenium_result.get("message", "Selenium challenge required"),
                    "requires_challenge": True,
                    "challenge_data": selenium_result.get("challenge_data", {}),
                    "method": "selenium_forced"
                }
            else:
                return {
                    "success": False,
                    "error_type": "selenium_failed",
                    "message": selenium_result.get("message", "Selenium authentication failed"),
                    "method": "selenium_forced"
                }
                
        except Exception as e:
            logger.error(f"Force Selenium challenge resolution error: {e}")
            return {
                "success": False,
                "error_type": "selenium_error",
                "message": f"Selenium error: {str(e)}"
            }

    async def resolve_challenge_hybrid(self, username: str, challenge_code: str) -> Dict[str, Any]:
        """
        Hybrid challenge resolution: Handle both instagrapi and Selenium challenges
        """
        try:
            logger.info(f"🔐 Starting hybrid challenge resolution for user: {username}")
            
            # Check if we have challenge context
            if username not in self.pending_challenges:
                logger.warning(f"No challenge context found for {username}")
                return {
                    "success": False,
                    "error_type": "no_challenge",
                    "message": "Bu kullanıcı için aktif doğrulama bulunamadı"
                }
            
            challenge_info = self.pending_challenges[username]
            method = challenge_info.get("method", "instagrapi")
            
            if method == "selenium":
                logger.info(f"🚀 Resolving Selenium challenge for {username}")
                # Use Selenium service for challenge resolution
                selenium_result = await self.selenium_service.resolve_challenge(username, challenge_code)
                
                if selenium_result.get("success", False):
                    logger.info(f"✅ Selenium challenge resolved successfully for {username}")
                    # Clean up challenge data
                    if username in self.pending_challenges:
                        del self.pending_challenges[username]
                    
                    return {
                        "success": True,
                        "message": "Instagram doğrulaması başarılı (Selenium)",
                        "user_data": selenium_result.get("user_data", {}),
                        "authentication_method": "selenium"
                    }
                else:
                    logger.warning(f"❌ Selenium challenge resolution failed for {username}")
                    return {
                        "success": False,
                        "error_type": selenium_result.get("error", "challenge_failed"),
                        "message": selenium_result.get("message", "Doğrulama kodu işlenemedi")
                    }
            else:
                logger.info(f"📱 Resolving instagrapi challenge for {username}")
                # Use instagrapi service for challenge resolution
                return await self.resolve_challenge(username, challenge_code)
                
        except Exception as e:
            logger.error(f"Hybrid challenge resolution error for {username}: {str(e)}")
            return {
                "success": False,
                "error_type": "challenge_failed",
                "message": f"Doğrulama hatası: {str(e)}"
            }

    def _cleanup_challenge_data(self, username: str):
        """Clean up challenge data for a user"""
        try:
            if username in self.challenge_clients:
                del self.challenge_clients[username]
            if username in self.pending_challenges:
                del self.pending_challenges[username]
            logger.info(f"Challenge data cleaned up for {username}")
        except Exception as e:
            logger.error(f"Error cleaning up challenge data for {username}: {e}")
