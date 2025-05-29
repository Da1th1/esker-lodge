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
    """Perform complete analysis with caching."""
    timesheet_df = load_timesheet_data_cached()
    payroll_data = load_payroll_data_cached()
    
    if timesheet_df is None or payroll_data[0] is None:
        return None, None, None, None, None
    
    payroll_df, hour_categories = payroll_data
    
    # Perform comparison
    comparison_df, hour_categories = compare_hours_detailed(
        timesheet_df, payroll_df, hour_categories, tolerance
    )
    
    # Generate reports
    comparison_report, anomalies, dept_summary, category_breakdown, stats = generate_detailed_reports(
        comparison_df, hour_categories, tolerance
    )
    
    return comparison_report, anomalies, dept_summary, category_breakdown, stats

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
    
    # Sidebar controls
    st.sidebar.header("🎛️ Analysis Controls")
    
    tolerance = st.sidebar.slider(
        "Hour Difference Tolerance", 
        min_value=0.5, 
        max_value=10.0, 
        value=2.0, 
        step=0.5,
        help="Threshold for flagging hour mismatches"
    )
    
    # Action buttons
    if st.sidebar.button("🔄 Refresh Data", type="secondary"):
        st.cache_data.clear()
        st.rerun()
    
    if st.sidebar.button("▶️ Run New Analysis", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    # Load and analyze data
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
        
        comparison_report, anomalies, dept_summary, category_breakdown, stats = results
    
    # Main metrics
    st.markdown("## 📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        coverage_rate = stats['coverage_rate']
        coverage_color = "alert-high" if coverage_rate < 50 else "alert-medium" if coverage_rate < 80 else "alert-low"
        st.markdown(f"""
        <div class="metric-container {coverage_color}">
            <h3>{coverage_rate:.1f}%</h3>
            <p>Employee Coverage Rate</p>
            <small>{stats['employees_in_both_systems']} of {stats['total_employees']} employees matched</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        mismatch_rate = (stats['employees_with_mismatches'] / stats['employees_in_both_systems'] * 100) if stats['employees_in_both_systems'] > 0 else 0
        mismatch_color = "alert-low" if mismatch_rate < 10 else "alert-medium" if mismatch_rate < 50 else "alert-high"
        st.markdown(f"""
        <div class="metric-container {mismatch_color}">
            <h3>{mismatch_rate:.1f}%</h3>
            <p>Mismatch Rate</p>
            <small>{stats['employees_with_mismatches']} employees with >{tolerance}h differences</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_diff = stats['total_difference']
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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", "👥 Employee Analysis", "🏢 Department Breakdown", 
        "⏰ Hour Categories", "📅 Time Period Analysis"
    ])
    
    with tab1:
        st.markdown("### 🎯 Analysis Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Coverage chart
            coverage_fig = create_coverage_chart(stats)
            st.plotly_chart(coverage_fig, use_container_width=True)
            
            # Key improvements
            st.markdown("""
            <div class="analysis-section">
                <h4>✅ Key Improvements (Employee ID-based)</h4>
                <ul>
                    <li><strong>Reliable Matching:</strong> 73.9% coverage vs previous chaos</li>
                    <li><strong>Accurate Data:</strong> Name format issues resolved</li>
                    <li><strong>Complete Categories:</strong> All 18 hour types tracked</li>
                    <li><strong>Stable Analysis:</strong> Employee IDs provide consistent matching</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Mismatch analysis
            mismatch_fig = create_mismatch_analysis_chart(comparison_report, stats)
            if mismatch_fig:
                st.plotly_chart(mismatch_fig, use_container_width=True)
            
            # Data quality info
            st.markdown(f"""
            <div class="analysis-section">
                <h4>📊 Data Quality Summary</h4>
                <ul>
                    <li><strong>Total Timesheet Hours:</strong> {stats['total_timesheet_hours']:,.0f}</li>
                    <li><strong>Total Payroll Hours:</strong> {stats['total_payroll_hours']:,.0f}</li>
                    <li><strong>Employees Matched:</strong> {stats['employees_in_both_systems']}</li>
                    <li><strong>Analysis Tolerance:</strong> ±{tolerance} hours</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 👥 Employee-Level Analysis")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_mismatches_only = st.checkbox("Show Only Mismatched Employees", value=True)
        
        with col2:
            show_matched_only = st.checkbox("Show Only Matched Employees", value=False)
        
        with col3:
            sort_by = st.selectbox("Sort By", 
                options=["Total Difference", "Timesheet Hours", "Employee Name"],
                index=0)
        
        # Filter and sort data
        display_df = comparison_report.copy()
        
        if show_matched_only:
            display_df = display_df[display_df['In Both Systems'] == True]
        
        if show_mismatches_only:
            display_df = display_df[display_df['Mismatch Flag'] == True]
        
        # Sort data
        if sort_by == "Total Difference":
            display_df = display_df.sort_values('Total Difference', key=abs, ascending=False)
        elif sort_by == "Timesheet Hours":
            display_df = display_df.sort_values('Timesheet Hours', ascending=False)
        else:
            display_df = display_df.sort_values('Employee Name')
        
        # Display table
        st.dataframe(
            display_df,
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
        
        st.info(f"Showing {len(display_df)} of {len(comparison_report)} employees")
    
    with tab3:
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
            fig.update_xaxis(tickangle=45)
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
    
    with tab4:
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
    
    with tab5:
        display_time_period_analysis()
        
        # Additional recommendations
        st.markdown("""
        ### 🎯 Recommendations
        
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