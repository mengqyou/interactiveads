#!/usr/bin/env python3
"""
Mini-Game Runner

Runs the generated Quick Skirmish mini-game
"""
import sys
import pygame
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from mini_game_generator.game_engine import QuickSkirmishEngine
from mini_game_generator.asset_manager import AssetManager
from mini_game_generator.ui_renderer import UIRenderer


def main():
    print("Starting Quick Skirmish Mini-Game...")
    print("Based on Tanks of Freedom")
    print()
    print("Controls:")
    print("- Left click: Select unit / Move / Attack")
    print("- Right click: Cancel selection")
    print("- R: Restart game (when game over)")
    print("- ESC: Quit")
    print()
    
    # Initialize pygame
    pygame.init()
    clock = pygame.time.Clock()
    
    # Get source game path
    source_game_path = Path("data/repositories/tanks-of-freedom")
    
    if not source_game_path.exists():
        print(f"Source game not found at {source_game_path}")
        print("Please run: python scripts/analyze_game.py tanks-of-freedom")
        return
    
    # Initialize game components
    engine = QuickSkirmishEngine()
    assets = AssetManager(source_game_path)
    assets.load_tanks_of_freedom_assets()
    
    renderer = UIRenderer(engine, assets)
    
    # Game loop
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and engine.game_over:
                    # Restart game
                    engine = QuickSkirmishEngine()
                    renderer.engine = engine
                    renderer.selected_unit_pos = None
                    renderer.highlighted_moves = []
                    renderer.highlighted_attacks = []
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    renderer.handle_click(event.pos)
                elif event.button == 3:  # Right click
                    renderer.handle_right_click(event.pos)
        
        # Render game
        renderer.render()
        
        # Control frame rate
        clock.tick(60)
    
    pygame.quit()
    print("Game closed")


if __name__ == "__main__":
    main()