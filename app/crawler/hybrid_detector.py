# ==============================================================================
# hybrid_detector.py — Hybrid Change Detector
# ==============================================================================
# Purpose: Combine fast sitemap detection with content change detection
# Sections: Imports, HybridDetector Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Internal -----
from .base_detector import BaseDetector, ChangeResult
from .sitemap_detector import SitemapDetector
from .content_detector import ContentDetector

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['HybridDetector']


class HybridDetector(BaseDetector):
    """Hybrid detector that combines sitemap and content detection for comprehensive monitoring."""
    
    def __init__(self, site_config: Any):
        super().__init__(site_config)
        self.sitemap_detector = SitemapDetector(site_config)
        self.content_detector = ContentDetector(site_config)
        
        # Configuration
        self.enable_content_detection = getattr(site_config, 'enable_content_detection', True)
        self.content_check_interval = getattr(site_config, 'content_check_interval', 24)  # hours
        self.last_content_check = None
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current state using both sitemap and content detection."""
        start_time = time.time()
        
        try:
            # Always run sitemap detection (fast)
            print(f"🔍 Running sitemap detection for {self.site_url}")
            sitemap_state = await self.sitemap_detector.get_current_state()
            
            # Conditionally run content detection
            content_state = None
            if self.enable_content_detection and self._should_run_content_check():
                print(f"📄 Running content detection for {self.site_url}")
                content_state = await self.content_detector.get_current_state()
                self.last_content_check = datetime.now()
            
            total_duration = time.time() - start_time
            
            return {
                "detection_method": "hybrid",
                "site_url": self.site_url,
                "sitemap_state": sitemap_state,
                "content_state": content_state,
                "total_duration": total_duration,
                "captured_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "detection_method": "hybrid",
                "site_url": self.site_url,
                "error": str(e),
                "total_duration": time.time() - start_time,
                "captured_at": datetime.now().isoformat()
            }
    
    async def detect_changes(self, previous_state: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """Detect changes using both sitemap and content detection."""
        result = self.create_result()
        
        try:
            current_state = await self.get_current_state()
            
            if previous_state is None:
                result.metadata["message"] = "First run - established hybrid baseline"
                result.metadata["total_duration"] = current_state.get("total_duration", 0)
                return result
            
            # Detect sitemap changes (always run)
            sitemap_changes = await self.sitemap_detector.detect_changes(
                previous_state.get("sitemap_state")
            )
            
            # Add sitemap changes to result
            for change in sitemap_changes.changes:
                result.add_change(
                    change["change_type"],
                    change["url"],
                    title=change.get("title", ""),
                    description=change.get("description", ""),
                    metadata=change.get("metadata", {})
                )
            
            # Detect content changes (if enabled and should run)
            content_changes = None
            if (self.enable_content_detection and 
                current_state.get("content_state") and 
                previous_state.get("content_state")):
                
                content_changes = await self.content_detector.detect_changes(
                    previous_state.get("content_state")
                )
                
                # Add content changes to result
                for change in content_changes.changes:
                    result.add_change(
                        change["change_type"],
                        change["url"],
                        title=change.get("title", ""),
                        description=change.get("description", ""),
                        metadata=change.get("metadata", {})
                    )
            
            # Update metadata
            result.metadata.update({
                "sitemap_changes": len(sitemap_changes.changes),
                "content_changes": len(content_changes.changes) if content_changes else 0,
                "total_duration": current_state.get("total_duration", 0),
                "detection_methods": ["sitemap", "content"] if content_changes else ["sitemap"]
            })
            
        except Exception as e:
            result.metadata["error"] = str(e)
        
        return result
    
    def _should_run_content_check(self) -> bool:
        """Determine if we should run content detection based on interval."""
        if not self.last_content_check:
            return True
        
        hours_since_last_check = (datetime.now() - self.last_content_check).total_seconds() / 3600
        return hours_since_last_check >= self.content_check_interval 