# Baseline Evolution System Implementation

## Overview

This document describes the implementation of the **Baseline Evolution System** that automatically updates baselines when changes are detected, exactly as specified in the requirements.

## System Behavior

The system now behaves exactly as described:

1. **Automatic Baseline Updates**: When a detection is triggered and changes are found, the baseline is automatically updated to a new baseline
2. **New Baseline Content**: The new baseline contains:
   - New date and time when it was established
   - Content hashes from the previous baseline that didn't change
   - New hashes for URLs that have changed
   - URLs that were added
   - URLs that were already present (unchanged)
   - **No URLs that were detected as deleted**
   - **No duplication of URLs**
3. **Output Generation**: The system still generates output files in the output directory showing the changes detected (or no changes if none were found)

## Implementation Components

### 1. Baseline Manager (`app/utils/baseline_manager.py`)

**Purpose**: Centralized baseline management with automatic updating capabilities

**Key Features**:
- `get_latest_baseline()`: Retrieves the most recent baseline for a site
- `update_baseline_from_changes()`: Creates new baseline by merging previous baseline with current state and changes
- `save_baseline()`: Saves new baseline with timestamp
- `validate_baseline()`: Validates baseline data structure and integrity

### 2. Baseline Merger (`app/utils/baseline_merger.py`)

**Purpose**: Intelligent merging of previous baseline with current state and detected changes

**Core Logic**:
```python
def merge_baselines(self, previous_baseline, current_state, detected_changes):
    # 1. Keep unchanged URLs from previous baseline
    # 2. Add new URLs from current state
    # 3. Update modified URLs with new hashes
    # 4. Remove deleted URLs
    # 5. Update metadata with new timestamp
```

**Change Type Mapping**:
- **New URLs**: `"new"`, `"new_content"`, `"sitemap_new"`
- **Deleted URLs**: `"deleted"`, `"page_deleted"`, `"removed"`, `"sitemap_deleted"`
- **Modified URLs**: `"modified"`, `"content_changed"`, `"content_modified"`, `"changed"`

### 3. Updated ChangeDetector (`app/crawler/change_detector.py`)

**Key Changes**:
- Integrates with `BaselineManager` for automatic baseline evolution
- Creates initial baselines when none exist
- Updates baselines when changes are detected
- Preserves existing output functionality
- Adds baseline evolution metadata to results

**New Flow**:
```python
async def _run_detection_method(self, site_config, method):
    # Get current baseline
    current_baseline = self.baseline_manager.get_latest_baseline(site_config.name)
    
    # Get current state
    detector = self._create_detector(site_config, method)
    current_state = await detector.get_current_state()
    
    # If no baseline exists, create initial baseline
    if current_baseline is None:
        initial_baseline = self.baseline_manager.merger.create_initial_baseline(...)
        baseline_file = self.baseline_manager.save_baseline(...)
        return result_with_baseline_info
    
    # Detect changes against the current baseline
    change_result = await detector.detect_changes(current_baseline)
    
    # Update baseline if changes were detected
    if change_result.changes:
        new_baseline = self.baseline_manager.update_baseline_from_changes(...)
        baseline_file = self.baseline_manager.save_baseline(...)
        baseline_updated = True
    
    # Still write current state for historical tracking
    self.writer.write_site_state(site_config.name, current_state)
    
    return result_with_baseline_evolution_info
```

### 4. Updated Detectors

All detectors have been updated to work with baselines instead of just previous state files:

- **SitemapDetector**: Compares current sitemap URLs against baseline URLs
- **ContentDetector**: Compares current content hashes against baseline hashes
- **FirecrawlDetector**: Uses baseline for incremental crawling
- **HybridDetector**: Combines sitemap and content analysis against baseline

## Baseline Evolution Process

### Step 1: Initial Baseline Creation
When no baseline exists for a site:
1. System detects this is the first run
2. Creates initial baseline from current state
3. Saves baseline with `evolution_type: "initial_creation"`
4. Returns baseline creation information

### Step 2: Change Detection Against Baseline
On subsequent runs:
1. System loads the latest baseline
2. Compares current state against baseline
3. Detects changes (new, deleted, modified URLs)
4. Generates change report

### Step 3: Baseline Update (When Changes Detected)
When changes are found:
1. System creates new baseline by merging:
   - Previous baseline (unchanged URLs)
   - Current state (new/modified URLs)
   - Excludes deleted URLs
2. Updates metadata with new timestamp
3. Saves new baseline with `evolution_type: "automatic_update"`
4. Validates merge result

### Step 4: Output Generation
System continues to:
1. Write change detection results to output directory
2. Write current state files for historical tracking
3. Include baseline evolution information in results

## Baseline Structure

### Initial Baseline
```json
{
  "site_id": "site_name",
  "site_name": "Site Name",
  "baseline_date": "20250804",
  "created_at": "2025-08-04T16:00:00",
  "baseline_version": "2.0",
  "evolution_type": "initial_creation",
  "sitemap_state": { ... },
  "content_hashes": { ... },
  "total_urls": 100,
  "total_content_hashes": 100,
  "metadata": { ... }
}
```

### Evolved Baseline
```json
{
  "site_id": "site_name",
  "site_name": "Site Name",
  "baseline_date": "20250804",
  "updated_at": "2025-08-04T16:30:00",
  "previous_baseline_date": "20250804",
  "changes_applied": 5,
  "evolution_type": "automatic_update",
  "sitemap_state": { ... },
  "content_hashes": { ... },
  "total_urls": 102,
  "total_content_hashes": 102,
  "change_summary": {
    "new_urls": 2,
    "deleted_urls": 1,
    "modified_urls": 2,
    "unchanged_urls": 97
  }
}
```

## API Integration

### Updated Endpoints

**POST /api/listeners/trigger/{site_id}**
```json
{
  "status": "started",
  "message": "Change detection started for site_id",
  "baseline_evolution_enabled": true,
  "baseline_updated": false,
  "progress_url": "/api/listeners/progress"
}
```

**GET /api/listeners/sites/{site_id}/status**
```json
{
  "site_id": "site_id",
  "site_name": "Site Name",
  "latest_baseline": {
    "date": "20250804",
    "total_urls": 100,
    "total_content_hashes": 100
  },
  "recent_change_files": [...],
  "latest_state_file": "..."
}
```

## Testing

### Test Coverage

1. **Baseline Evolution Tests** (`scripts/test_baseline_evolution.py`):
   - Initial baseline creation
   - Baseline update with new URLs
   - Baseline update with deleted URLs
   - Baseline update with modified content
   - Baseline update with mixed changes
   - No baseline update when no changes
   - Baseline validation

2. **Integration Tests** (`scripts/test_change_detector_integration.py`):
   - ChangeDetector initial run
   - ChangeDetector with existing baseline
   - Site status with baseline information
   - List sites with baseline information

### Running Tests
```bash
# Run baseline evolution tests
python scripts/test_baseline_evolution.py

# Run integration tests
python scripts/test_change_detector_integration.py
```

## Validation and Safety

### Baseline Validation
- **Structure Validation**: Ensures all required fields are present
- **Data Consistency**: Validates URL counts match hash counts
- **Merge Validation**: Verifies deleted URLs are removed, new URLs are added, modified URLs have updated hashes

### Error Handling
- **Fallback Behavior**: If baseline update fails, system returns previous baseline
- **Validation Warnings**: System logs warnings for potential issues
- **Graceful Degradation**: System continues to function even if baseline operations fail

### Rollback Capability
- **Baseline History**: All baselines are timestamped and preserved
- **Previous Baseline Reference**: New baselines reference previous baseline date
- **Manual Rollback**: Can manually revert to previous baseline if needed

## Benefits

1. **Automatic Evolution**: Baselines automatically evolve with site changes
2. **Accurate Tracking**: Maintains accurate history of site state over time
3. **No Duplication**: Eliminates duplicate URLs in baselines
4. **Clean Deletions**: Removes deleted URLs from baselines
5. **Preserved Functionality**: All existing output and monitoring features preserved
6. **Validation**: Comprehensive validation ensures baseline integrity
7. **Backward Compatibility**: Existing functionality remains unchanged

## Conclusion

The Baseline Evolution System has been successfully implemented and tested. It now behaves exactly as described:

- ✅ **Automatic baseline updates** when changes are detected
- ✅ **New baseline with correct content** (unchanged + new + modified, no deleted)
- ✅ **No URL duplication** in baselines
- ✅ **Output generation** continues as before
- ✅ **Comprehensive testing** validates all functionality
- ✅ **Backward compatibility** maintained

The system is ready for production use and will automatically evolve baselines while maintaining all existing functionality. 