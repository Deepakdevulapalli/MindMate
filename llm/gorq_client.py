import os
import requests
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

def generate_response(prompt, context):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    # Construct the system-level instruction
    system_message = {
        "role": "system",
        "content": (
            "You are a personalized assistant for the user. "
            "Use the user's past experience below to tailor your responses in a helpful and context-aware way. "
            "Past user experience:\n"
            f"{context}\n"
            "Now respond to the following user query accordingly."
        )
    }

    user_message = {
        "role": "user",
        "content": prompt
    }

    payload = {
        "model": MODEL,
        "messages": [system_message, user_message]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"
