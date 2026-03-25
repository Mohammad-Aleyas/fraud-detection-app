import streamlit as st
import numpy as np
import json
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Fraud Detection", layout="centered")

# -----------------------------
# CUSTOM CSS (PREMIUM UI)
# -----------------------------
st.markdown("""
<style>
.card {
    padding:15px;
    border-radius:12px;
    color:white;
    text-align:center;
    font-weight:bold;
    box-shadow: 2px 2px 12px rgba(0,0,0,0.3);
}
.low {background: linear-gradient(135deg,#22c55e,#14532d);}
.med {background: linear-gradient(135deg,#f59e0b,#78350f);}
.high {background: linear-gradient(135deg,#ef4444,#7f1d1d);}
.badge {
    padding:10px;
    border-radius:8px;
    font-weight:bold;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.title("💳 Fraud Detection in Digital Payments Using Probabilistic Methods")

DATA_FILE = "users.json"

# -----------------------------
# LOAD / SAVE
# -----------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

users = load_data()

# -----------------------------
# LOGIN
# -----------------------------
username = st.text_input("👤 Enter Username")

if not username:
    st.stop()

if username not in users:
    users[username] = {"history": ["L","L","M","L"]}
    save_data(users)

history = users[username]["history"]

# -----------------------------
# HISTORY DASHBOARD
# -----------------------------
st.markdown("## 📊 Transaction Dashboard")

cols = st.columns(len(history))

for i, val in enumerate(history):
    cls = "low" if val=="L" else "med" if val=="M" else "high"
    cols[i].markdown(f"<div class='card {cls}'>{val}</div>", unsafe_allow_html=True)

low = history.count('L')
med = history.count('M')
high = history.count('H')

c1, c2, c3 = st.columns(3)
c1.metric("🟢 Low", low)
c2.metric("🟡 Medium", med)
c3.metric("🔴 High", high)

# -----------------------------
# CHART
# -----------------------------
fig, ax = plt.subplots()
ax.bar(["Low","Medium","High"], [low,med,high])
ax.set_title("Spending Pattern")
st.pyplot(fig)

# -----------------------------
# NEW TRANSACTION
# -----------------------------
st.markdown("## 💰 New Transaction")

states = ['L','M','H']
prev_state = history[-1]

st.write(f"Previous: {prev_state}")

current_state = st.selectbox("Transaction Type", states)
amount = st.number_input("Amount", value=500)
location = st.selectbox("Location", ["local","foreign"])
device = st.selectbox("Device", ["known","new"])
time = st.selectbox("Time", ["day","night"])

# -----------------------------
# DETECT
# -----------------------------
if st.button("🚀 Analyze Transaction"):

    # MARKOV
    matrix = np.zeros((3,3))
    for i in range(len(history)-1):
        a = states.index(history[i])
        b = states.index(history[i+1])
        matrix[a][b] += 1

    for i in range(3):
        if matrix[i].sum() != 0:
            matrix[i] /= matrix[i].sum()

    i = states.index(prev_state)
    j = states.index(current_state)
    markov_prob = matrix[i][j]

    suspicious = markov_prob < 0.2

    # SCORE SYSTEM (CLEAR)
    score = 0
    score += 30 if amount > 10000 else 10
    score += 25 if location=="foreign" else 10
    score += 20 if device=="new" else 5
    score += 15 if time=="night" else 5
    if suspicious:
        score += 20

    st.markdown("## 🧾 Analysis Result")

    st.write(f"Markov Probability: {round(markov_prob*100,2)} %")
    st.write(f"Fraud Score: {score} %")

    # -----------------------------
    # RISK BADGE
    # -----------------------------
    if score < 40:
        st.markdown("<div class='badge' style='background:#22c55e;color:white'>LOW RISK</div>", unsafe_allow_html=True)
    elif score < 60:
        st.markdown("<div class='badge' style='background:#f59e0b;color:white'>MEDIUM RISK</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='badge' style='background:#ef4444;color:white'>HIGH RISK</div>", unsafe_allow_html=True)

    # -----------------------------
    # DECISION + OTP
    # -----------------------------
    if score >= 60:
        st.error("🚨 FRAUD DETECTED")

        otp = st.text_input("Enter OTP (1234)")

        if otp == "1234":
            st.success("✅ OTP VERIFIED - Transaction Allowed")
        elif otp:
            st.error("❌ Wrong OTP")

    else:
        st.success("✅ Transaction Approved")

    # SAVE HISTORY
    history.append(current_state)
    users[username]["history"] = history
    save_data(users)
