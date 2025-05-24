#!/usr/bin/env python3
"""
Examine source Excel files to understand data structure
"""

import pandas as pd
import os

def examine_excel_file(file_path):
    """Examine a single Excel file to understand its structure"""
    print(f"\nExamining: {os.path.basename(file_path)}")
    print("-" * 50)
    
    try:
        # Try reading with different header rows
        for header_row in [0, 1, 2, 3, 4, 5]:
            try:
                df = pd.read_excel(file_path, header=header_row)
                print(f"Header row {header_row}: Shape {df.shape}")
                
                # Show columns
                print(f"Columns: {list(df.columns)}")
                
                # Look for hour data
                hour_cols = [col for col in df.columns if 'hour' in str(col).lower() or 'basic' in str(col).lower()]
                if hour_cols:
                    print(f"Hour columns found: {hour_cols}")
                    for col in hour_cols:
                        non_zero = df[col].fillna(0)
                        non_zero = pd.to_numeric(non_zero, errors='coerce').fillna(0)
                        count_non_zero = (non_zero > 0).sum()
                        if count_non_zero > 0:
                            print(f"  {col}: {count_non_zero} non-zero values")
                            print(f"    Sample values: {list(non_zero[non_zero > 0].head())}")
                
                # Show first few rows of data
                if len(df) > 0:
                    print(f"First 3 rows:")
                    print(df.head(3).to_string())
                
                # If this looks like the right structure, stop here
                if 'Staff Number' in str(df.columns) and len(df) > 5:
                    return df
                    
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
        
    return None

def main():
    # Look at a few recent files
    timesheet_dir = "timesheets"
    
    # Get a few files to examine
    import glob
    files = glob.glob(os.path.join(timesheet_dir, "EskerLodgeNursingHome-2025-W*.xlsx"))
    files.extend(glob.glob(os.path.join(timesheet_dir, "EskerLodgeNursingHome-2024-W5*.xlsx")))
    
    files = files[:3]  # Just examine 3 files
    
    for file_path in files:
        df = examine_excel_file(file_path)
        if df is not None and len(df) > 0:
            # Look for any numeric data that might be hours
            print(f"\nNumeric columns analysis:")
            for col in df.columns:
                try:
                    numeric_data = pd.to_numeric(df[col], errors='coerce')
                    non_zero = (numeric_data > 0).sum()
                    if non_zero > 0:
                        max_val = numeric_data.max()
                        if max_val < 100:  # Likely hours if under 100
                            print(f"  {col}: {non_zero} values, max: {max_val}")
                except:
                    continue

if __name__ == "__main__":
    main() 