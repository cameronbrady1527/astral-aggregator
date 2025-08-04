# ==============================================================================
# test_config.py — Unit Tests for Configuration Management
# ==============================================================================
# Purpose: Test the configuration loading, validation, and management
# ==============================================================================

import pytest
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from app.utils.config import SiteConfig, ConfigManager


class TestSiteConfig:
    """Test the SiteConfig class."""
    
    def test_site_config_initialization(self):
        """Test SiteConfig initialization with basic parameters."""
        config = SiteConfig(
            name="Test Site",
            url="https://test.example.com/",
            sitemap_url="https://test.example.com/sitemap.xml"
        )
        
        assert config.name == "Test Site"
        assert config.url == "https://test.example.com/"
        assert config.sitemap_url == "https://test.example.com/sitemap.xml"
        assert config.detection_methods == ["sitemap"]
        assert config.check_interval_minutes == 1440
        assert config.is_active is True
    
    def test_site_config_with_custom_parameters(self):
        """Test SiteConfig initialization with custom parameters."""
        config = SiteConfig(
            name="Custom Site",
            url="https://custom.example.com/",
            sitemap_url="https://custom.example.com/sitemap.xml",
            detection_methods=["sitemap", "firecrawl"],
            check_interval_minutes=60,
            is_active=False,
            custom_param="custom_value"
        )
        
        assert config.name == "Custom Site"
        assert config.detection_methods == ["sitemap", "firecrawl"]
        assert config.check_interval_minutes == 60
        assert config.is_active is False
        assert config.custom_param == "custom_value"
    
    def test_site_config_to_dict(self):
        """Test SiteConfig to_dict method."""
        config = SiteConfig(
            name="Test Site",
            url="https://test.example.com/",
            sitemap_url="https://test.example.com/sitemap.xml",
            detection_methods=["sitemap", "firecrawl"],
            check_interval_minutes=120,
            is_active=True
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["name"] == "Test Site"
        assert config_dict["url"] == "https://test.example.com/"
        assert config_dict["sitemap_url"] == "https://test.example.com/sitemap.xml"
        assert config_dict["detection_methods"] == ["sitemap", "firecrawl"]
        assert config_dict["check_interval_minutes"] == 120
        assert config_dict["is_active"] is True


class TestConfigManager:
    """Test the ConfigManager class."""
    
    def test_config_manager_initialization(self, temp_config_file):
        """Test ConfigManager initialization with config file."""
        with patch('app.utils.config.ConfigManager.load_config'):
            manager = ConfigManager(temp_config_file)
            assert manager.config_file == Path(temp_config_file)
    
    def test_load_config_from_file(self, test_config):
        """Test loading configuration from YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            # Check that sites were loaded
            assert "test_site_1" in manager.sites
            assert "test_site_2" in manager.sites
            assert "test_site_3" in manager.sites
            
            # Check site configurations
            site1 = manager.sites["test_site_1"]
            assert site1.name == "Test Site 1"
            assert site1.url == "https://test1.example.com/"
            assert site1.detection_methods == ["sitemap"]
            assert site1.is_active is True
            
            site2 = manager.sites["test_site_2"]
            assert site2.detection_methods == ["sitemap", "firecrawl"]
            
            site3 = manager.sites["test_site_3"]
            assert site3.is_active is False
            
            # Check firecrawl and system config
            assert manager.firecrawl_config["api_key"] == "test-api-key"
            assert manager.system_config["output_directory"] == "test_output"
            
        finally:
            os.unlink(temp_file)
    
    def test_create_default_config(self):
        """Test creating default configuration when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "nonexistent.yaml"
            manager = ConfigManager(str(config_file))
            
            # Should create default config
            assert config_file.exists()
            
            # Load the created config to verify structure
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)
            
            assert "sites" in config_data
            assert "firecrawl" in config_data
            assert "system" in config_data
    
    def test_environment_variable_substitution(self):
        """Test environment variable substitution in config."""
        # Set test environment variable
        os.environ["TEST_API_KEY"] = "test-key-value"
        
        test_config_with_env = {
            "sites": {
                "test_site": {
                    "name": "Test Site",
                    "url": "https://test.example.com/",
                    "api_key": "${TEST_API_KEY}"
                }
            },
            "firecrawl": {
                "api_key": "${TEST_API_KEY}"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config_with_env, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            # Check that environment variables were substituted
            site = manager.sites["test_site"]
            assert site.api_key == "test-key-value"
            assert manager.firecrawl_config["api_key"] == "test-key-value"
            
        finally:
            os.unlink(temp_file)
            # Clean up environment variable
            if "TEST_API_KEY" in os.environ:
                del os.environ["TEST_API_KEY"]
    
    def test_get_site(self, test_config):
        """Test getting a specific site configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            # Test getting existing site
            site = manager.get_site("test_site_1")
            assert site is not None
            assert site.name == "Test Site 1"
            
            # Test getting non-existent site
            site = manager.get_site("nonexistent")
            assert site is None
    
        finally:
            os.unlink(temp_file)
    
    def test_get_active_sites(self, test_config):
        """Test getting only active sites."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            active_sites = manager.get_active_sites()
            
            # Should only return active sites
            assert len(active_sites) == 2
            site_names = [site.name for site in active_sites]
            assert "Test Site 1" in site_names
            assert "Test Site 2" in site_names
            assert "Test Site 3" not in site_names  # This one is inactive
            
        finally:
            os.unlink(temp_file)
    
    def test_add_site(self, test_config):
        """Test adding a new site configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            new_site = SiteConfig(
                name="New Test Site",
                url="https://new.example.com/",
                sitemap_url="https://new.example.com/sitemap.xml"
            )
            
            manager.add_site("new_site", new_site)
            
            # Verify site was added
            assert "new_site" in manager.sites
            added_site = manager.sites["new_site"]
            assert added_site.name == "New Test Site"
            assert added_site.url == "https://new.example.com/"
            
        finally:
            os.unlink(temp_file)
    
    def test_update_site(self, test_config):
        """Test updating an existing site configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            # Update site
            manager.update_site("test_site_1", name="Updated Site Name", is_active=False)
            
            # Verify changes
            updated_site = manager.sites["test_site_1"]
            assert updated_site.name == "Updated Site Name"
            assert updated_site.is_active is False
            # Other properties should remain unchanged
            assert updated_site.url == "https://test1.example.com/"
            
        finally:
            os.unlink(temp_file)
    
    def test_remove_site(self, test_config):
        """Test removing a site configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            # Verify site exists initially
            assert "test_site_1" in manager.sites
            
            # Remove site
            manager.remove_site("test_site_1")
            
            # Verify site was removed
            assert "test_site_1" not in manager.sites
            
        finally:
            os.unlink(temp_file)
    
    def test_save_config(self, test_config):
        """Test saving configuration to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            # Modify a site
            manager.update_site("test_site_1", name="Modified Site")
            
            # Save config
            manager.save_config()
            
            # Reload config to verify changes were saved
            new_manager = ConfigManager(temp_file)
            modified_site = new_manager.sites["test_site_1"]
            assert modified_site.name == "Modified Site"
            
        finally:
            os.unlink(temp_file)
    
    def test_get_firecrawl_config(self, test_config):
        """Test getting Firecrawl configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            firecrawl_config = manager.get_firecrawl_config()
            
            assert firecrawl_config["api_key"] == "test-api-key"
            assert firecrawl_config["base_url"] == "https://api.firecrawl.dev"
            
        finally:
            os.unlink(temp_file)
    
    def test_get_system_config(self, test_config):
        """Test getting system configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        try:
            manager = ConfigManager(temp_file)
            
            system_config = manager.get_system_config()
            
            assert system_config["output_directory"] == "test_output"
            assert system_config["log_level"] == "DEBUG"
            assert system_config["max_retries"] == 2
            assert system_config["timeout_seconds"] == 10
            
        finally:
            os.unlink(temp_file) 