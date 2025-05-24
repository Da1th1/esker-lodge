#!/usr/bin/env python3
"""
Professional Customer Report Generator for Esker Lodge Timesheet Analysis
Creates a comprehensive, client-ready report with executive summary, findings, and recommendations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
warnings.filterwarnings('ignore')

class CustomerReportGenerator:
    def __init__(self, csv_file=None):
        self.csv_file = self.find_latest_cleaned_file() if csv_file is None else csv_file
        self.df = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def find_latest_cleaned_file(self):
        """Find the latest cleaned CSV file"""
        import glob
        cleaned_files = glob.glob("corrected_timesheet_cleaned_*.csv")
        if cleaned_files:
            return max(cleaned_files)
        else:
            # Fallback to master file
            return 'master_timesheets_20250524_132012.csv'
    
    def load_data(self):
        """Load the cleaned timesheet data"""
        print("📊 Loading data for customer report...")
        self.df = pd.read_csv(self.csv_file)
        
        # If this is the master file, we need to apply time parsing
        if 'Total Hours_Hours' not in self.df.columns:
            print("⚠️  Applying time format conversion...")
            self.df = self.apply_time_conversion()
        
        print(f"✅ Loaded {len(self.df):,} records")
        return self.df
    
    def apply_time_conversion(self):
        """Apply time format conversion if needed"""
        from corrected_timesheet_analysis import CorrectedTimesheetAnalyzer
        analyzer = CorrectedTimesheetAnalyzer(self.csv_file)
        analyzer.load_data()
        return analyzer.clean_data()
    
    def create_executive_summary_chart(self):
        """Create executive summary visualization"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Department hours breakdown
        dept_hours = self.df.groupby('Department_Clean')['Total Hours_Hours'].sum().sort_values(ascending=False)
        dept_hours.head(8).plot(kind='bar', ax=ax1, color='steelblue', alpha=0.8)
        ax1.set_title('Total Hours by Department', fontweight='bold', fontsize=14)
        ax1.set_ylabel('Total Hours')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Monthly trends (approximate from weeks)
        weekly_totals = self.df.groupby('YearWeek')['Total Hours_Hours'].sum()
        ax2.plot(range(len(weekly_totals)), weekly_totals.values, marker='o', linewidth=2, color='darkgreen')
        ax2.set_title('Weekly Hours Trend', fontweight='bold', fontsize=14)
        ax2.set_ylabel('Total Hours')
        ax2.set_xlabel('Week')
        ax2.grid(True, alpha=0.3)
        
        # 3. Overtime distribution
        hours_data = self.df[self.df['Total Hours_Hours'] > 0]['Total Hours_Hours']
        ax3.hist(hours_data, bins=25, color='lightcoral', alpha=0.7, edgecolor='black')
        ax3.axvline(48, color='red', linestyle='--', linewidth=2, label='48h Overtime Threshold')
        ax3.axvline(hours_data.mean(), color='orange', linestyle='--', linewidth=2, 
                   label=f'Average: {hours_data.mean():.1f}h')
        ax3.set_title('Distribution of Weekly Hours', fontweight='bold', fontsize=14)
        ax3.set_xlabel('Hours per Week')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        
        # 4. Staff utilization by department
        dept_staff = self.df.groupby('Department_Clean')['Name'].nunique().sort_values(ascending=False)
        dept_staff.head(8).plot(kind='bar', ax=ax4, color='mediumseagreen', alpha=0.8)
        ax4.set_title('Number of Staff by Department', fontweight='bold', fontsize=14)
        ax4.set_ylabel('Number of Staff')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        chart_path = f'customer_report_summary_{self.timestamp}.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def create_compliance_chart(self):
        """Create compliance analysis chart"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Overtime by department
        overtime_by_dept = self.df[self.df['Total Hours_Hours'] > 48].groupby('Department_Clean').size()
        if len(overtime_by_dept) > 0:
            overtime_by_dept.sort_values(ascending=False).plot(kind='bar', ax=ax1, color='orange', alpha=0.8)
            ax1.set_title('Overtime Records by Department (>48h)', fontweight='bold')
            ax1.set_ylabel('Number of Overtime Records')
            ax1.tick_params(axis='x', rotation=45)
        
        # 2. High hours violations (>60h)
        high_hours = self.df[self.df['Total Hours_Hours'] > 60]
        if len(high_hours) > 0:
            high_hours_by_dept = high_hours.groupby('Department_Clean').size()
            high_hours_by_dept.plot(kind='bar', ax=ax2, color='red', alpha=0.8)
            ax2.set_title('Excessive Hours by Department (>60h)', fontweight='bold')
            ax2.set_ylabel('Number of Violations')
            ax2.tick_params(axis='x', rotation=45)
        
        # 3. Staff with missing pay rates
        missing_pay = self.df[(self.df['Pay Rate'].isna()) & (self.df['Total Hours_Hours'] > 0)]
        if len(missing_pay) > 0:
            missing_by_dept = missing_pay.groupby('Department_Clean').size()
            missing_by_dept.plot(kind='bar', ax=ax3, color='purple', alpha=0.8)
            ax3.set_title('Missing Pay Rates by Department', fontweight='bold')
            ax3.set_ylabel('Records Missing Pay Rate')
            ax3.tick_params(axis='x', rotation=45)
        
        # 4. Compliance summary
        total_records = len(self.df[self.df['Total Hours_Hours'] > 0])
        compliance_data = {
            'Compliant (<48h)': len(self.df[self.df['Total Hours_Hours'] <= 48]),
            'Overtime (48-60h)': len(self.df[(self.df['Total Hours_Hours'] > 48) & (self.df['Total Hours_Hours'] <= 60)]),
            'Excessive (>60h)': len(self.df[self.df['Total Hours_Hours'] > 60])
        }
        
        colors_pie = ['lightgreen', 'orange', 'red']
        ax4.pie(compliance_data.values(), labels=compliance_data.keys(), autopct='%1.1f%%', 
               colors=colors_pie, startangle=90)
        ax4.set_title('Hours Compliance Overview', fontweight='bold')
        
        plt.tight_layout()
        chart_path = f'customer_report_compliance_{self.timestamp}.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def calculate_key_metrics(self):
        """Calculate key metrics for the report"""
        total_records = len(self.df)
        records_with_hours = (self.df['Total Hours_Hours'] > 0).sum()
        total_hours = self.df['Total Hours_Hours'].sum()
        unique_staff = self.df['Name'].nunique()
        unique_departments = self.df['Department_Clean'].nunique()
        
        # Compliance metrics
        overtime_records = (self.df['Total Hours_Hours'] > 48).sum()
        excessive_hours = (self.df['Total Hours_Hours'] > 60).sum()
        missing_pay_rate = ((self.df['Pay Rate'].isna()) & (self.df['Total Hours_Hours'] > 0)).sum()
        
        # Staff metrics
        avg_hours_per_staff = self.df.groupby('Name')['Total Hours_Hours'].mean().mean()
        top_department = self.df.groupby('Department_Clean')['Total Hours_Hours'].sum().idxmax()
        
        return {
            'total_records': total_records,
            'records_with_hours': records_with_hours,
            'total_hours': total_hours,
            'unique_staff': unique_staff,
            'unique_departments': unique_departments,
            'overtime_records': overtime_records,
            'excessive_hours': excessive_hours,
            'missing_pay_rate': missing_pay_rate,
            'avg_hours_per_staff': avg_hours_per_staff,
            'top_department': top_department,
            'time_period': f"{self.df['YearWeek'].min()} to {self.df['YearWeek'].max()}"
        }
    
    def generate_pdf_report(self):
        """Generate professional PDF report"""
        print("📄 Generating PDF customer report...")
        
        # Create charts
        summary_chart = self.create_executive_summary_chart()
        compliance_chart = self.create_compliance_chart()
        
        # Calculate metrics
        metrics = self.calculate_key_metrics()
        
        # Create PDF
        report_filename = f"Esker_Lodge_Timesheet_Analysis_Report_{self.timestamp}.pdf"
        doc = SimpleDocTemplate(report_filename, pagesize=A4)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.darkblue,
            spaceBefore=20,
            spaceAfter=12
        )
        
        # Content
        content = []
        
        # Title page
        content.append(Paragraph("ESKER LODGE NURSING HOME", title_style))
        content.append(Paragraph("Timesheet Analysis Report", title_style))
        content.append(Spacer(1, 0.5*inch))
        content.append(Paragraph(f"Analysis Period: {metrics['time_period']}", styles['Normal']))
        content.append(Paragraph(f"Report Generated: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
        content.append(PageBreak())
        
        # Executive Summary
        content.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
        
        summary_text = f"""
        This comprehensive analysis of Esker Lodge timesheet data covers {metrics['total_records']:,} records 
        spanning {metrics['unique_staff']} staff members across {metrics['unique_departments']} departments 
        from {metrics['time_period']}.
        
        <b>Key Findings:</b>
        • Total Hours Worked: {metrics['total_hours']:,.0f} hours
        • Records with Hours: {metrics['records_with_hours']:,} ({metrics['records_with_hours']/metrics['total_records']*100:.1f}%)
        • Average Hours per Staff: {metrics['avg_hours_per_staff']:.1f} hours/week
        • Highest Activity Department: {metrics['top_department']}
        
        <b>Compliance Concerns:</b>
        • Overtime Records (>48h/week): {metrics['overtime_records']} ({metrics['overtime_records']/metrics['records_with_hours']*100:.1f}%)
        • Excessive Hours (>60h/week): {metrics['excessive_hours']} cases
        • Missing Pay Rate Records: {metrics['missing_pay_rate']} instances
        """
        
        content.append(Paragraph(summary_text, styles['Normal']))
        content.append(Spacer(1, 0.3*inch))
        
        # Add summary chart
        content.append(Image(summary_chart, width=7*inch, height=5.25*inch))
        content.append(PageBreak())
        
        # Department Analysis
        content.append(Paragraph("DEPARTMENT ANALYSIS", heading_style))
        
        # Department summary table
        dept_summary = self.df.groupby('Department_Clean').agg({
            'Total Hours_Hours': ['sum', 'mean'],
            'Name': 'nunique'
        }).round(1)
        dept_summary.columns = ['Total Hours', 'Avg Hours/Record', 'Staff Count']
        dept_summary = dept_summary.sort_values('Total Hours', ascending=False)
        
        dept_data = [['Department', 'Total Hours', 'Avg Hours/Record', 'Staff Count']]
        for dept, row in dept_summary.iterrows():
            dept_data.append([dept, f"{row['Total Hours']:,.0f}", f"{row['Avg Hours/Record']:.1f}", str(row['Staff Count'])])
        
        dept_table = Table(dept_data)
        dept_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(dept_table)
        content.append(PageBreak())
        
        # Compliance Analysis
        content.append(Paragraph("COMPLIANCE ANALYSIS", heading_style))
        
        compliance_text = f"""
        <b>EU Working Time Directive Compliance Assessment:</b>
        
        The analysis reveals several areas of concern regarding working time compliance:
        
        • <b>Overtime Frequency:</b> {metrics['overtime_records']} records show staff working more than 48 hours per week
        • <b>Excessive Hours:</b> {metrics['excessive_hours']} instances of staff working more than 60 hours per week
        • <b>Data Quality:</b> {metrics['missing_pay_rate']} records with hours worked but missing pay rates
        
        <b>Risk Assessment:</b>
        • HIGH RISK: Excessive hours violations may breach Working Time Directive limits
        • MEDIUM RISK: High overtime frequency suggests potential understaffing
        • LOW RISK: Missing pay rate data affects payroll accuracy
        """
        
        content.append(Paragraph(compliance_text, styles['Normal']))
        content.append(Spacer(1, 0.3*inch))
        content.append(Image(compliance_chart, width=7*inch, height=5.25*inch))
        content.append(PageBreak())
        
        # Recommendations
        content.append(Paragraph("RECOMMENDATIONS", heading_style))
        
        recommendations_text = """
        <b>IMMEDIATE ACTIONS REQUIRED:</b>
        
        1. <b>Address Excessive Hours:</b>
           • Review all cases where staff worked >60 hours/week
           • Implement controls to prevent Working Time Directive violations
           • Consider disciplinary action for unauthorized overtime
        
        2. <b>Fix Data Quality Issues:</b>
           • Update missing pay rates immediately
           • Implement validation checks in timesheet system
           • Train staff on proper data entry procedures
        
        <b>SHORT-TERM IMPROVEMENTS (1-4 weeks):</b>
        
        3. <b>Staffing Review:</b>
           • Analyze overtime patterns to identify understaffed departments
           • Consider additional hiring for departments with consistent overtime
           • Review shift patterns and workload distribution
        
        4. <b>Policy Updates:</b>
           • Establish clear overtime authorization procedures
           • Implement weekly hour monitoring and alerts
           • Create compliance reporting dashboard
        
        <b>LONG-TERM STRATEGIES (1-3 months):</b>
        
        5. <b>System Improvements:</b>
           • Implement automated compliance checking
           • Set up real-time monitoring alerts
           • Regular data quality audits
        
        6. <b>Staff Wellness:</b>
           • Monitor staff fatigue and burnout indicators
           • Ensure adequate rest periods between shifts
           • Regular health and safety assessments
        """
        
        content.append(Paragraph(recommendations_text, styles['Normal']))
        content.append(PageBreak())
        
        # Conclusion
        content.append(Paragraph("CONCLUSION", heading_style))
        
        conclusion_text = f"""
        The timesheet analysis reveals a generally well-functioning workforce management system with some areas 
        requiring immediate attention. With {metrics['total_hours']:,.0f} total hours worked across 
        {metrics['unique_staff']} staff members, Esker Lodge demonstrates significant operational capacity.
        
        However, the {metrics['overtime_records']} overtime instances and {metrics['excessive_hours']} cases 
        of excessive hours require immediate management attention to ensure compliance with employment legislation 
        and staff welfare standards.
        
        Implementation of the recommended actions will improve compliance, enhance data quality, and support 
        better workforce planning decisions.
        
        <b>Next Steps:</b>
        • Schedule immediate review meeting with HR leadership
        • Prioritize high-risk compliance issues
        • Implement monitoring systems for ongoing oversight
        • Plan quarterly reviews of timesheet data quality
        
        This analysis provides a foundation for evidence-based workforce management decisions and regulatory 
        compliance monitoring.
        """
        
        content.append(Paragraph(conclusion_text, styles['Normal']))
        
        # Build PDF
        doc.build(content)
        
        print(f"✅ Customer report generated: {report_filename}")
        return report_filename
    
    def generate_report(self):
        """Generate the complete customer report"""
        self.load_data()
        return self.generate_pdf_report()

def main():
    """Generate customer report"""
    print("🎯 GENERATING CUSTOMER REPORT")
    print("=" * 50)
    
    generator = CustomerReportGenerator()
    report_file = generator.generate_report()
    
    print(f"\n✅ Customer report completed!")
    print(f"📄 Report saved as: {report_file}")
    print("\nThis professional report is ready for customer presentation.")

if __name__ == "__main__":
    main() 