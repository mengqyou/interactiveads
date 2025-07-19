#!/usr/bin/env python3
"""
Test Kivy Version on Desktop

Quick test of the mobile-optimized version before building APK
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from mini_game_generator.kivy_game import QuickSkirmishApp
    
    print("Testing Kivy version of Quick Skirmish...")
    print("This is the same version that will run on Android")
    print()
    print("Controls:")
    print("- Click/tap unit to select")
    print("- Click/tap green areas to move")
    print("- Click/tap red areas to attack")
    print("- Use End Turn button when done")
    print()
    
    # Run the app
    QuickSkirmishApp().run()
    
except ImportError as e:
    print(f"Error importing Kivy: {e}")
    print("Please install Kivy first: pip install kivy kivymd")
except Exception as e:
    print(f"Error running app: {e}")

if __name__ == "__main__":
    pass