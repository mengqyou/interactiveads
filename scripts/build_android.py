#!/usr/bin/env python3
"""
Android Build Script

Builds the Quick Skirmish mini-game as an Android APK
"""
import subprocess
import sys
import os
from pathlib import Path


def install_android_deps():
    """Install Android build dependencies"""
    print("Installing Android build dependencies...")
    
    # Install buildozer and kivy
    deps = [
        "buildozer>=1.5.0",
        "kivy>=2.2.0", 
        "kivymd>=1.1.1",
        "python-for-android>=0.13.0"
    ]
    
    for dep in deps:
        print(f"Installing {dep}...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                               capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to install {dep}: {result.stderr}")
            return False
    
    return True


def setup_android_sdk():
    """Setup Android SDK requirements"""
    print("\nSetting up Android SDK...")
    print("You need to have the following installed:")
    print("1. Java 8 or 11 JDK")
    print("2. Android SDK (via Android Studio or command line tools)")
    print("3. Android NDK")
    print("4. Apache Ant")
    print("\nOn macOS, you can install these with:")
    print("  brew install openjdk@11 android-sdk android-ndk apache-ant")
    print("\nMake sure these environment variables are set:")
    print("  export ANDROID_HOME=/usr/local/share/android-sdk")
    print("  export ANDROID_NDK_HOME=/usr/local/share/android-ndk")
    print("  export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools")
    
    # Check if Android SDK is available
    android_home = os.environ.get('ANDROID_HOME')
    if not android_home:
        print("\n⚠️  ANDROID_HOME not set. Please install Android SDK first.")
        return False
    
    return True


def build_apk():
    """Build the Android APK"""
    print("\nBuilding Android APK...")
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # Initialize buildozer (first time only)
        print("Initializing buildozer...")
        result = subprocess.run(["buildozer", "init"], capture_output=True, text=True)
        if result.returncode != 0 and "already exists" not in result.stderr:
            print(f"Buildozer init failed: {result.stderr}")
        
        # Build debug APK
        print("Building debug APK (this may take 20-30 minutes the first time)...")
        result = subprocess.run(["buildozer", "android", "debug"], 
                               capture_output=False, text=True)
        
        if result.returncode == 0:
            apk_path = project_root / "bin" / "quickskirmish-1.0-arm64-v8a-debug.apk"
            if apk_path.exists():
                print(f"\n✅ APK built successfully!")
                print(f"Location: {apk_path}")
                print(f"Size: {apk_path.stat().st_size / 1024 / 1024:.1f} MB")
                return True
            else:
                print("APK built but not found at expected location")
                # List files in bin directory
                bin_dir = project_root / "bin"
                if bin_dir.exists():
                    print("Files in bin directory:")
                    for file in bin_dir.iterdir():
                        print(f"  {file.name}")
        else:
            print(f"Build failed with return code {result.returncode}")
            return False
            
    except FileNotFoundError:
        print("❌ Buildozer not found. Please install with: pip install buildozer")
        return False
    except Exception as e:
        print(f"❌ Build failed: {e}")
        return False


def create_install_instructions():
    """Create installation instructions"""
    instructions = """
# Quick Skirmish - Installation Instructions

## APK Installation

1. **Enable Unknown Sources** on your Android device:
   - Go to Settings > Security
   - Enable "Unknown sources" or "Install unknown apps"

2. **Transfer APK to your phone**:
   - Copy `quickskirmish-1.0-arm64-v8a-debug.apk` to your phone
   - Via USB, email, cloud storage, or adb

3. **Install the APK**:
   - Tap the APK file on your phone
   - Follow the installation prompts

## ADB Installation (if connected via USB)

```bash
# Install via ADB
adb install bin/quickskirmish-1.0-arm64-v8a-debug.apk

# Launch the app
adb shell am start -n com.interactiveads.quickskirmish/org.kivy.android.PythonActivity
```

## Game Controls

- **Tap unit**: Select unit
- **Tap green area**: Move unit
- **Tap red area**: Attack enemy
- **End Turn button**: End your turn
- **Restart button**: Start new game

## Comparison with Original

To compare with the original Tanks of Freedom:

1. **Download original**: 
   - F-Droid: https://f-droid.org/en/packages/p1x.in.tanks/
   - Google Play: Search "Tanks of Freedom"

2. **Compare features**:
   - Original: Full campaign, map editor, multiplayer
   - Mini-game: Quick 5-8 minute tactical battles
   - Both: Same visual style and unit types

3. **Test engagement**:
   - Time how long you play each version
   - Which one makes you want to download the full game?
"""
    
    with open("INSTALL_INSTRUCTIONS.md", "w") as f:
        f.write(instructions)
    
    print("Installation instructions saved to INSTALL_INSTRUCTIONS.md")


def main():
    """Main build process"""
    print("Quick Skirmish - Android Build System")
    print("=" * 40)
    
    # Check platform
    if sys.platform == "win32":
        print("⚠️  Windows detected. Consider using WSL for Android builds.")
    
    # Install dependencies
    if not install_android_deps():
        print("❌ Failed to install dependencies")
        return False
    
    # Setup Android SDK
    if not setup_android_sdk():
        print("❌ Android SDK setup required")
        return False
    
    # Build APK
    if build_apk():
        create_install_instructions()
        print("\n🎉 Build completed successfully!")
        print("Check INSTALL_INSTRUCTIONS.md for installation steps")
        return True
    else:
        print("❌ Build failed")
        return False


if __name__ == "__main__":
    main()