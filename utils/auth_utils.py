# auth_utils.py
import yaml
import bcrypt
from pathlib import Path
from datetime import datetime, date
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

CONFIG_PATH = "data/config.yaml"

def load_config():
    if not Path(CONFIG_PATH).exists():
        with open(CONFIG_PATH, "w") as f:
            yaml.dump({
                "credentials": {"usernames": {}},
                "cookie": {
                    "name": "personalized_llm_cookie",
                    "key": "some_secure_key",
                    "expiry_days": 30,
                }
            }, f)
    with open(CONFIG_PATH) as f:
        return yaml.load(f, Loader=SafeLoader)

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f)

def get_authenticator(config):
    return stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
    )

def signup_form(config):
    """Returns True once a new user has been registered."""
    st.header("Create a new account")
    full_name = st.text_input("Full Name", key="reg_name")
    dob       = st.date_input(
        "Date of Birth",
        min_value=date(1947, 1, 1),
        value=date.today(),
        key="reg_dob"
    )
    email     = st.text_input("Email (login ID)", key="reg_email")
    pw        = st.text_input("Password", type="password", key="reg_pw")

    if st.button("Sign Up", key="reg_submit"):
        if email in config["credentials"]["usernames"]:
            st.error("This email’s already registered.")
        elif not all([full_name, dob, email, pw]):
            st.warning("Fill all fields.")
        else:
            age = datetime.now().year - dob.year
            hashed = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
            config["credentials"]["usernames"][email] = {
                "name": full_name,
                "password": hashed,
                "dob":    dob.strftime("%Y-%m-%d"),
                "age":    age
            }
            save_config(config)
            st.success("Registration successful! Please log in.")
            return True
    if st.button("← Back to Login", key="back"):
        return True  # signal to go back
    return False
