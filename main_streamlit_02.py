import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

# App Title
st.set_page_config(page_title='RideAid - Vehicle Diagnosis', page_icon='🚗', layout='wide')
st.title('🚗 RideAid - Vehicle Diagnosis Chat')

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

# Define Custom CSS Styles
st.markdown("""
    <style>
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
            margin: 5px 0;
            max-width: 75%;
            font-size: 18px;
            font-weight: bold;
            word-wrap: break-word;
        }
        .user-message {
            background-color: #40dec7;
            color: black;
            text-align: left;
            margin-left: auto;
        }
        .assistant-message {
            background-color: #d59253;
            color: black;
            text-align: left;
            margin-right: auto;
        }
        .start-btn-container {
            text-align: center;
            margin-bottom: 15px;
        }
        .start-btn {
            background-color: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            width: 100%;
            font-size: 48px;
        }
        .start-btn:hover {
            background-color: #218838;
        }
        .score-box {
            background-color: #e8f4f8;
            padding: 8px;
            border-radius: 10px;
            text-align: center;
            color: #007BFF;
            font-size: 24px;
            font-weight: bold;
        }
        .diagnosis-box {
            background-color: #e8f4f8;
            padding: 8px;
            border-radius: 10px;
            text-align: left;
            color: #007BFF;
            font-size: 24px;
            font-weight: bold;
            height: 200px;
            overflow-y: auto;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        /* Fix input field width to match messages box */
        .chat-input-container {
            width: 75%;
            max-width: 600px;  /* Ensures it doesn't stretch too much */
            padding-top: 10px;
            text-align: left;
        }
        /* Adjust Streamlit's chat input width */
        [data-testid="stChatInput"] {
            max-width: 1290px !important; /* Fixes stretching */
            width: 100% !important;
            margin: 0;
            display: block;
            text-align: left;
        }
    </style>
""", unsafe_allow_html=True)

# Layout: Chat on Left, Diagnostic Summary on Right
col1, col2 = st.columns([3, 1])

with col1:
    start_button = st.button("🚀 Start Diagnosis", key="start_diagnosis", use_container_width=True)
    st.markdown("### 💬 Chat History")

    with st.container():
        for message in st.session_state.messages:
            role_class = "user-message" if message["role"] == "user" else "assistant-message"
            st.markdown(
                f"<div class='message-box {role_class}'>{message['content']}</div>",
                unsafe_allow_html=True
            )

    if start_button:
        url = "http://127.0.0.1:9035/vehicle_diagnosis"
        headers = {"Content-Type": "application/json"}
        body = {
            "user_id": user_id,
            "chat_id": None,
            "query": None
        }
        res = requests.post(url, headers=headers, json=body)
        if res.status_code == 200:
            data = res.json()
            st.session_state.chat_id = data["chat_id"]
            st.session_state.messages.append({'role': 'assistant', 'content': data["response"]})
        st.rerun()

st.markdown("""<div class='chat-input-container'>""", unsafe_allow_html=True)
query = st.chat_input("✍️ Describe your vehicle issue")
st.markdown("""</div>  <!-- Close chat-input-container -->""", unsafe_allow_html=True)

if query:
    st.session_state.messages.append({'role': 'user', 'content': query})
    try:
        url = "http://127.0.0.1:9035/vehicle_diagnosis"
        headers = {"Content-Type": "application/json"}
        body = {
            "chat_id": st.session_state.chat_id,
            "user_id": user_id,
            "query": query
        }
        res = requests.post(url, headers=headers, json=body)
        if res.status_code == 200:
            data = res.json()
            st.session_state.messages.append({'role': 'assistant', 'content': data["response"]})
            st.session_state.stage_history.append(data["stage"])
            st.session_state.results = data["results"]
    except Exception as ex:
        error_msg = f"❌ Error: {ex}"
        st.session_state.messages.append({'role': 'assistant', 'content': error_msg})
    
    st.rerun()

with col2:
    st.markdown("### 📊 Stage Trend")
    if st.session_state.stage_history:
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.plot(st.session_state.stage_history, marker='o', linestyle='-', color='b')
        ax.set_title("Stage Progression")
        ax.set_xlabel("Query Attempts")
        ax.set_ylabel("Stage")
        ax.set_yticks([1, 2, 3, 4])
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.markdown("<div class='score-box'>No stage data available.</div>", unsafe_allow_html=True)
    
    st.markdown("### 📜 Diagnosis Results")
    if st.session_state.results:
        st.markdown(f"<div class='diagnosis-box'>{st.session_state.results}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='score-box'>No diagnosis results available.</div>", unsafe_allow_html=True)