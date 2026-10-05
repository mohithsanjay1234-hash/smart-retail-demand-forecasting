# 🛒 Smart Retail Demand Forecasting System
### JNTUK B.Tech 2nd Year Curriculum Project (Unit 1 Syllabus Based)

> **Industry Problem Context**: A supermarket chain in Vizag loses crores annually due to overstocking perishables (spoilage loss) and understocking fast-moving consumer goods (lost sales revenue). Sales data is fragmented across Excel files (MVP Colony branch), POS machines (Gajuwaka Industrial Hub), and CSV exports (Siripuram Junction).

---

## 📁 Complete Project Directory Structure

```text
Smart retail demand forecasting/
│
├── data/
│   ├── raw/                           # Raw scattered source files from 3 Vizag branches
│   │   ├── branch1_mvp_colony.xlsx    # Excel ERP file (MVP Colony Branch)
│   │   ├── branch2_gajuwaka_pos.csv   # POS Machine export (Gajuwaka Branch)
│   │   └── branch3_siripuram.csv      # Cloud CSV export (Siripuram Branch)
│   └── processed/
│       ├── retail_store.db            # SQLite relational database (MySQL equivalent for Unit 1)
│       └── unified_sales_data.csv     # Cleaned, standardized unified dataset
│
├── src/                               # Modular Python source code (Python Unit 1)
│   ├── __init__.py                    # Python package initializer
│   ├── data_loader.py                 # Multi-source ETL ingestion & cleaning engine
│   ├── database.py                    # SQLite database interface & queries
│   ├── forecasting.py                 # Demand forecasting models (SMA, WMA, EMA)
│   └── alerts.py                      # Inventory stockout & perishable spoilage alert rules
│
├── app.py                             # Interactive Streamlit Web Application Dashboard
├── generate_sample_data.py            # Data generator script for 90-day Vizag retail sales
├── requirements.txt                   # Python library dependencies
└── README.md                          # Project documentation & JNTUK syllabus mapping
```

---

## 🎓 JNTUK 2nd Year Syllabus Alignment

| Syllabus Unit | Course Concept | How It Is Implemented In This Project |
| :--- | :--- | :--- |
| **Intro to DS Unit 1** | Data Science Pipeline & Data Maturity | Complete pipeline from raw multi-branch data ingestion to EDA and demand forecasting. |
| **Data Engineering Unit 1** | Ingestion, Cleaning & Schema Mapping | Standardizing mismatched column names from Excel (`.xlsx`) & CSV sources into SQLite DB. |
| **Python Unit 1** | Modules, Data Structures & Pandas | Modular code structure (`src/`) with Pandas DataFrame operations, aggregations, and functions. |

---

## 🚀 How to Run the Project (Step-by-Step)

### Step 1: Open Terminal / Command Prompt
Navigate to your project directory:
```bash
cd "c:\Users\mouni\OneDrive\Documents\Smart retail demand forecasting"
```

### Step 2: Install Required Libraries
```bash
pip install -r requirements.txt
```

### Step 3: Generate Branch Sales Data (Initial Setup)
Run the sample data generator script to populate `data/raw/`:
```bash
python generate_sample_data.py
```

### Step 4: Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
*The web browser will automatically open at `http://localhost:8501`!*

---

## 💻 Tech Stack Used
- **Programming Language**: Python 3.13
- **Data Engineering & Wrangling**: Pandas, NumPy
- **Database**: SQLite (SQL Relational DB)
- **Web UI & Dashboard**: Streamlit
- **Data Visualization**: Plotly Express, Matplotlib
- **AI Design Tools**: ChatGPT (Pipeline Architecture & Project Charter), Copilot (Data Cleaning Logic)

---

## 🎯 Key Features of the Dashboard
1. **Executive KPI Overview**: Live revenue stats, total units sold, critical stockout count, and perishable waste alert count.
2. **Data Engineering ETL Tab**: Interactive view of raw Excel & CSV branch files, schema transformation table, and SQLite DB explorer.
3. **Exploratory Data Analysis (EDA)**: Interactive Plotly charts for daily sales trends, perishable vs fast-moving goods comparison, and top products.
4. **Demand Forecast & Restocking Alerts**:
   - 7-Day Moving Average & Exponential Smoothing demand forecast per product.
   - Reorder Point (ROP) & Suggested Reorder Quantity calculation.
   - **CRITICAL STOCKOUT RISK** alerts for Fast-Moving Goods (Rice, Oil, Tea, Detergent).
   - **OVERSTOCK & SPOILAGE RISK** alerts for Perishables (Milk, Curd, Paneer, Tomatoes).
5. **Festival Scenario Simulator**: Simulate demand surges during Andhra festivals (Sankranti, Diwali) with custom multipliers (e.g. +50% surge).
6. **JNTUK Project Charter**: Academic documentation page summarizing course unit mapping and technical stack.

---

## 🎤 Expected Viva Voice / Lab Evaluation Questions

**Q1: Why did you use moving average models for forecasting?**
> *Answer*: For Unit 1 Data Science level, Simple & Weighted Moving Averages effectively capture recent sales trends without overfitting noise. Weighted Moving Average places higher importance on recent days (e.g., last 3 days) which reflects daily demand changes in perishable goods.

**Q2: How does the data cleaning pipeline handle mismatched files?**
> *Answer*: The `src/data_loader.py` module defines a column mapping dictionary that translates varied field names (`Txn_Date`, `POS_Timestamp`, `Date`) into a single standard column schema (`date`). It also converts string dates to `datetime64[ns]` and imputes missing quantity values using product-wise median imputation.

**Q3: How are restocking alerts calculated?**
> *Answer*: Suggested Reorder Quantity is computed as `Reorder Point - Current Stock`. Reorder Point includes 7-day predicted demand plus 2-day Safety Stock. If current stock falls below 50% of 7-day demand, a **CRITICAL STOCKOUT** alert is triggered. If stock exceeds 2x demand for perishables, an **OVERSTOCK & SPOILAGE RISK** alert is triggered.
