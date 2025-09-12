#!/bin/bash
# MOSDAC Bot Runner Script

# Activate virtual environment
source .venv/bin/activate

# Set up environment variables
export GEMINI_API_KEY="AIzaSyA22BG94hYIO6y79U7nuZDd73Nbeu3CEeA"
export LLM_MODE="api"

# Run the bot
python mosdac_bot.py
