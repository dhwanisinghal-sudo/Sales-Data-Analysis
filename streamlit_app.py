import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Optional forecasting
try:
    from statsmodels.tsa.arima.model import ARIMA
    forecasting_available = True
except:
    forecasting_available = False

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")
st.title("🛒 E-commerce Order Trend & Seasonal Analysis")
st.markdown("Complete dashboard with trends, seasonality & insights 📊")

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv", encoding='latin1')
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ------------------ PREPROCESS ------------------
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df = df.dropna(subset=['Order Date'])
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
df['Month Name'] = df['Order Date'].dt.strftime('%b')
df['Weekday'] = df['Order Date'].dt.day_name()
df['Quarter'] = df['Order Date'].dt.quarter

# ------------------ SIDEBAR FILTERS ------------------
st.sidebar.header("🔍 Filters")

# Date range filter
date_range = st.sidebar.date_input("Select Date Range",
                                  [df['Order Date'].min(), df['Order Date'].max()])

# Category filter
category = st.sidebar.multiselect("Category", df['Category'].dropna().unique())

# Year filter
year_options = sorted(df['Year'].unique())
year = st.sidebar.multiselect("Year", year_options)

# Apply filters
filtered_df = df.copy()
filtered_df = filtered_df[
    (filtered_df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (filtered_df['Order Date'] <= pd.to_datetime(date_range[1]))
]
if category:
    filtered_df = filtered_df[filtered_df['Category'].isin(category)]
if year:
    filtered_df = filtered_df[filtered_df['Year'].isin(year)]

# ------------------ KEY METRICS ------------------
st.subheader("📊 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

def safe_sum(df, col):
    return df[col].sum() if col in df.columns else 0

col1.metric("💰 Total Sales", f"{safe_sum(filtered_df,'Sales'):,.0f}")
col2.metric("📈 Total Profit", f"{safe_sum(filtered_df,'Profit'):,.0f}")
col3.metric("🛒 Orders", filtered_df.shape[0])
col4.metric("📦 Avg Order Value", f"{filtered_df['Sales'].mean():,.0f}" if 'Sales' in filtered_df.columns else "N/A")

# Sales Growth % (year over year)
if 'Sales' in filtered_df.columns and len(year) >= 2:
    current_year = max(year)
    prev_year = current_year - 1
    current_sales = safe_sum(filtered_df[filtered_df['Year']==current_year], 'Sales')
    prev_sales = safe_sum(filtered_df[filtered_df['Year']==prev_year], 'Sales')
    growth = ((current_sales - prev_sales)/prev_sales)*100 if prev_sales != 0 else 0
    col5.metric("📈 Sales Growth %", f"{growth:.2f}%")
else:
    col5.metric("📈 Sales Growth %", "N/A")

# ------------------ DAILY SALES TREND ------------------
st.subheader("📈 Daily Sales Trend")
if 'Sales' in filtered_df.columns:
    daily_sales = filtered_df.groupby('Order Date')['Sales'].sum()
    plt.figure()
    daily_sales.plot(title="Daily Sales")
    st.pyplot(plt)

# ------------------ SALES vs PROFIT TREND ------------------
st.subheader("📊 Sales vs Profit Trend")
if 'Sales' in filtered_df.columns and 'Profit' in filtered_df.columns:
    trend = filtered_df.groupby('Order Date')[['Sales','Profit']].sum()
    st.line_chart(trend)

# ------------------ ORDER VOLUME ------------------
st.subheader("📦 Order Volume Trend")
orders = filtered_df.groupby('Order Date').size()
plt.figure()
orders.plot(title="Orders per Day")
st.pyplot(plt)

# ------------------ MOVING AVERAGE ------------------
st.subheader("📉 Moving Average (7 Days)")
if 'Sales' in filtered_df.columns:
    rolling = daily_sales.rolling(7).mean()
    plt.figure()
    daily_sales.plot(label="Actual")
    rolling.plot(label="7-Day Avg")
    plt.legend()
    st.pyplot(plt)

# ------------------ MONTHLY TREND ------------------
st.subheader("📅 Monthly Trend")
if 'Sales' in filtered_df.columns:
    monthly = filtered_df.groupby(['Year','Month'])['Sales'].sum().reset_index()
    plt.figure()
    sns.lineplot(data=monthly, x='Month', y='Sales', hue='Year', marker='o')
    st.pyplot(plt)

# ------------------ TOP PRODUCTS ------------------
st.subheader("🏆 Top 10 Sub-Categories")
if 'Sub-Category' in filtered_df.columns:
    top_sub = filtered_df.groupby('Sub-Category')['Sales'].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_sub)

# ------------------ REGION / STATE ------------------
if 'Region' in filtered_df.columns:
    st.subheader("🌍 Sales by Region")
    region_sales = filtered_df.groupby('Region')['Sales'].sum()
    st.bar_chart(region_sales)

# ------------------ TOP CUSTOMERS ------------------
if 'Customer Name' in filtered_df.columns:
    st.subheader("👑 Top 10 Customers")
    top_customers = filtered_df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False).head(10)
    st.write(top_customers)

# ------------------ SEASONAL ANALYSIS ------------------
st.subheader("🌦 Seasonal Analysis")
if 'Sales' in filtered_df.columns:
    seasonal = filtered_df.groupby('Month Name')['Sales'].sum().reindex(
        ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    plt.figure()
    seasonal.plot(kind='bar', title="Seasonal Sales")
    st.pyplot(plt)

# ------------------ WEEKDAY SALES ------------------
st.subheader("📆 Weekday Sales")
if 'Sales' in filtered_df.columns:
    weekday_sales = filtered_df.groupby('Weekday')['Sales'].sum().reindex(
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    plt.figure()
    weekday_sales.plot(kind='bar', title="Weekday Sales")
    st.pyplot(plt)

# ------------------ QUARTERLY SALES ------------------
st.subheader("📅 Quarterly Sales")
if 'Sales' in filtered_df.columns:
    quarter = filtered_df.groupby('Quarter')['Sales'].sum()
    plt.figure()
    quarter.plot(kind='bar', title="Quarterly Sales")
    st.pyplot(plt)

# ------------------ CATEGORY-WISE ------------------
st.subheader("📦 Category-wise Sales")
if 'Sales' in filtered_df.columns:
    cat_sales = filtered_df.groupby('Category')['Sales'].sum()
    plt.figure()
    cat_sales.plot(kind='pie', autopct='%1.1f%%', title="Category-wise Sales")
    st.pyplot(plt)

# ------------------ PROFIT RATIO ------------------
st.subheader("💡 Profit Ratio")
if 'Sales' in filtered_df.columns and 'Profit' in filtered_df.columns:
    filtered_df['Profit Ratio'] = filtered_df['Profit']/filtered_df['Sales']
    st.write("Average Profit Ratio:", round(filtered_df['Profit Ratio'].mean(),3))

# ------------------ LOSS ORDERS ------------------
st.subheader("⚠️ Loss Making Orders")
if 'Profit' in filtered_df.columns:
    loss_df = filtered_df[filtered_df['Profit'] < 0]
    st.write("Total Loss Orders:", loss_df.shape[0])

# ------------------ FORECAST ------------------
if forecasting_available and 'Sales' in df.columns:
    st.subheader("🔮 Sales Forecast (Next 30 Days)")
    ts = df.groupby('Order Date')['Sales'].sum()
    try:
        model = ARIMA(ts, order=(5,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=30)
        plt.figure()
        ts.plot(label='Actual')
        forecast.plot(label='Forecast')
        plt.legend()
        st.pyplot(plt)
    except:
        st.warning("Forecasting failed due to data limitations")

# ------------------ PEAK MONTH ------------------
st.subheader("🏆 Peak Sales Month")
if 'Sales' in df.columns:
    peak_month = df.groupby('Month Name')['Sales'].sum().idxmax()
    st.success(f"Highest sales in: {peak_month}")

# ------------------ BUSINESS INSIGHTS ------------------
st.subheader("🧠 Business Insights")
if 'Sales' in df.columns:
    st.write("📦 Top Category:", df.groupby('Category')['Sales'].sum().idxmax())
if 'Profit' in df.columns:
    st.write("💰 Most Profitable Category:", df.groupby('Category')['Profit'].sum().idxmax())

# ------------------ DOWNLOAD ------------------
st.subheader("⬇️ Download Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "filtered_data.csv")

# ------------------ RAW DATA ------------------
st.subheader("📄 Raw Data")
if st.checkbox("Show Data"):
    st.write(filtered_df)
