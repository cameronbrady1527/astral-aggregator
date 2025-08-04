# ==============================================================================
# test_change_detector.py — Unit Tests for Change Detector
# ==============================================================================
# Purpose: Test the main change detection orchestrator
# ==============================================================================

import pytest
import tempfile
import yaml
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

from app.crawler.change_detector import ChangeDetector
from app.crawler.base_detector import ChangeResult


class TestChangeDetector:
    """Test the ChangeDetector class."""
    
    @pytest.fixture
    def temp_config_file(self, test_config):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        import os
        try:
            os.unlink(temp_file)
        except FileNotFoundError:
            pass
    
    def test_change_detector_initialization(self, temp_config_file):
        """Test ChangeDetector initialization."""
        detector = ChangeDetector(temp_config_file)
        
        assert detector.config_manager is not None
        assert detector.writer is not None
        assert detector.firecrawl_config is not None
        assert detector.firecrawl_config["api_key"] == "test-api-key"
    
    def test_change_detector_initialization_with_env_var(self, temp_config_file):
        """Test ChangeDetector initialization using environment variable."""
        import os
        original_config = os.environ.get('CONFIG_FILE')
        os.environ['CONFIG_FILE'] = temp_config_file
        
        try:
            detector = ChangeDetector()
            assert detector.config_manager is not None
        finally:
            if original_config:
                os.environ['CONFIG_FILE'] = original_config
            else:
                os.environ.pop('CONFIG_FILE', None)
    
    @pytest.mark.asyncio
    async def test_detect_changes_for_site_success(self, temp_config_file):
        """Test successful change detection for a site."""
        detector = ChangeDetector(temp_config_file)
        
        # Mock the detection method
        with patch.object(detector, '_run_detection_method') as mock_run_method:
            mock_result = {
                "status": "success",
                "changes_found": 2,
                "detection_time": "2024-01-01T00:00:00Z"
            }
            mock_run_method.return_value = mock_result
            
            # Mock the writer
            with patch.object(detector.writer, 'write_changes') as mock_write:
                mock_write.return_value = "test_output.json"
                
                result = await detector.detect_changes_for_site("test_site_1")
                
                assert result["site_id"] == "test_site_1"
                assert result["site_name"] == "Test Site 1"
                assert "detection_time" in result
                assert "methods" in result
                assert "sitemap" in result["methods"]
                assert result["output_file"] == "test_output.json"
    
    @pytest.mark.asyncio
    async def test_detect_changes_for_site_not_found(self, temp_config_file):
        """Test change detection for non-existent site."""
        detector = ChangeDetector(temp_config_file)
        
        with pytest.raises(ValueError, match="Site 'nonexistent' not found"):
            await detector.detect_changes_for_site("nonexistent")
    
    @pytest.mark.asyncio
    async def test_detect_changes_for_site_method_error(self, temp_config_file):
        """Test change detection when a method fails."""
        detector = ChangeDetector(temp_config_file)
        
        # Mock the detection method to raise an exception
        with patch.object(detector, '_run_detection_method') as mock_run_method:
            mock_run_method.side_effect = Exception("Detection failed")
            
            result = await detector.detect_changes_for_site("test_site_1")
            
            assert result["site_id"] == "test_site_1"
            assert "methods" in result
            assert "sitemap" in result["methods"]
            assert "error" in result["methods"]["sitemap"]
            assert "Detection failed" in result["methods"]["sitemap"]["error"]
    
    @pytest.mark.asyncio
    async def test_detect_changes_for_all_sites(self, temp_config_file):
        """Test detecting changes for all active sites."""
        detector = ChangeDetector(temp_config_file)
        
        # Mock the site detection
        with patch.object(detector, 'detect_changes_for_site') as mock_detect_site:
            mock_detect_site.return_value = {
                "site_id": "test_site_1",
                "status": "success"
            }
            
            result = await detector.detect_changes_for_all_sites()
            
            assert "detection_time" in result
            assert "sites" in result
            assert len(result["sites"]) == 2  # test_site_1 and test_site_2 are active
            assert "test_site_1" in result["sites"]
            assert "test_site_2" in result["sites"]
    
    @pytest.mark.asyncio
    async def test_detect_changes_for_all_sites_with_errors(self, temp_config_file):
        """Test detecting changes for all sites when some fail."""
        detector = ChangeDetector(temp_config_file)
        
        # Mock the site detection to fail for one site
        def mock_detect_site(site_id):
            if site_id == "test_site_1":
                return {"site_id": "test_site_1", "status": "success"}
            else:
                raise Exception("Site failed")
        
        with patch.object(detector, 'detect_changes_for_site', side_effect=mock_detect_site):
            result = await detector.detect_changes_for_all_sites()
            
            assert "sites" in result
            assert result["sites"]["test_site_1"]["status"] == "success"
            assert "error" in result["sites"]["test_site_2"]
    
    @pytest.mark.asyncio
    async def test_run_detection_method_sitemap(self, temp_config_file):
        """Test running sitemap detection method."""
        detector = ChangeDetector(temp_config_file)
        site_config = detector.config_manager.get_site("test_site_1")
        
        # Mock the detector creation and detection
        with patch.object(detector, '_create_detector') as mock_create_detector:
            mock_detector = MagicMock()
            mock_detector.detect_changes = AsyncMock(return_value=ChangeResult("sitemap", "Test Site"))
            mock_detector.get_current_state = AsyncMock(return_value={"urls": []})
            mock_create_detector.return_value = mock_detector
            
            # Mock previous state
            with patch.object(detector, '_get_previous_state') as mock_get_state:
                mock_get_state.return_value = None
                
                result = await detector._run_detection_method(site_config, "sitemap")
                
                assert result is not None
                mock_create_detector.assert_called_once_with(site_config, "sitemap")
                mock_detector.detect_changes.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_detection_method_firecrawl(self, temp_config_file):
        """Test running firecrawl detection method."""
        detector = ChangeDetector(temp_config_file)
        site_config = detector.config_manager.get_site("test_site_2")  # Has firecrawl method
        
        # Mock the detector creation and detection
        with patch.object(detector, '_create_detector') as mock_create_detector:
            mock_detector = MagicMock()
            mock_detector.detect_changes = AsyncMock(return_value=ChangeResult("firecrawl", "Test Site"))
            mock_detector.get_current_state = AsyncMock(return_value={"pages": {}})
            mock_create_detector.return_value = mock_detector
            
            # Mock previous state
            with patch.object(detector, '_get_previous_state') as mock_get_state:
                mock_get_state.return_value = None
                
                result = await detector._run_detection_method(site_config, "firecrawl")
                
                assert result is not None
                mock_create_detector.assert_called_once_with(site_config, "firecrawl")
    
    def test_create_detector_sitemap(self, temp_config_file):
        """Test creating sitemap detector."""
        detector = ChangeDetector(temp_config_file)
        site_config = detector.config_manager.get_site("test_site_1")
        
        from app.crawler.sitemap_detector import SitemapDetector
        
        result = detector._create_detector(site_config, "sitemap")
        
        assert isinstance(result, SitemapDetector)
        assert result.site_config == site_config
    
    def test_create_detector_firecrawl(self, temp_config_file):
        """Test creating firecrawl detector."""
        detector = ChangeDetector(temp_config_file)
        site_config = detector.config_manager.get_site("test_site_2")
        
        from app.crawler.firecrawl_detector import FirecrawlDetector
        
        result = detector._create_detector(site_config, "firecrawl")
        
        assert isinstance(result, FirecrawlDetector)
        assert result.site_config == site_config
    
    def test_create_detector_content(self, temp_config_file):
        """Test creating content detector."""
        detector = ChangeDetector(temp_config_file)
        site_config = detector.config_manager.get_site("test_site_1")
        
        from app.crawler.content_detector import ContentDetector
        
        result = detector._create_detector(site_config, "content")
        
        assert isinstance(result, ContentDetector)
        assert result.site_config == site_config
    
    def test_create_detector_hybrid(self, temp_config_file):
        """Test creating hybrid detector."""
        detector = ChangeDetector(temp_config_file)
        site_config = detector.config_manager.get_site("test_site_1")
        
        from app.crawler.hybrid_detector import HybridDetector
        
        result = detector._create_detector(site_config, "hybrid")
        
        assert isinstance(result, HybridDetector)
        assert result.site_config == site_config
    
    def test_create_detector_unknown_method(self, temp_config_file):
        """Test creating detector with unknown method."""
        detector = ChangeDetector(temp_config_file)
        site_config = detector.config_manager.get_site("test_site_1")
        
        with pytest.raises(ValueError, match="Unknown detection method"):
            detector._create_detector(site_config, "unknown_method")
    
    @pytest.mark.asyncio
    async def test_get_previous_state(self, temp_config_file):
        """Test getting previous state."""
        detector = ChangeDetector(temp_config_file)
        
        # Mock the writer to return a previous state file
        with patch.object(detector.writer, 'get_previous_state_file') as mock_get_file:
            mock_get_file.return_value = "previous_state.json"
            
            with patch.object(detector.writer, 'read_json_file') as mock_read:
                mock_read.return_value = {"state": "data"}
                
                result = await detector._get_previous_state("Test Site", "sitemap")
                
                assert result == "data"
                mock_get_file.assert_called_once_with("Test Site", "sitemap")
                mock_read.assert_called_once_with("previous_state.json")
    
    @pytest.mark.asyncio
    async def test_get_previous_state_no_file(self, temp_config_file):
        """Test getting previous state when no file exists."""
        detector = ChangeDetector(temp_config_file)
        
        # Mock the writer to return None
        with patch.object(detector.writer, 'get_previous_state_file') as mock_get_file:
            mock_get_file.return_value = None
            
            result = await detector._get_previous_state("Test Site", "sitemap")
            
            assert result is None
    
    def test_get_site_id(self, temp_config_file):
        """Test getting site ID from site config."""
        detector = ChangeDetector(temp_config_file)
        site_config = detector.config_manager.get_site("test_site_1")
        
        site_id = detector._get_site_id(site_config)
        
        assert site_id == "test_site_1"
    
    def test_get_site_status(self, temp_config_file):
        """Test getting site status."""
        detector = ChangeDetector(temp_config_file)
        
        status = detector.get_site_status("test_site_1")
        
        assert "site_id" in status
        assert "site_name" in status
        assert "is_active" in status
        assert "detection_methods" in status
        assert "recent_change_files" in status
        assert "latest_state_file" in status
        assert status["site_id"] == "test_site_1"
        assert status["site_name"] == "Test Site 1"
        assert status["is_active"] is True
    
    def test_get_site_status_nonexistent(self, temp_config_file):
        """Test getting status for non-existent site."""
        detector = ChangeDetector(temp_config_file)
        
        status = detector.get_site_status("nonexistent")
        
        assert "error" in status
        assert "Site 'nonexistent' not found" in status["error"]
    
    def test_list_sites(self, temp_config_file):
        """Test listing all sites."""
        detector = ChangeDetector(temp_config_file)
        
        sites = detector.list_sites()
        
        assert len(sites) == 3  # All sites including inactive
        site_ids = [site["site_id"] for site in sites]
        assert "test_site_1" in site_ids
        assert "test_site_2" in site_ids
        assert "test_site_3" in site_ids
        
        # Check that active sites are marked correctly
        active_sites = [site for site in sites if site["is_active"]]
        assert len(active_sites) == 2 