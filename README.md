# 🏎️ SuperTuxKart Mobile - Interactive Ad Mini-Game

A mobile-optimized mini-game based on the 129MB SuperTuxKart racing game, designed for interactive advertising and Android deployment via GitHub Actions.

## 🎮 Project Overview

This project demonstrates the current capabilities and limitations of AI in game analysis and generation. It successfully:

- **Analyzes** open source games (code + assets)
- **Identifies** engaging gameplay moments using AI
- **Generates** playable mini-games with extracted assets
- **Deploys** as Android APKs for real-world testing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Android SDK (for APK building)
- Git

### Installation
```bash
# Clone the repository
git clone https://github.com/mengqyou/interactiveads.git
cd interactiveads

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Test the System
```bash
# 1. Analyze a game
python scripts/analyze_game.py tanks-of-freedom

# 2. Find engaging moments
python scripts/analyze_moments.py data/tanks-of-freedom_analysis.json

# 3. Test mini-game (desktop)
python scripts/test_mini_game.py

# 4. Run mobile version (desktop preview)
python main.py
```

### Build Android APK
```bash
# Install Android build tools
python scripts/build_android.py
```

## 🎮 How to Play the Generated Game

### Quick Start
1. **Run the game**: `python main.py` (mobile version) or `python scripts/run_mini_game.py` (desktop)
2. **Select units**: Click/tap your blue units to select them
3. **Move**: Click/tap green highlighted areas to move
4. **Attack**: Click/tap red highlighted areas to attack enemies
5. **End turn**: Use "End Turn" button when finished

### Game Objective
- **Win by**: Eliminating all red enemy units OR having more units after 10 turns
- **Your forces**: 3 blue units (1 tank, 2 soldiers)
- **Enemy forces**: 3 red AI units (mirrors your setup)

### Strategy Tips
- **Focus fire**: Attack same enemy with multiple units
- **Positioning**: Control the center of the 6x6 battlefield
- **One action per turn**: Each unit can either move OR attack (not both)

*For complete gameplay guide, see [DESIGN_DOCUMENT.md - How to Play](DESIGN_DOCUMENT.md#how-to-play-quick-skirmish)*

## 📊 Results

### Successful Analysis: Tanks of Freedom
- **561 files** analyzed in 12 seconds
- **120 assets** extracted and categorized
- **5 engaging moments** identified
- **Quick Skirmish** rated highest (0.855 score)

### Generated Mini-Game: Quick Skirmish
- **6x6 tactical combat** with original game assets
- **5-8 minute** gameplay optimized for ads
- **Android APK** ready for installation
- **Real-time AI opponent** with strategic behavior

## 🏗️ Architecture

```
src/
├── game_analyzer/      # Repository analysis and asset extraction
├── engagement_ai/      # Pattern recognition and moment scoring
├── mini_game_generator/ # Game engine and mobile optimization
└── deployment/        # Cross-platform deployment tools

scripts/
├── analyze_game.py     # Analyze any GitHub game repository
├── analyze_moments.py  # AI engagement moment detection
├── test_mini_game.py   # Test generated games
├── build_android.py    # Build Android APKs
└── run_mini_game.py    # Run playable games
```

## 🤖 AI Capabilities Demonstrated

### ✅ What AI Does Well
- **Pattern Recognition**: Identifies game mechanics in code
- **Asset Extraction**: Automatically categorizes sprites/sounds
- **Code Generation**: Creates functional game engines
- **Cross-Platform**: Adapts for mobile deployment

### ❌ Current AI Limitations
- **Visual Analysis**: Basic categorization only
- **Game Balance**: Requires human tuning
- **Creative Content**: Cannot generate new assets
- **Player Psychology**: Limited engagement prediction

## 📱 Mobile Testing

### Install Original Game
- **F-Droid**: Search "Tanks of Freedom"
- **Google Play**: Search "Tanks of Freedom"

### Install Generated Mini-Game
1. Build APK: `python scripts/build_android.py`
2. Transfer `bin/quickskirmish-*.apk` to phone
3. Enable "Unknown sources" in Android settings
4. Install and compare!

## 📖 Documentation

- **[Design Document](DESIGN_DOCUMENT.md)** - Complete technical documentation
- **[Testing Guide](TESTING_GUIDE.md)** - Comparison testing framework
- **[AI Process Flow](AI_PROCESS_FLOWCHART.md)** - Visual AI workflow
- **[CLAUDE.md](CLAUDE.md)** - Development guidance

## 🔬 Testing Framework

### Engagement Metrics
- **Play Time**: How long until you stop playing?
- **Learning Curve**: How quickly did you understand?
- **Conversion Intent**: Want to try the full game?

### Success Criteria
1. Mini-game engages for full 5-8 minutes
2. Captures essence of original tactical gameplay
3. Creates desire to download full game

## 🛠️ Supported Games

Currently tested with:
- **Tanks of Freedom** (Godot strategy game) ✅
- **AnyRPG** (Unity RPG engine) 🔄
- **Godot Open RPG** (Turn-based RPG demo) 🔄
- **Hypersomnia** (C++ arena shooter) 🔄

## 🎯 Use Cases

### For Game Developers
- **Prototype Testing**: Quickly test game concepts
- **Marketing Tools**: Create interactive ads from existing games
- **Player Research**: A/B test different gameplay styles

### For Researchers
- **AI Limitations**: Understand current AI capabilities
- **Game Analysis**: Automated analysis of game repositories
- **Interactive Media**: Study AI-generated interactive content

## 🚧 Future Improvements

### Short-term (3-6 months)
- **Deep Learning**: CNN-based visual asset analysis
- **Multi-Engine**: Unity and Unreal Engine support
- **Web Deployment**: WebAssembly for browser games

### Long-term (1-2 years)
- **Procedural Content**: AI-generated levels and scenarios
- **Advanced AI**: Machine learning opponents
- **Commercial Platform**: Full production deployment system

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 🙏 Acknowledgments

- **Tanks of Freedom** - Original game by P1X team
- **Godot Engine** - Open source game engine
- **Kivy Project** - Cross-platform Python framework
- **Claude AI** - AI assistance in development

## 📞 Contact

**Mengqi You** - [@mengqyou](https://github.com/mengqyou)

Project Link: [https://github.com/mengqyou/interactiveads](https://github.com/mengqyou/interactiveads)

---

*This project demonstrates current AI capabilities in game analysis and generation while clearly documenting the limitations that require future advancement.*