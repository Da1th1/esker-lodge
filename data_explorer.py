#!/usr/bin/env python3
"""
Quick data exploration script for Esker Lodge timesheet data
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def explore_dataset():
    # Load the dataset
    print("Loading dataset...")
    df = pd.read_csv('master_timesheets_20250524_132012.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Total records: {len(df):,}")
    
    print("\nColumn names and data types:")
    for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes)):
        print(f"{i:2d}: {col:<25} ({dtype})")
    
    # Look for hour-related columns
    hour_columns = [col for col in df.columns if any(word in col.lower() for word in ['hour', 'basic', 'night', 'sunday', 'saturday', 'holiday'])]
    print(f"\nHour-related columns: {hour_columns}")
    
    # Check for non-empty values in key columns
    print("\nData availability check:")
    key_cols = ['Name', 'Department', 'Total Hours', 'Pay Rate', 'Basic', 'Night Rate']
    for col in key_cols:
        if col in df.columns:
            non_empty = df[col].notna() & (df[col] != '')
            non_zero = pd.to_numeric(df[col], errors='coerce') != 0
            print(f"{col:<15}: {non_empty.sum():,} non-empty, {non_zero.sum():,} non-zero")
    
    # Sample records with actual data
    print("\nSample records with Total Hours data:")
    total_hours_col = 'Total Hours' if 'Total Hours' in df.columns else None
    if total_hours_col:
        # Convert to numeric and find non-zero values
        df_temp = df.copy()
        df_temp[total_hours_col] = pd.to_numeric(df_temp[total_hours_col], errors='coerce')
        with_hours = df_temp[(df_temp[total_hours_col] > 0) & (df_temp[total_hours_col].notna())]
        print(f"Records with Total Hours > 0: {len(with_hours)}")
        if len(with_hours) > 0:
            print(with_hours[['Name', 'Department', 'Total Hours', 'YearWeek']].head(10))
    
    # Check for Basic hours
    print("\nSample records with Basic Hours data:")
    if 'Basic' in df.columns:
        df_temp = df.copy()
        df_temp['Basic'] = pd.to_numeric(df_temp['Basic'], errors='coerce')
        with_basic = df_temp[(df_temp['Basic'] > 0) & (df_temp['Basic'].notna())]
        print(f"Records with Basic Hours > 0: {len(with_basic)}")
        if len(with_basic) > 0:
            print(with_basic[['Name', 'Department', 'Basic', 'YearWeek']].head(10))
    
    # Department summary
    print(f"\nDepartment summary:")
    if 'Department Name' in df.columns:
        dept_counts = df['Department Name'].value_counts()
        print(dept_counts.head(10))
    elif 'Department' in df.columns:
        dept_counts = df['Department'].value_counts()
        print(dept_counts.head(10))
    
    # Time period coverage
    print(f"\nTime period coverage:")
    if 'YearWeek' in df.columns:
        periods = df['YearWeek'].value_counts().sort_index()
        print(f"First week: {periods.index[0]}")
        print(f"Last week: {periods.index[-1]}")
        print(f"Total weeks: {len(periods)}")

if __name__ == "__main__":
    explore_dataset() 