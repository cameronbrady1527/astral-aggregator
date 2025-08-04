#!/usr/bin/env python3
"""
Test Adaptive Rate Limiting
===========================

This script tests the adaptive rate limiting feature that dynamically adjusts
concurrency to maintain 100% success rate while maximizing speed.

Usage:
    python scripts/test_adaptive_rate_limiting.py
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


async def test_adaptive_rate_limiting():
    """Test the adaptive rate limiting feature."""
    
    print("Testing Adaptive Rate Limiting")
    print("=" * 50)
    
    # Load configuration
    config = ConfigManager()
    site_config = config.get_site('waverley_gov')
    
    if not site_config:
        print("Error: Could not find waverley_gov site configuration")
        return
    
    print(f"Site: {site_config.name}")
    print(f"URL: {site_config.url}")
    print(f"Adaptive rate limiting: {getattr(site_config, 'adaptive_rate_limiting', True)}")
    print(f"Initial concurrency: {getattr(site_config, 'max_concurrent_requests', 50)}")
    print(f"Min concurrency: {getattr(site_config, 'min_concurrent_requests', 10)}")
    print(f"Success rate threshold: {getattr(site_config, 'success_rate_threshold', 0.95):.1%}")
    print()
    
    # Create content detector
    content_detector = ContentDetector(site_config)
    
    try:
        print("Starting adaptive content detection...")
        start_time = time.time()
        
        # Get current state (this will use adaptive rate limiting)
        current_state = await content_detector.get_current_state()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Display results
        print("\nResults:")
        print("-" * 30)
        print(f"Total time: {total_time:.2f} seconds")
        print(f"URLs checked: {len(current_state.get('urls_checked', []))}")
        print(f"Content hashes: {len(current_state.get('content_hashes', {}))}")
        
        if current_state.get('urls_checked'):
            success_rate = len(current_state.get('content_hashes', {})) / len(current_state.get('urls_checked', []))
            urls_per_second = len(current_state.get('urls_checked', [])) / total_time
            print(f"Success rate: {success_rate:.1%}")
            print(f"Speed: {urls_per_second:.1f} URLs/second")
        
        # Show adaptive behavior
        if content_detector.adaptive_enabled:
            print(f"\nAdaptive Behavior:")
            print("-" * 30)
            print(f"Final concurrency: {content_detector.server_health['current_concurrency']}")
            print(f"Final success rate: {content_detector.server_health['success_rate']:.1%}")
            print(f"Total successful requests: {content_detector.server_health['success_count']}")
            print(f"Total failed requests: {content_detector.server_health['error_count']}")
            
            if content_detector.server_health['response_times']:
                avg_response_time = sum(content_detector.server_health['response_times']) / len(content_detector.server_health['response_times'])
                print(f"Average response time: {avg_response_time:.3f}s")
        
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
        
        if current_state.get('urls_checked'):
            success_rate = len(current_state.get('content_hashes', {})) / len(current_state.get('urls_checked', []))
            if success_rate > 0.95:
                print("✅ EXCELLENT: Success rate over 95%")
            elif success_rate > 0.90:
                print("✅ GOOD: Success rate over 90%")
            elif success_rate > 0.80:
                print("⚠️  ACCEPTABLE: Success rate over 80%")
            else:
                print("❌ POOR: Success rate under 80%")
        
        # Clean up
        await content_detector.close()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


async def test_adaptive_vs_fixed():
    """Compare adaptive rate limiting vs fixed concurrency."""
    
    print("\n" + "=" * 50)
    print("Comparing Adaptive vs Fixed Concurrency")
    print("=" * 50)
    
    config = ConfigManager()
    site_config = config.get_site('waverley_gov')
    
    if not site_config:
        print("Error: Could not find waverley_gov site configuration")
        return
    
    # Test 1: Fixed concurrency (50)
    print("\nTest 1: Fixed Concurrency (50)")
    print("-" * 30)
    
    # Temporarily disable adaptive rate limiting
    original_adaptive = getattr(site_config, 'adaptive_rate_limiting', True)
    site_config.adaptive_rate_limiting = False
    
    content_detector = ContentDetector(site_config)
    
    try:
        start_time = time.time()
        current_state = await content_detector.get_current_state()
        end_time = time.time()
        
        total_time = end_time - start_time
        urls_checked = len(current_state.get('urls_checked', []))
        content_hashes = len(current_state.get('content_hashes', {}))
        success_rate = content_hashes / urls_checked if urls_checked > 0 else 0
        speed = urls_checked / total_time if total_time > 0 else 0
        
        print(f"Time: {total_time:.2f}s")
        print(f"Success rate: {success_rate:.1%}")
        print(f"Speed: {speed:.1f} URLs/s")
        
        await content_detector.close()
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Adaptive concurrency
    print("\nTest 2: Adaptive Concurrency")
    print("-" * 30)
    
    # Re-enable adaptive rate limiting
    site_config.adaptive_rate_limiting = True
    
    content_detector = ContentDetector(site_config)
    
    try:
        start_time = time.time()
        current_state = await content_detector.get_current_state()
        end_time = time.time()
        
        total_time = end_time - start_time
        urls_checked = len(current_state.get('urls_checked', []))
        content_hashes = len(current_state.get('content_hashes', {}))
        success_rate = content_hashes / urls_checked if urls_checked > 0 else 0
        speed = urls_checked / total_time if total_time > 0 else 0
        
        print(f"Time: {total_time:.2f}s")
        print(f"Success rate: {success_rate:.1%}")
        print(f"Speed: {speed:.1f} URLs/s")
        print(f"Final concurrency: {content_detector.server_health['current_concurrency']}")
        
        await content_detector.close()
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Restore original setting
    site_config.adaptive_rate_limiting = original_adaptive
    
    print("\nComparison Summary:")
    print("-" * 30)
    print("Adaptive rate limiting should provide:")
    print("• Higher success rates")
    print("• Better speed optimization")
    print("• Automatic server load balancing")
    print("• No manual tuning required")


if __name__ == "__main__":
    # Run the main test
    asyncio.run(test_adaptive_rate_limiting())
    
    # Run comparison test
    asyncio.run(test_adaptive_vs_fixed()) 