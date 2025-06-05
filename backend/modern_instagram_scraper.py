"""
Modern Instagram Profile Scraper
Updated to work with Instagram's current page structure
"""

import requests
import json
import re
import logging
from typing import Dict, Optional, Any
from urllib.parse import unquote
import time

logger = logging.getLogger(__name__)

class ModernInstagramScraper:
    """Modern Instagram scraper that works with current Instagram structure"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Set up modern browser headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        })
        
        # Configure session to handle redirects and cookies
        self.session.max_redirects = 5
    
    async def scrape_profile(self, username: str) -> Dict[str, Any]:
        """
        Scrape Instagram profile using modern methods
        """
        try:
            logger.info(f"[MODERN_SCRAPER] Starting scrape for {username}")
            
            url = f"https://www.instagram.com/{username}/"
            
            # Make request with retry logic
            response = self._make_request_with_retry(url)
            if not response:
                return {"success": False, "message": "Failed to fetch profile page"}
            
            # Initialize profile data
            profile_data = {
                "username": username,
                "full_name": "",
                "bio": "",
                "profile_pic_url": "",
                "followers_count": 0,
                "following_count": 0,
                "media_count": 0,
                "is_private": False,
                "is_verified": False,
                "external_url": "",
                "post_images": []
            }
            
            # Method 1: Extract from script tags containing JSON data
            json_data = self._extract_json_from_scripts(response.text)
            if json_data:
                self._extract_from_json_data(json_data, profile_data)
            
            # Method 2: Extract profile picture from img tags and meta tags
            if not profile_data["profile_pic_url"]:
                profile_pic = self._extract_profile_picture_modern(response.text, username)
                if profile_pic:
                    profile_data["profile_pic_url"] = profile_pic
            
            # Method 3: Extract basic info from meta tags
            self._extract_from_meta_tags(response.text, profile_data)
            
            # Method 4: Extract counts from page content
            self._extract_counts_from_content(response.text, profile_data)
            
            # Check if account is private
            if "This Account is Private" in response.text or "Bu Hesap Gizli" in response.text:
                profile_data["is_private"] = True
            
            # Check if account is verified  
            if self._check_verification(response.text):
                profile_data["is_verified"] = True
            
            logger.info(f"[MODERN_SCRAPER] Successfully scraped {username}: {profile_data['media_count']} posts, pic_url: {'✓' if profile_data['profile_pic_url'] else '✗'}")
            
            return {
                "success": True,
                "profile": profile_data
            }
            
        except Exception as e:
            logger.error(f"[MODERN_SCRAPER] Error scraping {username}: {e}")
            return {"success": False, "message": f"Scraping error: {str(e)}"}
    
    def _make_request_with_retry(self, url: str, max_retries: int = 3) -> Optional[requests.Response]:
        """Make request with retry logic and proper decompression"""
        import gzip
        import io
        
        for attempt in range(max_retries):
            try:
                # Make request with explicit headers for better compression handling
                headers = self.session.headers.copy()
                headers['Accept-Encoding'] = 'gzip, deflate'
                
                response = self.session.get(url, timeout=15, headers=headers)
                
                if response.status_code == 200:
                    # Log response details for debugging
                    logger.info(f"[MODERN_SCRAPER] Response length: {len(response.content)} bytes")
                    logger.info(f"[MODERN_SCRAPER] Content encoding: {response.headers.get('Content-Encoding', 'none')}")
                    
                    # Handle potential compression issues
                    content = response.content
                    text_content = None
                    
                    # Check if content is gzip compressed but not properly decompressed
                    if content.startswith(b'\x1f\x8b'):  # gzip magic number
                        try:
                            logger.info("[MODERN_SCRAPER] Manually decompressing gzip content")
                            decompressed = gzip.decompress(content)
                            text_content = decompressed.decode('utf-8')
                            logger.info(f"[MODERN_SCRAPER] Manually decompressed: {len(text_content)} chars")
                        except Exception as e:
                            logger.warning(f"[MODERN_SCRAPER] Manual gzip decompression failed: {e}")
                            text_content = response.text
                    else:
                        # Use normal response text
                        text_content = response.text
                    
                    # Validate content
                    if text_content and len(text_content) > 100:
                        # Check for HTML content
                        if any(tag in text_content[:1000].lower() for tag in ['<html', '<head', '<body', '<meta']):
                            logger.info(f"[MODERN_SCRAPER] Valid HTML content received: {len(text_content)} chars")
                            
                            # Create a modified response with proper content if needed
                            if text_content != response.text:
                                response._content = text_content.encode('utf-8')
                                response.encoding = 'utf-8'
                            
                            return response
                        else:
                            logger.warning("[MODERN_SCRAPER] Content doesn't appear to be valid HTML")
                    else:
                        logger.warning(f"[MODERN_SCRAPER] Content too short or empty: {len(text_content if text_content else '')}")
                        
                elif response.status_code == 429:  # Rate limited
                    wait_time = 2 ** attempt
                    logger.warning(f"[MODERN_SCRAPER] Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.warning(f"[MODERN_SCRAPER] HTTP {response.status_code} on attempt {attempt + 1}")
                    
            except Exception as e:
                logger.warning(f"[MODERN_SCRAPER] Request failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        
        return None
    
    def _extract_json_from_scripts(self, html: str) -> Optional[Dict]:
        """Extract JSON data from script tags"""
        try:
            # Look for various patterns where Instagram stores data
            patterns = [
                r'window\._sharedData\s*=\s*({.*?});',
                r'window\.__additionalDataLoaded\([^,]+,\s*({.*?})\);',
                r'"ProfilePage"\s*:\s*\[({.*?})\]',
                r'"graphql"\s*:\s*({.*?"user".*?})',
                r'data-shared-data="([^"]*)"'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    try:
                        # Handle HTML encoded JSON
                        if pattern.endswith('"'):
                            match = unquote(match)
                        
                        data = json.loads(match)
                        if self._validate_instagram_data(data):
                            logger.info("[MODERN_SCRAPER] Found valid JSON data in script")
                            return data
                    except:
                        continue
            
            logger.debug("[MODERN_SCRAPER] No valid JSON data found in scripts")
            return None
            
        except Exception as e:
            logger.debug(f"[MODERN_SCRAPER] JSON extraction error: {e}")
            return None
    
    def _validate_instagram_data(self, data: Dict) -> bool:
        """Validate if JSON data contains Instagram profile information"""
        if not isinstance(data, dict):
            return False
        
        # Check for various Instagram data structures
        indicators = [
            "entry_data" in data,
            "ProfilePage" in str(data),
            "graphql" in data and "user" in str(data),
            "user" in data and "username" in str(data),
            "profile_pic_url" in str(data)
        ]
        
        return any(indicators)
    
    def _extract_from_json_data(self, data: Dict, profile_data: Dict):
        """Extract profile information from JSON data"""
        try:
            # Try different data structures
            user_data = None
            
            # Method 1: entry_data.ProfilePage structure
            if "entry_data" in data and "ProfilePage" in data["entry_data"]:
                profile_pages = data["entry_data"]["ProfilePage"]
                if profile_pages and len(profile_pages) > 0:
                    graphql = profile_pages[0].get("graphql", {})
                    user_data = graphql.get("user", {})
            
            # Method 2: Direct graphql.user structure
            elif "graphql" in data and "user" in data["graphql"]:
                user_data = data["graphql"]["user"]
            
            # Method 3: Direct user structure
            elif "user" in data:
                user_data = data["user"]
            
            if user_data:
                self._extract_user_data(user_data, profile_data)
                logger.info("[MODERN_SCRAPER] Successfully extracted data from JSON")
            
        except Exception as e:
            logger.debug(f"[MODERN_SCRAPER] JSON data extraction error: {e}")
    
    def _extract_user_data(self, user_data: Dict, profile_data: Dict):
        """Extract user data from Instagram user object"""
        try:
            # Basic profile info
            profile_data["full_name"] = user_data.get("full_name", "")
            profile_data["bio"] = user_data.get("biography", "")
            profile_data["is_private"] = user_data.get("is_private", False)
            profile_data["is_verified"] = user_data.get("is_verified", False)
            profile_data["external_url"] = user_data.get("external_url", "")
            
            # Profile picture (try different qualities)
            profile_pic_urls = [
                user_data.get("profile_pic_url_hd"),
                user_data.get("profile_pic_url"),
                user_data.get("profile_picture_url")
            ]
            
            for pic_url in profile_pic_urls:
                if pic_url and pic_url.startswith("http"):
                    profile_data["profile_pic_url"] = pic_url
                    break
            
            # Counts from different possible structures
            counts_sources = [
                # Standard structure
                {
                    "followers": user_data.get("edge_followed_by", {}).get("count", 0),
                    "following": user_data.get("edge_follow", {}).get("count", 0),
                    "media": user_data.get("edge_owner_to_timeline_media", {}).get("count", 0)
                },
                # Alternative structure
                {
                    "followers": user_data.get("follower_count", 0),
                    "following": user_data.get("following_count", 0),
                    "media": user_data.get("media_count", 0)
                }
            ]
            
            for counts in counts_sources:
                if any(counts.values()):
                    profile_data["followers_count"] = counts["followers"]
                    profile_data["following_count"] = counts["following"]
                    profile_data["media_count"] = counts["media"]
                    break
            
        except Exception as e:
            logger.debug(f"[MODERN_SCRAPER] User data extraction error: {e}")
    
    def _extract_profile_picture_modern(self, html: str, username: str) -> Optional[str]:
        """Extract profile picture using modern methods"""
        try:
            # Method 1: Look for high-resolution profile pictures in meta tags
            meta_patterns = [
                r'<meta property="og:image" content="([^"]*)"',
                r'<meta name="twitter:image" content="([^"]*)"',
                r'<link rel="icon" href="([^"]*)"'
            ]
            
            for pattern in meta_patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    if ("scontent" in match or "cdninstagram" in match) and match.startswith("http"):
                        logger.info(f"[MODERN_SCRAPER] Found profile picture via meta tag: {match}")
                        return match
            
            # Method 2: Look for profile pictures in img tags
            img_patterns = [
                rf'<img[^>]*alt="[^"]*{re.escape(username)}[^"]*"[^>]*src="([^"]*)"',
                r'<img[^>]*alt="[^"]*profile picture[^"]*"[^>]*src="([^"]*)"',
                r'<img[^>]*src="([^"]*)"[^>]*alt="[^"]*profile picture[^"]*"'
            ]
            
            for pattern in img_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    if ("scontent" in match or "cdninstagram" in match) and match.startswith("http"):
                        logger.info(f"[MODERN_SCRAPER] Found profile picture via img tag: {match}")
                        return match
            
            # Method 3: Look for any Instagram CDN images (fallback)
            cdn_pattern = r'https://[^"]*(?:scontent|cdninstagram)[^"]*\.(?:jpg|jpeg|png|webp)'
            matches = re.findall(cdn_pattern, html)
            
            # Filter out obvious non-profile images
            for match in matches:
                if not any(skip in match.lower() for skip in ['story', 'highlight', 'reel', 'post']):
                    logger.info(f"[MODERN_SCRAPER] Found profile picture via CDN fallback: {match}")
                    return match
            
            logger.debug(f"[MODERN_SCRAPER] No profile picture found for {username}")
            return None
            
        except Exception as e:
            logger.debug(f"[MODERN_SCRAPER] Profile picture extraction error: {e}")
            return None
    
    def _extract_from_meta_tags(self, html: str, profile_data: Dict):
        """Extract information from meta tags"""
        try:
            # Description meta tag often contains follower/following counts
            desc_pattern = r'<meta property="og:description" content="([^"]*)"'
            desc_matches = re.findall(desc_pattern, html)
            
            for desc in desc_matches:
                # Try to parse counts from description
                count_patterns = [
                    r'([\d,\.KM]+)\s*Followers?,\s*([\d,\.KM]+)\s*Following?,\s*([\d,\.KM]+)\s*Posts?',
                    r'([\d,\.KM]+)\s*takipçi,\s*([\d,\.KM]+)\s*takip,\s*([\d,\.KM]+)\s*gönderi',
                    r'([\d,\.KM]+)\s*followers?,\s*([\d,\.KM]+)\s*following?,\s*([\d,\.KM]+)\s*posts?'
                ]
                
                for pattern in count_patterns:
                    match = re.search(pattern, desc, re.IGNORECASE)
                    if match:
                        profile_data["followers_count"] = self._parse_count(match.group(1))
                        profile_data["following_count"] = self._parse_count(match.group(2))
                        profile_data["media_count"] = self._parse_count(match.group(3))
                        logger.info(f"[MODERN_SCRAPER] Extracted counts from meta: {profile_data['followers_count']} followers")
                        return
            
        except Exception as e:
            logger.debug(f"[MODERN_SCRAPER] Meta tag extraction error: {e}")
    
    def _extract_counts_from_content(self, html: str, profile_data: Dict):
        """Extract counts from page content"""
        try:
            # Look for count patterns in the HTML content
            count_patterns = [
                r'(\d+(?:,\d{3})*)\s*(?:posts?|gönderi)',
                r'(\d+(?:,\d{3})*)\s*(?:followers?|takipçi)',
                r'(\d+(?:,\d{3})*)\s*(?:following?|takip)'
            ]
            
            for i, pattern in enumerate(count_patterns):
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    count = self._parse_count(matches[0])
                    if i == 0:
                        profile_data["media_count"] = max(profile_data["media_count"], count)
                    elif i == 1:
                        profile_data["followers_count"] = max(profile_data["followers_count"], count)
                    elif i == 2:
                        profile_data["following_count"] = max(profile_data["following_count"], count)
            
        except Exception as e:
            logger.debug(f"[MODERN_SCRAPER] Content extraction error: {e}")
    
    def _check_verification(self, html: str) -> bool:
        """Check if account is verified"""
        verification_indicators = [
            'verified',
            'Verified',
            'class="coreSpriteVerifiedBadge"',
            'aria-label="Verified"',
            'title="Verified"'
        ]
        
        return any(indicator in html for indicator in verification_indicators)
    
    def _parse_count(self, count_str: str) -> int:
        """Parse count string like '1.2K', '2.5M' to integer"""
        if not count_str:
            return 0
        
        # Remove commas and convert to uppercase
        count_str = count_str.replace(",", "").replace(".", "").upper()
        
        try:
            if "K" in count_str:
                return int(float(count_str.replace("K", "")) * 1000)
            elif "M" in count_str:
                return int(float(count_str.replace("M", "")) * 1000000)
            else:
                return int(re.sub(r'[^\d]', '', count_str) or 0)
        except:
            return 0

# Global instance
modern_instagram_scraper = ModernInstagramScraper()

def scrape_instagram_profile_modern(username: str) -> Dict[str, Any]:
    """
    Modern Instagram profile scraper function
    """
    return modern_instagram_scraper.scrape_profile(username)
