#!/usr/bin/env python3
"""
Proxy Provider Switch Script
============================

This script helps switch between different proxy providers for the aggregator.
It can configure environment variables and update configuration files.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

class ProxySwitcher:
    """Handles switching between proxy providers."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / ".env"
        self.config_file = self.project_root / "config" / "proxy_config.yaml"
        
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get available proxy providers and their configurations."""
        return {
            "tor": {
                "name": "Tor Network",
                "description": "Free, anonymous, slow",
                "setup_required": True,
                "setup_script": "scripts/setup_tor.py",
                "test_script": "scripts/test_tor_integration.py"
            },
            "bright_data": {
                "name": "Bright Data",
                "description": "Premium residential proxies, fast",
                "setup_required": False,
                "cost": "$500/month (40GB)"
            },
            "oxylabs": {
                "name": "Oxylabs",
                "description": "Premium residential proxies, good balance",
                "setup_required": False,
                "cost": "$300/month (20GB)"
            },
            "proxymesh": {
                "name": "ProxyMesh",
                "description": "Basic residential proxies, affordable",
                "setup_required": False,
                "cost": "$15/month (5 IPs)"
            },
            "storm_proxies": {
                "name": "Storm Proxies",
                "description": "Basic residential proxies, affordable",
                "setup_required": False,
                "cost": "$50/month (5 IPs)"
            },
            "public": {
                "name": "Public Proxies",
                "description": "Free, unreliable, not recommended",
                "setup_required": False,
                "warning": "Unreliable and may be blocked"
            }
        }
    
    def list_providers(self):
        """List all available proxy providers."""
        providers = self.get_available_providers()
        
        print("🔧 Available Proxy Providers")
        print("=" * 50)
        
        for provider_id, info in providers.items():
            print(f"\n📡 {info['name']} ({provider_id})")
            print(f"   Description: {info['description']}")
            
            if 'cost' in info:
                print(f"   Cost: {info['cost']}")
            
            if 'warning' in info:
                print(f"   ⚠️  {info['warning']}")
            
            if info['setup_required']:
                print(f"   🔧 Setup script: {info['setup_script']}")
                print(f"   🧪 Test script: {info['test_script']}")
    
    def get_current_provider(self) -> str:
        """Get the currently configured proxy provider."""
        # Check environment variables
        provider = os.getenv('PROXY_PROVIDER')
        if provider:
            return provider
        
        # Check .env file
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.startswith('PROXY_PROVIDER='):
                        return line.split('=', 1)[1].strip()
        
        return "none"
    
    def switch_to_provider(self, provider_id: str):
        """Switch to a specific proxy provider."""
        providers = self.get_available_providers()
        
        if provider_id not in providers:
            print(f"❌ Unknown provider: {provider_id}")
            print("Use --list to see available providers")
            return False
        
        provider_info = providers[provider_id]
        print(f"🔄 Switching to {provider_info['name']}...")
        
        # Create environment configuration
        env_config = self._create_env_config(provider_id)
        
        # Write .env file
        self._write_env_file(env_config)
        
        # Update proxy config if it exists
        self._update_proxy_config(provider_id)
        
        print(f"✅ Switched to {provider_info['name']}")
        
        # Show next steps
        if provider_info['setup_required']:
            print(f"\n📋 Next steps:")
            print(f"   1. Run setup script: python {provider_info['setup_script']}")
            print(f"   2. Test integration: python {provider_info['test_script']}")
        else:
            print(f"\n📋 Next steps:")
            print(f"   1. Set your credentials in the .env file")
            print(f"   2. Test the integration: python scripts/test_proxy_integration.py")
        
        return True
    
    def _create_env_config(self, provider_id: str) -> Dict[str, str]:
        """Create environment configuration for a provider."""
        config = {
            "PROXY_PROVIDER": provider_id
        }
        
        if provider_id == "tor":
            config.update({
                "TOR_HOST": "127.0.0.1",
                "TOR_PORT": "9050",
                "TOR_CONTROL_PORT": "9051",
                "TOR_CONTROL_PASSWORD": "your_tor_control_password",
                "PROXY_HOST": "127.0.0.1",
                "PROXY_PORT": "9050",
                "PROXY_USERNAME": "",
                "PROXY_PASSWORD": "",
                "PROXY_SESSION_DURATION": "600",
                "PROXY_MAX_REQUESTS": "100",
                "PROXY_RETRY_ATTEMPTS": "3",
                "PROXY_TIMEOUT": "30"
            })
        elif provider_id in ["bright_data", "oxylabs"]:
            config.update({
                "PROXY_HOST": "your_proxy_host",
                "PROXY_PORT": "your_proxy_port",
                "PROXY_USERNAME": "your_username",
                "PROXY_PASSWORD": "your_password",
                "PROXY_COUNTRY": "us",
                "PROXY_CITY": "",
                "PROXY_SESSION_DURATION": "600",
                "PROXY_MAX_REQUESTS": "100",
                "PROXY_RETRY_ATTEMPTS": "3",
                "PROXY_TIMEOUT": "30"
            })
        elif provider_id in ["proxymesh", "storm_proxies"]:
            config.update({
                "PROXY_HOST": "your_proxy_host",
                "PROXY_PORT": "your_proxy_port",
                "PROXY_USERNAME": "your_username",
                "PROXY_PASSWORD": "your_password",
                "PROXY_SESSION_DURATION": "600",
                "PROXY_MAX_REQUESTS": "100",
                "PROXY_RETRY_ATTEMPTS": "3",
                "PROXY_TIMEOUT": "30"
            })
        elif provider_id == "public":
            config.update({
                "PROXY_HOST": "127.0.0.1",
                "PROXY_PORT": "8080",
                "PROXY_USERNAME": "",
                "PROXY_PASSWORD": "",
                "PROXY_SESSION_DURATION": "300",
                "PROXY_MAX_REQUESTS": "10",
                "PROXY_RETRY_ATTEMPTS": "5",
                "PROXY_TIMEOUT": "15"
            })
        
        return config
    
    def _write_env_file(self, config: Dict[str, str]):
        """Write configuration to .env file."""
        env_content = "# Proxy Configuration\n"
        env_content += "# Generated by switch_proxy.py\n\n"
        
        for key, value in config.items():
            env_content += f"{key}={value}\n"
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Updated {self.env_file}")
    
    def _update_proxy_config(self, provider_id: str):
        """Update proxy configuration file."""
        if not self.config_file.exists():
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            if not config:
                config = {}
            
            config['proxy_provider'] = provider_id
            
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            print(f"✅ Updated {self.config_file}")
            
        except Exception as e:
            print(f"⚠️  Could not update {self.config_file}: {e}")
    
    def show_current_status(self):
        """Show current proxy configuration status."""
        current_provider = self.get_current_provider()
        providers = self.get_available_providers()
        
        print("📊 Current Proxy Configuration")
        print("=" * 40)
        
        if current_provider == "none":
            print("❌ No proxy provider configured")
            print("💡 Use --switch <provider> to configure a provider")
        else:
            if current_provider in providers:
                provider_info = providers[current_provider]
                print(f"✅ Current provider: {provider_info['name']} ({current_provider})")
                print(f"   Description: {provider_info['description']}")
            else:
                print(f"⚠️  Unknown provider: {current_provider}")
        
        # Show environment variables
        print(f"\n🔧 Environment Variables:")
        env_vars = [
            'PROXY_PROVIDER', 'PROXY_HOST', 'PROXY_PORT', 
            'PROXY_USERNAME', 'PROXY_PASSWORD', 'TOR_CONTROL_PASSWORD'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                if 'PASSWORD' in var:
                    print(f"   {var}: {'*' * len(value)}")
                else:
                    print(f"   {var}: {value}")
            else:
                print(f"   {var}: Not set")
        
        # Check if .env file exists
        if self.env_file.exists():
            print(f"\n📄 .env file: {self.env_file} (exists)")
        else:
            print(f"\n📄 .env file: {self.env_file} (not found)")

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Switch between proxy providers")
    parser.add_argument('--list', action='store_true', help='List available providers')
    parser.add_argument('--switch', metavar='PROVIDER', help='Switch to a specific provider')
    parser.add_argument('--status', action='store_true', help='Show current configuration status')
    
    args = parser.parse_args()
    
    switcher = ProxySwitcher()
    
    if args.list:
        switcher.list_providers()
    elif args.switch:
        switcher.switch_to_provider(args.switch)
    elif args.status:
        switcher.show_current_status()
    else:
        # Show current status by default
        switcher.show_current_status()
        print(f"\n💡 Use --list to see available providers")
        print(f"💡 Use --switch <provider> to change providers")

if __name__ == "__main__":
    main() 