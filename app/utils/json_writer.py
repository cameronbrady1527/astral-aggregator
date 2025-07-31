# ==============================================================================
# json_writer.py — JSON Writer Utility for Change Detection Results
# ==============================================================================
# Purpose: Handle writing change detection results to timestamped JSON files
# Sections: Imports, ChangeDetectionWriter Class
# ==============================================================================

# ==============================================================================
# Imports
# ==============================================================================

# Standard Library -----
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# ==============================================================================
# Public exports
# ==============================================================================
__all__ = ['ChangeDetectionWriter']


class ChangeDetectionWriter:
    """Handles writing change detection results to JSON files in timestamped folders."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the writer with output directory and create timestamped run folder."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create a timestamp for this run
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_folder = self.output_dir / self.run_timestamp
        self.run_folder.mkdir(exist_ok=True)
    
    def write_changes(self, site_name: str, changes: Dict[str, Any]) -> str:
        """Write change detection results to a timestamped JSON file in the run folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{site_name}_{timestamp}.json"
        filepath = self.run_folder / filename
        
        output_data = {
            "metadata": {
                "site_name": site_name,
                "detection_time": datetime.now().isoformat(),
                "detection_method": changes.get("detection_method", "unknown"),
                "file_created": datetime.now().isoformat(),
                "run_timestamp": self.run_timestamp
            },
            "changes": changes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def write_site_state(self, site_name: str, state_data: Dict[str, Any]) -> str:
        """Write current site state to a JSON file in the run folder."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        method = state_data.get("detection_method", "unknown")
        filename = f"{site_name}_state_{method}_{timestamp}.json"
        filepath = self.run_folder / filename
        
        output_data = {
            "metadata": {
                "site_name": site_name,
                "state_captured": datetime.now().isoformat(),
                "detection_method": state_data.get("detection_method", "unknown"),
                "run_timestamp": self.run_timestamp
            },
            "state": state_data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return str(filepath)
    
    def get_latest_state_file(self, site_name: str, method: str = None) -> str | None:
        """Get the path to the most recent state file for a site across all run folders."""
        if method:
            pattern = f"{site_name}_state_{method}_*.json"
        else:
            pattern = f"{site_name}_state_*.json"
        state_files = []
        
        # Search in all run folders
        for run_folder in self.output_dir.iterdir():
            if run_folder.is_dir():
                state_files.extend(run_folder.glob(pattern))
        
        if not state_files:
            return None
        
        latest_file = max(state_files, key=lambda x: x.stat().st_mtime)
        return str(latest_file)
    
    def read_json_file(self, filepath: str) -> Dict[str, Any]:
        """Read and parse a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_change_files(self, site_name: str = None) -> List[str]:
        """List all change detection files across all run folders, optionally filtered by site."""
        files = []
        
        # Search in all run folders
        for run_folder in self.output_dir.iterdir():
            if run_folder.is_dir():
                if site_name:
                    pattern = f"{site_name}_*.json"
                else:
                    pattern = "*.json"
                
                files.extend(run_folder.glob(pattern))
        
        return [str(f) for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)]
    
    def get_run_folder(self) -> str:
        """Get the path to the current run folder."""
        return str(self.run_folder)
    
    def list_run_folders(self) -> List[str]:
        """List all run folders in chronological order."""
        run_folders = []
        for item in self.output_dir.iterdir():
            if item.is_dir():
                run_folders.append(str(item))
        
        return sorted(run_folders, reverse=True)  # Most recent first 