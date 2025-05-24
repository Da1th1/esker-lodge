#!/usr/bin/env python3
"""
Fresh Timesheet Combiner
Combines all Excel timesheet files from the timesheets folder into one clean dataset.
Ensures consistent headers and proper data appending.
"""

import os
import pandas as pd
import glob
from datetime import datetime
import re

def extract_week_info(filename):
    """Extract year and week number from filename."""
    # Use regex to extract year and week from filename like "EskerLodgeNursingHome-2024-W01.xlsx"
    match = re.search(r'(\d{4})-W(\d{1,2})', filename)
    if match:
        year = match.group(1)
        week = match.group(2).zfill(2)  # Pad with zero if needed
        return year, week
    return None, None

def standardize_excel_read(file_path):
    """Read Excel file with standardized approach."""
    try:
        # Read the file to determine the correct structure
        # We know from our analysis that headers are in row 4 (0-indexed)
        df = pd.read_excel(file_path, header=4)
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove rows where Staff Number is NaN (these are likely empty or header rows)
        if 'Staff Number' in df.columns:
            df = df.dropna(subset=['Staff Number'])
            
        # Ensure Staff Number is numeric where possible
        if 'Staff Number' in df.columns:
            df['Staff Number'] = pd.to_numeric(df['Staff Number'], errors='coerce')
            # Remove rows where Staff Number couldn't be converted (likely headers)
            df = df.dropna(subset=['Staff Number'])
        
        return df
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def main():
    print("🚀 Fresh Timesheet Combiner")
    print("=" * 60)
    
    # Path to the timesheets directory
    timesheet_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timesheets")
    
    # Get all Excel files in the timesheets directory (exclude temporary files)
    pattern = os.path.join(timesheet_dir, "EskerLodgeNursingHome-*.xlsx")
    timesheet_files = glob.glob(pattern)
    
    # Sort files by year and week for consistent processing
    timesheet_files.sort()
    
    print(f"Found {len(timesheet_files)} timesheet files")
    
    # Store individual dataframes
    all_dataframes = []
    header_established = False
    master_columns = None
    
    # Process each Excel file
    for i, file_path in enumerate(timesheet_files):
        filename = os.path.basename(file_path)
        
        # Skip temporary Excel files
        if filename.startswith('~$'):
            print(f"Skipping temporary file: {filename}")
            continue
            
        print(f"Processing {i+1:2d}/{len(timesheet_files)}: {filename}")
        
        # Read the Excel file
        df = standardize_excel_read(file_path)
        
        if df is None or len(df) == 0:
            print(f"  ⚠️  No valid data found in {filename}")
            continue
        
        # Establish master column structure from first successful file
        if not header_established:
            master_columns = list(df.columns)
            header_established = True
            print(f"  📋 Header established with {len(master_columns)} columns")
            print(f"     Columns: {master_columns}")
        
        # Ensure this file has the same columns as master
        if list(df.columns) != master_columns:
            print(f"  ⚠️  Column mismatch in {filename}")
            print(f"     Expected: {len(master_columns)} columns")
            print(f"     Found: {len(df.columns)} columns")
            
            # Try to align columns
            missing_cols = set(master_columns) - set(df.columns)
            extra_cols = set(df.columns) - set(master_columns)
            
            if missing_cols:
                print(f"     Missing: {missing_cols}")
                for col in missing_cols:
                    df[col] = None
            
            if extra_cols:
                print(f"     Extra: {extra_cols}")
                df = df.drop(columns=list(extra_cols))
            
            # Reorder columns to match master
            df = df[master_columns]
        
        # Extract year and week information
        year, week = extract_week_info(filename)
        
        # Add metadata columns
        df['Source_File'] = filename
        if year and week:
            df['Year'] = int(year)
            df['Week'] = int(week)
            df['YearWeek'] = f"{year}-W{week}"
        
        # Add to collection
        all_dataframes.append(df)
        print(f"  ✅ Added {len(df)} rows from {filename} (Year: {year}, Week: {week})")
    
    if not all_dataframes:
        print("❌ No valid dataframes were created. Check the file formats and paths.")
        return
    
    print(f"\n📊 Combining {len(all_dataframes)} dataframes...")
    
    # Combine all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
    
    # Sort by Year, Week, and Staff Number for consistent ordering
    if 'Year' in combined_df.columns and 'Week' in combined_df.columns:
        combined_df = combined_df.sort_values(['Year', 'Week', 'Staff Number'])
    
    # Reset index
    combined_df = combined_df.reset_index(drop=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output files
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save as CSV (primary format for dashboard)
    csv_output = os.path.join(output_dir, f"master_timesheets_{timestamp}.csv")
    combined_df.to_csv(csv_output, index=False)
    
    # Save as Excel (backup format)
    excel_output = os.path.join(output_dir, f"master_timesheets_{timestamp}.xlsx")
    combined_df.to_excel(excel_output, index=False)
    
    print(f"\n🎉 SUCCESS!")
    print(f"📁 CSV saved to: {csv_output}")
    print(f"📁 Excel saved to: {excel_output}")
    
    # Display comprehensive summary
    print(f"\n📈 DATASET SUMMARY:")
    print(f"{'Files processed:':<20} {len(all_dataframes)}")
    print(f"{'Total records:':<20} {len(combined_df):,}")
    print(f"{'Total columns:':<20} {len(combined_df.columns)}")
    
    if 'Year' in combined_df.columns:
        year_counts = combined_df['Year'].value_counts().sort_index()
        print(f"{'Year distribution:':<20}")
        for year, count in year_counts.items():
            print(f"  {year}: {count:,} records")
    
    if 'Staff Number' in combined_df.columns:
        unique_staff = combined_df['Staff Number'].nunique()
        print(f"{'Unique employees:':<20} {unique_staff}")
    
    print(f"\n📋 COLUMN STRUCTURE:")
    for i, col in enumerate(combined_df.columns, 1):
        non_null = combined_df[col].count()
        null_count = len(combined_df) - non_null
        print(f"  {i:2d}. {col:<25} ({non_null:,} non-null, {null_count:,} null)")
    
    print(f"\n🎯 SAMPLE DATA (first 3 rows):")
    if len(combined_df) > 0:
        sample_df = combined_df.head(3)
        print(sample_df.to_string())
    
    print(f"\n✅ Ready to use with dashboard!")
    print(f"   Update dashboard to use: {os.path.basename(csv_output)}")

if __name__ == "__main__":
    main() 