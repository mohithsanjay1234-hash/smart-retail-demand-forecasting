import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'retail_store.db')

def get_connection():
    """Establish connection to SQLite DB (Simulates MySQL Relational Database for Unit 1)."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_database(df_unified):
    """
    Creates sales_records table and loads unified cleaned data into SQLite database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create table schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            branch_name TEXT,
            product_id TEXT,
            product_name TEXT,
            category TEXT,
            item_type TEXT,
            unit_price REAL,
            quantity_sold INTEGER,
            current_stock INTEGER,
            shelf_life_days INTEGER,
            revenue REAL
        )
    ''')
    
    # Clear old data and insert current clean dataset
    cursor.execute("DELETE FROM sales_records")
    
    # Copy DataFrame to sql
    df_unified.to_sql('sales_records', conn, if_exists='append', index=False)
    
    conn.commit()
    conn.close()
    print(f"[DATABASE] Successfully loaded {len(df_unified)} records into SQLite database ({DB_PATH}).")

def query_sales_by_branch(branch_name=None):
    """Query data from SQLite database."""
    conn = get_connection()
    if branch_name and branch_name != "All Branches":
        query = "SELECT * FROM sales_records WHERE branch_name = ?"
        df = pd.read_sql_query(query, conn, params=(branch_name,))
    else:
        query = "SELECT * FROM sales_records"
        df = pd.read_sql_query(query, conn)
    conn.close()
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df
