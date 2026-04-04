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

    # ---------------- CLEAN ----------------
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    if "Sales" in df.columns:
        df = df[df["Sales"].notna()]
    if "Profit" in df.columns:
        df = df[df["Profit"].notna()]

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.header("Filters")

    if "Category" in df.columns:
        cat = st.sidebar.multiselect("Category",
                                    df["Category"].dropna().unique(),
                                    df["Category"].dropna().unique())
        if cat:
            df = df[df["Category"].isin(cat)]

    if "Region" in df.columns:
        reg = st.sidebar.multiselect("Region",
                                    df["Region"].dropna().unique(),
                                    df["Region"].dropna().unique())
        if reg:
            df = df[df["Region"].isin(reg)]

    if "Order Date" in df.columns and not df["Order Date"].isna().all():
        min_date = df["Order Date"].min()
        max_date = df["Order Date"].max()

        date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range)
            temp = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]

            if not temp.empty:
                df = temp

    # ---------------- EMPTY CHECK ----------------
    if df.empty:
        st.warning("⚠️ No data available for selected filters.")
    else:
        # ================= OVERVIEW =================
        st.header("📊 Overview")

        total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
        total_profit = df["Profit"].sum() if "Profit" in df.columns else 0
        total_orders = len(df)

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Sales", f"{total_sales:,.0f}")
        c2.metric("📈 Total Profit", f"{total_profit:,.0f}")
        c3.metric("📦 Total Orders", total_orders)

        st.markdown("---")

        # ================= TRENDS =================
        st.header("📈 Trends")

        col1, col2 = st.columns(2)

        if "Order Date" in df.columns:
            trend = df.groupby("Order Date")["Sales"].sum().reset_index()
            fig1 = px.line(trend, x="Order Date", y="Sales", title="Sales Trend")
            col1.plotly_chart(fig1, use_container_width=True)

            df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
            monthly = df.groupby("Month")["Sales"].sum().reset_index()
            fig2 = px.line(monthly, x="Month", y="Sales", title="Monthly Trend")
            col2.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # ================= ANALYSIS =================
        st.header("📊 Analysis")

        col3, col4 = st.columns(2)

        if "Category" in df.columns:
            cat_data = df.groupby("Category")["Sales"].sum().reset_index()
            fig3 = px.bar(cat_data, x="Category", y="Sales", title="Category Performance")
            col3.plotly_chart(fig3, use_container_width=True)

        if "Region" in df.columns:
            reg_data = df.groupby("Region")["Sales"].sum().reset_index()
            fig4 = px.pie(reg_data, names="Region", values="Sales", title="Region Share")
            col4.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")

        # ================= PRODUCTS =================
        if "Product Name" in df.columns:
            st.header("📦 Top Products")

            top_products = (
                df.groupby("Product Name")["Sales"]
                .sum()
                .sort_values(ascending=False)
                .head(5)
            )

            st.dataframe(top_products, use_container_width=True)

        st.markdown("---")

        # ================= INSIGHTS =================
        st.header("🤖 Insights")

        if total_profit < 0:
            st.error("❌ Business is in loss")
        else:
            st.success("✅ Business is profitable")

        if "Category" in df.columns:
            top_cat = df.groupby("Category")["Sales"].sum().idxmax()
            st.info(f"🔥 Best Category: {top_cat}")

        # ================= DOWNLOAD =================
        csv = df.to_csv(index=False)

        st.download_button("📥 Download Filtered Data", csv, "filtered_data.csv")

        # ================= RESET =================
        if st.sidebar.button("🔄 Reset Filters"):
            st.experimental_rerun()

else:
    st.info("👆 Upload a CSV file to start")
