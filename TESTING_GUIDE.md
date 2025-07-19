# Testing Guide: Original vs Generated Game

## Quick Setup (5 minutes)

### 1. Test the Mini-Game Locally First
```bash
# Install mobile dependencies
pip install kivy kivymd buildozer

# Test the Kivy version on desktop
python main.py
```

### 2. Build Android APK
```bash
# Install Android build tools (one-time setup)
brew install openjdk@11 android-sdk android-ndk apache-ant

# Set environment variables
export ANDROID_HOME=/usr/local/share/android-sdk
export ANDROID_NDK_HOME=/usr/local/share/android-ndk

# Build APK (takes 20-30 min first time)
python scripts/build_android.py
```

### 3. Install on Phone
- APK will be in `bin/quickskirmish-1.0-arm64-v8a-debug.apk`
- Transfer to phone and install (enable "Unknown sources" first)

## Original Game Installation

### Option A: F-Droid (Recommended)
1. Install F-Droid app store: https://f-droid.org/
2. Search for "Tanks of Freedom"
3. Install the full game

### Option B: Google Play Store
1. Search "Tanks of Freedom" 
2. Install official version

### Option C: Build from Source
```bash
# Clone original game
git clone https://github.com/w84death/Tanks-of-Freedom.git

# Import into Godot Engine and export for Android
# (Requires Godot 3.x and Android export templates)
```

## Comparison Testing Framework

### Engagement Metrics to Track

| Metric | Original Game | Mini-Game | Notes |
|--------|---------------|-----------|-------|
| **First Session Time** | ___ minutes | ___ minutes | How long until you stop playing? |
| **Learning Curve** | Easy/Medium/Hard | Easy/Medium/Hard | How quickly did you understand? |
| **Urge to Continue** | 1-10 scale | 1-10 scale | Want to keep playing? |
| **Visual Appeal** | 1-10 scale | 1-10 scale | Art style and polish |
| **Strategic Depth** | 1-10 scale | 1-10 scale | Tactical decision complexity |
| **Mobile UX** | 1-10 scale | 1-10 scale | Touch controls and UI |

### A/B Testing Scenarios

#### Scenario 1: Cold Start
- Install both games
- Play mini-game first (5-10 minutes)
- Then play original game
- **Question**: Does mini-game make you more interested in the original?

#### Scenario 2: Discovery
- Play original game first (10-15 minutes)
- Then play mini-game
- **Question**: Does mini-game capture the essence of the original?

#### Scenario 3: Time-Limited
- Give yourself only 10 minutes total
- Choose which game to play
- **Question**: Which provides better value in limited time?

### Key Differences to Evaluate

| Feature | Original | Mini-Game |
|---------|----------|-----------|
| **Campaign** | 15+ missions | Single skirmish |
| **Map Size** | Various (8x8 to 20x20) | Fixed 6x6 |
| **Unit Types** | 3 types + buildings | 3 types only |
| **Game Length** | 15-45 minutes/mission | 5-8 minutes |
| **Complexity** | Resource management | Pure combat |
| **Tutorial** | Built-in training | Learn by playing |

## Expected AI Limitations in Testing

### What the Mini-Game Does Well ✅
- **Quick engagement**: Should hook you in 30 seconds
- **Core mechanics**: Movement, attack, turn-based strategy preserved
- **Visual consistency**: Uses actual game sprites and sounds
- **Mobile optimization**: Touch-friendly interface

### What's Missing/Simplified ❌
- **Strategic depth**: No resource management or base building
- **Progression**: No campaign or unlocks
- **Polish**: Basic UI compared to full game
- **Content variety**: Single map vs. dozens in original

## Success Criteria for AI-Generated Interactive Ads

### Primary Goals
1. **Engagement**: Mini-game keeps attention for full 5-8 minutes
2. **Conversion Intent**: Makes you want to try the full game
3. **Core Experience**: Captures the tactical fun of the original

### Secondary Goals
1. **Technical**: Runs smoothly on Android
2. **UX**: Intuitive touch controls
3. **Performance**: Loads quickly, no crashes

## Testing Instructions

### Phase 1: Desktop Testing
```bash
# Test both versions side by side
python scripts/run_mini_game.py     # Pygame version
python main.py                      # Kivy mobile version
```

### Phase 2: Mobile Testing
1. Install both APKs on your Android device
2. Play mini-game for 5-10 minutes
3. Play original for 10-15 minutes
4. Fill out comparison metrics above

### Phase 3: Share Testing
- Send APK to friends/family
- Ask them to rate engagement (1-10)
- Track: Did they download the original game after?

## Data Collection

Create a simple feedback form:

```
Mini-Game Feedback:
- How long did you play? ___
- Would you download the full game? Yes/No
- Most engaging aspect: ___
- Biggest limitation: ___
- Overall rating (1-10): ___
```

This testing framework will help you evaluate whether AI can successfully create engaging interactive ads that drive interest in the original games!