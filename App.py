import streamlit as st
import numpy as np
import json
import os
import random
from datetime import datetime

st.set_page_config(page_title="Fraud Detection", layout="centered")

# -----------------------------
# STYLE (GPay-like)
# -----------------------------
st.markdown("""
<style>
.tx-card {
    background:#1f2937;
    padding:15px;
    border-radius:12px;
    margin-bottom:10px;
    color:white;
    display:flex;
    justify-content:space-between;
    align-items:center;
}
.success {color:#22c55e; font-weight:bold;}
.failed {color:#ef4444; font-weight:bold;}
.small {font-size:12px; color:#9ca3af;}
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

# -----------------------------
# CREATE TRANSACTION
# -----------------------------
def create_tx(state):
    if state == "L":
        amount = random.randint(100,500)
    elif state == "M":
        amount = random.randint(600,5000)
    else:
        amount = random.randint(6000,20000)

    return {
        "type": state,
        "amount": amount,
        "time": datetime.now().strftime("%d %b %I:%M %p"),
        "location": "local",
        "status": "Success"
    }

users = load_data()

# -----------------------------
# LOGIN
# -----------------------------
username = st.text_input("👤 Enter Username")

if not username:
    st.stop()

if username not in users:
    users[username] = {
        "history": [
            create_tx("L"),
            create_tx("L"),
            create_tx("M"),
            create_tx("L")
        ]
    }
    save_data(users)

history = users[username]["history"]
states = ['L','M','H']

# -----------------------------
# HISTORY (GPay style)
# -----------------------------
st.markdown("## 📱 Recent Payments")

for tx in reversed(history[-6:]):

    status_class = "success" if tx["status"]=="Success" else "failed"
    status_text = "✔ Paid" if tx["status"]=="Success" else "❌ Failed"

    st.markdown(
        f"""
        <div class="tx-card">
            <div>
                <b>₹{tx["amount"]}</b><br>
                <span class="small">{tx["time"]} • {tx["location"]}</span>
            </div>
            <div class="{status_class}">
                {status_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# NEW TRANSACTION
# -----------------------------
st.markdown("## 💸 Make Payment")

prev_state = history[-1]["type"]

current_state = st.selectbox("Transaction Type", states)
amount = st.number_input("Amount", value=500)
location = st.selectbox("Location", ["local","foreign"])
device = st.selectbox("Device", ["known","new"])
time = st.selectbox("Time", ["day","night"])

# -----------------------------
# DETECT
# -----------------------------
if st.button("Pay Now"):

    # MARKOV
    states_only = [tx["type"] for tx in history]

    matrix = np.zeros((3,3))
    for i in range(len(states_only)-1):
        a = states.index(states_only[i])
        b = states.index(states_only[i+1])
        matrix[a][b] += 1

    for i in range(3):
        if matrix[i].sum() != 0:
            matrix[i] /= matrix[i].sum()

    i = states.index(prev_state)
    j = states.index(current_state)
    markov_prob = matrix[i][j]

    suspicious = markov_prob < 0.2

    # SCORE
    score = 0
    score += 30 if amount > 10000 else 10
    score += 25 if location=="foreign" else 10
    score += 20 if device=="new" else 5
    score += 15 if time=="night" else 5
    if suspicious:
        score += 20

    st.markdown("## 🧾 Payment Status")

    if score >= 60:
        st.error("❌ Payment Failed (Fraud Detected)")

        otp = st.text_input("Enter OTP")

        if otp:
            if otp == "1234":
                st.success("✔ OTP Verified → Payment Successful")
                status = "Success"
            else:
                st.error("Incorrect OTP")
                status = "Failed"
        else:
            status = "Failed"

    else:
        st.success("✔ Payment Successful")
        status = "Success"

    # SAVE TRANSACTION
    new_tx = {
        "type": current_state,
        "amount": amount,
        "time": datetime.now().strftime("%d %b %I:%M %p"),
        "location": location,
        "status": status
    }

    history.append(new_tx)
    users[username]["history"] = history
    save_data(users)
