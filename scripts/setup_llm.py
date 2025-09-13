#!/usr/bin/env python3
"""
LLM Setup Helper for MOSDAC Bot
===============================

This script helps you configure the LLM for the MOSDAC AI Help Bot.
You can choose between API mode (Gemini) or offline mode (Ollama).
"""

import os
import subprocess
import sys
from pathlib import Path

def check_gemini_api():
    """Check if Gemini API key is available"""
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("✅ GEMINI_API_KEY is set")
        return True
    else:
        print("❌ GEMINI_API_KEY is not set")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        # Check if ollama command exists
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            
            # Check if server is running
            import requests
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
                if response.status_code == 200:
                    print("✅ Ollama server is running")
                    return True
                else:
                    print("❌ Ollama server is not responding")
                    return False
            except Exception as e:
                print(f"❌ Ollama server is not running: {e}")
                return False
        else:
            print("❌ Ollama is not installed")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False

def setup_api_mode():
    """Setup API mode with Gemini"""
    print("\n🔧 Setting up API mode (Gemini)...")
    
    if check_gemini_api():
        print("✅ API mode is ready!")
        print("   To use: export LLM_MODE=api")
        return True
    else:
        print("\n📝 To setup API mode:")
        print("1. Get a Gemini API key from: https://makersuite.google.com/app/apikey")
        print("2. Set the environment variable:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        print("   export LLM_MODE=api")
        return False

def setup_ollama_mode():
    """Setup Ollama mode"""
    print("\n🔧 Setting up Ollama mode...")
    
    if check_ollama():
        print("✅ Ollama mode is ready!")
        print("   To use: export LLM_MODE=ollama")
        return True
    else:
        print("\n📝 To setup Ollama mode:")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Start Ollama server: ollama serve")
        print("3. Pull a model: ollama pull llama3.2:latest")
        print("4. Set environment variable: export LLM_MODE=ollama")
        return False

def main():
    print("🤖 MOSDAC Bot LLM Setup Helper")
    print("=" * 40)
    
    print("\nCurrent Status:")
    print(f"LLM_MODE: {os.getenv('LLM_MODE', 'api (default)')}")
    
    # Check both modes
    api_ready = check_gemini_api()
    ollama_ready = check_ollama()
    
    print(f"\nAvailable Options:")
    print(f"1. API Mode (Gemini): {'✅ Ready' if api_ready else '❌ Not Ready'}")
    print(f"2. Ollama Mode (Offline): {'✅ Ready' if ollama_ready else '❌ Not Ready'}")
    
    if not api_ready and not ollama_ready:
        print("\n❌ Neither mode is ready. Please setup at least one option.")
        return
    
    print(f"\nRecommended:")
    if api_ready:
        print("✅ Use API mode (faster, no local setup required)")
        print("   export LLM_MODE=api")
    elif ollama_ready:
        print("✅ Use Ollama mode (offline, private)")
        print("   export LLM_MODE=ollama")
    
    print(f"\nTo test your setup:")
    print("   python -c \"from models.llm_loader import get_llm_info; print(get_llm_info())\"")

if __name__ == "__main__":
    main()
