import streamlit as st
import numpy as np
import json
import os
import matplotlib.pyplot as plt

st.set_page_config(page_title="Smart Fraud Detection", layout="centered")

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
# UI HEADER
# -----------------------------
st.markdown("## 💳 Fraud Detection System in Digital Payments Using Probabilistic Methods ")

# -----------------------------
# LOGIN
# -----------------------------
st.sidebar.header("👤 Login")
username = st.sidebar.text_input("Enter Username")

if username:
    if username not in users:
        users[username] = {"history": ["L","L","M","L"]}
        save_data(users)

    history = users[username]["history"]

    st.success(f"Welcome, {username}")

    # -----------------------------
    # CARD UI
    # -----------------------------
    st.markdown("### 💳 Your Card")
    st.markdown(f"""
    <div style='padding:20px; border-radius:15px; background:#1e3a8a; color:white'>
        <h4>Digital Payment Methods</h4>
        <p>**** **** **** 1234</p>
        <p>User: {username}</p>
    </div>
    """, unsafe_allow_html=True)

    # -----------------------------
    # HISTORY GRAPH
    # -----------------------------
    st.subheader("📊 Spending Pattern")

    states = ['L','M','H']
    count = [history.count('L'), history.count('M'), history.count('H')]

    fig, ax = plt.subplots()
    ax.bar(states, count)
    ax.set_title("Transaction Pattern")

    st.pyplot(fig)

    # -----------------------------
    # MARKOV MATRIX
    # -----------------------------
    matrix = np.zeros((3,3))

    for i in range(len(history)-1):
        a = states.index(history[i])
        b = states.index(history[i+1])
        matrix[a][b] += 1

    for i in range(3):
        if matrix[i].sum() != 0:
            matrix[i] /= matrix[i].sum()

    # -----------------------------
    # NEW TRANSACTION
    # -----------------------------
    st.subheader("💰 New Transaction")

    prev_state = history[-1]
    st.write(f"Previous: {prev_state}")

    current_state = st.selectbox("Transaction Type", states)
    amount = st.number_input("Amount", value=500)
    location = st.selectbox("Location", ["local", "foreign"])
    device = st.selectbox("Device", ["known", "new"])
    time = st.selectbox("Time", ["day", "night"])

    # -----------------------------
    # MODELS
    # -----------------------------
    def markov(prev, curr):
        i = states.index(prev)
        j = states.index(curr)
        prob = matrix[i][j]
        return prob < 0.1, prob

    def bayes(amount, location, device, time):
        P = 0.01
        P *= 0.8 if amount > 10000 else 0.2
        P *= 0.7 if location == "foreign" else 0.3
        P *= 0.6 if device == "new" else 0.2
        P *= 0.5 if time == "night" else 0.2
        return P

    # -----------------------------
    # FRAUD METER
    # -----------------------------
    def fraud_meter(score):
        st.progress(min(int(score*1000), 100))
        st.write(f"Fraud Score: {round(score*100,2)}%")

    # -----------------------------
    # DETECT
    # -----------------------------
    if st.button("🔍 Detect Fraud"):

        suspicious, prob = markov(prev_state, current_state)
        fraud_prob = bayes(amount, location, device, time)

        st.subheader("🧾 Result")

        st.write(f"Markov Probability: {round(prob,3)}")

        if suspicious:
            st.warning("⚠️ Abnormal Pattern Detected")
        else:
            st.success("✅ Normal Pattern")

        fraud_meter(fraud_prob)

        # -----------------------------
        # OTP SIMULATION
        # -----------------------------
        if fraud_prob > 0.05:
            st.error("🚨 Fraud Suspected! OTP Verification Required")

            otp = st.text_input("Enter OTP (use 1234)")

            if otp == "1234":
                st.success("✅ OTP Verified - Transaction Allowed")
            elif otp:
                st.error("❌ Incorrect OTP")

        else:
            st.success("✅ Transaction Approved")

        # SAVE HISTORY
        history.append(current_state)
        users[username]["history"] = history
        save_data(users)

else:
    st.info("👈 Please login from sidebar")
