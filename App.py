import streamlit as st
import numpy as np
import json
import os

st.set_page_config(page_title="Fraud Detection", layout="centered")

st.title("💳 Fraud Detection in Digital Payments Using Probabilistic Methods")

DATA_FILE = "users.json"

# -----------------------------
# LOAD / SAVE DATA
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
st.sidebar.header("👤 Login")
username = st.sidebar.text_input("Enter Username")

if not username:
    st.info("👈 Enter username to continue")
    st.stop()

if username not in users:
    users[username] = {"history": ["L","L","M","L"]}
    save_data(users)

history = users[username]["history"]

st.success(f"Logged in as {username}")

# -----------------------------
# SHOW HISTORY
# -----------------------------
st.subheader("📊 User Transaction History")
st.write("L = Low, M = Medium, H = High")
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

st.subheader("🔗 Markov Transition Matrix")
st.write(matrix)

# -----------------------------
# NEW TRANSACTION
# -----------------------------
st.subheader("💰 New Transaction")

prev_state = history[-1]
st.write(f"Previous Transaction: {prev_state}")

current_state = st.selectbox("Current Transaction", states)

amount = st.number_input("Amount (₹)", value=500)
location = st.selectbox("Location", ["local", "foreign"])
device = st.selectbox("Device", ["known", "new"])
time = st.selectbox("Time", ["day", "night"])

# -----------------------------
# MODELS
# -----------------------------
def markov_model(prev, curr):
    i = states.index(prev)
    j = states.index(curr)
    return matrix[i][j]

def bayesian_model(amount, location, device, time):
    P = 0.01

    P_amount = 0.8 if amount > 10000 else 0.2
    P_location = 0.7 if location == "foreign" else 0.3
    P_device = 0.6 if device == "new" else 0.2
    P_time = 0.5 if time == "night" else 0.2

    return P * P_amount * P_location * P_device * P_time

# -----------------------------
# DETECT BUTTON
# -----------------------------
if st.button("🔍 Detect Fraud"):

    markov_prob = markov_model(prev_state, current_state)
    fraud_prob = bayesian_model(amount, location, device, time)

    # Markov decision
    suspicious = markov_prob < 0.1

    # Final score
    final_score = fraud_prob
    if suspicious:
        final_score += 0.1

    st.subheader("🧾 Analysis Result")

    # Markov result
    st.write(f"Markov Probability: {round(markov_prob*100,2)} %")
    if suspicious:
        st.warning("⚠️ Abnormal Transaction Pattern")
    else:
        st.success("✅ Normal Transaction Pattern")

    # Bayesian result
    st.write(f"Fraud Probability: {round(fraud_prob*100,2)} %")

    # Risk factors (IN %)
    st.subheader("📊 Risk Factors")
    st.write(f"Amount Risk: {'80%' if amount > 10000 else '20%'}")
    st.write(f"Location Risk: {'70%' if location == 'foreign' else '30%'}")
    st.write(f"Device Risk: {'60%' if device == 'new' else '20%'}")
    st.write(f"Time Risk: {'50%' if time == 'night' else '20%'}")

    # Final score
    st.write(f"Final Fraud Score: {round(final_score*100,2)} %")

    # -----------------------------
    # FINAL DECISION + OTP
    # -----------------------------
    if final_score > 0.08:
        st.error("🚨 Fraud Detected")

        st.subheader("🔐 OTP Verification")
        otp = st.text_input("Enter OTP")

        if otp == "1234":
            st.success("✅ OTP Verified → Transaction Allowed")
        elif otp:
            st.error("❌ Incorrect OTP")

    else:
        st.success("✅ Transaction Approved")

    # Save transaction
    history.append(current_state)
    users[username]["history"] = history
    save_data(users)
