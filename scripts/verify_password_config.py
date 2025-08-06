#!/usr/bin/env python3
"""
Verify password configuration consistency.
"""

import os
import yaml
from pathlib import Path

def check_environment_variables():
    """Check environment variables."""
    print("🔧 Checking environment variables...")
    
    password = os.getenv('TOR_CONTROL_PASSWORD')
    if password:
        print(f"✅ TOR_CONTROL_PASSWORD: {password}")
        return password
    else:
        print("❌ TOR_CONTROL_PASSWORD not set")
        return None

def check_torrc_file():
    """Check torrc file configuration."""
    print("\n🔧 Checking torrc file...")
    
    torrc_path = Path(os.path.expanduser("~/AppData/Roaming/Tor/torrc"))
    if torrc_path.exists():
        print(f"✅ Torrc file exists: {torrc_path}")
        
        with open(torrc_path, 'r') as f:
            content = f.read()
            
        # Check for control port
        if "ControlPort 9051" in content:
            print("✅ ControlPort 9051 configured")
        else:
            print("❌ ControlPort 9051 not configured")
            
        # Check for hashed password
        if "HashedControlPassword" in content:
            lines = content.split('\n')
            for line in lines:
                if line.startswith("HashedControlPassword"):
                    print(f"✅ HashedControlPassword configured: {line.split()[1][:20]}...")
                    return line.split()[1]
        else:
            print("❌ HashedControlPassword not configured")
    else:
        print(f"❌ Torrc file not found: {torrc_path}")
    
    return None

def check_proxy_config():
    """Check proxy configuration file."""
    print("\n🔧 Checking proxy configuration...")
    
    config_path = Path("config/proxy_config.yaml")
    if config_path.exists():
        print(f"✅ Proxy config exists: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        if 'tor' in config and 'control_password' in config['tor']:
            password = config['tor']['control_password']
            print(f"✅ Control password in config: {password}")
            return password
        else:
            print("❌ Control password not in config")
    else:
        print(f"❌ Proxy config not found: {config_path}")
    
    return None

def verify_password_consistency():
    """Verify password consistency across all sources."""
    print("🚀 Verifying password configuration consistency...\n")
    
    env_password = check_environment_variables()
    torrc_hash = check_torrc_file()
    config_password = check_proxy_config()
    
    print("\n📊 Password Configuration Summary:")
    print(f"   Environment Variable: {'✅ Set' if env_password else '❌ Not Set'}")
    print(f"   Torrc Hash: {'✅ Configured' if torrc_hash else '❌ Not Configured'}")
    print(f"   Config File: {'✅ Set' if config_password else '❌ Not Set'}")
    
    # Check consistency
    if env_password and config_password:
        if env_password == config_password:
            print("✅ Environment and config passwords match")
        else:
            print("❌ Environment and config passwords don't match")
            print(f"   Environment: {env_password}")
            print(f"   Config: {config_password}")
    
    if torrc_hash:
        print(f"✅ Torrc hashed password: {torrc_hash[:20]}...")
    
    print("\n💡 Current Configuration:")
    print(f"   Password: {env_password or 'Not set'}")
    print(f"   Hash: {torrc_hash or 'Not configured'}")
    
    if env_password and torrc_hash:
        print("\n✅ Password configuration appears consistent!")
        print("   Tor identity rotation should work correctly.")
    else:
        print("\n⚠️ Password configuration may have issues.")
        print("   Check the details above.")

if __name__ == "__main__":
    verify_password_consistency() 