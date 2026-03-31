import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Optional forecasting (safe import)
try:
    from statsmodels.tsa.arima.model import ARIMA
    forecasting_available = True
except:
    forecasting_available = False

st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

st.title("🛒 E-commerce Order Trend & Seasonal Analysis")
st.markdown("Complete dashboard with trends, seasonality & insights 📊")

@st.cache_data
def load_data():
    df = pd.read_csv("train.csv", encoding='latin1')
    df.columns = df.columns.str.strip()  # remove spaces
    return df

df = load_data()

df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df = df.dropna(subset=['Order Date'])

df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month
df['Month Name'] = df['Order Date'].dt.strftime('%b')
df['Weekday'] = df['Order Date'].dt.day_name()
df['Quarter'] = df['Order Date'].dt.quarter

st.sidebar.header("🔍 Filters")
category = st.sidebar.multiselect("Category", df['Category'].dropna().unique())
year = st.sidebar.multiselect("Year", df['Year'].unique())

filtered_df = df.copy()
if category:
    filtered_df = filtered_df[filtered_df['Category'].isin(category)]
if year:
    filtered_df = filtered_df[filtered_df['Year'].isin(year)]

st.subheader("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

def safe_metric(df, col_name):
    return df[col_name].sum() if col_name in df.columns else 0

col1.metric("💰 Total Sales", f"{safe_metric(filtered_df,'Sales'):,.0f}")
col2.metric("📈 Total Profit", f"{safe_metric(filtered_df,'Profit'):,.0f}")
col3.metric("🛒 Orders", filtered_df.shape[0])
col4.metric("📦 Avg Order Value", f"{filtered_df['Sales'].mean():,.0f}" if 'Sales' in filtered_df.columns else "N/A")

st.subheader("📈 Daily Sales Trend")
if 'Sales' in filtered_df.columns:
    daily_sales = filtered_df.groupby('Order Date')['Sales'].sum()
    plt.figure()
    daily_sales.plot()
    st.pyplot(plt)

st.subheader("📦 Order Volume Trend")
orders = filtered_df.groupby('Order Date').size()
plt.figure()
orders.plot()
st.pyplot(plt)

st.subheader("📉 Moving Average (7 Days)")
if 'Sales' in filtered_df.columns:
    rolling = daily_sales.rolling(7).mean()
    plt.figure()
    daily_sales.plot(label="Actual")
    rolling.plot(label="7-Day Avg")
    plt.legend()
    st.pyplot(plt)

st.subheader("📅 Monthly Trend")
if 'Sales' in filtered_df.columns:
    monthly = filtered_df.groupby(['Year','Month'])['Sales'].sum().reset_index()
    plt.figure()
    sns.lineplot(data=monthly, x='Month', y='Sales', hue='Year', marker='o')
    st.pyplot(plt)

st.subheader("📊 Year-over-Year Growth")
if 'Sales' in df.columns:
    yoy = df.groupby('Year')['Sales'].sum().pct_change() * 100
    st.line_chart(yoy)

st.subheader("🌦 Seasonal Analysis")
if 'Sales' in filtered_df.columns:
    seasonal = filtered_df.groupby('Month Name')['Sales'].sum().reindex(
        ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])
    plt.figure()
    seasonal.plot(kind='bar')
    st.pyplot(plt)

st.subheader("📆 Weekday Sales")
if 'Sales' in filtered_df.columns:
    weekday_sales = filtered_df.groupby('Weekday')['Sales'].sum().reindex(
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    plt.figure()
    weekday_sales.plot(kind='bar')
    st.pyplot(plt)

st.subheader("📅 Quarterly Sales")
if 'Sales' in filtered_df.columns:
    quarter = filtered_df.groupby('Quarter')['Sales'].sum()
    plt.figure()
    quarter.plot(kind='bar')
    st.pyplot(plt)

st.subheader("📦 Category-wise Sales")
if 'Sales' in filtered_df.columns:
    cat_sales = filtered_df.groupby('Category')['Sales'].sum()
    plt.figure()
    cat_sales.plot(kind='pie', autopct='%1.1f%%')
    st.pyplot(plt)

st.subheader("💸 Profit vs Sales")
if 'Sales' in filtered_df.columns and 'Profit' in filtered_df.columns:
    plt.figure()
    sns.scatterplot(data=filtered_df, x='Sales', y='Profit', hue='Category')
    st.pyplot(plt)

st.subheader("🔥 Correlation Heatmap")
if 'Sales' in filtered_df.columns and 'Profit' in filtered_df.columns:
    plt.figure()
    sns.heatmap(filtered_df[['Sales','Profit']].corr(), annot=True)
    st.pyplot(plt)

st.subheader("💡 Profit Ratio")
if 'Sales' in filtered_df.columns and 'Profit' in filtered_df.columns:
    filtered_df['Profit Ratio'] = filtered_df['Profit'] / filtered_df['Sales']
    st.write("Average Profit Ratio:", round(filtered_df['Profit Ratio'].mean(), 3))

st.subheader("⚠️ Loss Making Orders")
if 'Profit' in filtered_df.columns:
    loss_df = filtered_df[filtered_df['Profit'] < 0]
    st.write("Total Loss Orders:", loss_df.shape[0])

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
else:
    st.info("Forecasting not available or Sales column missing")

st.subheader("🏆 Peak Sales Month")
if 'Sales' in df.columns:
    peak_month = df.groupby('Month Name')['Sales'].sum().idxmax()
    st.success(f"Highest sales in: {peak_month}")

st.subheader("🧠 Business Insights")
if 'Sales' in df.columns:
    st.write("📦 Top Category:", df.groupby('Category')['Sales'].sum().idxmax())
if 'Profit' in df.columns:
    st.write("💰 Most Profitable Category:", df.groupby('Category')['Profit'].sum().idxmax())

st.subheader("⬇️ Download Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", csv, "filtered_data.csv")

st.subheader("📄 Raw Data")
if st.checkbox("Show Data"):
    st.write(filtered_df)
