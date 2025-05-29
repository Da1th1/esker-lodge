#!/usr/bin/env python3
"""
Streamlit Dashboard for Esker Lodge Nursing Home - Detailed Timesheet vs Payroll Hours Comparison
================================================================================================

Interactive dashboard to explore discrepancies between timesheet and payroll data with detailed hour category breakdown.
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
    page_title="Esker Lodge - Detailed Hours Comparison Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define hour categories for consistent use
HOUR_CATEGORIES = [
    'Day Rate', 'Night Rate', 'Sat Day', 'Sat Night', 'Sun Day', 'Sun Night',
    'Old Day/Sat Rate', 'Old Night Rate', 'Old Sun Rate', 'Extra Shift Bonus',
    'Backpay', 'Bank Holiday', 'Holiday Pay', 'Cross Function Day1', 
    'Cross Function Day2', 'Cross Function Sun1', 'Training/Meeting', 'Statutory Sick Pay'
]

@st.cache_data
def load_comparison_data():
    """Load the most recent detailed comparison file."""
    try:
        # Look for detailed comparison files first
        files = glob.glob("esker_lodge_detailed_comparison_*.xlsx")
        if not files:
            # Fallback to regular comparison files
            files = glob.glob("esker_lodge_hours_comparison_*.xlsx")
        
        if not files:
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
    """Create sample data with detailed hour categories for demonstration."""
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
    
    # Generate sample data with hour categories
    comparison_data = []
    for i, name in enumerate(names):
        dept = np.random.choice(departments)
        timesheet_hours = np.random.normal(160, 20)  # Average 160 hours with variation
        
        # Generate sample hours for each category
        category_hours = {}
        remaining_hours = max(0, timesheet_hours + np.random.normal(0, 10))
        
        for category in HOUR_CATEGORIES:
            if remaining_hours > 0:
                # Assign hours based on category likelihood
                if category == 'Day Rate':
                    hours = np.random.uniform(0, min(remaining_hours * 0.7, 120))
                elif category in ['Night Rate', 'Sat Day', 'Sun Day']:
                    hours = np.random.uniform(0, min(remaining_hours * 0.3, 40))
                elif category in ['Training/Meeting', 'Holiday Pay']:
                    hours = np.random.uniform(0, min(remaining_hours * 0.1, 8))
                else:
                    hours = np.random.uniform(0, min(remaining_hours * 0.2, 20))
                
                hours = max(0, hours)
                category_hours[category] = round(hours, 2)
                remaining_hours = max(0, remaining_hours - hours)
            else:
                category_hours[category] = 0.0
        
        payroll_total = sum(category_hours.values())
        timesheet_hours = max(0, timesheet_hours)
        
        difference = payroll_total - timesheet_hours
        mismatch_flag = 1 if abs(difference) > 2 else 0
        
        # Create comparison row
        row = {
            'Employee Name': name,
            'Department': dept,
            'Timesheet Hours': round(timesheet_hours, 2),
            'Payroll Hours Total': round(payroll_total, 2),
            'Total Difference': round(difference, 2),
            'Mismatch Flag': mismatch_flag
        }
        
        # Add category hours
        row.update(category_hours)
        
        comparison_data.append(row)
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Create anomalies (employees with mismatches)
    anomalies_df = comparison_df[comparison_df['Mismatch Flag'] == 1].copy()
    
    # Create department summary
    dept_summary = comparison_df.groupby('Department').agg({
        'Employee Name': 'count',
        'Timesheet Hours': 'sum',
        'Payroll Hours Total': 'sum',
        'Total Difference': 'sum',
        'Mismatch Flag': 'sum'
    }).reset_index()
    
    # Create category breakdown
    category_breakdown = []
    for _, row in comparison_df.iterrows():
        for category in HOUR_CATEGORIES:
            if category in row.index and row[category] > 0:
                category_breakdown.append({
                    'Employee Name': row['Employee Name'],
                    'Department': row['Department'],
                    'Hour Category': category,
                    'Hours': row[category],
                    'Timesheet Hours': row['Timesheet Hours']
                })
    
    category_breakdown_df = pd.DataFrame(category_breakdown)
    
    sheets = {
        'Detailed Hours Comparison': comparison_df,
        'Anomalies': anomalies_df,
        'Department Summary': dept_summary,
        'Hour Category Breakdown': category_breakdown_df
    }
    
    return sheets, "Sample Data (Demo Mode)"

def create_overview_metrics(comparison_df, anomalies_df):
    """Create overview metrics cards."""
    total_employees = len(comparison_df)
    employees_with_mismatches = len(anomalies_df)
    mismatch_rate = (employees_with_mismatches / total_employees * 100) if total_employees > 0 else 0
    
    total_timesheet_hours = comparison_df['Timesheet Hours'].sum()
    total_payroll_hours = comparison_df['Payroll Hours Total'].sum()
    total_difference = comparison_df['Total Difference'].sum()
    
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
                                        (comparison_df['Payroll Hours Total'] > 0)]) / total_employees * 100
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
        'Payroll Hours Total': 'sum',
        'Total Difference': 'sum',
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
        negative_discrepancies = anomalies_df[anomalies_df['Total Difference'] < 0].head(10)
        if not negative_discrepancies.empty:
            st.dataframe(
                negative_discrepancies[['Employee Name', 'Department', 'Timesheet Hours', 
                                      'Payroll Hours Total', 'Total Difference']],
                use_container_width=True
            )
        else:
            st.info("No negative discrepancies found")
    
    with col2:
        st.subheader("🔴 Largest Positive Discrepancies")
        st.caption("Payroll hours > Timesheet hours")
        positive_discrepancies = anomalies_df[anomalies_df['Total Difference'] > 0].head(10)
        if not positive_discrepancies.empty:
            st.dataframe(
                positive_discrepancies[['Employee Name', 'Department', 'Timesheet Hours', 
                                      'Payroll Hours Total', 'Total Difference']],
                use_container_width=True
            )
        else:
            st.info("No positive discrepancies found")

def create_data_quality_analysis(comparison_df):
    """Create data quality analysis."""
    st.subheader("🔍 Data Quality Analysis")
    
    # Missing data analysis
    missing_timesheet = comparison_df[comparison_df['Timesheet Hours'] == 0]
    missing_payroll = comparison_df[comparison_df['Payroll Hours Total'] == 0]
    
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
                                       (comparison_df['Payroll Hours Total'] > 0)])
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
                missing_timesheet[['Employee Name', 'Department', 'Payroll Hours Total']].head(10),
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
                               (comparison_df['Payroll Hours Total'] > 0)].copy()
    
    if not filtered_df.empty:
        # Use absolute value of difference for size (Plotly requires non-negative values)
        filtered_df['Abs_Difference'] = filtered_df['Total Difference'].abs()
        
        fig = px.scatter(
            filtered_df,
            x='Timesheet Hours',
            y='Payroll Hours Total',
            color='Department',
            size='Abs_Difference',
            hover_data=['Employee Name', 'Total Difference'],
            title="Timesheet Hours vs Payroll Hours by Department",
            labels={
                'Timesheet Hours': 'Timesheet Hours',
                'Payroll Hours Total': 'Payroll Hours Total',
                'Abs_Difference': 'Absolute Difference'
            }
        )
        
        # Add perfect correlation line
        max_hours = max(filtered_df['Timesheet Hours'].max(), filtered_df['Payroll Hours Total'].max())
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
    differences = comparison_df['Total Difference']
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
            y='Total Difference',
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
                        'Payroll Hours Total', 'Total Difference', 'Mismatch Flag']],
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

def create_hour_category_analysis(comparison_df, category_breakdown_df):
    """Create detailed hour category analysis."""
    st.subheader("🕒 Hour Category Breakdown Analysis")
    
    # Check if we have category data
    category_columns = [col for col in HOUR_CATEGORIES if col in comparison_df.columns]
    
    if not category_columns:
        st.warning("No detailed hour category data available. Using sample data.")
        return
    
    # Category totals
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Total Hours by Category")
        category_totals = {}
        for category in category_columns:
            total = comparison_df[category].sum()
            if total > 0:
                category_totals[category] = total
        
        if category_totals:
            # Sort by total hours
            sorted_categories = dict(sorted(category_totals.items(), key=lambda x: x[1], reverse=True))
            
            fig_category = px.bar(
                x=list(sorted_categories.values()),
                y=list(sorted_categories.keys()),
                orientation='h',
                title="Total Hours by Category",
                labels={'x': 'Total Hours', 'y': 'Hour Category'},
                color=list(sorted_categories.values()),
                color_continuous_scale='viridis'
            )
            fig_category.update_layout(height=600)
            st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.subheader("Category Distribution")
        if category_totals:
            fig_pie = px.pie(
                values=list(category_totals.values()),
                names=list(category_totals.keys()),
                title="Distribution of Hours by Category"
            )
            fig_pie.update_layout(height=600)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Department vs Category heatmap
    st.subheader("🔥 Hours by Department and Category (Heatmap)")
    
    # Create department-category matrix
    dept_category_matrix = []
    for dept in comparison_df['Department'].unique():
        if pd.isna(dept):
            continue
        dept_data = comparison_df[comparison_df['Department'] == dept]
        row = {'Department': dept}
        
        for category in category_columns:
            row[category] = dept_data[category].sum()
        
        dept_category_matrix.append(row)
    
    if dept_category_matrix:
        matrix_df = pd.DataFrame(dept_category_matrix)
        matrix_df = matrix_df.set_index('Department')
        
        # Only show categories with significant hours
        matrix_df = matrix_df.loc[:, (matrix_df.sum() > 10)]
        
        if not matrix_df.empty:
            fig_heatmap = px.imshow(
                matrix_df.values,
                x=matrix_df.columns,
                y=matrix_df.index,
                aspect='auto',
                title="Hours by Department and Category",
                labels={'x': 'Hour Category', 'y': 'Department', 'color': 'Total Hours'},
                color_continuous_scale='viridis'
            )
            fig_heatmap.update_layout(height=500)
            st.plotly_chart(fig_heatmap, use_container_width=True)

def create_category_difference_analysis(comparison_df):
    """Create analysis of differences by category (if timesheet has category data)."""
    st.subheader("📊 Category-Level Discrepancy Analysis")
    
    # Check if we have category data
    category_columns = [col for col in HOUR_CATEGORIES if col in comparison_df.columns]
    
    if not category_columns:
        st.info("💡 **Note**: This analysis shows payroll hour categories. Timesheet data is aggregated, so we cannot compare differences by specific hour types.")
        return
    
    st.info("💡 **Analysis**: Since timesheet data is aggregated and payroll data is categorized, this shows the distribution of payroll hours by category for employees with discrepancies.")
    
    # Focus on employees with mismatches
    mismatched_employees = comparison_df[comparison_df['Mismatch Flag'] == True]
    
    if mismatched_employees.empty:
        st.info("No employees with significant discrepancies found.")
        return
    
    # Show category breakdown for mismatched employees
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Categories for Employees with Discrepancies")
        
        category_sums = {}
        for category in category_columns:
            total = mismatched_employees[category].sum()
            if total > 0:
                category_sums[category] = total
        
        if category_sums:
            sorted_categories = dict(sorted(category_sums.items(), key=lambda x: x[1], reverse=True))
            
            fig = px.bar(
                x=list(sorted_categories.keys()),
                y=list(sorted_categories.values()),
                title="Payroll Hours by Category (Mismatched Employees)",
                labels={'x': 'Hour Category', 'y': 'Total Hours'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Average Hours per Employee")
        
        avg_category_hours = {}
        num_mismatched = len(mismatched_employees)
        
        for category in category_columns:
            total = mismatched_employees[category].sum()
            if total > 0:
                avg_category_hours[category] = total / num_mismatched
        
        if avg_category_hours:
            sorted_avg = dict(sorted(avg_category_hours.items(), key=lambda x: x[1], reverse=True))
            
            fig = px.bar(
                x=list(sorted_avg.keys()),
                y=list(sorted_avg.values()),
                title="Average Hours per Employee by Category",
                labels={'x': 'Hour Category', 'y': 'Average Hours'}
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

def create_top_category_employees(comparison_df):
    """Show top employees by hour category."""
    st.subheader("👥 Top Employees by Hour Category")
    
    category_columns = [col for col in HOUR_CATEGORIES if col in comparison_df.columns]
    
    if not category_columns:
        st.warning("No detailed hour category data available.")
        return
    
    # Select category to analyze
    selected_category = st.selectbox(
        "Select hour category to analyze:",
        options=category_columns,
        index=0 if category_columns else 0
    )
    
    if selected_category:
        # Get top employees for this category
        category_data = comparison_df[comparison_df[selected_category] > 0].copy()
        category_data = category_data.sort_values(selected_category, ascending=False).head(20)
        
        if not category_data.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart of top employees
                fig = px.bar(
                    category_data.head(10),
                    x='Employee Name',
                    y=selected_category,
                    color='Department',
                    title=f"Top 10 Employees - {selected_category} Hours",
                    labels={'y': f'{selected_category} Hours'}
                )
                fig.update_xaxes(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Summary statistics
                st.metric(
                    f"Total {selected_category} Hours",
                    f"{comparison_df[selected_category].sum():,.1f}"
                )
                st.metric(
                    f"Employees with {selected_category}",
                    f"{len(comparison_df[comparison_df[selected_category] > 0])}"
                )
                st.metric(
                    f"Average {selected_category} Hours",
                    f"{comparison_df[selected_category].mean():.1f}"
                )
            
            # Detailed table
            st.subheader(f"Detailed {selected_category} Data")
            display_columns = ['Employee Name', 'Department', selected_category, 'Timesheet Hours', 'Total Difference']
            available_columns = [col for col in display_columns if col in category_data.columns]
            
            st.dataframe(
                category_data[available_columns],
                use_container_width=True
            )

def main():
    """Main dashboard function."""
    st.title("🏥 Esker Lodge Nursing Home")
    st.title("Detailed Timesheet vs Payroll Hours Comparison Dashboard")
    
    # Load data
    with st.spinner("Loading comparison data..."):
        sheets, filename = load_comparison_data()
    
    # Check if we're using sample data
    if filename == "Sample Data (Demo Mode)":
        st.warning("⚠️ **Demo Mode**: Using sample data for demonstration. Upload your actual data files to see real analysis.")
    
    # Extract data
    comparison_df = sheets['Detailed Hours Comparison']
    anomalies_df = sheets['Anomalies']
    dept_summary = sheets['Department Summary']
    category_breakdown_df = sheets.get('Hour Category Breakdown', pd.DataFrame())
    
    # Sidebar
    st.sidebar.title("📊 Dashboard Navigation")
    st.sidebar.info(f"**Data Source:** {filename}")
    st.sidebar.info(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Add instructions for real data in sidebar if using sample data
    if filename == "Sample Data (Demo Mode)":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📁 To Use Real Data:")
        st.sidebar.markdown("1. Run `python timesheet_payroll_comparison_detailed.py`")
        st.sidebar.markdown("2. Upload the generated Excel file")
        st.sidebar.markdown("3. Refresh the dashboard")
    
    # Navigation
    page = st.sidebar.selectbox(
        "Select Analysis View:",
        ["Overview", "Hour Category Analysis", "Category Differences", "Top Category Employees", 
         "Department Analysis", "Employee Analysis", "Data Quality", 
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
            - {len(comparison_df[comparison_df['Payroll Hours Total'] == 0])} employees missing from payroll
            """)
        
        with col2:
            total_diff = comparison_df['Total Difference'].sum()
            if total_diff > 0:
                st.warning(f"**Net Difference:** +{total_diff:,.0f} hours (Payroll > Timesheet)")
            else:
                st.warning(f"**Net Difference:** {total_diff:,.0f} hours (Timesheet > Payroll)")
        
        # Quick charts
        create_distribution_analysis(comparison_df)
        
    elif page == "Hour Category Analysis":
        create_hour_category_analysis(comparison_df, category_breakdown_df)
        
    elif page == "Category Differences":
        create_category_difference_analysis(comparison_df)
        
    elif page == "Top Category Employees":
        create_top_category_employees(comparison_df)
        
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