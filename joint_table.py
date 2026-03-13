import streamlit as st
import pandas as pd

st.set_page_config(page_title="حاسبة جدول الحياة المشترك", layout="wide")

st.title("👥 حاسبة احتمالات الحياة والوفاة المشتركة")

# مدخلات الأعمار
c1, c2, c3 = st.columns(3)
with c1:
    age_x = st.number_input("عمر الشخص الأول (x):", min_value=0, max_value=100, value=30)
with c2:
    age_y = st.number_input("عمر الشخص الثاني (y):", min_value=0, max_value=100, value=25)
with c3:
    horizon = st.number_input("عدد سنوات التوقع (t):", min_value=1, max_value=100, value=20)

st.markdown("---")

# توليد بيانات افتراضية (يمكن استبدالها برفع ملف Excel لجدول حياة حقيقي)
data = {
    "السنة (t)": list(range(horizon + 1)),
    "p(x+t)": [max(0, 1 - (age_x + t)/100) for t in range(horizon + 1)],
    "p(y+t)": [max(0, 1 - (age_y + t)/100) for t in range(horizon + 1)]
}

st.subheader("📝 مراجعة وتعديل احتمالات الحياة السنوية")
edited_df = st.data_editor(pd.DataFrame(data), use_container_width=True)

if st.button("📊 حساب النتائج الاكتوارية"):
    res_df = edited_df.copy()
    
    # 1. احتمال بقاء الاثنين معاً لسنة واحدة
    res_df["p_xy (بقاء الاثنين)"] = res_df["p(x+t)"] * res_df["p(y+t)"]
    
    # 2. احتمال وفاة أحدهما على الأقل خلال السنة
    res_df["q_xy (وفاة أحدهما)"] = 1 - res_df["p_xy (بقاء الاثنين)"]
    
    # 3. احتمال بقاء شخص واحد على الأقل (Status of last survivor)
    res_df["p_xy_bar (بقاء شخص واحد)"] = res_df["p(x+t)"] + res_df["p(y+t)"] - res_df["p_xy (بقاء الاثنين)"]
    
    # 4. حساب الاحتمال التراكمي للبقاء (n_p_xy)
    # نستخدم cumprod لحساب احتمال البقاء من السنة 0 إلى السنة t
    res_df["تراكمي: بقاء الاثنين"] = res_df["p_xy (بقاء الاثنين)"].cumprod()

    st.success("تم الحساب بنجاح!")
    st.dataframe(res_df.style.format("{:.5f}"), height=400)
    
    # رسم بياني توضيحي
    st.line_chart(res_df[["تراكمي: بقاء الاثنين", "p_xy_bar (بقاء شخص واحد)"]])