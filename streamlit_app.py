import streamlit as st
import pandas as pd
import plotly.express as px
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")
st.title("📊 E-commerce Sales Analytics Dashboard") 
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", "$2.3M")
col2.metric("Total Profit", "$286K")
col3.metric("Total Orders", "9,994")
col4.metric("Top Region", "West 🏆")
st.write("Explore sales trends, category performance & regional insights interactively") 
# ---------------- PAGE CONFIG ---------------- st.set_page_config(page_title="Dashboard", layout="wide")

uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

if uploaded_file:

    # -------- LOAD --------
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1')
    except:
        df = pd.read_csv(uploaded_file)

    df.columns = df.columns.str.strip()

    # -------- DATE SAFE --------
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    # -------- REMOVE NULLS --------
    if "Sales" in df.columns:
        df = df[df["Sales"].notna()]
    if "Profit" in df.columns:
        df = df[df["Profit"].notna()]

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.header("🎯 Filters")

    # Category
    if "Category" in df.columns:
        cat = st.sidebar.multiselect(
            "Category",
            df["Category"].dropna().unique(),
            df["Category"].dropna().unique()
        )
        if cat:
            df = df[df["Category"].isin(cat)]

    # Sub-Category
    if "Sub-Category" in df.columns:
        sub = st.sidebar.multiselect(
            "Sub-Category",
            df["Sub-Category"].dropna().unique(),
            df["Sub-Category"].dropna().unique()
        )
        if sub:
            df = df[df["Sub-Category"].isin(sub)]

    # Region
    if "Region" in df.columns:
        reg = st.sidebar.multiselect(
            "Region",
            df["Region"].dropna().unique(),
            df["Region"].dropna().unique()
        )
        if reg:
            df = df[df["Region"].isin(reg)]

    # Sales Range
    if "Sales" in df.columns:
        min_s = float(df["Sales"].min())
        max_s = float(df["Sales"].max())
        s_range = st.sidebar.slider("Sales Range", min_s, max_s, (min_s, max_s))
        df = df[(df["Sales"] >= s_range[0]) & (df["Sales"] <= s_range[1])]

    # Profit Range
    if "Profit" in df.columns:
        min_p = float(df["Profit"].min())
        max_p = float(df["Profit"].max())
        p_range = st.sidebar.slider("Profit Range", min_p, max_p, (min_p, max_p))
        df = df[(df["Profit"] >= p_range[0]) & (df["Profit"] <= p_range[1])]

    # Profit Type
    if "Profit" in df.columns:
        p_type = st.sidebar.selectbox("Profit Type", ["All", "Profit Only", "Loss Only"])
        if p_type == "Profit Only":
            df = df[df["Profit"] > 0]
        elif p_type == "Loss Only":
            df = df[df["Profit"] < 0]

    # Search
    if "Product Name" in df.columns:
        search = st.sidebar.text_input("🔍 Search Product")
        if search:
            df = df[df["Product Name"].str.contains(search, case=False, na=False)]

    # Top N
    top_n = st.sidebar.slider("Top N Products", 5, 20, 10)

    # Date filter
    if "Order Date" in df.columns and not df["Order Date"].isna().all():
        min_date = df["Order Date"].min()
        max_date = df["Order Date"].max()

        date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range)
            temp = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]
            if not temp.empty:
                df = temp

    # -------- EMPTY --------
    if df.empty:
        st.warning("⚠️ No data after filters")
    else:

        # SAFE KPIs
        total_sales = df["Sales"].sum() if "Sales" in df.columns else 0
        total_profit = df["Profit"].sum() if "Profit" in df.columns else 0
        total_orders = len(df)

        # ---------------- TABS ----------------
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
                st.plotly_chart(px.line(trend, x="Order Date", y="Sales"),
                                use_container_width=True)

                try:
                    df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
                    monthly = df.groupby("Month")["Sales"].sum().reset_index()
                    st.plotly_chart(px.line(monthly, x="Month", y="Sales"),
                                    use_container_width=True)
                except:
                    pass

        # -------- ANALYSIS --------
        with tab3:
            col1, col2 = st.columns(2)

            if "Category" in df.columns and "Sales" in df.columns:
                cat_data = df.groupby("Category")["Sales"].sum().reset_index()
                col1.plotly_chart(px.bar(cat_data, x="Category", y="Sales"),
                                  use_container_width=True)

            if "Region" in df.columns and "Sales" in df.columns:
                reg_data = df.groupby("Region")["Sales"].sum().reset_index()
                col2.plotly_chart(px.pie(reg_data, names="Region", values="Sales"),
                                  use_container_width=True)

            if "Sales" in df.columns and "Profit" in df.columns:
                st.plotly_chart(px.scatter(df, x="Sales", y="Profit", color="Category"),
                                use_container_width=True)

        # -------- PRODUCTS --------
        with tab4:
            if "Product Name" in df.columns and "Sales" in df.columns:
                top = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(top_n)
                st.dataframe(top, use_container_width=True)

        # -------- INSIGHTS --------
        with tab5:
            if total_profit < 0:
                st.error("Loss detected")
            else:
                st.success("Profitable")

            if "Category" in df.columns and "Sales" in df.columns:
                try:
                    top_cat = df.groupby("Category")["Sales"].sum().idxmax()
                    st.info(f"Best Category: {top_cat}")
                except:
                    pass

        # -------- DOWNLOAD --------
        st.download_button("Download Data", df.to_csv(index=False), "data.csv")

        # -------- RESET --------
        if st.sidebar.button("Reset Filters"):
            st.experimental_rerun()

else:
    st.info("Upload CSV to start")
