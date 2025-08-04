#!/usr/bin/env python3
"""
Baseline Evolution Test Runner
Comprehensive test suite for the baseline evolution system.
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

class BaselineEvolutionTestRunner:
    """Comprehensive test runner for baseline evolution system."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests for baseline evolution components."""
        print("🧪 Running Unit Tests...")
        print("=" * 50)
        
        unit_test_modules = [
            "tests.unit.test_baseline_manager",
            "tests.unit.test_baseline_merger",
            "tests.unit.test_change_detector",
            "tests.unit.test_sitemap_detector",
            "tests.unit.test_content_detector"
        ]
        
        results = {}
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for module in unit_test_modules:
            print(f"\n📋 Testing {module}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", module, 
                    "-v", "--tb=short"
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    print(f"✅ {module} - PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {module} - FAILED")
                    print(f"Error: {result.stderr}")
                    failed_tests += 1
                
                total_tests += 1
                results[module] = {
                    "status": "PASSED" if result.returncode == 0 else "FAILED",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
            except Exception as e:
                print(f"❌ {module} - ERROR: {e}")
                failed_tests += 1
                total_tests += 1
                results[module] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        return {
            "total_modules": total_tests,
            "passed_modules": passed_tests,
            "failed_modules": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": results
        }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests for baseline evolution workflow."""
        print("\n🔗 Running Integration Tests...")
        print("=" * 50)
        
        integration_test_modules = [
            "tests.integration.test_baseline_evolution_integration",
            "tests.integration.test_detector_integration"
        ]
        
        results = {}
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for module in integration_test_modules:
            print(f"\n📋 Testing {module}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", module, 
                    "-v", "--tb=short"
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    print(f"✅ {module} - PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {module} - FAILED")
                    print(f"Error: {result.stderr}")
                    failed_tests += 1
                
                total_tests += 1
                results[module] = {
                    "status": "PASSED" if result.returncode == 0 else "FAILED",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
            except Exception as e:
                print(f"❌ {module} - ERROR: {e}")
                failed_tests += 1
                total_tests += 1
                results[module] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        return {
            "total_modules": total_tests,
            "passed_modules": passed_tests,
            "failed_modules": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": results
        }
    
    def run_api_tests(self) -> Dict[str, Any]:
        """Run API tests for baseline evolution endpoints."""
        print("\n🌐 Running API Tests...")
        print("=" * 50)
        
        api_test_modules = [
            "tests.api.test_baseline_evolution_api",
            "tests.api.test_listeners"
        ]
        
        results = {}
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for module in api_test_modules:
            print(f"\n📋 Testing {module}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pytest", module, 
                    "-v", "--tb=short"
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    print(f"✅ {module} - PASSED")
                    passed_tests += 1
                else:
                    print(f"❌ {module} - FAILED")
                    print(f"Error: {result.stderr}")
                    failed_tests += 1
                
                total_tests += 1
                results[module] = {
                    "status": "PASSED" if result.returncode == 0 else "FAILED",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
            except Exception as e:
                print(f"❌ {module} - ERROR: {e}")
                failed_tests += 1
                total_tests += 1
                results[module] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        return {
            "total_modules": total_tests,
            "passed_modules": passed_tests,
            "failed_modules": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": results
        }
    
    def run_end_to_end_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests with real data simulation."""
        print("\n🔄 Running End-to-End Tests...")
        print("=" * 50)
        
        # Create test data and run end-to-end scenarios
        test_scenarios = [
            "first_detection_creates_baseline",
            "baseline_evolution_with_new_urls",
            "baseline_evolution_with_deleted_urls",
            "baseline_evolution_with_modified_content",
            "multiple_consecutive_evolutions",
            "error_handling_scenarios"
        ]
        
        results = {}
        total_scenarios = len(test_scenarios)
        passed_scenarios = 0
        failed_scenarios = 0
        
        for scenario in test_scenarios:
            print(f"\n📋 Testing scenario: {scenario}...")
            try:
                # Run specific end-to-end test
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    "tests.integration.test_baseline_evolution_integration::TestBaselineEvolutionWorkflow::test_" + scenario,
                    "-v", "--tb=short"
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    print(f"✅ {scenario} - PASSED")
                    passed_scenarios += 1
                else:
                    print(f"❌ {scenario} - FAILED")
                    print(f"Error: {result.stderr}")
                    failed_scenarios += 1
                
                results[scenario] = {
                    "status": "PASSED" if result.returncode == 0 else "FAILED",
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
            except Exception as e:
                print(f"❌ {scenario} - ERROR: {e}")
                failed_scenarios += 1
                results[scenario] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        return {
            "total_scenarios": total_scenarios,
            "passed_scenarios": passed_scenarios,
            "failed_scenarios": failed_scenarios,
            "success_rate": (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
            "results": results
        }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests for baseline evolution."""
        print("\n⚡ Running Performance Tests...")
        print("=" * 50)
        
        performance_tests = [
            "baseline_evolution_performance",
            "large_dataset_handling",
            "concurrent_operations"
        ]
        
        results = {}
        total_tests = len(performance_tests)
        passed_tests = 0
        failed_tests = 0
        
        for test in performance_tests:
            print(f"\n📋 Testing performance: {test}...")
            try:
                start_time = time.time()
                
                result = subprocess.run([
                    sys.executable, "-m", "pytest", 
                    f"tests.integration.test_baseline_evolution_integration::TestBaselineEvolutionWorkflow::test_{test}",
                    "-v", "--tb=short"
                ], capture_output=True, text=True, cwd=self.project_root)
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                if result.returncode == 0:
                    print(f"✅ {test} - PASSED (took {execution_time:.2f}s)")
                    passed_tests += 1
                else:
                    print(f"❌ {test} - FAILED (took {execution_time:.2f}s)")
                    print(f"Error: {result.stderr}")
                    failed_tests += 1
                
                results[test] = {
                    "status": "PASSED" if result.returncode == 0 else "FAILED",
                    "execution_time": execution_time,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
                
            except Exception as e:
                print(f"❌ {test} - ERROR: {e}")
                failed_tests += 1
                results[test] = {
                    "status": "ERROR",
                    "error": str(e)
                }
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "results": results
        }
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        report = {
            "test_run": {
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None
            },
            "summary": {
                "total_test_modules": 0,
                "total_passed_modules": 0,
                "total_failed_modules": 0,
                "overall_success_rate": 0
            },
            "results": self.test_results
        }
        
        # Calculate overall summary
        total_modules = 0
        total_passed = 0
        total_failed = 0
        
        for test_type, result in self.test_results.items():
            if "total_modules" in result:
                total_modules += result["total_modules"]
                total_passed += result["passed_modules"]
                total_failed += result["failed_modules"]
            elif "total_scenarios" in result:
                total_modules += result["total_scenarios"]
                total_passed += result["passed_scenarios"]
                total_failed += result["failed_scenarios"]
            elif "total_tests" in result:
                total_modules += result["total_tests"]
                total_passed += result["passed_tests"]
                total_failed += result["failed_tests"]
        
        report["summary"]["total_test_modules"] = total_modules
        report["summary"]["total_passed_modules"] = total_passed
        report["summary"]["total_failed_modules"] = total_failed
        report["summary"]["overall_success_rate"] = (total_passed / total_modules * 100) if total_modules > 0 else 0
        
        return report
    
    def save_test_report(self, report: Dict[str, Any], output_file: str = None):
        """Save test report to file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_reports/baseline_evolution_test_report_{timestamp}.json"
        
        # Create reports directory if it doesn't exist
        reports_dir = Path(output_file).parent
        reports_dir.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Test report saved to: {output_file}")
        return output_file
    
    def print_test_summary(self, report: Dict[str, Any]):
        """Print test summary to console."""
        print("\n" + "=" * 60)
        print("📊 BASELINE EVOLUTION TEST SUMMARY")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"Total Test Modules: {summary['total_test_modules']}")
        print(f"Passed: {summary['total_passed_modules']}")
        print(f"Failed: {summary['total_failed_modules']}")
        print(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        
        if report["test_run"]["duration_seconds"]:
            print(f"Total Duration: {report['test_run']['duration_seconds']:.2f} seconds")
        
        print("\n📋 Detailed Results:")
        for test_type, result in report["results"].items():
            print(f"\n{test_type.upper()}:")
            if "success_rate" in result:
                print(f"  Success Rate: {result['success_rate']:.1f}%")
            if "passed_modules" in result:
                print(f"  Passed: {result['passed_modules']}/{result['total_modules']}")
            elif "passed_scenarios" in result:
                print(f"  Passed: {result['passed_scenarios']}/{result['total_scenarios']}")
            elif "passed_tests" in result:
                print(f"  Passed: {result['passed_tests']}/{result['total_tests']}")
        
        # Print recommendations
        print("\n💡 Recommendations:")
        if summary['overall_success_rate'] >= 90:
            print("✅ Excellent! The baseline evolution system is working well.")
        elif summary['overall_success_rate'] >= 80:
            print("⚠️  Good, but there are some issues to address.")
        elif summary['overall_success_rate'] >= 60:
            print("⚠️  Fair, but significant improvements are needed.")
        else:
            print("❌ Poor performance. Major issues need to be resolved.")
    
    def run_all_tests(self, test_types: List[str] = None) -> Dict[str, Any]:
        """Run all tests or specified test types."""
        if test_types is None:
            test_types = ["unit", "integration", "api", "e2e", "performance"]
        
        self.start_time = datetime.now()
        
        print("🚀 Starting Baseline Evolution Test Suite")
        print("=" * 60)
        print(f"Test Types: {', '.join(test_types)}")
        print(f"Start Time: {self.start_time}")
        print("=" * 60)
        
        # Run specified test types
        if "unit" in test_types:
            self.test_results["unit_tests"] = self.run_unit_tests()
        
        if "integration" in test_types:
            self.test_results["integration_tests"] = self.run_integration_tests()
        
        if "api" in test_types:
            self.test_results["api_tests"] = self.run_api_tests()
        
        if "e2e" in test_types:
            self.test_results["end_to_end_tests"] = self.run_end_to_end_tests()
        
        if "performance" in test_types:
            self.test_results["performance_tests"] = self.run_performance_tests()
        
        self.end_time = datetime.now()
        
        # Generate and save report
        report = self.generate_test_report()
        report_file = self.save_test_report(report)
        self.print_test_summary(report)
        
        return report

def main():
    """Main function for test runner."""
    parser = argparse.ArgumentParser(description="Baseline Evolution Test Runner")
    parser.add_argument("--test-types", nargs="+", 
                       choices=["unit", "integration", "api", "e2e", "performance"],
                       default=["unit", "integration", "api", "e2e", "performance"],
                       help="Types of tests to run")
    parser.add_argument("--output", type=str, help="Output file for test report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = BaselineEvolutionTestRunner()
    
    try:
        # Run tests
        report = runner.run_all_tests(args.test_types)
        
        # Save report if specified
        if args.output:
            runner.save_test_report(report, args.output)
        
        # Exit with appropriate code
        if report["summary"]["overall_success_rate"] >= 80:
            print("\n✅ Test suite completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Test suite completed with failures!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 