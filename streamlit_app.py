import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>
.big-title {
    font-size:40px !important;
    font-weight:bold;
    color:#4CAF50;
}
.card {
    padding:15px;
    border-radius:10px;
    background-color:#f5f5f5;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ---------------- #
st.markdown('<p class="big-title">🛒 E-commerce Analytics Dashboard</p>', unsafe_allow_html=True)

# ---------------- FILE UPLOAD ---------------- #
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

def load_data():
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file, encoding='latin1')

    if os.path.exists("filtered_data.csv"):
        return pd.read_csv("filtered_data.csv", encoding='latin1')

    st.error("❌ Upload CSV or add 'filtered_data.csv'")
    st.stop()

df = load_data()

# ---------------- CLEANING ---------------- #
df.columns = df.columns.str.strip()

if "Order Date" in df.columns:
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Month"] = df["Order Date"].dt.strftime("%b")

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("🔍 Filters")

if "Category" in df.columns:
    cat = st.sidebar.multiselect(
        "Category",
        df["Category"].dropna().unique(),
        default=df["Category"].dropna().unique()
    )
    df = df[df["Category"].isin(cat)]

if "Region" in df.columns:
    reg = st.sidebar.multiselect(
        "Region",
        df["Region"].dropna().unique(),
        default=df["Region"].dropna().unique()
    )
    df = df[df["Region"].isin(reg)]

# ---------------- KPI SECTION ---------------- #
st.subheader("📊 Key Metrics")

col1, col2, col3 = st.columns(3)

sales = df["Sales"].sum() if "Sales" in df.columns else 0
profit = df["Profit"].sum() if "Profit" in df.columns else 0
orders = len(df)

col1.markdown(f'<div class="card">💰 <h2>{sales:,.0f}</h2><p>Total Sales</p></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="card">📈 <h2>{profit:,.0f}</h2><p>Total Profit</p></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="card">📦 <h2>{orders}</h2><p>Total Orders</p></div>', unsafe_allow_html=True)

# ---------------- CHARTS ---------------- #
st.subheader("📈 Sales Trend")

if "Order Date" in df.columns and "Sales" in df.columns:
    trend = df.groupby("Order Date")["Sales"].sum()
    st.line_chart(trend)

st.subheader("📅 Monthly Sales")

if "Month" in df.columns:
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    season = df.groupby("Month")["Sales"].sum().reindex(month_order)
    st.bar_chart(season)

# ---------------- CATEGORY ---------------- #
st.subheader("📦 Category Performance")

if "Category" in df.columns:
    cat_perf = df.groupby("Category")["Sales"].sum()
    st.bar_chart(cat_perf)

# ---------------- INSIGHTS ---------------- #
st.subheader("🧠 Insights")

if "Profit" in df.columns:
    if profit > 0:
        st.success("✅ Business is making profit")
    else:
        st.error("❌ Business is in loss")

if "Category" in df.columns:
    best_cat = df.groupby("Category")["Sales"].sum().idxmax()
    st.info(f"🏆 Best Category: {best_cat}")

# ---------------- DATA ---------------- #
st.subheader("📄 Data Preview")
st.dataframe(df)

# ---------------- DOWNLOAD ---------------- #
st.download_button(
    "⬇ Download Data",
    df.to_csv(index=False),
    file_name="filtered_data.csv"
)
