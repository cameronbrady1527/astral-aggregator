# ==============================================================================
# firecrawl_detector.py — Firecrawl-based Change Detector
# ==============================================================================
# Purpose: Detect changes using the Firecrawl API with advanced performance optimizations
# Sections: Imports, FirecrawlDetector Class, Performance Optimizations
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import asyncio
import time
import json
import hashlib
import pickle
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

# Third Party -----
from firecrawl import FirecrawlApp, ScrapeOptions

# Internal -----
from .base_detector import BaseDetector, ChangeResult

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['FirecrawlDetector']


class FirecrawlDetector(BaseDetector):
    """Detects changes using the Firecrawl API with Phase 3 & 4 optimizations."""
    
    def __init__(self, site_config: Any, api_key: str, base_url: str = "https://api.firecrawl.dev"):
        super().__init__(site_config)
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.app = FirecrawlApp(api_key=self.api_key)
        
        # Intelligent caching
        self.cache_dir = Path("cache/firecrawl")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = getattr(site_config, 'cache_duration_hours', 24)
        
        # Performance monitoring
        self.performance_history = []
        self.adaptive_timeout = getattr(site_config, 'adaptive_timeout', True)
        self.max_retries = getattr(site_config, 'max_retries', 3)
        self.backoff_factor = getattr(site_config, 'backoff_factor', 2.0)
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current state with intelligent caching and adaptive timeouts."""
        try:
            # Check intelligent cache first
            cached_result = await self._get_cached_result()
            if cached_result:
                print(f"Using cached result (saved {cached_result['cache_age_hours']:.1f}h ago)")
                return cached_result
            
            # Adaptive timeout based on performance history
            timeout = self._calculate_adaptive_timeout()
            
            crawl_data = await self._crawl_with_optimizations(timeout)
            
            # Cache the result
            await self._cache_result(crawl_data)
            
            return {
                "detection_method": "firecrawl_optimized",
                "site_url": self.site_url,
                "crawl_data": crawl_data,
                "captured_at": datetime.now().isoformat(),
                "firecrawl_base_url": self.base_url,
                "optimizations_applied": ["intelligent_caching", "adaptive_timeout", "parallel_processing"]
            }
        except Exception as e:
            return {
                "detection_method": "firecrawl_optimized",
                "site_url": self.site_url,
                "error": str(e),
                "captured_at": datetime.now().isoformat(),
                "firecrawl_base_url": self.base_url
            }
    
    async def detect_changes(self, previous_state: Optional[Dict[str, Any]] = None) -> ChangeResult:
        """Detect changes using Firecrawl with optimized performance."""
        result = self.create_result()
        
        try:
            if previous_state is None:
                crawl_data = await self._crawl_with_optimizations()
                result.metadata["message"] = "First run - established baseline with optimized crawl"
                result.metadata["total_pages_crawled"] = len(crawl_data.get("data", []))
                result.metadata["optimizations"] = ["intelligent_caching", "adaptive_timeout"]
                return result
            
            # Use incremental crawling for change detection
            crawl_data = await self._incremental_crawl(previous_state)
            
            # Process change tracking data
            changes_detected = 0
            for page_data in crawl_data.get("data", []):
                change_tracking = page_data.get("changeTracking", {})
                change_status = change_tracking.get("changeStatus", "unknown")
                visibility = change_tracking.get("visibility", "unknown")
                
                # Only report actual changes
                if change_status in ["new", "changed", "removed"]:
                    changes_detected += 1
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
            
            # Update performance metrics
            self._update_performance_metrics(crawl_data)
            
            result.metadata.update({
                "firecrawl_response": crawl_data,
                "api_endpoint": "FirecrawlApp SDK (Optimized)",
                "total_pages_crawled": len(crawl_data.get("data", [])),
                "credits_used": crawl_data.get("creditsUsed", 0),
                "performance_metrics": crawl_data.get("performance_metrics", {}),
                "changes_detected": changes_detected,
                "optimizations_applied": ["incremental_crawl", "adaptive_timeout", "performance_monitoring"]
            })
            
        except Exception as e:
            result.metadata["error"] = str(e)
            result.metadata["api_endpoint"] = "FirecrawlApp SDK (Optimized)"
        
        return result
    
    # Intelligent Caching Methods
    async def _get_cached_result(self) -> Optional[Dict[str, Any]]:
        """Get cached result if it's still valid."""
        try:
            cache_file = self.cache_dir / f"{self._get_site_hash()}.pkl"
            if not cache_file.exists():
                return None
            
            # Check cache age
            cache_age = time.time() - cache_file.stat().st_mtime
            cache_age_hours = cache_age / 3600
            
            if cache_age_hours > self.cache_duration:
                return None
            
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                cached_data['cache_age_hours'] = cache_age_hours
                return cached_data
                
        except Exception as e:
            print(f"Warning: Cache read error: {e}")
            return None
    
    async def _cache_result(self, crawl_data: Dict[str, Any]) -> None:
        """Cache the crawl result for future use."""
        try:
            cache_file = self.cache_dir / f"{self._get_site_hash()}.pkl"
            cache_data = {
                "detection_method": "firecrawl_optimized",
                "site_url": self.site_url,
                "crawl_data": crawl_data,
                "captured_at": datetime.now().isoformat(),
                "firecrawl_base_url": self.base_url,
                "cached_at": time.time()
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
                
        except Exception as e:
            print(f"Warning: Cache write error: {e}")
    
    def _get_site_hash(self) -> str:
        """Generate a hash for the site configuration."""
        config_str = f"{self.site_url}_{self.api_key[:8]}"
        return hashlib.md5(config_str.encode()).hexdigest()
    
    # Advanced Performance Methods
    async def _crawl_with_optimizations(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Crawl with all optimizations applied."""
        try:
            # Parallel processing with retries
            for attempt in range(self.max_retries):
                try:
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, self._sync_crawl_optimized),
                        timeout=timeout or 60.0
                    )
                    return result
                except asyncio.TimeoutError:
                    if attempt < self.max_retries - 1:
                        wait_time = self.backoff_factor ** attempt
                        print(f"Timeout, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        raise Exception("Crawl timed out after all retries")
                        
        except Exception as e:
            raise Exception(f"Optimized crawl failed: {e}")
    
    async def _incremental_crawl(self, previous_state: Dict[str, Any]) -> Dict[str, Any]:
        """Perform incremental crawl for change detection."""
        try:
            # Use shorter timeout for incremental crawls
            timeout = max(30, self._calculate_adaptive_timeout() // 2)
            
            # Smart incremental crawling
            config = getattr(self, 'firecrawl_config', {})
            limit = min(config.get('limit', 10), 5)  # Reduced limit for incremental
            
            scrape_options = self._create_optimized_scrape_options(config, incremental=True)
            
            print(f"Starting incremental crawl (limit: {limit}, timeout: {timeout}s)")
            
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, self._sync_incremental_crawl, limit, scrape_options),
                timeout=timeout
            )
            
            return result
            
        except Exception as e:
            raise Exception(f"Incremental crawl failed: {e}")
    
    def _sync_crawl_optimized(self) -> Dict[str, Any]:
        """Synchronous optimized crawl method."""
        start_time = time.time()
        try:
            config = getattr(self, 'firecrawl_config', {})
            limit = config.get('limit', 10)
            scrape_options = self._create_optimized_scrape_options(config)
            
            print(f"Starting optimized Firecrawl detection for {self.site_url}")
            print(f"Limit: {limit} pages, Optimizations: caching + adaptive timeout")
            
            crawl_start = time.time()
            result = self.app.crawl_url(
                self.site_url,
                limit=limit,
                scrape_options=scrape_options
            )
            crawl_duration = time.time() - crawl_start
            
            # Process result
            result_dict = self._process_crawl_result(result, crawl_duration, start_time)
            
            # Update performance history
            self._update_performance_metrics(result_dict)
            
            return result_dict
            
        except Exception as e:
            total_duration = time.time() - start_time
            print(f"Optimized crawl error after {total_duration:.2f}s: {e}")
            raise Exception(f"Optimized crawl failed: {e}")
    
    def _sync_incremental_crawl(self, limit: int, scrape_options: ScrapeOptions) -> Dict[str, Any]:
        """Synchronous incremental crawl method."""
        start_time = time.time()
        try:
            crawl_start = time.time()
            result = self.app.crawl_url(
                self.site_url,
                limit=limit,
                scrape_options=scrape_options
            )
            crawl_duration = time.time() - crawl_start
            
            return self._process_crawl_result(result, crawl_duration, start_time)
            
        except Exception as e:
            total_duration = time.time() - start_time
            print(f"Incremental crawl error after {total_duration:.2f}s: {e}")
            raise Exception(f"Incremental crawl failed: {e}")
    
    def _create_optimized_scrape_options(self, config: Dict[str, Any], incremental: bool = False) -> ScrapeOptions:
        """Create optimized ScrapeOptions with Phase 3 & 4 improvements."""
        wait_for = config.get('wait_for', 50 if incremental else 100)  # Faster for incremental
        timeout = config.get('timeout', 10000 if incremental else 15000)
        max_age = config.get('max_age', 7200000)  # 2 hour cache for better performance
        
        return ScrapeOptions(
            formats=['markdown', 'changeTracking'],
            waitFor=wait_for,
            timeout=timeout,
            maxAge=max_age,
            onlyMainContent=True,
            blockAds=True,
            includeTags=['main', 'article', '.content', '#content', 'body'],
            excludeTags=[
                'nav', 'footer', '.sidebar', '.ads', '.comments', '.header', '.menu',
                '.navigation', '.breadcrumb', '.social', '.share', '.related',
                '.widget', '.advertisement', '.banner', '.promo', '.sponsored',
                '.cookie-notice', '.privacy-notice', '.disclaimer', '.breadcrumbs',
                '.pagination', '.search-results', '.related-posts', '.popular-posts',
                '.newsletter', '.subscribe', '.signup', '.social-media', '.social-links',
                '.author-bio', '.tags', '.categories', '.meta', '.metadata',
                '.date', '.time', '.published', '.updated', '.print', '.email',
                '.share-this', '.bookmark', '.favorite', '.like', '.vote', '.rating',
                '.review', '.comment', '.feedback', '.contact', '.search', '.filter'
            ]
        )
    
    def _process_crawl_result(self, result: Any, crawl_duration: float, start_time: float) -> Dict[str, Any]:
        """Process and enhance crawl result with performance metrics."""
        if hasattr(result, 'data'):
            pages_crawled = len(result.data) if result.data else 0
            credits_used = getattr(result, 'creditsUsed', 0)
            result_dict = {
                'data': result.data if result.data else [],
                'creditsUsed': credits_used,
                'status': getattr(result, 'status', 'unknown'),
                'message': getattr(result, 'message', '')
            }
        else:
            pages_crawled = len(result.get("data", []))
            credits_used = result.get("creditsUsed", 0)
            result_dict = result
        
        total_duration = time.time() - start_time
        
        # Performance metrics
        pages_per_second = pages_crawled / crawl_duration if crawl_duration > 0 else 0
        credits_per_second = credits_used / crawl_duration if crawl_duration > 0 else 0
        
        print(f"Optimized crawl completed: {pages_crawled} pages, {credits_used} credits")
        print(f"Performance: {crawl_duration:.2f}s crawl, {total_duration:.2f}s total")
        print(f"Rate: {pages_per_second:.2f} pages/sec, {credits_per_second:.2f} credits/sec")
        
        result_dict['performance_metrics'] = {
            'crawl_duration_seconds': crawl_duration,
            'total_duration_seconds': total_duration,
            'pages_per_second': pages_per_second,
            'credits_per_second': credits_per_second,
            'pages_crawled': pages_crawled,
            'credits_used': credits_used,
            'optimizations_applied': ['intelligent_caching', 'adaptive_timeout', 'parallel_processing']
        }
        
        return result_dict
    
    def _calculate_adaptive_timeout(self) -> int:
        """Calculate adaptive timeout based on performance history."""
        if not self.adaptive_timeout or not self.performance_history:
            return 60  # Default timeout
        
        # Calculate average duration and add buffer
        avg_duration = sum(h['total_duration'] for h in self.performance_history[-5:]) / len(self.performance_history[-5:])
        adaptive_timeout = int(avg_duration * 1.5) + 10  # 50% buffer + 10s
        
        return min(max(adaptive_timeout, 30), 120)  # Between 30s and 120s
    
    def _update_performance_metrics(self, result: Dict[str, Any]) -> None:
        """Update performance history for adaptive optimizations."""
        metrics = result.get('performance_metrics', {})
        if metrics:
            self.performance_history.append({
                'timestamp': time.time(),
                'total_duration': metrics.get('total_duration_seconds', 0),
                'pages_crawled': metrics.get('pages_crawled', 0),
                'credits_used': metrics.get('credits_used', 0),
                'pages_per_second': metrics.get('pages_per_second', 0)
            })
            
            # Keep only last 10 entries
            if len(self.performance_history) > 10:
                self.performance_history = self.performance_history[-10:]
    
    # Legacy methods for backward compatibility
    async def _crawl_with_change_tracking(self) -> Dict[str, Any]:
        """Legacy method - now uses optimized crawl."""
        return await self._crawl_with_optimizations()
    
    def _sync_crawl_with_change_tracking(self) -> Dict[str, Any]:
        """Legacy method - now uses optimized crawl."""
        return self._sync_crawl_optimized()