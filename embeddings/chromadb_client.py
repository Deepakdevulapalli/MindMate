import os
import uuid
import yaml
from pathlib import Path
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Paths
BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR.parent / "config.yaml"
PERSIST_DIR = BASE_DIR.parent / 'data' / 'chroma_db'
PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# Initialize ChromaDB client with persistence
client = chromadb.Client(
    Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=str(PERSIST_DIR)
    )
)

# Create or get collection
collection = client.get_or_create_collection(
    name="user_data",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
)


def load_config() -> dict:
    """
    Load the YAML config containing user credentials and metadata.
    """
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)


def store_user_info(user_id: str, content: str, source_type: str = "note", metadata: dict = None) -> str:
    """
    Store a chunk of user info in ChromaDB under the given user_id.

    Args:
        user_id: Unique identifier for the user (e.g., email).
        content: Text content to embed and store.
        source_type: Type of source (e.g., "profile", "chat", "prompt", "response").
        metadata: Additional metadata dict.

    Returns:
        The generated document ID.
    """
    if metadata is None:
        metadata = {}

    doc_id = str(uuid.uuid4())
    record_metadata = {
        "user_id": user_id,
        "source_type": source_type,
        "timestamp": datetime.utcnow().isoformat(),
        **metadata
    }

    collection.add(
        documents=[content],
        metadatas=[record_metadata],
        ids=[doc_id]
    )
    client.persist()
    return doc_id


def get_relevant_context(user_id: str, query: str, n_results: int = 3) -> str:
    """
    Retrieve the most relevant stored documents for a given user and query.

    Args:
        user_id: Unique identifier for the user.
        query: The query text to find similar documents.
        n_results: Number of top results to return.

    Returns:
        A concatenated string of the retrieved documents.
    """
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"user_id": user_id}
    )
    docs = results.get("documents", [[]])[0]
    return "\n".join(docs)


def get_user_profile_context(user_id: str) -> str:
    """
    Build a base context string from the user's profile data in config.yaml.

    Args:
        user_id: The user's email (key in credentials).

    Returns:
        A descriptive string of the user's profile.
    """
    config = load_config()
    user = config.get('credentials', {}).get('usernames', {}).get(user_id)
    if not user:
        return ""
    name = user.get('name', '')
    age = user.get('age', '')
    return f"{name} is a {age}-year-old user."


def build_context(user_id: str, query: str) -> str:
    """
    Combine the user's profile context with relevant stored memory for a given query.

    Args:
        user_id: Unique identifier (email).
        query: Current user prompt.

    Returns:
        A full context string for LLM generation.
    """
    profile_ctx = get_user_profile_context(user_id)
    memory_ctx = get_relevant_context(user_id, query)

    parts = []
    if profile_ctx:
        parts.append(profile_ctx)
    if memory_ctx:
        parts.append(memory_ctx)
    return "\n".join(parts)


def log_interaction(user_id: str, prompt: str, response: str) -> None:
    """
    Store both the user prompt and LLM response back into ChromaDB for future retrieval.

    Args:
        user_id: Unique identifier (email).
        prompt: The user input text.
        response: The LLM output text.
    """
    # store prompt and response separately
    store_user_info(user_id, prompt, source_type="prompt")
    store_user_info(user_id, response, source_type="response")
