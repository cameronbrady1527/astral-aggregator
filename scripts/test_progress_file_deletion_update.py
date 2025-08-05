#!/usr/bin/env python3
"""
Test script to verify progress file deletion after baseline updates.
"""

import asyncio
import os
import json
import shutil
from datetime import datetime
from pathlib import Path

# Add the app directory to the Python path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.config import ConfigManager
from app.crawler.change_detector import ChangeDetector


async def test_progress_file_deletion_on_update():
    """Test that progress files are deleted after baseline updates."""
    print("🧪 Testing Progress File Deletion After Baseline Updates")
    print("=" * 60)
    
    # Initialize config manager
    config_manager = ConfigManager()
    
    # Test with a small site
    site_config = config_manager.get_site("waverley_gov")
    
    print(f"🔍 Testing with site: {site_config.name}")
    
    # Create a mock progress file to simulate interrupted crawling
    progress_dir = Path("progress")
    progress_dir.mkdir(exist_ok=True)
    
    # Create safe site name
    safe_site_name = site_config.name.lower().replace(" ", "_").replace("-", "_")
    progress_file = progress_dir / f"{safe_site_name}_progress.json"
    
    # Create mock progress data
    mock_progress = {
        "content_hashes": {"https://example.com": {"hash": "test123"}},
        "urls_processed": ["https://example.com"],
        "total_urls": ["https://example.com"],
        "timestamp": datetime.now().isoformat(),
        "site_url": site_config.url
    }
    
    # Save mock progress file
    with open(progress_file, 'w') as f:
        json.dump(mock_progress, f, indent=2)
    
    print(f"📁 Created mock progress file: {progress_file}")
    print(f"📊 Progress file exists: {progress_file.exists()}")
    
    # Initialize change detector
    change_detector = ChangeDetector()
    
    try:
        # Run change detection (this should detect changes and update baseline)
        print(f"\n🔄 Running change detection for {site_config.name}...")
        result = await change_detector.detect_changes_for_site("waverley_gov")
        
        print(f"\n📋 Change detection result:")
        print(f"   Baseline updated: {result.get('baseline_updated', False)}")
        print(f"   Baseline file: {result.get('baseline_file', 'None')}")
        
        # Check if progress file was deleted
        progress_file_exists = progress_file.exists()
        print(f"\n🗑️ Progress file deletion check:")
        print(f"   Progress file exists: {progress_file_exists}")
        
        if not progress_file_exists:
            print("✅ SUCCESS: Progress file was properly deleted after baseline update!")
        else:
            print("❌ FAILURE: Progress file was not deleted after baseline update!")
            
        # Check for any other progress files for this site
        other_progress_files = list(progress_dir.glob(f"{safe_site_name}_progress_*.json"))
        if other_progress_files:
            print(f"⚠️ Found additional progress files: {len(other_progress_files)}")
            for file in other_progress_files:
                print(f"   - {file}")
        else:
            print("✅ No additional progress files found")
            
    except Exception as e:
        print(f"❌ Error during change detection: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up any remaining progress files
        if progress_file.exists():
            progress_file.unlink()
            print(f"🧹 Cleaned up progress file: {progress_file}")
        
        # Clean up any timestamped progress files
        for file in progress_dir.glob(f"{safe_site_name}_progress_*.json"):
            file.unlink()
            print(f"🧹 Cleaned up progress file: {file}")


if __name__ == "__main__":
    asyncio.run(test_progress_file_deletion_on_update()) 