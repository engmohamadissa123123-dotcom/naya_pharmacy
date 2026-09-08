import streamlit as st
import pandas as pd
from datetime import datetime, date

# إعدادات الصفحة
st.set_page_config(
    page_title="صيدلية نايا - Naya Pharmacy",
    page_icon="💊",
    layout="wide"
)

# عنوان التطبيق
st.title("💊 نظام إدارة مخزون صيدلية نايا")
st.write("مرحباً بك في نظام إدارة وتتبع الأدوية والمنتجات الصيدلانية.")

# التهيئة المبدئية لبيانات المخزون في جلسة العمل
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=[
        "اسم الدواء", "الفئة", "الكمية", "سعر التكلفة", "سعر البيع", "تاريخ الانتهاء"
    ])

# الشريط الجانبي لإضافة منتج جديد
st.sidebar.header("➕ إضافة دواء جديد")
with st.sidebar.form("add_medicine_form", clear_on_submit=True):
    med_name = st.text_input("اسم الدواء / المنتج")
    category = st.selectbox("الفئة", ["أدوية عامة", "مسكنات", "مضادات حيوية", "مستحضرات تجميل", "مكملات غذائية", "أخرى"])
    quantity = st.number_input("الكمية", min_value=1, value=10, step=1)
    cost_price = st.number_input("سعر التكلفة", min_value=0.0, value=0.0, step=0.5)
    sell_price = st.number_input("سعر البيع", min_value=0.0, value=0.0, step=0.5)
    expiry_date = st.date_input("تاريخ الانتهاء", value=date.today())
    
    submitted = st.form_submit_button("إضافة للمخزون")
    if submitted:
        if med_name.strip() != "":
            new_data = pd.DataFrame([{
                "اسم الدواء": med_name,
                "الفئة": category,
                "الكمية": quantity,
                "سعر التكلفة": cost_price,
                "سعر البيع": sell_price,
                "تاريخ الانتهاء": expiry_date
            }])
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_data], ignore_index=True)
            st.sidebar.success(f"تمت إضافة {med_name} بنجاح!")
        else:
            st.sidebar.error("يرجى إدخال اسم الدواء.")

# ملخص وإحصائيات سريعة
st.header("📊 إحصائيات المخزون")
col1, col2, col3 = st.columns(3)
col1.metric("إجمالي المواد", len(st.session_state.inventory))
total_qty = int(st.session_state.inventory["الكمية"].sum()) if not st.session_state.inventory.empty else 0
col2.metric("إجمالي قطع الأدوية", total_qty)

# حساب المنتجات المنتهية أو القريبة من الانتهاء
today = date.today()
expired_count = 0
near_expiry_count = 0

if not st.session_state.inventory.empty:
    for exp in st.session_state.inventory["تاريخ الانتهاء"]:
        if isinstance(exp, str):
            exp = datetime.strptime(exp, "%Y-%m-%d").date()
        days_left = (exp - today).days
        if days_left < 0:
            expired_count += 1
        elif days_left <= 90:
            near_expiry_count += 1

col3.metric("تنبهات الصلاحية (منتهي / قريب)", f"{expired_count} / {near_expiry_count}")

st.divider()

# عرض جدول المخزون والتنبيهات
st.header("📋 جدول المخزون الحالي")

if st.session_state.inventory.empty:
    st.info("لا توجد أدوية مسجلة حالياً. استخدم القائمة الجانبية لإضافة منتجات جديدة.")
else:
    # دالة لتنسيق ألوان التنبيه بحسب الصلاحية
    def highlight_expiry(val):
        if isinstance(val, str):
            val = datetime.strptime(val, "%Y-%m-%d").date()
        days_left = (val - today).days
        if days_left < 0:
            return 'background-color: #ffcdd2; color: #b71c1c;'  # أحمر للمنتهي
        elif days_left <= 90:
            return 'background-color: #fff9c4; color: #f57f17;'  # أصفر لقريب الانتهاء
        return ''

    styled_df = st.session_state.inventory.style.map(highlight_expiry, subset=["تاريخ الانتهاء"])
    st.dataframe(styled_df, use_container_width=True)

    # إمكانية تحميل البيانات كملف CSV
    csv_data = st.session_state.inventory.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 تحميل جدول المخزون (CSV)",
        data=csv_data,
        file_name="naya_pharmacy_inventory.csv",
        mime="text/csv"
    )
