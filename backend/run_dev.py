#!/usr/bin/env python3
"""
Development runner for Dripple Video Processing Backend
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
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main development runner"""
    print("🚀 Starting Dripple Video Processing Backend Development Environment")
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Check if virtual environment exists
    if not Path("venv").exists():
        print("📦 Creating virtual environment...")
        if not run_command("python -m venv venv", "Virtual environment creation"):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Dependency installation"):
        sys.exit(1)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("📝 Creating .env file from template...")
        if Path("env.example").exists():
            import shutil
            shutil.copy("env.example", ".env")
            print("✅ .env file created. Please update the configuration as needed.")
        else:
            print("⚠️  No env.example file found. Please create a .env file manually.")
    
    print("\n🎉 Development environment setup complete!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your configuration")
    print("2. Start PostgreSQL and Redis services")
    print("3. Run database migrations: alembic upgrade head")
    print("4. Start the application: python start.py")
    print("\n🐳 Or use Docker Compose: docker-compose up --build")

if __name__ == "__main__":
    main()
