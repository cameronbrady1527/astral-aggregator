# ==============================================================================
# test_config.py — Unit Tests for Configuration Management
# ==============================================================================
# Purpose: Test ConfigManager class functionality
# ==============================================================================

import pytest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import yaml
from app.utils.config import ConfigManager, SiteConfig


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    def test_config_manager_initialization(self):
        """Test ConfigManager initialization with default config file."""
        with patch('builtins.open', mock_open(read_data='sites: {}')):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager()
                assert isinstance(config_manager.config_file, Path)
                assert config_manager.config_file == Path("config/sites.yaml")
    
    def test_config_manager_with_custom_file(self):
        """Test ConfigManager initialization with custom config file."""
        custom_file = "custom_config.yaml"
        with patch('builtins.open', mock_open(read_data='sites: {}')):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager(custom_file)
                assert config_manager.config_file == Path(custom_file)
    
    def test_load_config_success(self):
        """Test successful configuration loading."""
        config_data = {
            'sites': {
                'test_site': {
                    'name': 'Test Site',
                    'url': 'https://example.com',
                    'sitemap_url': 'https://example.com/sitemap.xml',
                    'detection_methods': ['sitemap'],
                    'check_interval_minutes': 1440,
                    'is_active': True
                }
            },
            'firecrawl': {'api_key': 'test_key'},
            'system': {'output_directory': 'output'}
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager()
                
                assert 'test_site' in config_manager.sites
                assert config_manager.sites['test_site'].name == 'Test Site'
                assert config_manager.sites['test_site'].url == 'https://example.com'
                assert config_manager.firecrawl_config == {'api_key': 'test_key'}
                assert config_manager.system_config == {'output_directory': 'output'}
    
    def test_load_config_file_not_found(self):
        """Test configuration loading when file doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            with patch.object(ConfigManager, 'create_default_config') as mock_create:
                config_manager = ConfigManager()
                mock_create.assert_called_once()
    
    def test_load_config_invalid_yaml(self):
        """Test configuration loading with invalid YAML."""
        with patch('builtins.open', mock_open(read_data='invalid: yaml: content: [unclosed bracket')):
            with patch('pathlib.Path.exists', return_value=True):
                with pytest.raises(yaml.scanner.ScannerError):
                    ConfigManager()
    
    def test_get_site_existing(self):
        """Test getting an existing site configuration."""
        config_data = {
            'sites': {
                'test_site': {
                    'name': 'Test Site',
                    'url': 'https://example.com'
                }
            }
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager()
                site = config_manager.get_site('test_site')
                
                assert site is not None
                assert site.name == 'Test Site'
                assert site.url == 'https://example.com'
    
    def test_get_site_nonexistent(self):
        """Test getting a non-existent site configuration."""
        with patch('builtins.open', mock_open(read_data='sites: {}')):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager()
                site = config_manager.get_site('nonexistent')
                
                assert site is None
    
    def test_get_active_sites(self):
        """Test getting all active sites."""
        config_data = {
            'sites': {
                'active_site': {
                    'name': 'Active Site',
                    'url': 'https://active.com',
                    'is_active': True
                },
                'inactive_site': {
                    'name': 'Inactive Site',
                    'url': 'https://inactive.com',
                    'is_active': False
                }
            }
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager()
                active_sites = config_manager.get_active_sites()
                
                assert len(active_sites) == 1
                assert active_sites[0].name == 'Active Site'
    
    def test_get_firecrawl_config(self):
        """Test getting Firecrawl configuration."""
        config_data = {
            'sites': {},
            'firecrawl': {
                'api_key': 'test_key',
                'base_url': 'https://api.firecrawl.dev'
            }
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager()
                firecrawl_config = config_manager.get_firecrawl_config()
                
                assert firecrawl_config['api_key'] == 'test_key'
                assert firecrawl_config['base_url'] == 'https://api.firecrawl.dev'
    
    def test_get_system_config(self):
        """Test getting system configuration."""
        config_data = {
            'sites': {},
            'system': {
                'output_directory': 'output',
                'log_level': 'INFO'
            }
        }
        
        with patch('builtins.open', mock_open(read_data=yaml.dump(config_data))):
            with patch('pathlib.Path.exists', return_value=True):
                config_manager = ConfigManager()
                system_config = config_manager.get_system_config()
                
                assert system_config['output_directory'] == 'output'
                assert system_config['log_level'] == 'INFO'


class TestSiteConfig:
    """Test cases for SiteConfig class."""
    
    def test_site_config_creation(self):
        """Test SiteConfig creation with all parameters."""
        site_config = SiteConfig(
            name='Test Site',
            url='https://example.com',
            sitemap_url='https://example.com/sitemap.xml',
            detection_methods=['sitemap', 'firecrawl'],
            check_interval_minutes=720,
            is_active=False
        )
        
        assert site_config.name == 'Test Site'
        assert site_config.url == 'https://example.com'
        assert site_config.sitemap_url == 'https://example.com/sitemap.xml'
        assert site_config.detection_methods == ['sitemap', 'firecrawl']
        assert site_config.check_interval_minutes == 720
        assert site_config.is_active is False
    
    def test_site_config_defaults(self):
        """Test SiteConfig creation with default values."""
        site_config = SiteConfig(
            name='Test Site',
            url='https://example.com'
        )
        
        assert site_config.name == 'Test Site'
        assert site_config.url == 'https://example.com'
        assert site_config.sitemap_url is None
        assert site_config.detection_methods == ['sitemap']
        assert site_config.check_interval_minutes == 1440
        assert site_config.is_active is True
    
    def test_site_config_to_dict(self):
        """Test SiteConfig to_dict method."""
        site_config = SiteConfig(
            name='Test Site',
            url='https://example.com',
            sitemap_url='https://example.com/sitemap.xml',
            detection_methods=['sitemap'],
            check_interval_minutes=1440,
            is_active=True
        )
        
        config_dict = site_config.to_dict()
        
        assert config_dict['name'] == 'Test Site'
        assert config_dict['url'] == 'https://example.com'
        assert config_dict['sitemap_url'] == 'https://example.com/sitemap.xml'
        assert config_dict['detection_methods'] == ['sitemap']
        assert config_dict['check_interval_minutes'] == 1440
        assert config_dict['is_active'] is True 