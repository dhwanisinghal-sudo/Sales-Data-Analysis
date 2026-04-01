import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# ================= LOAD =================
@st.cache_data
def load():
    df = pd.read_csv("filtered_data.csv")

    df.columns = df.columns.str.strip()

    # Convert date
    df["Order Date"] = pd.to_datetime(df["Order Date"])

    return df

df = load()

# ================= SIDEBAR =================
st.sidebar.title("Filters")

# Date filter
min_d = df["Order Date"].min()
max_d = df["Order Date"].max()

date_range = st.sidebar.date_input("Date Range", [min_d, max_d])

# Category filter (SAFE NOW)
category = st.sidebar.multiselect(
    "Category",
    sorted(df["Category"].dropna().unique())
)

# Region filter
region = st.sidebar.multiselect(
    "Region",
    sorted(df["Region"].dropna().unique())
)

# ================= FILTER =================
filtered = df.copy()

# Date
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[
        (filtered["Order Date"] >= start) &
        (filtered["Order Date"] <= end)
    ]

# Category
if category:
    filtered = filtered[filtered["Category"].isin(category)]

# Region
if region:
    filtered = filtered[filtered["Region"].isin(region)]

# ================= EMPTY =================
st.title("🛒 E-commerce Order Trend & Seasonality Dashboard")

if filtered.empty:
    st.warning("No data available")
    st.stop()

# ================= KPI =================
sales = filtered["Sales"].sum()
orders = len(filtered)

c1, c2 = st.columns(2)
c1.metric("📦 Orders", orders)
c2.metric("💰 Sales", f"{sales:,.0f}")

st.divider()

# ================= ORDER TREND =================
trend = filtered.groupby("Order Date").size().reset_index(name="Orders")

fig = px.line(trend, x="Order Date", y="Orders", title="Order Trend")
st.plotly_chart(fig, use_container_width=True)

# ================= MONTHLY =================
filtered["Month"] = filtered["Order Date"].dt.month
monthly = filtered.groupby("Month").size().reset_index(name="Orders")

fig2 = px.bar(monthly, x="Month", y="Orders", title="Monthly Seasonality")
st.plotly_chart(fig2, use_container_width=True)

# ================= HEATMAP =================
filtered["Year"] = filtered["Order Date"].dt.year

pivot = filtered.pivot_table(
    index="Year",
    columns="Month",
    values="Sales",
    aggfunc="count"
)

st.subheader("🔥 Seasonality Heatmap")
st.dataframe(pivot)

# ================= CATEGORY =================
cat = filtered.groupby("Category").size().reset_index(name="Orders")

fig3 = px.bar(cat, x="Category", y="Orders", color="Category")
st.plotly_chart(fig3, use_container_width=True)

# ================= INSIGHTS =================
peak_month = monthly.loc[monthly["Orders"].idxmax()]["Month"]
low_month = monthly.loc[monthly["Orders"].idxmin()]["Month"]

st.subheader("🤖 Insights")

st.info(f"""
📈 Peak Month: {peak_month}  
📉 Low Month: {low_month}  

👉 Strong seasonal pattern detected  
👉 Focus marketing in peak months  
👉 Improve strategy in low months  
""")
