#!/bin/bash
"""
SuperTuxKart Mobile Android Build Script

This script builds the SuperTuxKart mini-game as an Android APK
using Buildozer and Python-for-Android (p4a).
"""

echo "🏎️  Building SuperTuxKart Mobile APK..."
echo "========================================="

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "❌ Buildozer not found. Installing..."
    pip install buildozer
fi

# Check if Cython is installed (required for Kivy)
if ! python -c "import Cython" &> /dev/null; then
    echo "📦 Installing Cython..."
    pip install Cython
fi

# Check if Kivy is installed
if ! python -c "import kivy" &> /dev/null; then
    echo "📦 Installing Kivy..."
    pip install kivy kivymd
fi

# Create necessary directories
mkdir -p .buildozer
mkdir -p bin

# Copy main file
cp supertuxkart_mobile.py main.py

echo "🔧 Initializing Buildozer..."
buildozer init || echo "Buildozer already initialized"

# Copy our custom buildozer spec
cp buildozer_config.spec buildozer.spec

echo "📱 Building Android Debug APK..."
echo "This may take 10-30 minutes on first build..."

# Build the APK
buildozer android debug

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📱 APK created at: bin/supertuxkartmobile-1.0-arm64-v8a-debug.apk"
    echo ""
    echo "📲 To install on your device:"
    echo "   adb install bin/supertuxkartmobile-1.0-arm64-v8a-debug.apk"
    echo ""
    echo "🎮 Or transfer the APK to your phone and install manually"
    echo "   (Enable 'Install from unknown sources' in Android settings)"
else
    echo "❌ Build failed. Check the output above for errors."
    echo ""
    echo "Common solutions:"
    echo "1. Make sure Android SDK/NDK are properly installed"
    echo "2. Check Java version (OpenJDK 11 recommended)"
    echo "3. Ensure you have enough disk space (>10GB)"
    echo "4. Try: buildozer android clean"
fi

echo ""
echo "🏁 Build process complete!"