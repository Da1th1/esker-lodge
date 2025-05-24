# Esker Lodge Timesheet Analysis System

A comprehensive analysis system for Esker Lodge nursing home timesheet data, providing customer-ready reports and interactive dashboards.

## Overview

This system processes 71+ timesheet Excel files covering 104 staff members across 12 departments over 71 weeks (2024-W01 to 2025-W20), analyzing 77,616 total hours worked with comprehensive anomaly detection and compliance monitoring.

## 🚀 Quick Start

### Easy Launch
```bash
python run_analysis.py
```

This launches an interactive menu with all available options:
1. **📊 Streamlit Dashboard** - Interactive web interface
2. **📄 Customer Report** - Professional PDF report  
3. **🔧 Full Analysis** - Complete Excel analysis
4. **📈 Visualizations** - Chart generation
5. **📝 Text Report** - Comprehensive summary
6. **🧹 Data Explorer** - Quick data preview

### Direct Access
```bash
# Launch interactive dashboard
streamlit run timesheet_dashboard.py

# Generate customer report
python customer_report_generator.py

# Run full analysis
python corrected_timesheet_analysis.py
```

## 📊 Key Features

### 🏥 Customer Report Generator (`customer_report_generator.py`)
- **Professional PDF Report** suitable for client presentation
- **Executive Summary** with key metrics and findings
- **Compliance Analysis** with EU Working Time Directive assessment
- **Visual Charts** embedded in PDF
- **Actionable Recommendations** with priority levels
- **Risk Assessment** categorization

### 📱 Interactive Dashboard (`timesheet_dashboard.py`)
- **Real-time Filtering** by department and time period
- **Executive Metrics** with alert system
- **5 Comprehensive Tabs:**
  - Overview with trends and distributions
  - Department analysis with overtime tracking
  - Staff performance with heatmaps
  - Compliance monitoring with violation tracking
  - Data quality analysis with completeness metrics

### 🔧 Analysis Engine (`corrected_timesheet_analysis.py`)
- **Time Format Conversion** - Handles HH:MM to decimal hours
- **Anomaly Detection** - Excessive hours, missing pay rates, inactive staff
- **Compliance Checking** - EU Working Time Directive monitoring
- **Excel Export** - Detailed analysis files with multiple sheets

## 📈 Key Findings Summary

### 📊 Dataset Overview
- **5,745 total records** across 71 weeks
- **104 unique staff** across 12 departments
- **77,616 total hours** worked (41% of records with hours)
- **Time Period:** 2024-W01 to 2025-W20

### 🏢 Department Breakdown
- **HCA:** 39,829 hours (51.3%)
- **Nurse:** 15,448 hours (19.9%)
- **Catering:** 7,216 hours (9.3%)
- **Housekeeping:** 4,496 hours (5.8%)

### 🚨 Critical Issues Identified
- **HIGH PRIORITY:** 8 excessive hours cases (>60h/week)
- **HIGH PRIORITY:** 69 missing pay rate records with hours
- **MEDIUM PRIORITY:** 217 overtime instances (>48h/week, 9.2% rate)
- **LOW PRIORITY:** 86 inactive staff (5+ zero weeks)

### ⚖️ Compliance Concerns
- **8 records exceed 60h/week** (EU Working Time Directive violations)
- **19 staff with significant night work** (>100h total)
- **9.2% overtime rate** suggests potential understaffing

## 🛠️ Technical Implementation

### Data Processing Pipeline
1. **Source Files:** 71 Excel timesheet files
2. **Time Conversion:** HH:MM format → decimal hours
3. **Data Cleaning:** Standardize departments, handle missing values
4. **Analysis Engine:** Multi-faceted anomaly detection
5. **Output Generation:** PDF, Excel, CSV, PNG formats

### Quality Controls
- **Automated validation** of time format conversion
- **Cross-reference checking** for data consistency
- **Compliance rule engine** for regulation monitoring
- **Data completeness scoring** across all fields

## 📋 Requirements

```bash
pip install -r requirements.txt
```

### Dependencies
- **streamlit>=1.28.0** - Interactive dashboard
- **pandas>=1.5.0** - Data processing
- **plotly>=5.15.0** - Interactive visualizations
- **reportlab>=4.0.0** - PDF generation
- **matplotlib>=3.7.0** - Static charts
- **openpyxl>=3.1.0** - Excel file handling

## 📁 Project Structure

```
esker-lodge/
├── 📊 Analysis Core
│   ├── corrected_timesheet_analysis.py    # Main analysis engine
│   ├── customer_report_generator.py       # PDF report generator
│   └── timesheet_dashboard.py            # Streamlit dashboard
├── 📈 Visualization & Reporting  
│   ├── timesheet_visualizations.py       # Chart generation
│   ├── comprehensive_report.py           # Text summaries
│   └── data_explorer.py                 # Quick data preview
├── 📂 Data Files
│   ├── master_timesheets_20250524_132012.csv  # Combined dataset
│   ├── corrected_timesheet_cleaned_*.csv      # Processed data
│   └── timesheets/                            # Source Excel files (71 files)
├── 🛠️ Utilities
│   ├── run_analysis.py                   # Interactive launcher
│   ├── combine_all_timesheets.py        # Data combination script
│   └── requirements.txt                 # Dependencies
└── 📄 Documentation
    ├── README.md                        # This file
    └── setup.py                        # Package configuration
```

## 📊 Output Files Generated

### Customer Deliverables
- **`Esker_Lodge_Timesheet_Analysis_Report_[timestamp].pdf`** - Professional client report
- **Interactive Dashboard** - Real-time web interface at localhost:8501

### Technical Analysis Files
- **`corrected_timesheet_analysis_[timestamp].xlsx`** - Complete analysis workbook
- **`corrected_timesheet_cleaned_[timestamp].csv`** - Processed dataset
- **Various PNG charts** - Individual visualization files

## 💼 HR Recommendations

### Immediate Actions (High Priority)
1. **Review excessive hours compliance** - 8 cases >60h/week
2. **Fix missing pay rates** - 69 records affecting payroll
3. **Implement overtime controls** - Prevent Working Time Directive violations

### Short-term Improvements (1-4 weeks)
4. **Staffing review** - Address 9.2% overtime rate
5. **Policy updates** - Clear overtime authorization procedures
6. **System improvements** - Automated compliance monitoring

### Long-term Strategy (1-3 months)
7. **Data quality monitoring** - Regular validation checks
8. **Staff wellness programs** - Monitor fatigue indicators
9. **Quarterly reviews** - Ongoing compliance assessment

## 🎯 Business Value

- **Regulatory Compliance** - EU Working Time Directive adherence
- **Cost Management** - Overtime and staffing optimization
- **Risk Mitigation** - Early warning system for violations
- **Data-Driven Decisions** - Evidence-based workforce planning
- **Audit Readiness** - Comprehensive documentation trail

## 🔧 Development

The system uses a modular architecture with clear separation of concerns:
- **Data Layer:** CSV processing with time format handling
- **Analysis Layer:** Pandas-based computation engine
- **Visualization Layer:** Plotly/Matplotlib chart generation
- **Presentation Layer:** Streamlit dashboard + ReportLab PDF
- **Integration Layer:** Combined launcher and dependency management

## 📞 Support

For questions about the analysis or to request custom reporting features, refer to the comprehensive documentation within each module and the interactive help system in the dashboard.

---

**Generated by:** Esker Lodge Timesheet Analysis System  
**Last Updated:** May 2025  
**Version:** 2.0 - Customer Report & Dashboard Edition 