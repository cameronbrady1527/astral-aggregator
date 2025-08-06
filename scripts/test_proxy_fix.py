#!/usr/bin/env python3
"""
Test and fix proxy issues for the aggregator.
"""

import asyncio
import os
import sys
import aiohttp
from pathlib import Path

# Add the app directory to the path
app_path = str(Path(__file__).parent.parent / "app")
sys.path.insert(0, app_path)

# Import after adding to path
from utils.proxy_manager import create_proxy_manager_from_env, TorProxyManager
from utils.tor_service import initialize_tor_service, get_tor_service

async def test_proxy_connection():
    """Test proxy connection and functionality."""
    print("🔧 Testing proxy connection...")
    
    # Set environment variables if not already set
    if not os.getenv('PROXY_PROVIDER'):
        os.environ['PROXY_PROVIDER'] = 'tor'
        os.environ['TOR_HOST'] = '127.0.0.1'
        os.environ['TOR_PORT'] = '9050'
        os.environ['TOR_CONTROL_PORT'] = '9051'
        os.environ['TOR_CONTROL_PASSWORD'] = 'my_control_password_123'
        print("✅ Set proxy environment variables")
    
    try:
        # Initialize Tor service
        print("🔄 Initializing Tor service...")
        tor_service = await initialize_tor_service()
        if not tor_service:
            print("❌ Failed to initialize Tor service")
            return False
        
        # Check if Tor is healthy
        if not await tor_service.health_check():
            print("❌ Tor service is not healthy")
            return False
        
        print("✅ Tor service is running and healthy")
        
        # Create proxy manager
        print("🔄 Creating proxy manager...")
        proxy_manager = await create_proxy_manager_from_env()
        if not proxy_manager:
            print("❌ Failed to create proxy manager")
            return False
        
        print("✅ Proxy manager created successfully")
        
        # Test proxy connection
        print("🔄 Testing proxy connection...")
        connector = await proxy_manager.get_proxy_connector()
        if not connector:
            print("❌ Failed to get proxy connector")
            return False
        
        # Test with a simple request
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            try:
                async with session.get('http://httpbin.org/ip', timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        ip = data.get('origin', '').split(',')[0].strip()
                        print(f"✅ Proxy test successful! IP: {ip}")
                        
                        # Test identity rotation if available
                        if isinstance(proxy_manager, TorProxyManager):
                            print("🔄 Testing Tor identity rotation...")
                            if await proxy_manager.rotate_identity_on_rate_limit():
                                print("✅ Tor identity rotation successful")
                            else:
                                print("⚠️ Tor identity rotation failed (control port may not be configured)")
                        
                        return True
                    else:
                        print(f"❌ Proxy test failed with status: {response.status}")
                        return False
            except Exception as e:
                print(f"❌ Proxy test failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Error during proxy test: {e}")
        return False

async def test_rate_limit_handling():
    """Test rate limit handling with proxy rotation."""
    print("\n🔄 Testing rate limit handling...")
    
    try:
        proxy_manager = await create_proxy_manager_from_env()
        if not proxy_manager:
            print("❌ No proxy manager available")
            return False
        
        if isinstance(proxy_manager, TorProxyManager):
            print("🔄 Testing Tor identity rotation on rate limit...")
            success = await proxy_manager.rotate_identity_on_rate_limit()
            if success:
                print("✅ Tor identity rotation successful")
                return True
            else:
                print("⚠️ Tor identity rotation failed - control port may not be configured")
                print("💡 To enable identity rotation, add to your torrc:")
                print("   ControlPort 9051")
                print("   HashedControlPassword 16:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                print("   CookieAuthentication 0")
                return False
        else:
            print("ℹ️ Not using Tor proxy manager")
            return True
            
    except Exception as e:
        print(f"❌ Error testing rate limit handling: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting proxy test and fix...")
    
    # Test basic proxy connection
    proxy_ok = await test_proxy_connection()
    
    # Test rate limit handling
    rate_limit_ok = await test_rate_limit_handling()
    
    print("\n📊 Test Results:")
    print(f"   Proxy Connection: {'✅ PASS' if proxy_ok else '❌ FAIL'}")
    print(f"   Rate Limit Handling: {'✅ PASS' if rate_limit_ok else '⚠️ PARTIAL'}")
    
    if not proxy_ok:
        print("\n🔧 To fix proxy issues:")
        print("1. Run: .\\scripts\\setup_proxy_env.ps1")
        print("2. Configure Tor control port in torrc")
        print("3. Restart Tor")
        print("4. Run this test again")
    
    if not rate_limit_ok:
        print("\n🔧 To enable Tor identity rotation:")
        print("1. Add to your torrc file:")
        print("   ControlPort 9051")
        print("   HashedControlPassword 16:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print("   CookieAuthentication 0")
        print("2. Generate hashed password: tor --hash-password 'my_control_password_123'")
        print("3. Restart Tor")
        print("4. Run this test again")

if __name__ == "__main__":
    asyncio.run(main()) 