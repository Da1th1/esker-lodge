#!/usr/bin/env python3
"""
Esker Lodge Timesheet Visualizations
Creates charts and graphs for timesheet analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_cleaned_data():
    """Load the cleaned timesheet data"""
    # Use the most recent cleaned file
    import glob
    cleaned_files = glob.glob("corrected_timesheet_cleaned_*.csv")
    if cleaned_files:
        latest_file = max(cleaned_files)
        print(f"Loading cleaned data from: {latest_file}")
        return pd.read_csv(latest_file)
    else:
        print("No cleaned data file found. Please run corrected_timesheet_analysis.py first.")
        return None

def create_weekly_trends_chart(df):
    """Create weekly total hours trends by department"""
    plt.figure(figsize=(15, 8))
    
    # Aggregate weekly hours by department
    weekly_dept = df.groupby(['YearWeek', 'Department_Clean'])['Total Hours_Hours'].sum().reset_index()
    
    # Get top 6 departments by total hours
    top_depts = df.groupby('Department_Clean')['Total Hours_Hours'].sum().nlargest(6).index
    
    # Plot trends for top departments
    for dept in top_depts:
        dept_data = weekly_dept[weekly_dept['Department_Clean'] == dept]
        plt.plot(range(len(dept_data)), dept_data['Total Hours_Hours'], 
                marker='o', linewidth=2, label=dept, alpha=0.8)
    
    plt.title('Weekly Total Hours by Department (Top 6 Departments)', fontsize=16, fontweight='bold')
    plt.xlabel('Week Number', fontsize=12)
    plt.ylabel('Total Hours', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('weekly_hours_by_department.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return plt.gcf()

def create_department_breakdown_chart(df):
    """Create department breakdown charts"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Total hours by department (bar chart)
    dept_hours = df.groupby('Department_Clean')['Total Hours_Hours'].sum().sort_values(ascending=False)
    dept_hours.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_title('Total Hours by Department', fontweight='bold')
    ax1.set_ylabel('Total Hours')
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Average hours per staff by department
    dept_avg = df.groupby('Department_Clean')['Total Hours_Hours'].mean().sort_values(ascending=False)
    dept_avg.plot(kind='bar', ax=ax2, color='lightcoral')
    ax2.set_title('Average Hours per Record by Department', fontweight='bold')
    ax2.set_ylabel('Average Hours')
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Number of staff by department
    staff_count = df.groupby('Department_Clean')['Name'].nunique().sort_values(ascending=False)
    staff_count.plot(kind='bar', ax=ax3, color='lightgreen')
    ax3.set_title('Number of Unique Staff by Department', fontweight='bold')
    ax3.set_ylabel('Number of Staff')
    ax3.tick_params(axis='x', rotation=45)
    
    # 4. Department hours distribution (pie chart)
    dept_hours_top = dept_hours.head(8)
    others = dept_hours.iloc[8:].sum()
    if others > 0:
        dept_hours_top['Others'] = others
    
    ax4.pie(dept_hours_top.values, labels=dept_hours_top.index, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Hours Distribution by Department', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('department_breakdown.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def create_overtime_analysis_chart(df):
    """Create overtime analysis visualizations"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Distribution of weekly hours
    hours_data = df[df['Total Hours_Hours'] > 0]['Total Hours_Hours']
    ax1.hist(hours_data, bins=30, color='lightblue', alpha=0.7, edgecolor='black')
    ax1.axvline(48, color='red', linestyle='--', linewidth=2, label='48h Overtime Threshold')
    ax1.axvline(hours_data.mean(), color='orange', linestyle='--', linewidth=2, label=f'Mean: {hours_data.mean():.1f}h')
    ax1.set_title('Distribution of Weekly Hours Worked', fontweight='bold')
    ax1.set_xlabel('Hours per Week')
    ax1.set_ylabel('Frequency')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Overtime by department
    overtime_by_dept = df[df['Total Hours_Hours'] > 48].groupby('Department_Clean').size().sort_values(ascending=False)
    if len(overtime_by_dept) > 0:
        overtime_by_dept.plot(kind='bar', ax=ax2, color='salmon')
        ax2.set_title('Overtime Records by Department (>48h/week)', fontweight='bold')
        ax2.set_ylabel('Number of Overtime Records')
        ax2.tick_params(axis='x', rotation=45)
    
    # 3. Top staff with highest average hours
    top_staff = df.groupby('Name')['Total Hours_Hours'].mean().nlargest(10)
    top_staff.plot(kind='barh', ax=ax3, color='gold')
    ax3.set_title('Top 10 Staff by Average Weekly Hours', fontweight='bold')
    ax3.set_xlabel('Average Hours per Week')
    ax3.axvline(48, color='red', linestyle='--', alpha=0.7)
    
    # 4. Hours vs Pay Rate scatter plot
    active_staff = df[df['Total Hours_Hours'] > 0]
    scatter = ax4.scatter(active_staff['Pay Rate'], active_staff['Total Hours_Hours'], 
                         alpha=0.6, c=active_staff['Total Hours_Hours'], cmap='viridis')
    ax4.set_title('Hours Worked vs Pay Rate', fontweight='bold')
    ax4.set_xlabel('Pay Rate (€)')
    ax4.set_ylabel('Hours per Week')
    ax4.axhline(48, color='red', linestyle='--', alpha=0.7, label='48h Threshold')
    plt.colorbar(scatter, ax=ax4, label='Hours')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('overtime_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def create_contract_cost_center_analysis(df):
    """Create contract and cost center analysis"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Hours by Contract type
    contract_hours = df.groupby('Contract')['Total Hours_Hours'].sum().sort_values(ascending=False)
    contract_hours.plot(kind='bar', ax=ax1, color='mediumseagreen')
    ax1.set_title('Total Hours by Contract Type', fontweight='bold')
    ax1.set_ylabel('Total Hours')
    ax1.tick_params(axis='x', rotation=0)
    
    # 2. Staff count by Contract type
    contract_staff = df.groupby('Contract')['Name'].nunique()
    contract_staff.plot(kind='bar', ax=ax2, color='steelblue')
    ax2.set_title('Number of Staff by Contract Type', fontweight='bold')
    ax2.set_ylabel('Number of Staff')
    ax2.tick_params(axis='x', rotation=0)
    
    # 3. Hours by Cost Centre
    cost_center_hours = df.groupby('Cost Centre')['Total Hours_Hours'].sum().sort_values(ascending=False)
    cost_center_hours.plot(kind='bar', ax=ax3, color='plum')
    ax3.set_title('Total Hours by Cost Centre', fontweight='bold')
    ax3.set_ylabel('Total Hours')
    ax3.tick_params(axis='x', rotation=0)
    
    # 4. Average Pay Rate by Contract
    contract_pay = df.groupby('Contract')['Pay Rate'].mean()
    contract_pay.plot(kind='bar', ax=ax4, color='coral')
    ax4.set_title('Average Pay Rate by Contract Type', fontweight='bold')
    ax4.set_ylabel('Average Pay Rate (€)')
    ax4.tick_params(axis='x', rotation=0)
    
    plt.tight_layout()
    plt.savefig('contract_cost_center_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def create_staff_performance_heatmap(df):
    """Create staff performance heatmap"""
    # Get top 20 staff by total hours
    top_staff = df.groupby('Name')['Total Hours_Hours'].sum().nlargest(20).index
    
    # Create pivot table for heatmap
    staff_weekly = df[df['Name'].isin(top_staff)].pivot_table(
        index='Name', 
        columns='YearWeek', 
        values='Total Hours_Hours', 
        fill_value=0
    )
    
    # Only show recent weeks (last 20 weeks)
    recent_weeks = staff_weekly.columns[-20:]
    staff_weekly_recent = staff_weekly[recent_weeks]
    
    plt.figure(figsize=(20, 10))
    sns.heatmap(staff_weekly_recent, 
                cmap='YlOrRd', 
                cbar_kws={'label': 'Hours Worked'},
                linewidths=0.5,
                annot=False)
    
    plt.title('Staff Hours Heatmap - Top 20 Staff (Last 20 Weeks)', fontsize=16, fontweight='bold')
    plt.xlabel('Week', fontsize=12)
    plt.ylabel('Staff Name', fontsize=12)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    plt.savefig('staff_performance_heatmap.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return plt.gcf()

def create_anomaly_highlights(df):
    """Create visualizations highlighting anomalies"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. High hours staff (>60h/week)
    high_hours = df[df['Total Hours_Hours'] > 60]
    if len(high_hours) > 0:
        high_hours_summary = high_hours.groupby('Name')['Total Hours_Hours'].agg(['count', 'mean', 'max'])
        high_hours_summary['mean'].plot(kind='bar', ax=ax1, color='red', alpha=0.7)
        ax1.set_title('Staff with Excessive Hours (>60h/week)', fontweight='bold')
        ax1.set_ylabel('Average Hours')
        ax1.tick_params(axis='x', rotation=45)
        ax1.axhline(60, color='darkred', linestyle='--', alpha=0.8)
    
    # 2. Zero hours analysis
    zero_hours_count = df[df['Total Hours_Hours'] == 0].groupby('Name').size()
    top_zero_hours = zero_hours_count.nlargest(15)
    top_zero_hours.plot(kind='bar', ax=ax2, color='gray', alpha=0.7)
    ax2.set_title('Staff with Most Zero-Hour Weeks (Top 15)', fontweight='bold')
    ax2.set_ylabel('Number of Zero-Hour Weeks')
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Missing pay rate with hours
    missing_pay = df[(df['Pay Rate'].isna()) & (df['Total Hours_Hours'] > 0)]
    if len(missing_pay) > 0:
        missing_pay_summary = missing_pay.groupby('Name')['Total Hours_Hours'].sum().sort_values(ascending=False)
        missing_pay_summary.head(10).plot(kind='bar', ax=ax3, color='orange', alpha=0.7)
        ax3.set_title('Staff with Missing Pay Rates (Hours Worked)', fontweight='bold')
        ax3.set_ylabel('Total Hours without Pay Rate')
        ax3.tick_params(axis='x', rotation=45)
    
    # 4. Overtime frequency by staff
    overtime_freq = df[df['Total Hours_Hours'] > 48].groupby('Name').size().sort_values(ascending=False)
    if len(overtime_freq) > 0:
        overtime_freq.head(15).plot(kind='bar', ax=ax4, color='darkorange', alpha=0.7)
        ax4.set_title('Most Frequent Overtime Workers (Top 15)', fontweight='bold')
        ax4.set_ylabel('Number of Overtime Weeks')
        ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('anomaly_highlights.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return fig

def main():
    """Generate all visualizations"""
    print("🎨 ESKER LODGE TIMESHEET VISUALIZATIONS")
    print("=" * 60)
    
    # Load data
    df = load_cleaned_data()
    if df is None:
        return
    
    print(f"✅ Loaded {len(df):,} records for visualization")
    
    # Generate visualizations
    print("\n📊 Creating visualizations...")
    
    try:
        print("1. Weekly trends by department...")
        create_weekly_trends_chart(df)
        
        print("2. Department breakdown analysis...")
        create_department_breakdown_chart(df)
        
        print("3. Overtime analysis...")
        create_overtime_analysis_chart(df)
        
        print("4. Contract and cost center analysis...")
        create_contract_cost_center_analysis(df)
        
        print("5. Staff performance heatmap...")
        create_staff_performance_heatmap(df)
        
        print("6. Anomaly highlights...")
        create_anomaly_highlights(df)
        
        print("\n✅ All visualizations created successfully!")
        print("📁 Charts saved as PNG files in the current directory:")
        print("   - weekly_hours_by_department.png")
        print("   - department_breakdown.png") 
        print("   - overtime_analysis.png")
        print("   - contract_cost_center_analysis.png")
        print("   - staff_performance_heatmap.png")
        print("   - anomaly_highlights.png")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")

if __name__ == "__main__":
    main() 