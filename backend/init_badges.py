#!/usr/bin/env python3
"""
Badge System Initialization Script
This script initializes all badge definitions in the database.
"""

import sys
import os
import logging
from datetime import datetime

# Add the backend directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models import SessionLocal
from enhanced_badge_system import get_enhanced_badge_system
from enhanced_notifications import notification_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_badge_system():
    """Initialize the badge system with all badge definitions"""
    logger.info("🚀 Starting badge system initialization...")
    
    try:
        # Create database session
        db = SessionLocal()
        
        # Get enhanced badge system instance
        badge_system = get_enhanced_badge_system(SessionLocal, notification_service)
        
        # Initialize all badges
        logger.info("📋 Initializing badge definitions...")
        result = badge_system.initialize_badges(db)
        
        logger.info(f"✅ Badge initialization completed!")
        logger.info(f"📊 Results: {result}")
        
        # Display summary
        if result.get('success'):
            badges_added = result.get('badges_added', 0)
            badges_updated = result.get('badges_updated', 0)
            total_badges = result.get('total_badges', 0)
            
            print("\n" + "="*60)
            print("🎖️  BADGE SYSTEM INITIALIZATION COMPLETE")
            print("="*60)
            print(f"📈 Badges Added: {badges_added}")
            print(f"🔄 Badges Updated: {badges_updated}")
            print(f"🏆 Total Badges: {total_badges}")
            print("="*60)
            
            # Show badge categories
            logger.info("📂 Available badge categories:")
            categories = badge_system._get_badge_categories()
            for category_name, category_info in categories.items():
                print(f"   • {category_info['name']}: {category_info['description']}")
                
        else:
            logger.error(f"❌ Badge initialization failed: {result.get('message', 'Unknown error')}")
            
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Error during badge initialization: {e}")
        raise

def verify_badge_system():
    """Verify that the badge system is working correctly"""
    logger.info("🔍 Verifying badge system...")
    
    try:
        # Create database session
        db = SessionLocal()
        
        # Get enhanced badge system instance
        badge_system = get_enhanced_badge_system(SessionLocal, notification_service)
        
        # Get all badges from database
        from models import Badge
        badges = db.query(Badge).all()
        
        logger.info(f"✅ Found {len(badges)} badges in database")
        
        # Group by category
        category_counts = {}
        for badge in badges:
            category = badge.category
            category_counts[category] = category_counts.get(category, 0) + 1
            
        print("\n📊 Badges by Category:")
        for category, count in category_counts.items():
            print(f"   • {category}: {count} badges")
        
        # Test badge categories function
        categories = badge_system._get_badge_categories()
        logger.info(f"✅ Badge system supports {len(categories)} categories")
        
        db.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Badge system verification failed: {e}")
        return False

def show_usage():
    """Show usage instructions"""
    print("""
🎖️  Badge System Initialization Script

USAGE:
    python init_badges.py [command]

COMMANDS:
    init        Initialize all badge definitions (default)
    verify      Verify badge system is working
    help        Show this help message

EXAMPLES:
    python init_badges.py init       # Initialize badges
    python init_badges.py verify     # Verify system
    python init_badges.py           # Default: initialize badges

NOTE:
    Make sure the database is properly set up and the server is configured
    before running this script.
    """)

def main():
    """Main function"""
    import sys
    
    # Get command from arguments
    command = sys.argv[1] if len(sys.argv) > 1 else 'init'
    
    if command == 'help':
        show_usage()
        return
    elif command == 'verify':
        print("🔍 Verifying Badge System...")
        if verify_badge_system():
            print("✅ Badge system verification passed!")
        else:
            print("❌ Badge system verification failed!")
            sys.exit(1)
    elif command == 'init':
        print("🚀 Initializing Badge System...")
        initialize_badge_system()
        print("✅ Badge system initialization completed!")
        
        # Also verify after initialization
        print("\n🔍 Running verification...")
        if verify_badge_system():
            print("✅ Verification passed!")
        else:
            print("⚠️  Verification had issues, but initialization completed.")
    else:
        print(f"❌ Unknown command: {command}")
        show_usage()
        sys.exit(1)

if __name__ == "__main__":
    main()
