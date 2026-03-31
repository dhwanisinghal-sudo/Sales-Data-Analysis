import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# Title
st.title("🛒 E-commerce Order Trend & Seasonal Analysis")

# Load data
df = pd.read_csv('train.csv')

# Convert date
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
df['Month'] = df['Order Date'].dt.month
df['Year'] = df['Order Date'].dt.year

# Sidebar filters
st.sidebar.header("🔎 Filters")
category = st.sidebar.selectbox("Select Category", df['Category'].unique())
region = st.sidebar.selectbox("Select Region", df['Region'].unique())

filtered_df = df[(df['Category'] == category) & (df['Region'] == region)]

# Metrics
st.subheader("📌 Key Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"${filtered_df['Sales'].sum():,.0f}")
col2.metric("Total Orders", filtered_df.shape[0])
col3.metric("Average Sales", f"${filtered_df['Sales'].mean():.2f}")

# Layout columns
col1, col2 = st.columns(2)

# Monthly Trend
with col1:
    st.subheader("📈 Monthly Sales Trend")
    monthly_sales = filtered_df.groupby('Month')['Sales'].sum()
    fig, ax = plt.subplots()
    monthly_sales.plot(marker='o', ax=ax)
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales")
    st.pyplot(fig)

# Category Sales
with col2:
    st.subheader("📦 Category Sales")
    cat_sales = df.groupby('Category')['Sales'].sum()
    fig, ax = plt.subplots()
    cat_sales.plot(kind='bar', ax=ax)
    st.pyplot(fig)

# Second row
col3, col4 = st.columns(2)

# Region Sales
with col3:
    st.subheader("🌍 Region Sales")
    reg_sales = df.groupby('Region')['Sales'].sum()
    fig, ax = plt.subplots()
    reg_sales.plot(kind='bar', ax=ax)
    st.pyplot(fig)

# Segment Pie
with col4:
    st.subheader("👥 Segment Distribution")
    seg = df.groupby('Segment')['Sales'].sum()
    fig, ax = plt.subplots()
    seg.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    st.pyplot(fig)

# Footer
st.markdown("---")
st.markdown("✨ Developed using Streamlit | Data Analysis Project")
