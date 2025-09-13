#!/usr/bin/env python3
"""
MOSDAC AI Help Bot - Main Entry Point
=====================================

This is the main entry point for the MOSDAC AI Help Bot.
It imports and runs the core bot functionality.
"""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the bot
from core.mosdac_bot import main

if __name__ == "__main__":
    asyncio.run(main())