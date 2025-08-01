# ==============================================================================
# config.py — Configuration Management for Change Detection System
# ==============================================================================
# Purpose: Handle site configurations and system settings
# Sections: Imports, SiteConfig Class, ConfigManager Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import yaml
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Third Party -----
from dotenv import load_dotenv

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['SiteConfig', 'ConfigManager']


class SiteConfig:
    """Configuration for a single site."""
    
    def __init__(self, name: str, url: str, **kwargs):
        self.name = name
        self.url = url
        self.sitemap_url = kwargs.get('sitemap_url')
        self.detection_methods = kwargs.get('detection_methods', ['sitemap'])
        self.check_interval_minutes = kwargs.get('check_interval_minutes', 1440)
        self.is_active = kwargs.get('is_active', True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'url': self.url,
            'sitemap_url': self.sitemap_url,
            'detection_methods': self.detection_methods,
            'check_interval_minutes': self.check_interval_minutes,
            'is_active': self.is_active
        }


class ConfigManager:
    """Manages configuration for the change detection system."""
    
    def __init__(self, config_file: str = "config/sites.yaml"):
        """Initialize configuration manager."""
        # Load environment variables from .env file
        load_dotenv()
        
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(exist_ok=True)
        self.sites: Dict[str, SiteConfig] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        if not self.config_file.exists():
            self.create_default_config()
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Replace environment variable placeholders in the entire config
        config_data = self._substitute_env_vars(config_data)
        
        sites_data = config_data.get('sites', {})
        for site_id, site_data in sites_data.items():
            self.sites[site_id] = SiteConfig(**site_data)
        
        self.firecrawl_config = config_data.get('firecrawl', {})
        self.system_config = config_data.get('system', {})
    
    def _substitute_env_vars(self, data: Any) -> Any:
        """Recursively substitute environment variable placeholders."""
        if isinstance(data, dict):
            return {key: self._substitute_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith('${') and data.endswith('}'):
            # Extract environment variable name
            env_var = data[2:-1]  # Remove ${ and }
            env_value = os.getenv(env_var)
            if env_value is None:
                print(f"Warning: Environment variable {env_var} not found")
                return data  # Return original if not found
            return env_value
        else:
            return data
    
    def create_default_config(self) -> None:
        """Create a default configuration file."""
        default_config = {
            'sites': {
                'judiciary_uk': {
                    'name': 'Judiciary UK',
                    'url': 'https://www.judiciary.uk/',
                    'sitemap_url': 'https://www.judiciary.uk/sitemap.xml',
                    'detection_methods': ['sitemap', 'firecrawl'],
                    'check_interval_minutes': 1440,
                    'is_active': True
                },
                'waverley_gov': {
                    'name': 'Waverley Borough Council',
                    'url': 'https://www.waverley.gov.uk/',
                    'sitemap_url': 'https://www.waverley.gov.uk/sitemap.xml',
                    'detection_methods': ['sitemap', 'firecrawl'],
                    'check_interval_minutes': 1440,
                    'is_active': True
                }
            },
            'firecrawl': {
                'api_key': '${FIRECRAWL_API_KEY}',
                'base_url': 'https://api.firecrawl.dev'
            },
            'system': {
                'output_directory': 'output',
                'log_level': 'INFO',
                'max_retries': 3,
                'timeout_seconds': 30
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
    
    def get_site(self, site_id: str) -> Optional[SiteConfig]:
        """Get configuration for a specific site."""
        return self.sites.get(site_id)
    
    def get_active_sites(self) -> List[SiteConfig]:
        """Get all active sites."""
        return [site for site in self.sites.values() if site.is_active]
    
    def add_site(self, site_id: str, site_config: SiteConfig) -> None:
        """Add a new site configuration."""
        self.sites[site_id] = site_config
        self.save_config()
    
    def update_site(self, site_id: str, **kwargs) -> None:
        """Update an existing site configuration."""
        if site_id in self.sites:
            site = self.sites[site_id]
            for key, value in kwargs.items():
                if hasattr(site, key):
                    setattr(site, key, value)
            self.save_config()
    
    def remove_site(self, site_id: str) -> None:
        """Remove a site configuration."""
        if site_id in self.sites:
            del self.sites[site_id]
            self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        config_data = {
            'sites': {site_id: site.to_dict() for site_id, site in self.sites.items()},
            'firecrawl': self.firecrawl_config,
            'system': self.system_config
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def get_firecrawl_config(self) -> Dict[str, Any]:
        """Get Firecrawl configuration."""
        return self.firecrawl_config
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration."""
        return self.system_config 