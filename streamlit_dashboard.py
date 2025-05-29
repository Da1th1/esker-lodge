#!/usr/bin/env python3
"""
Esker Lodge - Enhanced Timesheet vs Payroll Analysis Dashboard
============================================================

Real-time dashboard for comparing timesheet and payroll data with
Employee ID-based matching and detailed hour category breakdown.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import re
import os
from pathlib import Path

# Import our analysis functions
from timesheet_payroll_comparison_detailed import (
    load_and_clean_timesheet_data,
    load_and_clean_payroll_data_detailed,
    compare_hours_detailed,
    generate_detailed_reports,
    generate_comparison_reports,
    clean_name
)

# Page configuration
st.set_page_config(
    page_title="Esker Lodge - Payroll Analysis v2.1",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
        border-radius: 10px;
        border: 2px solid #1f4e79;
    }
    
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f4e79;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .alert-high { border-left-color: #dc3545; background-color: #f8d7da; }
    .alert-medium { border-left-color: #ffc107; background-color: #fff3cd; }
    .alert-low { border-left-color: #28a745; background-color: #d4edda; }
    
    .analysis-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    
    .success-badge {
        background-color: #28a745;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: bold;
    }
    
    .improvement-badge {
        background-color: #17a2b8;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.875rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading functions
@st.cache_data(ttl=300)  # 5-minute cache
def load_timesheet_data_cached():
    """Load and cache timesheet data."""
    csv_file = "master_timesheets_20250524_132012.csv"
    if os.path.exists(csv_file):
        return load_and_clean_timesheet_data(csv_file)
    return None

@st.cache_data(ttl=300)  # 5-minute cache
def load_payroll_data_cached():
    """Load and cache payroll data."""
    excel_file = "1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx"
    sheet_name = "1788-Esker Lodge Ltd Employee H"
    if os.path.exists(excel_file):
        return load_and_clean_payroll_data_detailed(excel_file, sheet_name)
    return None, {}

@st.cache_data(ttl=300)  # 5-minute cache
def perform_analysis_cached(tolerance=2.0):
    """Perform complete analysis with caching and enhanced reporting."""
    timesheet_df = load_timesheet_data_cached()
    payroll_data = load_payroll_data_cached()
    
    if timesheet_df is None or payroll_data[0] is None:
        return None, None, None, None, None, None, None, None
    
    payroll_df, hour_categories = payroll_data
    
    # Perform comparison
    comparison_df, hour_categories = compare_hours_detailed(
        timesheet_df, payroll_df, hour_categories, tolerance
    )
    
    # Generate basic reports
    comparison_report, anomalies, dept_summary, category_breakdown, stats = generate_detailed_reports(
        comparison_df, hour_categories, tolerance
    )
    
    # Generate enhanced comparison reports with employee categorization
    excel_file = "1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx"
    comparison_report, anomalies, dept_summary, category_breakdown, enhanced_stats, employee_categories, category_summary, comparison_metrics = generate_comparison_reports(
        comparison_report, anomalies, dept_summary, category_breakdown, stats, excel_file, timesheet_df, payroll_df
    )
    
    return comparison_report, anomalies, dept_summary, category_breakdown, enhanced_stats, employee_categories, category_summary, comparison_metrics

def create_coverage_chart(stats):
    """Create employee coverage visualization."""
    fig = go.Figure()
    
    categories = ['Matched Employees', 'Timesheet Only', 'Payroll Only']
    values = [
        stats['employees_in_both_systems'],
        stats['employees_timesheet_only'], 
        stats['employees_payroll_only']
    ]
    colors = ['#28a745', '#ffc107', '#dc3545']
    
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=values,
        textposition='auto',
        name='Employee Coverage'
    ))
    
    fig.update_layout(
        title=f"Employee Coverage Analysis (Total: {stats['total_employees']})",
        xaxis_title="Employee Categories",
        yaxis_title="Number of Employees",
        height=400,
        showlegend=False
    )
    
    return fig

def create_hours_breakdown_chart(comparison_report, hour_categories):
    """Create hour categories breakdown chart."""
    if not hour_categories:
        return None
    
    # Calculate totals for each category
    category_totals = {}
    for category in hour_categories.keys():
        if category in comparison_report.columns:
            total = comparison_report[category].sum()
            if total > 0:  # Only include categories with hours
                category_totals[category.replace(' Hours', '')] = total
    
    if not category_totals:
        return None
    
    # Sort by total hours
    sorted_categories = dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=list(sorted_categories.keys()),
        y=list(sorted_categories.values()),
        marker_color='#1f4e79',
        text=[f'{v:,.0f}h' for v in sorted_categories.values()],
        textposition='auto'
    ))
    
    fig.update_layout(
        title="Payroll Hours by Category",
        xaxis_title="Hour Categories",
        yaxis_title="Total Hours",
        height=500,
        xaxis_tickangle=-45
    )
    
    return fig

def create_mismatch_analysis_chart(comparison_report, stats):
    """Create mismatch analysis visualization."""
    if stats['employees_in_both_systems'] == 0:
        return None
    
    matched_employees = comparison_report[comparison_report['In Both Systems'] == True]
    
    # Calculate mismatch severity
    high_mismatches = len(matched_employees[matched_employees['Total Difference'].abs() > 20])
    medium_mismatches = len(matched_employees[
        (matched_employees['Total Difference'].abs() > 5) & 
        (matched_employees['Total Difference'].abs() <= 20)
    ])
    low_mismatches = len(matched_employees[
        (matched_employees['Total Difference'].abs() > 2) & 
        (matched_employees['Total Difference'].abs() <= 5)
    ])
    no_mismatches = len(matched_employees[matched_employees['Total Difference'].abs() <= 2])
    
    fig = go.Figure()
    
    categories = ['No Mismatch (≤2h)', 'Low (2-5h)', 'Medium (5-20h)', 'High (>20h)']
    values = [no_mismatches, low_mismatches, medium_mismatches, high_mismatches]
    colors = ['#28a745', '#ffc107', '#fd7e14', '#dc3545']
    
    fig.add_trace(go.Pie(
        labels=categories,
        values=values,
        marker_colors=colors,
        hole=0.4,
        textinfo='label+percent+value',
        textposition='auto'
    ))
    
    fig.update_layout(
        title=f"Mismatch Severity Analysis (Matched Employees: {stats['employees_in_both_systems']})",
        height=400
    )
    
    return fig

def display_time_period_analysis():
    """Display time period mismatch information."""
    st.markdown("### 📅 Time Period Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-container">
            <h4>📊 Timesheet Data Coverage</h4>
            <ul>
                <li><strong>Period:</strong> 2024-W01 to 2025-W20</li>
                <li><strong>Duration:</strong> 71 weeks (~16.5 months)</li>
                <li><strong>Employees:</strong> 105 unique IDs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-container alert-medium">
            <h4>📋 Payroll Data Coverage</h4>
            <ul>
                <li><strong>Period:</strong> "Jan to Apr" (~4 months)</li>
                <li><strong>Ratio:</strong> ~4.4x less than timesheet</li>
                <li><strong>Employees:</strong> 94 unique IDs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.warning("""
    **⚠️ Time Period Mismatch Detected:** The large hour discrepancy (34,342 hours) is primarily due to 
    different time periods covered by each dataset. Expected payroll hours for full timesheet period: ~77,600 hours.
    """)

def main():
    """Main dashboard function."""
    # Header
    st.markdown("""
    <div class="main-header">
        🏥 Esker Lodge Nursing Home<br>
        <small style="font-size: 1.2rem;">Enhanced Timesheet vs Payroll Analysis v2.1</small><br>
        <span class="success-badge">Employee ID-Based Matching</span>
        <span class="improvement-badge">18 Hour Categories</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Load and analyze data
    tolerance = 2.0  # Set default tolerance
    
    with st.spinner("Loading data and performing Employee ID-based analysis..."):
        results = perform_analysis_cached(tolerance)
        
        if any(result is None for result in results):
            st.error("❌ Unable to load required data files. Please ensure both timesheet and payroll files are available.")
            st.info("""
            Required files:
            - `master_timesheets_20250524_132012.csv`
            - `1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx`
            """)
            return
        
        comparison_report, anomalies, dept_summary, category_breakdown, enhanced_stats, employee_categories, category_summary, comparison_metrics = results
    
    # Main metrics
    st.markdown("## 📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        coverage_rate = enhanced_stats['coverage_rate']
        coverage_color = "alert-high" if coverage_rate < 50 else "alert-medium" if coverage_rate < 80 else "alert-low"
        st.markdown(f"""
        <div class="metric-container {coverage_color}">
            <h3>{coverage_rate:.1f}%</h3>
            <p>Employee Coverage Rate</p>
            <small>{enhanced_stats['employees_in_both_systems']} of {enhanced_stats['total_employees']} employees matched</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        mismatch_rate = (enhanced_stats['employees_with_mismatches'] / enhanced_stats['employees_in_both_systems'] * 100) if enhanced_stats['employees_in_both_systems'] > 0 else 0
        mismatch_color = "alert-low" if mismatch_rate < 10 else "alert-medium" if mismatch_rate < 50 else "alert-high"
        st.markdown(f"""
        <div class="metric-container {mismatch_color}">
            <h3>{mismatch_rate:.1f}%</h3>
            <p>Mismatch Rate</p>
            <small>{enhanced_stats['employees_with_mismatches']} employees with >{tolerance}h differences</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_diff = enhanced_stats['total_difference']
        diff_color = "alert-low" if abs(total_diff) < 1000 else "alert-medium" if abs(total_diff) < 10000 else "alert-high"
        st.markdown(f"""
        <div class="metric-container {diff_color}">
            <h3>{total_diff:+,.0f}h</h3>
            <p>Total Hour Difference</p>
            <small>{'Payroll exceeds' if total_diff > 0 else 'Timesheet exceeds'} by {abs(total_diff):,.0f}h</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        categories_tracked = len([cat for cat in comparison_report.columns if 'Hours' in cat and cat != 'Timesheet Hours'])
        st.markdown(f"""
        <div class="metric-container alert-low">
            <h3>{categories_tracked}</h3>
            <p>Hour Categories Tracked</p>
            <small>Complete payroll breakdown</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Analysis Tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Overview", "👥 Active Employees", "😴 Inactive/New Employees", 
        "🏢 Department Breakdown", "⏰ Hour Categories", "📅 Period Comparison", "📊 Data Reports"
    ])
    
    with tab1:
        st.markdown("### 🎯 Analysis Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Coverage chart
            coverage_fig = create_coverage_chart(enhanced_stats)
            st.plotly_chart(coverage_fig, use_container_width=True)
            
            # Key improvements
            st.markdown(f"""
            <div class="analysis-section">
                <h4>✅ Key Improvements (Employee ID-based)</h4>
                <ul>
                    <li><strong>Reliable Matching:</strong> {enhanced_stats['coverage_rate']:.1f}% coverage vs previous chaos</li>
                    <li><strong>Accurate Data:</strong> Name format issues resolved</li>
                    <li><strong>Complete Categories:</strong> All 18 hour types tracked</li>
                    <li><strong>Employee Status:</strong> {enhanced_stats.get('active_employees', 0)} active, {enhanced_stats.get('inactive_employees', 0)} inactive</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Mismatch analysis
            mismatch_fig = create_mismatch_analysis_chart(comparison_report, enhanced_stats)
            if mismatch_fig:
                st.plotly_chart(mismatch_fig, use_container_width=True)
            
            # Period alignment info
            period_status = "✅ Aligned" if not enhanced_stats.get('period_mismatch', True) else "⚠️ Mismatch"
            st.markdown(f"""
            <div class="analysis-section">
                <h4>📊 Data Quality Summary</h4>
                <ul>
                    <li><strong>Period Status:</strong> {period_status}</li>
                    <li><strong>Timesheet Period:</strong> {enhanced_stats.get('timesheet_period', 'Unknown')}</li>
                    <li><strong>Payroll Period:</strong> {enhanced_stats.get('payroll_period', 'Unknown')}</li>
                    <li><strong>Analysis Tolerance:</strong> ±{tolerance} hours</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 👥 Active Employees")
        
        # Show category summary first
        if category_summary is not None and not category_summary.empty:
            st.markdown("#### Employee Status Overview")
            
            # Create visual summary
            col1, col2, col3, col4 = st.columns(4)
            
            active_count = enhanced_stats.get('active_employees', 0)
            inactive_count = enhanced_stats.get('inactive_employees', 0) 
            new_count = enhanced_stats.get('new_employees', 0)
            terminated_count = enhanced_stats.get('terminated_employees', 0)
            
            with col1:
                st.metric("Active", active_count, help="Regular weekly activity")
            with col2:
                st.metric("Inactive/Minimal", inactive_count, help="Limited recent activity")
            with col3:
                st.metric("New", new_count, help="Started in 2025")
            with col4:
                st.metric("Terminated", terminated_count, help="Payroll only, no timesheet")
        
        # Filter to show only active employees
        if employee_categories is not None and not employee_categories.empty:
            active_employees = employee_categories[employee_categories['Category'] == 'Active']
            
            st.markdown(f"#### Active Employees ({len(active_employees)})")
            
            if not active_employees.empty:
                # Sort options
                sort_by = st.selectbox("Sort Active Employees By", 
                    options=["Total Difference", "Timesheet Hours", "Employee Name"],
                    index=0,
                    key="active_sort")
                
                # Sort data
                if sort_by == "Total Difference":
                    active_employees = active_employees.sort_values('Total Difference', key=abs, ascending=False)
                elif sort_by == "Timesheet Hours":
                    active_employees = active_employees.sort_values('Timesheet Hours', ascending=False)
                else:
                    active_employees = active_employees.sort_values('Employee Name')
                
                # Display table
                st.dataframe(
                    active_employees,
                    use_container_width=True,
                    height=400,
                    column_config={
                        "Employee ID": st.column_config.NumberColumn("ID", format="%d"),
                        "Total Difference": st.column_config.NumberColumn(
                            "Difference", 
                            format="%.1f h",
                            help="Positive = Payroll exceeds Timesheet"
                        ),
                        "Timesheet Hours": st.column_config.NumberColumn("Timesheet", format="%.1f h"),
                        "Payroll Hours Total": st.column_config.NumberColumn("Payroll", format="%.1f h"),
                    }
                )
            else:
                st.warning("No active employees found in the current analysis.")
        else:
            st.error("Employee categorization data not available.")
    
    with tab3:
        st.markdown("### 😴 Inactive/New Employees")
        
        if employee_categories is not None and not employee_categories.empty:
            # Filter for non-active employees
            inactive_categories = ['Inactive/Minimal', 'New Employee', 'Terminated/Payroll Only', 'Timesheet Only', 'Moderate Activity']
            inactive_employees = employee_categories[employee_categories['Category'].isin(inactive_categories)]
            
            # Create tabs for different types
            if not inactive_employees.empty:
                inactive_tab1, inactive_tab2, inactive_tab3 = st.tabs(["🔻 Inactive/Minimal", "🆕 New Employees", "🚪 Terminated/Other"])
                
                with inactive_tab1:
                    inactive_minimal = inactive_employees[inactive_employees['Category'].str.contains('Inactive|Minimal')]
                    st.markdown(f"#### Inactive/Minimal Activity ({len(inactive_minimal)})")
                    
                    if not inactive_minimal.empty:
                        st.dataframe(
                            inactive_minimal,
                            use_container_width=True,
                            column_config={
                                "Employee ID": st.column_config.NumberColumn("ID", format="%d"),
                                "Category": st.column_config.TextColumn("Status"),
                                "Reason": st.column_config.TextColumn("Details"),
                                "Timesheet Hours": st.column_config.NumberColumn("Timesheet", format="%.1f h"),
                                "Payroll Hours Total": st.column_config.NumberColumn("Payroll", format="%.1f h"),
                            }
                        )
                    else:
                        st.info("No inactive/minimal activity employees found.")
                
                with inactive_tab2:
                    new_employees = inactive_employees[inactive_employees['Category'] == 'New Employee']
                    st.markdown(f"#### New Employees ({len(new_employees)})")
                    
                    if not new_employees.empty:
                        st.dataframe(
                            new_employees,
                            use_container_width=True,
                            column_config={
                                "Employee ID": st.column_config.NumberColumn("ID", format="%d"),
                                "Reason": st.column_config.TextColumn("Start Details"),
                                "Timesheet Hours": st.column_config.NumberColumn("Timesheet", format="%.1f h"),
                                "Payroll Hours Total": st.column_config.NumberColumn("Payroll", format="%.1f h"),
                            }
                        )
                    else:
                        st.info("No new employees found.")
                
                with inactive_tab3:
                    other_employees = inactive_employees[
                        ~inactive_employees['Category'].isin(['Inactive/Minimal', 'New Employee']) |
                        inactive_employees['Category'].str.contains('Terminated|Timesheet Only|Moderate')
                    ]
                    st.markdown(f"#### Terminated/Other Status ({len(other_employees)})")
                    
                    if not other_employees.empty:
                        st.dataframe(
                            other_employees,
                            use_container_width=True,
                            column_config={
                                "Employee ID": st.column_config.NumberColumn("ID", format="%d"),
                                "Category": st.column_config.TextColumn("Status"),
                                "Reason": st.column_config.TextColumn("Details"),
                                "Timesheet Hours": st.column_config.NumberColumn("Timesheet", format="%.1f h"),
                                "Payroll Hours Total": st.column_config.NumberColumn("Payroll", format="%.1f h"),
                            }
                        )
                    else:
                        st.info("No terminated/other status employees found.")
            else:
                st.info("No inactive/new employees found in current analysis.")
        else:
            st.error("Employee categorization data not available.")
    
    with tab4:
        st.markdown("### 🏢 Department Analysis")
        
        if not dept_summary.empty:
            # Department summary chart
            fig = px.bar(
                dept_summary, 
                x='Department', 
                y=['Total Timesheet Hours', 'Total Payroll Hours'],
                title="Hours by Department",
                barmode='group',
                height=400
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Department summary table
            st.dataframe(
                dept_summary,
                use_container_width=True,
                column_config={
                    "Total Difference": st.column_config.NumberColumn(
                        "Difference", 
                        format="%.1f h"
                    ),
                    "Total Timesheet Hours": st.column_config.NumberColumn("Timesheet", format="%.1f h"),
                    "Total Payroll Hours": st.column_config.NumberColumn("Payroll", format="%.1f h"),
                }
            )
        else:
            st.warning("No department data available for analysis.")
    
    with tab5:
        st.markdown("### ⏰ Hour Categories Breakdown")
        
        # Hour categories chart
        hours_fig = create_hours_breakdown_chart(comparison_report, 
            {cat: col for cat, col in zip(
                [col.replace(' Hours', '') for col in comparison_report.columns if 'Hours' in col and col != 'Timesheet Hours'],
                [col for col in comparison_report.columns if 'Hours' in col and col != 'Timesheet Hours']
            )}
        )
        
        if hours_fig:
            st.plotly_chart(hours_fig, use_container_width=True)
            
            # Category breakdown table
            if category_breakdown is not None and not category_breakdown.empty:
                st.markdown("#### Category Details")
                
                # Aggregate by category
                category_summary = category_breakdown.groupby('Hour Category').agg({
                    'Hours': 'sum',
                    'Employee ID': 'nunique'
                }).reset_index()
                category_summary.columns = ['Hour Category', 'Total Hours', 'Employees']
                category_summary = category_summary.sort_values('Total Hours', ascending=False)
                
                st.dataframe(
                    category_summary,
                    use_container_width=True,
                    column_config={
                        "Total Hours": st.column_config.NumberColumn("Hours", format="%.1f h"),
                        "Employees": st.column_config.NumberColumn("Employees", format="%d"),
                    }
                )
        else:
            st.warning("No hour category data available.")
    
    with tab6:
        st.markdown("### 📅 Period Comparison Analysis")
        
        # Display actual extracted periods
        if comparison_metrics:
            data_alignment = comparison_metrics.get('data_alignment', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h4>📊 Timesheet Data Coverage</h4>
                    <ul>
                        <li><strong>Period:</strong> {data_alignment.get('timesheet_period', 'Unknown')}</li>
                        <li><strong>Duration:</strong> 71 weeks (~16.5 months)</li>
                        <li><strong>Employees:</strong> {enhanced_stats.get('employees_timesheet_only', 0) + enhanced_stats.get('employees_in_both_systems', 0)} unique IDs</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                period_match = data_alignment.get('period_match', False)
                alert_class = "alert-low" if period_match else "alert-medium"
                
                st.markdown(f"""
                <div class="metric-container {alert_class}">
                    <h4>📋 Payroll Data Coverage</h4>
                    <ul>
                        <li><strong>Period:</strong> {data_alignment.get('payroll_period', 'Unknown')}</li>
                        <li><strong>Alignment:</strong> {'✅ Matched' if period_match else '⚠️ Mismatch'}</li>
                        <li><strong>Employees:</strong> {enhanced_stats.get('employees_payroll_only', 0) + enhanced_stats.get('employees_in_both_systems', 0)} unique IDs</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Period alignment analysis
            if not period_match:
                st.warning(f"""
                **⚠️ Time Period Mismatch Detected:** {data_alignment.get('coverage_gap_explanation', 'Different time periods')}
                
                The large hour discrepancy is primarily due to different time periods covered by each dataset.
                """)
            else:
                st.success("✅ Time periods are aligned between timesheet and payroll data.")
            
            # Employee status breakdown
            employee_status = comparison_metrics.get('employee_status', {})
            
            st.markdown("### 👥 Employee Status Distribution")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Active", 
                    employee_status.get('active', 0),
                    help="Employees with regular weekly activity"
                )
            
            with col2:
                st.metric(
                    "Inactive/Minimal", 
                    employee_status.get('inactive_minimal', 0),
                    help="Employees with limited recent activity"
                )
            
            with col3:
                st.metric(
                    "New", 
                    employee_status.get('new', 0),
                    help="New employees (started in 2025)"
                )
            
            with col4:
                st.metric(
                    "Terminated", 
                    employee_status.get('terminated', 0),
                    help="Terminated employees (payroll only)"
                )
        else:
            st.error("Comparison metrics not available.")
        
        # Recommendations based on analysis
        st.markdown("""
        ### 🎯 Data Alignment Recommendations
        
        #### Immediate Actions:
        1. **Obtain Complete Payroll Data** - Request payroll data for full timesheet period
        2. **Investigate Unmatched Employees** - Review employees present in only one system
        3. **Validate Sample Calculations** - Manual verification of select employees
        
        #### Expected Results After Period Alignment:
        - **Realistic Hour Totals** - Payroll hours should approach timesheet totals
        - **Improved Match Rate** - >95% for employees in both systems  
        - **Accurate Discrepancies** - <10% legitimate timing/calculation differences
        """)
    
    with tab7:
        st.markdown("### 📊 Data Reports")
        
        # Add data reports section
        st.markdown("""
        ### 📊 Data Reports
        
        #### Immediate Actions:
        1. **Obtain Complete Payroll Data** - Request payroll data for full 2024-W01 to 2025-W20 period
        2. **Investigate Unmatched Employees** - 13 timesheet-only + 2 payroll-only employees need review
        3. **Validate Sample Calculations** - Manual verification of 5-10 employees recommended
        
        #### Expected Results After Alignment:
        - **Realistic Hour Totals** - Expect ~77,600 payroll hours (matching timesheet)
        - **Improved Match Rate** - >95% for employees in both systems  
        - **Accurate Discrepancies** - <10% legitimate timing/calculation differences
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        🏥 Esker Lodge Nursing Home - Enhanced Payroll Analysis Dashboard v2.1<br>
        <small>Employee ID-based matching with 18 hour categories | Last updated: {}</small>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main() 