import pandas as pd
import numpy as np

def is_empty(val):
    if val is None or pd.isna(val): return True
    return str(val).strip() in ["", "None", "nan", "NaN"]

def run_table_calculations(df):
    data = df.copy()
    n = len(data)
    
    # تحويل الأعمدة لأرقام لضمان سلامة الحسابات
    cols = ["العمر x", "عدد الاحياء lx", "عدد الوفيات dx", "احتمال الوفاة qx", 
            "احتمال الحياة px", "توقع الحياة ex", "توقع الحياة الكامل ėx"]
    for col in data.columns[1:]:
        data[col] = pd.to_numeric(data[col], errors='coerce')

    # تشغيل حلقة تكرارية (RunCount = 10 كما في كود VBA) لضمان ترابط الحسابات
    for _ in range(10):
        for i in range(n):
            
            # --- 1. تحديث qx و px (مكملات) ---
            if not is_empty(data.iloc[i, 3]) and is_empty(data.iloc[i, 4]):
                data.iloc[i, 4] = round(1 - float(data.iloc[i, 3]), 4)
            elif not is_empty(data.iloc[i, 4]) and is_empty(data.iloc[i, 3]):
                data.iloc[i, 3] = round(1 - float(data.iloc[i, 4]), 4)
            
            # --- 2. تحديث ex و ėx (علاقة ثابتة) ---
            if not is_empty(data.iloc[i, 5]) and is_empty(data.iloc[i, 6]):
                data.iloc[i, 6] = round(float(data.iloc[i, 5]) + 0.5, 4)
            elif not is_empty(data.iloc[i, 6]) and is_empty(data.iloc[i, 5]):
                data.iloc[i, 5] = round(float(data.iloc[i, 6]) - 0.5, 4)

            # --- 3. حساب lx (العمود B) بالأولويات الثلاث ---
            if is_empty(data.iloc[i, 1]):
                # أولوية 1: الحساب العكسي (lx = lx_next / px)
                if i < n - 1 and not is_empty(data.iloc[i + 1, 1]) and not is_empty(data.iloc[i, 4]):
                    if float(data.iloc[i, 4]) != 0:
                        data.iloc[i, 1] = data.iloc[i + 1, 1] / data.iloc[i, 4]
                # أولوية 2: من الصف السابق (lx = lx_prev - dx_prev)
                elif i > 0 and not is_empty(data.iloc[i - 1, 1]) and not is_empty(data.iloc[i - 1, 2]):
                    data.iloc[i, 1] = data.iloc[i - 1, 1] - data.iloc[i - 1, 2]
                # أولوية 3: من الوفيات والناجين لاحقاً (lx = lx_next + dx_current)
                elif i < n - 1 and not is_empty(data.iloc[i + 1, 1]) and not is_empty(data.iloc[i, 2]):
                    data.iloc[i, 1] = data.iloc[i + 1, 1] + data.iloc[i, 2]

            # --- 4. حساب dx (العمود C) ---
            if is_empty(data.iloc[i, 2]):
                # أولوية 1: الفرق بين الناجين (dx = lx_current - lx_next)
                if i < n - 1 and not is_empty(data.iloc[i, 1]) and not is_empty(data.iloc[i + 1, 1]):
                    data.iloc[i, 2] = round(data.iloc[i, 1] - data.iloc[i + 1, 1], 0)
                # أولوية 2: من الاحتمال (dx = lx * qx)
                elif not is_empty(data.iloc[i, 1]) and not is_empty(data.iloc[i, 3]):
                    data.iloc[i, 2] = round(data.iloc[i, 1] * data.iloc[i, 3], 0)

            # --- 5. تحديث qx إذا توفر lx و dx ---
            if is_empty(data.iloc[i, 3]) and not is_empty(data.iloc[i, 1]) and not is_empty(data.iloc[i, 2]):
                if float(data.iloc[i, 1]) != 0:
                    data.iloc[i, 3] = round(data.iloc[i, 2] / data.iloc[i, 1], 4)

    # --- 6. حساب توقع الحياة (F, G) من مجموع lx (للمساحات الفارغة) ---
    for i in range(n):
        if is_empty(data.iloc[i, 5]) and not is_empty(data.iloc[i, 1]):
            sum_lx_future = data.iloc[i+1:, 1].sum()
            if sum_lx_future > 0 and data.iloc[i, 1] != 0:
                data.iloc[i, 5] = round(sum_lx_future / data.iloc[i, 1], 4)
                data.iloc[i, 6] = round(data.iloc[i, 5] + 0.5, 4)

    # التنسيق النهائي للأرقام
    data.iloc[:, 1:3] = data.iloc[:, 1:3].fillna(0).round(0).astype(int)
    return data

# (دوال الرموز الرياضية والحياة المشتركة تبقى كما هي دون تغيير)
def calculate_actuarial_logic(x, category, choice, v1, v2=0):
    try:
        x, v1, v2 = int(x), int(v1), int(v2)
        
        # دالة مساعدة لإخفاء الرقم 1 من الرموز الاكتوارية
        def fmt(n): return "" if n == 1 else str(n)
        
        if category == "احتمال الوفاة":
            # الحالة الجديدة: يموت قبل بلوغه العمر
            if choice == "يموت قبل بلوغه العمر":
                n = v1 - x
                return rf"_{{{fmt(n)}}}q_{{{x}}} = \frac{{l_{{{x}}} - l_{{{v1}}}}}{{l_{{{x}}}}}"

            elif choice == "يموت خلال مدة n":
                return rf"_{{{fmt(v1)}}}q_{{{x}}} = \frac{{l_{{{x}}} - l_{{{x+v1}}}}}{{l_{{{x}}}}}"

            elif choice in ["يموت بين العمر والعمر", "يعيش حتى بلوغه العمر ولكن لا يعيش حتى بلوغه العمر"]:
                m, n = v1 - x, v2 - v1
                m_part = f"{m}|" if m > 0 else ""
                return rf"_{{{m_part}{fmt(n)}}}q_{{{x}}} = \frac{{l_{{{v1}}} - l_{{{v2}}}}}{{l_{{{x}}}}}"

            elif choice == "يموت في السنة التالية لبلوغه العمر":
                m = v1 - x
                m_part = f"{m}|" if m > 0 else ""
                # هنا الاحتمال دائماً لسنة واحدة، لذا نستخدم q مباشرة (بدون n)
                return rf"_{{{m_part}}}q_{{{x}}} = \frac{{l_{{{v1}}} - l_{{{v1+1}}}}}{{l_{{{x}}}}}"

        else: # احتمال الحياة
            if choice == "يعيش حتى بلوغه العمر":
                n = v1 - x
                return rf"_{{{fmt(n)}}}p_{{{x}}} = \frac{{l_{{{v1}}}}}{{l_{{{x}}}}}"
            
            # يعيش لمدة n
            return rf"_{{{fmt(v1)}}}p_{{{x}}} = \frac{{l_{{{x+v1}}}}}{{l_{{{x}}}}}"

    except Exception:
        return "خطأ في المعطيات"

# في ملف logic.py
def calculate_joint_logic(x, y, n_px, n_py, j_type, n):
    # حساب القيم الأساسية
    n_qx = 1 - n_px
    n_qy = 1 - n_py
    n_pxy = n_px * n_py # بقاء الاثنين معاً
    
    if j_type == "بقاء الاثنين معاً":
        res = n_pxy
        formula = f"{{}}_{{{n}}}p_{{{x}:{y}}} = {n_px:.5f} \\times {n_py:.5f} = {res:.5f}"
    
    elif j_type == "احتمال حياة شخص واحد فقط":
        # (بقاء الأول ووفاة الثاني) + (وفاة الأول وبقاء الثاني)
        res = (n_px * n_qy) + (n_qx * n_py)
        formula = f"{{}}_{{{n}}}p_{{{x}:{y}}}^{{[1]}} = ({n_px:.5f} \\times {n_qy:.5f}) + ({n_qx:.5f} \\times {n_py:.5f}) = {res:.5f}"
        
    elif j_type == "احتمال حياة واحد على الاقل":
        res = n_px + n_py - n_pxy
        formula = f"{{}}_{{{n}}}p_{{\\overline{{{x}:{y}}}}} = {n_px:.5f} + {n_py:.5f} - {n_pxy:.5f} = {res:.5f}"
        
    elif j_type == "وفاة الاثنين معا":
        res = n_qx * n_qy
        formula = f"{{}}_{{{n}}}q_{{\\overline{{{x}:{y}}}}} = {n_qx:.5f} \\times {n_qy:.5f} = {res:.5f}"
        
    elif j_type == "احتمال وفاة شخص واحد فقط":
        # هي نفس احتمال حياة شخص واحد فقط في حالة شخصين
        res = (n_px * n_qy) + (n_qx * n_py)
        formula = f"{{}}_{{{n}}}q_{{{x}:{y}}}^{{[1]}} = ({n_px:.5f} \\times {n_qy:.5f}) + ({n_qx:.5f} \\times {n_py:.5f}) = {res:.5f}"
        
    elif j_type == "احتمال وفاة شخص واحد على الاقل":
        # تعني وفاة الأول أو وفاة الثاني أو كلاهما (عكس بقاء الاثنين معاً)
        res = 1 - n_pxy
        formula = f"{{}}_{{{n}}}q_{{{x}:{y}}} = 1 - {n_pxy:.5f} = {res:.5f}"
    
    return formula
# --- أضف الدالة الجديدة هنا (خارج أي دالة أخرى) ---
def calculate_lx_from_formula(formula, x_val):
    try:
        # تعريف الدوال المسموحة مثل sqrt
        allowed_names = {"x": x_val, "sqrt": lambda v: v**0.5}
        # حساب النتيجة
        return eval(formula, {"__builtins__": None}, allowed_names)
    except:
        return None