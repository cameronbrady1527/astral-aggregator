#!/usr/bin/env python3
"""
Clean up root directory and organize files.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def cleanup_root():
    """Clean up root directory and organize files."""
    print("🧹 CLEANING UP ROOT DIRECTORY")
    print("=" * 50)
    
    # Create directories if they don't exist
    directories = {
        "baselines": "baselines",
        "deliverables": "deliverables", 
        "verification_files": "verification_files",
        "comparison_results": "comparison_results",
        "temp_files": "temp_files"
    }
    
    for dir_name, dir_path in directories.items():
        Path(dir_path).mkdir(exist_ok=True)
        print(f"📁 Created/verified directory: {dir_path}")
    
    # Files to move and their destinations
    file_moves = {
        # Baseline files
        "baseline_verification_*.json": "verification_files",
        "comprehensive_content_check_*.json": "deliverables",
        "force_content_check_*.json": "deliverables",
        "daily_comparison_*.json": "comparison_results",
        
        # Test and verification files
        "test_*.py": "temp_files",
        "check_*.py": "temp_files", 
        "verify_*.py": "temp_files",
        "comprehensive_*.py": "temp_files",
        "establish_*.py": "temp_files",
        "force_*.py": "temp_files",
        
        # Other files
        "deliverables_*.json": "deliverables",
        "verification_*.json": "verification_files"
    }
    
    moved_files = []
    skipped_files = []
    
    # Move files based on patterns
    for pattern, destination in file_moves.items():
        if "*" in pattern:
            # Handle wildcard patterns
            import glob
            matching_files = glob.glob(pattern)
            for file_path in matching_files:
                if os.path.isfile(file_path):
                    try:
                        dest_path = os.path.join(destination, os.path.basename(file_path))
                        shutil.move(file_path, dest_path)
                        moved_files.append(f"{file_path} → {dest_path}")
                        print(f"📦 Moved: {file_path} → {dest_path}")
                    except Exception as e:
                        print(f"❌ Error moving {file_path}: {e}")
                        skipped_files.append(file_path)
        else:
            # Handle specific files
            if os.path.isfile(pattern):
                try:
                    dest_path = os.path.join(destination, os.path.basename(pattern))
                    shutil.move(pattern, dest_path)
                    moved_files.append(f"{pattern} → {dest_path}")
                    print(f"📦 Moved: {pattern} → {dest_path}")
                except Exception as e:
                    print(f"❌ Error moving {pattern}: {e}")
                    skipped_files.append(pattern)
    
    # List remaining files in root
    print(f"\n📋 REMAINING FILES IN ROOT:")
    root_files = [f for f in os.listdir(".") if os.path.isfile(f)]
    for file in sorted(root_files):
        if file not in [".gitignore", "README.md", "requirements.txt", "pyproject.toml", "uv.lock", "railway.toml", "Dockerfile"]:
            print(f"   📄 {file}")
    
    print(f"\n✅ CLEANUP SUMMARY:")
    print(f"   📦 Files moved: {len(moved_files)}")
    print(f"   ⚠️ Files skipped: {len(skipped_files)}")
    
    if moved_files:
        print(f"\n📦 MOVED FILES:")
        for move in moved_files:
            print(f"   {move}")
    
    if skipped_files:
        print(f"\n⚠️ SKIPPED FILES:")
        for skip in skipped_files:
            print(f"   {skip}")

if __name__ == "__main__":
    cleanup_root() 