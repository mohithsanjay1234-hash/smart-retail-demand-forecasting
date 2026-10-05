import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def forecast_next_week_demand(df, branch_name="All Branches", forecast_method="Weighted Moving Average", festival_multiplier=1.0):
    """
    Demand Forecasting Engine (Intro to DS Unit 1 / Python Unit 1):
    Predicts next 7-day demand for each product per branch based on historical transaction logs.
    
    Methods available:
    - Simple Moving Average (SMA - 7 days)
    - Weighted Moving Average (WMA - higher weight to recent days)
    - Exponential Smoothing (EMA)
    """
    if df.empty:
        return pd.DataFrame()

    # Filter by branch if specified
    if branch_name != "All Branches":
        filtered_df = df[df['branch_name'] == branch_name].copy()
    else:
        filtered_df = df.copy()

    latest_date = filtered_df['date'].max()
    last_7_days = latest_date - timedelta(days=7)
    last_14_days = latest_date - timedelta(days=14)
    last_30_days = latest_date - timedelta(days=30)

    # Group by product
    product_summary = []
    
    grouped = filtered_df.groupby(['product_id', 'product_name', 'category', 'item_type', 'shelf_life_days', 'unit_price'])

    for (p_id, p_name, category, item_type, shelf_life, unit_price), group in grouped:
        group_sorted = group.sort_values(by='date')
        
        # Latest current stock
        latest_record = group_sorted.iloc[-1]
        curr_stock = int(latest_record['current_stock'])
        branch = latest_record['branch_name'] if branch_name != "All Branches" else "All Branches"

        # Historical metrics
        recent_7 = group_sorted[group_sorted['date'] > last_7_days]['quantity_sold']
        recent_14 = group_sorted[group_sorted['date'] > last_14_days]['quantity_sold']
        recent_30 = group_sorted[group_sorted['date'] > last_30_days]['quantity_sold']

        sma_7 = recent_7.mean() if len(recent_7) > 0 else group_sorted['quantity_sold'].mean()
        sma_14 = recent_14.mean() if len(recent_14) > 0 else sma_7
        sma_30 = recent_30.mean() if len(recent_30) > 0 else sma_14

        # Weighted Moving Average calculation
        if len(recent_7) >= 7:
            weights = np.array([1, 2, 3, 4, 5, 6, 7])
            wma = np.sum(recent_7.values[-7:] * weights) / np.sum(weights)
        else:
            wma = sma_7

        # Exponential Smoothing calculation
        ema = group_sorted['quantity_sold'].ewm(span=7, adjust=False).mean().iloc[-1]

        # Select predicted daily demand based on algorithm choice
        if forecast_method == "Simple Moving Average (7D)":
            base_daily_pred = sma_7
        elif forecast_method == "Exponential Smoothing":
            base_daily_pred = ema
        else: # Weighted Moving Average
            base_daily_pred = wma

        # Apply festival / scenario multiplier
        adjusted_daily_pred = base_daily_pred * festival_multiplier
        
        # Predict 7-day total demand
        predicted_7d_demand = int(np.round(adjusted_daily_pred * 7))

        # Reorder level calculation (Safety Stock = 2 days of avg demand)
        safety_stock = int(np.ceil(adjusted_daily_pred * 2))
        reorder_point = predicted_7d_demand + safety_stock
        suggested_reorder_qty = max(0, reorder_point - curr_stock)

        product_summary.append({
            "Branch": branch,
            "Product ID": p_id,
            "Product Name": p_name,
            "Category": category,
            "Item Type": item_type,
            "Unit Price (₹)": unit_price,
            "Current Stock": curr_stock,
            "Avg Daily Sales (30D)": round(sma_30, 1),
            "Predicted Daily Sales": round(adjusted_daily_pred, 1),
            "Predicted 7-Day Demand": predicted_7d_demand,
            "Safety Stock Needed": safety_stock,
            "Suggested Reorder Qty": suggested_reorder_qty,
            "Shelf Life (Days)": shelf_life
        })

    forecast_df = pd.DataFrame(product_summary)
    return forecast_df
