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

def extract_date_range_from_filename(filename):
    """Extract date range from Excel filename."""
    # Extract date range from filename like "1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx"
    filename_lower = filename.lower()
    
    # Common month abbreviations
    months = {
        'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
        'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
        'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'
    }
    
    # Look for patterns like "Jan to Apr" or "January to April"
    for start_abbr, start_full in months.items():
        for end_abbr, end_full in months.items():
            pattern1 = f"{start_abbr} to {end_abbr}"
            pattern2 = f"{start_full} to {end_full}"
            
            if pattern1 in filename_lower:
                return f"{start_full} to {end_full}"
            elif pattern2 in filename_lower:
                return f"{start_full} to {end_full}"
    
    # Try to extract year if present
    year_match = re.search(r'\((\d+)\)', filename)
    year = year_match.group(1) if year_match else "Unknown Year"
    
    # Default fallback
    if "jan to apr" in filename_lower:
        return f"January to April {year}"
    
    return "Date range not specified"

def categorize_employees_by_activity(comparison_df, timesheet_df, payroll_df):
    """Categorize employees as active, inactive, or new based on data patterns."""
    
    try:
        # Debug: Print available columns
        print(f"Categorization debug - Available columns: {list(comparison_df.columns)}")
        
        # Analyze timesheet activity patterns
        timesheet_activity = timesheet_df.groupby('Employee_ID').agg({
            'Total Hours': ['sum', 'count'],
            'YearWeek': ['min', 'max']
        }).reset_index()
        
        # Flatten column names
        timesheet_activity.columns = ['Employee_ID', 'Total_Hours_Sum', 'Week_Count', 'First_Week', 'Last_Week']
        
        # Categorize employees
        categorized = []
        
        for _, row in comparison_df.iterrows():
            # Use the actual column names from comparison_df - check what's available
            emp_id = row.get('Employee ID', row.get('Employee_ID', None))
            emp_name = row.get('Employee Name', row.get('Employee_Name', 'Unknown'))
            
            if emp_id is None:
                print(f"Warning: Could not find Employee ID in row: {row.index.tolist()}")
                continue
                
            # Get activity data
            activity_data = timesheet_activity[timesheet_activity['Employee_ID'] == emp_id]
            
            category = "Unknown"
            reason = ""
            
            # Check column availability with fallbacks
            in_both = row.get('In Both Systems', row.get('In_Both', False))
            has_timesheet = row.get('Has Timesheet Data', row.get('In_Timesheet', False))
            has_payroll = row.get('Has Payroll Data', row.get('In_Payroll', False))
            timesheet_hours = row.get('Timesheet Hours', row.get('Total Hours', 0))
            payroll_hours = row.get('Payroll Hours Total', row.get('Total_Payroll_Hours', 0))
            total_diff = row.get('Total Difference', row.get('Total_Difference', 0))
            department = row.get('Department', 'Unknown')
            
            if in_both:
                # Employee in both systems
                if len(activity_data) > 0:
                    week_count = activity_data.iloc[0]['Week_Count']
                    total_hours = activity_data.iloc[0]['Total_Hours_Sum']
                    
                    if week_count >= 10 and total_hours > 100:  # Active threshold
                        category = "Active"
                        reason = f"Regular activity: {week_count} weeks, {total_hours:.0f} hours"
                    elif week_count < 5 or total_hours < 50:  # Inactive threshold
                        category = "Inactive/Minimal"
                        reason = f"Limited activity: {week_count} weeks, {total_hours:.0f} hours"
                    else:
                        category = "Moderate Activity"
                        reason = f"Moderate activity: {week_count} weeks, {total_hours:.0f} hours"
                else:
                    category = "Inactive/No Timesheet"
                    reason = "No timesheet records found"
                    
            elif has_timesheet and not has_payroll:
                # Timesheet only - might be new employee
                if len(activity_data) > 0:
                    week_count = activity_data.iloc[0]['Week_Count']
                    first_week = activity_data.iloc[0]['First_Week']
                    
                    if first_week >= '2025-W01':  # Started in 2025
                        category = "New Employee"
                        reason = f"Started {first_week}, {week_count} weeks active"
                    else:
                        category = "Timesheet Only"
                        reason = f"Active in timesheet ({week_count} weeks) but not in payroll"
                else:
                    category = "Timesheet Only"
                    reason = "In timesheet but not payroll"
                    
            elif has_payroll and not has_timesheet:
                # Payroll only - might be terminated employee
                category = "Terminated/Payroll Only"
                reason = "In payroll but no recent timesheet activity"
            
            categorized.append({
                'Employee ID': emp_id,
                'Employee Name': emp_name,
                'Category': category,
                'Reason': reason,
                'Timesheet Hours': timesheet_hours,
                'Payroll Hours Total': payroll_hours,
                'Total Difference': total_diff,
                'Department': department
            })
        
        print(f"Successfully categorized {len(categorized)} employees")
        return pd.DataFrame(categorized)
        
    except Exception as e:
        print(f"Error in employee categorization: {str(e)}")
        # Return empty dataframe on error
        return pd.DataFrame(columns=['Employee ID', 'Employee Name', 'Category', 'Reason', 'Timesheet Hours', 'Payroll Hours Total', 'Total Difference', 'Department'])

def generate_comparison_reports(comparison_report, anomalies, dept_summary, category_breakdown, stats, excel_filename, timesheet_df, payroll_df):
    """Generate enhanced reports with employee categorization and comparison features."""
    
    # Extract date range from filename
    payroll_period = extract_date_range_from_filename(excel_filename)
    
    # Get timesheet date range
    timesheet_period = f"{timesheet_df['YearWeek'].min()} to {timesheet_df['YearWeek'].max()}"
    
    # Categorize employees
    employee_categories = categorize_employees_by_activity(comparison_report, timesheet_df, payroll_df)
    
    # Create category summaries
    category_summary = employee_categories.groupby('Category').agg({
        'Employee ID': 'count',
        'Timesheet Hours': 'sum',
        'Payroll Hours Total': 'sum',
        'Total Difference': 'sum'
    }).reset_index()
    category_summary.columns = ['Category', 'Employee Count', 'Total Timesheet Hours', 'Total Payroll Hours', 'Total Difference']
    
    # Enhanced statistics with period information
    enhanced_stats = stats.copy()
    enhanced_stats.update({
        'payroll_period': payroll_period,
        'timesheet_period': timesheet_period,
        'period_mismatch': payroll_period != timesheet_period.replace('W', 'Week '),
        'active_employees': len(employee_categories[employee_categories['Category'] == 'Active']),
        'inactive_employees': len(employee_categories[employee_categories['Category'].str.contains('Inactive|Minimal')]),
        'new_employees': len(employee_categories[employee_categories['Category'] == 'New Employee']),
        'terminated_employees': len(employee_categories[employee_categories['Category'].str.contains('Terminated|Payroll Only')])
    })
    
    # Create comparison metrics
    comparison_metrics = {
        'data_alignment': {
            'timesheet_period': timesheet_period,
            'payroll_period': payroll_period,
            'period_match': not enhanced_stats['period_mismatch'],
            'coverage_gap_explanation': 'Timesheet covers 71 weeks vs Payroll covers ~16 weeks'
        },
        'employee_status': {
            'active': enhanced_stats['active_employees'],
            'inactive_minimal': enhanced_stats['inactive_employees'], 
            'new': enhanced_stats['new_employees'],
            'terminated': enhanced_stats['terminated_employees']
        }
    }
    
    return comparison_report, anomalies, dept_summary, category_breakdown, enhanced_stats, employee_categories, category_summary, comparison_metrics

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

def save_detailed_results(comparison_report, anomalies, dept_summary, category_breakdown, stats, employee_categories=None, category_summary=None):
    """Save all analysis results to Excel with multiple sheets including employee categorization."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"esker_lodge_enhanced_analysis_{timestamp}.xlsx"
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main comparison report
            comparison_report.to_excel(writer, sheet_name='Employee_Comparison', index=False)
            
            # Employee categories (new sheet)
            if employee_categories is not None:
                employee_categories.to_excel(writer, sheet_name='Employee_Categories', index=False)
            
            # Category summary (new sheet)
            if category_summary is not None:
                category_summary.to_excel(writer, sheet_name='Category_Summary', index=False)
            
            # Anomalies and high discrepancies
            if anomalies is not None and not anomalies.empty:
                anomalies.to_excel(writer, sheet_name='Anomalies', index=False)
            
            # Department summary
            if dept_summary is not None and not dept_summary.empty:
                dept_summary.to_excel(writer, sheet_name='Department_Summary', index=False)
            
            # Hour category breakdown
            if category_breakdown is not None and not category_breakdown.empty:
                category_breakdown.to_excel(writer, sheet_name='Hour_Categories', index=False)
            
            # Statistics summary
            stats_df = pd.DataFrame([stats])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
        print(f"✅ Enhanced results saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Error saving enhanced results: {str(e)}")
        return None

def display_enhanced_statistics(enhanced_stats, comparison_metrics):
    """Display enhanced analysis statistics."""
    print("\n" + "="*80)
    print("ENHANCED TIMESHEET vs PAYROLL ANALYSIS SUMMARY (Employee ID-based matching)")
    print("="*80)
    
    # Overall Matching Statistics
    print(f"\n📊 MATCHING ANALYSIS:")
    print(f"Total Employees Found: {enhanced_stats['total_employees']}")
    print(f"Employees in Both Systems: {enhanced_stats['employees_in_both_systems']}")
    print(f"Coverage Rate: {enhanced_stats['coverage_rate']:.1f}%")
    print(f"Employees Timesheet Only: {enhanced_stats['employees_timesheet_only']}")
    print(f"Employees Payroll Only: {enhanced_stats['employees_payroll_only']}")
    
    # Discrepancy Analysis
    mismatch_rate = (enhanced_stats['employees_with_mismatches'] / enhanced_stats['employees_in_both_systems'] * 100) if enhanced_stats['employees_in_both_systems'] > 0 else 0
    print(f"\n⚠️  DISCREPANCY ANALYSIS (for matched employees):")
    print(f"Employees with Mismatches: {enhanced_stats['employees_with_mismatches']}")
    print(f"Mismatch Rate: {mismatch_rate:.1f}%")
    print(f"Tolerance Threshold: ±{enhanced_stats['tolerance']} hours")
    
    # Hour Totals
    print(f"\n🕐 HOUR TOTALS:")
    print(f"Total Timesheet Hours: {enhanced_stats['total_timesheet_hours']:,.1f}")
    print(f"Total Payroll Hours: {enhanced_stats['total_payroll_hours']:,.1f}")
    print(f"Total Difference: {enhanced_stats['total_difference']:,.1f} hours")
    
    # Impact Assessment
    if enhanced_stats['total_difference'] != 0:
        if enhanced_stats['total_difference'] > 0:
            print(f"📈 Payroll exceeds timesheet by {abs(enhanced_stats['total_difference']):,.1f} hours")
        else:
            print(f"📉 Timesheet exceeds payroll by {abs(enhanced_stats['total_difference']):,.1f} hours")
    
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
        
        # Generate enhanced comparison reports with employee categorization
        comparison_report, anomalies, dept_summary, category_breakdown, enhanced_stats, employee_categories, category_summary, comparison_metrics = generate_comparison_reports(
            comparison_report, anomalies, dept_summary, category_breakdown, stats, excel_file, timesheet_df, payroll_df)
        
        # Save results
        output_file = save_detailed_results(comparison_report, anomalies, dept_summary, category_breakdown, enhanced_stats, employee_categories, category_summary)
        
        # Display statistics
        display_enhanced_statistics(enhanced_stats, comparison_metrics)
        
        # Print summary
        print("\n" + "="*80)
        print("ESKER LODGE - ENHANCED HOURS COMPARISON SUMMARY")
        print("="*80)
        
        print(f"\nPeriod Analysis:")
        print(f"  Timesheet Period: {enhanced_stats['timesheet_period']}")
        print(f"  Payroll Period: {enhanced_stats['payroll_period']}")
        print(f"  Period Alignment: {'❌ Mismatch' if enhanced_stats['period_mismatch'] else '✅ Aligned'}")
        
        print(f"\nEmployee Categorization:")
        print(f"  Active Employees: {enhanced_stats['active_employees']}")
        print(f"  Inactive/Minimal Activity: {enhanced_stats['inactive_employees']}")
        print(f"  New Employees: {enhanced_stats['new_employees']}")
        print(f"  Terminated/Payroll Only: {enhanced_stats['terminated_employees']}")
        
        print(f"\nOverall Statistics:")
        print(f"  Total Employees: {enhanced_stats['total_employees']}")
        print(f"  Employees with Mismatches (>{enhanced_stats['tolerance']}h): {enhanced_stats['employees_with_mismatches']}")
        print(f"  Total Timesheet Hours: {enhanced_stats['total_timesheet_hours']:,.1f}")
        print(f"  Total Payroll Hours: {enhanced_stats['total_payroll_hours']:,.1f}")
        print(f"  Total Difference: {enhanced_stats['total_difference']:+,.1f} hours")
        
        if hour_categories:
            print(f"\nHour Categories Tracked: {len(hour_categories)}")
            for category in hour_categories.keys():
                if category in comparison_report.columns:
                    total_hours = comparison_report[category].sum()
                    print(f"  {category}: {total_hours:,.1f} hours")
        
        print(f"\n✅ Enhanced analysis complete! Results saved to: {output_file}")
        
        return comparison_report, anomalies, dept_summary, category_breakdown, enhanced_stats, employee_categories, category_summary, comparison_metrics
        
    except Exception as e:
        print(f"❌ Error during enhanced analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None, None, None, None, None, None

if __name__ == "__main__":
    main() 