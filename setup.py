#!/usr/bin/env python3
"""
Setup script for NIFTY 50 Predictor
Creates virtual environment and installs dependencies (cross-platform)
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, shell=False):
    """Run a shell command and return success/failure"""
    try:
        subprocess.run(cmd, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False

def main():
    print("=" * 50)
    print("  NIFTY 50 Predictor - Setup Script")
    print("=" * 50)
    print()

    # Detect OS
    os_type = platform.system()
    print(f"Detected OS: {os_type}")
    print()

    # Step 1: Create virtual environment
    print("Step 1: Creating virtual environment...")
    if os.path.exists("venv"):
        print("  Virtual environment already exists. Skipping...")
    else:
        if not run_command(f"{sys.executable} -m venv venv"):
            print("Failed to create virtual environment!")
            return False
        print("  ✓ Virtual environment created")
    print()

    # Step 2: Activate and install dependencies
    print("Step 2: Installing dependencies...")

    # Determine pip path based on OS
    if os_type == "Windows":
        pip_path = os.path.join("venv", "Scripts", "pip.exe")
        activate_cmd = os.path.join("venv", "Scripts", "activate.bat")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
        activate_cmd = os.path.join("venv", "bin", "activate")

    # Install requirements
    if not run_command(f"{pip_path} install -r requirements.txt"):
        print("Failed to install dependencies!")
        return False
    print("  ✓ Dependencies installed")
    print()

    # Step 3: Instructions
    print("=" * 50)
    print("  Setup Complete!")
    print("=" * 50)
    print()
    print("To start the NIFTY 50 predictor app:")
    print()

    if os_type == "Windows":
        print("  1. Activate virtual environment:")
        print(f"     {activate_cmd}")
        print()
        print("  2. Run the app:")
        print("     python app.py")
    else:
        print("  1. Activate virtual environment:")
        print(f"     source {activate_cmd}")
        print()
        print("  2. Run the app:")
        print("     python3 app.py")

    print()
    print("  3. Open browser and go to:")
    print("     http://localhost:5000")
    print()
    print("=" * 50)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
