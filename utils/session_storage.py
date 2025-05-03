import json
import os

BASE_DIR = "data/chat_sessions"
ALL_SUMMARIES_FILENAME = "all_summaries.json"


def get_session_path(user_id: str, chat_id: str) -> str:
    """
    Path for a specific chat session JSON file.
    """
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, f"{chat_id}.json")


def get_all_summaries_path(user_id: str) -> str:
    """
    Path for the user's global summaries JSON file.
    """
    user_dir = os.path.join(BASE_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, ALL_SUMMARIES_FILENAME)


def load_session(user_id: str, chat_id: str):
    """
    Load a single session's history & summaries.
    Returns (chat_history, summaries, created_date).
    """
    path = get_session_path(user_id, chat_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
        created = data.get('created', chat_id[:8])
        return data.get('chat_history', []), data.get('summaries', {}), created
    return [], {}, chat_id[:8]


def save_session(user_id: str, chat_id: str, chat_history, summaries):
    """
    Save a single session's history & summaries.
    """
    path = get_session_path(user_id, chat_id)
    data = {
        'created': chat_id[:8],
        'chat_history': chat_history,
        'summaries': summaries,
    }
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_global_summaries(user_id: str):
    """
    Load the user's global summaries file, returning a dict mapping chat_id to its summaries dict.
    If none exists, returns {}.
    """
    path = get_all_summaries_path(user_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
        # extract only the summaries per chat
        return {chat_id: content.get('summaries', {}) for chat_id, content in data.items()}
    return {}


def save_global_summaries(user_id: str, chat_id: str, summary: str, turn_num: int):
    """
    Append a single turn's summary to the global summaries file.
    """
    path = get_all_summaries_path(user_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            all_data = json.load(f)
    else:
        all_data = {}

    if chat_id not in all_data:
        all_data[chat_id] = {
            'created': chat_id[:8],
            'summaries': {}
        }
    all_data[chat_id]['summaries'][str(turn_num)] = summary

    with open(path, 'w') as f:
        json.dump(all_data, f, indent=2)


def delete_session(user_id: str, chat_id: str):
    """
    Delete a session file. Does not touch global summaries.
    """
    path = get_session_path(user_id, chat_id)
    if os.path.exists(path):
        os.remove(path)


def list_user_sessions(user_id: str):
    """
    Return all chat_ids (excluding the global summary file), sorted desc.
    """
    user_dir = os.path.join(BASE_DIR, user_id)
    if not os.path.exists(user_dir):
        return []
    sessions = [
        fname[:-5] for fname in os.listdir(user_dir)
        if fname.endswith('.json') and fname != ALL_SUMMARIES_FILENAME
    ]
    return sorted(sessions, reverse=True)