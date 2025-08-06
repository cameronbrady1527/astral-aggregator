#!/usr/bin/env python3
"""
Demonstrate password vs hash difference.
"""

import os
import socket

def test_authentication():
    """Test authentication with plain text password."""
    print("🔧 Testing Tor authentication...")
    
    try:
        # Connect to Tor control port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', 9051))
        
        # Get the plain text password from environment
        plain_password = os.getenv('TOR_CONTROL_PASSWORD', 'my_control_password_123')
        print(f"📝 Using plain text password: {plain_password}")
        
        # Send authentication command with plain text password
        auth_command = f'AUTHENTICATE "{plain_password}"\r\n'
        sock.send(auth_command.encode())
        
        # Read response
        response = sock.recv(1024).decode()
        sock.close()
        
        if "250 OK" in response:
            print("✅ Authentication successful!")
            print("   This proves the plain text password is correct.")
            return True
        else:
            print(f"❌ Authentication failed: {response.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def explain_password_system():
    """Explain how the password system works."""
    print("🔐 Tor Password System Explanation:")
    print("")
    print("1. TOR_CONTROL_PASSWORD (Environment Variable):")
    print("   - Should be: my_control_password_123")
    print("   - This is the PLAIN TEXT password")
    print("   - Your application sends this to Tor")
    print("")
    print("2. HashedControlPassword (in torrc file):")
    print("   - Should be: 16:3223DA63D56369E66031AB7C86CC2CE449CA853A75A59E624B59D39E19")
    print("   - This is the HASHED version of the password")
    print("   - Tor stores this for security")
    print("")
    print("3. How authentication works:")
    print("   - Your app sends: my_control_password_123")
    print("   - Tor hashes it and compares to the hash in torrc")
    print("   - If they match → Authentication succeeds")
    print("")

def main():
    """Main function."""
    print("🚀 Password Configuration Verification")
    print("=" * 50)
    
    explain_password_system()
    
    # Test authentication
    success = test_authentication()
    
    print("📊 Result:")
    if success:
        print("✅ Configuration is CORRECT!")
        print("   - Plain text password works")
        print("   - Hash in torrc is correct")
        print("   - Tor identity rotation will work")
    else:
        print("❌ Configuration has issues")
        print("   - Check password and hash match")

if __name__ == "__main__":
    main() 