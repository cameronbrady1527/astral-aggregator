#!/usr/bin/env python3
"""
Test Ultra-Fast Content Detector
================================

This script tests the new ultra-fast content detector with massive concurrency
and connection pooling to verify Phase 1 optimizations are working correctly.

Usage:
    python scripts/test_ultra_fast_content_detector.py
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.utils.config import ConfigManager
from app.crawler.content_detector import ContentDetector


async def test_ultra_fast_content_detector():
    """Test the ultra-fast content detector with Waverley site."""
    
    print("Testing Ultra-Fast Content Detector")
    print("=" * 50)
    
    # Load configuration
    config = ConfigManager()
    site_config = config.get_site('waverley_gov')
    
    if not site_config:
        print("Error: Could not find waverley_gov site configuration")
        return
    
    print(f"Site: {site_config.name}")
    print(f"URL: {site_config.url}")
    print(f"Max concurrent requests: {getattr(site_config, 'max_concurrent_requests', 500)}")
    print(f"Connection pool size: {getattr(site_config, 'connection_pool_size', 1000)}")
    print(f"Batch size: {getattr(site_config, 'batch_size', 1000)}")
    print(f"Ultra-fast timeout: {getattr(site_config, 'ultra_fast_timeout', 5)}s")
    print(f"Max content pages: {getattr(site_config, 'max_content_pages', 0)}")
    print()
    
    # Create content detector
    content_detector = ContentDetector(site_config)
    
    try:
        print("Starting ultra-fast content detection...")
        start_time = time.time()
        
        # Get current state (this will use the ultra-fast methods)
        current_state = await content_detector.get_current_state()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Display results
        print("\nResults:")
        print("-" * 30)
        print(f"Total time: {total_time:.2f} seconds")
        print(f"URLs checked: {len(current_state.get('urls_checked', []))}")
        print(f"Content hashes: {len(current_state.get('content_hashes', {}))}")
        print(f"Success rate: {(len(current_state.get('content_hashes', {})) / len(current_state.get('urls_checked', [])) * 100):.1f}%")
        
        if current_state.get('urls_checked'):
            urls_per_second = len(current_state.get('urls_checked', [])) / total_time
            print(f"Speed: {urls_per_second:.1f} URLs/second")
        
        # Show some sample content hashes
        content_hashes = current_state.get('content_hashes', {})
        if content_hashes:
            print(f"\nSample content hashes:")
            for i, (url, hash_data) in enumerate(list(content_hashes.items())[:5]):
                if isinstance(hash_data, dict):
                    hash_value = hash_data.get('hash', 'N/A')
                    status = hash_data.get('status', 'unknown')
                else:
                    hash_value = str(hash_data)
                    status = 'legacy'
                print(f"  {i+1}. {url[:60]}... -> {hash_value[:20]}... ({status})")
        
        # Performance analysis
        print(f"\nPerformance Analysis:")
        print("-" * 30)
        if total_time < 30:
            print("✅ EXCELLENT: Completed in under 30 seconds")
        elif total_time < 60:
            print("✅ GOOD: Completed in under 1 minute")
        elif total_time < 300:
            print("⚠️  ACCEPTABLE: Completed in under 5 minutes")
        else:
            print("❌ SLOW: Took more than 5 minutes")
        
        if content_hashes and current_state.get('urls_checked'):
            success_rate = len(content_hashes) / len(current_state.get('urls_checked', [])) * 100
            if success_rate > 90:
                print("✅ EXCELLENT: Success rate over 90%")
            elif success_rate > 80:
                print("✅ GOOD: Success rate over 80%")
            elif success_rate > 70:
                print("⚠️  ACCEPTABLE: Success rate over 70%")
            else:
                print("❌ POOR: Success rate under 70%")
        
        # Clean up
        await content_detector.close()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


async def test_with_different_concurrency_levels():
    """Test different concurrency levels to find optimal settings."""
    
    print("\n" + "=" * 50)
    print("Testing Different Concurrency Levels")
    print("=" * 50)
    
    config = ConfigManager()
    site_config = config.get_site('waverley_gov')
    
    if not site_config:
        print("Error: Could not find waverley_gov site configuration")
        return
    
    # Test different concurrency levels
    concurrency_levels = [50, 100, 250, 500]
    
    for max_concurrent in concurrency_levels:
        print(f"\nTesting with {max_concurrent} concurrent requests...")
        
        # Temporarily modify the site config
        original_max_concurrent = getattr(site_config, 'max_concurrent_requests', 500)
        site_config.max_concurrent_requests = max_concurrent
        
        content_detector = ContentDetector(site_config)
        
        try:
            start_time = time.time()
            current_state = await content_detector.get_current_state()
            end_time = time.time()
            
            total_time = end_time - start_time
            urls_checked = len(current_state.get('urls_checked', []))
            content_hashes = len(current_state.get('content_hashes', {}))
            
            if urls_checked > 0:
                urls_per_second = urls_checked / total_time
                success_rate = (content_hashes / urls_checked * 100) if urls_checked > 0 else 0
                
                print(f"  Time: {total_time:.2f}s")
                print(f"  URLs: {urls_checked}")
                print(f"  Success: {content_hashes}")
                print(f"  Speed: {urls_per_second:.1f} URLs/s")
                print(f"  Success rate: {success_rate:.1f}%")
            
            await content_detector.close()
            
        except Exception as e:
            print(f"  Error: {e}")
        
        # Restore original setting
        site_config.max_concurrent_requests = original_max_concurrent


if __name__ == "__main__":
    # Run the main test
    asyncio.run(test_ultra_fast_content_detector())
    
    # Run concurrency level tests
    asyncio.run(test_with_different_concurrency_levels()) 