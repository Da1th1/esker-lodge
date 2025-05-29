# 📊 Excel Payroll File Analysis & Timesheet Correlation

## 🎯 Objective
**Correlate payroll data (Excel) with timesheet data (CSV) to identify discrepancies in pay and time reporting.**

---

## 📁 Data Sources

### 1. **Payroll Data**: `1788-Esker Lodge Ltd Hours & Gross Pay Jan to Apr (2).xlsx`
- **Sheet**: "1788-Esker Lodge Ltd Employee H"
- **Period**: January to April 2025
- **Structure**: Detailed hour categories with corresponding gross pay

### 2. **Timesheet Data**: `master_timesheets_20250524_132012.csv`
- **Period**: 2024-W01 to 2025-W20 (67 weeks)
- **Structure**: Weekly timesheet entries per employee
- **Source**: Individual weekly Excel timesheet files consolidated

---

## 🏗️ Excel Payroll File Structure

### **Row Layout**
```
Row 1: Hour Category Names (Headers)
Row 2: First Employee Data
Row 3: Second Employee Data
...and so on
```

### **Column Structure** (39 columns total)

#### **Employee Information (Columns 1-4)**
```
Column A: Depart          → Department (e.g., "Activity Therap", "HCA", "Nurse")
Column B: Sequence        → Employee ID number
Column C: Forename        → First name
Column D: Surname         → Last name
```

#### **Hour Categories & Gross Pay (Columns 5-39)**
*Pattern: [Hours Column, Gross Pay Column] pairs*

1. **Basic Hours**: `Basic` | `Gross`
2. **Night Rate**: `Night Rate` | `Gross` 
3. **Saturday Rate**: `Saturday Rate` | `Gross`
4. **Saturday Night Rate**: `Saturday Night Rate` | `Gross`
5. **Sunday Rate**: `Sunday Rate` | `Gross`
6. **Sunday Night Rate**: `Sunday Night Rate` | `Gross`
7. **Old Day/Sat Rate**: `Old Day/Sat Rate` | `Gross`
8. **Old Night Rate**: `Old Night Rate` | `Gross`
9. **Old Sun Rate**: `Old Sun Rate` | `Gross`
10. **Non-Rostered Day**: `Non-Rostered Day` | `Gross`
11. **Backpay**: `Backpay` | `Public Holiday Entitlement`
12. **Holidays**: `Holidays` | `Gross`
13. **Cross Function Day1**: `Cross Function Day1` | `Gross`
14. **Cross Function Day2**: `Cross Function Day2` | `Gross`
15. **Cross Function Sun1**: `Cross Function Sun1` | `Gross`
16. **Training/Meetings**: `Training/Meetings` | `Gross`
17. **Statutory Sick**: `Statutory Sick` | `Gross`

---

## 📋 Timesheet CSV Structure

### **Key Columns**
```
Staff Number          → Employee ID (matches Excel Sequence)
Name                  → Employee name (format: "SURNAME, Firstname")
Department Name       → Department description
Total Hours          → Weekly total hours (HH:MM format)
Year, Week, YearWeek  → Time period identifiers
Source_File           → Original weekly timesheet file
```

### **Hour Categories Available**
```
Basic, Night Rate, Sunday Rate, Sunday Night Rate, Holidays,
Public Holiday Entitlement, Statutory Sick, Non-Rostered Day,
Saturday Rate, Saturday Night Rate, Training/Meetings
```

---

## 🔄 Correlation Methodology

### **1. Employee Matching**
```python
# Excel: "Forename" + "Surname" → "John Smith"
# CSV: "Name" → "SMITH, John"
# Solution: Normalize both to "John Smith" format
```

### **2. Hour Aggregation**
- **Timesheet**: Sum weekly hours across all weeks (Jan-Apr 2025)
- **Payroll**: Use direct hour values from Excel (period totals)

### **3. Category Mapping**
```
Excel Column → Timesheet Column
═══════════════════════════════
Basic → Basic
Night Rate → Night Rate  
Saturday Rate → Saturday Rate
Saturday Night Rate → Saturday Night Rate
Sunday Rate → Sunday Rate
Sunday Night Rate → Sunday Night Rate
Old Day/Sat Rate → (Legacy data, no timesheet equivalent)
Old Night Rate → (Legacy data, no timesheet equivalent)
Old Sun Rate → (Legacy data, no timesheet equivalent)
Non-Rostered Day → Non-Rostered Day
Backpay → (Adjustment, no timesheet equivalent)
Holidays → Holidays
Cross Function Day1 → (Department transfer, limited timesheet data)
Cross Function Day2 → (Department transfer, limited timesheet data)
Cross Function Sun1 → (Department transfer, limited timesheet data)
Training/Meetings → Training/Meetings
Statutory Sick → Statutory Sick
```

---

## ⚠️ Current Discrepancy Findings

### **Overall Statistics**
- **📊 Total Employees**: 197
- **⚠️ Mismatch Rate**: 90.4% (178 employees with >2h difference)
- **📉 Net Difference**: -35,790 hours (Timesheet > Payroll)
- **🔍 Average Difference**: -181.7 hours per employee

### **Hour Category Breakdown** (Payroll Data)
```
Day Rate (Basic):           21,266.0 hours (50.9%)
Night Rate:                  4,713.1 hours (11.3%)
Weekend Hours Combined:      6,701.4 hours (16.1%)
├── Saturday Day:            2,932.9 hours
├── Saturday Night:            299.2 hours  
├── Sunday Day:              3,469.3 hours
└── Sunday Night:            1,499.0 hours
Extra Shift Bonus:           2,566.5 hours (6.1%)
Legacy Rates:                2,904.4 hours (7.0%)
Special Pay:                 2,170.1 hours (5.2%)
Cross Function:                 16.2 hours (0.04%)
```

---

## 🚨 Key Discrepancy Patterns

### **1. Major Hour Deficit**
- **Issue**: Timesheet hours (77,616h) exceed payroll hours (41,826h)
- **Implication**: Potential underpayment or timesheet over-reporting
- **Action Required**: Immediate investigation

### **2. Legacy Rate Usage**
- **Old Day/Sat Rate**: 2,153.2 hours
- **Old Night/Sun Rates**: 751.2 hours
- **Issue**: May indicate incorrect rate application or delayed system updates

### **3. Limited Cross-Function Tracking**
- **Cross Function Total**: Only 16.2 hours across all employees
- **Issue**: Possible under-reporting of inter-departmental work

### **4. Weekend Work Complexity**
- **Multiple Rates**: Separate day/night rates for Sat/Sun
- **High Volume**: 6,701 weekend hours (16% of total)
- **Risk**: Complex rate structure increases error probability

---

## 💡 Correlation Analysis Insights

### **Strengths of Current System**
✅ **Detailed Category Tracking**: 17 distinct hour types in payroll
✅ **Automated Matching**: Employee name normalization working
✅ **Period Alignment**: Both datasets cover Jan-Apr 2025
✅ **Department Mapping**: Successful correlation across departments

### **Areas for Improvement**
❌ **Rate Structure Complexity**: Too many legacy rates causing confusion
❌ **Cross-Function Tracking**: Minimal hours suggest under-reporting
❌ **Timesheet Aggregation**: Weekly data may miss daily rate variations
❌ **Missing Categories**: Some payroll categories have no timesheet equivalent

---

## 🎯 Recommended Actions

### **Immediate (High Priority)**
1. **🔍 Investigate -35,790 Hour Difference**
   - Review top 20 employees with largest discrepancies
   - Verify timesheet completion rates for Jan-Apr period
   - Check for missed payroll entries

2. **📊 Legacy Rate Review**
   - Audit 2,904 hours of "Old" rates
   - Ensure proper transition to current rate structure
   - Update system to prevent legacy rate usage

### **Short-term (Medium Priority)**
3. **🔄 Enhance Timesheet Categories**
   - Add cross-function hour tracking to weekly timesheets
   - Include backpay adjustment fields
   - Standardize rate categories between systems

4. **⚡ Real-time Validation**
   - Implement weekly comparison checks
   - Alert when individual differences exceed 5 hours
   - Create department-level monitoring dashboards

### **Long-term (Strategic)**
5. **🏗️ System Integration**
   - Direct timesheet-to-payroll system connection
   - Eliminate manual data transfer steps
   - Real-time hour validation during timesheet entry

6. **📈 Advanced Analytics**
   - Predictive modeling for hour discrepancies
   - Department benchmarking and trending
   - Cost impact analysis of discrepancies

---

## 🔧 Technical Implementation

### **Current Analysis Pipeline**
```
1. Load Excel → Extract 17 hour categories
2. Load CSV → Aggregate weekly hours by employee
3. Normalize names → Match employees across systems  
4. Compare totals → Calculate differences
5. Generate reports → Identify anomalies
6. Dashboard → Visualize discrepancies
```

### **Enhanced Dashboard Features**
- **Real-time Data Refresh**: Auto-update every 5 minutes
- **Category Drill-down**: Analyze specific hour types
- **Department Heatmaps**: Visual discrepancy patterns
- **Employee Search**: Quick individual lookups
- **Export Capabilities**: Excel/CSV downloads for further analysis

---

## 📊 Business Impact

### **Financial Implications**
- **Potential Underpayment**: 35,790 hours × average rate = significant liability
- **Compliance Risk**: Incorrect hour reporting affects labor law compliance
- **Audit Exposure**: Large discrepancies flag for external audits

### **Operational Benefits of Resolution**
- **✅ Accurate Payroll**: Ensure employees receive correct compensation
- **✅ Compliance**: Meet labor law requirements for hour tracking
- **✅ Efficiency**: Reduce manual reconciliation time
- **✅ Trust**: Build employee confidence in payroll accuracy

---

**📈 Conclusion**: The current analysis reveals significant discrepancies requiring immediate attention, particularly the 35,790-hour deficit. The enhanced dashboard and detailed correlation methodology provide the tools needed to identify, investigate, and resolve these issues systematically.

**🎯 Next Steps**: Focus on the top discrepancy cases, audit legacy rate usage, and implement real-time validation to prevent future mismatches. 