#!/usr/bin/env python3
"""
Simple proxy test script.
"""

import asyncio
import os
import aiohttp
import socket

async def test_tor_connection():
    """Test if Tor is accessible."""
    print("🔧 Testing Tor connection...")
    
    # Test if Tor port is open
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        
        if result == 0:
            print("✅ Tor SOCKS5 port (9050) is accessible")
        else:
            print("❌ Tor SOCKS5 port (9050) is not accessible")
            return False
    except Exception as e:
        print(f"❌ Error testing Tor port: {e}")
        return False
    
    # Test if control port is open
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9051))
        sock.close()
        
        if result == 0:
            print("✅ Tor control port (9051) is accessible")
            control_available = True
        else:
            print("⚠️ Tor control port (9051) is not accessible")
            print("   Identity rotation will not work without control port")
            control_available = False
    except Exception as e:
        print(f"❌ Error testing control port: {e}")
        control_available = False
    
    # Test SOCKS5 connection
    try:
        # Try to connect through Tor
        timeout = aiohttp.ClientTimeout(total=30)
        
        # Try with aiohttp-socks first
        try:
            from aiohttp_socks import ProxyConnector
            connector = ProxyConnector.from_url("socks5://127.0.0.1:9050")
            print("✅ Using aiohttp-socks for SOCKS5")
        except ImportError:
            try:
                connector = aiohttp.ProxyConnector.from_url("socks5://127.0.0.1:9050")
                print("✅ Using aiohttp built-in SOCKS5 support")
            except AttributeError:
                print("❌ SOCKS5 support not available")
                print("💡 Install aiohttp-socks: pip install aiohttp-socks")
                return False
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            async with session.get('http://httpbin.org/ip', timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    ip = data.get('origin', '').split(',')[0].strip()
                    print(f"✅ Tor connection successful! IP: {ip}")
                    return True
                else:
                    print(f"❌ Tor connection failed with status: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing Tor connection: {e}")
        return False

def check_environment():
    """Check environment variables."""
    print("🔧 Checking environment variables...")
    
    env_vars = {
        'PROXY_PROVIDER': os.getenv('PROXY_PROVIDER'),
        'TOR_HOST': os.getenv('TOR_HOST'),
        'TOR_PORT': os.getenv('TOR_PORT'),
        'TOR_CONTROL_PORT': os.getenv('TOR_CONTROL_PORT'),
        'TOR_CONTROL_PASSWORD': os.getenv('TOR_CONTROL_PASSWORD')
    }
    
    missing_vars = []
    for var, value in env_vars.items():
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("💡 Run: .\\scripts\\setup_proxy_env.ps1")
        return False
    
    return True

async def main():
    """Main test function."""
    print("🚀 Starting simple proxy test...")
    
    # Check environment
    env_ok = check_environment()
    
    # Test Tor connection
    tor_ok = await test_tor_connection()
    
    print("\n📊 Test Results:")
    print(f"   Environment: {'✅ PASS' if env_ok else '❌ FAIL'}")
    print(f"   Tor Connection: {'✅ PASS' if tor_ok else '❌ FAIL'}")
    
    if not env_ok:
        print("\n🔧 To fix environment issues:")
        print("1. Run: .\\scripts\\setup_proxy_env.ps1")
        print("2. Restart your terminal")
        print("3. Run this test again")
    
    if not tor_ok:
        print("\n🔧 To fix Tor issues:")
        print("1. Make sure Tor Browser is running")
        print("2. Check if Tor is listening on port 9050")
        print("3. Install aiohttp-socks: pip install aiohttp-socks")
        print("4. For identity rotation, configure Tor control port in torrc")
    
    if env_ok and tor_ok:
        print("\n✅ All tests passed! Proxy should work correctly.")

if __name__ == "__main__":
    asyncio.run(main()) 