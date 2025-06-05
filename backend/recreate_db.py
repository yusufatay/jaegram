#!/usr/bin/env python
import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import Base from models.py (which contains all your table definitions)
try:
    from models import Base
    logger.info("Successfully imported Base from models")
except ImportError as e:
    logger.error(f"Could not import Base from models: {e}")
    sys.exit(1)

def recreate_database():
    """Recreate all tables in the database based on current SQLAlchemy models."""
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    logger.info(f"Using database URL: {DATABASE_URL}")
    
    connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    
    try:
        engine = create_engine(DATABASE_URL, connect_args=connect_args)
        logger.info("Connected to database")
        
        # Option to drop all existing tables
        if "--drop" in sys.argv:
            logger.warning("Dropping all tables...")
            
            # For PostgreSQL, use CASCADE to handle foreign key constraints
            if DATABASE_URL.startswith("postgresql"):
                with engine.connect() as conn:
                    # Get all table names first
                    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
                    tables = [row[0] for row in result]
                    
                    # Drop each table with CASCADE
                    for table_name in tables:
                        try:
                            conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                            logger.info(f"Dropped table: {table_name}")
                        except Exception as e:
                            logger.warning(f"Could not drop table {table_name}: {e}")
                    
                    conn.commit()
            else:
                Base.metadata.drop_all(bind=engine)
            
            logger.info("All tables dropped successfully")
        
        # Create tables based on current models
        logger.info("Creating tables based on models...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
        
        # For PostgreSQL, let's list the tables we just created
        if DATABASE_URL.startswith("postgresql"):
            with engine.connect() as conn:
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
                tables = [row[0] for row in result]
                logger.info(f"Tables in database: {', '.join(tables)}")
                
                # Show columns in the users table
                result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users'"))
                columns = [(row[0], row[1]) for row in result]
                logger.info(f"Columns in users table: {columns}")
        
        return True
    except SQLAlchemyError as e:
        logger.error(f"Error recreating database: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error recreating database: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting database recreation process...")
    success = recreate_database()
    if success:
        logger.info("Database recreation process completed successfully")
        sys.exit(0)
    else:
        logger.error("Database recreation process failed")
        sys.exit(1)
