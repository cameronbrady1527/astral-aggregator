# ==============================================================================
# firecrawl_detector.py — Firecrawl-based Change Detector
# ==============================================================================
# Purpose: Detect changes using the Firecrawl API for sophisticated change tracking
# Sections: Imports, FirecrawlDetector Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

# Third Party -----
from firecrawl import FirecrawlApp, ScrapeOptions

# Internal -----
from .base_detector import BaseDetector, ChangeResult

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['FirecrawlDetector']


class FirecrawlDetector(BaseDetector):
    """Detects changes using the Firecrawl API with change tracking."""
    
    def __init__(self, site_config: Any, api_key: str, base_url: str = "https://api.firecrawl.dev"):
        super().__init__(site_config)
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.app = FirecrawlApp(api_key=self.api_key)
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get the current state using Firecrawl's crawl with change tracking."""
        try:
            crawl_data = await self._crawl_with_change_tracking()
            
            return {
                "detection_method": "firecrawl",
                "site_url": self.site_url,
                "crawl_data": crawl_data,
                "captured_at": datetime.now().isoformat(),
                "firecrawl_base_url": self.base_url
            }
        except Exception as e:
            return {
                "detection_method": "firecrawl",
                "site_url": self.site_url,
                "error": str(e),
                "captured_at": datetime.now().isoformat(),
                "firecrawl_base_url": self.base_url
            }
    
    async def detect_changes(self, previous_state: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """Detect changes using Firecrawl's change tracking API."""
        result = self.create_result()
        
        try:
            if previous_state is None:
                crawl_data = await self._crawl_with_change_tracking()
                result.metadata["message"] = "First run - established baseline with crawl"
                result.metadata["total_pages_crawled"] = len(crawl_data.get("data", []))
                return result
            
            # For subsequent runs, we'll use the same crawl with change tracking
            # The API will automatically compare with the previous state
            crawl_data = await self._crawl_with_change_tracking()
            
            # Process change tracking data
            for page_data in crawl_data.get("data", []):
                change_tracking = page_data.get("changeTracking", {})
                change_status = change_tracking.get("changeStatus", "unknown")
                visibility = change_tracking.get("visibility", "unknown")
                
                # Only report actual changes
                if change_status in ["new", "changed", "removed"]:
                    url = page_data.get("metadata", {}).get("url", "")
                    title = page_data.get("metadata", {}).get("title", "")
                    
                    result.add_change(
                        change_type=change_status,
                        url=url,
                        title=title,
                        visibility=visibility,
                        previous_scrape_at=change_tracking.get("previousScrapeAt"),
                        firecrawl_data=page_data
                    )
            
            result.metadata.update({
                "firecrawl_response": crawl_data,
                "api_endpoint": "FirecrawlApp SDK",
                "total_pages_crawled": len(crawl_data.get("data", [])),
                "credits_used": crawl_data.get("creditsUsed", 0),
                "performance_metrics": crawl_data.get("performance_metrics", {})
            })
            
        except Exception as e:
            result.metadata["error"] = str(e)
            result.metadata["api_endpoint"] = "FirecrawlApp SDK"
        
        return result
    
    async def _crawl_with_change_tracking(self) -> Dict[str, Any]:
        """Crawl the site with change tracking enabled using the Firecrawl SDK."""
        try:
            # Run the crawl in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._sync_crawl_with_change_tracking
            )
            return result
        except Exception as e:
            raise Exception(f"Firecrawl SDK error: {e}")
    
    def _sync_crawl_with_change_tracking(self) -> Dict[str, Any]:
        """Synchronous crawl method for the SDK."""
        start_time = time.time()
        try:
            # Get configuration settings for optimization
            config = getattr(self, 'firecrawl_config', {})
            limit = config.get('limit', 10)  # Use limit parameter (correct!)
            wait_for = config.get('wait_for', 100)  # Reduced to 100ms
            timeout = config.get('timeout', 15000)  # 15 second timeout
            max_age = config.get('max_age', 3600000)  # 1 hour cache for 500% speed boost
            
            print(f"🕷️ Starting Firecrawl detection for {self.site_url}")
            print(f"   📊 Limit: {limit} pages, Wait time: {wait_for}ms, Timeout: {timeout}ms")
            print(f"   ⚡ Using cached data (maxAge: {max_age}ms) for 500% speed boost")
            
            # Optimized settings for speed while keeping CSS selectors for completeness
            scrape_options = ScrapeOptions(
                formats=['markdown', 'changeTracking'],
                # Fast processing settings
                waitFor=wait_for,  # Correct parameter name
                timeout=timeout,
                # Performance optimizations
                onlyMainContent=True,  # Focus on main content only
                blockAds=True,  # Block ads for speed
                maxAge=max_age,  # Use cached data for 500% speed boost
                # Keep CSS selectors for completeness (as requested)
                includeTags=['main', 'article', '.content', '#content', 'body'],
                # More aggressive exclusions to reduce processing overhead
                excludeTags=[
                    'nav', 'footer', '.sidebar', '.ads', '.comments', 
                    '.header', '.menu', '.navigation', '.breadcrumb',
                    '.social', '.share', '.related', '.recommended',
                    '.widget', '.sidebar-widget', '.footer-widget',
                    '.advertisement', '.banner', '.promo', '.sponsored',
                    '.cookie-notice', '.privacy-notice', '.disclaimer',
                    '.breadcrumbs', '.pagination', '.search-results',
                    '.related-posts', '.popular-posts', '.trending',
                    '.newsletter', '.subscribe', '.signup',
                    '.social-media', '.social-links', '.social-icons',
                    '.author-bio', '.author-info', '.author-avatar',
                    '.tags', '.categories', '.meta', '.metadata',
                    '.date', '.time', '.published', '.updated',
                    '.print', '.email', '.share-this', '.bookmark',
                    '.favorite', '.like', '.vote', '.rating',
                    '.review', '.comment', '.feedback', '.contact',
                    '.search', '.filter', '.sort', '.view-options'
                ]
            )
            
            print(f"   🔄 Starting optimized crawl with limit={limit}...")
            crawl_start = time.time()
            result = self.app.crawl_url(
                self.site_url,
                limit=limit,  # ✅ Use the correct limit parameter
                scrape_options=scrape_options
            )
            crawl_duration = time.time() - crawl_start
            
            # Handle both dictionary and object responses from Firecrawl SDK
            if hasattr(result, 'data'):
                # New SDK format: CrawlStatusResponse object
                pages_crawled = len(result.data) if result.data else 0
                credits_used = getattr(result, 'creditsUsed', 0)
                # Convert to dictionary format for compatibility
                result_dict = {
                    'data': result.data if result.data else [],
                    'creditsUsed': credits_used,
                    'status': getattr(result, 'status', 'unknown'),
                    'message': getattr(result, 'message', '')
                }
            else:
                # Old SDK format: dictionary
                pages_crawled = len(result.get("data", []))
                credits_used = result.get("creditsUsed", 0)
                result_dict = result
            
            total_duration = time.time() - start_time
            
            # Performance metrics
            pages_per_second = pages_crawled / crawl_duration if crawl_duration > 0 else 0
            credits_per_second = credits_used / crawl_duration if crawl_duration > 0 else 0
            
            # Verify we didn't exceed the limit
            if pages_crawled > limit:
                print(f"   ⚠️ Warning: Crawled {pages_crawled} pages (exceeded limit of {limit})")
            else:
                print(f"   ✅ Crawl completed: {pages_crawled} pages, {credits_used} credits used")
            
            print(f"   ⏱️ Performance: {crawl_duration:.2f}s crawl, {total_duration:.2f}s total")
            print(f"   📈 Rate: {pages_per_second:.2f} pages/sec, {credits_per_second:.2f} credits/sec")
            
            # Add performance metrics to result
            result_dict['performance_metrics'] = {
                'crawl_duration_seconds': crawl_duration,
                'total_duration_seconds': total_duration,
                'pages_per_second': pages_per_second,
                'credits_per_second': credits_per_second,
                'pages_crawled': pages_crawled,
                'credits_used': credits_used
            }
            
            return result_dict
        except Exception as e:
            total_duration = time.time() - start_time
            print(f"   ❌ Firecrawl error after {total_duration:.2f}s: {e}")
            raise Exception(f"Firecrawl SDK crawl error: {e}") 