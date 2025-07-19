#!/usr/bin/env python3
"""
Main entry point for the Quick Skirmish mobile app
"""
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from mini_game_generator.kivy_game import QuickSkirmishApp

if __name__ == "__main__":
    QuickSkirmishApp().run()