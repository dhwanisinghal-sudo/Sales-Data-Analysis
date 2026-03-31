import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.arima.model import ARIMA

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# ------------------ TITLE ------------------
st.title("🛒 E-commerce Order Trend & Seasonal Analysis")
st.markdown("Complete dashboard with trends, seasonality, forecasting & business insights 📊")

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    df = pd.read_csv("train.csv", encoding='latin1')
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

category = st.sidebar.multiselect("Category", df['Category'].dropna().unique())
year = st.sidebar.multiselect("Year", df['Year'].unique())

filtered_df = df.copy()

if category:
    filtered_df = filtered_df[filtered_df['Category'].isin(category)]

if year:
    filtered_df = filtered_df[filtered_df['Year'].isin(year)]

# ------------------ KPIs ------------------
st.subheader("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"{filtered_df['Sales'].sum():,.0f}")
col2.metric("📈 Total Profit", f"{filtered_df['Profit'].sum():,.0f}")
col3.metric("🛒 Orders", filtered_df.shape[0])
col4.metric("📦 Avg Order Value", f"{filtered_df['Sales'].mean():,.0f}")

# ------------------ DAILY TREND ------------------
st.subheader("📈 Daily Sales Trend")

daily_sales = filtered_df.groupby('Order Date')['Sales'].sum()

plt.figure()
daily_sales.plot()
st.pyplot(plt)

# ------------------ ORDER COUNT TREND ------------------
st.subheader("📦 Order Volume Trend")

orders = filtered_df.groupby('Order Date').size()

plt.figure()
orders.plot()
st.pyplot(plt)

# ------------------ MOVING AVERAGE ------------------
st.subheader("📉 Moving Average (7 Days)")

rolling = daily_sales.rolling(window=7).mean()

plt.figure()
daily_sales.plot(label="Actual")
rolling.plot(label="7-Day Avg")
plt.legend()
st.pyplot(plt)

# ------------------ MONTHLY TREND ------------------
st.subheader("📅 Monthly Trend")

monthly = filtered_df.groupby(['Year','Month'])['Sales'].sum().reset_index()

plt.figure()
sns.lineplot(data=monthly, x='Month', y='Sales', hue='Year', marker='o')
st.pyplot(plt)

# ------------------ YEAR-OVER-YEAR ------------------
st.subheader("📊 Year-over-Year Growth")

yoy = df.groupby('Year')['Sales'].sum().pct_change() * 100
st.line_chart(yoy)

# ------------------ SEASONAL ANALYSIS ------------------
st.subheader("🌦 Seasonal Analysis")

seasonal = filtered_df.groupby('Month Name')['Sales'].sum().reindex(
    ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
)

plt.figure()
seasonal.plot(kind='bar')
st.pyplot(plt)

# ------------------ WEEKDAY ANALYSIS ------------------
st.subheader("📆 Weekday Sales")

weekday_sales = filtered_df.groupby('Weekday')['Sales'].sum().reindex(
    ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
)

plt.figure()
weekday_sales.plot(kind='bar')
st.pyplot(plt)

# ------------------ QUARTERLY ------------------
st.subheader("📅 Quarterly Sales")

quarter = filtered_df.groupby('Quarter')['Sales'].sum()

plt.figure()
quarter.plot(kind='bar')
st.pyplot(plt)

# ------------------ CATEGORY ------------------
st.subheader("📦 Category-wise Sales")

cat_sales = filtered_df.groupby('Category')['Sales'].sum()

plt.figure()
cat_sales.plot(kind='pie', autopct='%1.1f%%')
st.pyplot(plt)

# ------------------ PROFIT VS SALES ------------------
st.subheader("💸 Profit vs Sales")

plt.figure()
sns.scatterplot(data=filtered_df, x='Sales', y='Profit', hue='Category')
st.pyplot(plt)

# ------------------ HEATMAP ------------------
st.subheader("🔥 Correlation Heatmap")

plt.figure()
sns.heatmap(filtered_df[['Sales','Profit']].corr(), annot=True)
st.pyplot(plt)

# ------------------ PROFIT RATIO ------------------
st.subheader("💡 Profit Ratio")

filtered_df['Profit Ratio'] = filtered_df['Profit'] / filtered_df['Sales']
st.write("Average Profit Ratio:", filtered_df['Profit Ratio'].mean())

# ------------------ LOSS ORDERS ------------------
st.subheader("⚠️ Loss Making Orders")

loss_df = filtered_df[filtered_df['Profit'] < 0]
st.write("Total Loss Orders:", loss_df.shape[0])

# ------------------ FORECAST ------------------
st.subheader("🔮 Sales Forecast (Next 30 Days)")

ts = df.groupby('Order Date')['Sales'].sum()

model = ARIMA(ts, order=(5,1,0))
model_fit = model.fit()

forecast = model_fit.forecast(steps=30)

plt.figure()
ts.plot(label='Actual')
forecast.plot(label='Forecast')
plt.legend()
st.pyplot(plt)

# ------------------ PEAK MONTH ------------------
st.subheader("🏆 Peak Sales Month")

peak_month = df.groupby('Month Name')['Sales'].sum().idxmax()
st.success(f"Highest sales in: {peak_month}")

# ------------------ INSIGHTS ------------------
st.subheader("🧠 Business Insights")

st.write("📦 Top Category:", df.groupby('Category')['Sales'].sum().idxmax())
st.write("💰 Most Profitable Category:", df.groupby('Category')['Profit'].sum().idxmax())

# ------------------ DOWNLOAD ------------------
st.subheader("⬇️ Download Data")

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "filtered_data.csv")

# ------------------ RAW DATA ------------------
st.subheader("📄 Raw Data")

if st.checkbox("Show Data"):
    st.write(filtered_df)
