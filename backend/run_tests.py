#!/usr/bin/env python3
"""
Test runner for Dripple Video Processing Backend
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main test runner"""
    print("🧪 Running Dripple Video Processing Backend Tests")
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        print("❌ Virtual environment not found. Please run run_dev.py first")
        sys.exit(1)
    
    # Determine pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Install test dependencies
    if not run_command(f"{pip_cmd} install pytest pytest-asyncio pytest-cov", "Test dependency installation"):
        sys.exit(1)
    
    # Run tests
    test_commands = [
        (f"{python_cmd} -m pytest tests/ -v", "Running all tests"),
        (f"{python_cmd} -m pytest tests/ --cov=app --cov-report=term", "Running tests with coverage"),
    ]
    
    for command, description in test_commands:
        if not run_command(command, description):
            print(f"⚠️  {description} had issues, but continuing...")
    
    print("\n🎉 Test run completed!")

if __name__ == "__main__":
    main()
