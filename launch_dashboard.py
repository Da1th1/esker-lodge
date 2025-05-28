#!/usr/bin/env python3
"""
Launch script for the Esker Lodge Timesheet vs Payroll Comparison Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit dashboard."""
    
    # Check if we're in the right directory
    if not Path("streamlit_dashboard.py").exists():
        print("❌ Error: streamlit_dashboard.py not found in current directory")
        print("Please run this script from the project directory.")
        return
    
    # Check if comparison data exists
    import glob
    comparison_files = glob.glob("esker_lodge_hours_comparison_*.xlsx")
    if not comparison_files:
        print("⚠️  Warning: No comparison data found!")
        print("Run 'python timesheet_payroll_comparison.py' first to generate the data.")
        response = input("Do you want to run the analysis now? (y/n): ")
        if response.lower() == 'y':
            print("Running timesheet analysis...")
            subprocess.run([sys.executable, "timesheet_payroll_comparison.py"])
        else:
            print("Dashboard will show an error message until data is generated.")
    
    print("🚀 Starting Esker Lodge Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the server")
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_dashboard.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    main() 