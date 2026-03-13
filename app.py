import streamlit as st
import pandas as pd
import logic

st.set_page_config(page_title="المنصة الاكتوارية الموحدة", layout="wide")

# CSS مطور لرفع المحتوى وإضافة التوقيع
st.markdown("""
    <style>
    /* تقليل المسافة العلوية للحاوية الرئيسية */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }
    
    th, td, input { text-align: center !important; }
    [data-testid="stDataFrame"] div { text-align: center !important; }
    .stButton>button { width: 100%; border-radius: 5px; }
    
    /* تنسيق العنوان الرئيسي */
    .main-header { 
        text-align: center; 
        color: #1E3A8A !important; 
        font-size: 20px !important; 
        margin-bottom: 0px !important; 
        padding-bottom: 0px !important;
        line-height: 1.2;
    }

    h1.main-header {
        font-size: 20px !important;
    }
    
    /* تنسيق التوقيع */
    .signature {
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        font-size: 14px;
        color: #666;
        margin-top: -5px; 
        margin-bottom: 20px;
        font-weight: bold;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 9px; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# عرض العنوان والتوقيع
st.markdown("<h1 class='main-header'>🛡️ المنصة الاكتوارية </h1>", unsafe_allow_html=True)
st.markdown("<p class='signature'>By : BaDeR </p>", unsafe_allow_html=True)

# تهيئة البيانات
if 'main_data' not in st.session_state:
    st.session_state.main_data = pd.DataFrame({
        "العمر x": list(range(5)),
        "عدد الاحياء lx": [None]*5, "عدد الوفيات dx": [None]*5, 
        "احتمال الوفاة qx": [None]*5, "احتمال الحياة px": [None]*5, 
        "توقع الحياة ex": [None]*5, "توقع الحياة الكامل ėx": [None]*5
    })

# --- إنشاء التبويبات (Tabs) ---
tab1, tab2 = st.tabs(["📊 جدول حياة الفرد ومولد الرموز", "👥 جدول الحياة والوفاة لشخصين"])

with tab1:
    # --- القسم الأول: جدول الحياة ---
    st.subheader("📋 بناء جدول الحياة")

    # 1. أضف كود رفع الملف هنا (قبل الجدول مباشرة)
    uploaded_file = st.file_uploader("📂 رفع جدول حياة من ملف Excel (يرجى التاكد من كافة الاعمدة)", type=["xlsx", "xls"])

    if uploaded_file is not None:
        try:
            # قراءة الملف مع إلغاء اعتبار الصف الأول كعناوين (header=None) 
            # لضمان تجاهل أي مسميات تماماً
            df_excel = pd.read_excel(uploaded_file, header=None)
            
            if len(df_excel.columns) >= 2:
                if st.button("✅ اعتماد بيانات ملف Excel"):
                    # 1. جلب أول عمودين فقط بناءً على ترتيبهم (0 و 1)
                    new_df = df_excel.iloc[:, [0, 1]].copy()
                    
                    # 2. إعادة تسميتهم داخلياً لتتوافق مع محرك الحسابات
                    new_df.columns = ["العمر x", "عدد الاحياء lx"]
                    
                    # 3. تنظيف البيانات: تحويل كل شيء لأرقام وحذف أي صفوف تحتوي على نصوص 
                    # (مثل صف العناوين الأصلي في ملفك)
                    new_df = new_df.apply(pd.to_numeric, errors='coerce').dropna()
                    
                    # 4. التأكد من أن العمر رقم صحيح و lx رقم عشري
                    new_df["العمر x"] = new_df["العمر x"].astype(int)
                    new_df["عدد الاحياء lx"] = new_df["عدد الاحياء lx"].astype(float)

                    # إرسال البيانات النهائية للملف المنطقي (logic.py) لحساب باقي الجدول
                    st.session_state.main_data = logic.run_table_calculations(new_df)
                    
                    st.success("✅ تم تجاهل مسميات الأعمدة واعتماد أول عمودين كبيانات رقمية.")
                    st.rerun()
            else:
                st.error("❌ خطأ: يجب أن يحتوي الملف على عمودين على الأقل.")
        except Exception as e:
            st.error(f"⚠️ حدث خطأ أثناء القراءة: {e}")

    # 2. عرض الجدول (المحرر)
    edited_df = st.data_editor(st.session_state.main_data, use_container_width=True, num_rows="dynamic", key="combined_editor")

    # 3. أزرار التحكم (التحديث والمسح)
    col_run, col_clear = st.columns(2)
    with col_run:
        if st.button("🔄 تحديث وحساب الجدول", type="primary"):
            st.session_state.main_data = logic.run_table_calculations(edited_df)
            st.rerun()
    with col_clear:
        if st.button("🗑️ مسح بيانات الجدول"):
            st.session_state.main_data = pd.DataFrame({
                "العمر x": list(range(5)), "عدد الاحياء lx": [None]*5, "عدد الوفيات dx": [None]*5, 
                "احتمال الوفاة qx": [None]*5, "احتمال الحياة px": [None]*5, 
                "توقع الحياة ex": [None]*5, "توقع الحياة الكامل ėx": [None]*5    
            })
            st.rerun()

    st.divider() # الخط الفاصل

    # قمنا بوضع 3 أعمدة وجعلنا عمود الدالة هو الأخير (جهة اليمين)
    col_empty1, col_empty2, col_func = st.columns([1, 1, 1])

    with col_func:
        # 1. عنوان فرعي صغير ومحاذاة لليمين
        st.markdown("<h4 style='text-align: right;'>🧪 دالة lx المخصصة</h4>", unsafe_allow_html=True)
        
        # 2. خيار التفعيل
        use_formula = st.checkbox("تفعيل الحساب بالدالة", key="use_f")
        
        if use_formula:
            # 3. خانة الإدخال فارغة مع نص توضيحي يختفي عند الكتابة
            formula_input = st.text_input("lx = :", value="", placeholder="مثال: 1000 * √(100-x)", key="formula_field")
            
            if formula_input == "":
                st.caption("⚠️ يرجى إدخال الدالة للبدء")

    # --- القسم الجديد: حساب احتمالية البقاء من الجدول ---
    st.subheader("🎯 حساب الاحتمالات من الجدول")

    available_ages = st.session_state.main_data.dropna(subset=['عدد الاحياء lx'])['العمر x'].tolist()

    if len(available_ages) > 1:
        calc_options = [
            "احتمال يعيش حتى بلوغه العمر (x+n)",
            "احتمال يعيش (n) سنوات على الأقل",
            "احتمال شخص يموت قبل بلوغه العمر (x+n)",
            "احتمال يموت بين عمرين محددين",
            "احتمال يموت في العام التالي لبلوغ عمر معين",
            "احتمال يعيش لعمر معين ويموت قبل عمر آخر"
        ]
        
        selected_calc = st.selectbox("اختر نوع الاحتمال المطلوب:", calc_options)
        df = st.session_state.main_data

        c_p1, c_p2, c_p3 = st.columns(3)
        
        with c_p1:
            x_age = st.selectbox("عمر الشخص الحالي (x):", options=available_ages, key="x_age_calc")

        with c_p2:
            if selected_calc == "احتمال يعيش (n) سنوات على الأقل":
                n_years = st.number_input("عدد السنوات (n):", min_value=1, step=1, value=1)
                target_age = x_age + n_years
                target_age = st.selectbox("العام المستهدف (يموت بين x و x+1):", [a for a in available_ages if a >= x_age and (a + 1) in available_ages])
            else:
                target_age = st.selectbox("إلى العمر / العمر الأول:", [a for a in available_ages if a > x_age])

        with c_p3:
            if "بين" in selected_calc or "يموت قبل عمر آخر" in selected_calc:
                final_age = st.selectbox("إلى العمر الثاني:", [a for a in available_ages if a > target_age])
            elif "العام التالي" in selected_calc:
                final_age = target_age + 1

        if st.button("🧮 احسب النتيجة من الجدول"):
            try:  # تأكد من وجود النقطتين هنا لمنع الخطأ الذي ظهر في الصورة
                get_lx = lambda age: df.loc[df['العمر x'] == age, 'عدد الاحياء lx'].values[0]
                lx = get_lx(x_age)
                
                # --- تحديد المدد وتنسيقها ---
                n_val = int(target_age - x_age)
                n_disp = "" if n_val == 1 else str(n_val)

                if selected_calc == "احتمال يعيش حتى بلوغه العمر (x+n)" or selected_calc == "احتمال يعيش (n) سنوات على الأقل":
                    ln = get_lx(target_age)
                    res = ln / lx
                    st.latex(f"{{}}_{{{n_disp}}}p_{{{int(x_age)}}} = \\frac{{l_{{{int(target_age)}}}}}{{l_{{{int(x_age)}}}}} = {res:.5f}")

                elif selected_calc == "احتمال شخص يموت قبل بلوغه العمر (x+n)":
                    ln = get_lx(target_age)
                    res = 1 - (ln / lx)
                    st.latex(f"{{}}_{{{n_disp}}}q_{{{int(x_age)}}} = 1 - \\frac{{l_{{{int(target_age)}}}}}{{l_{{{int(x_age)}}}}} = {res:.5f}")

                elif selected_calc == "احتمال يموت بين عمرين محددين" or selected_calc == "احتمال يعيش لعمر معين ويموت قبل عمر آخر":
                    l_start = get_lx(target_age)
                    l_end = get_lx(final_age)
                    res = (l_start - l_end) / lx
                    
                    # التصحيح هنا: m هي مدة التأجيل، و n هي مدة الوفاة (الفرق بين العمر الثاني والأول)
                    m = int(target_age - x_age)
                    n = int(final_age - target_age)
                    
                    m_disp = f"{m}|" if m > 0 else ""
                    n_p_disp = "" if n == 1 else str(n)
                    
                    # ستظهر الآن بالشكل الصحيح: m|n qx
                    st.latex(f"{{}}_{{{m_disp}{n_p_disp}}}q_{{{int(x_age)}}} = \\frac{{l_{{{int(target_age)}}} - l_{{{int(final_age)}}}}}{{l_{{{int(x_age)}}}}} = {res:.5f}")

                elif selected_calc == "احتمال يموت في عام معين (محدد)":
                    l_m = get_lx(target_age)
                    l_m1 = get_lx(target_age + 1)
                    res = (l_m - l_m1) / lx
                    st.latex(f"{{}}_{{{n_disp}}}|q_{{{int(x_age)}}} = \\frac{{l_{{{int(target_age)}}} - l_{{{int(target_age+1)}}}}}{{l_{{{int(x_age)}}}}} = {res:.5f}")

                elif selected_calc == "احتمال يموت في العام التالي لبلوغ عمر معين":
                    l_next = get_lx(target_age)
                    l_next2 = get_lx(target_age + 1)
                    res = (l_next - l_next2) / lx
                    st.latex(f"{{}}_{{{n_disp}}}|q_{{{int(x_age)}}} = {res:.5f}")

            except Exception as e:
                st.error(f"حدث خطأ: {e}. تأكد من وجود جميع الأعمار في الجدول.")
    else:
        st.info("يرجى تعبئة الجدول والضغط على زر التحديث لتفعيل الحسابات.")

    # --- القسم الثاني: مولد الرموز ---
    st.subheader("📝 مولد الرموز الرياضية")
    col_sym_a, col_sym_b = st.columns(2)
    with col_sym_a:
        age_x_input = st.number_input("العمر الحالي (x):", value=20, key="s_age_x")
        cat_type = st.radio("نوع الاحتمال:", ["احتمال الوفاة", "احتمال الحياة"], horizontal=True, key="s_cat")
    with col_sym_b:
        options = ["يموت خلال مدة n", "يموت بين العمر والعمر", "يعيش حتى بلوغه العمر ولكن لا يعيش حتى بلوغه العمر", "يموت في السنة التالية لبلوغه العمر"] if cat_type == "احتمال الوفاة" else ["يعيش لمدة n", "يعيش حتى بلوغه العمر"]
        choice = st.selectbox("اختر الحالة:", options, key="s_choice")
        
        if "بين العمر" in choice or "ولكن لا يعيش" in choice:
            v1 = st.number_input("من عمر (x1):", value=age_x_input+5, key="sv1")
            v2 = st.number_input("إلى عمر (x2):", value=age_x_input+10, key="sv2")
        elif "حتى بلوغه" in choice:
            v1 = st.number_input("العمر المستهدف:", value=age_x_input+10, key="sv1")
            v2 = 0
        else:
            v1 = st.number_input("المدة (n):", value=5, key="sv1")
            v2 = 0

    if st.button("✨ النتيجة", type="secondary"):
        st.latex(logic.calculate_actuarial_logic(age_x_input, cat_type, choice, v1, v2))

with tab2:
    # --- القسم الثالث: حسابات الشخصين ---
    st.subheader("👥 احتمالات الحياة والوفاة لشخصين")
    j_n = st.number_input("الرمز الزمني للفترة (n):", min_value=1, value=1, step=1, key="j_n")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.info("👤 بيانات الشخص الأول (x)")
        jx = st.number_input("العمر الصحيح (x):", min_value=0, step=1, key="jx")
        type_x = st.selectbox("نوع المعطى (الأول):", ["احتمال حياة", "احتمال وفاة"], key="tx")
        val_x = st.number_input(f"قيمة الاحتمال (x):", min_value=0.0, max_value=1.0, value=0.90, format="%.5f", key="vx")
    with c2:
        st.info("👤 بيانات الشخص الثاني (y)")
        jy = st.number_input("العمر الصحيح (y):", min_value=0, step=1, key="jy")
        type_y = st.selectbox("نوع المعطى (الثاني):", ["احتمال حياة", "احتمال وفاة"], key="ty")
        val_y = st.number_input(f"قيمة الاحتمال (y):", min_value=0.0, max_value=1.0, value=0.85, format="%.5f", key="vy")
    
    st.markdown("---")
    j_type = st.selectbox("🔍 حدد الاحتمال المطلوب حسابه:", [
        "بقاء الاثنين معاً", "احتمال حياة شخص واحد فقط", "احتمال حياة واحد على الاقل",
        "وفاة الاثنين معا", "احتمال وفاة شخص واحد فقط", "احتمال وفاة شخص واحد على الاقل"
    ], key="j_type")
    
    if st.button("🧮 إجراء الحساب المشترك", type="primary"):
        final_npx = val_x if type_x == "احتمال حياة" else (1 - val_x)
        final_npy = val_y if type_y == "احتمال حياة" else (1 - val_y)
        result = logic.calculate_joint_logic(jx, jy, final_npx, final_npy, j_type, j_n)
        st.latex(result)