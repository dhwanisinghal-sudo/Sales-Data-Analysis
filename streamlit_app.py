import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="E-commerce Analytics Dashboard", layout="wide")

# -------------------- LOAD DATA -------------------- #
@st.cache_data
def load_data():
    paths = [
        "filtered_data.csv",
        "data/filtered_data.csv",
        "./filtered_data.csv"
    ]
    
    for path in paths:
        if os.path.exists(path):
            df = pd.read_csv(path, encoding='latin1')
            return df
    
    st.error("❌ CSV file not found. Upload 'filtered_data.csv'")
    st.write("Available files:", os.listdir())
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# -------------------- DATA CLEANING -------------------- #
df.columns = df.columns.str.strip()

# Convert Date
if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Month Name"] = df["Order Date"].dt.strftime("%b")

# Fill missing numeric values
for col in ["Sales", "Profit", "Quantity"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df = df.dropna(how="all")

# -------------------- SIDEBAR -------------------- #
st.sidebar.title("🔍 Filter Panel")

# Date filter
if "Order Date" in df.columns:
    min_date = df["Order Date"].min()
    max_date = df["Order Date"].max()

    start, end = st.sidebar.date_input("Select Date Range", [min_date, max_date])
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

if df.empty:
    st.warning("⚠️ No data for selected filters")
    st.stop()

# -------------------- TITLE -------------------- #
st.title("🛒 E-commerce Order Trend & Seasonal Analysis")

# -------------------- KPI SECTION -------------------- #
col1, col2, col3, col4 = st.columns(4)

total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
total_profit = df["Profit"].sum() if "Profit" in df.columns else 0
total_orders = len(df)
avg_order = total_sales / total_orders if total_orders > 0 else 0

col1.metric("💰 Total Sales", f"{total_sales:,.0f}")
col2.metric("📈 Total Profit", f"{total_profit:,.0f}")
col3.metric("📦 Orders", total_orders)
col4.metric("🧾 Avg Order Value", f"{avg_order:,.0f}")

# -------------------- TREND ANALYSIS -------------------- #
st.subheader("📊 Sales Trend Over Time")

if "Order Date" in df.columns:
    trend = df.groupby("Order Date")["Sales"].sum().reset_index()
    st.line_chart(trend.set_index("Order Date"))

# -------------------- SEASONALITY -------------------- #
st.subheader("📅 Monthly Seasonality")

if "Month Name" in df.columns:
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]

    season = df.groupby("Month Name")["Sales"].sum().reindex(month_order)
    st.bar_chart(season)

# -------------------- CATEGORY PERFORMANCE -------------------- #
st.subheader("📦 Category Performance")

if "Category" in df.columns:
    cat_perf = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    st.bar_chart(cat_perf)

# -------------------- TOP PRODUCTS -------------------- #
st.subheader("🏆 Top Products")

if "Product Name" in df.columns:
    top_products = df.groupby("Product Name")["Sales"].sum().nlargest(10)
    st.dataframe(top_products)

# -------------------- PROFIT VS SALES -------------------- #
st.subheader("📉 Profit vs Sales")

if "Sales" in df.columns and "Profit" in df.columns:
    st.scatter_chart(df[["Sales", "Profit"]])

# -------------------- HEATMAP STYLE TABLE -------------------- #
st.subheader("🔥 Region vs Category Pivot")

if "Region" in df.columns and "Category" in df.columns:
    pivot = pd.pivot_table(
        df,
        values="Sales",
        index="Region",
        columns="Category",
        aggfunc="sum",
        fill_value=0
    )
    st.dataframe(pivot)

# -------------------- INSIGHTS -------------------- #
st.subheader("🧠 Auto Insights")

if total_profit < 0:
    st.error("❌ Overall business is in LOSS")
elif total_profit > 0:
    st.success("✅ Business is PROFITABLE")

if "Category" in df.columns:
    best_cat = df.groupby("Category")["Sales"].sum().idxmax()
    st.info(f"🏆 Best Performing Category: {best_cat}")

if "Region" in df.columns:
    best_region = df.groupby("Region")["Sales"].sum().idxmax()
    st.info(f"🌍 Best Region: {best_region}")

# -------------------- DOWNLOAD -------------------- #
st.download_button(
    "⬇ Download Filtered Data",
    df.to_csv(index=False),
    file_name="filtered_output.csv"
)
