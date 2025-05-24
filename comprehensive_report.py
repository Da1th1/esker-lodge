#!/usr/bin/env python3
"""
Comprehensive Esker Lodge Timesheet Analysis Report
Generates a detailed summary report with findings and recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_latest_analysis():
    """Load the latest analysis results"""
    import glob
    
    # Load cleaned data
    cleaned_files = glob.glob("corrected_timesheet_cleaned_*.csv")
    if cleaned_files:
        latest_cleaned = max(cleaned_files)
        df = pd.read_csv(latest_cleaned)
    else:
        print("❌ No cleaned data found. Please run corrected_timesheet_analysis.py first.")
        return None
    
    return df

def generate_executive_summary(df):
    """Generate executive summary"""
    print("🎯 EXECUTIVE SUMMARY")
    print("=" * 70)
    
    total_records = len(df)
    records_with_hours = (df['Total Hours_Hours'] > 0).sum()
    total_hours = df['Total Hours_Hours'].sum()
    unique_staff = df['Name'].nunique()
    
    print(f"📊 OVERVIEW")
    print(f"   • Total Records: {total_records:,}")
    print(f"   • Records with Hours: {records_with_hours:,} ({records_with_hours/total_records*100:.1f}%)")
    print(f"   • Total Hours Worked: {total_hours:,.0f} hours")
    print(f"   • Unique Staff Members: {unique_staff}")
    print(f"   • Time Period: {df['YearWeek'].min()} to {df['YearWeek'].max()}")
    
    # Key findings
    overtime_records = (df['Total Hours_Hours'] > 48).sum()
    excessive_hours = (df['Total Hours_Hours'] > 60).sum()
    missing_pay_rate = ((df['Pay Rate'].isna()) & (df['Total Hours_Hours'] > 0)).sum()
    zero_hours_staff = (df[df['Total Hours_Hours'] == 0].groupby('Name').size() >= 5).sum()
    
    print(f"\n🚨 KEY CONCERNS")
    print(f"   • Overtime Records (>48h): {overtime_records} ({overtime_records/records_with_hours*100:.1f}%)")
    print(f"   • Excessive Hours (>60h): {excessive_hours}")
    print(f"   • Missing Pay Rates: {missing_pay_rate}")
    print(f"   • Inactive Staff (5+ zero weeks): {zero_hours_staff}")
    
    return {
        'total_records': total_records,
        'total_hours': total_hours,
        'unique_staff': unique_staff,
        'overtime_records': overtime_records,
        'excessive_hours': excessive_hours,
        'missing_pay_rate': missing_pay_rate,
        'zero_hours_staff': zero_hours_staff
    }

def generate_department_analysis(df):
    """Generate department analysis"""
    print("\n🏢 DEPARTMENT ANALYSIS")
    print("=" * 70)
    
    dept_summary = df.groupby('Department_Clean').agg({
        'Total Hours_Hours': ['sum', 'mean', 'count'],
        'Name': 'nunique',
        'Pay Rate': 'mean'
    }).round(2)
    
    dept_summary.columns = ['Total_Hours', 'Avg_Hours_Per_Record', 'Total_Records', 'Unique_Staff', 'Avg_Pay_Rate']
    dept_summary = dept_summary.sort_values('Total_Hours', ascending=False)
    
    print("📊 DEPARTMENT SUMMARY (Ranked by Total Hours)")
    print(dept_summary.to_string())
    
    # Department overtime analysis
    print(f"\n⏰ OVERTIME BY DEPARTMENT (>48h/week)")
    dept_overtime = df[df['Total Hours_Hours'] > 48].groupby('Department_Clean').agg({
        'Total Hours_Hours': ['count', 'mean']
    }).round(2)
    dept_overtime.columns = ['Overtime_Records', 'Avg_Overtime_Hours']
    dept_overtime = dept_overtime.sort_values('Overtime_Records', ascending=False)
    print(dept_overtime.to_string())
    
    return dept_summary, dept_overtime

def generate_staff_analysis(df):
    """Generate staff analysis"""
    print("\n👥 STAFF ANALYSIS")
    print("=" * 70)
    
    # Top performers by total hours
    staff_summary = df.groupby('Name').agg({
        'Total Hours_Hours': ['sum', 'mean', 'count', 'max'],
        'Department_Clean': lambda x: ', '.join(x.unique()),
        'Pay Rate': 'first'
    }).round(2)
    
    staff_summary.columns = ['Total_Hours', 'Avg_Hours', 'Weeks_Worked', 'Max_Weekly_Hours', 'Departments', 'Pay_Rate']
    staff_summary = staff_summary.sort_values('Total_Hours', ascending=False)
    
    print("📊 TOP 15 STAFF BY TOTAL HOURS")
    print(staff_summary.head(15).to_string())
    
    # Overtime champions
    overtime_staff = staff_summary[staff_summary['Max_Weekly_Hours'] > 48].sort_values('Max_Weekly_Hours', ascending=False)
    print(f"\n⏰ STAFF WITH OVERTIME (Max Weekly Hours >48)")
    print(f"Total staff with overtime: {len(overtime_staff)}")
    if len(overtime_staff) > 0:
        print(overtime_staff.head(10)[['Total_Hours', 'Avg_Hours', 'Max_Weekly_Hours', 'Departments']].to_string())
    
    return staff_summary, overtime_staff

def generate_anomaly_details(df):
    """Generate detailed anomaly analysis"""
    print("\n🚨 DETAILED ANOMALY ANALYSIS")
    print("=" * 70)
    
    anomalies = {}
    
    # 1. Excessive hours (>60h/week)
    excessive_hours = df[df['Total Hours_Hours'] > 60]
    print(f"1. EXCESSIVE HOURS (>60h/week): {len(excessive_hours)} records")
    if len(excessive_hours) > 0:
        print("   Staff involved:")
        excessive_summary = excessive_hours.groupby('Name').agg({
            'Total Hours_Hours': ['count', 'mean', 'max'],
            'Department_Clean': 'first',
            'YearWeek': lambda x: ', '.join(x.astype(str))
        }).round(2)
        excessive_summary.columns = ['Occurrences', 'Avg_Hours', 'Max_Hours', 'Department', 'Weeks']
        print(excessive_summary.to_string())
        anomalies['excessive_hours'] = excessive_summary
    
    # 2. Missing pay rates with hours worked
    missing_pay = df[(df['Pay Rate'].isna()) & (df['Total Hours_Hours'] > 0)]
    print(f"\n2. MISSING PAY RATES: {len(missing_pay)} records")
    if len(missing_pay) > 0:
        print("   Staff affected:")
        missing_summary = missing_pay.groupby('Name').agg({
            'Total Hours_Hours': ['count', 'sum'],
            'Department_Clean': 'first'
        }).round(2)
        missing_summary.columns = ['Records', 'Total_Hours_Affected', 'Department']
        print(missing_summary.to_string())
        anomalies['missing_pay'] = missing_summary
    
    # 3. Inactive staff (multiple zero-hour weeks)
    zero_hours_count = df[df['Total Hours_Hours'] == 0].groupby('Name').size()
    inactive_staff = zero_hours_count[zero_hours_count >= 5].sort_values(ascending=False)
    print(f"\n3. INACTIVE STAFF (5+ zero weeks): {len(inactive_staff)} staff")
    if len(inactive_staff) > 0:
        print("   Most inactive staff:")
        inactive_with_dept = df.groupby('Name')['Department_Clean'].first()
        inactive_df = pd.DataFrame({
            'Zero_Hour_Weeks': inactive_staff,
            'Department': inactive_with_dept[inactive_staff.index]
        })
        print(inactive_df.head(15).to_string())
        anomalies['inactive_staff'] = inactive_df
    
    # 4. Unusual patterns
    print(f"\n4. UNUSUAL PATTERNS")
    
    # Very low hours (>0 but <1)
    low_hours = df[(df['Total Hours_Hours'] > 0) & (df['Total Hours_Hours'] < 1)]
    print(f"   • Very low hours (<1h, >0): {len(low_hours)} records")
    
    # High frequency workers (appearing in >50 weeks)
    frequent_workers = df.groupby('Name').size()
    very_frequent = frequent_workers[frequent_workers > 50]
    print(f"   • High frequency workers (>50 weeks): {len(very_frequent)} staff")
    
    return anomalies

def generate_recommendations(df, summary_stats):
    """Generate HR recommendations"""
    print("\n💼 HR RECOMMENDATIONS")
    print("=" * 70)
    
    recommendations = []
    
    # High priority recommendations
    print("🔴 HIGH PRIORITY")
    
    if summary_stats['excessive_hours'] > 0:
        recommendations.append({
            'Priority': 'HIGH',
            'Issue': 'Excessive Working Hours',
            'Details': f"{summary_stats['excessive_hours']} instances of staff working >60 hours/week",
            'Action': 'Review overtime policies, check EU Working Time Directive compliance',
            'Timeline': 'Immediate'
        })
        print(f"   1. Review {summary_stats['excessive_hours']} cases of excessive hours (>60h/week)")
        print("      → Check compliance with Working Time Directive")
        print("      → Investigate workload distribution")
    
    if summary_stats['missing_pay_rate'] > 0:
        recommendations.append({
            'Priority': 'HIGH',
            'Issue': 'Missing Pay Rates',
            'Details': f"{summary_stats['missing_pay_rate']} records with hours but no pay rate",
            'Action': 'Update payroll system, ensure all working staff have valid pay rates',
            'Timeline': 'Immediate'
        })
        print(f"   2. Fix {summary_stats['missing_pay_rate']} missing pay rate records")
        print("      → Update payroll system immediately")
        print("      → Ensure accurate wage calculations")
    
    # Medium priority recommendations  
    print("\n🟡 MEDIUM PRIORITY")
    
    overtime_rate = (summary_stats['overtime_records'] / (df['Total Hours_Hours'] > 0).sum()) * 100
    if overtime_rate > 15:  # If >15% of records are overtime
        recommendations.append({
            'Priority': 'MEDIUM',
            'Issue': 'High Overtime Rate',
            'Details': f"{overtime_rate:.1f}% of working records are overtime (>48h)",
            'Action': 'Review staffing levels, consider additional hiring',
            'Timeline': '1-2 weeks'
        })
        print(f"   3. High overtime rate ({overtime_rate:.1f}% of records >48h)")
        print("      → Review staffing levels")
        print("      → Consider additional hiring")
    
    if summary_stats['zero_hours_staff'] > 10:
        recommendations.append({
            'Priority': 'MEDIUM',  
            'Issue': 'Inactive Staff Records',
            'Details': f"{summary_stats['zero_hours_staff']} staff with 5+ weeks of zero hours",
            'Action': 'Review employment status, clean up inactive records',
            'Timeline': '2-4 weeks'
        })
        print(f"   4. Review {summary_stats['zero_hours_staff']} inactive staff members")
        print("      → Verify current employment status")
        print("      → Clean up data records")
    
    # Low priority recommendations
    print("\n🟢 LOW PRIORITY")
    
    recommendations.append({
        'Priority': 'LOW',
        'Issue': 'Data Quality Improvement',
        'Details': 'Implement regular data validation checks',
        'Action': 'Set up automated data quality monitoring',
        'Timeline': '1 month'
    })
    print("   5. Implement data quality monitoring")
    print("      → Set up automated validation checks")
    print("      → Regular data accuracy reviews")
    
    return recommendations

def generate_compliance_check(df):
    """Generate compliance analysis"""
    print("\n⚖️ COMPLIANCE ANALYSIS")
    print("=" * 70)
    
    # EU Working Time Directive compliance
    print("📋 EU WORKING TIME DIRECTIVE COMPLIANCE")
    
    # 48-hour average check (over reference period)
    staff_avg_hours = df.groupby('Name')['Total Hours_Hours'].mean()
    non_compliant_avg = staff_avg_hours[staff_avg_hours > 48]
    
    print(f"   • Staff averaging >48h/week: {len(non_compliant_avg)}")
    if len(non_compliant_avg) > 0:
        print("     Most concerning:")
        print(non_compliant_avg.sort_values(ascending=False).head(5).to_string())
    
    # 60-hour maximum check
    max_hours_violations = (df['Total Hours_Hours'] > 60).sum()
    print(f"   • Records exceeding 60h/week: {max_hours_violations}")
    
    # Rest period analysis (would need additional data for full analysis)
    print(f"\n📊 ADDITIONAL COMPLIANCE CONSIDERATIONS")
    print("   • Daily rest periods: Requires daily timesheet data")
    print("   • Weekly rest periods: Requires detailed scheduling data")
    print("   • Night work limits: Partially visible in 'Night Rate' hours")
    
    # Calculate night work hours
    if 'Night Rate_Hours' in df.columns:
        night_work = df.groupby('Name')['Night Rate_Hours'].sum().sort_values(ascending=False)
        heavy_night_workers = night_work[night_work > 100]  # Significant night work
        print(f"   • Staff with significant night work (>100h total): {len(heavy_night_workers)}")

def main():
    """Generate comprehensive report"""
    print("📋 COMPREHENSIVE ESKER LODGE TIMESHEET ANALYSIS REPORT")
    print("Generated on:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    # Load data
    df = load_latest_analysis()
    if df is None:
        return
    
    # Generate report sections
    summary_stats = generate_executive_summary(df)
    dept_summary, dept_overtime = generate_department_analysis(df)
    staff_summary, overtime_staff = generate_staff_analysis(df)
    anomalies = generate_anomaly_details(df)
    recommendations = generate_recommendations(df, summary_stats)
    generate_compliance_check(df)
    
    # Summary conclusion
    print(f"\n🎯 CONCLUSION")
    print("=" * 70)
    print("This analysis reveals several areas requiring immediate attention:")
    print(f"• {summary_stats['excessive_hours']} cases of excessive working hours")
    print(f"• {summary_stats['missing_pay_rate']} payroll data inconsistencies")
    print(f"• {summary_stats['overtime_records']} overtime instances requiring review")
    print(f"• {summary_stats['zero_hours_staff']} inactive staff records to clean up")
    
    print("\nRecommendation: Prioritize high-priority issues for immediate resolution")
    print("to ensure compliance and accurate payroll processing.")
    
    print(f"\n📄 Supporting files generated:")
    print("   • corrected_timesheet_analysis_[timestamp].xlsx - Detailed analysis")
    print("   • corrected_timesheet_cleaned_[timestamp].csv - Clean dataset")
    print("   • Various PNG charts for visual analysis")

if __name__ == "__main__":
    main() 