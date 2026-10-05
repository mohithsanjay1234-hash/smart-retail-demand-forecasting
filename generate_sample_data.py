import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_mock_datasets():
    """
    Generates realistic 90-day sales data for 3 branches of Vizag Superstores.
    Simulates real-world data engineering challenges:
    - Multiple file formats (.xlsx, .csv)
    - Inconsistent column names across source systems (POS vs ERP)
    - Missing values and dirty data snippets
    """
    data_dir = os.path.join(os.path.dirname(__file__), 'data', 'raw')
    os.makedirs(data_dir, exist_ok=True)
    
    np.random.seed(42)
    start_date = datetime.now() - timedelta(days=90)
    dates = [start_date + timedelta(days=i) for i in range(90)]
    
    products = [
        # Perishables (high risk of waste/spoilage)
        {"id": "P101", "name": "Jersey Fresh Milk 1L", "category": "Dairy", "type": "Perishable", "price": 60, "shelf_life_days": 3},
        {"id": "P102", "name": "Heritage Curd 500g", "category": "Dairy", "type": "Perishable", "price": 40, "shelf_life_days": 5},
        {"id": "P103", "name": "Fresh Paneer 200g", "category": "Dairy", "type": "Perishable", "price": 110, "shelf_life_days": 7},
        {"id": "P104", "name": "Local Hybrid Tomatoes 1kg", "category": "Produce", "type": "Perishable", "price": 35, "shelf_life_days": 4},
        {"id": "P105", "name": "Fresh Spinach Bunch", "category": "Produce", "type": "Perishable", "price": 20, "shelf_life_days": 2},
        {"id": "P106", "name": "Modern Brown Bread 400g", "category": "Bakery", "type": "Perishable", "price": 45, "shelf_life_days": 4},
        
        # Fast-Moving Goods (high risk of stockouts)
        {"id": "F201", "name": "Sona Masoori Rice 10kg", "category": "Staples", "type": "Fast-Moving Goods", "price": 550, "shelf_life_days": 180},
        {"id": "F202", "name": "Freedom Sunflower Oil 1L", "category": "Staples", "type": "Fast-Moving Goods", "price": 135, "shelf_life_days": 180},
        {"id": "F203", "name": "Tata Tea Gold 500g", "category": "Beverages", "type": "Fast-Moving Goods", "price": 280, "shelf_life_days": 365},
        {"id": "F204", "name": "Maggi Masala Noodles 4-Pack", "category": "Packaged Food", "type": "Fast-Moving Goods", "price": 56, "shelf_life_days": 180},
        {"id": "F205", "name": "Surf Excel Easy Wash 1kg", "category": "Household", "type": "Fast-Moving Goods", "price": 140, "shelf_life_days": 365},
        {"id": "F206", "name": "Good Knight Gold Flash Refill", "category": "Household", "type": "Fast-Moving Goods", "price": 85, "shelf_life_days": 365},
    ]

    # --- Branch 1: MVP Colony (Excel format, ERP naming) ---
    b1_records = []
    for d in dates:
        # Weekend sales boost
        is_weekend = d.weekday() >= 5
        multiplier = 1.35 if is_weekend else 1.0
        
        for p in products:
            base_sales = np.random.randint(15, 50) if p["type"] == "Perishable" else np.random.randint(10, 35)
            qty = max(1, int(base_sales * multiplier + np.random.normal(0, 3)))
            
            # Stock levels simulation
            curr_stock = int(qty * np.random.uniform(0.8, 2.5))
            
            b1_records.append({
                "Txn_Date": d.strftime("%Y-%m-%d"),
                "Branch_Name": "MVP Colony",
                "Product_ID": p["id"],
                "Item_Description": p["name"],
                "Category": p["category"],
                "Item_Type": p["type"],
                "Unit_Price_INR": p["price"],
                "Quantity_Sold": qty,
                "Current_Stock_Units": curr_stock,
                "Shelf_Life_Days": p["shelf_life_days"]
            })
            
    df_b1 = pd.DataFrame(b1_records)
    # Inject a few dirty rows for data engineering cleaning practice
    df_b1.loc[12, "Quantity_Sold"] = np.nan
    df_b1.loc[45, "Unit_Price_INR"] = -10  # outlier / error
    b1_path = os.path.join(data_dir, "branch1_mvp_colony.xlsx")
    df_b1.to_excel(b1_path, index=False)

    # --- Branch 2: Gajuwaka POS Machine (CSV format, POS machine format) ---
    b2_records = []
    for d in dates:
        is_weekend = d.weekday() >= 5
        multiplier = 1.4 if is_weekend else 1.0
        
        for p in products:
            base_sales = np.random.randint(20, 60) if p["type"] == "Fast-Moving Goods" else np.random.randint(10, 30)
            qty = max(1, int(base_sales * multiplier + np.random.normal(0, 4)))
            curr_stock = int(qty * np.random.uniform(0.6, 2.0))
            
            b2_records.append({
                "POS_Timestamp": d.strftime("%d/%m/%Y"), # different date format
                "Store_Location": "Gajuwaka Industrial Hub",
                "SKU_Code": p["id"],
                "Product_Name": p["name"],
                "Dept_Category": p["category"],
                "Classification": p["type"],
                "MRP": p["price"],
                "Units_Out": qty,
                "Inventory_Level": curr_stock,
                "Expiry_Window": p["shelf_life_days"]
            })
            
    df_b2 = pd.DataFrame(b2_records)
    b2_path = os.path.join(data_dir, "branch2_gajuwaka_pos.csv")
    df_b2.to_csv(b2_path, index=False)

    # --- Branch 3: Siripuram (CSV format, Cloud System export) ---
    b3_records = []
    for d in dates:
        is_weekend = d.weekday() >= 5
        multiplier = 1.25 if is_weekend else 1.0
        
        for p in products:
            base_sales = np.random.randint(12, 45)
            qty = max(1, int(base_sales * multiplier + np.random.normal(0, 2)))
            curr_stock = int(qty * np.random.uniform(0.7, 2.2))
            
            b3_records.append({
                "Date": d.strftime("%Y/%m/%d"),
                "Branch": "Siripuram Junction",
                "Prod_ID": p["id"],
                "Item_Name": p["name"],
                "Category": p["category"],
                "Product_Type": p["type"],
                "Price": p["price"],
                "Qty_Sold": qty,
                "Available_Stock": curr_stock,
                "Max_Shelf_Days": p["shelf_life_days"]
            })
            
    df_b3 = pd.DataFrame(b3_records)
    b3_path = os.path.join(data_dir, "branch3_siripuram.csv")
    df_b3.to_csv(b3_path, index=False)

    print(f"[SUCCESS] Generated sample raw datasets:")
    print(f" - {b1_path}")
    print(f" - {b2_path}")
    print(f" - {b3_path}")

if __name__ == "__main__":
    generate_mock_datasets()
