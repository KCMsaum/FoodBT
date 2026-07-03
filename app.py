import streamlit as st
import requests
import time

# ---------------- BLYNK CONFIG ----------------
# V2 = order data this app writes (fp, tp, F, ID)
# V1 = "reached" flag the server/bot app writes (1 = bot has arrived)
# V3 = "box opened" confirmation this app writes after ID re-check passes
BLYNK_TOKEN = "IO0iFP7etbXAdaT14wGIc-f6vSnQ9wIm"
SERVER = "https://sgp1.blynk.cloud"

def send_to_pin(pin, value):
    url = f"{SERVER}/external/api/update"
    params = {"token": BLYNK_TOKEN, pin: value}
    response = requests.get(url, params=params)
    return response.status_code

def read_pin(pin):
    try:
        url = f"{SERVER}/external/api/get"
        params = {"token": BLYNK_TOKEN, pin: ""}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.text.strip().strip('"')
    except Exception:
        return None
# ----------------------------------------------

st.set_page_config(
    page_title="Campus Food Delivery",
    page_icon="🍔",
    layout="centered"
)
st.title("🍽️ Campus Food Delivery Bot")

# ========================
# SESSION STATE
# ========================
if "order_placed" not in st.session_state:
    st.session_state.order_placed = False
if "order_id" not in st.session_state:
    st.session_state.order_id = ""
if "order_food" not in st.session_state:
    st.session_state.order_food = ""
if "reached" not in st.session_state:
    st.session_state.reached = False
if "box_opened" not in st.session_state:
    st.session_state.box_opened = False

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
    "VC Building",
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

# ========================
# STEP 1: PLACE ORDER
# ========================
if not st.session_state.order_placed:
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
            data_string = f"fp:{from_place},tp:{to_place},F:{food},ID:{user_id}"
            status = send_to_pin("v2", data_string)
            if status == 200:
                send_to_pin("v1", 0)  # clear any stale reached flag
                st.session_state.order_placed = True
                st.session_state.order_id = user_id
                st.session_state.order_food = food
                st.session_state.reached = False
                st.session_state.box_opened = False
                st.rerun()
            else:
                st.error("❌ Failed to send data to Blynk")

# ========================
# STEP 2: WAIT FOR BOT / VERIFY / OPEN BOX
# ========================
else:
    st.success("✅ Order sent to delivery bot!")
    st.write(f"🍔 Food: **{st.session_state.order_food}**")

    if not st.session_state.reached:
        st.info("🤖 Please wait until the bot reaches your location...")
        val = read_pin("v1")
        if val == "1":
            st.session_state.reached = True
            st.rerun()
        else:
            time.sleep(4)
            st.rerun()

    else:
        st.success("🤖 The bot has arrived at your location!")

        if not st.session_state.box_opened:
            st.subheader("🔐 Verify Your ID to Open the Food Box")
            confirm_id = st.text_input("Re-enter your ID to confirm", key="confirm_id")

            if st.button("🔓 Confirm & Open Box"):
                if confirm_id and confirm_id == st.session_state.order_id:
                    status = send_to_pin("v3", 1)
                    if status == 200:
                        st.session_state.box_opened = True
                        st.rerun()
                    else:
                        st.error("❌ Failed to send open command")
                else:
                    st.error("ID does not match your order. Please try again.")
        else:
            st.success("✅ Food box opened! Enjoy your meal.")
            st.balloons()
            if st.button("🔁 Place New Order"):
                st.session_state.order_placed = False
                st.session_state.order_id = ""
                st.session_state.order_food = ""
                st.session_state.reached = False
                st.session_state.box_opened = False
                st.rerun()
