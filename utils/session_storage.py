import json
import os



def get_session_path(user_id: str) -> str:
    DATA_DIR = f"data/chat_sessions/{user_id}"
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{user_id}_chat.json")

def load_session(user_id: str):
    """Load previous chat history and summaries for a user."""
    path = get_session_path(user_id)
    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
            return data.get("chat_history", []), data.get("summaries", {})
    return [], {}

def save_session(user_id: str, chat_history, summaries):
    """Save current session data to file."""
    path = get_session_path(user_id)
    data = {
        "chat_history": chat_history,
        "summaries": summaries,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
