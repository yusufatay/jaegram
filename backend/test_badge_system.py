#!/usr/bin/env python3
"""
Comprehensive Badge System Integration Test
Tests all aspects of the enhanced badge system integration.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models import SessionLocal
from backend.models import User, Task, TaskStatus, Badge, UserBadge, CoinTransaction, CoinTransactionType
from enhanced_badge_system import get_enhanced_badge_system
from enhanced_notifications import notification_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BadgeSystemTester:
    def __init__(self):
        self.db = SessionLocal()
        self.badge_system = get_enhanced_badge_system(SessionLocal, notification_service)
        
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    async def test_badge_initialization(self):
        """Test badge system initialization"""
        logger.info("🎯 Testing badge initialization...")
        
        try:
            # Initialize badges
            result = self.badge_system.initialize_badges(self.db)
            
            if result['success']:
                logger.info(f"✅ Badge initialization successful: {result['badges_added']} added, {result['badges_updated']} updated")
                return True
            else:
                logger.error(f"❌ Badge initialization failed: {result['message']}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Badge initialization error: {e}")
            return False
    
    async def test_badge_categories(self):
        """Test badge categories functionality"""
        logger.info("📂 Testing badge categories...")
        
        try:
            categories = self.badge_system._get_badge_categories()
            
            if categories:
                logger.info(f"✅ Found {len(categories)} badge categories")
                for name, info in categories.items():
                    logger.info(f"   • {info['name']}: {info['description']}")
                return True
            else:
                logger.error("❌ No badge categories found")
                return False
                
        except Exception as e:
            logger.error(f"❌ Badge categories test error: {e}")
            return False
    
    async def test_user_badge_checking(self):
        """Test badge checking for a user"""
        logger.info("👤 Testing user badge checking...")
        
        try:
            # Get or create a test user
            test_user = self.db.query(User).filter(User.username == "test_badge_user").first()
            
            if not test_user:
                logger.info("Creating test user for badge testing...")
                test_user = User(
                    username="test_badge_user",
                    email="test_badge@example.com",
                    hashed_password="test_hash",
                    coin_balance=1000,
                    instagram_followers=500,
                    instagram_username="test_insta"
                )
                self.db.add(test_user)
                self.db.commit()
                self.db.refresh(test_user)
            
            # Test badge checking
            result = await self.badge_system.check_and_award_badges(test_user.id)
            
            if result['success']:
                new_badges = result.get('new_badges', [])
                logger.info(f"✅ Badge checking successful: {len(new_badges)} new badges awarded")
                
                for badge in new_badges:
                    logger.info(f"   🏆 Awarded: {badge['name']}")
                    
                return True
            else:
                logger.error(f"❌ Badge checking failed: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ User badge checking error: {e}")
            return False
    
    async def test_task_completion_badges(self):
        """Test badge awarding for task completion"""
        logger.info("📋 Testing task completion badge awarding...")
        
        try:
            # Get test user
            test_user = self.db.query(User).filter(User.username == "test_badge_user").first()
            
            if not test_user:
                logger.error("❌ Test user not found")
                return False
            
            # Create some completed tasks for testing
            initial_tasks = self.db.query(Task).filter(
                Task.user_id == test_user.id,
                Task.status == TaskStatus.completed
            ).count()
            
            logger.info(f"User has {initial_tasks} completed tasks")
            
            # Create a few test tasks
            for i in range(3):
                task = Task(
                    user_id=test_user.id,
                    platform="instagram",
                    task_type="follow",
                    target_username=f"test_target_{i}",
                    reward_coins=50,
                    status=TaskStatus.completed,
                    completed_at=datetime.utcnow()
                )
                self.db.add(task)
            
            self.db.commit()
            
            # Check for badges after task completion
            result = await self.badge_system.check_and_award_badges(test_user.id)
            
            if result['success']:
                new_badges = result.get('new_badges', [])
                logger.info(f"✅ Task completion badge test successful: {len(new_badges)} badges")
                return True
            else:
                logger.error(f"❌ Task completion badge test failed: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Task completion badge test error: {e}")
            return False
    
    async def test_badge_progress(self):
        """Test badge progress tracking"""
        logger.info("📊 Testing badge progress tracking...")
        
        try:
            # Get test user
            test_user = self.db.query(User).filter(User.username == "test_badge_user").first()
            
            if not test_user:
                logger.error("❌ Test user not found")
                return False
            
            # Get user's badge progress
            progress = await self.badge_system.get_user_badge_progress(test_user.id)
            
            if progress['success']:
                stats = progress['progress']
                logger.info(f"✅ Badge progress retrieved successfully")
                logger.info(f"   📈 Total badges: {stats['total_badges']}")
                logger.info(f"   🏆 Earned badges: {stats['earned_badges']}")
                logger.info(f"   📊 Progress: {stats['completion_percentage']:.1f}%")
                
                # Show category breakdown
                for category, info in stats['categories'].items():
                    earned = info['earned']
                    total = info['total']
                    percentage = info['percentage']
                    logger.info(f"   • {category}: {earned}/{total} ({percentage:.1f}%)")
                
                return True
            else:
                logger.error(f"❌ Badge progress test failed: {progress.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Badge progress test error: {e}")
            return False
    
    async def test_badge_leaderboard(self):
        """Test badge leaderboard functionality"""
        logger.info("🏅 Testing badge leaderboard...")
        
        try:
            # Get badge leaderboard
            leaderboard = await self.badge_system.get_badge_leaderboard(limit=10)
            
            if leaderboard['success']:
                users = leaderboard['users']
                logger.info(f"✅ Badge leaderboard retrieved: {len(users)} users")
                
                for i, user in enumerate(users[:5], 1):
                    username = user.get('username', 'Unknown')
                    badge_count = user.get('total_badges', 0)
                    categories = user.get('category_counts', {})
                    logger.info(f"   {i}. {username}: {badge_count} badges")
                
                return True
            else:
                logger.error(f"❌ Badge leaderboard test failed: {leaderboard.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Badge leaderboard test error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all badge system tests"""
        logger.info("🚀 Starting comprehensive badge system tests...")
        
        tests = [
            ("Badge Initialization", self.test_badge_initialization),
            ("Badge Categories", self.test_badge_categories),
            ("User Badge Checking", self.test_user_badge_checking),
            ("Task Completion Badges", self.test_task_completion_badges),
            ("Badge Progress", self.test_badge_progress),
            ("Badge Leaderboard", self.test_badge_leaderboard),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"🧪 Running: {test_name}")
            logger.info('='*50)
            
            try:
                result = await test_func()
                results[test_name] = result
                status = "✅ PASSED" if result else "❌ FAILED"
                logger.info(f"{status}: {test_name}")
            except Exception as e:
                logger.error(f"❌ ERROR in {test_name}: {e}")
                results[test_name] = False
        
        # Show summary
        logger.info(f"\n{'='*60}")
        logger.info("📋 TEST SUMMARY")
        logger.info('='*60)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{status}: {test_name}")
        
        logger.info(f"\n🎯 Overall Result: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! Badge system integration is working correctly.")
        else:
            logger.warning(f"⚠️  {total - passed} tests failed. Please check the issues above.")
        
        return passed == total

async def main():
    """Main function"""
    print("🎖️  Badge System Integration Test Suite")
    print("="*50)
    
    tester = BadgeSystemTester()
    
    try:
        success = await tester.run_all_tests()
        
        if success:
            print("\n🎉 All badge system tests completed successfully!")
            print("✅ Badge system integration is ready for production!")
        else:
            print("\n⚠️  Some tests failed. Please review the logs above.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Test suite error: {e}")
        sys.exit(1)
    finally:
        # Cleanup
        if hasattr(tester, 'db'):
            tester.db.close()

if __name__ == "__main__":
    asyncio.run(main())
