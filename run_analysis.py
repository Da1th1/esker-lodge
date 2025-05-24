#!/usr/bin/env python3
"""
Esker Lodge Timesheet Analysis - Main Launcher
Choose which analysis component to run
"""

import sys
import subprocess
import os
from datetime import datetime

def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🏥 ESKER LODGE TIMESHEET ANALYSIS SYSTEM")
    print("=" * 70)
    print(f"Welcome! Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def show_menu():
    """Show the main menu"""
    print("📋 AVAILABLE ANALYSIS OPTIONS:")
    print()
    print("1. 📊 Run Streamlit Dashboard (Interactive Web Interface)")
    print("2. 📄 Generate Customer Report (Professional PDF)")
    print("3. 🔧 Run Full Timesheet Analysis (Excel Output)")
    print("4. 📈 Generate Visualizations (PNG Charts)")
    print("5. 📝 Generate Comprehensive Report (Text Summary)")
    print("6. 🧹 Quick Data Explorer (Preview Dataset)")
    print("7. ❌ Exit")
    print()

def run_streamlit_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching Streamlit Dashboard...")
    print("📱 The dashboard will open in your web browser")
    print("🔗 Usually at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print()
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "timesheet_dashboard.py"])
    except KeyboardInterrupt:
        print("\n✅ Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def generate_customer_report():
    """Generate the professional customer report"""
    print("📄 Generating Professional Customer Report...")
    print("⏳ This may take a few minutes to create charts and PDF...")
    print()
    
    try:
        result = subprocess.run([sys.executable, "customer_report_generator.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Customer report generated successfully!")
            print(result.stdout)
        else:
            print("❌ Error generating customer report:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running customer report generator: {e}")

def run_full_analysis():
    """Run the full corrected timesheet analysis"""
    print("🔧 Running Full Timesheet Analysis...")
    print("📊 This will analyze all data and generate Excel files...")
    print()
    
    try:
        result = subprocess.run([sys.executable, "corrected_timesheet_analysis.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Full analysis completed!")
            print(result.stdout)
        else:
            print("❌ Error running analysis:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running analysis: {e}")

def generate_visualizations():
    """Generate visualization charts"""
    print("📈 Generating Visualization Charts...")
    print("🎨 Creating PNG chart files...")
    print()
    
    try:
        result = subprocess.run([sys.executable, "timesheet_visualizations.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Visualizations generated!")
            print(result.stdout)
        else:
            print("❌ Error generating visualizations:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")

def generate_comprehensive_report():
    """Generate comprehensive text report"""
    print("📝 Generating Comprehensive Report...")
    print("📋 Creating detailed text summary...")
    print()
    
    try:
        result = subprocess.run([sys.executable, "comprehensive_report.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Comprehensive report generated!")
            print(result.stdout)
        else:
            print("❌ Error generating comprehensive report:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error generating comprehensive report: {e}")

def run_data_explorer():
    """Run quick data explorer"""
    print("🧹 Running Quick Data Explorer...")
    print("👀 Examining dataset structure...")
    print()
    
    try:
        result = subprocess.run([sys.executable, "data_explorer.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Data exploration completed!")
            print(result.stdout)
        else:
            print("❌ Error running data explorer:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running data explorer: {e}")

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        'timesheet_dashboard.py',
        'customer_report_generator.py', 
        'corrected_timesheet_analysis.py',
        'timesheet_visualizations.py',
        'comprehensive_report.py',
        'data_explorer.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("⚠️  WARNING: Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print()
        return False
    
    return True

def main():
    """Main application loop"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Some required files are missing. Please ensure all analysis scripts are present.")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("👉 Please select an option (1-7): ").strip()
            print()
            
            if choice == '1':
                run_streamlit_dashboard()
            elif choice == '2':
                generate_customer_report()
            elif choice == '3':
                run_full_analysis()
            elif choice == '4':
                generate_visualizations()
            elif choice == '5':
                generate_comprehensive_report()
            elif choice == '6':
                run_data_explorer()
            elif choice == '7':
                print("👋 Goodbye! Thank you for using Esker Lodge Analysis System.")
                break
            else:
                print("❌ Invalid choice. Please select a number from 1-7.")
            
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Analysis system stopped by user.")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main() 