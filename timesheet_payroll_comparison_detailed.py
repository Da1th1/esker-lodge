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
    
    # Clean employee names (keep for reference)
    df['Name_Cleaned'] = df['Name'].apply(clean_name)
    
    # Use Employee ID as primary key, clean it
    df['Employee_ID'] = pd.to_numeric(df['Staff Number'], errors='coerce')
    
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
    
    # Remove invalid entries - now using Employee_ID as primary filter
    df = df.dropna(subset=['Employee_ID'])
    df = df[df['Employee_ID'] > 0]  # Valid employee IDs should be positive
    
    print(f"Cleaned timesheet data shape: {df.shape}")
    print(f"Unique Employee IDs in timesheet: {df['Employee_ID'].nunique()}")
    
    return df

def load_and_clean_payroll_data_detailed(excel_file, sheet_name):
    """Load payroll data with detailed hour category breakdown."""
    print("Loading detailed payroll data...")
    
    # Load data with header in row 0
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=0)
    
    print(f"Original payroll data shape: {df.shape}")
    print(f"Excel columns: {df.columns.tolist()[:10]}")
    
    # Create full name (keep for reference)
    df['Full_Name'] = df['Forename'].astype(str) + ' ' + df['Surname'].astype(str)
    df['Name_Cleaned'] = df['Full_Name'].apply(clean_name)
    
    # Use Employee ID as primary key - clean the Sequence column
    df['Employee_ID'] = pd.to_numeric(df['Sequence'], errors='coerce')
    
    # Remove invalid entries - now using Employee_ID as primary filter
    df = df.dropna(subset=['Employee_ID'])
    df = df[df['Employee_ID'] > 0]  # Valid employee IDs should be positive
    df = df[df['Name_Cleaned'] != 'Nan Nan']
    
    print(f"Unique Employee IDs in payroll: {df['Employee_ID'].nunique()}")
    print(f"Sample Employee IDs: {sorted(df['Employee_ID'].unique())[:10]}")
    
    # Map hour categories to their corresponding columns
    hour_categories = {}
    
    # Map all hour categories (non-Gross columns) based on the actual Excel structure
    for col in df.columns:
        col_str = str(col).strip()
        # Skip gross pay columns
        if 'Gross' in col_str:
            continue
        # Skip employee info columns
        if col_str in ['Depart', 'Sequence', 'Forename', 'Surname']:
            continue
            
        # Map to appropriate category names
        if col_str == 'Basic':
            hour_categories['Basic Hours'] = col
        elif col_str == 'Night Rate':
            hour_categories['Night Rate Hours'] = col
        elif col_str == 'Saturday Rate':
            hour_categories['Saturday Day Hours'] = col
        elif col_str == 'Saturday Night Rate':
            hour_categories['Saturday Night Hours'] = col
        elif col_str == 'Sunday Rate':
            hour_categories['Sunday Day Hours'] = col
        elif col_str == 'Sunday Night Rate':
            hour_categories['Sunday Night Hours'] = col
        elif col_str == 'Old Day/Sat Rate':
            hour_categories['Old Day/Saturday Rate Hours'] = col
        elif col_str == 'Old Night Rate':
            hour_categories['Old Night Rate Hours'] = col
        elif col_str == 'Old Sun Rate':
            hour_categories['Old Sunday Rate Hours'] = col
        elif col_str == 'Non-Rostered Day':
            hour_categories['Non-Rostered Day Hours'] = col
        elif col_str == 'Backpay':
            hour_categories['Backpay Hours'] = col
        elif col_str == 'Public Holiday Entitlement':
            hour_categories['Public Holiday Hours'] = col
        elif col_str == 'Holidays':
            hour_categories['Holiday Hours'] = col
        elif col_str == 'Cross Function Day1':
            hour_categories['Cross Function Day1 Hours'] = col
        elif col_str == 'Cross Function Day2':
            hour_categories['Cross Function Day2 Hours'] = col
        elif col_str == 'Cross Function Sun1':
            hour_categories['Cross Function Sun1 Hours'] = col
        elif col_str == 'Training/Meetings':
            hour_categories['Training/Meeting Hours'] = col
        elif col_str == 'Statutory Sick':
            hour_categories['Statutory Sick Pay Hours'] = col
    
    print(f"Hour category mappings found: {len(hour_categories)}")
    for category, col in hour_categories.items():
        print(f"  {category}: {col}")
    
    # Convert hour columns to numeric
    for category, col in hour_categories.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate total hours
    hour_cols = list(hour_categories.values())
    existing_hour_cols = [col for col in hour_cols if col in df.columns]
    
    if existing_hour_cols:
        df['Total_Payroll_Hours'] = df[existing_hour_cols].sum(axis=1)
        print(f"Calculated total hours using {len(existing_hour_cols)} hour columns")
    else:
        df['Total_Payroll_Hours'] = 0
        print("Warning: No hour columns found for calculation")
    
    print(f"Cleaned payroll data shape: {df.shape}")
    print(f"Sample total hours: {df['Total_Payroll_Hours'].head().tolist()}")
    
    return df, hour_categories

def compare_hours_detailed(timesheet_df, payroll_df, hour_categories, tolerance=2.0):
    """Compare hours with detailed category breakdown using Employee IDs."""
    print("Comparing hours with detailed breakdown using Employee IDs...")
    
    # Aggregate timesheet data by Employee_ID
    timesheet_total = timesheet_df.groupby('Employee_ID').agg({
        'Total Hours': 'sum',
        'Department Name': 'first',
        'Name_Cleaned': 'first'  # Keep name for reference
    }).reset_index()
    
    # For payroll, we need to aggregate both totals and categories by Employee_ID
    payroll_agg_data = {
        'Total_Payroll_Hours': 'sum', 
        'Depart': 'first',
        'Name_Cleaned': 'first'  # Keep name for reference
    }
    
    # Add hour categories to aggregation using the actual column names (Hrs, Hrs.1, etc.)
    for category, col in hour_categories.items():
        if col in payroll_df.columns:
            payroll_agg_data[col] = 'sum'  # Use actual column name, not renamed
    
    payroll_agg = payroll_df.groupby('Employee_ID').agg(payroll_agg_data).reset_index()
    
    # Merge datasets on Employee_ID
    comparison = pd.merge(timesheet_total, payroll_agg, on='Employee_ID', how='outer')
    
    # Fill missing values
    comparison['Total Hours'] = comparison['Total Hours'].fillna(0)
    comparison['Total_Payroll_Hours'] = comparison['Total_Payroll_Hours'].fillna(0)
    
    # Use names for display (prefer timesheet name, fallback to payroll name)
    comparison['Employee_Name'] = comparison['Name_Cleaned_x'].fillna(comparison['Name_Cleaned_y'])
    comparison['Employee_Name'] = comparison['Employee_Name'].fillna('Unknown Employee')
    
    # Calculate total difference
    comparison['Total_Difference'] = comparison['Total_Payroll_Hours'] - comparison['Total Hours']
    comparison['Abs_Total_Difference'] = abs(comparison['Total_Difference'])
    
    # Flag mismatches
    comparison['Mismatch'] = comparison['Abs_Total_Difference'] > tolerance
    
    # Clean up department names (prefer timesheet dept, fallback to payroll dept)
    comparison['Department'] = comparison['Department Name'].fillna(comparison['Depart'])
    
    # Fill category hour columns with 0 if missing
    for category, col in hour_categories.items():
        if col in comparison.columns:
            comparison[col] = comparison[col].fillna(0)
    
    # Add matching status for analysis
    comparison['In_Timesheet'] = comparison['Total Hours'] > 0
    comparison['In_Payroll'] = comparison['Total_Payroll_Hours'] > 0
    comparison['In_Both'] = comparison['In_Timesheet'] & comparison['In_Payroll']
    
    print(f"Employees in timesheet only: {(~comparison['In_Payroll'] & comparison['In_Timesheet']).sum()}")
    print(f"Employees in payroll only: {(comparison['In_Payroll'] & ~comparison['In_Timesheet']).sum()}")
    print(f"Employees in both systems: {comparison['In_Both'].sum()}")
    
    return comparison, hour_categories

def generate_detailed_reports(comparison_df, hour_categories, tolerance=2.0):
    """Generate reports with detailed hour category breakdown."""
    print("Generating detailed reports...")
    
    # Prepare columns for main report
    base_columns = ['Employee_ID', 'Employee_Name', 'Department', 'Total Hours', 'Total_Payroll_Hours', 'Total_Difference', 'Mismatch', 'In_Timesheet', 'In_Payroll', 'In_Both']
    
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
        'Employee_ID': 'Employee ID',
        'Employee_Name': 'Employee Name',
        'Total Hours': 'Timesheet Hours',
        'Total_Payroll_Hours': 'Payroll Hours Total',
        'Total_Difference': 'Total Difference',
        'Mismatch': 'Mismatch Flag',
        'In_Timesheet': 'Has Timesheet Data',
        'In_Payroll': 'Has Payroll Data',
        'In_Both': 'In Both Systems'
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
            employee_id = row['Employee ID']
            employee_name = row['Employee Name']
            department = row['Department']
            
            for category in hour_categories.keys():
                if category in row.index:
                    breakdown_data.append({
                        'Employee ID': employee_id,
                        'Employee Name': employee_name,
                        'Department': department,
                        'Hour Category': category,
                        'Hours': row[category],
                        'Timesheet Hours': row['Timesheet Hours']
                    })
        
        if breakdown_data:
            category_breakdown = pd.DataFrame(breakdown_data)
    
    # Anomalies report (only employees in both systems with mismatches)
    anomalies = comparison_report[
        (comparison_report['Mismatch Flag'] == True) & 
        (comparison_report['In Both Systems'] == True)
    ].copy()
    
    # Department summary with category breakdowns
    dept_summary_data = []
    for dept in comparison_report['Department'].unique():
        if pd.isna(dept):
            continue
            
        dept_data = comparison_report[comparison_report['Department'] == dept]
        
        summary_row = {
            'Department': dept,
            'Employee Count': len(dept_data),
            'Employees in Both Systems': (dept_data['In Both Systems'] == True).sum(),
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
    
    # Enhanced statistics
    matched_employees = comparison_report[comparison_report['In Both Systems'] == True]
    
    stats = {
        'total_employees': len(comparison_report),
        'employees_in_both_systems': len(matched_employees),
        'employees_timesheet_only': (comparison_report['Has Timesheet Data'] & ~comparison_report['Has Payroll Data']).sum(),
        'employees_payroll_only': (comparison_report['Has Payroll Data'] & ~comparison_report['Has Timesheet Data']).sum(),
        'employees_with_mismatches': len(anomalies),
        'total_timesheet_hours': comparison_report['Timesheet Hours'].sum(),
        'total_payroll_hours': comparison_report['Payroll Hours Total'].sum(),
        'total_difference': comparison_report['Total Difference'].sum(),
        'tolerance': tolerance,
        'coverage_rate': len(matched_employees) / len(comparison_report) * 100 if len(comparison_report) > 0 else 0
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

def display_statistics(stats):
    """Display enhanced analysis statistics."""
    print("\n" + "="*80)
    print("ENHANCED TIMESHEET vs PAYROLL ANALYSIS SUMMARY (Employee ID-based matching)")
    print("="*80)
    
    # Overall Matching Statistics
    print(f"\n📊 MATCHING ANALYSIS:")
    print(f"Total Employees Found: {stats['total_employees']}")
    print(f"Employees in Both Systems: {stats['employees_in_both_systems']}")
    print(f"Coverage Rate: {stats['coverage_rate']:.1f}%")
    print(f"Employees Timesheet Only: {stats['employees_timesheet_only']}")
    print(f"Employees Payroll Only: {stats['employees_payroll_only']}")
    
    # Discrepancy Analysis
    mismatch_rate = (stats['employees_with_mismatches'] / stats['employees_in_both_systems'] * 100) if stats['employees_in_both_systems'] > 0 else 0
    print(f"\n⚠️  DISCREPANCY ANALYSIS (for matched employees):")
    print(f"Employees with Mismatches: {stats['employees_with_mismatches']}")
    print(f"Mismatch Rate: {mismatch_rate:.1f}%")
    print(f"Tolerance Threshold: ±{stats['tolerance']} hours")
    
    # Hour Totals
    print(f"\n🕐 HOUR TOTALS:")
    print(f"Total Timesheet Hours: {stats['total_timesheet_hours']:,.1f}")
    print(f"Total Payroll Hours: {stats['total_payroll_hours']:,.1f}")
    print(f"Total Difference: {stats['total_difference']:,.1f} hours")
    
    # Impact Assessment
    if stats['total_difference'] != 0:
        if stats['total_difference'] > 0:
            print(f"📈 Payroll exceeds timesheet by {abs(stats['total_difference']):,.1f} hours")
        else:
            print(f"📉 Timesheet exceeds payroll by {abs(stats['total_difference']):,.1f} hours")
    
    print("="*80)

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
        
        # Display statistics
        display_statistics(stats)
        
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