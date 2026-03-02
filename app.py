import streamlit as st
import pickle
import re
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("scam_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Job Scam Risk Detection",
    layout="wide"
)

# ---------------- CUSTOM STYLING ----------------
st.markdown("""
<style>
.main {background-color: #f6f8fc;}
.block-container {padding-top: 2rem;}
.card {
    background-color: white;
    padding: 25px;
    border-radius: 14px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.1);
    margin-top: 20px;
}
.risk-high {color: #b30000; font-size: 22px; font-weight: bold;}
.risk-medium {color: #ff8c00; font-size: 22px; font-weight: bold;}
.risk-low {color: #006400; font-size: 22px; font-weight: bold;}
.footer {
    text-align: center;
    color: gray;
    font-size: 14px;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🚨 AI-Based Job Offer Risk Assessment System")
st.markdown(
    "This system analyzes **job structure, salary realism, payment requests, "
    "contact authenticity, URLs, and message content** to detect job and internship scams."
)

# ---------------- INPUT SECTION ----------------
st.markdown("## 📝 Job Offer Details")

col1, col2 = st.columns(2)

with col1:
    job_title = st.text_input("Job Title")
    company = st.text_input("Company Name")
    salary = st.text_input("Salary Offered (e.g., 30000/month)")

with col2:
    email = st.text_input("Contact Email")
    link = st.text_input("Job Application URL")

description = st.text_area("Job Description / Message")

# ---------------- ANALYSIS ----------------
if st.button("🔍 Analyze Job Offer"):

    risk = 0
    reasons = []

    # ---------- ML TEXT ANALYSIS ----------
    combined_text = f"{job_title} {company} {description}"
    vec = vectorizer.transform([combined_text])
    pred = model.predict(vec)[0]

    if pred == 1:
        risk += 30
        reasons.append("Scam-like language detected")

    # ---------- PAYMENT REQUEST ----------
    if re.search(r'fee|payment|deposit|registration|charges', description.lower()):
        risk += 25
        reasons.append("Payment request detected")

    # ---------- SALARY REALISM ----------
    numbers = re.findall(r'\d+', salary)
    if numbers:
        sal = int(numbers[0])
        if sal > 50000 and "intern" in job_title.lower():
            risk += 20
            reasons.append("Unrealistic salary for internship")

    # ---------- EMAIL AUTHENTICITY ----------
    if email.endswith("@gmail.com") or email.endswith("@yahoo.com") or email.endswith("@outlook.com"):
        risk += 15
        reasons.append("Non-official email domain")

    # ---------- URL CHECK ----------
    if "bit.ly" in link or len(link) < 15:
        risk += 10
        reasons.append("Suspicious job link")

    # ---------- COMPANY NAME ----------
    if len(company.split()) <= 2:
        risk += 5
        reasons.append("Generic or unverifiable company name")

    risk = min(risk, 100)

    # ---------------- RESULT CARD ----------------
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🔍 Analysis Result")

    # Risk meter
    st.markdown("### 🔥 Risk Meter")
    st.progress(risk / 100)

    if risk >= 70:
        st.markdown(f"<p class='risk-high'>❌ HIGH RISK SCAM ({risk}%)</p>", unsafe_allow_html=True)
        advice = "Do NOT proceed. This job shows multiple scam indicators."
    elif risk >= 40:
        st.markdown(f"<p class='risk-medium'>⚠️ MEDIUM RISK ({risk}%)</p>", unsafe_allow_html=True)
        advice = "Verify company details carefully before applying."
    else:
        st.markdown(f"<p class='risk-low'>✅ LOW RISK / LIKELY GENUINE ({risk}%)</p>", unsafe_allow_html=True)
        advice = "Appears genuine. Always apply through official portals."

    st.markdown("**🧠 Advice:** " + advice)

    # ---------------- RISK FACTORS ----------------
    st.markdown("### 📌 Detected Risk Factors")
    if reasons:
        for r in reasons:
            st.write("•", r)
    else:
        st.write("No major risk factors detected")

    # ---------------- CENTERED GRAPHS ----------------
    st.markdown("---")
    st.subheader("📊 Visual Risk Analysis")

    # -------- Graph 1: Risk Contribution --------
    risk_data = {
        "Scam Language": 30 if "Scam-like language detected" in reasons else 0,
        "Payment Request": 25 if "Payment request detected" in reasons else 0,
        "Unrealistic Salary": 20 if "Unrealistic salary for internship" in reasons else 0,
        "Email Domain": 15 if "Non-official email domain" in reasons else 0,
        "Suspicious URL": 10 if "Suspicious job link" in reasons else 0,
        "Company Name": 5 if "Generic or unverifiable company name" in reasons else 0,
    }

    df = pd.DataFrame.from_dict(risk_data, orient="index", columns=["Risk Contribution"])
    df = df[df["Risk Contribution"] > 0]

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown("#### Risk Contribution Breakdown")
        if not df.empty:
            st.bar_chart(df)

    # -------- Graph 2: Risk Distribution --------
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        [risk, 100 - risk],
        labels=["Risk", "Safe"],
        autopct="%1.1f%%",
        startangle=90
    )
    ax.axis("equal")

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.markdown("#### Overall Risk Distribution")
        st.pyplot(fig)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
AI-Based Job Offer Risk Assessment & Scam Detection System <br>
Final-Year / IPD Level Project
</div>
""", unsafe_allow_html=True)

