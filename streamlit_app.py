import streamlit as st
import pandas as pd
import plotly.express as px

# ================= CONFIG =================
st.set_page_config(page_title="Ultimate E-commerce Dashboard", layout="wide")

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")

    # Clean columns
    df.columns = df.columns.str.strip()

    # Auto rename
    rename = {}
    for col in df.columns:
        c = col.lower()
        if "sales" in c:
            rename[col] = "Sales"
        elif "profit" in c:
            rename[col] = "Profit"
        elif "order" in c and "date" in c:
            rename[col] = "Order Date"
        elif "category" in c:
            rename[col] = "Category"
        elif "product" in c:
            rename[col] = "Product Name"
        elif "region" in c:
            rename[col] = "Region"

    df = df.rename(columns=rename)

    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    return df

df = load_data()

# ================= SIDEBAR =================
st.sidebar.title("🔍 Smart Filters")

# Date filter
if "Order Date" in df.columns:
    min_d, max_d = df["Order Date"].min(), df["Order Date"].max()
    date_range = st.sidebar.date_input("Date", [min_d, max_d])
else:
    date_range = []

# Category
category = st.sidebar.multiselect(
    "Category",
    df["Category"].dropna().unique() if "Category" in df.columns else []
)

# Region
region = st.sidebar.multiselect(
    "Region",
    df["Region"].dropna().unique() if "Region" in df.columns else []
)

# ================= FILTER =================
filtered = df.copy()

try:
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[
            (filtered["Order Date"] >= start) &
            (filtered["Order Date"] <= end)
        ]
except:
    pass

if category:
    filtered = filtered[filtered["Category"].isin(category)]

if region:
    filtered = filtered[filtered["Region"].isin(region)]

# ================= EMPTY =================
if filtered.empty:
    st.warning("⚠️ No data for selected filters")
    st.stop()

# ================= KPIs =================
sales = filtered["Sales"].sum() if "Sales" in filtered.columns else 0
profit = filtered["Profit"].sum() if "Profit" in filtered.columns else 0
orders = len(filtered)

prev = df.iloc[:len(filtered)]
prev_sales = prev["Sales"].sum() if "Sales" in prev.columns else 1

growth = ((sales - prev_sales) / prev_sales) * 100 if prev_sales != 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("💰 Sales", f"{sales:,.0f}", f"{growth:.1f}%")
c2.metric("📈 Profit", f"{profit:,.0f}")
c3.metric("📦 Orders", orders)

st.divider()

# ================= TREND =================
if all(col in filtered.columns for col in ["Order Date", "Sales"]):
    trend = filtered.groupby("Order Date")["Sales"].sum().reset_index()

    fig = px.line(trend, x="Order Date", y="Sales", title="Sales Trend")
    st.plotly_chart(fig, use_container_width=True)

# ================= CATEGORY =================
if "Category" in filtered.columns:
    cat = filtered.groupby("Category")["Sales"].sum().reset_index()

    fig = px.bar(cat, x="Category", y="Sales", color="Category")
    st.plotly_chart(fig, use_container_width=True)

# ================= REGION =================
if "Region" in filtered.columns:
    reg = filtered.groupby("Region")["Sales"].sum().reset_index()

    fig = px.pie(reg, names="Region", values="Sales")
    st.plotly_chart(fig, use_container_width=True)

# ================= TOP PRODUCTS =================
if "Product Name" in filtered.columns:
    top = (
        filtered.groupby("Product Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(top, x="Sales", y="Product Name", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

# ================= HEATMAP =================
if "Order Date" in filtered.columns:
    filtered["Month"] = filtered["Order Date"].dt.month
    filtered["Year"] = filtered["Order Date"].dt.year

    pivot = filtered.pivot_table(
        values="Sales",
        index="Year",
        columns="Month",
        aggfunc="sum"
    )

    st.subheader("🔥 Seasonality Heatmap")
    st.dataframe(pivot)

# ================= DOWNLOAD =================
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Data", csv, "filtered_data.csv")

# ================= AI INSIGHTS =================
st.subheader("🤖 Smart Insights")

insight = f"""
- Total Sales: {sales:,.0f}
- Total Profit: {profit:,.0f}
- Orders: {orders}

👉 Peak performance observed in top categories/products.
👉 Consider focusing on high-selling regions.
👉 Monitor months with low sales for strategy improvement.
"""

st.info(insight)
