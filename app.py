import streamlit as st
from utils.auth_utils import load_config, get_authenticator, signup_form
from utils.chat_ui import render_chat  # or inline if you skipped chat_ui.py

def main():
    st.set_page_config("MindMate", layout="centered")
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
        return

    if status in (False, None):
        if st.button("New user? Sign up", key="to_signup"):
            st.session_state.show_signup = True
        if status is False:
            st.error("Bad credentials.")
        else:
            st.info("Enter login details.")
        return

    # logged in
    auth.logout("Logout", key="logout_btn", location="sidebar")
    st.success(f"Welcome, {name}!")
    render_chat(username)

if __name__ == "__main__":
    main()

