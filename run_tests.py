#!/usr/bin/env python3
# ==============================================================================
# run_tests.py — Test Runner Script
# ==============================================================================
# Purpose: Run tests with different configurations and options
# ==============================================================================

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for the aggregator project")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "api", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Run with verbose output"
    )
    parser.add_argument(
        "--fast", 
        action="store_true",
        help="Skip slow tests"
    )
    parser.add_argument(
        "--markers", 
        action="store_true",
        help="Show available test markers"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    cmd = ["uv", "run", "pytest"]
    
    # Add coverage if requested
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing", "--cov-report=html"])
    
    # Add verbose output if requested
    if args.verbose:
        cmd.append("-v")
    
    # Add test type filters
    if args.type == "unit":
        cmd.append("tests/unit/")
    elif args.type == "integration":
        cmd.append("tests/integration/")
    elif args.type == "api":
        cmd.append("tests/api/")
    else:  # all
        cmd.append("tests/")
    
    # Skip slow tests if requested
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    # Show markers if requested
    if args.markers:
        subprocess.run(["uv", "run", "pytest", "--markers"])
        return
    
    # Run the tests
    success = run_command(cmd, f"{args.type.title()} tests")
    
    if success:
        print(f"\n🎉 All {args.type} tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 Some {args.type} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 