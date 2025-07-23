#!/bin/bash
"""
Manual Android APK Build Script
Downloads correct Android SDK and builds SuperTuxKart Mobile APK
"""

echo "🏎️  Manual Android APK Build for SuperTuxKart Mobile"
echo "=================================================="

# Set up environment
export JAVA_HOME="/opt/homebrew/opt/openjdk@11"
export PATH="$JAVA_HOME/bin:$PATH"

# Create build directory
mkdir -p android-build
cd android-build

echo "📥 Downloading Android Command Line Tools..."
curl -O https://dl.google.com/android/repository/commandlinetools-mac-8512546_latest.zip
unzip -q commandlinetools-mac-8512546_latest.zip

# Set up Android SDK
export ANDROID_HOME="$(pwd)/android-sdk"
mkdir -p $ANDROID_HOME/cmdline-tools
mv cmdline-tools $ANDROID_HOME/cmdline-tools/latest

export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

echo "📱 Setting up Android SDK..."
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-30" "build-tools;30.0.3"

echo "📦 Downloading Android NDK..."
curl -O https://dl.google.com/android/repository/android-ndk-r25b-darwin.zip
unzip -q android-ndk-r25b-darwin.zip
export ANDROID_NDK_HOME="$(pwd)/android-ndk-r25b"

# Go back to project root
cd ..

echo "🔨 Building APK with correct SDK..."
source venv_android/bin/activate

# Update buildozer.spec with correct SDK paths
cat > buildozer.spec << 'EOF'
[app]
title = SuperTuxKart Mobile
package.name = supertuxkartmobile
package.domain = org.interactiveads
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2

EOF

# Set buildozer environment
export ANDROIDAPI="30"
export ANDROIDMINAPI="21"
export ANDROIDNDK="$(pwd)/android-build/android-ndk-r25b"
export ANDROIDSDKROOT="$(pwd)/android-build/android-sdk"

echo "🚀 Starting APK build..."
buildozer android debug

if [ $? -eq 0 ]; then
    echo "✅ APK Build Successful!"
    echo "📱 APK Location: bin/supertuxkartmobile-1.0-arm64-v8a-debug.apk"
    ls -la bin/*.apk
else
    echo "❌ APK Build Failed"
    echo "Check the output above for errors"
fi