import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# ---------------- TITLE ----------------
st.title("📊 E-commerce Analytics Dashboard")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1')
    except:
        df = pd.read_csv(uploaded_file)

    df.columns = df.columns.str.strip()

    # ---------------- BASIC CLEAN ----------------
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    df = df.dropna(subset=["Sales", "Profit"], errors='ignore')

    # ---------------- SIDEBAR ----------------
    st.sidebar.header("Filters")

    # Category
    if "Category" in df.columns:
        category = st.sidebar.multiselect(
            "Category",
            df["Category"].dropna().unique(),
            df["Category"].dropna().unique()
        )
        if category:
            df = df[df["Category"].isin(category)]

    # Region
    if "Region" in df.columns:
        region = st.sidebar.multiselect(
            "Region",
            df["Region"].dropna().unique(),
            df["Region"].dropna().unique()
        )
        if region:
            df = df[df["Region"].isin(region)]

    # Date
    if "Order Date" in df.columns and not df["Order Date"].isna().all():
        min_date = df["Order Date"].min()
        max_date = df["Order Date"].max()

        date_range = st.sidebar.date_input(
            "Date Range",
            [min_date, max_date]
        )

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range)
            df = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]

    # ---------------- EMPTY CHECK ----------------
    if df.empty:
        st.warning("⚠️ No data available for selected filters.")
    else:
        # ---------------- KPIs ----------------
        total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
        total_profit = df["Profit"].sum() if "Profit" in df.columns else 0
        total_orders = len(df)

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Sales", f"{total_sales:,.0f}")
        c2.metric("📈 Total Profit", f"{total_profit:,.0f}")
        c3.metric("📦 Total Orders", total_orders)

        # ---------------- SALES TREND ----------------
        if "Order Date" in df.columns:
            trend = df.groupby("Order Date")["Sales"].sum().reset_index()

            fig1 = px.line(trend, x="Order Date", y="Sales", title="Sales Trend")
            st.plotly_chart(fig1, use_container_width=True)

        # ---------------- CATEGORY ----------------
        if "Category" in df.columns:
            cat = df.groupby("Category")["Sales"].sum().reset_index()

            fig2 = px.bar(cat, x="Category", y="Sales", title="Sales by Category")
            st.plotly_chart(fig2, use_container_width=True)

        # ---------------- REGION ----------------
        if "Region" in df.columns:
            reg = df.groupby("Region")["Sales"].sum().reset_index()

            fig3 = px.pie(reg, names="Region", values="Sales", title="Region Distribution")
            st.plotly_chart(fig3, use_container_width=True)

        # ---------------- TOP PRODUCTS ----------------
        if "Product Name" in df.columns:
            st.subheader("Top Products")

            top_products = (
                df.groupby("Product Name")["Sales"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )

            st.dataframe(top_products)

        # ---------------- DOWNLOAD ----------------
        csv = df.to_csv(index=False)

        st.download_button(
            "Download Filtered Data",
            csv,
            "filtered_data.csv"
        )

else:
    st.info("👆 Please upload a CSV file to start.")
