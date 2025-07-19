# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Interactive Ads Generator for Mid/Hardcore Games - An AI-powered system that:
1. Analyzes open source mid/hardcore games (code + creatives)
2. Identifies engaging moments using AI
3. Generates playable 5-10 minute mini-games with same characters
4. Serves games via cloud/Android to drive app downloads

## Architecture

### Core Components
- **Game Analyzer**: Parses game code, assets, and identifies key mechanics
- **Engagement AI**: ML pipeline to find most compelling game moments
- **Mini-Game Generator**: Creates playable experiences using extracted assets
- **Deployment Engine**: Cloud/Android delivery system

### Technology Stack
- Game Analysis: Python (AST parsing, computer vision for assets)
- AI Pipeline: TensorFlow/PyTorch for engagement prediction
- Game Generation: Unity/Godot for cross-platform compatibility
- Backend: Node.js/Python FastAPI for cloud services
- Mobile: Kotlin/Java for Android deployment

### Data Flow
1. Source game → Code/Asset analysis → Feature extraction
2. Features → AI model → Engagement scoring
3. Top moments → Template generation → Mini-game creation
4. Mini-game → Cloud hosting → Android app integration

## Development Commands

### Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Game Analysis
```bash
# Analyze an open source game
python scripts/analyze_game.py tanks-of-freedom

# Identify engaging moments
python scripts/analyze_moments.py data/tanks-of-freedom_analysis.json
```

### Mini-Game Generation
```bash
# Test mini-game engine
python scripts/test_mini_game.py

# Run playable mini-game (requires display)
python scripts/run_mini_game.py
```

## Current AI Capabilities Demonstrated

### What the AI Successfully Accomplished ✅
- **Game Analysis**: Parsed 198 GDScript files, extracted 120 assets, detected Godot engine
- **Pattern Recognition**: Identified combat/strategy/resource patterns in code
- **Engagement Scoring**: Rated "Quick Skirmish" highest (0.855 feasibility score)
- **Asset Utilization**: Automatically extracted and categorized character sprites
- **Code Generation**: Created complete game engine (500+ lines) with AI opponent
- **Gameplay Adaptation**: Simplified 8-minute tactical combat for quick play

### Current AI Limits Reached ❌
- **Visual Asset Analysis**: Basic categorization only, no deep computer vision
- **Game Balance**: Requires human tuning for optimal difficulty progression
- **Procedural Content**: Cannot generate new levels or scenarios dynamically
- **Advanced AI**: Simple rule-based opponent, not ML-powered gameplay
- **Cross-Engine Translation**: Manual adaptation needed for different engines

## Test Results Summary
- **Source Game**: Tanks of Freedom (1k+ GitHub stars, active Godot project)
- **Generated Mini-Game**: Quick Skirmish (6x6 tactical combat, 5-8 min gameplay)
- **Technical Stack**: Python + Pygame with extracted assets and sounds
- **Deployment Ready**: Core engine functional, needs packaging for web/mobile

## Next Steps for Production
- Package for web deployment (Pygame → Pyodide/WebAssembly)
- Create Android APK (Pygame → Kivy or BeeWare)
- Add cloud analytics for engagement tracking
- Implement multiplayer via WebSocket backend