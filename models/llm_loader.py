# privata/models/llm_loader.py

import os
import subprocess
import requests
from typing import Any, List, Dict, Optional
from config import Config

# LLM Configuration
LLM_MODE = os.getenv("LLM_MODE", "api")  # "api" or "ollama"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# Initialize based on mode
if LLM_MODE == "api":
    if not GEMINI_API_KEY:
        raise EnvironmentError("Set GEMINI_API_KEY in your environment for API mode.")
    
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    
elif LLM_MODE == "ollama":
    # Check if Ollama is available
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            raise ConnectionError("Ollama server not responding")
    except Exception as e:
        raise EnvironmentError(f"Ollama not available: {e}. Set LLM_MODE=api to use Gemini API instead.")

def ensure_ollama_running():
    """Check if Ollama is running and pull model if needed"""
    if LLM_MODE != "ollama":
        return True
        
    try:
        # Check if server is running
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            return False
            
        # Check if model exists
        models = response.json().get("models", [])
        model_names = [model["name"] for model in models]
        
        if OLLAMA_MODEL not in model_names:
            print(f"🔄 Pulling Ollama model: {OLLAMA_MODEL}")
            subprocess.run(["ollama", "pull", OLLAMA_MODEL], check=True)
            
        return True
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        return False

def run_llm(prompt: str) -> str:
    """Run LLM with current mode (API or Ollama)"""
    try:
        if LLM_MODE == "api":
            return _run_gemini_api(prompt)
        elif LLM_MODE == "ollama":
            return _run_ollama(prompt)
        else:
            raise ValueError(f"Unknown LLM_MODE: {LLM_MODE}")
    except Exception as e:
        raise RuntimeError(f"[LLM Error] {e}")

def _run_gemini_api(prompt: str) -> str:
    """Run Gemini API"""
    response = model.generate_content(prompt)
    return response.text.strip()

def _run_ollama(prompt: str) -> str:
    """Run Ollama locally"""
    if not ensure_ollama_running():
        raise RuntimeError("Ollama is not running or model not available")
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        timeout=120  # Longer timeout for local inference
    )
    
    if response.status_code != 200:
        raise RuntimeError(f"Ollama API error: {response.status_code}")
    
    result = response.json()
    return result.get("response", "").strip()

def get_llm_info() -> Dict[str, Any]:
    """Get current LLM configuration info"""
    return {
        "mode": LLM_MODE,
        "api_key_set": bool(GEMINI_API_KEY) if LLM_MODE == "api" else None,
        "ollama_model": OLLAMA_MODEL if LLM_MODE == "ollama" else None,
        "ollama_url": OLLAMA_URL if LLM_MODE == "ollama" else None,
        "available": _check_availability()
    }

def _check_availability() -> bool:
    """Check if current LLM mode is available"""
    try:
        if LLM_MODE == "api":
            return bool(GEMINI_API_KEY)
        elif LLM_MODE == "ollama":
            return ensure_ollama_running()
        return False
    except Exception:
        return False
