import pandas as pd

def generate_inventory_alerts(forecast_df):
    """
    Business Rules & Inventory Risk Engine:
    Evaluates forecasted demand against current store inventory levels to detect:
    1. UNDERSTOCKING / STOCKOUT RISK (especially for Fast-Moving Goods)
    2. OVERSTOCKING / SPOILAGE RISK (especially for Perishables with short shelf life)
    3. OPTIMAL STOCK STATUS
    """
    if forecast_df.empty:
        return forecast_df

    alerts = []
    risk_level = []
    recommended_action = []

    for _, row in forecast_df.iterrows():
        curr_stock = row['Current Stock']
        pred_demand = row['Predicted 7-Day Demand']
        item_type = row['Item Type']
        shelf_life = row['Shelf Life (Days)']
        reorder_qty = row['Suggested Reorder Qty']

        # Rule 1: High Risk Stockout (Understocking)
        if curr_stock < (pred_demand * 0.5):
            alerts.append("CRITICAL: Understock Risk")
            risk_level.append("HIGH RISK - STOCKOUT")
            if item_type == "Fast-Moving Goods":
                recommended_action.append(f"🚨 Immediate Emergency Restock: Order {reorder_qty} units to prevent sales loss.")
            else:
                recommended_action.append(f"⚠️ Restock Immediately: Order {reorder_qty} units.")

        # Rule 2: Low Stock Warning
        elif curr_stock < pred_demand:
            alerts.append("WARNING: Moderate Low Stock")
            risk_level.append("MEDIUM RISK")
            recommended_action.append(f"📦 Place Regular Reorder: Order {reorder_qty} units.")

        # Rule 3: High Overstocking & Spoilage Risk for Perishables
        elif curr_stock > (pred_demand * 2.0) and item_type == "Perishable":
            alerts.append("DANGER: Overstock & Spoilage Risk")
            risk_level.append("HIGH RISK - PERISHABLE WASTE")
            recommended_action.append(f"💸 Overstocked! Perishable items will expire in {shelf_life} days. Offer 15-25% discount or bundle offer.")

        # Rule 4: Mild Excess Stock
        elif curr_stock > (pred_demand * 2.2):
            alerts.append("NOTICE: Excess Stock")
            risk_level.append("LOW RISK - EXCESS HOLDING")
            recommended_action.append("Hold replenishment orders for next cycle. Promote via end-cap display.")

        # Rule 5: Optimal Inventory
        else:
            alerts.append("HEALTHY: Optimal Stock Level")
            risk_level.append("OPTIMAL")
            recommended_action.append("Maintain current inventory levels.")

    df_alerts = forecast_df.copy()
    df_alerts['Stock Alert Status'] = alerts
    df_alerts['Risk Level'] = risk_level
    df_alerts['Recommended Action'] = recommended_action

    return df_alerts
