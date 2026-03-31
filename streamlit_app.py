st.subheader("📈 E-commerce Order Trend & Seasonal Analysis")

# Date convert
df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)

# Extract Month & Year
df['Month'] = df['Order Date'].dt.month
df['Year'] = df['Order Date'].dt.year

# Monthly Sales Trend
monthly_sales = df.groupby('Month')['Sales'].sum()

fig, ax = plt.subplots()
monthly_sales.plot(kind='line', marker='o', ax=ax)
ax.set_title("Monthly Sales Trend")
st.pyplot(fig)

# Year-wise Trend
yearly_sales = df.groupby('Year')['Sales'].sum()

fig, ax = plt.subplots()
yearly_sales.plot(kind='bar', ax=ax)
ax.set_title("Yearly Sales")
st.pyplot(fig)
