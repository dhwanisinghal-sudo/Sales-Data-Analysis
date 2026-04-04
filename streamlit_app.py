import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI E-commerce Dashboard", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
.card {
    background: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;color:#00f2fe;'>🤖 AI E-commerce Dashboard</h1>", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload your CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='latin1')
    df.columns = df.columns.str.strip()

    # ---------------- CLEANING ----------------
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    df = df.dropna()

    # ---------------- SIDEBAR FILTERS ----------------
    st.sidebar.header("🎯 Filters")

    if "Category" in df.columns:
        cat = st.sidebar.multiselect("Category", df["Category"].unique(), df["Category"].unique())
        df = df[df["Category"].isin(cat)]

    if "Region" in df.columns:
        reg = st.sidebar.multiselect("Region", df["Region"].unique(), df["Region"].unique())
        df = df[df["Region"].isin(reg)]

    if "Order Date" in df.columns:
        start, end = st.sidebar.date_input("Date Range",
                                          [df["Order Date"].min(), df["Order Date"].max()])
        df = df[(df["Order Date"] >= pd.to_datetime(start)) &
                (df["Order Date"] <= pd.to_datetime(end))]

    # ---------------- CHECK ----------------
    if df.empty:
        st.warning("⚠️ No data after filters")
    else:
        # ---------------- KPIs ----------------
        sales = int(df["Sales"].sum()) if "Sales" in df.columns else 0
        profit = int(df["Profit"].sum()) if "Profit" in df.columns else 0
        orders = df.shape[0]

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Sales", sales)
        c2.metric("📈 Profit", profit)
        c3.metric("📦 Orders", orders)

        # ---------------- SALES TREND ----------------
        if "Order Date" in df.columns:
            trend = df.groupby("Order Date")["Sales"].sum().reset_index()

            fig = px.line(trend, x="Order Date", y="Sales",
                          title="📊 Sales Trend", markers=True)
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        # ---------------- CATEGORY ----------------
        if "Category" in df.columns:
            cat_data = df.groupby("Category")["Sales"].sum().reset_index()

            fig2 = px.bar(cat_data, x="Category", y="Sales",
                          title="🏆 Category Performance", text_auto=True)
            fig2.update_layout(template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        # ---------------- REGION ----------------
        if "Region" in df.columns:
            reg_data = df.groupby("Region")["Sales"].sum().reset_index()

            fig3 = px.pie(reg_data, names="Region", values="Sales",
                          title="🌍 Region Share")
            fig3.update_layout(template="plotly_dark")
            st.plotly_chart(fig3, use_container_width=True)

        # ---------------- AI INSIGHTS ----------------
        st.subheader("🤖 AI Insights")

        try:
            top_cat = df.groupby("Category")["Sales"].sum().idxmax()
            worst_cat = df.groupby("Category")["Sales"].sum().idxmin()

            st.success(f"🔥 Best Category: {top_cat}")
            st.warning(f"⚠️ Weak Category: {worst_cat}")
        except:
            pass

        if profit < 0:
            st.error("❌ Loss detected! Reduce discounts or costs")
        else:
            st.info("✅ Business is profitable")

        # ---------------- FORECAST ----------------
        st.subheader("🔮 Simple Sales Forecast (Next 7 Days)")

        if "Order Date" in df.columns:
            trend = df.groupby("Order Date")["Sales"].sum().reset_index()

            trend = trend.sort_values("Order Date")

            # Moving average
            trend["MA"] = trend["Sales"].rolling(7).mean()

            last_date = trend["Order Date"].max()

            future_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
            future_sales = [trend["MA"].iloc[-1]] * 7

            forecast_df = pd.DataFrame({
                "Order Date": future_dates,
                "Sales": future_sales
            })

            full_df = pd.concat([trend[["Order Date", "Sales"]], forecast_df])

            fig4 = px.line(full_df, x="Order Date", y="Sales",
                           title="📈 Forecast vs Actual")
            fig4.update_layout(template="plotly_dark")
            st.plotly_chart(fig4, use_container_width=True)

else:
    st.info("👆 Upload CSV to start")
