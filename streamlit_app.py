import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard", layout="wide")

st.title("📊 E-commerce Dashboard")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:

    # -------- SAFE LOAD --------
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1')
    except:
        df = pd.read_csv(uploaded_file)

    df.columns = df.columns.str.strip()

    # -------- SAFE DATE --------
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    # -------- REMOVE NULLS SAFE --------
    if "Sales" in df.columns:
        df = df[df["Sales"].notna()]
    if "Profit" in df.columns:
        df = df[df["Profit"].notna()]

    # -------- SIDEBAR --------
    st.sidebar.header("Filters")

    # Category
    if "Category" in df.columns:
        cat = st.sidebar.multiselect("Category",
                                    df["Category"].dropna().unique(),
                                    df["Category"].dropna().unique())
        if cat:
            df = df[df["Category"].isin(cat)]

    # Region
    if "Region" in df.columns:
        reg = st.sidebar.multiselect("Region",
                                    df["Region"].dropna().unique(),
                                    df["Region"].dropna().unique())
        if reg:
            df = df[df["Region"].isin(reg)]

    # Date
    if "Order Date" in df.columns and not df["Order Date"].isna().all():
        min_date = df["Order Date"].min()
        max_date = df["Order Date"].max()

        date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range)

            if start <= end:
                temp = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]
                if not temp.empty:
                    df = temp

    # -------- EMPTY --------
    if df.empty:
        st.warning("No data available")
    else:

        # KPIs safe
        total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
        total_profit = df["Profit"].sum() if "Profit" in df.columns else 0
        total_orders = len(df)

        # -------- TABS --------
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Overview", "Trends", "Analysis", "Products", "Insights"
        ])

        # -------- OVERVIEW --------
        with tab1:
            c1, c2, c3 = st.columns(3)
            c1.metric("Sales", f"{total_sales:,.0f}")
            c2.metric("Profit", f"{total_profit:,.0f}")
            c3.metric("Orders", total_orders)

        # -------- TRENDS --------
        with tab2:
            if "Order Date" in df.columns and "Sales" in df.columns:
                trend = df.groupby("Order Date")["Sales"].sum().reset_index()
                fig = px.line(trend, x="Order Date", y="Sales")
                st.plotly_chart(fig, use_container_width=True)

                # Monthly safe
                try:
                    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
                    monthly = df.groupby("Month")["Sales"].sum().reset_index()
                    fig2 = px.line(monthly, x="Month", y="Sales")
                    st.plotly_chart(fig2, use_container_width=True)
                except:
                    pass

        # -------- ANALYSIS --------
        with tab3:
            col1, col2 = st.columns(2)

            if "Category" in df.columns:
                cat_data = df.groupby("Category")["Sales"].sum().reset_index()
                fig3 = px.bar(cat_data, x="Category", y="Sales")
                col1.plotly_chart(fig3, use_container_width=True)

            if "Region" in df.columns:
                reg_data = df.groupby("Region")["Sales"].sum().reset_index()
                fig4 = px.pie(reg_data, names="Region", values="Sales")
                col2.plotly_chart(fig4, use_container_width=True)

            if "Sales" in df.columns and "Profit" in df.columns:
                fig5 = px.scatter(df, x="Sales", y="Profit", color="Category")
                st.plotly_chart(fig5, use_container_width=True)

        # -------- PRODUCTS --------
        with tab4:
            if "Product Name" in df.columns:
                top = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(10)
                st.dataframe(top)

        # -------- INSIGHTS --------
        with tab5:
            if total_profit < 0:
                st.error("Loss detected")
            else:
                st.success("Profitable")

            if "Category" in df.columns:
                try:
                    top_cat = df.groupby("Category")["Sales"].sum().idxmax()
                    st.info(f"Best Category: {top_cat}")
                except:
                    pass

        # -------- DOWNLOAD --------
        csv = df.to_csv(index=False)
        st.download_button("Download Data", csv, "data.csv")

else:
    st.info("Upload CSV to start")
