# ==============================================================================
# base_detector.py — Base Detector Class for Change Detection
# ==============================================================================
# Purpose: Abstract base class for different change detection methods
# Sections: Imports, ChangeResult Class, BaseDetector Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['ChangeResult', 'BaseDetector']


class ChangeResult:
    """Represents the result of a change detection operation."""
    
    def __init__(self, detection_method: str, site_name: str):
        self.detection_method = detection_method
        self.site_name = site_name
        self.detection_time = datetime.now().isoformat()
        self.changes: List[Dict[str, Any]] = []
        self.summary = {
            "total_changes": 0,
            "new_pages": 0,
            "modified_pages": 0,
            "deleted_pages": 0
        }
        self.metadata: Dict[str, Any] = {}
    
    def add_change(self, change_type: str, url: str, **kwargs):
        """Add a change to the result."""
        change = {
            "url": url,
            "change_type": change_type,
            "detected_at": datetime.now().isoformat(),
            **kwargs
        }
        self.changes.append(change)
        
        self.summary["total_changes"] += 1
        if change_type == "new":
            self.summary["new_pages"] += 1
        elif change_type == "modified":
            self.summary["modified_pages"] += 1
        elif change_type == "deleted":
            self.summary["deleted_pages"] += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "detection_method": self.detection_method,
            "site_name": self.site_name,
            "detection_time": self.detection_time,
            "changes": self.changes,
            "summary": self.summary,
            "metadata": self.metadata
        }


class BaseDetector(ABC):
    """Abstract base class for change detection methods."""
    
    def __init__(self, site_config: Any):
        """Initialize the detector with site configuration."""
        self.site_config = site_config
        self.site_name = site_config.name
        self.site_url = site_config.url
    
    @abstractmethod
    async def detect_changes(self, previous_baseline: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """
        Detect changes in the website against a baseline.
        
        Args:
            previous_baseline: The previous baseline to compare against. 
                              If None, this is the first run and should establish a baseline.
        
        Returns:
            ChangeResult: The result of the change detection operation
        """
        pass
    
    @abstractmethod
    async def get_current_state(self) -> Dict[str, Any]:
        """Get the current state of the website."""
        pass
    
    def create_result(self) -> ChangeResult:
        """Create a new ChangeResult instance."""
        return ChangeResult(
            detection_method=self.__class__.__name__.lower().replace('detector', ''),
            site_name=self.site_name
        ) 