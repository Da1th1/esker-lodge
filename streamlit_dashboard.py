#!/usr/bin/env python3
"""
Streamlit Dashboard for Esker Lodge Nursing Home - Timesheet vs Payroll Hours Comparison
========================================================================================

Interactive dashboard to explore discrepancies between timesheet and payroll data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import glob
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Esker Lodge - Hours Comparison Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_comparison_data():
    """Load the most recent comparison file."""
    try:
        files = glob.glob("esker_lodge_hours_comparison_*.xlsx")
        if not files:
            # Check if we're in a deployment environment and create sample data
            return create_sample_data()
        
        latest_file = max(files)
        
        # Load all sheets
        sheets = {}
        with pd.ExcelFile(latest_file) as xls:
            for sheet_name in xls.sheet_names:
                sheets[sheet_name] = pd.read_excel(xls, sheet_name=sheet_name)
        
        return sheets, latest_file
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return create_sample_data()

def create_sample_data():
    """Create sample data for demonstration purposes."""
    # Create sample comparison data
    np.random.seed(42)  # For reproducible results
    
    departments = ['HCA', 'Nurse', 'Housekeeping', 'Kitchen', 'Maintenance', 'Administration']
    names = [
        'John Smith', 'Mary Johnson', 'David Brown', 'Sarah Wilson', 'Michael Davis',
        'Lisa Anderson', 'Robert Taylor', 'Jennifer White', 'William Jones', 'Patricia Miller',
        'James Garcia', 'Linda Martinez', 'Richard Rodriguez', 'Barbara Lewis', 'Joseph Lee',
        'Susan Walker', 'Thomas Hall', 'Nancy Allen', 'Christopher Young', 'Betty King'
    ]
    
    n_employees = len(names)
    
    # Generate sample data
    comparison_data = []
    for i, name in enumerate(names):
        dept = np.random.choice(departments)
        timesheet_hours = np.random.normal(160, 20)  # Average 160 hours with variation
        
        # Add some realistic discrepancies
        if np.random.random() < 0.3:  # 30% chance of significant discrepancy
            payroll_hours = timesheet_hours + np.random.normal(0, 15)
        else:
            payroll_hours = timesheet_hours + np.random.normal(0, 3)
        
        # Ensure non-negative hours
        timesheet_hours = max(0, timesheet_hours)
        payroll_hours = max(0, payroll_hours)
        
        difference = payroll_hours - timesheet_hours
        mismatch_flag = 1 if abs(difference) > 2 else 0
        
        comparison_data.append({
            'Employee Name': name,
            'Department': dept,
            'Timesheet Hours': round(timesheet_hours, 2),
            'Payroll Hours': round(payroll_hours, 2),
            'Difference': round(difference, 2),
            'Mismatch Flag': mismatch_flag
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Create anomalies (employees with mismatches)
    anomalies_df = comparison_df[comparison_df['Mismatch Flag'] == 1].copy()
    
    # Create department summary
    dept_summary = comparison_df.groupby('Department').agg({
        'Employee Name': 'count',
        'Timesheet Hours': 'sum',
        'Payroll Hours': 'sum',
        'Difference': 'sum',
        'Mismatch Flag': 'sum'
    }).reset_index()
    
    sheets = {
        'Hours Comparison': comparison_df,
        'Anomalies': anomalies_df,
        'Department Summary': dept_summary
    }
    
    return sheets, "Sample Data (Demo Mode)"

def create_overview_metrics(comparison_df, anomalies_df):
    """Create overview metrics cards."""
    total_employees = len(comparison_df)
    employees_with_mismatches = len(anomalies_df)
    mismatch_rate = (employees_with_mismatches / total_employees * 100) if total_employees > 0 else 0
    
    total_timesheet_hours = comparison_df['Timesheet Hours'].sum()
    total_payroll_hours = comparison_df['Payroll Hours'].sum()
    total_difference = comparison_df['Difference'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Employees",
            value=f"{total_employees:,}",
            help="Total unique employees in the analysis"
        )
    
    with col2:
        st.metric(
            label="Mismatch Rate",
            value=f"{mismatch_rate:.1f}%",
            delta=f"{employees_with_mismatches} employees",
            delta_color="inverse",
            help="Percentage of employees with discrepancies > 2 hours"
        )
    
    with col3:
        st.metric(
            label="Total Hours Difference",
            value=f"{total_difference:+,.0f}",
            help="Net difference between payroll and timesheet hours"
        )
    
    with col4:
        coverage_rate = len(comparison_df[(comparison_df['Timesheet Hours'] > 0) & 
                                        (comparison_df['Payroll Hours'] > 0)]) / total_employees * 100
        st.metric(
            label="Data Coverage",
            value=f"{coverage_rate:.1f}%",
            help="Percentage of employees present in both systems"
        )

def create_department_analysis(comparison_df, anomalies_df):
    """Create department-level analysis."""
    st.subheader("📊 Department Analysis")
    
    # Department summary
    dept_summary = comparison_df.groupby('Department').agg({
        'Employee Name': 'count',
        'Timesheet Hours': 'sum',
        'Payroll Hours': 'sum',
        'Difference': 'sum',
        'Mismatch Flag': 'sum'
    }).reset_index()
    dept_summary.columns = ['Department', 'Employee Count', 'Total Timesheet Hours', 
                           'Total Payroll Hours', 'Total Difference', 'Employees with Mismatches']
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Mismatch rate by department
        dept_summary['Mismatch Rate'] = (dept_summary['Employees with Mismatches'] / 
                                       dept_summary['Employee Count'] * 100)
        
        fig_mismatch = px.bar(
            dept_summary.sort_values('Mismatch Rate', ascending=True),
            x='Mismatch Rate',
            y='Department',
            orientation='h',
            title="Mismatch Rate by Department (%)",
            color='Mismatch Rate',
            color_continuous_scale='Reds'
        )
        fig_mismatch.update_layout(height=500)
        st.plotly_chart(fig_mismatch, use_container_width=True)
    
    with col2:
        # Hours difference by department
        fig_diff = px.bar(
            dept_summary.sort_values('Total Difference'),
            x='Total Difference',
            y='Department',
            orientation='h',
            title="Total Hours Difference by Department",
            color='Total Difference',
            color_continuous_scale='RdBu_r'
        )
        fig_diff.update_layout(height=500)
        st.plotly_chart(fig_diff, use_container_width=True)
    
    # Department summary table
    st.subheader("Department Summary Table")
    st.dataframe(
        dept_summary.sort_values('Employees with Mismatches', ascending=False),
        use_container_width=True
    )

def create_employee_analysis(comparison_df, anomalies_df):
    """Create employee-level analysis."""
    st.subheader("👥 Employee Analysis")
    
    # Top discrepancies
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Largest Negative Discrepancies")
        st.caption("Timesheet hours > Payroll hours")
        negative_discrepancies = anomalies_df[anomalies_df['Difference'] < 0].head(10)
        if not negative_discrepancies.empty:
            st.dataframe(
                negative_discrepancies[['Employee Name', 'Department', 'Timesheet Hours', 
                                      'Payroll Hours', 'Difference']],
                use_container_width=True
            )
        else:
            st.info("No negative discrepancies found")
    
    with col2:
        st.subheader("🔴 Largest Positive Discrepancies")
        st.caption("Payroll hours > Timesheet hours")
        positive_discrepancies = anomalies_df[anomalies_df['Difference'] > 0].head(10)
        if not positive_discrepancies.empty:
            st.dataframe(
                positive_discrepancies[['Employee Name', 'Department', 'Timesheet Hours', 
                                      'Payroll Hours', 'Difference']],
                use_container_width=True
            )
        else:
            st.info("No positive discrepancies found")

def create_data_quality_analysis(comparison_df):
    """Create data quality analysis."""
    st.subheader("🔍 Data Quality Analysis")
    
    # Missing data analysis
    missing_timesheet = comparison_df[comparison_df['Timesheet Hours'] == 0]
    missing_payroll = comparison_df[comparison_df['Payroll Hours'] == 0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Missing from Timesheet",
            value=len(missing_timesheet),
            help="Employees with no timesheet hours recorded"
        )
    
    with col2:
        st.metric(
            label="Missing from Payroll",
            value=len(missing_payroll),
            help="Employees with no payroll hours recorded"
        )
    
    with col3:
        both_systems = len(comparison_df[(comparison_df['Timesheet Hours'] > 0) & 
                                       (comparison_df['Payroll Hours'] > 0)])
        st.metric(
            label="In Both Systems",
            value=both_systems,
            help="Employees present in both timesheet and payroll"
        )
    
    # Show missing data details
    col1, col2 = st.columns(2)
    
    with col1:
        if not missing_timesheet.empty:
            st.subheader("Missing from Timesheet")
            st.dataframe(
                missing_timesheet[['Employee Name', 'Department', 'Payroll Hours']].head(10),
                use_container_width=True
            )
    
    with col2:
        if not missing_payroll.empty:
            st.subheader("Missing from Payroll")
            st.dataframe(
                missing_payroll[['Employee Name', 'Department', 'Timesheet Hours']].head(10),
                use_container_width=True
            )

def create_scatter_plot(comparison_df):
    """Create scatter plot of timesheet vs payroll hours."""
    st.subheader("📈 Timesheet vs Payroll Hours Correlation")
    
    # Filter out zero values for better visualization
    filtered_df = comparison_df[(comparison_df['Timesheet Hours'] > 0) & 
                               (comparison_df['Payroll Hours'] > 0)].copy()
    
    if not filtered_df.empty:
        # Use absolute value of difference for size (Plotly requires non-negative values)
        filtered_df['Abs_Difference'] = filtered_df['Difference'].abs()
        
        fig = px.scatter(
            filtered_df,
            x='Timesheet Hours',
            y='Payroll Hours',
            color='Department',
            size='Abs_Difference',
            hover_data=['Employee Name', 'Difference'],
            title="Timesheet Hours vs Payroll Hours by Department",
            labels={
                'Timesheet Hours': 'Timesheet Hours',
                'Payroll Hours': 'Payroll Hours',
                'Abs_Difference': 'Absolute Difference'
            }
        )
        
        # Add perfect correlation line
        max_hours = max(filtered_df['Timesheet Hours'].max(), filtered_df['Payroll Hours'].max())
        fig.add_trace(
            go.Scatter(
                x=[0, max_hours],
                y=[0, max_hours],
                mode='lines',
                name='Perfect Match',
                line=dict(dash='dash', color='red')
            )
        )
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.info("💡 **Chart Info:** Point size represents the absolute difference between timesheet and payroll hours. Hover over points to see employee details and actual difference values.")
    else:
        st.warning("No data available for correlation analysis")

def create_distribution_analysis(comparison_df):
    """Create distribution analysis of differences."""
    st.subheader("📊 Distribution of Hour Differences")
    
    # Filter out extreme outliers for better visualization
    differences = comparison_df['Difference']
    q1, q3 = differences.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    filtered_differences = differences[(differences >= lower_bound) & (differences <= upper_bound)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram of differences
        fig_hist = px.histogram(
            x=filtered_differences,
            nbins=30,
            title="Distribution of Hour Differences",
            labels={'x': 'Hour Difference (Payroll - Timesheet)', 'y': 'Count'}
        )
        fig_hist.add_vline(x=0, line_dash="dash", line_color="red", 
                          annotation_text="Perfect Match")
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Box plot by department
        fig_box = px.box(
            comparison_df,
            x='Department',
            y='Difference',
            title="Hour Differences by Department"
        )
        fig_box.update_xaxes(tickangle=45)
        fig_box.update_layout(height=400)
        st.plotly_chart(fig_box, use_container_width=True)

def create_detailed_search(comparison_df):
    """Create detailed employee search functionality."""
    st.subheader("🔍 Employee Search & Details")
    
    # Search functionality
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            "Search for employee by name:",
            placeholder="Enter employee name..."
        )
    
    with col2:
        department_filter = st.selectbox(
            "Filter by department:",
            options=['All'] + sorted(comparison_df['Department'].dropna().unique().tolist())
        )
    
    # Apply filters
    filtered_df = comparison_df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Employee Name'].str.contains(search_term, case=False, na=False)
        ]
    
    if department_filter != 'All':
        filtered_df = filtered_df[filtered_df['Department'] == department_filter]
    
    # Display results
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[['Employee Name', 'Department', 'Timesheet Hours', 
                        'Payroll Hours', 'Difference', 'Mismatch Flag']],
            use_container_width=True
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name=f"esker_lodge_filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No employees found matching the search criteria.")

def create_recommendations():
    """Create recommendations section."""
    st.subheader("💡 Recommendations")
    
    st.markdown("""
    ### 🔴 High Priority Actions
    - **Review data collection processes** - The high mismatch rate indicates systemic issues
    - **Verify timesheet and payroll system integration** - Ensure data flows correctly between systems
    - **Investigate missing employees** - Focus on employees present in only one system
    
    ### 📋 Data Reconciliation
    - **Weekly reconciliation checks** - Implement regular comparison processes
    - **Automated alerts** - Set up notifications for discrepancies > 2 hours
    - **Staff training** - Ensure proper timesheet completion procedures
    
    ### 🎯 Department Focus
    - **HCA Department** - Highest number of discrepancies, needs immediate attention
    - **Nursing Department** - Second highest, review scheduling processes
    - **Housekeeping** - Check for proper hour recording procedures
    
    ### 🔧 Process Improvements
    - **Approval workflows** - Review and streamline approval processes
    - **Real-time validation** - Implement checks during timesheet entry
    - **Regular audits** - Schedule monthly data quality reviews
    """)

def main():
    """Main dashboard function."""
    st.title("🏥 Esker Lodge Nursing Home")
    st.title("Timesheet vs Payroll Hours Comparison Dashboard")
    
    # Load data
    with st.spinner("Loading comparison data..."):
        sheets, filename = load_comparison_data()
    
    # Check if we're using sample data
    if filename == "Sample Data (Demo Mode)":
        st.warning("⚠️ **Demo Mode**: Using sample data for demonstration. Upload your actual data files to see real analysis.")
    
    # Extract data
    comparison_df = sheets['Hours Comparison']
    anomalies_df = sheets['Anomalies']
    dept_summary = sheets['Department Summary']
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Navigation")
    st.sidebar.info(f"**Data Source:** {filename}")
    st.sidebar.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Add instructions for real data in sidebar if using sample data
    if filename == "Sample Data (Demo Mode)":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📁 To Use Real Data:")
        st.sidebar.markdown("1. Run `python timesheet_payroll_comparison.py`")
        st.sidebar.markdown("2. Upload the generated Excel file")
        st.sidebar.markdown("3. Refresh the dashboard")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Analysis View:",
        ["Overview", "Department Analysis", "Employee Analysis", "Data Quality", 
         "Correlation Analysis", "Employee Search", "Recommendations"]
    )
    
    # Overview metrics (always shown)
    create_overview_metrics(comparison_df, anomalies_df)
    st.divider()
    
    # Page content based on selection
    if page == "Overview":
        st.subheader("📋 Executive Summary")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
            **Key Findings:**
            - {len(comparison_df)} total employees analyzed
            - {len(anomalies_df)} employees with significant discrepancies (>{2} hours)
            - {len(comparison_df[comparison_df['Timesheet Hours'] == 0])} employees missing from timesheet
            - {len(comparison_df[comparison_df['Payroll Hours'] == 0])} employees missing from payroll
            """)
        
        with col2:
            total_diff = comparison_df['Difference'].sum()
            if total_diff > 0:
                st.warning(f"**Net Difference:** +{total_diff:,.0f} hours (Payroll > Timesheet)")
            else:
                st.warning(f"**Net Difference:** {total_diff:,.0f} hours (Timesheet > Payroll)")
        
        # Quick charts
        create_distribution_analysis(comparison_df)
        
    elif page == "Department Analysis":
        create_department_analysis(comparison_df, anomalies_df)
        
    elif page == "Employee Analysis":
        create_employee_analysis(comparison_df, anomalies_df)
        
    elif page == "Data Quality":
        create_data_quality_analysis(comparison_df)
        
    elif page == "Correlation Analysis":
        create_scatter_plot(comparison_df)
        create_distribution_analysis(comparison_df)
        
    elif page == "Employee Search":
        create_detailed_search(comparison_df)
        
    elif page == "Recommendations":
        create_recommendations()
    
    # Footer
    st.divider()
    st.caption(f"Dashboard generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
              f"Data from {filename}")

if __name__ == "__main__":
    main() 