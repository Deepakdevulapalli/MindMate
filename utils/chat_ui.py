import streamlit as st
import re
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from streamlit.components.v1 import html

from llm.gorq_client import generate_response
from utils.session_storage import (
    load_session,
    save_session,
    save_global_summaries,
    load_global_summaries,
    delete_session,
    list_user_sessions,
)

# Configuration path for user credentials
CONFIG_PATH = "data/config.yaml"

# ---------------------- Utility Functions ----------------------
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
        return yaml.load(f, Loader=yaml.SafeLoader)


def get_credentials(username: str) -> dict:
    config = load_config()
    return config.get("credentials", {}).get("usernames", {}).get(username, {})


def create_chat_id() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def fetch_summary(prompt: str, reply: str) -> str:
    summary_prompt = (
        f"User asked: {prompt}\n"
        f"AI answered: {reply}\n\n"
        "Now generate a **very short**, 1–2 sentence summary of this exchange, "
        "and **enclose it** in triple quotes like this:\n\"\"\"Your summary here.\"\"\""
    )
    llm_out = generate_response(summary_prompt, context="")
    match = re.search(r'"""(.*?)"""', llm_out, flags=re.S)
    return match.group(1).strip() if match else "(no summary found)"

# ---------------------- Sidebar: Chat Sessions ----------------------
def chat_sidebar(user_id: str):
    st.sidebar.title("💬 Chat Sessions")
    sessions = list_user_sessions(user_id)

    # Unique key per user for the New Chat button
    new_chat_key = f"new_chat_btn_{user_id}"
    if st.sidebar.button("➕ New Chat", key=new_chat_key):
        # remove empty latest if any
        if sessions:
            hist, _, _ = load_session(user_id, sessions[0])
            if not hist:
                delete_session(user_id, sessions[0])
        new_id = create_chat_id()
        st.session_state.chat_id = new_id
        st.session_state.chat_history = []
        st.session_state.summaries = {}
        st.session_state.turn_counter = 0
        save_session(user_id, new_id, [], {})
        st.rerun()

    groups = defaultdict(list)
    for sid in sessions:
        try:
            date = datetime.strptime(sid[:8], "%Y%m%d").strftime("%d-%b-%Y")
        except ValueError:
            date = "Unknown"
        groups[date].append(sid)

    for date in sorted(groups.keys(), reverse=True):
        st.sidebar.markdown(f"### {date}")
        for sid in sorted(groups[date], reverse=True):
            label = f"🗂️ Chat {sid[-6:]}"
            c1, c2 = st.sidebar.columns([0.85, 0.15])
            if c1.button(label, key=f"open_{sid}"):
                hist, sums, _ = load_session(user_id, sid)
                st.session_state.update({
                    'chat_id': sid,
                    'chat_history': hist,
                    'summaries': sums,
                    'turn_counter': len(sums)
                })
                st.rerun()
            if c2.button("🗑️", key=f"del_{sid}"):
                delete_session(user_id, sid)
                st.rerun()

# ---------------------- Chat Interface ----------------------
def init_session_state(user_id: str):
    if 'chat_history' not in st.session_state:
        sessions = list_user_sessions(user_id)
        if sessions:
            sid = sessions[0]
            hist, sums, _ = load_session(user_id, sid)
            st.session_state.chat_id = sid
            st.session_state.chat_history = hist
            st.session_state.summaries = sums
            st.session_state.turn_counter = len(sums)
        else:
            chat_sidebar(user_id)
            st.stop()


def build_context(username: str, personalized: bool) -> str:
    if personalized:
        all_sums = load_global_summaries(username) or {}
        summaries = all_sums.get(st.session_state.chat_id, {})
    else:
        summaries = st.session_state.get('summaries', {})

    creds = get_credentials(username)
    return (
        f"Username: {creds.get('name')} ({creds.get('age')}). "
        f"Previous summaries: {summaries}"
    )


def handle_message(user_id: str, prompt: str, personalized: bool):
    context = build_context(user_id, personalized)
    reply = generate_response(prompt, context)
    summary = fetch_summary(prompt, reply)

    st.session_state.turn_counter += 1
    st.session_state.summaries[st.session_state.turn_counter] = summary
    st.session_state.chat_history += [('User', prompt), ('AI', reply)]

    save_session(
        user_id,
        st.session_state.chat_id,
        st.session_state.chat_history,
        st.session_state.summaries
    )
    if personalized:
        save_global_summaries(
            user_id,
            st.session_state.chat_id,
            summary,
            st.session_state.turn_counter
        )
    st.session_state.user_input = ''


def render_chat(username: str):
    st.markdown("""
        <h1 style='text-align:center;'>🤖 Personalized AI Mentor 💬</h1>
    """, unsafe_allow_html=True)
    st.write("Ask me anything…")

    init_session_state(username)
    chat_sidebar(username)

    for sender, msg in st.session_state.chat_history:
        align = 'flex-end' if sender == 'User' else 'flex-start'
        bg = '#34b7f1' if sender == 'User' else '#dcf8c6'
        clr = 'white' if sender == 'User' else 'black'
        radius = '12px 12px 0 12px' if sender == 'User' else '12px 12px 12px 0'
        st.markdown(
            f"""
            <div style='display:flex; justify-content:{align}; margin:5px 0;'>
              <div style='background:{bg}; color:{clr}; padding:10px; border-radius:{radius}; max-width:70%'>
                {msg}
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    col_q, col_s = st.columns([4, 1])
    with col_s:
        personalized = st.selectbox(
            "Scope",
            ("Personalized", "Unpersonalized"),
            help="Use global summaries vs. current session only"
        ) == "Personalized"
    with col_q:
        def submit():
            text = st.session_state.user_input.strip()
            if not text:
                st.warning("Enter a message")
                return
            handle_message(username, text, personalized)
        st.text_input("Your question:", key="user_input", on_change=submit)
        if st.button("Send", key="send_btn"):
            submit()
