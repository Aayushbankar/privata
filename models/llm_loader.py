# privata/models/llm_loader.py

import os
import google.generativeai as genai
from config import Config
from typing import Any , List, Dict

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("Set GEMINI_API_KEY in your environment.")

genai.configure(api_key=API_KEY)

# Gemini 1.5 Flash (fast, chat-optimized)
model = genai.GenerativeModel("models/gemini-2.5-flash")

def ensure_ollama_running():
    pass  # No local check required for Gemini

def run_llm(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"[Gemini API Error] {e}")
