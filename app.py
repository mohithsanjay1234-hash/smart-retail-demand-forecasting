import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import custom modules
from src.data_loader import load_and_clean_branch_data
from src.database import initialize_database, query_sales_by_branch
from src.forecasting import forecast_next_week_demand
from src.alerts import generate_inventory_alerts

# --- Page Config ---
st.set_page_config(
    page_title="Smart Retail Demand Forecasting - Vizag Superstores",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e2640 0%, #0f172a 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 1.8rem;
        color: #f8fafc;
        font-weight: 700;
    }
    .badge-critical {
        background-color: #7f1d1d;
        color: #fca5a5;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-warning {
        background-color: #78350f;
        color: #fde68a;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-healthy {
        background-color: #064e3b;
        color: #6ee7b7;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def get_processed_data():
    raw_dir = os.path.join(os.path.dirname(__file__), 'data', 'raw')
    if not os.path.exists(os.path.join(raw_dir, "branch1_mvp_colony.xlsx")):
        from generate_sample_data import generate_mock_datasets
        generate_mock_datasets()
    df_clean = load_and_clean_branch_data()
    initialize_database(df_clean)
    return df_clean

# Load pipeline data
try:
    df_sales = get_processed_data()
except Exception as e:
    st.error(f"Error initializing data pipeline: {e}")
    st.stop()

# --- Sidebar ---
st.sidebar.image("https://img.icons8.com/isometric/96/shopping-cart.png", width=70)
st.sidebar.title("Vizag Retail Superstores")
st.sidebar.caption("Smart Retail Demand Forecasting System")
st.sidebar.markdown("---")

navigation = st.sidebar.radio(
    "Navigation Menu",
    [
        "🏠 Executive Overview",
        "🔄 Data Engineering & Ingestion",
        "📊 Exploratory Data Analysis (EDA)",
        "🔮 Demand Forecast & Restocking Alerts",
        "🧪 Festival Scenario Simulator",
        "🎓 JNTUK Syllabus & Charter"
    ]
)

st.sidebar.markdown("---")
selected_branch = st.sidebar.selectbox(
    "Select Branch Location",
    ["All Branches", "MVP Colony", "Gajuwaka Industrial Hub", "Siripuram Junction"]
)

# Filter dataset by selected branch
df_filtered = query_sales_by_branch(selected_branch)

# --- 1. EXECUTIVE OVERVIEW ---
if navigation == "🏠 Executive Overview":
    st.title("🛒 Smart Retail Demand Forecasting System")
    st.caption("Vizag Supermarket Chain • Perishable & Fast-Moving Goods Inventory Optimization")
    
    st.markdown("""
    > **Industry Problem Statement**: Vizag Superstores lost significant revenue annually due to **overstocking perishable items** (spoilage risk) and **understocking fast-moving consumer goods** (lost sales). Sales data was fragmented across Excel files (MVP Colony), POS terminals (Gajuwaka), and cloud CSVs (Siripuram).
    """)

    # Top KPI Metrics
    total_rev = df_filtered['revenue'].sum()
    total_units = df_filtered['quantity_sold'].sum()
    total_txns = len(df_filtered)
    
    # Calculate stock alerts
    forecast_df = forecast_next_week_demand(df_filtered, branch_name=selected_branch)
    alert_df = generate_inventory_alerts(forecast_df)
    
    critical_understock = len(alert_df[alert_df['Risk Level'] == 'HIGH RISK - STOCKOUT'])
    overstock_perishable = len(alert_df[alert_df['Risk Level'] == 'HIGH RISK - PERISHABLE WASTE'])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Revenue</div>
            <div class="metric-value">₹{total_rev:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Quantity Sold</div>
            <div class="metric-value">{total_units:,} units</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">🚨 Stockout Alerts (FMCG)</div>
            <div class="metric-value" style="color: #ef4444;">{critical_understock} Products</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">💸 Overstock Alerts (Perishables)</div>
            <div class="metric-value" style="color: #f59e0b;">{overstock_perishable} Products</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📈 Demand Trend & Inventory Health Overview")
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        # Revenue by category
        cat_rev = df_filtered.groupby(['category', 'item_type'])['revenue'].sum().reset_index()
        fig_cat = px.bar(
            cat_rev, x='category', y='revenue', color='item_type',
            title="Revenue Contribution by Category (Perishable vs FMCG)",
            labels={'revenue': 'Revenue (₹)', 'category': 'Product Category'},
            template="plotly_dark",
            color_discrete_map={'Perishable': '#f87171', 'Fast-Moving Goods': '#38bdf8'}
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_chart2:
        # Branch Revenue comparison
        branch_rev = df_sales.groupby('branch_name')['revenue'].sum().reset_index()
        fig_branch = px.pie(
            branch_rev, values='revenue', names='branch_name',
            title="Sales Contribution Across Vizag Branches",
            hole=0.4,
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_branch, use_container_width=True)

    st.markdown("### 🚨 Urgent Action Items for Next Week")
    high_priority = alert_df[alert_df['Risk Level'].str.contains('HIGH RISK')]
    if not high_priority.empty:
        st.dataframe(
            high_priority[['Branch', 'Product Name', 'Item Type', 'Current Stock', 'Predicted 7-Day Demand', 'Suggested Reorder Qty', 'Risk Level', 'Recommended Action']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("All inventory levels are currently in a healthy state!")

# --- 2. DATA ENGINEERING & INGESTION ---
elif navigation == "🔄 Data Engineering & Ingestion":
    st.title("🔄 Multi-Source Data Ingestion & ETL Pipeline")
    st.caption("JNTUK Data Engineering Unit 1 • Python Unit 1 Data Ingestion")
    
    st.markdown("""
    In real-world retail chains, data is rarely uniform. Here, raw sales data originates from 3 distinct systems across Vizag:
    - **Branch 1 (MVP Colony)**: ERP export in `.xlsx` format (custom headers `Txn_Date`, `Unit_Price_INR`).
    - **Branch 2 (Gajuwaka Industrial Hub)**: POS Terminal export in `.csv` format (`POS_Timestamp`, `Units_Out`).
    - **Branch 3 (Siripuram Junction)**: Cloud database CSV (`Date`, `Qty_Sold`).
    """)

    tab1, tab2, tab3 = st.tabs(["📂 Inspect Raw Sources", "⚙️ Data Cleaning & ETL Rules", "🗄️ Unified SQLite DB View"])
    
    with tab1:
        raw_dir = os.path.join(os.path.dirname(__file__), 'data', 'raw')
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.markdown("#### 📄 MVP Colony (`.xlsx`)")
            df_b1_raw = pd.read_excel(os.path.join(raw_dir, "branch1_mvp_colony.xlsx"))
            st.dataframe(df_b1_raw.head(5), use_container_width=True)
            st.caption(f"Total Rows: {len(df_b1_raw)} | File: Excel")
            
        with col_r2:
            st.markdown("#### 📄 Gajuwaka POS (`.csv`)")
            df_b2_raw = pd.read_csv(os.path.join(raw_dir, "branch2_gajuwaka_pos.csv"))
            st.dataframe(df_b2_raw.head(5), use_container_width=True)
            st.caption(f"Total Rows: {len(df_b2_raw)} | File: CSV")
            
        with col_r3:
            st.markdown("#### 📄 Siripuram Cloud (`.csv`)")
            df_b3_raw = pd.read_csv(os.path.join(raw_dir, "branch3_siripuram.csv"))
            st.dataframe(df_b3_raw.head(5), use_container_width=True)
            st.caption(f"Total Rows: {len(df_b3_raw)} | File: CSV")

    with tab2:
        st.markdown("### 🛠️ Data Cleaning & Normalization Steps Executed")
        st.markdown("""
        1. **Schema Standardization**: Unified column names (`Txn_Date` / `POS_Timestamp` / `Date` -> `date`).
        2. **Datetime Normalization**: Parsed strings in multiple formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `YYYY/MM/DD`) to `datetime64[ns]`.
        3. **Missing Value Imputation**: Calculated median quantity sold per product for missing POS records.
        4. **Data Type Casting & Validation**: Filtered negative price anomalies (`unit_price > 0`).
        5. **Derived Features**: Calculated `revenue = unit_price * quantity_sold` and classified products into `Perishable` vs `Fast-Moving Goods`.
        """)
        
        if st.button("🔄 Re-run Data Pipeline & Refresh Database"):
            load_and_clean_branch_data()
            st.success("ETL Pipeline executed successfully! Data refreshed in SQLite Database.")

    with tab3:
        st.markdown("### 🗄️ Standardized Unified Dataset (Stored in SQLite `sales_records` table)")
        st.dataframe(df_filtered.head(100), use_container_width=True)
        st.caption(f"Showing {len(df_filtered)} cleaned transaction logs for {selected_branch}.")

# --- 3. EXPLORATORY DATA ANALYSIS (EDA) ---
elif navigation == "📊 Exploratory Data Analysis (EDA)":
    st.title("📊 Exploratory Data Analysis (EDA)")
    st.caption("Intro to Data Science Unit 1 • Descriptive Analytics & Visualizations")

    # Time series daily revenue trend
    st.markdown("### 📅 Daily Sales Trend Analysis")
    daily_sales = df_filtered.groupby(['date', 'item_type'])['revenue'].sum().reset_index()
    
    fig_daily = px.line(
        daily_sales, x='date', y='revenue', color='item_type',
        title=f"Daily Revenue Trend ({selected_branch})",
        labels={'revenue': 'Revenue (₹)', 'date': 'Transaction Date'},
        template="plotly_dark",
        color_discrete_map={'Perishable': '#ef4444', 'Fast-Moving Goods': '#3b82f6'}
    )
    st.plotly_chart(fig_daily, use_container_width=True)

    col_eda1, col_eda2 = st.columns(2)
    with col_eda1:
        st.markdown("### 🏆 Top 10 Revenue Generating Products")
        top_prod = df_filtered.groupby('product_name')['revenue'].sum().reset_index()
        top_prod = top_prod.sort_values(by='revenue', ascending=False).head(10)
        
        fig_top = px.bar(
            top_prod, x='revenue', y='product_name', orientation='h',
            title="Top 10 Products by Total Revenue",
            labels={'revenue': 'Revenue (₹)', 'product_name': 'Product'},
            template="plotly_dark",
            color='revenue',
            color_continuous_scale='Viridis'
        )
        fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

    with col_eda2:
        st.markdown("### 📦 Volume Sold vs Unit Price Relationship")
        prod_scatter = df_filtered.groupby(['product_name', 'item_type', 'unit_price'])['quantity_sold'].sum().reset_index()
        
        fig_scatter = px.scatter(
            prod_scatter, x='unit_price', y='quantity_sold', color='item_type',
            size='quantity_sold', hover_name='product_name',
            title="Price vs Volume Sold per Product",
            labels={'unit_price': 'Unit Price (₹)', 'quantity_sold': 'Total Units Sold'},
            template="plotly_dark",
            color_discrete_map={'Perishable': '#f87171', 'Fast-Moving Goods': '#38bdf8'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

# --- 4. DEMAND FORECAST & RESTOCKING ALERTS ---
elif navigation == "🔮 Demand Forecast & Restocking Alerts":
    st.title("🔮 Demand Forecasting & Restocking Alert Engine")
    st.caption("Next-Week Product Demand Forecasting & Branch Restocking Recommendations")

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        forecast_algo = st.selectbox(
            "Select Forecasting Algorithm",
            ["Weighted Moving Average (Recommended)", "Simple Moving Average (7D)", "Exponential Smoothing"]
        )
    with col_ctrl2:
        risk_filter = st.selectbox(
            "Filter by Risk Alert Status",
            ["All Products", "Critical Stockout Risk", "Overstocking & Spoilage Risk", "Healthy"]
        )

    # Generate Forecast
    forecast_df = forecast_next_week_demand(df_filtered, branch_name=selected_branch, forecast_method=forecast_algo)
    alert_df = generate_inventory_alerts(forecast_df)

    # Apply risk filter
    if risk_filter == "Critical Stockout Risk":
        display_df = alert_df[alert_df['Risk Level'] == 'HIGH RISK - STOCKOUT']
    elif risk_filter == "Overstocking & Spoilage Risk":
        display_df = alert_df[alert_df['Risk Level'] == 'HIGH RISK - PERISHABLE WASTE']
    elif risk_filter == "Healthy":
        display_df = alert_df[alert_df['Risk Level'] == 'OPTIMAL']
    else:
        display_df = alert_df.copy()

    st.markdown("### 📊 Next 7-Day Demand Forecast & Reorder Plan")
    st.dataframe(
        display_df[[
            'Branch', 'Product Name', 'Category', 'Item Type', 'Current Stock',
            'Predicted 7-Day Demand', 'Safety Stock Needed', 'Suggested Reorder Qty',
            'Stock Alert Status', 'Recommended Action'
        ]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("### 📉 Visual Demand Forecast vs Current Inventory")
    
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        x=display_df['Product Name'],
        y=display_df['Current Stock'],
        name='Current Store Inventory',
        marker_color='#3b82f6'
    ))
    fig_comp.add_trace(go.Bar(
        x=display_df['Product Name'],
        y=display_df['Predicted 7-Day Demand'],
        name='Predicted 7-Day Demand',
        marker_color='#10b981'
    ))
    fig_comp.update_layout(
        barmode='group',
        title=f"Current Stock vs Next-Week Demand ({selected_branch})",
        xaxis_title="Product",
        yaxis_title="Units",
        template="plotly_dark"
    )
    st.plotly_chart(fig_comp, use_container_width=True)

# --- 5. FESTIVAL SCENARIO SIMULATOR ---
elif navigation == "🧪 Festival Scenario Simulator":
    st.title("🧪 Festival & Seasonal Demand Scenario Simulator")
    st.caption("Simulate demand spikes during Vizag Festivals (Sankranti, Diwali, Ugadi)")

    st.markdown("""
    During major festive seasons in Andhra Pradesh (e.g., **Sankranti**, **Diwali**, **Visakha Utsav**), retail demand for staples, dairy, and sweets surges dramatically. Use the simulator below to stress-test your supply chain!
    """)

    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        event = st.selectbox(
            "Select Festive Event",
            ["Sankranti (High Sweets & Dairy Demand +50%)", "Diwali Festival (+35% FMCG)", "Normal Business Week (1.0x)", "Custom Multiplier"]
        )
    
    if event == "Sankranti (High Sweets & Dairy Demand +50%)":
        mult = 1.50
    elif event == "Diwali Festival (+35% FMCG)":
        mult = 1.35
    elif event == "Normal Business Week (1.0x)":
        mult = 1.00
    else:
        mult = st.slider("Select Custom Demand Surge Multiplier", 0.50, 2.50, 1.25, 0.05)

    with col_sim2:
        st.info(f"Applying **{mult:.2f}x** Demand Surge Multiplier across {selected_branch}.")

    # Generate scenario forecast
    sim_forecast = forecast_next_week_demand(df_filtered, branch_name=selected_branch, festival_multiplier=mult)
    sim_alerts = generate_inventory_alerts(sim_forecast)

    total_sim_demand = sim_forecast['Predicted 7-Day Demand'].sum()
    total_reorder = sim_forecast['Suggested Reorder Qty'].sum()
    out_of_stock_count = len(sim_alerts[sim_alerts['Risk Level'] == 'HIGH RISK - STOCKOUT'])

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Simulated Total 7-Day Demand", f"{total_sim_demand:,} units", f"+{(mult-1)*100:.0f}%")
    with c2:
        st.metric("Total Suggested Reorder Quantity", f"{total_reorder:,} units")
    with c3:
        st.metric("Potential Stockout Products", f"{out_of_stock_count} Items", delta=f"{out_of_stock_count} At Risk", delta_color="inverse")

    st.markdown("### 📋 Simulated Purchase Order Plan for Store Managers")
    st.dataframe(
        sim_alerts[['Product Name', 'Category', 'Item Type', 'Current Stock', 'Predicted 7-Day Demand', 'Suggested Reorder Qty', 'Recommended Action']],
        use_container_width=True,
        hide_index=True
    )

# --- 6. JNTUK SYLLABUS MAPPING & CHARTER ---
elif navigation == "🎓 JNTUK Syllabus & Charter":
    st.title("🎓 JNTUK 2nd Year Syllabus Mapping & Project Charter")
    st.caption("Academic Project Documentation • JNTUK B.Tech Curriculum Alignment")

    st.markdown("""
    ### 📌 Project Metadata
    - **Project Title**: Smart Retail Demand Forecasting System
    - **Target Institution**: Jawaharlal Nehru Technological University Kakinada (JNTUK)
    - **Academic Level**: B.Tech 2nd Year (Semester III/IV)
    - **Domain**: Data Science / Data Engineering / Retail Analytics

    ---
    ### 📚 Curriculum Unit Mapping (JNTUK 2nd Year Syllabus)
    
    | Syllabus Unit | Topics Covered in Project | Implementation Details |
    | :--- | :--- | :--- |
    | **Intro to DS Unit 1** | Data Science Pipeline, Source Systems, Data Maturity | End-to-end data lifecycle from raw multi-branch exports to executive dashboard insights. |
    | **Data Engineering Unit 1** | Data Ingestion, Cleaning, Schema Standardization, Storage | Processing Excel (`.xlsx`), CSV files, handling missing values, storing in SQLite DB. |
    | **Python Unit 1** | Data Wrangling, Pandas, Modules, Control Flow | Modular Python code structure (`src/data_loader.py`, `src/forecasting.py`, `src/alerts.py`). |

    ---
    ### 🤖 AI Tools & Technology Stack
    - **AI Assistant Tools**: 
      - *ChatGPT*: Designed the 5-layer pipeline architecture & academic project charter.
      - *GitHub Copilot*: Assisted in writing automated ETL cleaning functions & Streamlit UI components.
    - **Programming Language**: Python 3.13
    - **Data Processing**: Pandas, NumPy
    - **Database**: SQLite (Simulating MySQL relational storage)
    - **Visualization**: Plotly Express, Matplotlib
    - **Web Framework**: Streamlit
    """)
