#!/usr/bin/env python3
"""
Test Tor identity rotation.
"""

import asyncio
import socket
import os

async def test_tor_control_connection():
    """Test connection to Tor control port."""
    print("🔧 Testing Tor control port connection...")
    
    try:
        # Test if control port is accessible
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9051))
        sock.close()
        
        if result == 0:
            print("✅ Tor control port (9051) is accessible")
            return True
        else:
            print("❌ Tor control port (9051) is not accessible")
            return False
    except Exception as e:
        print(f"❌ Error testing control port: {e}")
        return False

async def test_tor_authentication():
    """Test Tor authentication."""
    print("🔧 Testing Tor authentication...")
    
    try:
        # Simple socket connection to test authentication
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9051))
        
        # Send authentication command
        password = os.getenv('TOR_CONTROL_PASSWORD', 'my_control_password_123')
        auth_command = f'AUTHENTICATE "{password}"\r\n'
        sock.send(auth_command.encode())
        
        # Read response
        response = sock.recv(1024).decode()
        sock.close()
        
        if "250 OK" in response:
            print("✅ Tor authentication successful")
            return True
        else:
            print(f"❌ Tor authentication failed: {response.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during authentication test: {e}")
        return False

async def test_identity_rotation():
    """Test identity rotation."""
    print("🔧 Testing identity rotation...")
    
    try:
        # Simple socket connection to test identity rotation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9051))
        
        # Authenticate
        password = os.getenv('TOR_CONTROL_PASSWORD', 'my_control_password_123')
        auth_command = f'AUTHENTICATE "{password}"\r\n'
        sock.send(auth_command.encode())
        response = sock.recv(1024).decode()
        
        if "250 OK" not in response:
            print(f"❌ Authentication failed: {response.strip()}")
            sock.close()
            return False
        
        # Send NEWNYM command
        newnym_command = 'SIGNAL NEWNYM\r\n'
        sock.send(newnym_command.encode())
        response = sock.recv(1024).decode()
        sock.close()
        
        if "250 OK" in response:
            print("✅ Identity rotation successful")
            return True
        else:
            print(f"❌ Identity rotation failed: {response.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error during identity rotation test: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Starting Tor identity rotation test...")
    
    # Check environment
    password = os.getenv('TOR_CONTROL_PASSWORD')
    if password:
        print(f"✅ TOR_CONTROL_PASSWORD is set: {password[:10]}...")
    else:
        print("❌ TOR_CONTROL_PASSWORD is not set")
        return
    
    # Test control port
    control_ok = await test_tor_control_connection()
    
    # Test authentication
    auth_ok = await test_tor_authentication()
    
    # Test identity rotation
    rotation_ok = await test_identity_rotation()
    
    print("\n📊 Test Results:")
    print(f"   Control Port: {'✅ PASS' if control_ok else '❌ FAIL'}")
    print(f"   Authentication: {'✅ PASS' if auth_ok else '❌ FAIL'}")
    print(f"   Identity Rotation: {'✅ PASS' if rotation_ok else '❌ FAIL'}")
    
    if control_ok and auth_ok and rotation_ok:
        print("\n✅ All tests passed! Tor identity rotation should work correctly.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 