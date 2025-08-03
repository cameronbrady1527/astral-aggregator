#!/usr/bin/env python3
"""
Comprehensive verification script for the change detection system.
This script helps verify that the system is correctly detecting changes for judiciary and waverly sites.
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.crawler.change_detector import ChangeDetector
from app.utils.config import ConfigManager

class SystemVerifier:
    """Comprehensive system verification for change detection."""
    
    def __init__(self):
        self.detector = ChangeDetector()
        self.config = ConfigManager()
        self.verification_results = {}
    
    async def run_verification_cycle(self, site_id: str, cycle_name: str) -> Dict[str, Any]:
        """Run a single verification cycle for a site."""
        print(f"\n🔄 Running verification cycle '{cycle_name}' for {site_id}...")
        
        start_time = time.time()
        try:
            results = await self.detector.detect_changes_for_site(site_id)
            duration = time.time() - start_time
            
            cycle_result = {
                "cycle_name": cycle_name,
                "site_id": site_id,
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
                "success": True,
                "results": results,
                "output_file": results.get("output_file")
            }
            
            print(f"✅ Cycle completed in {duration:.2f}s")
            return cycle_result
            
        except Exception as e:
            duration = time.time() - start_time
            cycle_result = {
                "cycle_name": cycle_name,
                "site_id": site_id,
                "timestamp": datetime.now().isoformat(),
                "duration": duration,
                "success": False,
                "error": str(e)
            }
            
            print(f"❌ Cycle failed: {e}")
            return cycle_result
    
    def analyze_changes(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the detected changes for patterns and validity."""
        analysis = {
            "total_changes": 0,
            "change_types": {},
            "url_patterns": {},
            "suspicious_changes": [],
            "validation_notes": []
        }
        
        methods = results.get("methods", {})
        for method_name, method_data in methods.items():
            if "error" in method_data:
                analysis["validation_notes"].append(f"Method {method_name} failed: {method_data['error']}")
                continue
            
            changes = method_data.get("changes", [])
            summary = method_data.get("summary", {})
            
            analysis["total_changes"] += summary.get("total_changes", 0)
            
            # Analyze change types
            for change in changes:
                change_type = change.get("change_type", "unknown")
                analysis["change_types"][change_type] = analysis["change_types"].get(change_type, 0) + 1
                
                # Analyze URL patterns
                url = change.get("url", "")
                if url:
                    domain = url.split("/")[2] if len(url.split("/")) > 2 else "unknown"
                    analysis["url_patterns"][domain] = analysis["url_patterns"].get(domain, 0) + 1
                    
                    # Check for suspicious patterns
                    if self._is_suspicious_change(change):
                        analysis["suspicious_changes"].append(change)
        
        return analysis
    
    def _is_suspicious_change(self, change: Dict[str, Any]) -> bool:
        """Check if a change looks suspicious."""
        url = change.get("url", "").lower()
        change_type = change.get("change_type", "")
        
        # Check for common suspicious patterns
        suspicious_patterns = [
            "admin", "login", "wp-", "php", "cgi", "asp", "jsp",
            "test", "dev", "staging", "beta", "debug"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in url:
                return True
        
        # Check for very long URLs (potential spam)
        if len(url) > 200:
            return True
        
        return False
    
    def compare_cycles(self, cycle1: Dict[str, Any], cycle2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two verification cycles."""
        comparison = {
            "cycle1_name": cycle1["cycle_name"],
            "cycle2_name": cycle2["cycle_name"],
            "time_between_cycles": None,
            "change_differences": {},
            "consistency_score": 0.0
        }
        
        # Calculate time between cycles
        time1 = datetime.fromisoformat(cycle1["timestamp"])
        time2 = datetime.fromisoformat(cycle2["timestamp"])
        comparison["time_between_cycles"] = (time2 - time1).total_seconds()
        
        # Compare changes
        if cycle1["success"] and cycle2["success"]:
            analysis1 = self.analyze_changes(cycle1["results"])
            analysis2 = self.analyze_changes(cycle2["results"])
            
            comparison["change_differences"] = {
                "total_changes_diff": analysis2["total_changes"] - analysis1["total_changes"],
                "change_types_diff": {},
                "new_suspicious_changes": len(analysis2["suspicious_changes"]) - len(analysis1["suspicious_changes"])
            }
            
            # Calculate consistency score
            if analysis1["total_changes"] > 0 and analysis2["total_changes"] > 0:
                # Simple consistency: if both cycles detected changes, that's consistent
                comparison["consistency_score"] = 1.0
            elif analysis1["total_changes"] == 0 and analysis2["total_changes"] == 0:
                # Both cycles detected no changes - also consistent
                comparison["consistency_score"] = 1.0
            else:
                # Mixed results - less consistent
                comparison["consistency_score"] = 0.5
        
        return comparison
    
    async def verify_site(self, site_id: str, cycles: int = 3) -> Dict[str, Any]:
        """Run comprehensive verification for a site."""
        print(f"\n🔍 Starting comprehensive verification for {site_id}")
        print("=" * 60)
        
        verification_result = {
            "site_id": site_id,
            "verification_start": datetime.now().isoformat(),
            "cycles": [],
            "analysis": {},
            "recommendations": []
        }
        
        # Run multiple cycles
        for i in range(cycles):
            cycle_name = f"cycle_{i+1}"
            cycle_result = await self.run_verification_cycle(site_id, cycle_name)
            verification_result["cycles"].append(cycle_result)
            
            # Add delay between cycles
            if i < cycles - 1:
                print("⏳ Waiting 30 seconds before next cycle...")
                await asyncio.sleep(30)
        
        # Analyze results
        successful_cycles = [c for c in verification_result["cycles"] if c["success"]]
        
        if successful_cycles:
            # Analyze the last successful cycle
            last_cycle = successful_cycles[-1]
            verification_result["analysis"] = self.analyze_changes(last_cycle["results"])
            
            # Compare cycles if we have multiple successful ones
            if len(successful_cycles) >= 2:
                comparison = self.compare_cycles(successful_cycles[0], successful_cycles[-1])
                verification_result["cycle_comparison"] = comparison
            
            # Generate recommendations
            verification_result["recommendations"] = self._generate_recommendations(
                verification_result["analysis"], 
                verification_result.get("cycle_comparison", {})
            )
        
        verification_result["verification_end"] = datetime.now().isoformat()
        return verification_result
    
    def _generate_recommendations(self, analysis: Dict[str, Any], comparison: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        # Check for suspicious changes
        if analysis.get("suspicious_changes"):
            recommendations.append(
                f"⚠️  Found {len(analysis['suspicious_changes'])} suspicious changes. "
                "Review these manually to ensure they are legitimate."
            )
        
        # Check for high change volume
        total_changes = analysis.get("total_changes", 0)
        if total_changes > 50:
            recommendations.append(
                f"📈 High volume of changes detected ({total_changes}). "
                "Consider adjusting detection sensitivity or checking for false positives."
            )
        elif total_changes == 0:
            recommendations.append(
                "✅ No changes detected. This could be normal for stable sites, "
                "or the detection might need adjustment."
            )
        
        # Check consistency
        consistency_score = comparison.get("consistency_score", 0)
        if consistency_score < 0.8:
            recommendations.append(
                "🔄 Inconsistent results between cycles detected. "
                "Consider running more verification cycles or checking for transient issues."
            )
        
        return recommendations
    
    def print_verification_report(self, verification_result: Dict[str, Any]):
        """Print a comprehensive verification report."""
        print(f"\n📊 VERIFICATION REPORT FOR {verification_result['site_id'].upper()}")
        print("=" * 80)
        
        # Summary
        successful_cycles = [c for c in verification_result["cycles"] if c["success"]]
        print(f"✅ Successful cycles: {len(successful_cycles)}/{len(verification_result['cycles'])}")
        
        if successful_cycles:
            # Analysis
            analysis = verification_result["analysis"]
            print(f"\n📈 CHANGE ANALYSIS:")
            print(f"   Total changes: {analysis.get('total_changes', 0)}")
            print(f"   Change types: {analysis.get('change_types', {})}")
            print(f"   Suspicious changes: {len(analysis.get('suspicious_changes', []))}")
            
            # Cycle comparison
            if "cycle_comparison" in verification_result:
                comparison = verification_result["cycle_comparison"]
                print(f"\n🔄 CYCLE COMPARISON:")
                print(f"   Time between cycles: {comparison.get('time_between_cycles', 0):.1f}s")
                print(f"   Consistency score: {comparison.get('consistency_score', 0):.2f}")
                print(f"   Change difference: {comparison.get('change_differences', {}).get('total_changes_diff', 0)}")
            
            # Recommendations
            recommendations = verification_result.get("recommendations", [])
            if recommendations:
                print(f"\n💡 RECOMMENDATIONS:")
                for rec in recommendations:
                    print(f"   {rec}")
            else:
                print(f"\n✅ No specific recommendations - system appears to be working correctly")
        
        # Timing
        start_time = datetime.fromisoformat(verification_result["verification_start"])
        end_time = datetime.fromisoformat(verification_result["verification_end"])
        total_duration = (end_time - start_time).total_seconds()
        print(f"\n⏱️  Total verification time: {total_duration:.1f}s")

async def main():
    """Main verification function."""
    print("🔍 COMPREHENSIVE SYSTEM VERIFICATION")
    print("=" * 60)
    print("This script will verify the change detection system for judiciary and waverly sites.")
    print("It will run multiple detection cycles and analyze the results for accuracy.")
    
    verifier = SystemVerifier()
    
    # Verify both sites
    sites_to_verify = ["judiciary_uk", "waverley_gov"]
    
    for site_id in sites_to_verify:
        try:
            verification_result = await verifier.verify_site(site_id, cycles=2)
            verifier.print_verification_report(verification_result)
            
            # Save verification result
            output_file = f"verification_{site_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(verification_result, f, indent=2, default=str)
            print(f"\n💾 Verification result saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ Verification failed for {site_id}: {e}")
    
    print(f"\n🎉 Verification completed for all sites!")

if __name__ == "__main__":
    asyncio.run(main()) 