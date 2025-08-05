#!/usr/bin/env python3
"""
Test script to verify content detector fixes for connection errors, rate limiting, and NoneType exceptions.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from crawler.content_detector import ContentDetector

class MockSiteConfig:
    """Mock site configuration for testing."""
    def __init__(self):
        self.url = "https://www.judiciary.uk"  # Required by base detector
        self.sitemap_url = "https://www.judiciary.uk/sitemap.xml"
        self.name = "judiciary_test"
        self.max_concurrent_requests = 10
        self.min_concurrent_requests = 1
        self.connection_pool_size = 20
        self.batch_size = 5
        self.ultra_fast_timeout = 5
        self.adaptive_rate_limiting = True
        self.success_rate_threshold = 0.95
        self.rate_adjustment_factor = 0.8
        self.rate_increase_factor = 1.1
        self.progressive_ramping = True
        self.ramp_start_concurrency = 1
        self.ramp_target_concurrency = 10
        self.ramp_batch_size = 3
        self.ip_rotation_enabled = True
        self.user_agent_rotation = True
        self.session_rotation_interval = 10
        self.force_session_rotation = False

async def test_session_management():
    """Test session management and connection handling."""
    print("🧪 Testing session management...")
    
    config = MockSiteConfig()
    detector = ContentDetector(config)
    
    try:
        # Test session creation
        session1 = await detector._create_ultra_fast_session()
        print(f"✅ Session 1 created: {session1 is not None}")
        
        # Test session rotation
        detector._request_count = 15  # Force rotation
        session2 = await detector._rotate_session_if_needed()
        print(f"✅ Session 2 created: {session2 is not None}")
        print(f"✅ Sessions are different: {session1 != session2}")
        
        # Test connection cleanup
        await detector._cleanup_connections()
        print(f"✅ Connection cleanup completed")
        
        # Test new session after cleanup
        session3 = await detector._create_ultra_fast_session()
        print(f"✅ Session 3 created after cleanup: {session3 is not None}")
        
    except Exception as e:
        print(f"❌ Session management test failed: {e}")
        return False
    
    finally:
        await detector.close()
    
    print("✅ Session management test passed!")
    return True

async def test_rate_limiting_handling():
    """Test rate limiting detection and handling."""
    print("🧪 Testing rate limiting handling...")
    
    config = MockSiteConfig()
    detector = ContentDetector(config)
    
    try:
        # Test rate limiting detection methods
        assert detector._is_429_rate_limited(0.1, 3) == True, "Should detect rate limiting"
        assert detector._is_429_rate_limited(0.8, 1) == False, "Should not detect rate limiting"
        
        # Test IP-level rate limiting detection
        assert detector._is_ip_level_rate_limited(0.05, 1) == True, "Should detect IP-level rate limiting"
        assert detector._is_ip_level_rate_limited(0.8, 1) == False, "Should not detect IP-level rate limiting"
        
        # Test persistent low success detection
        assert detector._is_persistent_low_success(0.45, 3) == True, "Should detect persistent low success"
        assert detector._is_persistent_low_success(0.8, 1) == False, "Should not detect persistent low success"
        
        print("✅ Rate limiting detection tests passed!")
        
        # Test rate limiting handler
        session = await detector._create_ultra_fast_session()
        new_session = await detector._handle_rate_limiting(session, 3)
        print(f"✅ Rate limiting handler completed: {new_session is not None}")
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {e}")
        return False
    
    finally:
        await detector.close()
    
    print("✅ Rate limiting handling test passed!")
    return True

async def test_none_checks():
    """Test None checks and error handling."""
    print("🧪 Testing None checks...")
    
    config = MockSiteConfig()
    detector = ContentDetector(config)
    
    try:
        # Test with None session
        detector._session = None
        detector._connector = None
        
        # This should handle None gracefully
        session = await detector._create_ultra_fast_session()
        print(f"✅ Created session from None state: {session is not None}")
        
        # Test cleanup with None objects
        await detector._cleanup_connections()
        print("✅ Cleanup with None objects completed")
        
    except Exception as e:
        print(f"❌ None checks test failed: {e}")
        return False
    
    finally:
        await detector.close()
    
    print("✅ None checks test passed!")
    return True

async def test_progressive_ramping():
    """Test progressive ramping with mock URLs."""
    print("🧪 Testing progressive ramping...")
    
    config = MockSiteConfig()
    detector = ContentDetector(config)
    
    # Mock URLs that will likely fail (to test error handling)
    test_urls = [
        "https://www.judiciary.uk/test1",
        "https://www.judiciary.uk/test2", 
        "https://www.judiciary.uk/test3",
        "https://www.judiciary.uk/test4",
        "https://www.judiciary.uk/test5"
    ]
    
    try:
        session = await detector._create_ultra_fast_session()
        
        # Test progressive ramping with a small batch
        print("Testing progressive ramping with mock URLs...")
        result = await detector._fetch_with_progressive_ramping(session, test_urls[:3])
        
        print(f"✅ Progressive ramping completed: {len(result)} results")
        print(f"✅ Result keys: {list(result.keys())}")
        
    except Exception as e:
        print(f"❌ Progressive ramping test failed: {e}")
        return False
    
    finally:
        await detector.close()
    
    print("✅ Progressive ramping test passed!")
    return True

async def main():
    """Run all tests."""
    print("🚀 Starting content detector fix verification tests...")
    print("=" * 60)
    
    tests = [
        test_session_management,
        test_rate_limiting_handling,
        test_none_checks,
        test_progressive_ramping
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes appear to be working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the fixes.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 