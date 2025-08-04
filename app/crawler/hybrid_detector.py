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
    
    async def detect_changes(self, previous_baseline: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """Detect changes using hybrid approach combining sitemap and content analysis."""
        result = self.create_result()
        
        try:
            # Get current state
            current_state = await self.get_current_state()
            
            if previous_baseline is None:
                result.metadata["message"] = "First run - establishing hybrid baseline"
                result.metadata["total_urls"] = len(current_state.get("urls", []))
                result.metadata["total_content_hashes"] = len(current_state.get("content_hashes", {}))
                return result
            
            # Compare sitemap URLs
            baseline_urls = set(previous_baseline.get("sitemap_state", {}).get("urls", []))
            current_urls = set(current_state.get("urls", []))
            
            new_urls = current_urls - baseline_urls
            deleted_urls = baseline_urls - current_urls
            common_urls = baseline_urls & current_urls
            
            # Add sitemap changes
            for url in new_urls:
                result.add_change("new", url, title=f"New page: {url}")
            
            for url in deleted_urls:
                result.add_change("deleted", url, title=f"Removed page: {url}")
            
            # Compare content hashes for common URLs
            baseline_hashes = previous_baseline.get("content_hashes", {})
            current_hashes = current_state.get("content_hashes", {})
            
            content_changes = 0
            for url in common_urls:
                baseline_hash = baseline_hashes.get(url, {}).get("hash")
                current_hash = current_hashes.get(url, {}).get("hash")
                
                if baseline_hash and current_hash and baseline_hash != current_hash:
                    result.add_change(
                        "content_changed",
                        url,
                        title=f"Content modified: {url}",
                        description=f"Content hash changed from {baseline_hash[:8]} to {current_hash[:8]}"
                    )
                    content_changes += 1
            
            # Add metadata
            result.metadata.update({
                "total_urls": len(current_urls),
                "new_urls": len(new_urls),
                "deleted_urls": len(deleted_urls),
                "content_changes": content_changes,
                "hybrid_analysis": True
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