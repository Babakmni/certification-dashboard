
# Web dashboard using Streamlit with color-coded bar charts for certifications
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load data (you can replace with actual Excel or CSV file)
@st.cache_data
def load_data():
    df = pd.read_excel("certification.xlsx", sheet_name=None)
    combined = []
    for sheet_name, sheet in df.items():
        if sheet.empty:
            continue
        sheet.columns = [str(c).strip() for c in sheet.columns]
        if 'Start Date' not in sheet and 'تازیخ شروع Start Date' in sheet:
            sheet['Start Date'] = pd.to_datetime(sheet['تازیخ شروع Start Date'], errors='coerce')
        if 'Expire Date' not in sheet and 'تازیخ پایان' in sheet:
            sheet['Expire Date'] = pd.to_datetime(sheet['تازیخ پایان'], errors='coerce')
        sheet = sheet.dropna(subset=['Expire Date'])
        sheet['Product'] = sheet['Product'].astype(str)
        sheet['certification'] = sheet['certification'].astype(str)
        sheet['Remaining Days'] = (sheet['Expire Date'] - datetime.today()).dt.days
        sheet['Remaining Months'] = (sheet['Remaining Days'] / 30).round(1)
        sheet['Sheet'] = sheet_name
        combined.append(sheet[['Product', 'certification', 'Start Date', 'Expire Date', 'Remaining Days', 'Remaining Months', 'Sheet']])
    return pd.concat(combined, ignore_index=True)

# Categorize status
def status_color(months):
    if months < 3:
        return 'red'
    elif months < 6:
        return 'orange'
    else:
        return 'green'

data = load_data()
st.title("📊 Certification Dashboard - Tosan Techno")
st.write("تاریخ امروز: ", datetime.today().strftime("%Y-%m-%d"))

# Editable table
edited_data = st.data_editor(data, num_rows="dynamic")

# Product filter
products = edited_data['Product'].unique()
selected_product = st.selectbox("محصول را انتخاب کنید:", products)

product_data = edited_data[edited_data['Product'] == selected_product]

# Plot bar chart
st.subheader(f"📦 نمودار وضعیت گواهی‌های {selected_product}")
fig, ax = plt.subplots(figsize=(10, 5))
colors = product_data['Remaining Months'].apply(status_color)
ax.bar(product_data['certification'], product_data['Remaining Months'], color=colors)
ax.axhline(y=3, color='red', linestyle='--', linewidth=1)
ax.axhline(y=6, color='orange', linestyle='--', linewidth=1)
ax.set_ylabel("ماه باقی‌مانده")
ax.set_xlabel("نوع گواهی")
ax.set_title("زمان باقی‌مانده تا انقضا")
plt.xticks(rotation=45)
st.pyplot(fig)

# Warn for critical certifications
st.subheader("⚠️ هشدار محصولات بحرانی")
critical = edited_data[(edited_data['Remaining Months'] < 3)]
over3 = critical.groupby("Product").size()
over3 = over3[over3 > 3]
if not over3.empty:
    for product, count in over3.items():
        st.error(f"{product} دارای {count} گواهی با کمتر از ۳ ماه زمان باقی‌مانده است 😟")
else:
    st.success("هیچ محصولی با بیش از ۳ گواهی بحرانی یافت نشد.")
