# 🏥 Esker Lodge Nursing Home - Detailed Timesheet vs Payroll Dashboard

Interactive Streamlit dashboard for analyzing discrepancies between timesheet and payroll data with **detailed hour category breakdowns**.

## ✨ New Features

### 🕒 Hour Category Analysis
The dashboard now breaks down payroll differences by specific hour types:
- **Day Rate** - Regular daytime hours
- **Night Rate** - Night shift hours  
- **Weekend Shifts** - Saturday/Sunday day and night
- **Overtime Categories** - Old rates and extra shift bonuses
- **Special Pay** - Training, holiday pay, sick pay, bank holidays
- **Cross Function** - Cross-departmental work hours

### 📊 New Dashboard Views
1. **Hour Category Analysis** - Total hours and distribution by category
2. **Category Differences** - Shows which hour types have the most discrepancies
3. **Top Category Employees** - Identify employees with highest hours in each category
4. **Department Heatmap** - Visual breakdown of hours by department and category

## 🚀 Quick Start

### 1. Generate Detailed Analysis
```bash
# Run the enhanced comparison script
python timesheet_payroll_comparison_detailed.py
```

### 2. Launch Dashboard
```bash
python launch_dashboard.py
```

### 3. Access Dashboard
Open your browser to: http://localhost:8501

## 📁 Project Structure

```
esker lodge/
├── streamlit_dashboard.py                    # Enhanced dashboard with category analysis
├── timesheet_payroll_comparison_detailed.py  # New detailed analysis script
├── timesheet_payroll_comparison.py           # Original comparison script
├── launch_dashboard.py                       # Easy launcher script
├── requirements.txt                          # Python dependencies
├── DASHBOARD_README.md                       # Detailed dashboard documentation
├── DEPLOYMENT.md                             # Streamlit Cloud deployment guide
└── README.md                                 # This file
```

## 📈 Data Sources

### Input Files
- **Timesheet Data**: `master_timesheets_20250524_132012.csv`
- **Payroll Data**: `1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx`

### Generated Analysis Files
- **Detailed Analysis**: `esker_lodge_detailed_comparison_YYYYMMDD_HHMMSS.xlsx`
- **Regular Analysis**: `esker_lodge_hours_comparison_YYYYMMDD_HHMMSS.xlsx`

## 🎯 Key Insights Provided

### Hour Category Breakdown
- **Day Rate**: 21,266 hours (50.9% of total payroll hours)
- **Night Rate**: 4,713 hours (11.3% of total)
- **Weekend Work**: 6,701 hours (Sat/Sun combined)
- **Special Pay**: 2,158 hours (Training, holiday, sick pay)

### Discrepancy Analysis
- **90.4% mismatch rate** between timesheet and payroll
- **-35,790 hour difference** (timesheet higher than payroll)
- **178 employees** with discrepancies >2 hours

### Department Focus Areas
- **HCA Department** - Highest discrepancies in day and night rates
- **Nursing** - Significant weekend and night shift variations
- **Support Departments** - Cross-function and training hour discrepancies

## 🔧 Technical Features

### Enhanced Data Processing
- **Smart Category Mapping** - Automatically maps Excel columns to hour types
- **Robust Error Handling** - Graceful fallback to sample data
- **Time Format Conversion** - Handles HH:MM to decimal conversion
- **Name Normalization** - Consistent employee name matching

### Interactive Visualizations
- **Plotly Charts** - Interactive bar charts, heatmaps, and pie charts
- **Department Filtering** - Focus analysis on specific departments
- **Employee Search** - Find specific employees across all views
- **Category Selection** - Drill down into specific hour types

### Export Capabilities
- **Excel Export** - Multiple sheets with detailed breakdowns
- **CSV Downloads** - Filtered data for further analysis
- **Chart Export** - Save visualizations for reports

## 💡 Use Cases

### Management Review
- Identify departments with highest hour discrepancies
- Understand which shift types have reporting issues
- Track cross-department work allocation

### Payroll Verification
- Verify specific hour categories against timesheets
- Identify employees with unusual hour patterns
- Check compliance with shift differentials

### Operational Insights
- Analyze weekend and night shift coverage
- Track training and development hours
- Monitor holiday and sick pay accuracy

## 🚀 Deployment

### Local Development
```bash
pip install -r requirements.txt
python launch_dashboard.py
```

### Streamlit Cloud
See `DEPLOYMENT.md` for detailed deployment instructions to Streamlit Cloud.

## 📞 Support

For questions or issues:
1. Check the detailed logs in the dashboard
2. Review `DASHBOARD_README.md` for troubleshooting
3. Ensure all data files are in the correct format

---

**Last Updated**: 2025-01-29 | **Version**: 2.0 - Detailed Hour Category Analysis 