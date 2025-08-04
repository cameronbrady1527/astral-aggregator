# ==============================================================================
# test_baseline_merger.py — Tests for BaselineMerger
# ==============================================================================
# Purpose: Test baseline merging logic with various scenarios
# Sections: Imports, Test Classes
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import pytest
from datetime import datetime
from typing import Dict, Any, List

# Internal -----
from app.utils.baseline_merger import BaselineMerger


class TestBaselineMerger:
    """Test cases for BaselineMerger class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.merger = BaselineMerger()
        
        # Sample previous baseline
        self.previous_baseline = {
            "site_id": "test_site",
            "site_name": "Test Site",
            "baseline_date": "20240101",
            "created_at": "2024-01-01T00:00:00",
            "sitemap_state": {
                "urls": [
                    "https://example.com/page1",
                    "https://example.com/page2", 
                    "https://example.com/page3",
                    "https://example.com/page4"
                ]
            },
            "content_hashes": {
                "https://example.com/page1": {"hash": "abc123", "content_length": 100},
                "https://example.com/page2": {"hash": "def456", "content_length": 200},
                "https://example.com/page3": {"hash": "ghi789", "content_length": 300},
                "https://example.com/page4": {"hash": "jkl012", "content_length": 400}
            },
            "total_urls": 4,
            "total_content_hashes": 4
        }
        
        # Sample current state
        self.current_state = {
            "sitemap_state": {
                "urls": [
                    "https://example.com/page1",
                    "https://example.com/page2",
                    "https://example.com/page5",  # New page
                    "https://example.com/page6"   # New page
                ]
            },
            "content_hashes": {
                "https://example.com/page1": {"hash": "abc123", "content_length": 100},  # Unchanged
                "https://example.com/page2": {"hash": "def999", "content_length": 250},  # Modified
                "https://example.com/page5": {"hash": "mno345", "content_length": 500},  # New
                "https://example.com/page6": {"hash": "pqr678", "content_length": 600}   # New
            }
        }
    
    def test_change_type_mappings(self):
        """Test that all change types are properly mapped."""
        # Test new URL types
        assert self.merger.change_type_mappings["new"] == "new_urls"
        assert self.merger.change_type_mappings["new_content"] == "new_urls"
        assert self.merger.change_type_mappings["sitemap_new"] == "new_urls"
        
        # Test deleted URL types
        assert self.merger.change_type_mappings["deleted"] == "deleted_urls"
        assert self.merger.change_type_mappings["page_deleted"] == "deleted_urls"
        assert self.merger.change_type_mappings["removed"] == "deleted_urls"
        assert self.merger.change_type_mappings["sitemap_deleted"] == "deleted_urls"
        assert self.merger.change_type_mappings["removed_from_sitemap"] == "deleted_urls"
        
        # Test modified URL types
        assert self.merger.change_type_mappings["modified"] == "modified_urls"
        assert self.merger.change_type_mappings["content_changed"] == "modified_urls"
        assert self.merger.change_type_mappings["content_modified"] == "modified_urls"
        assert self.merger.change_type_mappings["changed"] == "modified_urls"
    
    def test_analyze_changes_basic(self):
        """Test basic change analysis."""
        changes = [
            {"url": "https://example.com/page5", "change_type": "new"},
            {"url": "https://example.com/page3", "change_type": "deleted"},
            {"url": "https://example.com/page2", "change_type": "modified"}
        ]
        
        result = self.merger._analyze_changes(changes)
        
        assert "https://example.com/page5" in result["new_urls"]
        assert "https://example.com/page3" in result["deleted_urls"]
        assert "https://example.com/page2" in result["modified_urls"]
        assert len(result["unchanged_urls"]) == 0
    
    def test_analyze_changes_all_types(self):
        """Test analysis with all change type variations."""
        changes = [
            {"url": "https://example.com/page5", "change_type": "new_content"},
            {"url": "https://example.com/page3", "change_type": "page_deleted"},
            {"url": "https://example.com/page2", "change_type": "content_changed"},
            {"url": "https://example.com/page4", "change_type": "removed_from_sitemap"},
            {"url": "https://example.com/page6", "change_type": "sitemap_new"},
            {"url": "https://example.com/page7", "change_type": "changed"}
        ]
        
        result = self.merger._analyze_changes(changes)
        
        assert "https://example.com/page5" in result["new_urls"]
        assert "https://example.com/page6" in result["new_urls"]
        assert "https://example.com/page3" in result["deleted_urls"]
        assert "https://example.com/page4" in result["deleted_urls"]
        assert "https://example.com/page2" in result["modified_urls"]
        assert "https://example.com/page7" in result["modified_urls"]
    
    def test_analyze_changes_unknown_type(self):
        """Test handling of unknown change types."""
        changes = [
            {"url": "https://example.com/page5", "change_type": "unknown_type"},
            {"url": "https://example.com/page6", "change_type": "new"}
        ]
        
        result = self.merger._analyze_changes(changes)
        
        # Unknown type should be ignored
        assert "https://example.com/page5" not in result["new_urls"]
        assert "https://example.com/page5" not in result["deleted_urls"]
        assert "https://example.com/page5" not in result["modified_urls"]
        
        # Known type should be processed
        assert "https://example.com/page6" in result["new_urls"]
    
    def test_validate_change_consistency_no_conflicts(self):
        """Test validation with no conflicting changes."""
        change_info = {
            "new_urls": {"https://example.com/page5"},
            "deleted_urls": {"https://example.com/page3"},
            "modified_urls": {"https://example.com/page2"},
            "unchanged_urls": set()
        }
        
        result = self.merger._validate_change_consistency(change_info)
        
        assert result["is_valid"] is True
        assert len(result["warnings"]) == 0
        assert len(result["errors"]) == 0
    
    def test_validate_change_consistency_conflicts(self):
        """Test validation with conflicting changes."""
        change_info = {
            "new_urls": {"https://example.com/page5", "https://example.com/conflict1"},
            "deleted_urls": {"https://example.com/page3", "https://example.com/conflict1"},
            "modified_urls": {"https://example.com/page2", "https://example.com/conflict2"},
            "unchanged_urls": set()
        }
        
        result = self.merger._validate_change_consistency(change_info)
        
        assert result["is_valid"] is True  # Should still be valid after resolution
        assert len(result["warnings"]) == 2  # Two conflicts detected
        
        # Conflicts should be resolved
        assert "https://example.com/conflict1" not in change_info["deleted_urls"]  # Removed from deleted
        assert "https://example.com/conflict2" not in change_info["modified_urls"]  # Removed from modified
    
    def test_merge_content_hashes_basic(self):
        """Test basic content hash merging."""
        previous_hashes = {
            "https://example.com/page1": {"hash": "abc123", "content_length": 100},
            "https://example.com/page2": {"hash": "def456", "content_length": 200},
            "https://example.com/page3": {"hash": "ghi789", "content_length": 300}
        }
        
        current_hashes = {
            "https://example.com/page1": {"hash": "abc123", "content_length": 100},  # Unchanged
            "https://example.com/page2": {"hash": "def999", "content_length": 250},  # Modified
            "https://example.com/page4": {"hash": "jkl012", "content_length": 400}   # New
        }
        
        change_info = {
            "new_urls": {"https://example.com/page4"},
            "deleted_urls": {"https://example.com/page3"},
            "modified_urls": {"https://example.com/page2"},
            "unchanged_urls": {"https://example.com/page1"}
        }
        
        result = self.merger._merge_content_hashes(previous_hashes, current_hashes, change_info)
        
        # Should contain unchanged, new, and modified URLs
        assert "https://example.com/page1" in result
        assert result["https://example.com/page1"]["hash"] == "abc123"  # Unchanged hash
        
        assert "https://example.com/page2" in result
        assert result["https://example.com/page2"]["hash"] == "def999"  # Updated hash
        
        assert "https://example.com/page4" in result
        assert result["https://example.com/page4"]["hash"] == "jkl012"  # New hash
        
        # Should not contain deleted URL
        assert "https://example.com/page3" not in result
        
        assert len(result) == 3
    
    def test_merge_baselines_complete(self):
        """Test complete baseline merging process."""
        changes = [
            {"url": "https://example.com/page5", "change_type": "new"},
            {"url": "https://example.com/page6", "change_type": "new"},
            {"url": "https://example.com/page3", "change_type": "deleted"},
            {"url": "https://example.com/page4", "change_type": "deleted"},
            {"url": "https://example.com/page2", "change_type": "modified"}
        ]
        
        result = self.merger.merge_baselines(
            self.previous_baseline, 
            self.current_state, 
            changes
        )
        
        # Check metadata
        assert result["baseline_date"] == datetime.now().strftime("%Y%m%d")
        assert result["previous_baseline_date"] == "20240101"
        assert result["changes_applied"] == 5
        assert result["evolution_type"] == "automatic_update"
        
        # Check sitemap state
        assert result["sitemap_state"]["urls"] == self.current_state["sitemap_state"]["urls"]
        
        # Check content hashes
        content_hashes = result["content_hashes"]
        assert len(content_hashes) == 4  # 2 unchanged + 2 new
        
        # Unchanged URL
        assert "https://example.com/page1" in content_hashes
        assert content_hashes["https://example.com/page1"]["hash"] == "abc123"
        
        # Modified URL (should have new hash)
        assert "https://example.com/page2" in content_hashes
        assert content_hashes["https://example.com/page2"]["hash"] == "def999"
        
        # New URLs
        assert "https://example.com/page5" in content_hashes
        assert "https://example.com/page6" in content_hashes
        
        # Deleted URLs should not be present
        assert "https://example.com/page3" not in content_hashes
        assert "https://example.com/page4" not in content_hashes
        
        # Check counts
        assert result["total_content_hashes"] == 4
        assert result["total_urls"] == 4
        
        # Check change summary
        summary = result["change_summary"]
        assert summary["new_urls"] == 2
        assert summary["deleted_urls"] == 2
        assert summary["modified_urls"] == 1
        assert summary["unchanged_urls"] == 1
    
    def test_merge_baselines_no_changes(self):
        """Test baseline merging when no changes are detected."""
        changes = []
        
        result = self.merger.merge_baselines(
            self.previous_baseline, 
            self.current_state, 
            changes
        )
        
        # Should still update metadata
        assert result["baseline_date"] == datetime.now().strftime("%Y%m%d")
        assert result["changes_applied"] == 0
        
        # Should keep all previous content hashes
        assert len(result["content_hashes"]) == 4
        assert "https://example.com/page1" in result["content_hashes"]
        assert "https://example.com/page2" in result["content_hashes"]
        assert "https://example.com/page3" in result["content_hashes"]
        assert "https://example.com/page4" in result["content_hashes"]
    
    def test_merge_baselines_missing_current_hash(self):
        """Test handling when current state is missing expected hashes."""
        changes = [
            {"url": "https://example.com/page5", "change_type": "new"},
            {"url": "https://example.com/page2", "change_type": "modified"}
        ]
        
        # Remove page2 from current state to simulate missing hash
        incomplete_current_state = self.current_state.copy()
        del incomplete_current_state["content_hashes"]["https://example.com/page2"]
        
        result = self.merger.merge_baselines(
            self.previous_baseline, 
            incomplete_current_state, 
            changes
        )
        
        # Should still work, but page2 won't be in the result
        assert "https://example.com/page5" in result["content_hashes"]
        assert "https://example.com/page2" not in result["content_hashes"]
    
    def test_validate_merge_result(self):
        """Test merge result validation."""
        changes = [
            {"url": "https://example.com/page5", "change_type": "new"},
            {"url": "https://example.com/page3", "change_type": "deleted"},
            {"url": "https://example.com/page2", "change_type": "modified"}
        ]
        
        new_baseline = self.merger.merge_baselines(
            self.previous_baseline, 
            self.current_state, 
            changes
        )
        
        validation_result = self.merger.validate_merge_result(
            self.previous_baseline,
            new_baseline,
            changes
        )
        
        assert validation_result["is_valid"] is True
        assert len(validation_result["errors"]) == 0
    
    def test_create_initial_baseline(self):
        """Test initial baseline creation."""
        result = self.merger.create_initial_baseline(
            "test_site",
            "Test Site",
            self.current_state
        )
        
        assert result["site_id"] == "test_site"
        assert result["site_name"] == "Test Site"
        assert result["baseline_date"] == datetime.now().strftime("%Y%m%d")
        assert result["evolution_type"] == "initial_creation"
        assert result["sitemap_state"] == self.current_state["sitemap_state"]
        assert result["content_hashes"] == self.current_state["content_hashes"]
        assert result["total_urls"] == 4
        assert result["total_content_hashes"] == 4
    
    def test_merge_baselines_error_handling(self):
        """Test error handling in baseline merging."""
        # Test with invalid previous baseline
        invalid_baseline = None
        
        result = self.merger.merge_baselines(
            invalid_baseline, 
            self.current_state, 
            []
        )
        
        # Should return the invalid baseline as fallback
        assert result == invalid_baseline
    
    def test_edge_case_empty_changes(self):
        """Test edge case with empty changes list."""
        changes = []
        
        result = self.merger._analyze_changes(changes)
        
        assert len(result["new_urls"]) == 0
        assert len(result["deleted_urls"]) == 0
        assert len(result["modified_urls"]) == 0
        assert len(result["unchanged_urls"]) == 0
    
    def test_edge_case_malformed_changes(self):
        """Test edge case with malformed change data."""
        changes = [
            {"url": "", "change_type": "new"},  # Empty URL
            {"url": "https://example.com/page1", "change_type": ""},  # Empty change type
            {"url": "https://example.com/page2"},  # Missing change type
            {"change_type": "new"},  # Missing URL
            {"url": "https://example.com/page3", "change_type": "new"}  # Valid
        ]
        
        result = self.merger._analyze_changes(changes)
        
        # Should only process the valid change
        assert "https://example.com/page3" in result["new_urls"]
        assert len(result["new_urls"]) == 1 