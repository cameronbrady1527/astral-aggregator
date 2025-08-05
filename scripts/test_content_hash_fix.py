#!/usr/bin/env python3
"""
Test Content Hash Fix Script
============================

This script tests the fix for the UnboundLocalError in the content detector
to ensure that content hashes are properly processed and reported.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.crawler.content_detector import ContentDetector
from app.crawler.hybrid_detector import HybridDetector
from app.utils.config import ConfigManager

async def test_content_hash_fix():
    """Test that the content hash fix works correctly."""
    
    print("🧪 Testing Content Hash Fix")
    print("=" * 50)
    
    try:
        # Create config manager
        config_manager = ConfigManager()
        
        # Test with a small site first
        site_config = config_manager.get_site("waverley_gov")
        
        print(f"🔍 Testing Content Detector...")
        content_detector = ContentDetector(site_config)
        
        # Get current state
        current_state = await content_detector.get_current_state()
        
        content_hashes = current_state.get("content_hashes", {})
        total_pages = current_state.get("total_pages", 0)
        
        print(f"✅ Content hashes fetched: {len(content_hashes)}")
        print(f"✅ Total pages reported: {total_pages}")
        
        if content_hashes:
            print("✅ Sample content hashes:")
            for i, (url, hash_data) in enumerate(list(content_hashes.items())[:3]):
                if isinstance(hash_data, dict):
                    hash_value = hash_data.get('hash', 'N/A')[:20]
                else:
                    hash_value = str(hash_data)[:20]
                print(f"   {i+1}. {url[:50]}... -> {hash_value}...")
        else:
            print("⚠️ No content hashes found - this might indicate an issue")
        
        # Test hybrid detector
        print(f"\n🔍 Testing Hybrid Detector...")
        hybrid_detector = HybridDetector(site_config)
        
        # Get current state
        current_state = await hybrid_detector.get_current_state()
        
        sitemap_state = current_state.get("sitemap_state", {})
        content_state = current_state.get("content_state", {})
        
        print(f"✅ Sitemap URLs: {len(sitemap_state.get('urls', []))}")
        
        if content_state:
            content_hashes = content_state.get("content_hashes", {})
            print(f"✅ Content hashes in hybrid: {len(content_hashes)}")
            
            if content_hashes:
                print("✅ Sample hybrid content hashes:")
                for i, (url, hash_data) in enumerate(list(content_hashes.items())[:3]):
                    if isinstance(hash_data, dict):
                        hash_value = hash_data.get('hash', 'N/A')[:20]
                    else:
                        hash_value = str(hash_data)[:20]
                    print(f"   {i+1}. {url[:50]}... -> {hash_value}...")
            else:
                print("⚠️ No content hashes in hybrid state")
        else:
            print("⚠️ No content state in hybrid detector")
        
        print(f"\n✅ Test completed successfully!")
        print(f"✅ UnboundLocalError fix appears to be working")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_content_hash_fix()) 