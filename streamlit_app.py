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
    df.columns = df.columns.str.strip()  # clean column names
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
date_range = st.sidebar.date_input("Select Date Range", [df['Order Date'].min(), df['Order Date'].max()])
category = st.sidebar.multiselect("Category", df['Category'].dropna().unique())
year_options = sorted(df['Year'].unique())
year = st.sidebar.multiselect("Year", year_options)

# ------------------ APPLY FILTERS ------------------
filtered_df = df.copy()
filtered_df = filtered_df[
    (filtered_df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (filtered_df['Order Date'] <= pd.to_datetime(date_range[1]))
]
if category:
    filtered_df = filtered_df[filtered_df['Category'].isin(category)]
if year:
    filtered_df = filtered_df[filtered_df['Year'].isin(year)]

# ------------------ SAFE METRICS FUNCTION ------------------
def safe_sum(df, col):
    return df[col].sum() if col in df.columns and not df.empty else 0

def safe_mean(df, col):
    return df[col].mean() if col in df.columns and not df.empty else 0

def safe_count(df):
    return df.shape[0] if not df.empty else 0

# ------------------ KEY METRICS ------------------
st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"{safe_sum(filtered_df,'Sales'):,.0f}")
col2.metric("📈 Total Profit", f"{safe_sum(filtered_df,'Profit'):,.0f}")
col3.metric("🛒 Orders", safe_count(filtered_df))
col4.metric("📦 Avg Order Value", f"{safe_mean(filtered_df,'Sales'):,.0f}")

# ------------------ DAILY SALES ------------------
st.subheader("📈 Daily Sales Trend")
if not filtered_df.empty and 'Sales' in filtered_df.columns:
    daily_sales = filtered_df.groupby('Order Date')['Sales'].sum()
    plt.figure(figsize=(10,4))
    daily_sales.plot(title="Daily Sales", color='green')
    plt.xlabel("Date")
    plt.ylabel("Sales")
    st.pyplot(plt)
else:
    st.info("No sales data for this selection.")

# ------------------ SALES VS PROFIT ------------------
st.subheader("📊 Sales vs Profit Trend")
if not filtered_df.empty and 'Sales' in filtered_df.columns and 'Profit' in filtered_df.columns:
    trend = filtered_df.groupby('Order Date')[['Sales','Profit']].sum()
    st.line_chart(trend)
else:
    st.info("No sales/profit data for this selection.")

# ------------------ ORDER VOLUME ------------------
st.subheader("📦 Order Volume Trend")
if not filtered_df.empty:
    orders = filtered_df.groupby('Order Date').size()
    plt.figure(figsize=(10,4))
    orders.plot(title="Orders per Day", color='orange')
    plt.xlabel("Date")
    plt.ylabel("Number of Orders")
    st.pyplot(plt)
else:
    st.info("No order data for this selection.")

# ------------------ MOVING AVERAGE ------------------
st.subheader("📉 Moving Average (7 Days)")
if not filtered_df.empty and 'Sales' in filtered_df.columns:
    rolling = daily_sales.rolling(7).mean()
    plt.figure(figsize=(10,4))
    daily_sales.plot(label="Actual", color='blue')
    rolling.plot(label="7-Day Avg", color='red')
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Sales")
    st.pyplot(plt)

# ------------------ MONTHLY TREND ------------------
st.subheader("📅 Monthly Trend")
if not filtered_df.empty and 'Sales' in filtered_df.columns:
    monthly = filtered_df.groupby(['Year','Month'])['Sales'].sum().reset_index()
    plt.figure(figsize=(10,4))
    sns.lineplot(data=monthly, x='Month', y='Sales', hue='Year', marker='o')
    plt.title("Monthly Sales Trend")
    st.pyplot(plt)

# ------------------ CATEGORY-WISE ------------------
st.subheader("📦 Category-wise Sales")
if not filtered_df.empty and 'Sales' in filtered_df.columns and 'Category' in filtered_df.columns:
    cat_sales = filtered_df.groupby('Category')['Sales'].sum()
    plt.figure(figsize=(6,6))
    cat_sales.plot(kind='pie', autopct='%1.1f%%', title="Category-wise Sales")
    st.pyplot(plt)

# ------------------ PROFIT RATIO ------------------
st.subheader("💡 Profit Ratio")
if not filtered_df.empty and 'Profit' in filtered_df.columns and 'Sales' in filtered_df.columns:
    filtered_df['Profit Ratio'] = np.where(filtered_df['Sales']!=0,
                                           filtered_df['Profit']/filtered_df['Sales'], 0)
    st.write("Average Profit Ratio:", round(filtered_df['Profit Ratio'].mean(),3))
else:
    st.info("Profit ratio cannot be calculated for this selection.")

# ------------------ LOSS ORDERS ------------------
st.subheader("⚠️ Loss Making Orders")
if not filtered_df.empty and 'Profit' in filtered_df.columns:
    loss_df = filtered_df[filtered_df['Profit'] < 0]
    st.write("Total Loss Orders:", loss_df.shape[0])
else:
    st.info("No loss orders for this selection.")

# ------------------ DOWNLOAD ------------------
st.subheader("⬇️ Download Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "filtered_data.csv")

# ------------------ RAW DATA ------------------
st.subheader("📄 Raw Data")
if st.checkbox("Show Data"):
    st.write(filtered_df)
