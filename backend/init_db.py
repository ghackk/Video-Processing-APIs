#!/usr/bin/env python3
"""
Database initialization script for Dripple Video Processing Backend
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.config.database import engine, Base
from app.config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with all tables"""
    try:
        logger.info("🔄 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
        # Create directories if they don't exist
        Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(settings.processed_dir).mkdir(parents=True, exist_ok=True)
        Path("assets/fonts").mkdir(parents=True, exist_ok=True)
        
        logger.info("✅ Directories created successfully!")
        logger.info(f"📁 Upload directory: {settings.upload_dir}")
        logger.info(f"📁 Processed directory: {settings.processed_dir}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
