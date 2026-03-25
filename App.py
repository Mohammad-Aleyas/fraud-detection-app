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
st.sidebar.header("👤 User Login")
username = st.sidebar.text_input("Enter Username")

if username:
    if username not in users:
        users[username] = {"history": ["L","L","M","L"]}
        save_data(users)

    history = users[username]["history"]

    st.success(f"User: {username}")

    st.subheader("📊 Previous Transactions")
    st.write(history)

    states = ['L','M','H']

    # -----------------------------
    # BUILD MARKOV MATRIX
    # -----------------------------
    matrix = np.zeros((3,3))

    for i in range(len(history)-1):
        a = states.index(history[i])
        b = states.index(history[i+1])
        matrix[a][b] += 1

    for i in range(3):
        if matrix[i].sum() != 0:
            matrix[i] /= matrix[i].sum()

    st.write("Transition Matrix:")
    st.write(matrix)

    # -----------------------------
    # NEW TRANSACTION
    # -----------------------------
    st.subheader("💰 New Transaction")

    prev_state = history[-1]
    st.write(f"Previous Transaction: {prev_state}")

    current_state = st.selectbox("Current Transaction", states)
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
    # DETECT
    # -----------------------------
    if st.button("🔍 Detect Fraud"):

        suspicious, markov_prob = markov(prev_state, current_state)
        fraud_prob = bayes(amount, location, device, time)

        # COMBINE BOTH
        final_score = fraud_prob
        if suspicious:
            final_score += 0.05

        st.subheader("🧾 Result")

        st.write(f"Markov Probability: {round(markov_prob,3)}")
        st.write(f"Fraud Probability: {round(fraud_prob*100,2)} %")
        st.write(f"Final Risk Score: {round(final_score*100,2)} %")

        # -----------------------------
        # DECISION + OTP
        # -----------------------------
        if final_score > 0.05:
            st.error("🚨 Fraud Detected! OTP Verification Required")

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
    st.info("👈 Please enter username to continue")
