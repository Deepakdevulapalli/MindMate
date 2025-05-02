# # # chat_ui.py
# from llm.gorq_client import generate_response
# import re
# import streamlit as st
# from utils.session_storage import load_session, save_session
# from yaml.loader import SafeLoader
# import yaml
# from pathlib import Path

# CONFIG_PATH = "data/config.yaml"
# def load_config():
#     if not Path(CONFIG_PATH).exists():
#         with open(CONFIG_PATH, "w") as f:
#             yaml.dump({
#                 "credentials": {"usernames": {}},
#                 "cookie": {
#                     "name": "personalized_llm_cookie",
#                     "key": "some_secure_key",
#                     "expiry_days": 30,
#                 }
#             }, f)
#     with open(CONFIG_PATH) as f:
#         return yaml.load(f, Loader=SafeLoader)

# def get_credentials(username):
#     # Load the config
#     config = load_config()
    
#     # Look up the username in the 'usernames' section of the config
#     usernames = config.get("credentials", {}).get("usernames", {})
    
#     # Retrieve the credentials for the given username
#     user_credentials = usernames.get(username, None)
    
#     if user_credentials:
#         name = user_credentials.get("name", None)
#         age = user_credentials.get("age", None)
#         return name, age
#     else:
#         print(f"No credentials found for username: {username}")
#         return None, None



# def fetch_summary(prompt: str, reply: str) -> str:
#     """Ask the LLM for a tiny summary and extract it."""
#     summary_prompt = (
#         f"User asked: {prompt}\n"
#         f"AI answered: {reply}\n\n"
#         "Now generate a **very short**, 1–2 sentence summary of this exchange, "
#         "and **enclose it** in triple quotes like this:\n\"\"\"Your tiny summary here.\"\"\""
#     )
#     llm_out = generate_response(summary_prompt, context="")
#     match = re.search(r'\"\"\"(.*?)\"\"\"', llm_out, flags=re.S)
#     return match.group(1).strip() if match else "(no summary found)"

# def init_session_state(user_id: str):
#     if 'chat_input' not in st.session_state:
#         st.session_state.chat_input = ""

#     if 'chat_history' not in st.session_state or 'summaries' not in st.session_state:
#         chat_history, summaries = load_session(user_id)
#         st.session_state.chat_history = chat_history
#         st.session_state.summaries = summaries
#         st.session_state.turn_counter = len(summaries)


# # Build context for the AI
# def build_context(username: str) -> str:
#     """Construct the context prompt."""
#     name,age = get_credentials(username)
#     last = st.session_state.summaries
#     return f"Username is {name} and his age is {age}. Here is the list of previous converstation with llm and their output {last}"


# def handle_message(user_id: str, prompt: str):
#     context = build_context(user_id)
#     reply = generate_response(prompt, context)
#     summary = fetch_summary(prompt, reply)

#     st.session_state.turn_counter += 1
#     st.session_state.summaries[st.session_state.turn_counter] = summary
#     st.session_state.chat_history.append(('User', prompt))
#     st.session_state.chat_history.append(('AI', reply))

#     # Save after each new message
#     save_session(user_id, st.session_state.chat_history, st.session_state.summaries)

# # Main chat rendering function
# def render_chat(username: str):
#     """Render the Streamlit chat interface."""
#     st.title("Personalized AI Mentor")
#     st.write("Ask me anything…")

#     init_session_state(username)

#     # Display chat history
#     for sender, message in st.session_state.chat_history:
#         if sender == 'User':
#             st.markdown(
#                 f'<div style="text-align: left; background-color: #f0f0f0; border-radius: 10px; padding: 10px; margin-bottom: 5px;">{message}</div>',
#                 unsafe_allow_html=True
#             )
#         else:
#             st.markdown(
#                 f'<div style="text-align: right; background-color: #4CAF50; color: white; border-radius: 10px; padding: 10px; margin-bottom: 5px;">{message}</div>',
#                 unsafe_allow_html=True
#             )

#     # Callback to handle input submission
#     def on_submit():
#         prompt = st.session_state.chat_input
#         if prompt.strip():
#             handle_message(username, prompt)
#             st.session_state.chat_input = ""  # Clear input after processing
#         else:
#             st.warning("Please enter a message.")

#     # Text input with on_change callback
#     st.text_input("Your question:", key="chat_input", on_change=on_submit)

#     # Optional button for submission
#     if st.button("Get Response"):
#         on_submit()






# # chat_ui.py
from llm.gorq_client import generate_response
import re
import streamlit as st
from utils.session_storage import load_session, save_session
from yaml.loader import SafeLoader
import yaml
from pathlib import Path

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

def get_credentials(username):
    # Load the config
    config = load_config()
    
    # Look up the username in the 'usernames' section of the config
    usernames = config.get("credentials", {}).get("usernames", {})
    
    # Retrieve the credentials for the given username
    user_credentials = usernames.get(username, None)
    
    if user_credentials:
        name = user_credentials.get("name", None)
        age = user_credentials.get("age", None)
        return name, age
    else:
        print(f"No credentials found for username: {username}")
        return None, None



def fetch_summary(prompt: str, reply: str) -> str:
    """Ask the LLM for a tiny summary and extract it."""
    summary_prompt = (
        f"User asked: {prompt}\n"
        f"AI answered: {reply}\n\n"
        "Now generate a **very short**, 1–2 sentence summary of this exchange, "
        "and **enclose it** in triple quotes like this:\n\"\"\"Your tiny summary here.\"\"\""
    )
    llm_out = generate_response(summary_prompt, context="")
    match = re.search(r'\"\"\"(.*?)\"\"\"', llm_out, flags=re.S)
    return match.group(1).strip() if match else "(no summary found)"

def init_session_state(user_id: str):
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""

    if 'chat_history' not in st.session_state or 'summaries' not in st.session_state:
        chat_history, summaries = load_session(user_id)
        st.session_state.chat_history = chat_history
        st.session_state.summaries = summaries
        st.session_state.turn_counter = len(summaries)


# Build context for the AI
def build_context(username: str) -> str:
    """Construct the context prompt."""
    name,age = get_credentials(username)
    last = st.session_state.summaries
    return f"Username is {name} and his age is {age}. Here is the list of previous converstation with llm and their output {last}"


def handle_message(user_id: str, prompt: str):
    context = build_context(user_id)
    reply = generate_response(prompt, context)
    summary = fetch_summary(prompt, reply)

    st.session_state.turn_counter += 1
    st.session_state.summaries[st.session_state.turn_counter] = summary
    st.session_state.chat_history.append(('User', prompt))
    st.session_state.chat_history.append(('AI', reply))

    # Save after each new message
    save_session(user_id, st.session_state.chat_history, st.session_state.summaries)

# Main chat rendering function
def render_chat(username: str):
    """Render the Streamlit chat interface."""
    st.markdown(
        "<h1 style='text-align: center; color: #2c3e50; background-color: #f7f7f7; padding: 20px; border-radius: 12px;'>🤖 Personalized AI Mentor 💬</h1>",
        unsafe_allow_html=True
    )

    st.write("Ask me anything…")

    init_session_state(username)

    # Display chat history with WhatsApp-style message bubbles
    for sender, message in st.session_state.chat_history:
        if sender == 'User':
            st.markdown(
                f'''
                <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                    <div style="
                        background-color: #34b7f1;
                        color: white;
                        padding: 12px 16px;
                        border-radius: 12px 12px 0px 12px;
                        max-width: 75%;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        font-size: 15px;
                    ">
                        {message}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'''
                <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                    <div style="
                        background-color: #dcf8c6;
                        color: #000;
                        padding: 12px 16px;
                        border-radius: 12px 12px 12px 0px;
                        max-width: 75%;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                        font-size: 15px;
                    ">
                        {message}
                    </div>
                </div>
                ''',
                unsafe_allow_html=True
            )
            


    # Callback to handle input submission
    def on_submit():
        prompt = st.session_state.chat_input
        if prompt.strip():
            handle_message(username, prompt)
            st.session_state.chat_input = ""  # Clear input after processing
        else:
            st.warning("Please enter a message.")

    # Text input with on_change callback
    st.text_input("Your question:", key="chat_input", on_change=on_submit)

    # Optional button for submission
    if st.button("Get Response"):
        on_submit()


