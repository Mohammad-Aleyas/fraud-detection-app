import streamlit as st
import numpy as np
import json
import os

st.set_page_config(page_title="Fraud Detection", layout="centered")

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
username = st.text_input("Enter Username")

if not username:
    st.stop()

if username not in users:
    users[username] = {"history": ["L","L","M","L"]}
    save_data(users)

history = users[username]["history"]

st.write("### 📊 Transaction History")
st.write(history)

states = ['L','M','H']

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
st.write("### 💰 New Transaction")

prev_state = history[-1]
st.write(f"Previous: {prev_state}")

current_state = st.selectbox("Current Transaction", states)

amount = st.number_input("Amount", value=500)
location = st.selectbox("Location", ["local", "foreign"])
device = st.selectbox("Device", ["known", "new"])
time = st.selectbox("Time", ["day", "night"])

# -----------------------------
# DETECT
# -----------------------------
if st.button("Detect Fraud"):

    # MARKOV
    i = states.index(prev_state)
    j = states.index(current_state)
    markov_prob = matrix[i][j]

    suspicious = markov_prob < 0.2   # relaxed threshold

    # BAYESIAN (simple & stable)
    score = 0

    if amount > 10000:
        score += 30
    else:
        score += 10

    if location == "foreign":
        score += 25
    else:
        score += 10

    if device == "new":
        score += 20
    else:
        score += 5

    if time == "night":
        score += 15
    else:
        score += 5

    # Add Markov impact
    if suspicious:
        score += 20

    st.write("### 🧾 Result")

    st.write(f"Markov Probability: {round(markov_prob*100,2)} %")

    if suspicious:
        st.warning("⚠️ Abnormal Pattern")
    else:
        st.success("✅ Normal Pattern")

    st.write(f"Fraud Score: {score} %")

    # -----------------------------
    # FINAL DECISION
    # -----------------------------
    if score >= 60:
        st.error("🚨 Fraud Detected")

        otp = st.text_input("Enter OTP (1234)")

        if otp == "1234":
            st.success("✅ OTP Verified → Transaction Allowed")
        elif otp:
            st.error("❌ Wrong OTP")

    else:
        st.success("✅ Transaction Approved")

    # Save transaction
    history.append(current_state)
    users[username]["history"] = history
    save_data(users)
