# noinspection PyUnusedImports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# ==========================================
# 1. Functions for Specific Cleaning
# ==========================================

def clean_dataset_1(df):
    """
    Specific cleaning for Dataset 1 (Cost of Cultivation).
    Renames complex column names to simple coding-friendly names.
    """
    # Rename Columns to be coding-friendly
    new_names = {
        'Cost of Cultivation (`/Hectare) A2+FL': 'Cost_A2_FL',
        'Cost of Cultivation (`/Hectare) C2': 'Cost_C2',
        'Cost of Production (`/Quintal) C2': 'Production_Cost',
        'Yield (Quintal/ Hectare)': 'Yield'
    }
    df = df.rename(columns=new_names)
    return df

def clean_dataset_2(df):
    """
    Specific cleaning for Dataset 2.
    1. Strips extra spaces from column names.
    2. Replaces spaces/hyphens with underscores.
    3. Cleans 'Crop' column and DROPS 'Total' summary rows to avoid double-counting.
    """
    # 1. Standardize Column Names
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(' ', '_').str.replace('-', '_')

    # 2. Clean 'Crop' values
    if 'Crop' in df.columns:
        df['Crop'] = df['Crop'].str.strip()

        # 3. Filter out summary rows (Rows starting with 'Total')
        # We keep only rows where 'Crop' does NOT start with 'Total'
        df = df[~df['Crop'].str.startswith('Total')]

    return df

def clean_dataset_3(df):
    """
    Specific cleaning for Dataset 3 (Crop Varieties).
    1. Drops empty columns.
    2. Renames columns to be coding-friendly.
    3. Fills missing text information.
    """
    # 1. Drop the empty 'Unnamed' column if it exists
    # axis=1 means columns, inplace=False returns a new copy
    df = df.dropna(axis=1, how='all')

    # 2. Standardize Column Names
    df.columns = df.columns.str.strip()

    new_names = {
        'Season/ duration in days': 'Season_Duration',
        'Recommended Zone': 'Recommended_Zone'
    }
    df = df.rename(columns=new_names)

    # 3. Fill missing values for text columns
    # Since this is descriptive data, we don't want to delete rows, just label them.
    df = df.fillna("Unknown")

    # 4. Clean 'Crop' column
    # we just strip spaces.
    if 'Crop' in df.columns:
        df['Crop'] = df['Crop'].str.strip()

    return df

def clean_dataset_4(df):
    """
    Specific cleaning for Dataset 4.
    """
    # 1. Drop completely empty rows AND create a fresh copy
    df = df.dropna(how='all').copy()

    # 2. Clean 'Crop' column (remove spaces)
    if 'Crop' in df.columns:
        df['Crop'] = df['Crop'].str.strip()

    # 3. Rename Columns and Force Numeric Conversion
    new_columns = []
    for col in df.columns:
        if col == 'Crop':
            new_columns.append(col)
        else:
            new_name = 'Year_' + col.strip().replace('-', '_')
            new_columns.append(new_name)

            # Force numeric
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.columns = new_columns

    return df

def clean_dataset_5(df):
    """
    Specific cleaning for Dataset 5 (Time Series).
    1. Standardizes column names (removes spaces, renames years).
    2. Fills missing values (NaN) with 0.
    """
    # 1. Standardize Column Names (Fixes " 3-1993" -> "3-1993")
    df.columns = df.columns.str.strip()

    # 2. Rename Year Columns to be coding-friendly
    # Change "3-1993" to "Year_1993"
    new_columns = []
    for col in df.columns:
        if col.startswith('3-'):
            # Extract the year part and add prefix
            year = col.split('-')[1]
            new_columns.append(f"Year_{year}")
        else:
            new_columns.append(col)

    df.columns = new_columns

    # 3. Fill Missing Values
    # Since this is a time series, empty usually means "no data recorded".
    # We fill with 0 so we can calculate averages/sums without errors.
    df = df.fillna(0)

    return df

# ==========================================
# 2. Analysis and Visualization
# ==========================================

# --- Analysis  ---
def analyze_dataset_1(df):
    """
    Performs analysis on Dataset 1 to answer:
    1. What are the average costs and yields?
    2. Which State has the highest Yield?
    3. Which Crop is the most expensive?
    4. Is there a correlation between Cost and Yield?
    """
    print("\n---  Analysis Report for Dataset 1 (Cost & Yield) ---")

    # 1. Summary Statistics
    print("\n[1] General Summary (Averages, Min, Max):")
    # We select only the numeric columns for the summary
    summary = df[['Cost_A2_FL', 'Cost_C2', 'Production_Cost', 'Yield']].describe()
    print(summary)

    # 2. Highest Yielding State & Crop
    # We find the row with the maximum value in the 'Yield' column
    max_yield_row = df.loc[df['Yield'].idxmax()]
    print("\n[2] Highest Yield Record:")
    print(f"   State: {max_yield_row['State']}")
    print(f"   Crop:  {max_yield_row['Crop']}")
    print(f"   Yield: {max_yield_row['Yield']} Quintal/Hectare")

    # 3. Most Expensive Crop (Cost C2)
    max_cost_row = df.loc[df['Cost_C2'].idxmax()]
    print("\n[3] Most Expensive Cultivation:")
    print(f"   Crop:  {max_cost_row['Crop']}")
    print(f"   State: {max_cost_row['State']}")
    print(f"   Cost:  {max_cost_row['Cost_C2']} Rs/Hectare")

    # 4. Lowest Cost of Production (Most Efficient)
    min_prod_cost_row = df.loc[df['Production_Cost'].idxmin()]
    print("\n[5] Lowest Production Cost (Most Efficient):")
    print(f"   Crop:  {min_prod_cost_row['Crop']}")
    print(f"   State: {min_prod_cost_row['State']}")
    print(f"   Cost:  {min_prod_cost_row['Production_Cost']} Rs/Quintal")

def analyze_dataset_2(df):
    """
    Analyzes Dataset 2 to find the HIGHEST Production, Area, and Yield.
    Uses simple string splitting to clean the Year (No complex libraries).
    """
    print("\n---  Analysis Report for Dataset 2 (All-Time Highs) ---")

    metrics = ['Production', 'Area', 'Yield']

    for metric in metrics:
        # 1. Find columns for this metric
        metric_cols = [col for col in df.columns if metric in col]

        if not metric_cols:
            continue

        # 2. Melt (Wide -> Long) to search all years
        subset = df[['Crop'] + metric_cols]
        melted = subset.melt(id_vars='Crop', var_name='Year', value_name='Value')

        # 3. Ensure numbers are numbers (not text)
        melted['Value'] = pd.to_numeric(melted['Value'], errors='coerce')

        # 4. Find the Row with the Maximum Value
        if melted['Value'].notna().any():
            max_row = melted.loc[melted['Value'].idxmax()]

            # 5. Simple Year Cleaning
            # Example: "Production_2010_11"
            raw_year = str(max_row['Year'])

            # We split the text by '_' -> ['Production', '2010', '11']
            parts = raw_year.split('_')

            # We take the last two parts and join them with a hyphen
            if len(parts) >= 2:
                clean_year = f"{parts[-2]}-{parts[-1]}"  # Becomes "2010-11"
            else:
                clean_year = raw_year

            print(f"\n Highest {metric} Recorded:")
            print(f"   Crop:  {max_row['Crop']}")
            print(f"   Value: {max_row['Value']} Units")
            print(f"   Year:  {clean_year}")

    # Calculate Percentage Growth in Area (2006-07 to 2010-11)
    if 'Area_2006_07' in df.columns and 'Area_2010_11' in df.columns:
        # (New - Old) / Old * 100
        df['Area_Growth'] = ((df['Area_2010_11'] - df['Area_2006_07']) / df['Area_2006_07']) * 100

        fastest_growth = df.sort_values(by='Area_Growth', ascending=False).iloc[0]
        print("\n Fastest Expanding Crop (Area Growth 2006-2010):")
        print(f"   Crop:   {fastest_growth['Crop']}")
        print(f"   Growth: +{fastest_growth['Area_Growth']:.2f}%")

        # Clean up temp column
        df.drop(columns=['Area_Growth'], inplace=True)

def analyze_dataset_3(df):
    """
    Analyzes Dataset 3 (Crop Varieties).
    Since this is text data, we COUNT how many varieties exist for each crop.
    """
    print("\n---  Analysis Report for Dataset 3 (Varieties) ---")

    # 1. Count varieties per crop
    # value_counts() is a magic function that counts unique entries
    variety_counts = df['Crop'].value_counts()

    print("\n[1] Total Crops Listed:")
    print(f"   {len(variety_counts)} different crops.")

    # 2. Crop with the most varieties
    most_varieties = variety_counts.idxmax()
    count_most = variety_counts.max()

    print("\n[2] Crop with the Most Varieties:")
    print(f"   Crop: {most_varieties}")
    print(f"   Count: {count_most} varieties registered")

    # 3. Crop with the least varieties
    least_varieties = variety_counts.idxmin()
    count_least = variety_counts.min()

    print("\n[3] Crop with the Fewest Varieties:")
    print(f"   Crop: {least_varieties}")
    print(f"   Count: {count_least} variety registered")

    # 4. Top Recommended Zone
    # We count how many times each Zone appears
    top_zone = df['Recommended_Zone'].value_counts().idxmax()
    zone_count = df['Recommended_Zone'].value_counts().max()

    print("\n[4] Region with Most Recommended Varieties:")
    print(f"   Zone:  {top_zone}")
    print(f"   Count: {zone_count} varieties")

def analyze_dataset_4(df):
    """
    Analyzes Dataset 4 (Indices).
    Since these are Index numbers (Base 100), we look for Growth.
    """
    print("\n---  Analysis Report for Dataset 4 (Agricultural Indices) ---")

    # 1. Identify Year Columns
    # The columns start with 'Year_' due to our cleaning step
    year_cols = [col for col in df.columns if 'Year_' in col]
    first_year = year_cols[0]  # Year_2004_05
    last_year = year_cols[-1]  # Year_2011_12

    # 2. Calculate Growth (Absolute Change in Index)
    # We create a temporary column for this calculation
    df['Total_Growth'] = df[last_year] - df[first_year]

    # 3. Fastest Growing Sector
    fastest = df.sort_values(by='Total_Growth', ascending=False).iloc[0]
    print("\n[1] Fastest Growing Sector (2004-2012):")
    print(f"   Sector: {fastest['Crop']}")
    print(f"   Growth: +{fastest['Total_Growth']:.1f} points")

    # 4. Slowest Growing Sector
    slowest = df.sort_values(by='Total_Growth', ascending=True).iloc[0]
    print("\n[2] Slowest Growing Sector:")
    print(f"   Sector: {slowest['Crop']}")
    print(f"   Growth: +{slowest['Total_Growth']:.1f} points")

    # Clean up temp column
    df.drop(columns=['Total_Growth'], inplace=True)

    # 5. Most Volatile Sector (Highest Fluctuation)
    # Standard Deviation measures how much the numbers jump up and down
    # We calculate std across the year columns
    df['Volatility'] = df[year_cols].std(axis=1)

    most_volatile = df.sort_values(by='Volatility', ascending=False).iloc[0]
    print("\n[3] Most Volatile Sector (Highest Fluctuation):")
    print(f"   Sector: {most_volatile['Crop']}")
    print(f"   Std Dev: {most_volatile['Volatility']:.2f}")

    df.drop(columns=['Volatility'], inplace=True)

def analyze_dataset_5(df):
    """
    Analyzes Dataset 5 (Time Series).
    Finds the highest production value ever recorded in the dataset.
    """
    print("\n---  Analysis Report for Dataset 5 (Time Series) ---")

    # 1. Identify Year Columns (they start with 'Year_')
    year_cols = [col for col in df.columns if 'Year_' in col]

    # 2. Find the All-Time Highest Value
    # We look at the subset of year columns
    # We use max() to find the highest number in the entire table subset
    max_val = df[year_cols].max().max()

    # Find the row and column where this maximum happened
    # stack() turns the table into a long list so we can find the exact spot
    stacked = df[year_cols].stack()
    idx, col = stacked.idxmax()

    # Get the name of the Particular
    particular_name = df.loc[idx, 'Particulars']
    year_name = col.replace('Year_', '')

    print("\n[1] All-Time Highest Record:")
    print(f"   Category: {particular_name}")
    print(f"   Value:    {max_val}")
    print(f"   Year:     {year_name}")

    # 3. Identify the Worst Year (Biggest Drop in Total Production)
    # First, calculate Total Production per year (sum of all rows)
    yearly_totals = df[year_cols].sum()

    # Calculate difference from previous year
    yearly_changes = yearly_totals.diff()

    # Find the year with the biggest negative number (Drop)
    worst_year_col = yearly_changes.idxmin()
    drop_amount = yearly_changes.min()

    year_name = worst_year_col.replace('Year_', '')

    print("\n[2] Year with Biggest Production Drop:")
    print(f"   Year: {year_name}")
    print(f"   Drop: {drop_amount:.2f} Units")


# --- Visualization ---
def plot_dataset_1(df):
    """
    Creates visualizations for Dataset 1:
    1. Bar Chart: Cost of Cultivation by Crop
    2. Scatter Plot: Cost vs. Yield
    """
    print("\n---  Plotting Dataset 1 Visualizations ---")

    # Chart 1: Cost of Cultivation by Crop
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='Crop', y='Cost_C2',hue='Crop', legend=False, palette='viridis')
    plt.title('Average Cost of Cultivation (C2) by Crop', fontsize=16)
    plt.xlabel('Crop Name', fontsize=12)
    plt.ylabel('Cost (Rs/Hectare)', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('Dataset1_Cost_by_Crop.png')
    print("   -> Saved 'Dataset1_Cost_by_Crop.png'")
    plt.close()  # Close the plot to clear memory

    # Chart 2: State-wise Yield Comparison (Top 10 Records)
    # We pick the top 10 entries with the highest yield to keep the chart readable
    top_yields = df.sort_values(by='Yield', ascending=False).head(10)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_yields, x='State', y='Yield', hue='Crop', palette='viridis')
    plt.title('Top 10 High-Yielding States & Crops', fontsize=16)
    plt.xlabel('State', fontsize=12)
    plt.ylabel('Yield (Quintal/Hectare)', fontsize=12)
    plt.legend(title='Crop')
    plt.tight_layout()
    plt.savefig('Dataset1_State_Yield.png')
    print("   -> Saved 'Dataset1_State_Yield.png'")
    plt.close()

def plot_dataset_2(df):
    """
    Plots Trends (All Years) for Production, Area, and Yield.
    Selects Top 3 and Bottom 3 based on their ALL-TIME Highest value.
    """
    metrics = ['Production', 'Area', 'Yield']

    print("\n---  Plotting Top 3 & Bottom 3 Trends (All-Time) ---")

    for metric in metrics:
        # 1. Identify columns for this metric
        metric_cols = [col for col in df.columns if metric in col]

        if not metric_cols:
            continue

        # 2. Calculate "All-Time Max" for each crop
        # We create a temporary column to sort by
        # max(axis=1) finds the highest number in the row across all years
        df['All_Time_Max'] = df[metric_cols].max(axis=1)

        # 3. Sort Descending (Big -> Small) based on All-Time Max
        df_sorted = df.sort_values(by='All_Time_Max', ascending=False)

        # Top 3
        top_3_df = df_sorted.head(3)

        # Bottom 3 (Filter out 0s so we don't get empty crops)
        # We want crops that have at least SOME activity (> 1.0)
        df_non_zero = df_sorted[df_sorted['All_Time_Max'] > 1.0]
        bottom_3_df = df_non_zero.tail(3)

        # --- Inner Function to Draw the Chart ---
        def create_chart(sub_df, label):
            # Filter columns: Crop + Metric Columns
            subset = sub_df[['Crop'] + metric_cols].copy()

            # Melt (Wide -> Long)
            melted = subset.melt(id_vars='Crop', var_name='Year', value_name=metric)

            # Clean Year Column using simple split (No Regex)
            # "Production_2006_07" -> "2006-07"
            melted['Year'] = melted['Year'].apply(
                lambda x: x.split('_')[-2] + '-' + x.split('_')[-1] if '_' in str(x) else x)

            plt.figure(figsize=(10, 6))

            sns.lineplot(data=melted, x='Year', y=metric, hue='Crop', marker='o', palette='bright')

            plt.title(f'{label} Crops (All-Time): {metric} Trend', fontsize=16)
            plt.xlabel('Year', fontsize=12)
            plt.ylabel(metric, fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend(title='Crop')
            plt.tight_layout()

            # Save File
            filename = f'Dataset2_{metric}_{label.replace(" ", "")}.png'
            plt.savefig(filename)
            print(f"   -> Saved '{filename}'")
            plt.close()

        # 4. Generate the charts
        create_chart(top_3_df, "Top 3")
        create_chart(bottom_3_df, "Bottom 3")

        # Drop the temp column to keep df clean
        df.drop(columns=['All_Time_Max'], inplace=True)

def plot_dataset_3(df):
    """
    Visualizes Dataset 3:
    Bar Chart showing the Number of Varieties per Crop.
    """
    print("\n---  Plotting Dataset 3 Visualizations ---")

    # 1. Count the varieties for each crop
    # We create a new mini-dataframe just for plotting
    plot_data = df['Crop'].value_counts().reset_index()
    plot_data.columns = ['Crop', 'Variety_Count']

    # 2. Plot
    plt.figure(figsize=(12, 6))

    # We use 'barplot' to show the counts
    sns.barplot(data=plot_data, x='Crop', y='Variety_Count', hue='Crop', legend=False, palette='icefire')

    plt.title('Number of Varieties Registered per Crop', fontsize=16)
    plt.xlabel('Crop Name', fontsize=12)
    plt.ylabel('Number of Varieties', fontsize=12)
    plt.xticks(rotation=45, ha='right')  # Rotate labels to fit them all
    plt.tight_layout()

    plt.savefig('Dataset3_Variety_Counts.png')
    print("   -> Saved 'Dataset3_Variety_Counts.png'")
    plt.close()

def plot_dataset_4(df):
    """
    Visualizes Dataset 4:
    1. Line Chart of Trends for All Sectors.
    2. Bar Chart of Total Growth.
    """
    print("\n---  Plotting Dataset 4 Visualizations ---")

    # Melt Data for Line Chart
    # We want columns that start with "Year_"
    year_cols = [col for col in df.columns if 'Year_' in col]

    # Create subset and melt
    df_melted = df[['Crop'] + year_cols].melt(id_vars='Crop', var_name='Year', value_name='Index_Value')

    # Clean Year text: "Year_2004_05" -> "2004-05"
    df_melted['Year'] = df_melted['Year'].str.replace('Year_', '').str.replace('_', '-')

    # --- Chart 1: Trend Line Chart (All Sectors) ---
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_melted, x='Year', y='Index_Value', hue='Crop', marker='o', palette='tab10')

    plt.title('Trends in Agricultural Production Indices (2004-2012)', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Index Value (Base 2004=100)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Sector')  # Legend outside
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('Dataset4_Trends.png')
    print("   -> Saved 'Dataset4_Trends.png'")
    plt.close()

    # --- Chart 2: Total Growth Bar Chart ---
    # Compare First Year vs Last Year
    first_year = year_cols[0]
    last_year = year_cols[-1]

    # Calculate Growth again for plotting
    df['Growth'] = df[last_year] - df[first_year]
    df_sorted = df.sort_values(by='Growth', ascending=False)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_sorted, x='Crop', y='Growth', hue='Crop', legend=False,  palette='viridis')

    plt.title('Total Index Growth (2004 to 2012)', fontsize=16)
    plt.xlabel('Sector', fontsize=12)
    plt.ylabel('Growth Points (Index)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('Dataset4_Growth_Bar.png')
    print("   -> Saved 'Dataset4_Growth_Bar.png'")
    plt.close()

    # Remove temp column
    df.drop(columns=['Growth'], inplace=True)

def plot_dataset_5(df):
    """
    Visualizes Dataset 5:
    Line Chart of the Top 5 Categories (by Average Value) over the years.
    """
    print("\n---  Plotting Dataset 5 Visualizations ---")

    # 1. Identify Year Columns
    year_cols = [col for col in df.columns if 'Year_' in col]

    # 2. Find Top 5 Categories by Average Value
    # We calculate the mean across all years for each row
    df['Average_Value'] = df[year_cols].mean(axis=1)

    # Sort and pick top 5
    top_5 = df.sort_values(by='Average_Value', ascending=False).head(5)

    # 3. Melt for Plotting
    # We only melt the Top 5 rows
    df_melted = top_5.melt(id_vars='Particulars', value_vars=year_cols, var_name='Year', value_name='Value')

    # Clean Year text: "Year_1993" -> "1993"
    df_melted['Year'] = df_melted['Year'].str.replace('Year_', '')

    # 4. Create Line Chart
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_melted, x='Year', y='Value', hue='Particulars', marker='o', palette='magma')

    plt.title('Trend of Top 5 Agricultural Categories (1993-2014)', fontsize=16)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Production Volume', fontsize=12)

    # Rotate x-axis labels because there are many years
    plt.xticks(rotation=45)

    # Move legend outside
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Category')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig('Dataset5_Trends.png')
    print("   -> Saved 'Dataset5_Trends.png'")
    plt.close()

    # Clean up temp column
    if 'Average_Value' in df.columns:
        df.drop(columns=['Average_Value'], inplace=True)



# ==========================================
# 3. Core Data Processing Functions
# ==========================================

def load_data(file_paths):
    """Loads all CSV files into a dictionary of pandas DataFrames."""
    dataframes = {}
    print("--- 1. Loading Data ---")
    for key, path in file_paths.items():
        try:
            dataframes[key] = pd.read_csv(path)
            print(f"Loaded {path} as {key} (Rows: {len(dataframes[key])})")
        except FileNotFoundError:
            print(f"ERROR: File not found at {path}. Skipping.")
    return dataframes

def inspect_and_clean_data(dataframes):
    """
    Performs initial inspection and applies cleaning logic.
    """
    print("\n--- 2. Data Inspection and Cleaning ---")
    cleaned_dataframes = {}

    for name, df in dataframes.items():
        print(f"\n===== Processing: {name} =====")

        # --- A. General Cleaning (Applies to ALL files) ---
        # 1. Strip extra spaces from column names (e.g. "State " -> "State")
        df.columns = df.columns.str.strip()

        # 2. Drop duplicate rows if any exist
        df = df.drop_duplicates()

        # --- B. Specific Cleaning (Applies to specific files) ---
        if name == 'df1':
            print("   -> Applying custom cleaning for df1...")
            df = clean_dataset_1(df)

        elif name == 'df2':
            print("   -> Applying custom cleaning for df2...")
            df = clean_dataset_2(df)

        elif name == 'df3':
            print("   -> Applying custom cleaning for df3...")
            df = clean_dataset_3(df)

        elif name == 'df4':
            print("   -> Applying custom cleaning for df4...")
            df = clean_dataset_4(df)

        elif name == 'df5':
            print("   -> Applying custom cleaning for df5...")
            df = clean_dataset_5(df)

        # --- C. Inspection Summary ---
        # Print missing values to help us decide next steps
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if not missing.empty:
            print(f"   -> Warning: Missing values found:\n{missing}")
        else:
            print("   -> No missing values.")

        # Save the cleaned dataframe
        cleaned_dataframes[name] = df
        print(f"   -> Final Columns: {list(df.columns)}")

    return cleaned_dataframes


# ==========================================
# 4. Main Execution Block
# ==========================================

if __name__ == "__main__":
    # Define file paths
    # (Using raw strings r'' helps avoid errors with backslashes on Windows)
    FILE_PATHS = {
        'df1': r'crop_production\datafile_1.csv',
        'df2': r'crop_production\datafile_2.csv',
        'df3': r'crop_production\datafile_3.csv',
        'df4': r'crop_production\datafile_4.csv',
        'df5': r'crop_production\datafile_5.csv',
    }

    # 1. Load Data
    raw_data = load_data(FILE_PATHS)

    # 2. Inspect and Clean Data
    cleaned_data = inspect_and_clean_data(raw_data)

    # 3. Verify Cleaned Dataframes
    if 'df1' in cleaned_data:
        print("\n--- Preview of Cleaned df1 ---")
        print(cleaned_data['df1'].head())

    if 'df2' in cleaned_data:
        print("\n--- Preview of Cleaned df2 ---")
        print(cleaned_data['df2'].head())

    if 'df3' in cleaned_data:
        print("\n--- Preview of Cleaned df3 ---")
        print(cleaned_data['df3'].head())

    if 'df4' in cleaned_data:
        print("\n--- Preview of Cleaned df4 ---")
        print(cleaned_data['df4'].head())

    if 'df5' in cleaned_data:
        print("\n--- Preview of Cleaned df5 ---")
        print(cleaned_data['df5'].head())

    # 4. Run Analysis and Visualization
    if 'df1' in cleaned_data:
        analyze_dataset_1(cleaned_data['df1'])
        plot_dataset_1(cleaned_data['df1'])

    if 'df2' in cleaned_data:
        analyze_dataset_2(cleaned_data['df2'])
        plot_dataset_2(cleaned_data['df2'])

    if 'df3' in cleaned_data:
        analyze_dataset_3(cleaned_data['df3'])
        plot_dataset_3(cleaned_data['df3'])

    if 'df4' in cleaned_data:
        analyze_dataset_4(cleaned_data['df4'])
        plot_dataset_4(cleaned_data['df4'])

    if 'df5' in cleaned_data:
        analyze_dataset_5(cleaned_data['df5'])
        plot_dataset_5(cleaned_data['df5'])