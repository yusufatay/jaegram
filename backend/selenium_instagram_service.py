#!/usr/bin/env python3
"""
Selenium-based Instagram Login and Challenge Resolution Service
Advanced web automation for Instagram authentication with challenge handling
"""

import asyncio
import logging
import os
import time
import json
import re
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    ElementClickInterceptedException, StaleElementReferenceException
)

# Configure logging
logger = logging.getLogger(__name__)

class SeleniumInstagramService:
    """Advanced Selenium-based Instagram service with challenge resolution"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.session_dir = "instagram_sessions"
        self.screenshots_dir = "instagram_screenshots"
        self.challenge_contexts = {}
        self.logged_in_users = {}
        
        # Create directories
        os.makedirs(self.session_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Chrome options for Instagram
        self.chrome_options = self._get_chrome_options()
        
        logger.info("Selenium Instagram Service initialized")
    
    def _get_chrome_options(self) -> Options:
        """Configure Chrome options for visible user interaction"""
        options = Options()
        
        # VISIBLE MODE - For user interaction
        # options.add_argument("--headless") # This line is removed - now visible
        
        # Window settings
        options.add_argument("--window-size=1200,800")
        # options.add_argument("--start-maximized") # Can cause issues in some environments
        
        # Security and performance
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu") # Often helpful in headless/server environments
        
        # Instagram specific settings
        prefs = {
            "profile.default_content_setting_values.notifications": 2,  # Disable notifications
            "profile.default_content_settings.popups": 0,  # Block pop-ups
            "credentials_enable_service": False, # Disable password saving prompt
            "profile.password_manager_enabled": False # Disable password manager
        }
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("excludeSwitches", ['enable-automation']) # Corrected line
        options.add_experimental_option('useAutomationExtension', False) # Corrected line

        # Normal browser behavior
        options.add_argument("--disable-blink-features=AutomationControlled") # More robust way to hide automation
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36') # Common user agent
        
        return options
    
    def _init_driver(self) -> bool:
        """Initialize Chrome WebDriver"""
        try:
            # Try to find ChromeDriver automatically
            # Ensure chromedriver is in PATH or specify its location via Service
            try:
                service = Service() # Assumes chromedriver is in PATH
                logger.info("Attempting to use ChromeDriver from PATH.")
            except Exception as e:
                logger.warning(f"ChromeDriver not found in PATH or Service() failed: {e}. Trying common locations.")
                # Add common paths for chromedriver if needed, or ensure it's installed and in PATH
                # Example: service = Service(executable_path=\'/usr/local/bin/chromedriver\')
                return False

            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            
            # Configure WebDriver
            self.driver.execute_script("Object.defineProperty(navigator, \'webdriver\', {get: () => undefined})")
            self.driver.implicitly_wait(5) # Reduced implicit wait, prefer explicit waits
            self.wait = WebDriverWait(self.driver, 15) # Default explicit wait
            
            logger.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}", exc_info=True)
            if self.driver:
                self.driver.quit()
            self.driver = None
            return False

    async def open_instagram_for_manual_login(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Opens Instagram in a visible browser for the user to log in manually.
        The browser session remains active for subsequent operations.
        """
        try:
            logger.info(f"🌐 Attempting to open Instagram for manual login (user: {username or 'Not provided'})...") # Corrected f-string
            
            if self.driver:
                logger.warning("Browser already open. Reusing existing session for manual login.")
                try:
                    self.driver.get("https://www.instagram.com/accounts/login/")
                    # Potentially bring window to front if possible, platform dependent
                except Exception as e:
                    logger.error(f"Error navigating to login page on existing driver: {e}. Attempting to re-initialize.")
                    self.close_browser() # Close faulty driver
                    if not self._init_driver():
                        return {
                            "success": False, "error": "webdriver_reinit_failed",
                            "message": "Failed to re-initialize WebDriver after an issue with the existing session."
                        }
                    self.driver.get("https://www.instagram.com/accounts/login/")

            elif not self._init_driver():
                return {
                    "success": False, "error": "webdriver_init_failed",
                    "message": "Failed to initialize WebDriver. Ensure Chrome and ChromeDriver are correctly installed and configured."
                }
            else:
                 self.driver.get("https://www.instagram.com/accounts/login/")

            await asyncio.sleep(2) # Allow page to start loading

            # Handle cookie banners/privacy notices
            await self._handle_privacy_notices() # Increased wait within this function if needed

            if username:
                try:
                    username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
                    await self._type_human_like(username_field, username)
                    logger.info(f"✅ Username \'{username}\' pre-filled.")
                except TimeoutException:
                    logger.warning("Username field not found in time to pre-fill.")
                except Exception as e:
                    logger.warning(f"Could not pre-fill username: {e}")
            
            logger.info("✅ Instagram login page opened. User should log in manually in the browser.")
            return {
                "success": True,
                "message": "Instagram login page is open in the browser. Please log in manually.",
                "status": "awaiting_manual_login",
                "browser_session_active": True
            }

        except Exception as e:
            logger.error(f"Error opening Instagram for manual login: {e}", exc_info=True)
            self._take_screenshot("error_manual_login_open")
            if self.driver:
                self.close_browser()
            return {
                "success": False, "error": "manual_login_open_exception",
                "message": f"An unexpected error occurred: {str(e)}",
                "browser_session_active": False
            }

    async def get_login_status_and_capture_session(self) -> Dict[str, Any]:
        """
        Checks if the user has successfully logged in manually.
        If logged in, captures session data (cookies).
        """
        if not self.driver:
            return {"success": False, "status": "browser_closed", "message": "Browser is not open."}

        try:
            current_url = self.driver.current_url
            logger.info(f"🔍 Checking login status. Current URL: {current_url}")

            # Success indicators (logged in)
            if any(indicator in current_url for indicator in ["instagram.com/", "/feed/", "/home/", "/explore/", "/direct/"]) and \
               not any(indicator in current_url for indicator in ["/accounts/login/", "/challenge/"]):
                
                logger.info("🎉 Login successful! Capturing session data...")
                await self._handle_privacy_notices() # Handle any post-login popups

                # Try to dismiss "Save login info" if it appears
                try:
                    save_info_button_not_now = self._find_element_safe([
                        "//button[contains(text(), \'Not Now\')]",
                        "//button[contains(text(), \'Şimdi Değil\')]"
                    ], timeout=3)
                    if save_info_button_not_now:
                        await self._click_safe(save_info_button_not_now)
                        logger.info("Dismissed 'Save login info' prompt.")
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.debug(f"No 'Save login info' prompt found or error dismissing: {e}")

                # Try to dismiss "Turn on notifications" if it appears
                try:
                    notifications_button_not_now = self._find_element_safe([
                        "//button[contains(text(), \'Not Now\')]", # Often same text
                        "//button[contains(text(), \'Şimdi Değil\')]",
                        "//button[text()=\'Not Now\']", # More specific
                         "//div[@role=\'dialog\']//button[contains(., \'Not Now\') or contains(., \'Şimdi Değil\')]"
                    ], timeout=3)
                    if notifications_button_not_now:
                        await self._click_safe(notifications_button_not_now)
                        logger.info("Dismissed 'Turn on notifications' prompt.")
                        await asyncio.sleep(1)
                except Exception as e:
                    logger.debug(f"No 'Turn on notifications' prompt found or error dismissing: {e}")


                cookies = self.driver.get_cookies()
                user_data = await self._extract_user_data() # Extract basic user data

                session_id = user_data.get("username") or f"manual_user_{int(time.time())}"
                self.logged_in_users[session_id] = {
                    "cookies": cookies,
                    "user_data": user_data,
                    "login_time": datetime.now().isoformat()
                }
                
                # Optionally, save cookies to a file for persistence if needed later
                # self._save_session_cookies(session_id, cookies)

                logger.info(f"✅ Session captured for user: {user_data.get('username', 'N/A')}")
                return {
                    "success": True,
                    "status": "logged_in",
                    "message": "User is logged in. Session data captured.",
                    "user_data": user_data,
                    "cookies": cookies # Sending cookies back for now, might store server-side only
                }

            # Challenge page indicators
            elif any(indicator in current_url for indicator in ["/challenge/", "/coppa/"]):
                logger.info("🔐 User is on a challenge page.")
                challenge_data = await self._analyze_challenge_page()
                return {
                    "success": False, # Not an error, but login not complete
                    "status": "challenge_required",
                    "message": "Instagram requires verification.",
                    "challenge_details": challenge_data
                }
            
            # Still on login page
            elif "/accounts/login/" in current_url:
                logger.info("⏳ User is still on the login page.")
                return {"success": False, "status": "awaiting_login", "message": "User has not logged in yet."}

            else:
                logger.warning(f"❓ Unknown login status. URL: {current_url}")
                self._take_screenshot(f"unknown_login_status_{int(time.time())}")
                return {
                    "success": False, "status": "unknown", 
                    "message": "Could not determine login status.",
                    "current_url": current_url
                }

        except Exception as e:
            logger.error(f"Error checking login status or capturing session: {e}", exc_info=True)
            self._take_screenshot("error_check_login_status")
            return {
                "success": False, "status": "error",
                "message": f"An error occurred while checking login status: {str(e)}"
            }

    def close_browser(self) -> Dict[str, Any]:
        """Closes the Selenium WebDriver browser instance."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🔴 Selenium WebDriver browser closed.")
                self.driver = None
                return {"success": True, "message": "Browser closed successfully."}
            except Exception as e:
                logger.error(f"Error closing browser: {e}", exc_info=True)
                self.driver = None # Ensure driver is None even if quit fails
                return {"success": False, "error": "browser_close_exception", "message": str(e)}
        else:
            logger.info("ℹ️ Browser was not open.")
            return {"success": True, "message": "Browser was not open."}

    async def _handle_privacy_notices(self, attempts=2, wait_time=2):
        """Handle Instagram privacy notices and cookie banners more robustly."""
        logger.debug("Attempting to handle privacy/cookie notices...")
        for attempt in range(attempts):
            try:
                # Common privacy notice selectors (prioritize more specific ones)
                # Using XPath for text matching as it's more reliable for this
                # Ensure these XPaths are robust
                privacy_selectors_xpath = [
                    "//button[contains(text(), \'Accept All\') or contains(text(), \'Allow all cookies\') or contains(text(), \'Tümünü Kabul Et\')]",
                    "//button[contains(text(), \'Accept\') or contains(text(), \'Allow\') or contains(text(), \'Kabul Et\')]",
                    "//button[@data-cookiebanner=\'accept_button\']",
                    "//div[@role=\'dialog\']//button[contains(., \'Accept\') or contains(., \'Kabul Et\')]", # More specific to dialogs
                ]
                
                found_and_clicked = False
                for xpath_selector in privacy_selectors_xpath:
                    try:
                        # Use a shorter wait for finding these elements as they should appear quickly
                        elements = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_all_elements_located((By.XPATH, xpath_selector))
                        )
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                await self._click_safe(element)
                                logger.info(f"Clicked privacy notice button using XPath: {xpath_selector}")
                                await asyncio.sleep(1.5) # Wait for action to complete
                                found_and_clicked = True
                                break # Exit inner loop once clicked
                        if found_and_clicked:
                            break # Exit outer loop if clicked
                    except TimeoutException:
                        logger.debug(f"Privacy notice with XPath \'{xpath_selector}\' not found or not clickable in time.")
                        continue # Try next selector
                    except Exception as e:
                        logger.warning(f"Error interacting with privacy notice ({xpath_selector}): {e}")
                        continue
                
                if found_and_clicked:
                    logger.info("Privacy/cookie notice handled.")
                    return True # Successfully handled

                # If no specific button found, check for generic close buttons on overlays if any
                # This is more risky and should be used cautiously
                # Example: self._find_element_safe(["div[aria-label*='cookie' i] button[aria-label*='close' i]"])

                logger.debug(f"No privacy notices found or handled on attempt {attempt + 1}")
                if attempt < attempts -1:
                    await asyncio.sleep(wait_time) # Wait before next attempt
                
            except Exception as e:
                logger.warning(f"Exception during privacy notice handling (attempt {attempt + 1}): {e}")
                if attempt < attempts -1:
                     await asyncio.sleep(wait_time)
        logger.info("Finished privacy notice handling attempts.")
        return False # Not handled after all attempts
    
    async def _analyze_challenge_page(self) -> Dict[str, Any]:
        """Analyze the challenge page to extract information"""
        try:
            await asyncio.sleep(1) # Ensure page is settled
            page_source = self.driver.page_source.lower() # Lowercase for case-insensitive matching
            current_url = self.driver.current_url.lower()
            
            self._take_screenshot(f"analyze_challenge_{int(time.time())}")

            challenge_info = {
                "challenge_type": "unknown", # e.g., "sms", "email", "totp", "security_questions"
                "contact_point_hint": None, # e.g., "email ending in @example.com", "phone ending in 1234"
                "message": "Verification required.", # General message
                "can_try_another_way": False,
                "form_fields": [] # e.g., [{"name": "security_code", "type": "text", "label": "Security Code"}]
            }

            # General challenge indicators
            if "challenge" in current_url or "checkpoint" in current_url or "verify" in current_url:
                logger.info("Challenge page detected by URL.")

            # Extract main heading or title of the challenge
            try:
                heading_elements = self._find_elements_safe([
                    "h1", "h2", "div[role=\\'heading\\']"
                ], timeout=2)
                if heading_elements:
                    challenge_info["message"] = heading_elements[0].text.strip()
                    logger.info(f"Challenge heading: {challenge_info['message']}")
            except Exception as e: # Added proper except
                logger.debug(f"Could not extract challenge heading: {e}")


            # Look for specific challenge types
            if "enter the code we sent to your email" in page_source or "e-postana gönderdiğimiz kodu gir" in page_source:
                challenge_info["challenge_type"] = "email_code"
                challenge_info["form_fields"].append({"name": "security_code", "type": "text", "label": "Email Verification Code"})
            elif "enter the code we sent to your phone" in page_source or "telefonuna gönderdiğimiz kodu gir" in page_source:
                challenge_info["challenge_type"] = "sms_code"
                challenge_info["form_fields"].append({"name": "security_code", "type": "text", "label": "SMS Verification Code"})
            elif "enter your backup code" in page_source or "yedek kodunu gir" in page_source:
                challenge_info["challenge_type"] = "backup_code"
                challenge_info["form_fields"].append({"name": "backup_code", "type": "text", "label": "Backup Code"})
            elif "two-factor authentication" in page_source or "iki faktörlü kimlik doğrulama" in page_source:
                 challenge_info["challenge_type"] = "totp" # Time-based One-Time Password
                 challenge_info["form_fields"].append({"name": "verification_code", "type": "text", "label": "Authentication App Code"})
            elif "upload a photo of yourself" in page_source or "selfie" in page_source or ("kimliğini doğrula" in page_source and "fotoğraf" in page_source) : # More specific for photo ID
                challenge_info["challenge_type"] = "photo_id"
                challenge_info["message"] = "Photo ID verification required."
            elif "answer security questions" in page_source or "güvenlik sorularını yanıtla" in page_source:
                challenge_info["challenge_type"] = "security_questions"
                # Further analysis could extract the questions themselves if needed
            
            # Extract contact point hint (e.g., masked email or phone)
            try:
                # Look for elements that typically contain the masked contact info
                contact_hint_elements = self._find_elements_safe([
                    "//div[contains(text(), \\'@\\') and string-length(text()) > 5]", # For email
                    "//div[contains(text(), \\'+\\') and string-length(text()) > 5]", # For phone
                    "//span[contains(text(), \\'@\\') and string-length(text()) > 5]",
                    "//span[contains(text(), \\'+\\') and string-length(text()) > 5]",
                    "//p[contains(text(), \\'@\\')]",
                    "//p[contains(text(), \\'+\\')]",
                    "//label[contains(text(), \\'@\\')]",
                    "//label[contains(text(), \\'+\\')]"
                ], timeout=2)

                if contact_hint_elements:
                    for el in contact_hint_elements:
                        text = el.text.strip()
                        if text and ("sent to" in page_source or "gönderildi" in page_source or "ending in" in page_source or "ile biten" in page_source): # Ensure it's related to where code was sent
                             # Basic validation to avoid overly long/irrelevant texts
                            if len(text) < 100 and ("@" in text or "+" in text or any(c.isdigit() for c in text)):
                                challenge_info["contact_point_hint"] = text
                                logger.info(f"Found contact point hint: {text}")
                                break 
            except Exception as e: # Added proper except
                logger.debug(f"Could not extract contact point hint: {e}")

            # Check for "Try another way" or "Başka bir yöntem dene"
            try:
                try_another_way_button = self._find_element_safe([
                    "//button[contains(text(), \\'Try another way\\')]",
                    "//button[contains(text(), \\'Başka bir yöntem dene\\')]",
                    "//a[contains(text(), \\'Try another way\\')]",
                    "//a[contains(text(), \\'Başka bir yöntem dene\\')]"
                ], timeout=2)
                if try_another_way_button and try_another_way_button.is_displayed():
                    challenge_info["can_try_another_way"] = True
                    logger.info("Option to \\'Try another way\\' is available.")
            except Exception as e: # Added proper except from previous incorrect { and added exception variable
                 logger.debug(f"No \\'Try another way\\' option found: {e}")


            # If still unknown, provide a generic message
            if challenge_info["challenge_type"] == "unknown" and not challenge_info["form_fields"]:
                 challenge_info["message"] = "An unknown verification step is required. Please check the browser."
                 # Try to find any input field as a generic form field
                 generic_input = self._find_element_safe(["input[type=\\'text\\']", "input[type=\\'tel\\']"], timeout=1)
                 if generic_input:
                     label_text = "Verification Code"
                     try: # Try to get associated label
                         label_el = self.driver.find_element(By.XPATH, f"//label[@for=\\'{generic_input.get_attribute('id')}\\']")
                         if label_el: label_text = label_el.text.strip()
                     except Exception as e: # Added proper except
                         logger.debug(f"Could not get label for generic input: {e}")
                     challenge_info["form_fields"].append({"name": generic_input.get_attribute("name") or "unknown_code", "type": "text", "label": label_text})


            logger.info(f"Challenge analysis result: {challenge_info}")
            return challenge_info
            
        except Exception as e:
            logger.error(f"Error analyzing challenge page: {e}", exc_info=True)
            self._take_screenshot(f"error_analyze_challenge_{int(time.time())}")
            return { # Return a default structure on error
                "challenge_type": "error_parsing",
                "message": "Error analyzing challenge page. Please check the browser.",
                "contact_point_hint": None,
                "can_try_another_way": False,
                "form_fields": []
            }

    async def _extract_user_data(self) -> Dict[str, Any]:
        """Extract user data from Instagram profile page after successful login"""
        try:
            logger.info("Extracting user data from Instagram profile")
            user_data = {
                "username": None,
                "full_name": None,
                "profile_pic_url": None,
                "followers_count": None,
                "following_count": None,
                "posts_count": None,
                "bio": None,
                "is_verified": False,
                "is_private": False
            }
            
            # Wait for page to load
            await asyncio.sleep(2)
            
            # Try to navigate to profile if not already there
            current_url = self.driver.current_url
            if "/profile/" not in current_url and not current_url.endswith("/?"):
                try:
                    # Click on profile icon/link
                    profile_links = self._find_elements_safe([
                        "a[href*='/profile/']",
                        "a[aria-label*='Profile']",
                        "svg[aria-label*='Profile']",
                        "[data-testid='user-avatar']"
                    ], timeout=3)
                    
                    if profile_links:
                        await self._click_safe(profile_links[0])
                        await asyncio.sleep(3)
                except Exception as e:
                    logger.debug(f"Could not navigate to profile: {e}")
            
            # Extract username from URL or meta tags
            try:
                username_patterns = [
                    "//meta[@property='profile:username']/@content",
                    "//meta[@name='twitter:title']/@content",
                    "//h1//text()",
                    "//h2[contains(@class, 'username')]//text()"
                ]
                
                for pattern in username_patterns:
                    try:
                        elements = self.driver.find_elements(By.XPATH, pattern)
                        if elements:
                            text = elements[0].get_attribute("textContent") if hasattr(elements[0], "get_attribute") else str(elements[0])
                            if text and text.strip() and not text.startswith("@"):
                                user_data["username"] = text.strip()
                                break
                    except Exception:
                        continue
                        
                # Fallback: extract from URL
                if not user_data["username"]:
                    url_parts = current_url.split('/')
                    for part in url_parts:
                        if part and part not in ['https:', '', 'www.instagram.com', 'instagram.com']:
                            user_data["username"] = part
                            break
                            
            except Exception as e:
                logger.debug(f"Could not extract username: {e}")
            
            # Extract profile picture
            try:
                profile_pic_selectors = [
                    "img[alt*='profile picture']",
                    "img[data-testid*='user-avatar']",
                    "header img",
                    "img[src*='profile_pic']"
                ]
                
                pic_element = self._find_element_safe(profile_pic_selectors, timeout=2)
                if pic_element:
                    src = pic_element.get_attribute("src")
                    if src and "profile_pic" in src:
                        user_data["profile_pic_url"] = src
                        
            except Exception as e:
                logger.debug(f"Could not extract profile picture: {e}")
            
            # Extract full name
            try:
                name_selectors = [
                    "//meta[@property='og:title']/@content",
                    "//h1[contains(@class, 'full-name')]//text()",
                    "//div[contains(@class, 'full-name')]//text()",
                    "//span[contains(@class, 'full-name')]//text()"
                ]
                
                for selector in name_selectors:
                    try:
                        if selector.startswith("//"):
                            elements = self.driver.find_elements(By.XPATH, selector)
                        else:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            
                        if elements:
                            text = elements[0].get_attribute("content") if "meta" in selector else elements[0].text
                            if text and text.strip() and text != user_data.get("username"):
                                user_data["full_name"] = text.strip()
                                break
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract full name: {e}")
            
            # Extract stats (followers, following, posts)
            try:
                stats_selectors = [
                    "//a[contains(@href, '/followers/')]//span//text()",
                    "//a[contains(@href, '/following/')]//span//text()",
                    "//div[contains(text(), 'posts')]//text()"
                ]
                
                stats_text_elements = self._find_elements_safe([
                    "header section ul li",
                    "div[class*='stats'] span",
                    "a[href*='/followers/'] span",
                    "a[href*='/following/'] span"
                ], timeout=2)
                
                for element in stats_text_elements:
                    try:
                        text = element.text.strip()
                        if text and any(char.isdigit() for char in text):
                            # Try to parse numbers
                            numbers = re.findall(r'[\d,]+', text)
                            if numbers:
                                number = int(numbers[0].replace(',', ''))
                                if "follower" in text.lower():
                                    user_data["followers_count"] = number
                                elif "following" in text.lower():
                                    user_data["following_count"] = number
                                elif "post" in text.lower():
                                    user_data["posts_count"] = number
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract stats: {e}")
            
            # Extract bio
            try:
                bio_selectors = [
                    "//meta[@property='og:description']/@content",
                    "//div[contains(@class, 'bio')]//text()",
                    "//section//div[contains(@class, 'biography')]//text()"
                ]
                
                for selector in bio_selectors:
                    try:
                        if selector.startswith("//"):
                            elements = self.driver.find_elements(By.XPATH, selector)
                        else:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            
                        if elements:
                            text = elements[0].get_attribute("content") if "meta" in selector else elements[0].text
                            if text and text.strip():
                                user_data["bio"] = text.strip()
                                break
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.debug(f"Could not extract bio: {e}")
            
            # Check if account is verified or private
            try:
                # Look for verification badge
                verified_selectors = [
                    "svg[aria-label*='Verified']",
                    "span[title*='Verified']",
                    "div[class*='verified']"
                ]
                
                verified_element = self._find_element_safe(verified_selectors, timeout=1)
                if verified_element:
                    user_data["is_verified"] = True
                
                # Check if private
                page_source = self.driver.page_source.lower()
                if "private account" in page_source or "this account is private" in page_source:
                    user_data["is_private"] = True
                    
            except Exception as e:
                logger.debug(f"Could not check verification/privacy status: {e}")
            
            logger.info(f"Extracted user data: {user_data}")
            return user_data
            
        except Exception as e:
            logger.error(f"Error extracting user data: {e}", exc_info=True)
            return {
                "username": None,
                "full_name": None,
                "profile_pic_url": None,
                "followers_count": None,
                "following_count": None,
                "posts_count": None,
                "bio": None,
                "is_verified": False,
                "is_private": False
            }

    async def _extract_error_message(self) -> str:
        """Extract error message from Instagram page"""
        try:
            error_selectors = [
                "div[role='alert']",
                ".error-message",
                "[data-testid='error-message']",
                "div[class*='error']",
                "span[class*='error']",
                "p[class*='error']",
                "div[id*='error']",
                "//div[contains(text(), 'incorrect') or contains(text(), 'wrong') or contains(text(), 'invalid')]",
                "//span[contains(text(), 'incorrect') or contains(text(), 'wrong') or contains(text(), 'invalid')]",
                "//p[contains(text(), 'incorrect') or contains(text(), 'wrong') or contains(text(), 'invalid')]"
            ]
            
            for selector in error_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if elements:
                        error_text = elements[0].text.strip()
                        if error_text and len(error_text) > 0:
                            logger.info(f"Found error message: {error_text}")
                            return error_text
                except Exception:
                    continue
            
            # Fallback: look in page source for common error patterns
            page_source = self.driver.page_source.lower()
            error_patterns = [
                "incorrect username or password",
                "wrong password",
                "invalid credentials",
                "account not found",
                "login failed",
                "incorrect code",
                "expired code",
                "invalid verification code"
            ]
            
            for pattern in error_patterns:
                if pattern in page_source:
                    return pattern.title()
            
            return "An error occurred. Please try again."
            
        except Exception as e:
            logger.debug(f"Could not extract error message: {e}")
            return "An error occurred. Please try again."

    async def _type_human_like(self, element, text: str, min_delay: float = 0.05, max_delay: float = 0.15):
        """Type text in a human-like manner with random delays between keystrokes"""
        try:
            import random
            
            if not element or not text:
                logger.warning("Invalid element or text for human-like typing")
                return
            
            logger.debug(f"Typing text human-like: {len(text)} characters")
            
            # Clear field first
            element.clear()
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Type each character with random delay
            for char in text:
                element.send_keys(char)
                delay = random.uniform(min_delay, max_delay)
                await asyncio.sleep(delay)
            
            # Small pause after typing
            await asyncio.sleep(random.uniform(0.1, 0.3))
            
        except Exception as e:
            logger.error(f"Error in human-like typing: {e}")
            # Fallback to normal typing
            try:
                element.clear()
                element.send_keys(text)
            except Exception as fallback_e:
                logger.error(f"Fallback typing also failed: {fallback_e}")

    def _cleanup_challenge(self, username: str):
        """Clean up challenge context for a user"""
        try:
            if username in self.challenge_contexts:
                del self.challenge_contexts[username]
                logger.info(f"Cleaned up challenge context for {username}")
        except Exception as e:
            logger.error(f"Error cleaning up challenge context for {username}: {e}")

    def open_instagram_for_manual_login(self) -> Dict[str, Any]:
        """Opens Instagram login page in a visible browser for manual user interaction"""
        try:
            logger.info("🌐 Opening Instagram for manual login...")
            
            # Initialize driver with visible browser
            if not self.driver:
                if not self._init_driver():
                    raise Exception("Failed to initialize WebDriver")
            
            # Navigate to Instagram login
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            # Wait for page to load
            time.sleep(3)
            
            # Take screenshot for debugging
            self._take_screenshot("manual_login_opened")
            
            logger.info("✅ Instagram login page opened. User can now login manually.")
            
            return {
                "success": True,
                "message": "Instagram login page opened. Please login manually in the browser.",
                "instructions": "Complete the login process including any challenges in the opened browser window."
            }
            
        except Exception as e:
            logger.error(f"Error opening Instagram for manual login: {e}")
            return {
                "success": False,
                "error": "browser_open_failed",
                "message": f"Failed to open browser: {str(e)}"
            }

    def get_login_status_and_capture_session(self) -> Dict[str, Any]:
        """Check login status and capture session data if logged in"""
        try:
            if not self.driver:
                return {
                    "success": False,
                    "error": "no_browser",
                    "message": "No browser session active"
                }
            
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            # Check if we're logged in by looking for feed/home indicators
            if any(path in current_url for path in ['/feed/', '/home/', '/?']) and 'instagram.com' in current_url:
                logger.info("✅ User appears to be logged in")
                
                # Try to extract user data
                user_data = asyncio.run(self._extract_user_data())
                
                # Get cookies for session persistence
                cookies = self.driver.get_cookies()
                
                self._take_screenshot("login_success_captured")
                
                return {
                    "success": True,
                    "logged_in": True,
                    "message": "Successfully logged in",
                    "user_data": user_data,
                    "session_cookies": cookies,
                    "current_url": current_url
                }
            
            # Check if still on login page or challenge page
            elif any(indicator in current_url for indicator in ['login', 'challenge', 'checkpoint', 'verify']):
                page_source = self.driver.page_source.lower()
                
                # Check for specific challenge indicators
                if any(challenge in current_url for challenge in ['challenge', 'checkpoint', 'verify']):
                    challenge_info = asyncio.run(self._analyze_challenge_page())
                    return {
                        "success": True,
                        "logged_in": False,
                        "status": "challenge_required",
                        "message": "Challenge verification required",
                        "challenge_info": challenge_info,
                        "current_url": current_url
                    }
                
                # Still on login page
                return {
                    "success": True,
                    "logged_in": False,
                    "status": "login_incomplete",
                    "message": "Login not completed yet",
                    "current_url": current_url
                }
            
            # Unknown state
            else:
                return {
                    "success": True,
                    "logged_in": False,
                    "status": "unknown",
                    "message": "Unknown login status",
                    "current_url": current_url
                }
                
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return {
                "success": False,
                "error": "status_check_failed",
                "message": f"Failed to check login status: {str(e)}"
            }

    def _take_screenshot(self, name: str):
        """Take a screenshot for debugging purposes"""
        try:
            if self.driver:
                timestamp = int(time.time())
                filename = f"{name}_{timestamp}.png"
                filepath = os.path.join(self.screenshots_dir, filename)
                self.driver.save_screenshot(filepath)
                logger.info(f"Screenshot saved: {filepath}")
                return filepath
            else:
                logger.warning("Cannot take screenshot: no driver active")
                return None
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return None

    def _find_element_safe(self, selectors: List[str], timeout: int = 5):
        """Safely find an element using multiple selectors"""
        try:
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        element = WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        element = WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    if element:
                        return element
                except TimeoutException:
                    continue
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            return None
        except Exception as e:
            logger.debug(f"Error in _find_element_safe: {e}")
            return None

    def _find_elements_safe(self, selectors: List[str], timeout: int = 5):
        """Safely find elements using multiple selectors"""
        try:
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        return elements
                except Exception as e:
                    logger.debug(f"Error with selector {selector}: {e}")
                    continue
            return []
        except Exception as e:
            logger.debug(f"Error in _find_elements_safe: {e}")
            return []

    async def _click_safe(self, element, timeout: int = 3):
        """Safely click an element with retries"""
        try:
            if element and element.is_displayed() and element.is_enabled():
                # Try normal click first
                try:
                    element.click()
                    return True
                except ElementClickInterceptedException:
                    # Try JavaScript click if normal click fails
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as e:
                    logger.debug(f"Click failed: {e}")
                    return False
            return False
        except Exception as e:
            logger.debug(f"Error in _click_safe: {e}")
            return False
