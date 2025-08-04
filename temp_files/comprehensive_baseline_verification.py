#!/usr/bin/env python3
"""
Comprehensive Baseline Verification
This script verifies baseline quality and saves results to a file.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def verify_baseline_quality():
    """Verify baseline quality and save results."""
    print("🔍 COMPREHENSIVE BASELINE VERIFICATION")
    print("=" * 60)
    
    results = {
        "verification_timestamp": datetime.now().isoformat(),
        "overall_status": "PASSED",
        "baselines": {},
        "issues": [],
        "recommendations": []
    }
    
    baseline_dir = Path("baselines")
    if not baseline_dir.exists():
        results["overall_status"] = "FAILED"
        results["issues"].append("Baselines directory not found")
        return results
    
    baseline_files = list(baseline_dir.glob("*_baseline.json"))
    print(f"📁 Found {len(baseline_files)} baseline files")
    
    for baseline_file in baseline_files:
        print(f"\n📄 Analyzing: {baseline_file.name}")
        site_id = baseline_file.name.split("_")[0]
        
        baseline_result = {
            "file_name": baseline_file.name,
            "file_size_mb": 0,
            "status": "UNKNOWN",
            "issues": [],
            "data_quality": {}
        }
        
        try:
            # Check file size
            file_size = baseline_file.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            baseline_result["file_size_mb"] = round(file_size_mb, 2)
            
            print(f"   Size: {file_size_mb:.2f} MB")
            
            # Load and validate JSON
            with open(baseline_file, 'r', encoding='utf-8') as f:
                baseline = json.load(f)
            
            # Check required fields
            required_fields = ['site_id', 'site_name', 'baseline_date', 'content_state', 'sitemap_state', 'summary']
            missing_fields = [field for field in required_fields if field not in baseline]
            
            if missing_fields:
                baseline_result["status"] = "FAILED"
                baseline_result["issues"].append(f"Missing required fields: {missing_fields}")
                results["issues"].append(f"{site_id}: Missing fields {missing_fields}")
            else:
                baseline_result["status"] = "PASSED"
                print(f"   ✅ Valid structure")
                
                # Check data quality
                content_state = baseline['content_state']
                sitemap_state = baseline['sitemap_state']
                summary = baseline['summary']
                
                # Content state quality
                if 'content_hashes' in content_state and isinstance(content_state['content_hashes'], dict):
                    content_hashes_count = len(content_state['content_hashes'])
                    baseline_result["data_quality"]["content_hashes_count"] = content_hashes_count
                    print(f"   Content hashes: {content_hashes_count}")
                    
                    if content_hashes_count == 0:
                        baseline_result["issues"].append("No content hashes found")
                        results["issues"].append(f"{site_id}: No content hashes")
                else:
                    baseline_result["issues"].append("Invalid content_hashes structure")
                    results["issues"].append(f"{site_id}: Invalid content_hashes structure")
                
                # Sitemap state quality
                if 'urls' in sitemap_state and isinstance(sitemap_state['urls'], list):
                    sitemap_urls_count = len(sitemap_state['urls'])
                    baseline_result["data_quality"]["sitemap_urls_count"] = sitemap_urls_count
                    print(f"   Sitemap URLs: {sitemap_urls_count}")
                    
                    if sitemap_urls_count == 0:
                        baseline_result["issues"].append("No sitemap URLs found")
                        results["issues"].append(f"{site_id}: No sitemap URLs")
                else:
                    baseline_result["issues"].append("Invalid sitemap URLs structure")
                    results["issues"].append(f"{site_id}: Invalid sitemap URLs structure")
                
                # Summary quality
                baseline_result["data_quality"]["summary"] = summary
                print(f"   Summary: {summary}")
                
                # Check for reasonable data
                total_pages = summary.get('total_pages', 0)
                if total_pages == 0:
                    baseline_result["issues"].append("Total pages is 0")
                    results["issues"].append(f"{site_id}: Total pages is 0")
                elif total_pages > 50000:  # Suspiciously large
                    baseline_result["issues"].append(f"Very large page count: {total_pages}")
                    results["issues"].append(f"{site_id}: Very large page count {total_pages}")
                
                # Check file size vs content
                if file_size_mb > 10 and content_hashes_count < 1000:
                    baseline_result["issues"].append("Large file size but few content hashes")
                    results["issues"].append(f"{site_id}: Large file size but few content hashes")
            
        except json.JSONDecodeError as e:
            baseline_result["status"] = "FAILED"
            baseline_result["issues"].append(f"JSON decode error: {e}")
            results["issues"].append(f"{site_id}: JSON decode error - {e}")
        except Exception as e:
            baseline_result["status"] = "FAILED"
            baseline_result["issues"].append(f"Error: {e}")
            results["issues"].append(f"{site_id}: Error - {e}")
        
        results["baselines"][site_id] = baseline_result
        
        # Update overall status
        if baseline_result["status"] == "FAILED":
            results["overall_status"] = "FAILED"
    
    # Generate recommendations
    if results["overall_status"] == "PASSED":
        results["recommendations"].append("All baselines are valid and ready for daily comparison")
        results["recommendations"].append("Run daily baseline system to establish comparison baselines")
    else:
        results["recommendations"].append("Fix identified issues before proceeding")
        results["recommendations"].append("Re-run baseline establishment after fixes")
    
    # Save results
    results_file = f"baseline_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {results_file}")
    print(f"📊 Overall status: {results['overall_status']}")
    
    if results["issues"]:
        print(f"\n⚠️ Issues found:")
        for issue in results["issues"]:
            print(f"   - {issue}")
    
    if results["recommendations"]:
        print(f"\n💡 Recommendations:")
        for rec in results["recommendations"]:
            print(f"   - {rec}")
    
    return results

if __name__ == "__main__":
    verify_baseline_quality() 