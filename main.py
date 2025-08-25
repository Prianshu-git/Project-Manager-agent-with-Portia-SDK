#!/usr/bin/env python3
"""
Main entry point for PM Agentic AI System
Coordinates the complete product management workflow with Portia SDK integration
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the PM Agentic AI System"""
    logger.info("🚀 Starting PM Agentic AI System with Portia SDK Integration")
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = ['GOOGLE_API_KEY', 'SLACK_BOT_TOKEN', 'SLACK_APP_TOKEN', 'PORTIA_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.info("Please check your .env file and ensure all required API keys are set")
        return
    
    logger.info("✅ Environment variables configured successfully")
    
    # Import and run the feature selection UI
    try:
        from ui_feature_selection import FeatureSelectionUI, main as ui_main
        logger.info("📋 Loading Feature Selection UI...")
        ui_main()
    except ImportError as e:
        logger.error(f"Failed to import UI module: {e}")
        logger.error("Please ensure all dependencies are installed and modules are available")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
