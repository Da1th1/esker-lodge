#!/usr/bin/env python3
"""
Generate a detailed summary report for the Esker Lodge timesheet vs payroll comparison.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def load_latest_comparison():
    """Load the most recent comparison file."""
    import glob
    files = glob.glob("esker_lodge_hours_comparison_*.xlsx")
    if not files:
        print("No comparison files found!")
        return None
    
    latest_file = max(files)
    print(f"Loading data from: {latest_file}")
    
    # Load all sheets
    sheets = {}
    with pd.ExcelFile(latest_file) as xls:
        for sheet_name in xls.sheet_names:
            sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
    
    return sheets, latest_file

def analyze_discrepancies(comparison_df, anomalies_df):
    """Provide detailed analysis of discrepancies."""
    
    print("\n" + "="*80)
    print("DETAILED DISCREPANCY ANALYSIS")
    print("="*80)
    
    # Overall statistics
    total_employees = len(comparison_df)
    employees_in_timesheet_only = len(comparison_df[comparison_df['Payroll Hours'] == 0])
    employees_in_payroll_only = len(comparison_df[comparison_df['Timesheet Hours'] == 0])
    employees_in_both = total_employees - employees_in_timesheet_only - employees_in_payroll_only
    
    print(f"\nEmployee Coverage:")
    print(f"  Total unique employees: {total_employees}")
    print(f"  In timesheet only: {employees_in_timesheet_only}")
    print(f"  In payroll only: {employees_in_payroll_only}")
    print(f"  In both systems: {employees_in_both}")
    
    # Discrepancy patterns
    if len(anomalies_df) > 0:
        print(f"\nDiscrepancy Patterns:")
        
        # Positive vs negative differences
        positive_diff = anomalies_df[anomalies_df['Difference'] > 0]
        negative_diff = anomalies_df[anomalies_df['Difference'] < 0]
        
        print(f"  Payroll > Timesheet: {len(positive_diff)} employees")
        print(f"  Timesheet > Payroll: {len(negative_diff)} employees")
        
        if len(positive_diff) > 0:
            print(f"  Avg excess in payroll: {positive_diff['Difference'].mean():.1f} hours")
        if len(negative_diff) > 0:
            print(f"  Avg excess in timesheet: {abs(negative_diff['Difference'].mean()):.1f} hours")
        
        # Department analysis
        dept_discrepancies = anomalies_df.groupby('Department').agg({
            'Employee Name': 'count',
            'Difference': ['mean', 'sum']
        }).round(2)
        
        print(f"\nDepartments with Most Discrepancies:")
        dept_discrepancies.columns = ['Count', 'Avg_Diff', 'Total_Diff']
        dept_discrepancies = dept_discrepancies.sort_values('Count', ascending=False)
        print(dept_discrepancies.head(10).to_string())

def identify_data_quality_issues(comparison_df):
    """Identify potential data quality issues."""
    
    print("\n" + "="*80)
    print("DATA QUALITY ANALYSIS")
    print("="*80)
    
    # Missing data
    missing_timesheet = comparison_df[comparison_df['Timesheet Hours'] == 0]
    missing_payroll = comparison_df[comparison_df['Payroll Hours'] == 0]
    
    print(f"\nMissing Data Issues:")
    print(f"  Employees with no timesheet hours: {len(missing_timesheet)}")
    print(f"  Employees with no payroll hours: {len(missing_payroll)}")
    
    if len(missing_timesheet) > 0:
        print(f"\nEmployees missing from timesheet (top 10):")
        print(missing_timesheet[['Employee Name', 'Department', 'Payroll Hours']].head(10).to_string(index=False))
    
    if len(missing_payroll) > 0:
        print(f"\nEmployees missing from payroll (top 10):")
        print(missing_payroll[['Employee Name', 'Department', 'Timesheet Hours']].head(10).to_string(index=False))
    
    # Extreme values
    high_hours = comparison_df[
        (comparison_df['Timesheet Hours'] > 2000) | 
        (comparison_df['Payroll Hours'] > 2000)
    ]
    
    if len(high_hours) > 0:
        print(f"\nEmployees with unusually high hours (>2000):")
        print(high_hours[['Employee Name', 'Department', 'Timesheet Hours', 'Payroll Hours']].to_string(index=False))

def generate_recommendations(comparison_df, anomalies_df):
    """Generate actionable recommendations."""
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    total_employees = len(comparison_df)
    mismatch_rate = len(anomalies_df) / total_employees * 100
    
    print(f"\n1. PRIORITY ACTIONS:")
    
    if mismatch_rate > 50:
        print(f"   🔴 HIGH PRIORITY: {mismatch_rate:.1f}% mismatch rate indicates systemic issues")
        print(f"      - Review data collection processes")
        print(f"      - Verify timesheet and payroll system integration")
    elif mismatch_rate > 20:
        print(f"   🟡 MEDIUM PRIORITY: {mismatch_rate:.1f}% mismatch rate needs attention")
    else:
        print(f"   🟢 LOW PRIORITY: {mismatch_rate:.1f}% mismatch rate is acceptable")
    
    # Specific recommendations based on data
    missing_timesheet = len(comparison_df[comparison_df['Timesheet Hours'] == 0])
    missing_payroll = len(comparison_df[comparison_df['Payroll Hours'] == 0])
    
    print(f"\n2. DATA RECONCILIATION:")
    if missing_timesheet > 0:
        print(f"   - Investigate {missing_timesheet} employees missing from timesheet system")
    if missing_payroll > 0:
        print(f"   - Investigate {missing_payroll} employees missing from payroll system")
    
    # Department-specific recommendations
    if len(anomalies_df) > 0:
        dept_issues = anomalies_df.groupby('Department').size().sort_values(ascending=False)
        print(f"\n3. DEPARTMENT FOCUS:")
        for dept, count in dept_issues.head(3).items():
            print(f"   - {dept}: {count} employees with discrepancies")
    
    print(f"\n4. PROCESS IMPROVEMENTS:")
    print(f"   - Implement weekly reconciliation checks")
    print(f"   - Set up automated alerts for discrepancies > 2 hours")
    print(f"   - Train staff on proper timesheet completion")
    print(f"   - Review approval workflows")

def main():
    """Main execution function."""
    
    # Load the latest comparison data
    sheets, filename = load_latest_comparison()
    if not sheets:
        return
    
    comparison_df = sheets['Hours Comparison']
    anomalies_df = sheets['Anomalies']
    dept_summary = sheets['Department Summary']
    
    print("ESKER LODGE NURSING HOME")
    print("Timesheet vs Payroll Hours - Detailed Analysis Report")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Source: {filename}")
    
    # Run analyses
    analyze_discrepancies(comparison_df, anomalies_df)
    identify_data_quality_issues(comparison_df)
    generate_recommendations(comparison_df, anomalies_df)
    
    print(f"\n" + "="*80)
    print("REPORT COMPLETE")
    print("="*80)
    print(f"For detailed data, see: {filename}")

if __name__ == "__main__":
    main() 