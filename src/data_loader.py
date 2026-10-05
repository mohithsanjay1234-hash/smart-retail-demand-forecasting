import os
import glob
import pandas as pd
import numpy as np

def load_and_clean_branch_data(raw_data_dir=None):
    """
    Data Engineering Pipeline (Unit 1):
    Ingests raw sales files from multiple Vizag supermarket branches (.xlsx, .csv),
    standardizes schema variations, handles missing/corrupted values, and outputs a clean unified DataFrame.
    """
    if raw_data_dir is None:
        raw_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')

    cleaned_dfs = []
    
    # Check for raw files
    excel_files = glob.glob(os.path.join(raw_data_dir, "*.xlsx")) + glob.glob(os.path.join(raw_data_dir, "*.xls"))
    csv_files = glob.glob(os.path.join(raw_data_dir, "*.csv"))

    all_file_paths = excel_files + csv_files

    if not all_file_paths:
        raise FileNotFoundError(f"No raw files (.xlsx, .csv) found in {raw_data_dir}. Run generate_sample_data.py first!")

    for file_path in all_file_paths:
        file_name = os.path.basename(file_path)
        
        if file_path.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(file_path)
        else:
            df_raw = pd.read_csv(file_path)

        # Standardize column mappings dynamically
        column_mapping = {
            # Date mappings
            "Txn_Date": "date", "POS_Timestamp": "date", "Date": "date",
            # Branch mappings
            "Branch_Name": "branch_name", "Store_Location": "branch_name", "Branch": "branch_name",
            # Product ID mappings
            "Product_ID": "product_id", "SKU_Code": "product_id", "Prod_ID": "product_id",
            # Product Name mappings
            "Item_Description": "product_name", "Product_Name": "product_name", "Item_Name": "product_name",
            # Category mappings
            "Category": "category", "Dept_Category": "category",
            # Item type mappings
            "Item_Type": "item_type", "Classification": "item_type", "Product_Type": "item_type",
            # Price mappings
            "Unit_Price_INR": "unit_price", "MRP": "unit_price", "Price": "unit_price",
            # Quantity mappings
            "Quantity_Sold": "quantity_sold", "Units_Out": "quantity_sold", "Qty_Sold": "quantity_sold",
            # Stock mappings
            "Current_Stock_Units": "current_stock", "Inventory_Level": "current_stock", "Available_Stock": "current_stock",
            # Shelf life mappings
            "Shelf_Life_Days": "shelf_life_days", "Expiry_Window": "shelf_life_days", "Max_Shelf_Days": "shelf_life_days"
        }

        # Rename matching columns
        df_clean = df_raw.rename(columns=column_mapping)
        
        # Ensure all required standardized columns exist
        required_cols = [
            'date', 'branch_name', 'product_id', 'product_name', 
            'category', 'item_type', 'unit_price', 'quantity_sold', 
            'current_stock', 'shelf_life_days'
        ]

        # Convert date to standard datetime format
        df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')

        # Clean numerical columns
        df_clean['quantity_sold'] = pd.to_numeric(df_clean['quantity_sold'], errors='coerce')
        df_clean['unit_price'] = pd.to_numeric(df_clean['unit_price'], errors='coerce')
        df_clean['current_stock'] = pd.to_numeric(df_clean['current_stock'], errors='coerce')
        df_clean['shelf_life_days'] = pd.to_numeric(df_clean['shelf_life_days'], errors='coerce')

        # Remove invalid prices or negative values
        df_clean = df_clean[df_clean['unit_price'] > 0]
        
        # Fill missing quantity with median for that product
        df_clean['quantity_sold'] = df_clean.groupby('product_id')['quantity_sold'].transform(
            lambda x: x.fillna(x.median())
        ).fillna(1)

        # Calculate Total Revenue
        df_clean['revenue'] = df_clean['quantity_sold'] * df_clean['unit_price']

        cleaned_dfs.append(df_clean[required_cols + ['revenue']])

    # Combine all cleaned branch datasets
    unified_df = pd.concat(cleaned_dfs, ignore_index=True)
    unified_df.sort_values(by=['date', 'branch_name', 'product_id'], inplace=True)
    
    # Save processed CSV
    processed_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)
    unified_path = os.path.join(processed_dir, 'unified_sales_data.csv')
    unified_df.to_csv(unified_path, index=False)

    return unified_df

if __name__ == "__main__":
    df = load_and_clean_branch_data()
    print(f"[DATA PIPELINE COMPLETE] Cleaned & unified {len(df)} records across Vizag branches.")
