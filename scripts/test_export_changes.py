#!/usr/bin/env python3
"""
Test Export Changes - Create sample change data and test Excel export
This script creates sample change files and tests the Excel export functionality.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from export_changes_to_excel import ChangesExporter


def create_sample_changes_data(site_name: str) -> dict:
    """Create sample changes data for testing."""
    base_time = datetime.now() - timedelta(hours=2)
    
    changes = [
        {
            "url": f"https://www.{site_name.lower().replace(' ', '')}.uk/page1",
            "change_type": "new_page",
            "detected_at": (base_time + timedelta(minutes=5)).isoformat(),
            "details": "New URL found in sitemap",
            "previous_hash": "",
            "new_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            "file_type": ""
        },
        {
            "url": f"https://www.{site_name.lower().replace(' ', '')}.uk/page2",
            "change_type": "modified_content",
            "detected_at": (base_time + timedelta(minutes=15)).isoformat(),
            "details": "Content hash changed from abc123... to def456...",
            "previous_hash": "abc1234567890123456789012345678901234567890abcdef1234567890abcdef",
            "new_hash": "def4567890123456789012345678901234567890abcdef1234567890abcdef123456",
            "file_type": ""
        },
        {
            "url": f"https://www.{site_name.lower().replace(' ', '')}.uk/page3",
            "change_type": "deleted_page",
            "detected_at": (base_time + timedelta(minutes=25)).isoformat(),
            "details": "URL no longer in sitemap",
            "previous_hash": "ghi7890123456789012345678901234567890abcdef1234567890abcdef123456",
            "new_hash": "",
            "file_type": ""
        },
        {
            "url": f"https://www.{site_name.lower().replace(' ', '')}.uk/image.jpg",
            "change_type": "ignored_file",
            "detected_at": (base_time + timedelta(minutes=35)).isoformat(),
            "details": "Skipped: image/document file",
            "previous_hash": "",
            "new_hash": "",
            "file_type": "JPG"
        }
    ]
    
    return {
        "metadata": {
            "site_name": site_name,
            "detection_time": base_time.isoformat(),
            "total_changes": len(changes),
            "file_created": datetime.now().isoformat()
        },
        "changes": changes
    }


def create_sample_changes_files():
    """Create sample changes files for testing."""
    # Use project root path
    project_root = Path(__file__).parent.parent
    changes_dir = project_root / "changes"
    changes_dir.mkdir(exist_ok=True)
    
    sites = ["Judiciary UK", "Waverley Borough Council"]
    
    for site_name in sites:
        # Create sample data
        changes_data = create_sample_changes_data(site_name)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{site_name}_{timestamp}_changes.json"
        filepath = changes_dir / filename
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(changes_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created sample changes file: {filepath}")


def main():
    """Main function."""
    print("=" * 60)
    print("🧪 Test Export Changes to Excel")
    print("=" * 60)
    
    # Create sample data
    print("\n📝 Creating sample changes files...")
    create_sample_changes_files()
    
    # Test export
    print("\n📊 Testing Excel export...")
    exporter = ChangesExporter()
    output_file = exporter.export_all_changes()
    
    if output_file:
        print(f"\n🎉 Test completed successfully!")
        print(f"📁 Excel file created: {output_file}")
        print(f"📂 Sample data files created in: changes/")
    else:
        print("\n❌ Test failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 