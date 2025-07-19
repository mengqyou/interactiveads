"""
Asset Manager

Loads and manages game assets extracted from the source game
"""
import pygame
from typing import Dict, Tuple
from pathlib import Path
from PIL import Image
import numpy as np


class AssetManager:
    """Manages game assets for mini-game generation"""
    
    def __init__(self, source_game_path: Path):
        self.source_path = source_game_path
        self.sprites: Dict[str, pygame.Surface] = {}
        self.animations: Dict[str, list] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Initialize pygame
        pygame.init()
        pygame.mixer.init()
        
    def load_tanks_of_freedom_assets(self):
        """Load specific assets from Tanks of Freedom"""
        assets_path = self.source_path / "assets"
        
        # Load unit spritesheet
        self._load_unit_sprites(assets_path / "units" / "units_spritesheet.png")
        
        # Load terrain assets  
        self._load_terrain_sprites(assets_path / "terrain")
        
        # Load UI elements
        self._load_ui_sprites(assets_path / "gui")
        
        # Load sounds
        self._load_sounds(assets_path / "sounds")
        
    def _load_unit_sprites(self, spritesheet_path: Path):
        """Extract unit sprites from spritesheet"""
        if not spritesheet_path.exists():
            print(f"Unit spritesheet not found: {spritesheet_path}")
            return
            
        try:
            # Load the spritesheet
            spritesheet = pygame.image.load(str(spritesheet_path))
            
            # Tanks of Freedom unit sprites are 32x32 pixels
            sprite_size = 32
            sheet_width = spritesheet.get_width()
            sheet_height = spritesheet.get_height()
            
            sprites_per_row = sheet_width // sprite_size
            
            # Extract individual sprites
            sprite_index = 0
            unit_types = ['soldier_blue', 'soldier_red', 'tank_blue', 'tank_red', 'heli_blue', 'heli_red']
            
            for y in range(0, sheet_height, sprite_size):
                for x in range(0, sheet_width, sprite_size):
                    if sprite_index < len(unit_types):
                        sprite_rect = pygame.Rect(x, y, sprite_size, sprite_size)
                        sprite = spritesheet.subsurface(sprite_rect)
                        self.sprites[unit_types[sprite_index]] = sprite.copy()
                        sprite_index += 1
                        
        except Exception as e:
            print(f"Error loading unit sprites: {e}")
            # Create placeholder sprites
            self._create_placeholder_sprites()
    
    def _create_placeholder_sprites(self):
        """Create simple placeholder sprites for testing"""
        size = 32
        
        # Create colored rectangles as placeholders
        colors = {
            'soldier_blue': (0, 100, 200),
            'soldier_red': (200, 50, 50),
            'tank_blue': (0, 150, 255),
            'tank_red': (255, 100, 100),
            'heli_blue': (100, 200, 255),
            'heli_red': (255, 150, 150)
        }
        
        for unit_type, color in colors.items():
            surface = pygame.Surface((size, size))
            surface.fill(color)
            
            # Add simple shape to distinguish unit types
            if 'soldier' in unit_type:
                pygame.draw.circle(surface, (255, 255, 255), (size//2, size//2), size//3)
            elif 'tank' in unit_type:
                pygame.draw.rect(surface, (255, 255, 255), (size//4, size//4, size//2, size//2))
            elif 'heli' in unit_type:
                pygame.draw.polygon(surface, (255, 255, 255), [(size//2, size//4), (size//4, 3*size//4), (3*size//4, 3*size//4)])
            
            self.sprites[unit_type] = surface
    
    def _load_terrain_sprites(self, terrain_path: Path):
        """Load terrain sprites"""
        # Create simple terrain tiles
        tile_size = 32
        
        # Grass tile
        grass = pygame.Surface((tile_size, tile_size))
        grass.fill((100, 150, 50))
        self.sprites['terrain_grass'] = grass
        
        # Selected tile highlight
        highlight = pygame.Surface((tile_size, tile_size))
        highlight.fill((255, 255, 0))
        highlight.set_alpha(128)
        self.sprites['highlight'] = highlight
        
        # Move indicator
        move_indicator = pygame.Surface((tile_size, tile_size))
        move_indicator.fill((0, 255, 0))
        move_indicator.set_alpha(100)
        self.sprites['move_indicator'] = move_indicator
        
        # Attack indicator
        attack_indicator = pygame.Surface((tile_size, tile_size))
        attack_indicator.fill((255, 0, 0))
        attack_indicator.set_alpha(100)
        self.sprites['attack_indicator'] = attack_indicator
    
    def _load_ui_sprites(self, gui_path: Path):
        """Load UI elements"""
        # Create simple UI elements
        
        # Health bar background
        health_bg = pygame.Surface((30, 4))
        health_bg.fill((100, 100, 100))
        self.sprites['health_bg'] = health_bg
        
        # Health bar fill
        health_fill = pygame.Surface((30, 4))
        health_fill.fill((0, 255, 0))
        self.sprites['health_fill'] = health_fill
        
        # Button
        button = pygame.Surface((100, 30))
        button.fill((150, 150, 150))
        pygame.draw.rect(button, (200, 200, 200), button.get_rect(), 2)
        self.sprites['button'] = button
    
    def _load_sounds(self, sounds_path: Path):
        """Load sound effects"""
        try:
            # Try to load actual sound files
            sound_files = {
                'move': sounds_path / "fx" / "move.wav",
                'attack': sounds_path / "fx" / "explosion.wav",
                'select': sounds_path / "fx" / "select.wav"
            }
            
            for sound_name, sound_path in sound_files.items():
                if sound_path.exists():
                    self.sounds[sound_name] = pygame.mixer.Sound(str(sound_path))
                    
        except Exception as e:
            print(f"Error loading sounds: {e}")
    
    def get_unit_sprite(self, unit_type: str, team: str) -> pygame.Surface:
        """Get sprite for specific unit type and team"""
        sprite_key = f"{unit_type}_{team}"
        return self.sprites.get(sprite_key, self.sprites.get('soldier_blue'))
    
    def get_sprite(self, name: str) -> pygame.Surface:
        """Get sprite by name"""
        return self.sprites.get(name)
    
    def play_sound(self, name: str):
        """Play sound effect"""
        if name in self.sounds:
            self.sounds[name].play()
    
    def scale_sprite(self, sprite: pygame.Surface, scale: float) -> pygame.Surface:
        """Scale sprite by factor"""
        if sprite:
            new_size = (int(sprite.get_width() * scale), int(sprite.get_height() * scale))
            return pygame.transform.scale(sprite, new_size)
        return sprite