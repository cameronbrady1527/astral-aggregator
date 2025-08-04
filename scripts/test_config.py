#!/usr/bin/env python3
"""
Test script to verify configuration is loaded correctly.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.config import ConfigManager

def test_config():
    """Test if configuration is loaded correctly."""
    print("🔍 TESTING CONFIGURATION LOADING")
    print("=" * 40)
    
    config = ConfigManager()
    
    # Test Judiciary UK
    judiciary = config.get_site('judiciary_uk')
    if judiciary:
        print(f"✅ Judiciary UK config loaded")
        print(f"   max_content_pages: {getattr(judiciary, 'max_content_pages', 'NOT SET')}")
        print(f"   enable_content_detection: {getattr(judiciary, 'enable_content_detection', 'NOT SET')}")
    else:
        print("❌ Judiciary UK config not found")
    
    # Test Waverley
    waverley = config.get_site('waverley_gov')
    if waverley:
        print(f"✅ Waverley config loaded")
        print(f"   max_content_pages: {getattr(waverley, 'max_content_pages', 'NOT SET')}")
        print(f"   enable_content_detection: {getattr(waverley, 'enable_content_detection', 'NOT SET')}")
    else:
        print("❌ Waverley config not found")

if __name__ == "__main__":
    test_config() 