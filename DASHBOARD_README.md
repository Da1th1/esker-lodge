# 🏥 Esker Lodge Nursing Home - Timesheet vs Payroll Dashboard

An interactive Streamlit dashboard for analyzing discrepancies between timesheet and payroll data.

## 🚀 Quick Start

### Option 1: Using the Launcher Script
```bash
python launch_dashboard.py
```

### Option 2: Direct Streamlit Command
```bash
streamlit run streamlit_dashboard.py --server.port 8501
```

### Option 3: Generate Data First (if needed)
```bash
# Generate comparison data
python timesheet_payroll_comparison.py

# Then launch dashboard
streamlit run streamlit_dashboard.py
```

## 📊 Dashboard Features

### 🏠 Overview Page
- **Executive Summary**: Key metrics and findings at a glance
- **Distribution Analysis**: Visual representation of hour differences
- **Quick Statistics**: Total employees, mismatch rates, coverage metrics

### 🏢 Department Analysis
- **Mismatch Rate by Department**: Horizontal bar chart showing which departments have the most discrepancies
- **Hours Difference by Department**: Visual comparison of total hour differences
- **Department Summary Table**: Detailed breakdown with employee counts and totals

### 👥 Employee Analysis
- **Largest Discrepancies**: Split view showing:
  - Negative discrepancies (Timesheet > Payroll)
  - Positive discrepancies (Payroll > Timesheet)
- **Top 10 Lists**: Most significant discrepancies for immediate attention

### 🔍 Data Quality Analysis
- **Missing Data Metrics**: Employees missing from each system
- **Coverage Analysis**: Employees present in both systems
- **Data Completeness**: Visual indicators of data quality issues

### 📈 Correlation Analysis
- **Scatter Plot**: Timesheet vs Payroll hours with perfect match line
- **Department Color Coding**: Visual identification of department patterns
- **Interactive Hover**: Employee details on hover

### 🔎 Employee Search
- **Name Search**: Find specific employees by name
- **Department Filter**: Filter by department
- **Export Functionality**: Download filtered results as CSV
- **Real-time Filtering**: Instant results as you type

### 💡 Recommendations
- **Priority Actions**: Based on mismatch severity
- **Data Reconciliation**: Specific steps for data cleanup
- **Department Focus**: Targeted recommendations by department
- **Process Improvements**: Long-term solutions

## 📋 Key Metrics Explained

### Mismatch Rate
Percentage of employees with discrepancies greater than 2 hours between timesheet and payroll data.

### Data Coverage
Percentage of employees present in both timesheet and payroll systems.

### Hours Difference
Net difference calculated as: `Payroll Hours - Timesheet Hours`
- **Positive**: Payroll shows more hours than timesheet
- **Negative**: Timesheet shows more hours than payroll

## 🎯 Navigation

Use the sidebar to navigate between different analysis views:

1. **Overview** - Executive summary and key findings
2. **Department Analysis** - Department-level breakdowns
3. **Employee Analysis** - Individual employee discrepancies
4. **Data Quality** - Missing data and coverage analysis
5. **Correlation Analysis** - Visual correlation between systems
6. **Employee Search** - Search and filter functionality
7. **Recommendations** - Actionable insights and next steps

## 📊 Interactive Features

### Filtering and Search
- Search employees by name (partial matches supported)
- Filter by department
- Real-time results

### Data Export
- Download filtered employee data as CSV
- Timestamped filenames for version control

### Visual Interactions
- Hover over charts for detailed information
- Zoom and pan on scatter plots
- Interactive legends on charts

## 🔧 Technical Details

### Data Sources
- **Timesheet Data**: `master_timesheets_20250524_132012.csv`
- **Payroll Data**: `1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx`

### Processing
- Automatic name normalization for matching
- Time format conversion (HH:MM to decimal hours)
- Missing data handling
- Outlier detection for visualizations

### Performance
- Data caching for faster load times
- Optimized visualizations for large datasets
- Responsive design for different screen sizes

## 🚨 Alerts and Warnings

The dashboard will show:
- **Red alerts** for high mismatch rates (>50%)
- **Yellow warnings** for medium mismatch rates (20-50%)
- **Green indicators** for acceptable rates (<20%)

## 📱 Browser Compatibility

Tested and optimized for:
- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🔄 Data Refresh

To refresh data:
1. Run the analysis script: `python timesheet_payroll_comparison.py`
2. Refresh the dashboard browser page
3. New data will be automatically loaded

## 📞 Support

For technical issues or questions about the analysis:
1. Check the console output for error messages
2. Ensure all required packages are installed: `pip install -r requirements.txt`
3. Verify data files are present in the project directory

## 🎨 Customization

The dashboard can be customized by modifying:
- **Colors**: Update the color schemes in the Plotly charts
- **Thresholds**: Adjust the 2-hour tolerance in the analysis
- **Metrics**: Add new calculated fields or visualizations
- **Layout**: Modify the Streamlit layout and components

---

**Last Updated**: May 28, 2025  
**Version**: 1.0  
**Author**: AI Assistant 