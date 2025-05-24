#!/usr/bin/env python3
"""
Esker Lodge Timesheet Analysis Script
Comprehensive analysis of staff working hours and anomaly detection
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TimesheetAnalyzer:
    def __init__(self, csv_file='master_timesheets_20250524_132012.csv'):
        self.csv_file = csv_file
        self.df = None
        self.cleaned_df = None
        
    def load_data(self):
        """Load and initial inspection of the timesheet data"""
        print("🔄 Loading timesheet data...")
        self.df = pd.read_csv(self.csv_file)
        print(f"✅ Loaded {len(self.df):,} records with {len(self.df.columns)} columns")
        print(f"📅 Time period: {self.df['YearWeek'].min()} to {self.df['YearWeek'].max()}")
        return self.df
    
    def clean_data(self):
        """Clean and prepare the data for analysis"""
        print("\n🧹 Cleaning data...")
        self.cleaned_df = self.df.copy()
        
        # Define hour columns
        hour_columns = ['Basic', 'Night Rate', 'Sunday Rate', 'Sunday Night Rate', 
                       'Holidays', 'Public Holiday Entitlement', 'Saturday Rate', 
                       'Saturday Night Rate', 'Total Hours']
        
        # Convert hour columns to numeric
        for col in hour_columns:
            if col in self.cleaned_df.columns:
                # Handle text values, empty strings, and convert to numeric
                self.cleaned_df[col] = pd.to_numeric(
                    self.cleaned_df[col].astype(str).str.replace(',', ''), 
                    errors='coerce'
                ).fillna(0)
        
        # Ensure Pay Rate is numeric
        if 'Pay Rate' in self.cleaned_df.columns:
            self.cleaned_df['Pay Rate'] = pd.to_numeric(
                self.cleaned_df['Pay Rate'], errors='coerce'
            )
        
        # Calculate Total Hours if needed (sum of all hour types)
        if 'Total Hours' in self.cleaned_df.columns:
            # If Total Hours is empty/zero, calculate from other fields
            mask = (self.cleaned_df['Total Hours'] == 0) | (self.cleaned_df['Total Hours'].isna())
            if mask.any():
                other_hour_cols = [col for col in hour_columns if col != 'Total Hours' and col in self.cleaned_df.columns]
                calculated_total = self.cleaned_df[other_hour_cols].sum(axis=1)
                self.cleaned_df.loc[mask, 'Total Hours'] = calculated_total[mask]
        
        # Clean department names
        if 'Department Name' in self.cleaned_df.columns:
            self.cleaned_df['Department_Clean'] = self.cleaned_df['Department Name'].fillna(self.cleaned_df['Department'])
        else:
            self.cleaned_df['Department_Clean'] = self.cleaned_df['Department']
        
        print(f"✅ Data cleaning completed")
        print(f"📊 Records with Total Hours > 0: {(self.cleaned_df['Total Hours'] > 0).sum():,}")
        
        return self.cleaned_df
    
    def basic_statistics(self):
        """Generate basic statistics and summaries"""
        print("\n📈 BASIC STATISTICS")
        print("=" * 50)
        
        # Overall statistics
        total_records = len(self.cleaned_df)
        unique_staff = self.cleaned_df['Name'].nunique()
        unique_departments = self.cleaned_df['Department_Clean'].nunique()
        
        print(f"Total Records: {total_records:,}")
        print(f"Unique Staff Members: {unique_staff:,}")
        print(f"Unique Departments: {unique_departments}")
        print(f"Time Period: {self.cleaned_df['YearWeek'].min()} to {self.cleaned_df['YearWeek'].max()}")
        
        # Hours statistics
        total_hours_worked = self.cleaned_df['Total Hours'].sum()
        avg_hours_per_record = self.cleaned_df['Total Hours'].mean()
        
        print(f"\nTotal Hours Worked: {total_hours_worked:,.2f}")
        print(f"Average Hours per Record: {avg_hours_per_record:.2f}")
        
        if total_hours_worked > 0:
            # Hours by department
            print(f"\n📊 HOURS BY DEPARTMENT")
            dept_hours = self.cleaned_df.groupby('Department_Clean')['Total Hours'].agg(['sum', 'mean', 'count']).round(2)
            dept_hours.columns = ['Total Hours', 'Avg Hours', 'Records']
            dept_hours = dept_hours.sort_values('Total Hours', ascending=False)
            print(dept_hours.head(10))
            
            # Hours by staff (top 10)
            print(f"\n👥 TOP 10 STAFF BY TOTAL HOURS")
            staff_hours = self.cleaned_df.groupby('Name')['Total Hours'].agg(['sum', 'mean', 'count']).round(2)
            staff_hours.columns = ['Total Hours', 'Avg Hours', 'Records']
            staff_hours = staff_hours.sort_values('Total Hours', ascending=False)
            print(staff_hours.head(10))
    
    def detect_anomalies(self):
        """Detect various anomalies in the timesheet data"""
        print("\n🚨 ANOMALY DETECTION")
        print("=" * 50)
        
        anomalies = {}
        
        # 1. Unusually high or low Total Hours
        high_hours_threshold = 60  # More than 60 hours per week
        low_hours_threshold = 1    # Less than 1 hour per week (but > 0)
        
        high_hours = self.cleaned_df[self.cleaned_df['Total Hours'] > high_hours_threshold]
        low_hours = self.cleaned_df[(self.cleaned_df['Total Hours'] > 0) & (self.cleaned_df['Total Hours'] < low_hours_threshold)]
        
        print(f"🔺 HIGH HOURS (>{high_hours_threshold}h/week): {len(high_hours)} records")
        if len(high_hours) > 0:
            print(high_hours[['Name', 'Department_Clean', 'Total Hours', 'YearWeek']].head(10))
            anomalies['high_hours'] = high_hours
        
        print(f"\n🔻 LOW HOURS (<{low_hours_threshold}h/week, >0): {len(low_hours)} records")
        if len(low_hours) > 0:
            print(low_hours[['Name', 'Department_Clean', 'Total Hours', 'YearWeek']].head(10))
            anomalies['low_hours'] = low_hours
        
        # 2. Staff with repeated 0 hours across multiple weeks
        zero_hours_by_staff = self.cleaned_df[self.cleaned_df['Total Hours'] == 0].groupby('Name').size()
        repeated_zero_hours = zero_hours_by_staff[zero_hours_by_staff >= 5]  # 5+ weeks of zero hours
        
        print(f"\n⚪ STAFF WITH REPEATED ZERO HOURS (5+ weeks): {len(repeated_zero_hours)}")
        if len(repeated_zero_hours) > 0:
            print(repeated_zero_hours.head(10))
            anomalies['repeated_zero_hours'] = repeated_zero_hours
        
        # 3. Missing Pay Rate where other work indicators are present
        missing_pay_rate = self.cleaned_df[
            (self.cleaned_df['Pay Rate'].isna()) & 
            (self.cleaned_df['Total Hours'] > 0)
        ]
        
        print(f"\n💰 MISSING PAY RATE WITH HOURS WORKED: {len(missing_pay_rate)} records")
        if len(missing_pay_rate) > 0:
            print(missing_pay_rate[['Name', 'Department_Clean', 'Total Hours', 'Pay Rate', 'YearWeek']].head(10))
            anomalies['missing_pay_rate'] = missing_pay_rate
        
        # 4. Staff appearing under multiple departments inconsistently
        staff_dept_changes = self.cleaned_df.groupby('Name')['Department_Clean'].nunique()
        multiple_departments = staff_dept_changes[staff_dept_changes > 1]
        
        print(f"\n🔄 STAFF IN MULTIPLE DEPARTMENTS: {len(multiple_departments)}")
        if len(multiple_departments) > 0:
            print(multiple_departments.head(10))
            anomalies['multiple_departments'] = multiple_departments
            
            # Show details for these staff
            print("\nDetails for staff in multiple departments:")
            for name in multiple_departments.head(5).index:
                staff_data = self.cleaned_df[self.cleaned_df['Name'] == name][['Name', 'Department_Clean', 'YearWeek']]
                unique_depts = staff_data['Department_Clean'].unique()
                print(f"{name}: {list(unique_depts)}")
        
        # 5. Overtime analysis (>48 hours/week)
        overtime_threshold = 48
        overtime_records = self.cleaned_df[self.cleaned_df['Total Hours'] > overtime_threshold]
        
        print(f"\n⏰ OVERTIME (>{overtime_threshold}h/week): {len(overtime_records)} records")
        if len(overtime_records) > 0:
            overtime_summary = overtime_records.groupby('Name').agg({
                'Total Hours': ['count', 'mean', 'max'],
                'YearWeek': 'count'
            }).round(2)
            overtime_summary.columns = ['Overtime_Weeks', 'Avg_Hours', 'Max_Hours', 'Total_Weeks']
            print(overtime_summary.head(10))
            anomalies['overtime'] = overtime_records
        
        return anomalies
    
    def weekly_analysis(self):
        """Analyze weekly trends and patterns"""
        print("\n📅 WEEKLY ANALYSIS")
        print("=" * 50)
        
        # Weekly total hours by department
        weekly_dept = self.cleaned_df.groupby(['YearWeek', 'Department_Clean'])['Total Hours'].sum().reset_index()
        weekly_total = self.cleaned_df.groupby('YearWeek')['Total Hours'].sum()
        
        print(f"📊 Weekly hours range: {weekly_total.min():.2f} - {weekly_total.max():.2f}")
        print(f"📊 Average weekly hours: {weekly_total.mean():.2f}")
        
        # Top 5 departments by total hours
        dept_totals = self.cleaned_df.groupby('Department_Clean')['Total Hours'].sum().sort_values(ascending=False)
        print(f"\nTop departments by total hours:")
        print(dept_totals.head(5))
        
        return weekly_dept, weekly_total
    
    def generate_summary_tables(self):
        """Generate summary tables for HR review"""
        print("\n📋 GENERATING SUMMARY TABLES")
        print("=" * 50)
        
        # Staff summary
        staff_summary = self.cleaned_df.groupby('Name').agg({
            'Total Hours': ['sum', 'mean', 'count', 'max'],
            'Department_Clean': lambda x: ', '.join(x.unique()),
            'Pay Rate': 'first',
            'YearWeek': ['min', 'max']
        }).round(2)
        
        staff_summary.columns = ['Total_Hours', 'Avg_Hours', 'Weeks_Worked', 'Max_Weekly_Hours', 
                                'Departments', 'Pay_Rate', 'First_Week', 'Last_Week']
        
        # Department summary
        dept_summary = self.cleaned_df.groupby('Department_Clean').agg({
            'Total Hours': ['sum', 'mean', 'count'],
            'Name': 'nunique',
            'Pay Rate': 'mean'
        }).round(2)
        
        dept_summary.columns = ['Total_Hours', 'Avg_Hours', 'Records', 'Unique_Staff', 'Avg_Pay_Rate']
        
        # Contract and Cost Centre analysis
        contract_summary = self.cleaned_df.groupby(['Contract', 'Cost Centre']).agg({
            'Total Hours': 'sum',
            'Name': 'nunique'
        }).round(2)
        
        return staff_summary, dept_summary, contract_summary
    
    def generate_hr_flags(self, anomalies):
        """Generate flags for HR review"""
        print("\n🚩 HR REVIEW FLAGS")
        print("=" * 50)
        
        flags = []
        
        # High priority flags
        if 'high_hours' in anomalies and len(anomalies['high_hours']) > 0:
            flags.append({
                'Priority': 'HIGH',
                'Type': 'Excessive Hours',
                'Count': len(anomalies['high_hours']),
                'Description': 'Staff working >60 hours/week - check for overtime compliance'
            })
        
        if 'missing_pay_rate' in anomalies and len(anomalies['missing_pay_rate']) > 0:
            flags.append({
                'Priority': 'HIGH',
                'Type': 'Missing Pay Rate',
                'Count': len(anomalies['missing_pay_rate']),
                'Description': 'Hours recorded without pay rate - payroll impact'
            })
        
        # Medium priority flags
        if 'multiple_departments' in anomalies and len(anomalies['multiple_departments']) > 0:
            flags.append({
                'Priority': 'MEDIUM',
                'Type': 'Department Changes',
                'Count': len(anomalies['multiple_departments']),
                'Description': 'Staff appearing in multiple departments - verify transfers'
            })
        
        if 'overtime' in anomalies and len(anomalies['overtime']) > 0:
            flags.append({
                'Priority': 'MEDIUM',
                'Type': 'Regular Overtime',
                'Count': len(anomalies['overtime']),
                'Description': 'Staff regularly working >48 hours/week'
            })
        
        # Low priority flags
        if 'repeated_zero_hours' in anomalies and len(anomalies['repeated_zero_hours']) > 0:
            flags.append({
                'Priority': 'LOW',
                'Type': 'Inactive Staff',
                'Count': len(anomalies['repeated_zero_hours']),
                'Description': 'Staff with 5+ weeks of zero hours - verify employment status'
            })
        
        flags_df = pd.DataFrame(flags)
        if len(flags_df) > 0:
            print(flags_df.to_string(index=False))
        else:
            print("No significant flags identified.")
        
        return flags_df
    
    def save_results(self, staff_summary, dept_summary, contract_summary, anomalies, flags_df):
        """Save analysis results to Excel files"""
        print("\n💾 SAVING RESULTS")
        print("=" * 50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Main analysis file
        analysis_file = f"timesheet_analysis_{timestamp}.xlsx"
        with pd.ExcelWriter(analysis_file, engine='openpyxl') as writer:
            staff_summary.to_excel(writer, sheet_name='Staff_Summary')
            dept_summary.to_excel(writer, sheet_name='Department_Summary')
            contract_summary.to_excel(writer, sheet_name='Contract_Summary')
            
            # Anomalies
            for anomaly_type, data in anomalies.items():
                if isinstance(data, pd.DataFrame) and len(data) > 0:
                    data.to_excel(writer, sheet_name=f'Anomaly_{anomaly_type}', index=False)
                elif isinstance(data, pd.Series) and len(data) > 0:
                    data.to_excel(writer, sheet_name=f'Anomaly_{anomaly_type}')
            
            # HR flags
            if len(flags_df) > 0:
                flags_df.to_excel(writer, sheet_name='HR_Flags', index=False)
        
        print(f"✅ Analysis saved to: {analysis_file}")
        
        # Save cleaned data
        cleaned_file = f"timesheet_cleaned_{timestamp}.csv"
        self.cleaned_df.to_csv(cleaned_file, index=False)
        print(f"✅ Cleaned data saved to: {cleaned_file}")
        
        return analysis_file, cleaned_file
    
    def run_full_analysis(self):
        """Run the complete analysis pipeline"""
        print("🚀 ESKER LODGE TIMESHEET ANALYSIS")
        print("=" * 70)
        
        # Load and clean data
        self.load_data()
        self.clean_data()
        
        # Basic statistics
        self.basic_statistics()
        
        # Anomaly detection
        anomalies = self.detect_anomalies()
        
        # Weekly analysis
        weekly_dept, weekly_total = self.weekly_analysis()
        
        # Generate summaries
        staff_summary, dept_summary, contract_summary = self.generate_summary_tables()
        
        # Generate HR flags
        flags_df = self.generate_hr_flags(anomalies)
        
        # Save results
        analysis_file, cleaned_file = self.save_results(
            staff_summary, dept_summary, contract_summary, anomalies, flags_df
        )
        
        print(f"\n✅ ANALYSIS COMPLETE!")
        print(f"📄 Results saved to: {analysis_file}")
        print(f"📄 Cleaned data: {cleaned_file}")
        
        return {
            'staff_summary': staff_summary,
            'dept_summary': dept_summary,
            'contract_summary': contract_summary,
            'anomalies': anomalies,
            'flags': flags_df,
            'weekly_data': (weekly_dept, weekly_total)
        }

def main():
    """Main execution function"""
    analyzer = TimesheetAnalyzer()
    results = analyzer.run_full_analysis()
    return results

if __name__ == "__main__":
    main() 