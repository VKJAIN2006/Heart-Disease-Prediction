import streamlit as st
import pandas as pd
import joblib

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Heart Disease Prediction",
    page_icon="❤️",
    layout="wide"
)


# ------------------ LOAD MODEL FILES ------------------
model = joblib.load("logistic_heart.pkl")
scaler = joblib.load("scaler.pkl")
expected_columns = joblib.load("columns.pkl")

# ------------------ HEADER ------------------
st.markdown(
    """
    <h1 style='text-align:center; color:#e63946;'>❤️ Heart Disease Prediction System</h1>
    <p style='text-align:center; font-size:18px;'>
    AI-powered application to estimate heart disease risk using clinical data
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

# ------------------ SIDEBAR INPUTS ------------------
st.sidebar.header("🩺 Patient Information")

age = st.sidebar.slider("Age", 18, 100, 40)
sex = st.sidebar.selectbox("Sex", ["M", "F"])
chest_pain = st.sidebar.selectbox("Chest Pain Type", ["ATA", "NAP", "TA", "ASY"])
resting_bp = st.sidebar.number_input("Resting Blood Pressure (mm Hg)", 80, 200, 120)
cholesterol = st.sidebar.number_input("Cholesterol (mg/dL)", 100, 600, 200)
fasting_bs = st.sidebar.selectbox("Fasting Blood Sugar > 120 mg/dL", [0, 1])
resting_ecg = st.sidebar.selectbox("Resting ECG", ["Normal", "ST", "LVH"])
max_hr = st.sidebar.slider("Max Heart Rate", 60, 220, 150)
exercise_angina = st.sidebar.selectbox("Exercise Induced Angina", ["Y", "N"])
oldpeak = st.sidebar.slider("Oldpeak (ST Depression)", 0.0, 6.0, 1.0)
st_slope = st.sidebar.selectbox("ST Slope", ["Up", "Flat", "Down"])

# ------------------ MAIN SECTION ------------------
st.markdown("## 🧠 Prediction Result")

if st.button("🔍 Predict Risk"):

    # Create raw input dictionary
    raw_input = {
        'Age': age,
        'RestingBP': resting_bp,
        'Cholesterol': cholesterol,
        'FastingBS': fasting_bs,
        'MaxHR': max_hr,
        'Oldpeak': oldpeak,
        'Sex_' + sex: 1,
        'ChestPainType_' + chest_pain: 1,
        'RestingECG_' + resting_ecg: 1,
        'ExerciseAngina_' + exercise_angina: 1,
        'ST_Slope_' + st_slope: 1
    }

    # Create DataFrame
    input_df = pd.DataFrame([raw_input])

    # Fill missing columns
    for col in expected_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # Reorder columns
    input_df = input_df[expected_columns]

    # Scale input
    scaled_input = scaler.transform(input_df)

    # Prediction
    prediction = model.predict(scaled_input)[0]
    probability = model.predict_proba(scaled_input)[0][1] * 100

    # Display result
    if prediction == 1:
        st.error("⚠️ **High Risk of Heart Disease**")
        st.markdown(
            f"""
            <div style='background-color:#ffe6e6; padding:25px; border-radius:12px;'>
            <h3 style='color:#d00000;'>Risk Probability: {probability:.2f}%</h3>
            <p>Please consult a healthcare professional for further evaluation.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.success("✅ **Low Risk of Heart Disease**")
        st.markdown(
            f"""
            <div style='background-color:#e6ffe6; padding:25px; border-radius:12px;'>
            <h3 style='color:#2d6a4f;'>Risk Probability: {probability:.2f}%</h3>
            <p>Maintain a healthy lifestyle and regular checkups.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ------------------ FOOTER ------------------
st.markdown(
    """
    <hr>
    <p style='text-align:center; color:gray;'>
    ⚕️ This tool is for educational purposes only and should not be considered a medical diagnosis.
    </p>
    """,
    unsafe_allow_html=True
)
