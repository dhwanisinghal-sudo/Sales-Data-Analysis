import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

st.title("🛒 E-commerce Order Trend & Seasonal Analysis")

# -------------------- DATA LOAD -------------------- #
@st.cache_data
def load_data(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding='latin1')
        return df
    
    # fallback: try local files
    paths = ["filtered_data.csv", "data/filtered_data.csv"]
    for path in paths:
        if os.path.exists(path):
            return pd.read_csv(path, encoding='latin1')
    
    return pd.DataFrame()

# Upload option
uploaded_file = st.file_uploader("📂 Upload CSV (Recommended)", type=["csv"])

df = load_data(uploaded_file)

# अगर data nahi mila
if df.empty:
    st.error("❌ No CSV file found!")
    st.info("👉 Upload file OR keep 'filtered_data.csv' in same folder")
    st.write("📂 Available files:", os.listdir())
    st.stop()

st.success("✅ Data Loaded Successfully")

# -------------------- CLEANING -------------------- #
df.columns = df.columns.str.strip()

if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%b")

for col in ["Sales", "Profit", "Quantity"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df = df.dropna(how="all")

# -------------------- SIDEBAR FILTERS -------------------- #
st.sidebar.header("🔍 Filters")

# Date filter
if "Order Date" in df.columns:
    min_date = df["Order Date"].min()
    max_date = df["Order Date"].max()

    start, end = st.sidebar.date_input("Date Range", [min_date, max_date])
    df = df[(df["Order Date"] >= pd.to_datetime(start)) &
            (df["Order Date"] <= pd.to_datetime(end))]

# Category
if "Category" in df.columns:
    cat = st.sidebar.multiselect(
        "Category",
        df["Category"].dropna().unique(),
        default=df["Category"].dropna().unique()
    )
    df = df[df["Category"].isin(cat)]

# Region
if "Region" in df.columns:
    reg = st.sidebar.multiselect(
        "Region",
        df["Region"].dropna().unique(),
        default=df["Region"].dropna().unique()
    )
    df = df[df["Region"].isin(reg)]

# Segment
if "Segment" in df.columns:
    seg = st.sidebar.multiselect(
        "Segment",
        df["Segment"].dropna().unique(),
        default=df["Segment"].dropna().unique()
    )
    df = df[df["Segment"].isin(seg)]

# Empty check after filters
if df.empty:
    st.warning("⚠️ No data available for selected filters")
    st.stop()

# -------------------- KPIs -------------------- #
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
total_profit = df["Profit"].sum() if "Profit" in df.columns else 0
total_orders = len(df)
avg_order = total_sales / total_orders if total_orders > 0 else 0

col1.metric("💰 Total Sales", f"{total_sales:,.0f}")
col2.metric("📈 Total Profit", f"{total_profit:,.0f}")
col3.metric("📦 Orders", total_orders)
col4.metric("🧾 Avg Order Value", f"{avg_order:,.0f}")

# -------------------- CHARTS -------------------- #
st.subheader("📈 Sales Trend")

if "Order Date" in df.columns and "Sales" in df.columns:
    trend = df.groupby("Order Date")["Sales"].sum()
    st.line_chart(trend)

st.subheader("📅 Monthly Seasonality")

if "Month Name" in df.columns:
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]

    season = df.groupby("Month Name")["Sales"].sum().reindex(month_order)
    st.bar_chart(season)

st.subheader("📦 Category Performance")

if "Category" in df.columns:
    cat_perf = df.groupby("Category")["Sales"].sum()
    st.bar_chart(cat_perf)

st.subheader("📉 Profit vs Sales")

if "Sales" in df.columns and "Profit" in df.columns:
    st.scatter_chart(df[["Sales", "Profit"]])

# -------------------- TABLE -------------------- #
st.subheader("📄 Data Preview")
st.dataframe(df)

# -------------------- DOWNLOAD -------------------- #
st.download_button(
    "⬇ Download Filtered Data",
    df.to_csv(index=False),
    file_name="filtered_data_output.csv"
)
