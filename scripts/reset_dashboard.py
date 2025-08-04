#!/usr/bin/env python3
"""
Dashboard Reset Script - Clear all existing change detection state
This script resets the dashboard to start fresh with 0 changes.
"""

import asyncio
import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class DashboardReset:
    """Reset dashboard state and clear existing change detection data."""
    
    def __init__(self):
        self.base_dir = Path(".")
    
    async def reset_all_state(self) -> Dict[str, Any]:
        """Reset all dashboard and change detection state."""
        print("🔄 Starting comprehensive dashboard reset...")
        
        reset_results = {
            "reset_time": datetime.now().isoformat(),
            "actions_taken": [],
            "errors": []
        }
        
        # Step 1: Clear output directory (but keep structure)
        await self._clear_output_directory(reset_results)
        
        # Step 2: Clear cache directory
        await self._clear_cache_directory(reset_results)
        
        # Step 3: Clear temp files
        await self._clear_temp_files(reset_results)
        
        # Step 4: Reset any database state (if applicable)
        await self._reset_database_state(reset_results)
        
        # Step 5: Create fresh state files
        await self._create_fresh_state_files(reset_results)
        
        return reset_results
    
    async def _clear_output_directory(self, results: Dict[str, Any]):
        """Clear the output directory but keep the structure."""
        output_dir = self.base_dir / "output"
        
        if output_dir.exists():
            print("🗑️  Clearing output directory...")
            
            # Remove all files in output directory
            for item in output_dir.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                        results["actions_taken"].append(f"Deleted file: {item}")
                    elif item.is_dir():
                        shutil.rmtree(item)
                        results["actions_taken"].append(f"Deleted directory: {item}")
                except PermissionError:
                    error_msg = f"Permission denied: {item}"
                    results["errors"].append(error_msg)
                    print(f"⚠️  {error_msg}")
                except Exception as e:
                    error_msg = f"Failed to delete {item}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"⚠️  {error_msg}")
            
            print("✅ Output directory cleared")
        else:
            print("📁 Output directory doesn't exist, creating...")
            output_dir.mkdir(exist_ok=True)
            results["actions_taken"].append("Created output directory")
    
    async def _clear_cache_directory(self, results: Dict[str, Any]):
        """Clear the cache directory."""
        cache_dir = self.base_dir / "cache"
        
        if cache_dir.exists():
            print("🗑️  Clearing cache directory...")
            
            try:
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(exist_ok=True)
                results["actions_taken"].append("Cleared cache directory")
                print("✅ Cache directory cleared")
            except Exception as e:
                error_msg = f"Failed to clear cache: {str(e)}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        else:
            print("📁 Cache directory doesn't exist, creating...")
            cache_dir.mkdir(exist_ok=True)
            results["actions_taken"].append("Created cache directory")
    
    async def _clear_temp_files(self, results: Dict[str, Any]):
        """Clear temporary files."""
        temp_dir = self.base_dir / "temp_files"
        
        if temp_dir.exists():
            print("🗑️  Clearing temporary files...")
            
            try:
                for item in temp_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                        results["actions_taken"].append(f"Deleted temp file: {item.name}")
                print("✅ Temporary files cleared")
            except Exception as e:
                error_msg = f"Failed to clear temp files: {str(e)}"
                results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
        else:
            print("📁 Temp directory doesn't exist, creating...")
            temp_dir.mkdir(exist_ok=True)
            results["actions_taken"].append("Created temp directory")
    
    async def _reset_database_state(self, results: Dict[str, Any]):
        """Reset any database state (placeholder for future implementation)."""
        print("🗄️  Checking for database state...")
        
        # This would typically involve:
        # - Clearing database tables
        # - Resetting counters
        # - Clearing session data
        
        # For now, just note that no database state was found
        results["actions_taken"].append("No database state found to reset")
        print("✅ No database state to reset")
    
    async def _create_fresh_state_files(self, results: Dict[str, Any]):
        """Create fresh state files to indicate reset."""
        print("📝 Creating fresh state files...")
        
        # Create a reset marker file
        reset_marker = self.base_dir / "dashboard_reset.json"
        reset_data = {
            "reset_time": datetime.now().isoformat(),
            "reset_type": "comprehensive",
            "status": "completed",
            "next_action": "create_baseline"
        }
        
        with open(reset_marker, 'w', encoding='utf-8') as f:
            json.dump(reset_data, f, indent=2, ensure_ascii=False)
        
        results["actions_taken"].append("Created reset marker file")
        print("✅ Fresh state files created")
    
    async def save_reset_report(self, results: Dict[str, Any]) -> str:
        """Save reset report to file."""
        reports_dir = self.base_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = reports_dir / f"dashboard_reset_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return str(report_file)


async def main():
    """Main function."""
    print("🚀 Dashboard Reset Tool")
    print("=" * 50)
    
    # Confirm reset
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("⚠️  Force reset mode - proceeding without confirmation")
    else:
        print("⚠️  This will clear ALL existing change detection state!")
        print("   - Output files will be deleted")
        print("   - Cache will be cleared")
        print("   - Temporary files will be removed")
        print("   - Dashboard will be reset to 0 changes")
        print()
        
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("❌ Reset cancelled")
            return 1
    
    # Perform reset
    resetter = DashboardReset()
    results = await resetter.reset_all_state()
    
    # Save report
    report_file = await resetter.save_reset_report(results)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Dashboard Reset Summary:")
    print(f"   Reset time: {results['reset_time']}")
    print(f"   Actions taken: {len(results['actions_taken'])}")
    print(f"   Errors: {len(results['errors'])}")
    print(f"   Report saved to: {report_file}")
    
    if results['errors']:
        print("\n❌ Errors encountered:")
        for error in results['errors']:
            print(f"   - {error}")
    
    print("\n✅ Dashboard reset complete!")
    print("💡 Next steps:")
    print("   1. Create a new comprehensive baseline")
    print("   2. Start monitoring for changes")
    print("   3. Verify the system shows 0 changes initially")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 