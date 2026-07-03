import os
import sys

print(f"Python: {sys.version_info.major}.{sys.version_info.minor}")

packages = ["streamlit", "langchain", "langgraph",
            "pdfplumber", "docx", "httpx", "bs4", "dotenv", "groq"]

for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ❌ {pkg}")

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if api_key:
    from groq import Groq

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "Say: Setup successful!"}],
    )
    print("✅ Groq API:", response.choices[0].message.content.strip())