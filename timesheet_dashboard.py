#!/usr/bin/env python3
"""
Interactive Esker Lodge Timesheet Analysis Dashboard
Streamlit-based dashboard for comprehensive timesheet analysis and monitoring
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import glob
from datetime import datetime
import re

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Esker Lodge Timesheet Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f4e79;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.metric-card {
    background: linear-gradient(145deg, #f0f8ff, #e6f3ff);
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #1f4e79;
    margin: 0.5rem 0;
}
.alert-high {
    background-color: #ffe6e6;
    border-left: 5px solid #ff4444;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
.alert-medium {
    background-color: #fff4e6;
    border-left: 5px solid #ff8800;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
.alert-low {
    background-color: #e6ffe6;
    border-left: 5px solid #00cc44;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_timesheet_data():
    """Load and cache timesheet data"""
    # Find the latest cleaned file
    cleaned_files = glob.glob("corrected_timesheet_cleaned_*.csv")
    if cleaned_files:
        latest_file = max(cleaned_files)
        df = pd.read_csv(latest_file)
        
        # If this doesn't have the corrected hours columns, apply conversion
        if 'Total Hours_Hours' not in df.columns:
            df = apply_time_conversion(df)
    else:
        # Load master file and apply conversion
        df = pd.read_csv('master_timesheets_20250524_132012.csv')
        df = apply_time_conversion(df)
    
    return df

def parse_time_to_hours(time_str):
    """Convert time format (HH:MM) to decimal hours"""
    if pd.isna(time_str) or time_str == '' or time_str == 0:
        return 0.0
    
    time_str = str(time_str).strip()
    
    # Handle already numeric values
    try:
        return float(time_str)
    except:
        pass
    
    # Handle time format HH:MM
    if ':' in time_str:
        try:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return hours + (minutes / 60.0)
        except:
            return 0.0
    
    # Handle other formats
    try:
        numbers = re.findall(r'\d+', time_str)
        if len(numbers) >= 2:
            hours = int(numbers[0])
            minutes = int(numbers[1])
            return hours + (minutes / 60.0)
        elif len(numbers) == 1:
            return float(numbers[0])
    except:
        pass
    
    return 0.0

def apply_time_conversion(df):
    """Apply time format conversion to dataframe"""
    df_converted = df.copy()
    
    # Define hour columns
    hour_columns = ['Basic', 'Night Rate', 'Sunday Rate', 'Sunday Night Rate', 
                   'Holidays', 'Public Holiday Entitlement', 'Saturday Rate', 
                   'Saturday Night Rate', 'Total Hours']
    
    # Convert hour columns from time format to decimal hours
    for col in hour_columns:
        if col in df_converted.columns:
            df_converted[col + '_Hours'] = df_converted[col].apply(parse_time_to_hours)
    
    # Ensure Pay Rate is numeric
    if 'Pay Rate' in df_converted.columns:
        df_converted['Pay Rate'] = pd.to_numeric(df_converted['Pay Rate'], errors='coerce')
    
    # Clean department names
    if 'Department Name' in df_converted.columns:
        df_converted['Department_Clean'] = df_converted['Department Name'].fillna(df_converted['Department'])
    else:
        df_converted['Department_Clean'] = df_converted['Department']
    
    return df_converted

def create_overview_metrics(df):
    """Create overview metrics for the dashboard"""
    total_records = len(df)
    records_with_hours = (df['Total Hours_Hours'] > 0).sum()
    total_hours = df['Total Hours_Hours'].sum()
    unique_staff = df['Name'].nunique()
    unique_departments = df['Department_Clean'].nunique()
    
    # Compliance metrics
    overtime_records = (df['Total Hours_Hours'] > 48).sum()
    excessive_hours = (df['Total Hours_Hours'] > 60).sum()
    missing_pay_rate = ((df['Pay Rate'].isna()) & (df['Total Hours_Hours'] > 0)).sum()
    
    return {
        'total_records': total_records,
        'records_with_hours': records_with_hours,
        'total_hours': total_hours,
        'unique_staff': unique_staff,
        'unique_departments': unique_departments,
        'overtime_records': overtime_records,
        'excessive_hours': excessive_hours,
        'missing_pay_rate': missing_pay_rate
    }

def main():
    """Main dashboard function"""
    # Header
    st.markdown('<h1 class="main-header">🏥 Esker Lodge Timesheet Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading timesheet data..."):
        df = load_timesheet_data()
    
    # Sidebar filters
    st.sidebar.header("📋 Filters")
    
    # Department filter
    departments = ['All'] + sorted(df['Department_Clean'].unique().tolist())
    selected_dept = st.sidebar.selectbox("Department", departments)
    
    # Time period filter
    weeks = sorted(df['YearWeek'].unique())
    week_range = st.sidebar.select_slider(
        "Time Period",
        options=weeks,
        value=(weeks[0], weeks[-1])
    )
    
    # Filter data
    filtered_df = df.copy()
    if selected_dept != 'All':
        filtered_df = filtered_df[filtered_df['Department_Clean'] == selected_dept]
    
    filtered_df = filtered_df[
        (filtered_df['YearWeek'] >= week_range[0]) & 
        (filtered_df['YearWeek'] <= week_range[1])
    ]
    
    # Overview metrics
    metrics = create_overview_metrics(filtered_df)
    
    st.markdown("## 📊 Executive Dashboard")
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Hours Worked",
            value=f"{metrics['total_hours']:,.0f}",
            delta=f"{metrics['records_with_hours']:,} records"
        )
    
    with col2:
        st.metric(
            label="Active Staff",
            value=metrics['unique_staff'],
            delta=f"{metrics['unique_departments']} departments"
        )
    
    with col3:
        overtime_rate = (metrics['overtime_records'] / max(metrics['records_with_hours'], 1)) * 100
        st.metric(
            label="Overtime Rate",
            value=f"{overtime_rate:.1f}%",
            delta=f"{metrics['overtime_records']} records >48h",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Compliance Issues",
            value=metrics['excessive_hours'],
            delta="Records >60h/week",
            delta_color="inverse"
        )
    
    with col5:
        st.metric(
            label="Data Quality",
            value=metrics['missing_pay_rate'],
            delta="Missing pay rates",
            delta_color="inverse"
        )
    
    # Alert section
    if metrics['excessive_hours'] > 0 or metrics['missing_pay_rate'] > 0:
        st.markdown("### 🚨 Priority Alerts")
        
        if metrics['excessive_hours'] > 0:
            st.markdown(f"""
            <div class="alert-high">
                <strong>HIGH PRIORITY:</strong> {metrics['excessive_hours']} instances of staff working >60 hours/week detected. 
                This may violate EU Working Time Directive limits.
            </div>
            """, unsafe_allow_html=True)
        
        if metrics['missing_pay_rate'] > 0:
            st.markdown(f"""
            <div class="alert-medium">
                <strong>MEDIUM PRIORITY:</strong> {metrics['missing_pay_rate']} records have hours worked but missing pay rates. 
                This affects payroll accuracy.
            </div>
            """, unsafe_allow_html=True)
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", "🏢 Department Analysis", "👥 Staff Analysis", 
        "⚖️ Compliance", "📋 Data Quality"
    ])
    
    with tab1:
        st.markdown("### Weekly Trends Analysis")
        
        # Weekly trends chart
        weekly_data = filtered_df.groupby(['YearWeek', 'Department_Clean'])['Total Hours_Hours'].sum().reset_index()
        
        if not weekly_data.empty:
            fig = px.line(
                weekly_data, 
                x='YearWeek', 
                y='Total Hours_Hours', 
                color='Department_Clean',
                title="Weekly Hours by Department",
                labels={'Total Hours_Hours': 'Hours Worked', 'YearWeek': 'Week'}
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        # Hours distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Hours Distribution")
            hours_data = filtered_df[filtered_df['Total Hours_Hours'] > 0]['Total Hours_Hours']
            
            if not hours_data.empty:
                fig = px.histogram(
                    x=hours_data,
                    nbins=30,
                    title="Distribution of Weekly Hours",
                    labels={'x': 'Hours per Week', 'y': 'Frequency'}
                )
                fig.add_vline(x=48, line_dash="dash", line_color="red", annotation_text="48h Threshold")
                fig.add_vline(x=hours_data.mean(), line_dash="dash", line_color="orange", 
                             annotation_text=f"Mean: {hours_data.mean():.1f}h")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Compliance Overview")
            compliance_data = {
                'Category': ['Compliant (<48h)', 'Overtime (48-60h)', 'Excessive (>60h)'],
                'Count': [
                    len(filtered_df[filtered_df['Total Hours_Hours'] <= 48]),
                    len(filtered_df[(filtered_df['Total Hours_Hours'] > 48) & (filtered_df['Total Hours_Hours'] <= 60)]),
                    len(filtered_df[filtered_df['Total Hours_Hours'] > 60])
                ]
            }
            
            fig = px.pie(
                values=compliance_data['Count'],
                names=compliance_data['Category'],
                title="Hours Compliance Distribution",
                color_discrete_map={
                    'Compliant (<48h)': 'lightgreen',
                    'Overtime (48-60h)': 'orange', 
                    'Excessive (>60h)': 'red'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Department Performance Analysis")
        
        # Department summary
        dept_summary = filtered_df.groupby('Department_Clean').agg({
            'Total Hours_Hours': ['sum', 'mean', 'count'],
            'Name': 'nunique',
            'Pay Rate': 'mean'
        }).round(2)
        
        dept_summary.columns = ['Total Hours', 'Avg Hours/Record', 'Total Records', 'Unique Staff', 'Avg Pay Rate']
        dept_summary = dept_summary.sort_values('Total Hours', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Department Summary Table")
            st.dataframe(dept_summary, use_container_width=True)
        
        with col2:
            st.markdown("#### Total Hours by Department")
            fig = px.bar(
                x=dept_summary.index,
                y=dept_summary['Total Hours'],
                title="Total Hours by Department",
                labels={'x': 'Department', 'y': 'Total Hours'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Overtime analysis by department
        st.markdown("#### Overtime Analysis by Department")
        overtime_by_dept = filtered_df[filtered_df['Total Hours_Hours'] > 48].groupby('Department_Clean').agg({
            'Total Hours_Hours': ['count', 'mean']
        }).round(2)
        
        if not overtime_by_dept.empty:
            overtime_by_dept.columns = ['Overtime Records', 'Avg Overtime Hours']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    x=overtime_by_dept.index,
                    y=overtime_by_dept['Overtime Records'],
                    title="Overtime Records by Department",
                    labels={'x': 'Department', 'y': 'Number of Overtime Records'}
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    x=overtime_by_dept.index,
                    y=overtime_by_dept['Avg Overtime Hours'],
                    title="Average Overtime Hours by Department",
                    labels={'x': 'Department', 'y': 'Average Hours'}
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### Staff Performance Analysis")
        
        # Top performers
        staff_summary = filtered_df.groupby('Name').agg({
            'Total Hours_Hours': ['sum', 'mean', 'count', 'max'],
            'Department_Clean': lambda x: ', '.join(x.unique()),
            'Pay Rate': 'first'
        }).round(2)
        
        staff_summary.columns = ['Total Hours', 'Avg Hours', 'Weeks Worked', 'Max Weekly Hours', 'Departments', 'Pay Rate']
        staff_summary = staff_summary.sort_values('Total Hours', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top 15 Staff by Total Hours")
            st.dataframe(staff_summary.head(15), use_container_width=True)
        
        with col2:
            st.markdown("#### Staff with Highest Average Hours")
            top_avg_staff = staff_summary.sort_values('Avg Hours', ascending=False).head(10)
            
            fig = px.bar(
                x=top_avg_staff['Avg Hours'],
                y=top_avg_staff.index,
                orientation='h',
                title="Top 10 Staff by Average Hours",
                labels={'x': 'Average Hours per Week', 'y': 'Staff Name'}
            )
            fig.add_vline(x=48, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
        
        # Staff heatmap for top performers
        st.markdown("#### Staff Performance Heatmap (Top 20 Staff)")
        
        top_20_staff = staff_summary.head(20).index
        heatmap_data = filtered_df[filtered_df['Name'].isin(top_20_staff)].pivot_table(
            index='Name',
            columns='YearWeek',
            values='Total Hours_Hours',
            fill_value=0
        )
        
        if not heatmap_data.empty:
            # Limit to recent weeks for readability
            recent_weeks = heatmap_data.columns[-15:] if len(heatmap_data.columns) > 15 else heatmap_data.columns
            heatmap_recent = heatmap_data[recent_weeks]
            
            fig = px.imshow(
                heatmap_recent.values,
                x=heatmap_recent.columns,
                y=heatmap_recent.index,
                color_continuous_scale='YlOrRd',
                title="Staff Hours Heatmap (Recent Weeks)",
                labels={'x': 'Week', 'y': 'Staff Name', 'color': 'Hours'}
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### Compliance Monitoring")
        
        # High hours violations
        excessive_hours_data = filtered_df[filtered_df['Total Hours_Hours'] > 60]
        
        if not excessive_hours_data.empty:
            st.markdown("#### ⚠️ Excessive Hours Violations (>60h/week)")
            
            excessive_summary = excessive_hours_data.groupby('Name').agg({
                'Total Hours_Hours': ['count', 'mean', 'max'],
                'Department_Clean': 'first',
                'YearWeek': lambda x: ', '.join(x.astype(str))
            }).round(2)
            excessive_summary.columns = ['Violations', 'Avg Hours', 'Max Hours', 'Department', 'Weeks']
            
            st.dataframe(excessive_summary, use_container_width=True)
            
            # Violations by week
            violations_by_week = excessive_hours_data.groupby('YearWeek').size()
            
            fig = px.bar(
                x=violations_by_week.index,
                y=violations_by_week.values,
                title="Excessive Hours Violations by Week",
                labels={'x': 'Week', 'y': 'Number of Violations'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No excessive hours violations (>60h/week) found in the selected period.")
        
        # Overtime analysis
        st.markdown("#### Overtime Analysis (>48h/week)")
        
        overtime_data = filtered_df[filtered_df['Total Hours_Hours'] > 48]
        
        if not overtime_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                overtime_by_staff = overtime_data.groupby('Name').size().sort_values(ascending=False).head(15)
                
                fig = px.bar(
                    x=overtime_by_staff.values,
                    y=overtime_by_staff.index,
                    orientation='h',
                    title="Most Frequent Overtime Workers",
                    labels={'x': 'Number of Overtime Weeks', 'y': 'Staff Name'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                overtime_trend = overtime_data.groupby('YearWeek').size()
                
                fig = px.line(
                    x=overtime_trend.index,
                    y=overtime_trend.values,
                    title="Overtime Trend Over Time",
                    labels={'x': 'Week', 'y': 'Number of Overtime Records'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Compliance summary
        total_working_records = len(filtered_df[filtered_df['Total Hours_Hours'] > 0])
        overtime_rate = len(overtime_data) / max(total_working_records, 1) * 100
        violation_rate = len(excessive_hours_data) / max(total_working_records, 1) * 100
        
        st.markdown("#### Compliance Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if overtime_rate < 10:
                st.success(f"✅ Overtime Rate: {overtime_rate:.1f}% (Good)")
            elif overtime_rate < 20:
                st.warning(f"⚠️ Overtime Rate: {overtime_rate:.1f}% (Moderate)")
            else:
                st.error(f"❌ Overtime Rate: {overtime_rate:.1f}% (High)")
        
        with col2:
            if violation_rate == 0:
                st.success(f"✅ Violation Rate: {violation_rate:.1f}% (Compliant)")
            elif violation_rate < 1:
                st.warning(f"⚠️ Violation Rate: {violation_rate:.1f}% (Low Risk)")
            else:
                st.error(f"❌ Violation Rate: {violation_rate:.1f}% (High Risk)")
        
        with col3:
            missing_rate = metrics['missing_pay_rate'] / max(total_working_records, 1) * 100
            if missing_rate == 0:
                st.success(f"✅ Missing Pay Rate: {missing_rate:.1f}% (Complete)")
            elif missing_rate < 5:
                st.warning(f"⚠️ Missing Pay Rate: {missing_rate:.1f}% (Minor)")
            else:
                st.error(f"❌ Missing Pay Rate: {missing_rate:.1f}% (Significant)")
    
    with tab5:
        st.markdown("### Data Quality Analysis")
        
        # Missing pay rates
        missing_pay_data = filtered_df[(filtered_df['Pay Rate'].isna()) & (filtered_df['Total Hours_Hours'] > 0)]
        
        if not missing_pay_data.empty:
            st.markdown("#### 💰 Missing Pay Rate Records")
            
            missing_summary = missing_pay_data.groupby('Name').agg({
                'Total Hours_Hours': ['count', 'sum'],
                'Department_Clean': 'first'
            }).round(2)
            missing_summary.columns = ['Records', 'Total Hours Affected', 'Department']
            
            st.dataframe(missing_summary, use_container_width=True)
        else:
            st.success("✅ No missing pay rate issues found.")
        
        # Zero hours analysis
        st.markdown("#### ⭕ Staff with Multiple Zero-Hour Weeks")
        
        zero_hours_count = filtered_df[filtered_df['Total Hours_Hours'] == 0].groupby('Name').size()
        inactive_staff = zero_hours_count[zero_hours_count >= 5].sort_values(ascending=False)
        
        if not inactive_staff.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(inactive_staff.head(15), use_container_width=True)
            
            with col2:
                fig = px.bar(
                    x=inactive_staff.head(15).values,
                    y=inactive_staff.head(15).index,
                    orientation='h',
                    title="Staff with Most Zero-Hour Weeks",
                    labels={'x': 'Number of Zero-Hour Weeks', 'y': 'Staff Name'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("✅ No staff with excessive zero-hour weeks found.")
        
        # Data completeness summary
        st.markdown("#### 📊 Data Completeness Summary")
        
        completeness_data = {
            'Field': ['Name', 'Department', 'Total Hours', 'Pay Rate', 'YearWeek'],
            'Total Records': [len(filtered_df)] * 5,
            'Complete Records': [
                filtered_df['Name'].notna().sum(),
                filtered_df['Department_Clean'].notna().sum(),
                filtered_df['Total Hours_Hours'].notna().sum(),
                filtered_df['Pay Rate'].notna().sum(),
                filtered_df['YearWeek'].notna().sum()
            ]
        }
        
        completeness_df = pd.DataFrame(completeness_data)
        completeness_df['Completeness %'] = (completeness_df['Complete Records'] / completeness_df['Total Records'] * 100).round(1)
        
        st.dataframe(completeness_df, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    **Dashboard Information:**
    - Data loaded from: {len(df):,} total records
    - Filtered to: {len(filtered_df):,} records
    - Time period: {week_range[0]} to {week_range[1]}
    - Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)

if __name__ == "__main__":
    main() 