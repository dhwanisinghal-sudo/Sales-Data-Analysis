import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Dashboard", layout="wide")

# ---------------- DARK TECH CSS ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: radial-gradient(circle at 20% 20%, #0f2027, #203a43, #000000);
    color: #e0e0e0;
}

/* Title */
h1 {
    text-align: center;
    color: #00f2fe;
    text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
}

/* KPI Cards */
[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(0,255,255,0.2);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 10px rgba(0,255,255,0.2);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #000000, #0f2027);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #00f2fe, #4facfe);
    color: black;
    border-radius: 10px;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-thumb {
    background: #00f2fe;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown("<h1>⚡ AI E-commerce Command Center</h1>", unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("📂 Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='latin1')
    df.columns = df.columns.str.strip()

    # ---------------- CLEAN ----------------
    if "Order Date" in df.columns:
        df["Order Date"] = pd.to_datetime(df["Order Date"], errors='coerce')

    # only important columns clean
    for col in ["Sales", "Profit"]:
        if col in df.columns:
            df = df[df[col].notna()]

    # ---------------- SIDEBAR ----------------
    st.sidebar.header("🎯 Filters")

    # Category
    if "Category" in df.columns:
        cat = st.sidebar.multiselect("Category",
                                    df["Category"].unique(),
                                    df["Category"].unique())
        df = df[df["Category"].isin(cat)]

    # Region
    if "Region" in df.columns:
        reg = st.sidebar.multiselect("Region",
                                    df["Region"].unique(),
                                    df["Region"].unique())
        df = df[df["Region"].isin(reg)]

    # Date
    if "Order Date" in df.columns:
        min_date = df["Order Date"].min()
        max_date = df["Order Date"].max()

        st.sidebar.write("📅 Available:", min_date.date(), "to", max_date.date())

        date_range = st.sidebar.date_input("Date Range", [min_date, max_date])

        if len(date_range) == 2:
            start, end = pd.to_datetime(date_range)

            if start <= end:
                filtered_df = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)]

                # AUTO FIX if empty
                if not filtered_df.empty:
                    df = filtered_df
                else:
                    st.warning("⚠️ No data in selected range → showing full data")

    # ---------------- CHECK ----------------
    if df.empty:
        st.error("❌ No data available")
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

            fig = px.line(trend, x="Order Date", y="Sales", markers=True)
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        # ---------------- CATEGORY ----------------
        if "Category" in df.columns:
            cat_data = df.groupby("Category")["Sales"].sum().reset_index()

            fig2 = px.bar(cat_data, x="Category", y="Sales", text_auto=True)
            fig2.update_layout(template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

        # ---------------- REGION ----------------
        if "Region" in df.columns:
            reg_data = df.groupby("Region")["Sales"].sum().reset_index()

            fig3 = px.pie(reg_data, names="Region", values="Sales")
            fig3.update_layout(template="plotly_dark")
            st.plotly_chart(fig3, use_container_width=True)

        # ---------------- AI INSIGHTS ----------------
        st.subheader("🤖 AI Insights")

        if "Category" in df.columns:
            top = df.groupby("Category")["Sales"].sum().idxmax()
            low = df.groupby("Category")["Sales"].sum().idxmin()

            st.success(f"🔥 Best Category: {top}")
            st.warning(f"⚠️ Weak Category: {low}")

        if profit < 0:
            st.error("❌ Loss detected!")
        else:
            st.info("✅ Profitable business")

        # ---------------- FORECAST ----------------
        st.subheader("🔮 Forecast (Next 7 Days)")

        if "Order Date" in df.columns:
            trend = df.groupby("Order Date")["Sales"].sum().reset_index()
            trend = trend.sort_values("Order Date")

            trend["MA"] = trend["Sales"].rolling(7).mean()

            last = trend["Order Date"].max()

            future_dates = [last + timedelta(days=i) for i in range(1, 8)]
            future_sales = [trend["MA"].iloc[-1]] * 7

            forecast = pd.DataFrame({
                "Order Date": future_dates,
                "Sales": future_sales
            })

            full = pd.concat([trend[["Order Date", "Sales"]], forecast])

            fig4 = px.line(full, x="Order Date", y="Sales")
            fig4.update_layout(template="plotly_dark")
            st.plotly_chart(fig4, use_container_width=True)

else:
    st.info("👆 Upload CSV to start")
