#!/usr/bin/env python3
"""
Setup script for Esker Lodge Timesheet Analysis Dashboard
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Setting up Esker Lodge Timesheet Analysis Dashboard")
    print("=" * 50)
    
    # Check if we're in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  Warning: You're not in a virtual environment.")
        print("It's recommended to create one first:")
        print("   python -m venv .venv")
        print("   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate")
        print()
        
        response = input("Continue anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return
    
    # Check if master dataset exists
    master_csv = "master_timesheets_20250524_132012.csv"
    if not os.path.exists(master_csv):
        print(f"📊 Master dataset not found. Creating it...")
        if not run_command("python combine_all_timesheets.py", "Combining timesheet data"):
            return
    else:
        print(f"✅ Master dataset found: {master_csv}")
    
    print()
    print("🎉 Setup completed successfully!")
    print()
    print("To start the dashboard:")
    print("   streamlit run timesheet_dashboard.py")
    print()
    print("Then open your browser to: http://localhost:8501")

if __name__ == "__main__":
    main() 