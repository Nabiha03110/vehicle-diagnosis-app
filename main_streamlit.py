import streamlit as st
import requests
import json
import matplotlib.pyplot as plt

# App Title
st.set_page_config(page_title='RideAid - Vehicle Diagnosis', page_icon='🚗', layout='wide')
st.markdown("""
    <style>
        .title-container {
            text-align: center;
            margin-bottom: 20px;
        }
        .chat-history-container {
            text-align: left;
            margin-left: 245px;
            margin-bottom: 10px;
        }
        .chat-container {
            padding: 15px;
            border-radius: 10px;
            max-height: 500px;
            overflow-y: auto;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
        .message-box {
            padding: 10px;
            border-radius: 10px;
            margin: 7px 250px;
            max-width: 38%;
            font-size: 18px;
            font-weight: normal;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #b2b5e0;
            color: black;
            text-align: left;
            margin-left: auto;
        }
        .assistant-message {
            background-color: #ddd0c8;
            color: black;
            text-align: left;
            margin-right: auto;
        }
        .chat-input-container {
            width: 75%;
            max-width: 600px;
            padding-top: 10px;
            text-align: center;
        }
        [data-testid="stChatInput"] {
            max-width: 1290px !important;
            width: 100% !important;
            margin: 0 auto;
            display: block;
            text-align: left;
        }
        .start-btn {
            width: 75%;
            max-width: 600px;
            padding-top: 10px;
            text-align: center;
        }
        [data-testid="stButton"] {
            max-width: 200px !important;
            width: 100% !important;
            margin: 0 auto;
            display: block;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)


# Initialize session state variables
if "chat_id" not in st.session_state:
    st.session_state.chat_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stage_history" not in st.session_state:
    st.session_state.stage_history = []
if "results" not in st.session_state:
    st.session_state.results = None

# User ID input
user_id = 1

st.markdown("<div class='title-container'><h1>🚗 RideAid - Vehicle Diagnosis Chat</h1></div>", unsafe_allow_html=True)

# Start Diagnosis Button
st.markdown("<div class='chat-input-container'>", unsafe_allow_html=True)
start_button = st.button("🚀 Start Diagnosis", key="start_diagnosis", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# Chat History
st.markdown("<div class='chat-history-container'><h3>💬 Chat History</h3></div>", unsafe_allow_html=True)
with st.container():
    for message in st.session_state.messages:
        role_class = "user-message" if message["role"] == "user" else "assistant-message"
        st.markdown(
            f"<div class='message-box {role_class}'>{message['content']}</div>",
            unsafe_allow_html=True
        )

if start_button:
    # url = "http://127.0.0.1:9035/vehicle_diagnosis"
    url = "http://51.21.161.137:9036/vehicle_diagnosis"
    headers = {"Content-Type": "application/json"}
    body = {"user_id": user_id, "chat_id": None, "query": None}
    res = requests.post(url, headers=headers, json=body)
    if res.status_code == 200:
        data = res.json()
        st.session_state.chat_id = data["chat_id"]
        st.session_state.messages.append({'role': 'assistant', 'content': data["response"]})
    st.rerun()

# Chat Input
st.markdown("<div class='chat-input-container'>", unsafe_allow_html=True)
query = st.chat_input("✍️ Describe your vehicle issue")
st.markdown("</div>", unsafe_allow_html=True)

if query:
    st.session_state.messages.append({'role': 'user', 'content': query})
    try:
        # url = "http://127.0.0.1:9035/vehicle_diagnosis"
        url = "http://51.21.161.137:9036/vehicle_diagnosis"
        headers = {"Content-Type": "application/json"}
        body = {"chat_id": st.session_state.chat_id, "user_id": user_id, "query": query}
        res = requests.post(url, headers=headers, json=body)
        if res.status_code == 200:
            data = res.json()
            diagnosis_response = data["response"]
            diagnosis_results = data.get("results", "No diagnosis details available.")
            if diagnosis_results != []:
                full_response = f"{diagnosis_response}\n\n🔗 Related Articles:\n\n{diagnosis_results}"
            else:
                full_response = diagnosis_response
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})
            st.session_state.stage_history.append(data.get("stage", "Unknown"))
    except Exception as ex:
        error_msg = f"❌ Error: {ex}"
        st.session_state.messages.append({'role': 'assistant', 'content': error_msg})
    st.rerun()