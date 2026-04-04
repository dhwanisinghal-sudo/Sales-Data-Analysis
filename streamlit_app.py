import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #141e30, #243b55);
    color: white;
}
.metric-card {
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align: center; color: #00c6ff;'>🚀 E-commerce Analytics Dashboard</h1>", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='latin1')

    # ---------------- DATA CLEANING ----------------
    df.columns = df.columns.str.strip()

    # Convert date safely
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    # Remove nulls
    df = df.dropna()

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.header("🎯 Filters")

    # Category Filter
    if "Category" in df.columns:
        category = st.sidebar.multiselect(
            "Select Category",
            df["Category"].unique(),
            default=df["Category"].unique()
        )
        df = df[df["Category"].isin(category)]

    # Region Filter
    if "Region" in df.columns:
        region = st.sidebar.multiselect(
            "Select Region",
            df["Region"].unique(),
            default=df["Region"].unique()
        )
        df = df[df["Region"].isin(region)]

    # Date Filter
    if "Order Date" in df.columns:
        min_date = df["Order Date"].min()
        max_date = df["Order Date"].max()

        date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range)
            df = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]

    # ---------------- CHECK DATA ----------------
    if df.empty:
        st.warning("⚠️ No data available for selected filters.")
    else:
        # ---------------- KPIs ----------------
        total_sales = int(df["Sales"].sum()) if "Sales" in df.columns else 0
        total_profit = int(df["Profit"].sum()) if "Profit" in df.columns else 0
        total_orders = df.shape[0]

        col1, col2, col3 = st.columns(3)

        col1.metric("💰 Total Sales", total_sales)
        col2.metric("📈 Total Profit", total_profit)
        col3.metric("📦 Total Orders", total_orders)

        # ---------------- SALES TREND ----------------
        if "Order Date" in df.columns and "Sales" in df.columns:
            sales_trend = df.groupby("Order Date")["Sales"].sum().reset_index()

            fig1 = px.line(
                sales_trend,
                x="Order Date",
                y="Sales",
                title="📈 Sales Trend",
                markers=True
            )
            fig1.update_layout(template="plotly_dark")
            st.plotly_chart(fig1, use_container_width=True)

        # ---------------- CATEGORY WISE ----------------
        if "Category" in df.columns:
            cat_data = df.groupby("Category")["Sales"].sum().reset_index()

            fig2 = px.bar(
                cat_data,
                x="Category",
                y="Sales",
                title="📊 Sales by Category",
                text_auto=True
            )
            fig2.update_layout(template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        # ---------------- REGION WISE ----------------
        if "Region" in df.columns:
            reg_data = df.groupby("Region")["Sales"].sum().reset_index()

            fig3 = px.pie(
                reg_data,
                names="Region",
                values="Sales",
                title="🌍 Sales Distribution by Region"
            )
            fig3.update_layout(template="plotly_dark")
            st.plotly_chart(fig3, use_container_width=True)

        # ---------------- INSIGHTS ----------------
        st.subheader("🧠 Insights")

        if "Profit" in df.columns and total_profit < 0:
            st.error("⚠️ Overall loss detected! Reduce discounts.")

        if "Category" in df.columns:
            top_cat = df.groupby("Category")["Sales"].sum().idxmax()
            st.success(f"🔥 Top Performing Category: {top_cat}")

        if "Region" in df.columns:
            top_region = df.groupby("Region")["Sales"].sum().idxmax()
            st.info(f"🌍 Best Region: {top_region}")

else:
    st.info("👆 Please upload a CSV file to get started.")
