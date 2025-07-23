#!/usr/bin/env python3
"""
SuperTuxKart Mobile: Kart Combat Arena
Main entry point for Android APK
"""

# Import the mobile game
from supertuxkart_mobile import SuperTuxKartMobileApp

if __name__ == '__main__':
    app = SuperTuxKartMobileApp()
    app.run()