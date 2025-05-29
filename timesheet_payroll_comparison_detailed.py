#!/usr/bin/env python3
"""
Enhanced Timesheet vs Payroll Comparison with Hour Category Breakdown
==================================================================

This script compares timesheet and payroll data and breaks down differences
by specific hour categories (Day Rate, Night Rate, Weekend shifts, etc.)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

def clean_name(name):
    """Clean and standardize employee names."""
    if pd.isna(name) or name == '':
        return ''
    
    name = str(name).strip()
    
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name)
    
    # Convert to title case
    name = name.title()
    
    # Handle common name variations
    name = name.replace("Mc ", "Mc").replace("O'", "O'")
    
    return name

def load_and_clean_timesheet_data(csv_file):
    """Load and clean timesheet data from CSV."""
    print("Loading timesheet data...")
    
    df = pd.read_csv(csv_file)
    print(f"Original timesheet data shape: {df.shape}")
    
    # Clean employee names
    df['Name_Cleaned'] = df['Name'].apply(clean_name)
    
    # Convert time format to decimal hours
    def convert_time_to_hours(time_str):
        if pd.isna(time_str) or time_str == '' or time_str == '00:00':
            return 0.0
        
        time_str = str(time_str).strip()
        
        if ':' in time_str:
            try:
                parts = time_str.split(':')
                hours = int(parts[0])
                minutes = int(parts[1])
                return round(hours + minutes/60, 2)
            except:
                return 0.0
        else:
            try:
                return float(time_str)
            except:
                return 0.0
    
    df['Total Hours'] = df['Total Hours'].apply(convert_time_to_hours)
    
    # Remove invalid entries
    df = df.dropna(subset=['Name_Cleaned'])
    df = df[df['Name_Cleaned'] != '']
    
    print(f"Cleaned timesheet data shape: {df.shape}")
    
    return df

def load_and_clean_payroll_data_detailed(excel_file, sheet_name):
    """Load payroll data with detailed hour category breakdown."""
    print("Loading detailed payroll data...")
    
    # Load with no header to see the structure
    df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
    
    # Get hour type names from row 3 (index 2)
    hour_types = df_raw.iloc[2].tolist()
    
    # Get column indicators from row 4 (index 3) 
    column_types = df_raw.iloc[3].tolist()
    
    # Load data starting from row 5 (index 4)
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=4)
    
    print(f"Original payroll data shape: {df.shape}")
    
    # Create full name
    df['Full_Name'] = df['Forename'].astype(str) + ' ' + df['Surname'].astype(str)
    df['Name_Cleaned'] = df['Full_Name'].apply(clean_name)
    
    # Remove invalid entries
    df = df.dropna(subset=['Name_Cleaned'])
    df = df[df['Name_Cleaned'] != '']
    df = df[df['Name_Cleaned'] != 'Nan Nan']
    
    # Map hour categories to their corresponding columns
    hour_categories = {}
    
    # Define the expected hour categories and their column mappings
    expected_categories = [
        'Day Rate', 'Night Rate', 'Sat Day', 'Sat Night', 'Sun Day', 'Sun Night',
        'Old Day/Sat Rate', 'Old Night Rate', 'Old Sun Rate', 'Extra Shift Bonus',
        'Backpay', 'Bank Holiday', 'Holiday Pay', 'Cross Function Day1', 
        'Cross Function Day2', 'Cross Function Sun1', 'Training/Meeting', 'Statutory Sick Pay'
    ]
    
    # Find hour columns by looking for 'Hrs' in column names
    hour_columns = [col for col in df.columns if 'Hrs' in str(col)]
    
    # Map categories to hour columns
    category_idx = 0
    for i, col in enumerate(df.columns):
        if col in hour_columns:
            # Find the corresponding category from the header rows
            if category_idx < len(expected_categories):
                category_name = expected_categories[category_idx]
                hour_categories[category_name] = col
                category_idx += 1
    
    print(f"Hour category mappings: {hour_categories}")
    
    # Convert hour columns to numeric
    for category, col in hour_categories.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate total hours
    hour_cols = list(hour_categories.values())
    existing_hour_cols = [col for col in hour_cols if col in df.columns]
    
    if existing_hour_cols:
        df['Total_Payroll_Hours'] = df[existing_hour_cols].sum(axis=1)
    else:
        df['Total_Payroll_Hours'] = 0
    
    print(f"Cleaned payroll data shape: {df.shape}")
    
    # Store category mappings for later use - use a different approach since pandas doesn't allow direct attribute assignment
    return df, hour_categories

def compare_hours_detailed(timesheet_df, payroll_df, hour_categories, tolerance=2.0):
    """Compare hours with detailed category breakdown."""
    print("Comparing hours with detailed breakdown...")
    
    # Aggregate timesheet data by name
    timesheet_total = timesheet_df.groupby('Name_Cleaned').agg({
        'Total Hours': 'sum',
        'Department Name': 'first'
    }).reset_index()
    
    # For payroll, we need to aggregate both totals and categories
    payroll_agg_data = {'Total_Payroll_Hours': 'sum', 'Depart': 'first'}
    
    # Add hour categories to aggregation using the actual column names (Hrs, Hrs.1, etc.)
    for category, col in hour_categories.items():
        if col in payroll_df.columns:
            payroll_agg_data[col] = 'sum'  # Use actual column name, not renamed
    
    payroll_agg = payroll_df.groupby('Name_Cleaned').agg(payroll_agg_data).reset_index()
    
    # Merge datasets
    comparison = pd.merge(timesheet_total, payroll_agg, on='Name_Cleaned', how='outer')
    
    # Fill missing values
    comparison['Total Hours'] = comparison['Total Hours'].fillna(0)
    comparison['Total_Payroll_Hours'] = comparison['Total_Payroll_Hours'].fillna(0)
    
    # Calculate total difference
    comparison['Total_Difference'] = comparison['Total_Payroll_Hours'] - comparison['Total Hours']
    comparison['Abs_Total_Difference'] = abs(comparison['Total_Difference'])
    
    # Flag mismatches
    comparison['Mismatch'] = comparison['Abs_Total_Difference'] > tolerance
    
    # Clean up department names
    comparison['Department'] = comparison['Department Name'].fillna(comparison['Depart'])
    
    # Fill category hour columns with 0 if missing
    for category, col in hour_categories.items():
        if col in comparison.columns:
            comparison[col] = comparison[col].fillna(0)
    
    return comparison, hour_categories

def generate_detailed_reports(comparison_df, hour_categories, tolerance=2.0):
    """Generate reports with detailed hour category breakdown."""
    print("Generating detailed reports...")
    
    # Prepare columns for main report
    base_columns = ['Name_Cleaned', 'Department', 'Total Hours', 'Total_Payroll_Hours', 'Total_Difference', 'Mismatch']
    
    # Add hour category columns (using actual column names)
    category_columns = []
    for category, col in hour_categories.items():
        if col in comparison_df.columns:
            category_columns.append(col)
    
    all_columns = base_columns + category_columns
    available_columns = [col for col in all_columns if col in comparison_df.columns]
    
    # Main comparison report
    comparison_report = comparison_df[available_columns].copy()
    
    # Rename columns for clarity
    column_rename = {
        'Name_Cleaned': 'Employee Name',
        'Total Hours': 'Timesheet Hours',
        'Total_Payroll_Hours': 'Payroll Hours Total',
        'Total_Difference': 'Total Difference',
        'Mismatch': 'Mismatch Flag'
    }
    
    # Add category column renames (from Hrs.X to actual category names)
    for category, col in hour_categories.items():
        if col in comparison_report.columns:
            column_rename[col] = category
    
    comparison_report = comparison_report.rename(columns=column_rename)
    
    # Sort by absolute difference
    comparison_report = comparison_report.sort_values('Total Difference', key=abs, ascending=False)
    
    # Create hour category breakdown report
    category_breakdown = None
    if hour_categories:
        breakdown_data = []
        for _, row in comparison_report.iterrows():
            employee_name = row['Employee Name']
            department = row['Department']
            
            for category in hour_categories.keys():
                if category in row.index:
                    breakdown_data.append({
                        'Employee Name': employee_name,
                        'Department': department,
                        'Hour Category': category,
                        'Hours': row[category],
                        'Timesheet Hours': row['Timesheet Hours']
                    })
        
        if breakdown_data:
            category_breakdown = pd.DataFrame(breakdown_data)
    
    # Anomalies report
    anomalies = comparison_report[comparison_report['Mismatch Flag'] == True].copy()
    
    # Department summary with category breakdowns
    dept_summary_data = []
    for dept in comparison_report['Department'].unique():
        if pd.isna(dept):
            continue
            
        dept_data = comparison_report[comparison_report['Department'] == dept]
        
        summary_row = {
            'Department': dept,
            'Employee Count': len(dept_data),
            'Total Timesheet Hours': dept_data['Timesheet Hours'].sum(),
            'Total Payroll Hours': dept_data['Payroll Hours Total'].sum(),
            'Total Difference': dept_data['Total Difference'].sum(),
            'Employees with Mismatches': (dept_data['Mismatch Flag'] == True).sum()
        }
        
        # Add category totals
        for category in hour_categories.keys():
            if category in dept_data.columns:
                summary_row[f'{category} Total'] = dept_data[category].sum()
        
        dept_summary_data.append(summary_row)
    
    dept_summary = pd.DataFrame(dept_summary_data)
    
    # Statistics
    stats = {
        'total_employees': len(comparison_report),
        'employees_with_mismatches': len(anomalies),
        'total_timesheet_hours': comparison_report['Timesheet Hours'].sum(),
        'total_payroll_hours': comparison_report['Payroll Hours Total'].sum(),
        'total_difference': comparison_report['Total Difference'].sum(),
        'tolerance': tolerance
    }
    
    return comparison_report, anomalies, dept_summary, category_breakdown, stats

def save_detailed_results(comparison_report, anomalies, dept_summary, category_breakdown, stats):
    """Save detailed results to Excel."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"esker_lodge_detailed_comparison_{timestamp}.xlsx"
    
    print(f"Saving detailed results to {filename}...")
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Main comparison with categories
        comparison_report.to_excel(writer, sheet_name='Detailed Hours Comparison', index=False)
        
        # Anomalies
        anomalies.to_excel(writer, sheet_name='Anomalies', index=False)
        
        # Department summary
        dept_summary.to_excel(writer, sheet_name='Department Summary', index=False)
        
        # Category breakdown
        if category_breakdown is not None:
            category_breakdown.to_excel(writer, sheet_name='Hour Category Breakdown', index=False)
        
        # Summary statistics
        stats_df = pd.DataFrame([stats])
        stats_df.to_excel(writer, sheet_name='Summary Statistics', index=False)
    
    return filename

def main():
    """Main execution function."""
    # File paths
    csv_file = "master_timesheets_20250524_132012.csv"
    excel_file = "1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx"
    sheet_name = "1788-Esker Lodge Ltd Employee H"
    tolerance = 2.0
    
    try:
        # Load and clean data
        timesheet_df = load_and_clean_timesheet_data(csv_file)
        payroll_df, hour_categories = load_and_clean_payroll_data_detailed(excel_file, sheet_name)
        
        # Compare hours with detailed breakdown
        comparison_df, hour_categories = compare_hours_detailed(timesheet_df, payroll_df, hour_categories, tolerance)
        
        # Generate detailed reports
        comparison_report, anomalies, dept_summary, category_breakdown, stats = generate_detailed_reports(
            comparison_df, hour_categories, tolerance)
        
        # Save results
        output_file = save_detailed_results(comparison_report, anomalies, dept_summary, category_breakdown, stats)
        
        # Print summary
        print("\n" + "="*80)
        print("ESKER LODGE - DETAILED HOURS COMPARISON SUMMARY")
        print("="*80)
        
        print(f"\nOverall Statistics:")
        print(f"  Total Employees: {stats['total_employees']}")
        print(f"  Employees with Mismatches (>{stats['tolerance']}h): {stats['employees_with_mismatches']}")
        print(f"  Mismatch Rate: {stats['employees_with_mismatches']/stats['total_employees']*100:.1f}%")
        print(f"  Total Timesheet Hours: {stats['total_timesheet_hours']:,.1f}")
        print(f"  Total Payroll Hours: {stats['total_payroll_hours']:,.1f}")
        print(f"  Total Difference: {stats['total_difference']:+,.1f} hours")
        
        if hour_categories:
            print(f"\nHour Categories Tracked: {len(hour_categories)}")
            for category in hour_categories.keys():
                if category in comparison_report.columns:
                    total_hours = comparison_report[category].sum()
                    print(f"  {category}: {total_hours:,.1f} hours")
        
        print(f"\n✅ Detailed analysis complete! Results saved to: {output_file}")
        
        return comparison_report, anomalies, dept_summary, category_breakdown
        
    except Exception as e:
        print(f"❌ Error during detailed analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None, None

if __name__ == "__main__":
    main() 