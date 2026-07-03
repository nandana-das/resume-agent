import os
from dotenv import load_dotenv
load_dotenv()

try:
    import streamlit as st
except Exception:
    st = None

# ✏️ Change this to switch LLMs everywhere
# Options: "groq" | "gemini" | "claude" | "ollama"
DEFAULT_PROVIDER = "groq"


def _get_config_value(key: str, default=None):
    if st is not None:
        try:
            if key in st.secrets:
                value = st.secrets.get(key)
                if value:
                    return value
        except Exception:
            pass

    value = os.getenv(key)
    if value:
        return value

    return default

def get_llm(provider=DEFAULT_PROVIDER):
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=_get_config_value("GROQ_API_KEY"),
            temperature=0.3
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # ← updated model name
            google_api_key=_get_config_value("GEMINI_API_KEY"),
            temperature=0.3
        )
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model="llama3.1", temperature=0.3)