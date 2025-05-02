from utils.auth_utils import load_config, get_authenticator, signup_form
from utils.chat_ui import render_chat  # or inline if you skipped chat_ui.py
import streamlit as st
import base64

# Page config
st.set_page_config("MindMate", layout="centered")

# Read and encode logo image as base64
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_base64 = get_base64_of_image('data/KK.png')

# CSS for enhanced UI with heading and caption
st.markdown("""
    <style>
        /* Background Gradient */
        body {
            background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        }


        /* Header with logo, heading and caption */
        .header {
            text-align: center;
            margin-bottom: 1.5rem;
            padding: 1rem;
            background: linear-gradient(90deg, rgba(92,107,192,1) 0%, rgba(63,81,181,1) 100%);
            border-radius: 10px;
        }

        .header h1 {
            font-size: 2rem;
            color: #ffffff;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .header .caption {
            font-size: 1rem;
            color: #e0e0e0;
            margin: 0.5rem 0 1rem 0;
        }

        .header img {
            width: 120px;
            border-radius: 50%;
            border: 2px solid #ffffff;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        /* Styling buttons */
        .stButton > button {
            background-color: #5C6BC0;
            color: white;
            font-weight: bold;
            padding: 0.75rem 2rem;
            border-radius: 25px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border: none;
            font-size: 1rem;
        }

        .stButton > button:hover {
            background-color: #3F51B5;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        }

        /* Styling text inputs */
        .stTextInput > div > div > input {
            border-radius: 25px;
            border: 1px solid #ddd;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            width: 100%;
        }

        .stTextInput > div > div > input:focus {
            border-color: #5C6BC0;
            outline: none;
        }

        /* Success message */
        .success-box {
            background-color: #E8F5E9;
            color: #388E3C;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin-top: 1.5rem;
        }

        /* Error message */
        .error-box {
            background-color: #FFEBEE;
            color: #D32F2F;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin-top: 1.5rem;
        }

        /* Info message */
        .info-box {
            background-color: #E3F2FD;
            color: #1976D2;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            margin-top: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Visual container
st.markdown('<div class="main">', unsafe_allow_html=True)

# Header with heading, caption, and base64 logo
logo_html = (
    "<div class='header'>"
    "<h1>Welcome to MindMate</h1>"
    "<p class='caption'>Let's understand you</p>"
    f"<img src='data:image/jpeg;base64,{logo_base64}' alt='MindMate Logo'>"
    "</div>"
)
st.markdown(logo_html, unsafe_allow_html=True)

# Load config
cfg = load_config()

# toggle in-session
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

auth = get_authenticator(cfg)
auth.login(key="login", location="main")

status   = st.session_state.get("authentication_status")
name     = st.session_state.get("name")
username = st.session_state.get("username")

if st.session_state.show_signup:
    done = signup_form(cfg)
    if done:
        st.session_state.show_signup = False
    st.markdown('</div>', unsafe_allow_html=True)  # close .main
    st.stop()

if status in (False, None):
    if st.button("New user? Sign up", key="to_signup"):
        st.session_state.show_signup = True
    if status is False:
        st.markdown('<div class="error-box">❌ Bad credentials. Please try again.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-box">🔐 Enter login details to continue.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # close .main
    st.stop()

# Logged in
auth.logout("Logout", key="logout_btn", location="sidebar")

st.markdown(f'<div class="success-box">✅ Welcome, {name}!</div>', unsafe_allow_html=True)
render_chat(username)

st.markdown('</div>', unsafe_allow_html=True)  # close .main
