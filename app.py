import streamlit as st
import requests

# ---------------- BLYNK CONFIG ----------------
BLYNK_TOKEN = "eveLTyW2cyI55u0wSuLjG57RS_4sZvOC"
SERVER = "https://sgp1.blynk.cloud"

def send_to_v2(value):
    url = f"{SERVER}/external/api/update"
    params = {
        "token": BLYNK_TOKEN,
        "v2": value
    }
    response = requests.get(url, params=params)
    return response.status_code
# ----------------------------------------------

st.set_page_config(
    page_title="Campus Food Delivery",
    page_icon="🍔",
    layout="centered"
)

st.title("🍽️ Campus Food Delivery Bot")

# Food options
foods = [
    "Rice",
    "Burger",
    "Pizza",
    "Biriyani",
    "Sandwich",
    "Noodles"
]

# Location options (same for both)
locations = [
    "BangaBondhu Hall",
    "TSC",
    "Shah Hall",
    "Tareque Huda Hall",
    "Q.K. Hall",
    "Sheikh Rassel Hall",
    "Sufia Kamal and Samsen Nahar Hall",
    "EME Building",
    "CSE Building",
    "3 no. canteen"
]

st.subheader("🧾 Order Details")

food = st.selectbox("🍛 Select Food", foods)
from_place = st.selectbox("📍 From Place", locations)
to_place = st.selectbox("📍 To Place", locations)
user_id = st.text_input("🆔 Enter Your ID")

if st.button("📦 Place Order"):
    if not user_id:
        st.error("Please enter your ID")
    elif from_place == to_place:
        st.error("From and To locations cannot be the same")
    else:
        # Create string for V2
        data_string = f"fp:{from_place},tp:{to_place},F:{food},ID:{user_id}"

        status = send_to_v2(data_string)

        if status == 200:
            st.success("✅ Order sent to delivery bot!")
            st.code(data_string)
            st.info("🤖 Please wait until the bot reaches your location")
        else:
            st.error("❌ Failed to send data to Blynk")
