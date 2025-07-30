# ==============================================================================
# test_change_detection.py — Test script for the change detection system
# ==============================================================================
# Purpose: Test the basic functionality of the change detection system
# Sections: Imports, Test Functions, Main Function
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
import os

# Third-Party -----
from dotenv import load_dotenv

# Internal -----
from app.crawler.change_detector import ChangeDetector
from app.utils.config import ConfigManager

# Load environment variables
load_dotenv()

# ==============================================================================
# Test Functions
# ==============================================================================

async def test_sitemap_detection():
    """Test sitemap-based change detection."""
    print("Testing sitemap-based change detection...")
    
    detector = ChangeDetector()
    
    try:
        results = await detector.detect_changes_for_site("judiciary_uk")
        print(f"Judiciary UK detection completed")
        print(f"Output file: {results.get('output_file', 'N/A')}")
        
        for method, method_result in results.get("methods", {}).items():
            if "error" in method_result:
                print(f"{method}: {method_result['error']}")
            else:
                summary = method_result.get("summary", {})
                print(f"{method}: {summary.get('total_changes', 0)} changes detected")
                
    except Exception as e:
        print(f"Judiciary UK detection failed: {e}")
    
    try:
        results = await detector.detect_changes_for_site("waverley_gov")
        print(f"Waverley Gov detection completed")
        print(f"Output file: {results.get('output_file', 'N/A')}")
        
        for method, method_result in results.get("methods", {}).items():
            if "error" in method_result:
                print(f"{method}: {method_result['error']}")
            else:
                summary = method_result.get("summary", {})
                print(f"{method}: {summary.get('total_changes', 0)} changes detected")
                
    except Exception as e:
        print(f"Waverley Gov detection failed: {e}")


async def test_all_sites():
    """Test detection for all configured sites."""
    print("\nTesting detection for all sites...")
    
    detector = ChangeDetector()
    
    try:
        results = await detector.detect_changes_for_all_sites()
        print(f"All sites detection completed")
        
        for site_id, site_results in results.get("sites", {}).items():
            if "error" in site_results:
                print(f"{site_id}: {site_results['error']}")
            else:
                print(f"{site_id}: Detection completed")
                
    except Exception as e:
        print(f"All sites detection failed: {e}")


def test_configuration():
    """Test configuration loading."""
    print("Testing configuration...")
    
    try:
        config = ConfigManager()
        sites = config.get_active_sites()
        print(f"Configuration loaded successfully")
        print(f"Active sites: {len(sites)}")
        
        for site in sites:
            print(f"   - {site.name}: {site.url}")
        
        # Test API key loading
        firecrawl_config = config.get_firecrawl_config()
        api_key = firecrawl_config.get('api_key')
        if api_key and api_key != '${FIRECRAWL_API_KEY}':
            print(f"Firecrawl API key loaded: {api_key[:10]}...")
        else:
            print(f"Firecrawl API key not found - set FIRECRAWL_API_KEY in .env")
            
    except Exception as e:
        print(f"Configuration test failed: {e}")


def test_json_writer():
    """Test JSON writer functionality."""
    print("\nTesting JSON writer...")
    
    try:
        from app.utils.json_writer import ChangeDetectionWriter
        
        writer = ChangeDetectionWriter()
        
        sample_data = {
            "detection_method": "test",
            "test_data": "This is a test"
        }
        
        output_file = writer.write_changes("test_site", sample_data)
        print(f"JSON writer test completed")
        print(f"Output file: {output_file}")
        
        read_data = writer.read_json_file(output_file)
        print(f"File read successfully: {read_data.get('metadata', {}).get('site_name')}")
        
    except Exception as e:
        print(f"JSON writer test failed: {e}")


async def main():
    """Run all tests."""
    print("Starting change detection system tests...\n")
    
    test_configuration()
    test_json_writer()
    await test_sitemap_detection()
    await test_all_sites()
    
    print("\nAll tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 