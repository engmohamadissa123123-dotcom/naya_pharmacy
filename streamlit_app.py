import streamlit as st
import pandas as pd
from datetime import datetime, date

# اعدادات الصفحة
st.set_page_config(
    page_title="صيدلية نايا - Naya Pharmacy",
    page_icon="💊",
    layout="wide"
)

# عنوان التطبيق
st.title("💊 نظام إدارة مخزون صيدلية نايا")
st.markdown("---")

# رابط ورقة Google Sheets
SHEET_ID = "1yvZUcMYt0BFXJ5SLFnN9h1mDMfwpvrI4uwgcZo13K3s"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

# دالة لتحميل البيانات من Google Sheets
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        # التأكد من تنظيف أسماء الأعمدة
        df.columns = [str(col).strip() for col in df.columns]
        return df
    except Exception as e:
        # في حال كان الجدول فارغاً تماماً
        columns = ["اسم الدواء", "الفئة", "الكمية", "سعر التكلفة", "سعر البيع", "تاريخ الانتهاء"]
        return pd.DataFrame(columns=columns)

# تحميل البيانات في الذاكرة الحالية
if "inventory" not in st.session_state:
    st.session_state.inventory = load_data()

# القائمة الجانبية لإضافة منتج جديد
st.sidebar.header("➕ إضافة دواء جديد")

with st.sidebar.form("add_med_form", clear_on_submit=True):
    med_name = st.text_input("اسم الدواء")
    category = st.selectbox("الفئة", ["أدوية عامة", "مضادات حيوية", "مسكنات", "فيتامينات", "مستلزمات طبية", "أخرى"])
    quantity = st.number_input("الكمية", min_value=1, step=1, value=10)
    cost_price = st.number_input("سعر التكلفة", min_value=0.0, step=0.5, value=0.0)
    sell_price = st.number_input("سعر البيع", min_value=0.0, step=0.5, value=0.0)
    expiry_date = st.date_input("تاريخ الانتهاء", min_value=date.today())
    
    submitted = st.form_submit_button("إضافة للمخزون")
    
    if submitted:
        if med_name.strip() == "":
            st.sidebar.error("يرجى إدخال اسم الدواء!")
        else:
            new_data = {
                "اسم الدواء": med_name,
                "الفئة": category,
                "الكمية": int(quantity),
                "سعر التكلفة": float(cost_price),
                "سعر البيع": float(sell_price),
                "تاريخ الانتهاء": str(expiry_date)
            }
            new_df = pd.DataFrame([new_data])
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_df], ignore_index=True)
            st.sidebar.success(f"تمت إضافة {med_name} بنجاح!")

# إحصائيات سريعة
df = st.session_state.inventory

col1, col2, col3 = st.columns(3)
col1.metric("إجمالي المواد", len(df))
col2.metric("إجمالي قطع الأدوية", int(df["الكمية"].sum()) if not df.empty and "الكمية" in df.columns else 0)

# تنبهات الصلاحية
expired_count = 0
near_expiry_count = 0

if not df.empty and "تاريخ الانتهاء" in df.columns:
    today = date.today()
    for exp_str in df["تاريخ الانتهاء"]:
        try:
            exp_d = datetime.strptime(str(exp_str), "%Y-%m-%d").date()
            days_left = (exp_d - today).days
            if days_left <= 0:
                expired_count += 1
            elif days_left <= 90:
                near_expiry_count += 1
        except:
            pass

col3.metric("تنبيهات الصلاحية (منتهي / قريب)", f"{expired_count} / {near_expiry_count}")

st.markdown("---")
st.subheader("📋 جدول المخزون الحالي")

# عرض الجدول
if df.empty:
    st.info("لا توجد أدوية مسجلة حالياً. استخدم القائمة الجانبية لإضافة منتجات جديدة.")
else:
    st.dataframe(df, use_container_width=True)

    # زر تحديث البيانات من Google Sheets
    if st.button("🔄 تحديث البيانات من السحابة"):
        st.session_state.inventory = load_data()
        st.rerun()

    # زر تحميل البيانات CSV
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 تحميل جدول المخزون (CSV)",
        data=csv_data,
        file_name=f"naya_pharmacy_inventory_{date.today()}.csv",
        mime="text/csv"
    )
