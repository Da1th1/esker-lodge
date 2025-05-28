# 🏥 Esker Lodge Nursing Home - Timesheet vs Payroll Dashboard

Interactive Streamlit dashboard for analyzing discrepancies between timesheet and payroll data.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Dashboard
```bash
python launch_dashboard.py
```

Or directly:
```bash
streamlit run streamlit_dashboard.py --server.port 8501
```

### 3. Access Dashboard
Open your browser to: http://localhost:8501

## 📁 Project Structure

```
esker lodge/
├── streamlit_dashboard.py          # Main dashboard application
├── launch_dashboard.py             # Easy launcher script
├── timesheet_payroll_comparison.py # Data processing script
├── requirements.txt                # Python dependencies
├── DASHBOARD_README.md             # Detailed dashboard documentation
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
│
├── Data Files:
├── master_timesheets_20250524_132012.csv    # Source timesheet data
├── master_timesheets_20250524_132012.xlsx   # Source timesheet data (Excel)
├── 1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx  # Source payroll data
├── esker_lodge_hours_comparison_*.xlsx      # Generated comparison results
│
└── Audit Files:
    ├── AuditRecords.xlsx
    ├── AuditRecords_01-24.xlsx
    ├── AuditRecords_2-24.xlsx
    └── RosterBrowser.xlsx
```

## 🎯 Features

- **Interactive Analysis**: 7 different analysis views
- **Real-time Filtering**: Search employees and filter by department
- **Visual Analytics**: Charts, graphs, and correlation analysis
- **Data Export**: Download filtered results as CSV
- **Responsive Design**: Works on desktop and mobile

## 📊 Dashboard Views

1. **Overview** - Executive summary and key metrics
2. **Department Analysis** - Department-level breakdowns
3. **Employee Analysis** - Individual discrepancies
4. **Data Quality** - Missing data analysis
5. **Correlation Analysis** - Visual correlation between systems
6. **Employee Search** - Search and filter functionality
7. **Recommendations** - Actionable insights

## 🔧 Data Processing

To regenerate comparison data:
```bash
python timesheet_payroll_comparison.py
```

This will create a new `esker_lodge_hours_comparison_*.xlsx` file with updated analysis.

## 📋 Key Metrics

- **Mismatch Rate**: Percentage of employees with >2 hour discrepancies
- **Data Coverage**: Employees present in both systems
- **Hours Difference**: Net difference (Payroll - Timesheet)

## 🚨 Troubleshooting

### Dashboard won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that comparison data exists (run the comparison script first)

### No data showing
- Run `python timesheet_payroll_comparison.py` to generate comparison data
- Refresh the dashboard page

### Performance issues
- Install watchdog for better performance: `pip install watchdog`

## 📞 Support

For issues or questions:
1. Check the detailed documentation in `DASHBOARD_README.md`
2. Ensure all required files are present
3. Verify Python dependencies are installed

---

**Last Updated**: May 28, 2025  
**Version**: 1.0  
**Dashboard URL**: http://localhost:8501 