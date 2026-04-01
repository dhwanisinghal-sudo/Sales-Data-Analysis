import streamlit as st
import pandas as pd

# Plotly safe
try:
    import plotly.express as px
    PLOTLY = True
except:
    PLOTLY = False

st.set_page_config(page_title="GOD MODE Dashboard", layout="wide")

# ================= LOAD =================
@st.cache_data
def load():
    df = pd.read_csv("train.csv")

    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.duplicated()]

    rename = {}
    for col in df.columns:
        c = col.lower()
        if "order" in c and "date" in c:
            rename[col] = "Order Date"
        elif "sales" in c:
            rename[col] = "Sales"
        elif "category" in c:
            rename[col] = "Category"

    df = df.rename(columns=rename)

    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

    return df

df = load()

# ================= FILTER =================
st.sidebar.title("⚙️ Controls")

filtered = df.copy()

if "Order Date" in df.columns:
    min_d, max_d = df["Order Date"].min(), df["Order Date"].max()
    dr = st.sidebar.date_input("Date Range", [min_d, max_d])

    if len(dr) == 2:
        start, end = pd.to_datetime(dr[0]), pd.to_datetime(dr[1])
        filtered = filtered[
            (filtered["Order Date"] >= start) &
            (filtered["Order Date"] <= end)
        ]

if "Category" in df.columns:
    cat = st.sidebar.multiselect(
        "Category",
        df["Category"].astype(str).dropna().unique()
    )
    if cat:
        filtered = filtered[filtered["Category"].astype(str).isin(cat)]

# ================= EMPTY =================
st.title("🛒 E-commerce GOD MODE Dashboard")

if filtered.empty:
    st.warning("No data")
    st.stop()

# ================= KPI =================
orders = len(filtered)
sales = filtered["Sales"].sum() if "Sales" in filtered.columns else 0

c1, c2 = st.columns(2)
c1.metric("📦 Orders", orders)
c2.metric("💰 Sales", f"{sales:,.0f}")

st.divider()

# ================= DAILY TREND =================
trend = filtered.groupby("Order Date").size().reset_index(name="Orders")

# Moving Average
trend["MA7"] = trend["Orders"].rolling(7).mean()

st.subheader("📈 Order Trend + Moving Average")

if PLOTLY:
    fig = px.line(trend, x="Order Date", y=["Orders", "MA7"])
    st.plotly_chart(fig, use_container_width=True)
else:
    st.line_chart(trend.set_index("Order Date"))

# ================= MONTHLY =================
filtered["Month"] = filtered["Order Date"].dt.month
monthly = filtered.groupby("Month").size()

# Growth
growth = monthly.pct_change() * 100

st.subheader("📅 Monthly Orders + Growth")
st.bar_chart(monthly)

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

# ================= PEAK DETECTION =================
peak_day = trend.loc[trend["Orders"].idxmax()]

st.subheader("🚀 Peak Analysis")

st.success(f"""
Peak Orders Day: {peak_day['Order Date'].date()}  
Orders: {int(peak_day['Orders'])}
""")

# ================= CATEGORY =================
if "Category" in filtered.columns:
    cat = filtered.groupby("Category").size()

    st.subheader("🛍️ Category Orders")
    st.bar_chart(cat)

# ================= SMART INSIGHTS =================
st.subheader("🤖 Smart Insights")

peak_month = monthly.idxmax()
low_month = monthly.idxmin()

st.info(f"""
📌 Peak Month: {peak_month}  
📉 Low Month: {low_month}  

📊 Orders show clear seasonal behavior  
📈 Moving average smooths volatility  
🚀 Focus marketing during peak months  
⚠️ Improve sales strategy in low months  
""")
