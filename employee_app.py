import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# إعداد قاعدة البيانات
engine = create_engine('sqlite:///employees.db')
table_name = 'employees'

# إنشاء الجدول إذا لم يكن موجودًا
with engine.connect() as conn:
    conn.execute(text(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            department TEXT
        );
    '''))

# قراءة البيانات من القاعدة
def load_data():
    return pd.read_sql(f"SELECT * FROM {table_name}", engine)

# إضافة أو تعديل موظف
def save_employee(data, emp_id=None):
    with engine.connect() as conn:
        if emp_id is None:
            conn.execute(
                text(f"INSERT INTO {table_name} (name, phone, email, department) VALUES (:name, :phone, :email, :department)"),
                data
            )
        else:
            data["id"] = emp_id
            conn.execute(
                text(f"UPDATE {table_name} SET name=:name, phone=:phone, email=:email, department=:department WHERE id=:id"),
                data
            )

# حذف موظف
def delete_employee(emp_id):
    with engine.connect() as conn:
        conn.execute(text(f"DELETE FROM {table_name} WHERE id=:id"), {"id": emp_id})

# واجهة المستخدم
st.title("دليل هواتف الموظفين")
df = load_data()

# 🔍 البحث
st.subheader("🔍 البحث عن موظف")
search_name = st.text_input("ابحث بالاسم")
search_dept = st.text_input("ابحث بالقسم")

filtered_df = df.copy()
if search_name:
    filtered_df = filtered_df[filtered_df["name"].str.contains(search_name, case=False, na=False)]
if search_dept:
    filtered_df = filtered_df[filtered_df["department"].str.contains(search_dept, case=False, na=False)]

# عرض النتائج بعد التصفية
st.subheader("📊 نتائج البحث أو الجدول الكامل")
st.dataframe(filtered_df)

# النموذج
st.subheader("➕ إضافة / ✏️ تعديل موظف")
with st.form("form"):
    name = st.text_input("الاسم")
    phone = st.text_input("رقم الهاتف")
    email = st.text_input("البريد الإلكتروني")
    department = st.text_input("القسم")
    selected = st.selectbox("اختر موظف للتعديل (أو لا شيء للإضافة)", options=["جديد"] + df["id"].astype(str).tolist())

    if st.form_submit_button("💾 حفظ"):
        emp_data = {"name": name, "phone": phone, "email": email, "department": department}
        if selected == "جديد":
            save_employee(emp_data)
            st.success("✅ تم الإضافة")
        else:
            save_employee(emp_data, int(selected))
            st.success("✅ تم التعديل")

df = load_data()

# حذف موظف
st.subheader("❌ حذف موظف")
if len(df) > 0:
    employee_names = df["name"] + " - " + df["id"].astype(str)
    selected_name = st.selectbox("اختر موظف للحذف", options=employee_names)
    if st.button("🗑️ حذف"):
        selected_id = int(selected_name.split(" - ")[-1])
        delete_employee(selected_id)
        st.success("🚮 تم الحذف")
else:
    st.info("لا يوجد موظفون لحذفهم.")
