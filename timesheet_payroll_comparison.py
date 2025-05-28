#!/usr/bin/env python3
"""
Esker Lodge Nursing Home - Timesheet vs Payroll Hours Comparison
================================================================

This script compares timesheet data (CSV) with payroll data (Excel) to identify
discrepancies in recorded hours for staff members.

Author: AI Assistant
Date: 2025
"""

import pandas as pd
import numpy as np
import warnings
from datetime import datetime
import re

warnings.filterwarnings('ignore')

def clean_name(name):
    """
    Normalize name format for consistent matching.
    Handles various formats like "SURNAME, FIRSTNAME" and "Firstname, Lastname"
    """
    if pd.isna(name) or name == '':
        return ''
    
    name = str(name).strip()
    
    # Handle "SURNAME, FIRSTNAME" format
    if ',' in name:
        parts = name.split(',')
        if len(parts) == 2:
            surname = parts[0].strip()
            firstname = parts[1].strip()
            # Convert to "Firstname Lastname" format
            return f"{firstname.title()} {surname.title()}"
    
    # Already in "Firstname Lastname" format
    return name.title()

def load_and_clean_timesheet_data(csv_file):
    """
    Load and clean the timesheet CSV data.
    """
    print("Loading timesheet data...")
    df = pd.read_csv(csv_file)
    
    print(f"Original timesheet data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Clean and normalize names
    df['Name_Cleaned'] = df['Name'].apply(clean_name)
    
    # Convert Total Hours from HH:MM format to decimal hours
    def convert_time_to_hours(time_str):
        """Convert HH:MM format to decimal hours"""
        if pd.isna(time_str) or time_str == '':
            return 0.0
        
        time_str = str(time_str).strip()
        
        # Handle HH:MM format
        if ':' in time_str:
            try:
                parts = time_str.split(':')
                hours = float(parts[0])
                minutes = float(parts[1]) if len(parts) > 1 else 0
                return hours + (minutes / 60.0)
            except (ValueError, IndexError):
                return 0.0
        
        # Handle already numeric values
        try:
            return float(time_str)
        except ValueError:
            return 0.0
    
    df['Total Hours'] = df['Total Hours'].apply(convert_time_to_hours)
    
    # Remove rows with missing names
    df = df.dropna(subset=['Name_Cleaned'])
    df = df[df['Name_Cleaned'] != '']
    
    print(f"Cleaned timesheet data shape: {df.shape}")
    print(f"Sample Total Hours after conversion: {df['Total Hours'].head(10).tolist()}")
    
    return df

def load_and_clean_payroll_data(excel_file, sheet_name):
    """
    Load and clean the payroll Excel data.
    Uses row 5 (index 4) as headers and processes hour columns.
    """
    print("Loading payroll data...")
    
    # Load with row 5 as header (index 4)
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=4)
    
    print(f"Original payroll data shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Create full name from Forename and Surname
    df['Full_Name'] = df['Forename'].astype(str) + ' ' + df['Surname'].astype(str)
    df['Name_Cleaned'] = df['Full_Name'].apply(clean_name)
    
    # Remove rows with missing names
    df = df.dropna(subset=['Name_Cleaned'])
    df = df[df['Name_Cleaned'] != '']
    df = df[df['Name_Cleaned'] != 'Nan Nan']
    
    # Identify hour columns (columns that contain 'Hrs' in the name)
    hour_columns = [col for col in df.columns if 'Hrs' in str(col)]
    print(f"Hour columns found: {hour_columns}")
    
    # Convert hour columns to numeric
    for col in hour_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate total hours from all hour columns
    if hour_columns:
        df['Total_Payroll_Hours'] = df[hour_columns].sum(axis=1)
    else:
        # If no 'Hrs' columns found, look for other patterns
        # Look for columns that might contain hours data
        potential_hour_cols = []
        for col in df.columns:
            if any(keyword in str(col).lower() for keyword in ['day', 'night', 'sat', 'sun', 'training', 'sick', 'cross', 'function']):
                # Check if this column contains numeric data that could be hours
                try:
                    numeric_data = pd.to_numeric(df[col], errors='coerce')
                    if not numeric_data.isna().all() and (numeric_data >= 0).all():
                        potential_hour_cols.append(col)
                except:
                    continue
        
        print(f"Potential hour columns: {potential_hour_cols}")
        
        # Convert potential hour columns to numeric
        for col in potential_hour_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        if potential_hour_cols:
            df['Total_Payroll_Hours'] = df[potential_hour_cols].sum(axis=1)
        else:
            df['Total_Payroll_Hours'] = 0
    
    print(f"Cleaned payroll data shape: {df.shape}")
    
    return df

def compare_hours(timesheet_df, payroll_df, tolerance=2.0):
    """
    Compare hours between timesheet and payroll data.
    """
    print("Comparing hours between datasets...")
    
    # Aggregate timesheet data by name and week
    timesheet_agg = timesheet_df.groupby(['Name_Cleaned', 'YearWeek']).agg({
        'Total Hours': 'sum',
        'Department Name': 'first',
        'Year': 'first',
        'Week': 'first'
    }).reset_index()
    
    # Aggregate payroll data by name (no week info in payroll data)
    payroll_agg = payroll_df.groupby('Name_Cleaned').agg({
        'Total_Payroll_Hours': 'sum',
        'Depart': 'first'
    }).reset_index()
    
    # For comparison, also aggregate timesheet data by name only
    timesheet_total = timesheet_df.groupby('Name_Cleaned').agg({
        'Total Hours': 'sum',
        'Department Name': 'first'
    }).reset_index()
    
    # Merge datasets
    comparison = pd.merge(timesheet_total, payroll_agg, on='Name_Cleaned', how='outer')
    
    # Fill missing values
    comparison['Total Hours'] = comparison['Total Hours'].fillna(0)
    comparison['Total_Payroll_Hours'] = comparison['Total_Payroll_Hours'].fillna(0)
    
    # Calculate differences
    comparison['Difference'] = comparison['Total_Payroll_Hours'] - comparison['Total Hours']
    comparison['Abs_Difference'] = abs(comparison['Difference'])
    
    # Flag mismatches
    comparison['Mismatch'] = comparison['Abs_Difference'] > tolerance
    
    # Clean up department names
    comparison['Department'] = comparison['Department Name'].fillna(comparison['Depart'])
    
    return comparison, timesheet_agg

def generate_reports(comparison_df, timesheet_weekly_df, tolerance=2.0):
    """
    Generate comprehensive reports.
    """
    print("Generating reports...")
    
    # Main comparison report
    comparison_report = comparison_df[['Name_Cleaned', 'Department', 'Total Hours', 
                                     'Total_Payroll_Hours', 'Difference', 'Mismatch']].copy()
    comparison_report.columns = ['Employee Name', 'Department', 'Timesheet Hours', 
                                'Payroll Hours', 'Difference', 'Mismatch Flag']
    
    # Sort by absolute difference
    comparison_report = comparison_report.sort_values('Difference', key=abs, ascending=False)
    
    # Anomalies report (mismatches only)
    anomalies = comparison_report[comparison_report['Mismatch Flag'] == True].copy()
    
    # Summary statistics
    total_employees = len(comparison_report)
    employees_with_mismatches = len(anomalies)
    total_timesheet_hours = comparison_report['Timesheet Hours'].sum()
    total_payroll_hours = comparison_report['Payroll Hours'].sum()
    total_difference = comparison_report['Difference'].sum()
    
    # Department summary
    dept_summary = comparison_report.groupby('Department').agg({
        'Employee Name': 'count',
        'Timesheet Hours': 'sum',
        'Payroll Hours': 'sum',
        'Difference': 'sum',
        'Mismatch Flag': 'sum'
    }).reset_index()
    dept_summary.columns = ['Department', 'Employee Count', 'Total Timesheet Hours', 
                           'Total Payroll Hours', 'Total Difference', 'Employees with Mismatches']
    
    return comparison_report, anomalies, dept_summary, {
        'total_employees': total_employees,
        'employees_with_mismatches': employees_with_mismatches,
        'total_timesheet_hours': total_timesheet_hours,
        'total_payroll_hours': total_payroll_hours,
        'total_difference': total_difference,
        'tolerance': tolerance
    }

def save_results(comparison_report, anomalies, dept_summary, stats, timesheet_weekly):
    """
    Save results to Excel file with multiple sheets.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"esker_lodge_hours_comparison_{timestamp}.xlsx"
    
    print(f"Saving results to {filename}...")
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Main comparison
        comparison_report.to_excel(writer, sheet_name='Hours Comparison', index=False)
        
        # Anomalies
        anomalies.to_excel(writer, sheet_name='Anomalies', index=False)
        
        # Department summary
        dept_summary.to_excel(writer, sheet_name='Department Summary', index=False)
        
        # Weekly timesheet data
        timesheet_weekly.to_excel(writer, sheet_name='Weekly Timesheet Data', index=False)
        
        # Summary statistics
        stats_df = pd.DataFrame([stats])
        stats_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
    
    return filename

def print_summary(comparison_report, anomalies, dept_summary, stats):
    """
    Print summary to console.
    """
    print("\n" + "="*80)
    print("ESKER LODGE NURSING HOME - HOURS COMPARISON SUMMARY")
    print("="*80)
    
    print(f"\nOverall Statistics:")
    print(f"  Total Employees: {stats['total_employees']}")
    print(f"  Employees with Mismatches (>{stats['tolerance']}h): {stats['employees_with_mismatches']}")
    print(f"  Mismatch Rate: {stats['employees_with_mismatches']/stats['total_employees']*100:.1f}%")
    print(f"  Total Timesheet Hours: {stats['total_timesheet_hours']:,.1f}")
    print(f"  Total Payroll Hours: {stats['total_payroll_hours']:,.1f}")
    print(f"  Total Difference: {stats['total_difference']:+,.1f} hours")
    
    print(f"\nTop 10 Largest Discrepancies:")
    print(anomalies.head(10)[['Employee Name', 'Department', 'Timesheet Hours', 
                             'Payroll Hours', 'Difference']].to_string(index=False))
    
    print(f"\nDepartment Summary:")
    print(dept_summary.to_string(index=False))

def main():
    """
    Main execution function.
    """
    # File paths
    csv_file = "master_timesheets_20250524_132012.csv"
    excel_file = "1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx"
    sheet_name = "1788-Esker Lodge Ltd Employee H"
    tolerance = 2.0  # Hours tolerance for mismatch detection
    
    try:
        # Load and clean data
        timesheet_df = load_and_clean_timesheet_data(csv_file)
        payroll_df = load_and_clean_payroll_data(excel_file, sheet_name)
        
        # Compare hours
        comparison_df, timesheet_weekly = compare_hours(timesheet_df, payroll_df, tolerance)
        
        # Generate reports
        comparison_report, anomalies, dept_summary, stats = generate_reports(
            comparison_df, timesheet_weekly, tolerance)
        
        # Save results
        output_file = save_results(comparison_report, anomalies, dept_summary, stats, timesheet_weekly)
        
        # Print summary
        print_summary(comparison_report, anomalies, dept_summary, stats)
        
        print(f"\n✅ Analysis complete! Results saved to: {output_file}")
        
        return comparison_report, anomalies, dept_summary
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    main() 