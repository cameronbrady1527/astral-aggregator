# ==============================================================================
# baseline_merger.py — Baseline Merger Logic
# ==============================================================================
# Purpose: Intelligent merging of previous baseline with current state and changes
# Sections: Imports, BaselineMerger Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
from datetime import datetime
from typing import Dict, Any, List, Set

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['BaselineMerger']


class BaselineMerger:
    """Handles intelligent merging of baselines with current state and changes."""
    
    def __init__(self):
        """Initialize the baseline merger."""
        # Define change type mappings for consistent categorization
        self.change_type_mappings = {
            # New URLs
            "new": "new_urls",
            "new_content": "new_urls", 
            "sitemap_new": "new_urls",
            
            # Deleted URLs
            "deleted": "deleted_urls",
            "page_deleted": "deleted_urls",
            "removed": "deleted_urls",
            "sitemap_deleted": "deleted_urls",
            "removed_from_sitemap": "deleted_urls",
            
            # Modified URLs
            "modified": "modified_urls",
            "content_changed": "modified_urls",
            "content_modified": "modified_urls",
            "changed": "modified_urls"
        }
    
    def merge_baselines(self, previous_baseline: Dict[str, Any], 
                       current_state: Dict[str, Any], 
                       detected_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge previous baseline with current state and detected changes.
        
        This implements the exact logic you described:
        1. Keep unchanged URLs from previous baseline
        2. Add new URLs from current state
        3. Update modified URLs with new hashes
        4. Remove deleted URLs
        5. Update metadata with new timestamp
        """
        try:
            # Extract change information
            change_info = self._analyze_changes(detected_changes)
            
            # Validate change consistency
            validation_result = self._validate_change_consistency(change_info)
            if not validation_result["is_valid"]:
                print(f"Warning: Change consistency issues detected: {validation_result['warnings']}")
            
            # Start with previous baseline
            new_baseline = previous_baseline.copy()
            
            # Update content hashes based on changes
            new_baseline["content_hashes"] = self._merge_content_hashes(
                previous_baseline.get("content_hashes", {}),
                current_state.get("content_hashes", {}),
                change_info
            )
            
            # Update sitemap state with current state
            if "sitemap_state" in current_state:
                new_baseline["sitemap_state"] = current_state["sitemap_state"]
            
            # Update counts
            new_baseline["total_content_hashes"] = len(new_baseline["content_hashes"])
            if "sitemap_state" in new_baseline:
                new_baseline["total_urls"] = len(new_baseline["sitemap_state"].get("urls", []))
            
            # Add change summary
            new_baseline["change_summary"] = {
                "new_urls": len(change_info["new_urls"]),
                "deleted_urls": len(change_info["deleted_urls"]),
                "modified_urls": len(change_info["modified_urls"]),
                "unchanged_urls": len(change_info["unchanged_urls"]),
                "change_validation": validation_result
            }
            
            # --- CRITICAL: Set the new baseline date and updated_at timestamp LAST ---
            current_time = datetime.now()
            new_baseline["baseline_date"] = current_time.strftime("%Y%m%d")
            new_baseline["updated_at"] = current_time.isoformat()
            new_baseline["previous_baseline_date"] = previous_baseline.get("baseline_date")
            new_baseline["changes_applied"] = len(detected_changes)
            new_baseline["evolution_type"] = "automatic_update"
            
            return new_baseline
            
        except Exception as e:
            print(f"Error merging baselines: {e}")
            # Return the previous baseline as fallback
            return previous_baseline
    
    def _analyze_changes(self, detected_changes: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """Analyze detected changes to categorize URLs using comprehensive change type mapping."""
        change_info = {
            "new_urls": set(),
            "deleted_urls": set(),
            "modified_urls": set(),
            "unchanged_urls": set()
        }
        
        # Track URLs that appear in multiple categories (for validation)
        url_categories = {}
        
        for change in detected_changes:
            url = change.get("url", "")
            change_type = change.get("change_type", "")
            
            if not url or not change_type:
                continue
            
            # Map change type to category
            category = self.change_type_mappings.get(change_type)
            if category:
                change_info[category].add(url)
                
                # Track which categories this URL appears in
                if url not in url_categories:
                    url_categories[url] = set()
                url_categories[url].add(category)
            else:
                print(f"Warning: Unknown change type '{change_type}' for URL '{url}'")
        
        return change_info
    
    def _validate_change_consistency(self, change_info: Dict[str, Set[str]]) -> Dict[str, Any]:
        """Validate that changes are consistent and don't have conflicting categorizations."""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check for URLs that appear in multiple categories
        new_urls = change_info["new_urls"]
        deleted_urls = change_info["deleted_urls"]
        modified_urls = change_info["modified_urls"]
        
        # URLs that are both new and deleted (conflict)
        new_and_deleted = new_urls & deleted_urls
        if new_and_deleted:
            validation_result["warnings"].append(
                f"URLs marked as both new and deleted: {len(new_and_deleted)} URLs"
            )
            # Remove from deleted (keep as new)
            change_info["deleted_urls"] -= new_and_deleted
        
        # URLs that are both new and modified (conflict)
        new_and_modified = new_urls & modified_urls
        if new_and_modified:
            validation_result["warnings"].append(
                f"URLs marked as both new and modified: {len(new_and_modified)} URLs"
            )
            # Remove from modified (keep as new)
            change_info["modified_urls"] -= new_and_modified
        
        # URLs that are both deleted and modified (conflict)
        deleted_and_modified = deleted_urls & modified_urls
        if deleted_and_modified:
            validation_result["warnings"].append(
                f"URLs marked as both deleted and modified: {len(deleted_and_modified)} URLs"
            )
            # Remove from modified (keep as deleted)
            change_info["modified_urls"] -= deleted_and_modified
        
        return validation_result
    
    def _merge_content_hashes(self, previous_hashes: Dict[str, Any], 
                            current_hashes: Dict[str, Any], 
                            change_info: Dict[str, Set[str]]) -> Dict[str, Any]:
        """
        Merge content hashes based on change analysis.
        
        Logic:
        1. Keep unchanged URLs from previous baseline
        2. Add new URLs from current state
        3. Update modified URLs with new hashes
        4. Remove deleted URLs
        """
        merged_hashes = {}
        
        # Get all URLs from previous baseline
        previous_urls = set(previous_hashes.keys())
        
        # Get all URLs from current state
        current_urls = set(current_hashes.keys())
        
        # Calculate unchanged URLs (in previous but not in any change category)
        all_changed_urls = (change_info["new_urls"] | 
                           change_info["deleted_urls"] | 
                           change_info["modified_urls"])
        unchanged_urls = previous_urls - all_changed_urls
        
        # 1. Keep unchanged URLs from previous baseline
        for url in unchanged_urls:
            if url in previous_hashes:
                merged_hashes[url] = previous_hashes[url]
        
        # 2. Add new URLs from current state
        for url in change_info["new_urls"]:
            if url in current_hashes:
                merged_hashes[url] = current_hashes[url]
            else:
                print(f"Warning: New URL '{url}' not found in current state")
        
        # 3. Update modified URLs with new hashes
        for url in change_info["modified_urls"]:
            if url in current_hashes:
                merged_hashes[url] = current_hashes[url]
            else:
                print(f"Warning: Modified URL '{url}' not found in current state")
        
        # 4. Remove deleted URLs (they are not added to merged_hashes)
        # This is handled implicitly by not including them
        
        # Log summary
        print(f"Baseline merge summary:")
        print(f"  - Unchanged URLs: {len(unchanged_urls)}")
        print(f"  - New URLs: {len(change_info['new_urls'])}")
        print(f"  - Modified URLs: {len(change_info['modified_urls'])}")
        print(f"  - Deleted URLs: {len(change_info['deleted_urls'])}")
        print(f"  - Total URLs in new baseline: {len(merged_hashes)}")
        
        return merged_hashes
    
    def validate_merge_result(self, previous_baseline: Dict[str, Any], 
                            new_baseline: Dict[str, Any], 
                            detected_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that the merge result is correct."""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check that deleted URLs are actually removed
            previous_urls = set(previous_baseline.get("content_hashes", {}).keys())
            new_urls = set(new_baseline.get("content_hashes", {}).keys())
            
            deleted_urls = {change["url"] for change in detected_changes 
                          if change.get("change_type") in self.change_type_mappings 
                          and self.change_type_mappings[change.get("change_type")] == "deleted_urls"}
            
            for url in deleted_urls:
                if url in new_urls:
                    validation_result["errors"].append(f"Deleted URL still present: {url}")
                    validation_result["is_valid"] = False
            
            # Check that new URLs are added
            new_detected_urls = {change["url"] for change in detected_changes 
                               if change.get("change_type") in self.change_type_mappings 
                               and self.change_type_mappings[change.get("change_type")] == "new_urls"}
            
            for url in new_detected_urls:
                if url not in new_urls:
                    validation_result["errors"].append(f"New URL not added: {url}")
                    validation_result["is_valid"] = False
            
            # Check that modified URLs have updated hashes
            modified_urls = {change["url"] for change in detected_changes 
                           if change.get("change_type") in self.change_type_mappings 
                           and self.change_type_mappings[change.get("change_type")] == "modified_urls"}
            
            previous_hashes = previous_baseline.get("content_hashes", {})
            new_hashes = new_baseline.get("content_hashes", {})
            
            for url in modified_urls:
                if url in previous_hashes and url in new_hashes:
                    if previous_hashes[url].get("hash") == new_hashes[url].get("hash"):
                        validation_result["warnings"].append(f"Modified URL has same hash: {url}")
            
            # Check that unchanged URLs have same hashes
            unchanged_urls = previous_urls - deleted_urls - new_detected_urls - modified_urls
            
            for url in unchanged_urls:
                if url in previous_hashes and url in new_hashes:
                    if previous_hashes[url].get("hash") != new_hashes[url].get("hash"):
                        validation_result["errors"].append(f"Unchanged URL has different hash: {url}")
                        validation_result["is_valid"] = False
            
            return validation_result
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Validation error: {e}")
            return validation_result
    
    def create_initial_baseline(self, site_id: str, site_name: str, 
                              current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Create an initial baseline from current state."""
        baseline_data = {
            "site_id": site_id,
            "site_name": site_name,
            "baseline_date": datetime.now().strftime("%Y%m%d"),
            "created_at": datetime.now().isoformat(),
            "baseline_version": "2.0",
            "evolution_type": "initial_creation",
            "sitemap_state": current_state.get("sitemap_state", {}),
            "content_hashes": current_state.get("content_hashes", {}),
            "total_urls": len(current_state.get("sitemap_state", {}).get("urls", [])),
            "total_content_hashes": len(current_state.get("content_hashes", {})),
            "metadata": {
                "creation_method": "baseline_merger",
                "content_hash_algorithm": "sha256",
                "baseline_type": "initial"
            }
        }
        
        return baseline_data 