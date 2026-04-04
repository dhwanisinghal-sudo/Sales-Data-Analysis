import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# ---------------- CLEAN DARK THEME ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0a0f1c, #111827);
    color: #e5e7eb;
}
h1 {
    text-align: center;
    color: #38bdf8;
}
[data-testid="metric-container"] {
    background: rgba(17, 24, 39, 0.9);
    padding: 15px;
    border-radius: 12px;
}
section[data-testid="stSidebar"] {
    background: #020617;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1>📊 E-commerce Analytics Dashboard</h1>", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')
    df.columns = df.columns.str.strip()

    # ---------------- CLEAN ----------------
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    for col in ["Sales", "Profit"]:
        if col in df.columns:
            df = df[df[col].notna()]

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.header("🎯 Filters")

    if "Category" in df.columns:
        cat = st.sidebar.multiselect("Category", df["Category"].unique(), df["Category"].unique())
        df = df[df["Category"].isin(cat)]

    if "Region" in df.columns:
        reg = st.sidebar.multiselect("Region", df["Region"].unique(), df["Region"].unique())
        df = df[df["Region"].isin(reg)]

    if "Order Date" in df.columns:
        min_date = df["Order Date"].min()
        max_date = df["Order Date"].max()

        st.sidebar.write("📅 Available:", min_date.date(), "to", max_date.date())

        date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range)
            temp = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]

            if not temp.empty:
                df = temp
            else:
                st.warning("⚠️ No data → showing full dataset")

    if df.empty:
        st.error("❌ No data available")
    else:
        # ---------------- KPIs ----------------
        sales = int(df["Sales"].sum())
        profit = int(df["Profit"].sum())
        orders = df.shape[0]

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Sales", sales)
        c2.metric("📈 Profit", profit)
        c3.metric("📦 Orders", orders)

        # ---------------- SALES TREND ----------------
        trend = df.groupby("Order Date")["Sales"].sum().reset_index()

        fig1 = px.line(trend, x="Order Date", y="Sales", markers=True)
        fig1.update_layout(template="plotly_dark",
                           paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)

        # ---------------- CATEGORY ----------------
        cat_data = df.groupby("Category")["Sales"].sum().reset_index()

        fig2 = px.bar(cat_data, x="Category", y="Sales", text_auto=True)
        fig2.update_layout(template="plotly_dark",
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)

        # ---------------- REGION ----------------
        reg_data = df.groupby("Region")["Sales"].sum().reset_index()

        fig3 = px.pie(reg_data, names="Region", values="Sales")
        fig3.update_layout(template="plotly_dark",
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)

        # ---------------- MONTHLY TREND ----------------
        df["Month"] = df["Order Date"].dt.to_period("M").astype(str)
        monthly = df.groupby("Month")["Sales"].sum().reset_index()

        fig4 = px.line(monthly, x="Month", y="Sales", markers=True)
        fig4.update_layout(template="plotly_dark",
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig4, use_container_width=True)

        # ---------------- PROFIT VS SALES ----------------
        fig5 = px.scatter(df, x="Sales", y="Profit",
                          color="Category", size="Sales")
        fig5.update_layout(template="plotly_dark",
                           paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig5, use_container_width=True)

        # ---------------- TOP PRODUCTS ----------------
        if "Product Name" in df.columns:
            st.subheader("🔥 Top Products")

            top_products = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(5)
            st.dataframe(top_products)

        # ---------------- SUB CATEGORY ----------------
        if "Sub-Category" in df.columns:
            sub = df.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False).head(10)

            fig6 = px.bar(sub, x=sub.values, y=sub.index, orientation='h')
            fig6.update_layout(template="plotly_dark",
                               paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig6, use_container_width=True)

        # ---------------- AI INSIGHTS ----------------
        st.subheader("🤖 Insights")

        if profit < 0:
            st.error("❌ Loss detected")
        else:
            st.success("✅ Business profitable")

        top_cat = df.groupby("Category")["Sales"].sum().idxmax()
        st.info(f"🔥 Best Category: {top_cat}")

        # ---------------- DOWNLOAD ----------------
        csv = df.to_csv(index=False)

        st.download_button("📥 Download Data", csv, "filtered_data.csv")

        # ---------------- RESET ----------------
        if st.sidebar.button("🔄 Reset Filters"):
            st.experimental_rerun()

else:
    st.info("👆 Upload CSV to start")
