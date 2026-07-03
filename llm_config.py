import os
from dotenv import load_dotenv
load_dotenv()

# ✏️ Change this to switch LLMs everywhere
# Options: "groq" | "gemini" | "claude" | "ollama"
DEFAULT_PROVIDER = "groq"

def get_llm(provider=DEFAULT_PROVIDER):
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3
        )
    elif provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",  # ← updated model name
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3
        )
    elif provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model="llama3.1", temperature=0.3)